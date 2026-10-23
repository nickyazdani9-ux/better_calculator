"""Typed, composable mathematical workspace on top of the existing restricted CAS.

This API is independent of the historical tab/plugin UI. Inputs are references to
previous nodes, never expressions reconstructed from displayed result strings.
No user-provided Python, SymPy sympify strings, or arbitrary functions run.
"""
from dataclasses import dataclass
import copy
import json
import re

import sympy as sp

from engine import parse_math, parse_matrix

NAME = re.compile(r'[A-Za-z][A-Za-z0-9_]{0,20}\Z')
NODE_ID = re.compile(r'[a-z][a-z0-9_]{0,31}\Z')
MAX_NODES = 64
MAX_BATCH = 24
MAX_SNAPSHOT_BYTES = 75000
SNAPSHOT_FORMAT = 'calculator2.workspace'
SNAPSHOT_VERSION = 1
SCALARS = frozenset({'scalar', 'scalar_field'})
ALL_KINDS = frozenset({'scalar', 'scalar_field', 'vector', 'covector', 'matrix', 'tensor2'})


def symbol(token, *, real=False):
    if not isinstance(token, str) or not NAME.fullmatch(token) or token in {'I','E','pi','oo','inf'}:
        raise ValueError('Expected a simple symbolic variable name.')
    return sp.Symbol(token, real=True) if real else sp.Symbol(token)


def coordinates(value):
    if value is None or value == '':
        return ()
    tokens = value.split(',') if isinstance(value, str) else value
    if not isinstance(tokens, list) and not isinstance(tokens, tuple):
        raise ValueError('Coordinates must be a list or comma-separated names.')
    tokens = [str(s).strip() for s in tokens]
    if not 1 <= len(tokens) <= 4 or len(tokens) != len(set(tokens)):
        raise ValueError('Supply 1–4 distinct coordinate names.')
    return tuple(symbol(t, real=True) for t in tokens)


def normalise(expr, coords):
    """Coordinates are real; free symbols not declared as coordinates stay general."""
    mapping = {sp.Symbol(str(c)): c for c in coords}
    if isinstance(expr, list):
        return [normalise(x, coords) for x in expr]
    return expr.xreplace(mapping)


def scalar_expr(text, coords=()):
    expr = normalise(parse_math(text), coords)
    if not isinstance(expr, sp.Expr):
        raise ValueError('Expected a scalar expression.')
    return expr


def context_metric(raw, coords):
    if raw is None:
        return None
    if not coords:
        raise ValueError('A metric requires coordinate names.')
    matrix = sp.ImmutableMatrix(normalise(parse_matrix(raw), coords))
    if matrix.shape != (len(coords), len(coords)):
        raise ValueError('Metric dimensions must match coordinates.')
    if matrix != matrix.T:
        raise ValueError('Metric must be symmetric.')
    if any(entry.is_real is not True for entry in matrix):
        raise ValueError('Metric components must be provably real; declare coordinates or assumptions.')
    if sp.simplify(matrix.det()) == 0:
        raise ValueError('Metric must be nondegenerate.')
    return matrix


def change_chart(kind, value, old_coords, old_metric, variance, target_names, mapping):
    """Pull components into a new chart given old coordinates as functions of new.

    J[i,a] = partial old_x[i] / partial new_x[a]. The requested map
    must be locally invertible; singular chart boundaries are not inferred.
    """
    if not old_coords:
        raise ValueError('Coordinate transformation requires an existing chart.')
    new_coords = coordinates(target_names)
    if len(new_coords) != len(old_coords):
        raise ValueError('Coordinate transformation must preserve dimension.')
    if set(new_coords) & set(old_coords) or {x.name for x in new_coords} & {x.name for x in old_coords}:
        raise ValueError('Use distinct old and new coordinate names.')
    if not isinstance(mapping, list) or len(mapping) != len(old_coords):
        raise ValueError('Mapping must give each old coordinate as an expression in the new coordinates.')
    functions = [scalar_expr(expr, new_coords) for expr in mapping]
    if any(not expr.free_symbols <= set(new_coords) for expr in functions):
        raise ValueError('Coordinate mapping may depend only on the new chart coordinates.')
    jac = sp.ImmutableMatrix([[sp.diff(expr, c) for c in new_coords] for expr in functions])
    if sp.simplify(jac.det()) == 0:
        raise ValueError('Coordinate transformation has a singular Jacobian.')
    inverse = jac.inv()
    substitution = dict(zip(old_coords, functions))
    if isinstance(value, sp.MatrixBase):
        changed = value.subs(substitution, simultaneous=True)
        if kind == 'vector':
            changed = inverse * changed
        elif kind == 'covector':
            changed = jac.T * changed
        elif kind == 'tensor2':
            left = inverse if variance[0] == 'up' else jac.T
            right = inverse if variance[1] == 'up' else jac.T
            changed = left * changed * right.T
        else:
            raise ValueError('Generic matrices do not have a tensor transformation law.')
        changed = sp.ImmutableMatrix(changed.applyfunc(sp.simplify))
    else:
        changed = sp.simplify(value.subs(substitution, simultaneous=True))
    new_metric = None
    if old_metric is not None:
        metric_at_new = old_metric.subs(substitution, simultaneous=True)
        new_metric = sp.ImmutableMatrix((jac.T * metric_at_new * jac).applyfunc(sp.simplify))
    return changed, new_coords, new_metric

@dataclass(frozen=True)
class MathNode:
    id: str
    kind: str
    value: object
    parents: tuple = ()
    operation: str = 'define'
    coords: tuple = ()
    metric: object = None
    variance: tuple = ()

    def public(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'expr': sp.sstr(self.value),
            'latex': sp.latex(self.value),
            'parents': list(self.parents),
            'operation': self.operation,
            'variance': list(self.variance),
            'context': {
                'coordinates': [str(c) for c in self.coords],
                'metric': sp.sstr(self.metric) if self.metric is not None else None,
            },
        }


# Only compatible kinds appear in the dispatch table. No user-defined callables.
OPERATION_SIGNATURES = {
    'simplify': ALL_KINDS,
    'expand': SCALARS,
    'factor': SCALARS,
    'conjugate': ALL_KINDS,
    'differentiate': SCALARS,
    'integrate': SCALARS,
    'exterior_derivative': frozenset({'scalar_field'}),
    'norm_squared': frozenset({'vector', 'covector'}),
    'determinant': frozenset({'matrix'}),
    'residue': SCALARS,
    'substitute': ALL_KINDS,
    'expectation': SCALARS,
    'add': ALL_KINDS,
    'multiply': ALL_KINDS,
    'pair': frozenset({'vector', 'covector'}),
    'tensor_product': frozenset({'vector', 'covector'}),
    'contract': frozenset({'tensor2'}),
    'raise_index': frozenset({'covector'}),
    'lower_index': frozenset({'vector'}),
    'change_coordinates': frozenset({'scalar_field', 'vector', 'covector', 'tensor2'}),
}


class Workspace:
    def __init__(self):
        self.nodes = {}
        # The journal records *validated requests*, not untrusted SymPy text.
        # Replaying the journal reproduces typed values and their dependencies.
        self.journal = []

    @staticmethod
    def _recordable(request):
        """Freeze an input command and reject fields outside the versioned protocol."""
        allowed = {
            'define': {'command', 'id', 'kind', 'coordinates', 'metric',
                       'expression', 'components', 'matrix'},
            'apply': {'command', 'id', 'operation', 'source', 'other', 'variable',
                      'order', 'point', 'lower', 'upper', 'expression',
                      'normals', 'independent', 'coordinates', 'mapping'},
        }
        cmd = request.get('command')
        if cmd not in allowed:
            raise ValueError('Only define/apply commands can be recorded.')
        if request.get('action', 'workspace') != 'workspace':
            raise ValueError('Invalid workspace action.')
        unsupported = set(request) - allowed[cmd] - {'action'}
        if unsupported:
            raise ValueError('Unsupported workspace command field: ' + ', '.join(sorted(unsupported)))
        data = copy.deepcopy({key: value for key, value in request.items() if key != 'action'})
        try:
            encoded = json.dumps(data, allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError('Workspace commands must contain JSON-safe values.') from exc
        if len(encoded) > MAX_SNAPSHOT_BYTES:
            raise ValueError('Workspace command is too large.')
        return data

    @staticmethod
    def _id(request):
        token = request.get('id')
        if not isinstance(token, str) or not NODE_ID.fullmatch(token):
            raise ValueError('Node id must begin with a lowercase letter and contain only a–z, 0–9 or _.')
        return token

    def _save(self, node):
        if node.id in self.nodes:
            raise ValueError(f'Node {node.id!r} already exists; use a new id or reset.')
        if len(self.nodes) >= MAX_NODES:
            raise ValueError('Workspace limit reached (64 nodes).')
        self.nodes[node.id] = node
        return {'ok': True, 'node': node.public()}

    def _get(self, token):
        if not isinstance(token, str) or token not in self.nodes:
            raise ValueError(f'Unknown node: {token!r}.')
        return self.nodes[token]

    def define(self, request):
        ident = self._id(request)
        if ident in self.nodes:
            raise ValueError(f'Node {ident!r} already exists.')
        kind = request.get('kind', 'scalar')
        coords = coordinates(request.get('coordinates'))
        metric = context_metric(request.get('metric'), coords)
        if kind in SCALARS:
            value = scalar_expr(request.get('expression', ''), coords)
            kind = 'scalar_field' if coords else 'scalar'
        elif kind in ('vector', 'covector'):
            if not coords:
                raise ValueError('Vectors and covectors require coordinates.')
            parts = normalise(parse_math(request.get('components', '')), coords)
            if not isinstance(parts, list) or len(parts) != len(coords) or any(not isinstance(x, sp.Expr) for x in parts):
                raise ValueError('Components must be a list with one scalar per coordinate.')
            value = sp.ImmutableMatrix(parts)
        elif kind == 'matrix':
            value = sp.ImmutableMatrix(normalise(parse_matrix(request.get('matrix','')), coords))
        else:
            raise ValueError(f'Unknown mathematical kind: {kind!r}.')
        return self._save(MathNode(ident, kind, value, coords=coords, metric=metric))

    @staticmethod
    def _merge_context(left, right):
        if left.coords and right.coords and left.coords != right.coords:
            raise ValueError('Incompatible coordinate systems; supply an explicit coordinate transform.')
        if left.metric is not None and right.metric is not None and left.metric != right.metric:
            raise ValueError('Incompatible metrics; select or transform to a shared metric.')
        # Symbol('x') and a real chart coordinate x are different SymPy objects.
        # Never combine them silently only because their printed names match.
        scoped = left if left.coords else right
        unscoped = right if left.coords else left
        if scoped.coords and not unscoped.coords:
            chart_names = {c.name for c in scoped.coords}
            collisions = [s for s in unscoped.value.free_symbols
                          if s.name in chart_names and s not in scoped.coords]
            if collisions:
                raise ValueError('Undeclared coordinate assumptions conflict; define both objects in the same chart.')
        return left.coords or right.coords, left.metric if left.metric is not None else right.metric

    def apply(self, request):
        ident = self._id(request)
        op = request.get('operation')
        if op not in OPERATION_SIGNATURES:
            raise ValueError('Unknown unified mathematical operation.')
        source = self._get(request.get('source'))
        if source.kind not in OPERATION_SIGNATURES[op]:
            raise ValueError(f'Operation {op} does not accept {source.kind}.')
        value, kind = source.value, source.kind
        coords, metric = source.coords, source.metric
        parents = (source.id,)
        variance = source.variance

        if op in ('simplify', 'expand', 'factor', 'conjugate'):
            fn = {'simplify': sp.simplify, 'expand': sp.expand, 'factor': sp.factor,
                  'conjugate': sp.conjugate}[op]
            if isinstance(value, sp.MatrixBase):
                value = value.applyfunc(fn)
            else:
                value = fn(value)
        elif op in ('differentiate', 'integrate', 'residue'):
            variable = symbol(request.get('variable'))
            if coords and variable.name in {c.name for c in coords}:
                variable = next(c for c in coords if c.name == variable.name)
            if op == 'differentiate':
                order = request.get('order', 1)
                if type(order) is not int or not 1 <= order <= 12:
                    raise ValueError('Differentiation order must be an integer from 1 to 12.')
                value = sp.diff(value, variable, order)
            elif op == 'integrate':
                if 'lower' in request or 'upper' in request:
                    if not isinstance(request.get('lower'), str) or not isinstance(request.get('upper'), str):
                        raise ValueError('Definite integration needs both bounds.')
                    value = sp.integrate(value, (variable, scalar_expr(request['lower'], coords), scalar_expr(request['upper'], coords)))
                else:
                    value = sp.integrate(value, variable)
            else:
                if variable in coords:
                    raise ValueError('Residues require a complex variable, not a real coordinate.')
                value = sp.residue(value, variable, scalar_expr(request.get('point', '0'), coords))
        elif op == 'exterior_derivative':
            if not coords:
                raise ValueError('The exterior derivative needs a declared coordinate chart.')
            value = sp.ImmutableMatrix([sp.diff(value, x) for x in coords])
            kind = 'covector'
        elif op == 'norm_squared':
            if metric is None:
                raise ValueError('Squared norm requires an explicit metric.')
            matrix = metric.inv() if kind == 'covector' else metric
            value = sp.simplify((value.conjugate().T * matrix * value)[0])
            kind = 'scalar_field'
        elif op == 'raise_index':
            if metric is None:
                raise ValueError('Raising an index requires a metric.')
            value = metric.inv() * value
            kind = 'vector'
        elif op == 'lower_index':
            if metric is None:
                raise ValueError('Lowering an index requires a metric.')
            value = metric * value
            kind = 'covector'
        elif op == 'change_coordinates':
            value, coords, metric = change_chart(
                kind, value, coords, metric, variance,
                request.get('coordinates'), request.get('mapping'))
        elif op == 'contract':
            if variance not in (('up', 'down'), ('down', 'up')):
                raise ValueError('Contraction needs one upper and one lower index; use the metric explicitly.')
            value = sp.simplify(sp.trace(value))
            kind = 'scalar_field'
            variance = ()
        elif op == 'determinant':
            if value.rows != value.cols:
                raise ValueError('Determinant requires a square matrix.')
            value = value.det()
            kind = 'scalar_field' if coords else 'scalar'
        elif op == 'substitute':
            variable = symbol(request.get('variable'))
            if coords and variable.name in {c.name for c in coords}:
                variable = next(c for c in coords if c.name == variable.name)
            replacement = scalar_expr(request.get('expression', ''), coords)
            value = value.subs(variable, replacement)
            if variable in coords:
                # Restricting a field does not automatically induce a chart/metric.
                coords, metric = (), None
                if kind == 'scalar_field':
                    kind = 'scalar'
                if kind in ('vector', 'covector', 'tensor2'):
                    kind = 'matrix'
                    variance = ()
        elif op == 'expectation':
            from sympy.stats import Normal, E
            normals = request.get('normals')
            if not isinstance(normals, dict) or not 1 <= len(normals) <= 4:
                raise ValueError('Provide 1–4 independent normal distributions in normals.')
            if request.get('independent') is not True:
                raise ValueError('Independent normal variables must be explicitly acknowledged (independent: true).')
            subs = {}
            random_names = set(normals)
            for name, info in normals.items():
                if not isinstance(info, dict):
                    raise ValueError('Each normal variable requires mean and std.')
                free = symbol(name)
                if coords and name in {c.name for c in coords}:
                    free = next(c for c in coords if c.name == name)
                if free not in value.free_symbols:
                    raise ValueError(f'Variable {name} does not occur in the expression.')
                mean = scalar_expr(info.get('mean', '0'))
                std = scalar_expr(info.get('std', '1'))
                if std.is_positive is not True:
                    raise ValueError('Normal standard deviations must be provably positive.')
                if any(s.name in random_names for s in mean.free_symbols | std.free_symbols):
                    raise ValueError('Distribution parameters cannot depend on the declared random variables.')
                subs[free] = Normal('rv_' + name, mean, std)
            value = sp.simplify(E(value.subs(subs)))
            # An expectation is not automatically a field on the original chart.
            coords, metric = (), None
            kind = 'scalar'
        elif op in ('add', 'multiply', 'pair', 'tensor_product'):
            other = self._get(request.get('other'))
            coords, metric = self._merge_context(source, other)
            parents += (other.id,)
            scalar_pair = source.kind in SCALARS and other.kind in SCALARS
            same_linear_kind = source.kind == other.kind and source.kind in ('vector', 'covector', 'matrix', 'tensor2')
            scalar_linear_pair = ((source.kind in SCALARS and other.kind in ('vector', 'covector', 'matrix', 'tensor2')) or
                                  (other.kind in SCALARS and source.kind in ('vector', 'covector', 'matrix', 'tensor2')))
            if op == 'pair':
                if {source.kind, other.kind} != {'vector', 'covector'}:
                    raise ValueError('Canonical pairing requires a vector and a covector.')
                vector = source.value if source.kind == 'vector' else other.value
                covector = source.value if source.kind == 'covector' else other.value
                value = sp.simplify((covector.T * vector)[0])
                kind, variance = 'scalar_field', ()
            elif op == 'tensor_product':
                if source.kind not in ('vector', 'covector') or other.kind not in ('vector', 'covector'):
                    raise ValueError('Tensor product requires two vector/covector operands.')
                if not coords or source.coords != other.coords:
                    raise ValueError('Tensor factors require the same declared coordinates.')
                value = source.value * other.value.T
                variance = tuple('up' if node.kind == 'vector' else 'down' for node in (source, other))
                kind = 'tensor2'
            elif op == 'add' and same_linear_kind and source.variance != other.variance:
                raise ValueError('Cannot add tensors with different index variance.')
            elif op == 'add' and not (scalar_pair or same_linear_kind):
                raise ValueError('Addition requires compatible scalar or tensor kinds.')
            elif op == 'multiply' and not (scalar_pair or scalar_linear_pair):
                raise ValueError('Multiplication of these objects needs an explicit contraction or product.')
            if op in ('pair', 'tensor_product'):
                pass
            elif scalar_pair:
                kind = 'scalar_field' if coords else 'scalar'
                value = sp.simplify(value + other.value if op == 'add' else value * other.value)
            elif same_linear_kind:
                if source.value.shape != other.value.shape:
                    raise ValueError('Array shapes do not match.')
                value = value + other.value
            else:
                kind = other.kind if source.kind in SCALARS else source.kind
                variance = other.variance if source.kind in SCALARS else source.variance
                value = value * other.value if source.kind in SCALARS else other.value * value

        if isinstance(value, sp.MatrixBase):
            value = sp.ImmutableMatrix(value)
        return self._save(MathNode(ident, kind, value, parents, op, coords, metric, variance))

    def handle(self, request):
        try:
            return self.command(request)
        except (ValueError, TypeError, KeyError, ZeroDivisionError, NotImplementedError, sp.PolynomialError) as exc:
            return {'ok': False, 'error': str(exc)}
        except Exception as exc:
            return {'ok': False, 'error': f'Mathematical operation failed: {type(exc).__name__}: {exc}'}

    def command(self, request):
        if not isinstance(request, dict):
            raise ValueError('Workspace command must be an object.')
        cmd = request.get('command')
        if cmd in ('define', 'apply'):
            step = self._recordable(request)
            output = self.define(step) if cmd == 'define' else self.apply(step)
            self.journal.append(step)
            return output
        if cmd == 'get':
            return {'ok': True, 'node': self._get(request.get('id')).public()}
        if cmd == 'graph':
            return {'ok': True, 'nodes': [node.public() for node in self.nodes.values()]}
        if cmd == 'operations':
            return {'ok': True, 'operations': {op: sorted(kinds) for op, kinds in OPERATION_SIGNATURES.items()}}
        if cmd == 'export':
            snapshot = {'format': SNAPSHOT_FORMAT, 'version': SNAPSHOT_VERSION,
                        'steps': copy.deepcopy(self.journal)}
            return {'ok': True, 'snapshot': snapshot}
        if cmd == 'import':
            snapshot = request.get('snapshot')
            if not isinstance(snapshot, dict) or set(snapshot) != {'format', 'version', 'steps'}:
                raise ValueError('Invalid workspace snapshot structure.')
            if snapshot['format'] != SNAPSHOT_FORMAT or type(snapshot['version']) is not int or snapshot['version'] != SNAPSHOT_VERSION:
                raise ValueError('Unsupported workspace snapshot format/version.')
            steps = snapshot['steps']
            if not isinstance(steps, list) or len(steps) > MAX_NODES:
                raise ValueError('Snapshot exceeds the 64-node limit.')
            try:
                encoded = json.dumps(snapshot, allow_nan=False)
            except (TypeError, ValueError) as exc:
                raise ValueError('Snapshot must be JSON-safe.') from exc
            if len(encoded) > MAX_SNAPSHOT_BYTES:
                raise ValueError('Snapshot exceeds the size limit.')
            before_nodes, before_journal = self.nodes, self.journal
            self.nodes, self.journal = {}, []
            try:
                for index, step in enumerate(steps):
                    if not isinstance(step, dict) or step.get('command') not in ('define', 'apply'):
                        raise ValueError(f'Invalid snapshot step {index}: expected define/apply.')
                    try:
                        self.command(step)
                    except Exception as exc:
                        raise ValueError(f'Invalid snapshot step {index}: {exc}') from exc
            except Exception:
                self.nodes, self.journal = before_nodes, before_journal
                raise
            return {'ok': True, 'nodes': [node.public() for node in self.nodes.values()]}
        if cmd == 'reset':
            self.nodes.clear()
            self.journal.clear()
            return {'ok': True, 'nodes': []}
        if cmd == 'batch':
            steps = request.get('steps')
            if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_BATCH:
                raise ValueError('Batch requires 1–24 steps.')
            before = self.nodes.copy()
            before_journal = copy.deepcopy(self.journal)
            results = []
            for index, step in enumerate(steps):
                try:
                    if not isinstance(step, dict) or step.get('command') in ('batch', 'reset'):
                        raise ValueError('Nested batches and reset are not allowed.')
                    results.append(self.command(step))
                except Exception as exc:
                    self.nodes = before
                    self.journal = before_journal
                    return {'ok': False, 'failed_step': index, 'error': str(exc)}
            return {'ok': True, 'results': results}
        raise ValueError('Unknown workspace command.')


WORKSPACE = Workspace()


def execute(request):
    """JSON-safe API. Workspace is scoped to this Python interpreter / Web Worker."""
    return WORKSPACE.handle(request)
