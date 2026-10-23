"""Typed, composable mathematical workspace on top of the existing restricted CAS.

This API is independent of the historical tab/plugin UI. Inputs are references to
previous nodes, never expressions reconstructed from displayed result strings.
No user-provided Python, SymPy sympify strings, or arbitrary functions run.
"""
from dataclasses import dataclass
import re

import sympy as sp

from engine import parse_math, parse_matrix

NAME = re.compile(r'[A-Za-z][A-Za-z0-9_]{0,20}\Z')
NODE_ID = re.compile(r'[a-z][a-z0-9_]{0,31}\Z')
MAX_NODES = 64
MAX_BATCH = 24
SCALARS = frozenset({'scalar', 'scalar_field'})
ALL_KINDS = frozenset({'scalar', 'scalar_field', 'vector', 'covector', 'matrix'})


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


@dataclass(frozen=True)
class MathNode:
    id: str
    kind: str
    value: object
    parents: tuple = ()
    operation: str = 'define'
    coords: tuple = ()
    metric: object = None

    def public(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'expr': sp.sstr(self.value),
            'latex': sp.latex(self.value),
            'parents': list(self.parents),
            'operation': self.operation,
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
}


class Workspace:
    def __init__(self):
        self.nodes = {}

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
                if kind in ('vector', 'covector'):
                    kind = 'matrix'
        elif op == 'expectation':
            from sympy.stats import Normal, E
            normals = request.get('normals')
            if not isinstance(normals, dict) or not 1 <= len(normals) <= 4:
                raise ValueError('Provide 1–4 independent normal distributions in normals.')
            if request.get('independent') is not True:
                raise ValueError('Independent normal variables must be explicitly acknowledged (independent: true).')
            subs = {}
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
                subs[free] = Normal('rv_' + name, mean, std)
            value = sp.simplify(E(value.subs(subs)))
            # An expectation is not automatically a field on the original chart.
            coords, metric = (), None
            kind = 'scalar'
        elif op in ('add', 'multiply'):
            other = self._get(request.get('other'))
            coords, metric = self._merge_context(source, other)
            parents += (other.id,)
            scalar_pair = source.kind in SCALARS and other.kind in SCALARS
            same_linear_kind = source.kind == other.kind and source.kind in ('vector', 'covector', 'matrix')
            scalar_linear_pair = ((source.kind in SCALARS and other.kind in ('vector', 'covector', 'matrix')) or
                                  (other.kind in SCALARS and source.kind in ('vector', 'covector', 'matrix')))
            if op == 'add' and not (scalar_pair or same_linear_kind):
                raise ValueError('Addition requires compatible scalar or tensor kinds.')
            if op == 'multiply' and not (scalar_pair or scalar_linear_pair):
                raise ValueError('Multiplication of these objects needs an explicit contraction or product.')
            if scalar_pair:
                kind = 'scalar_field' if coords else 'scalar'
                value = sp.simplify(value + other.value if op == 'add' else value * other.value)
            elif same_linear_kind:
                if source.value.shape != other.value.shape:
                    raise ValueError('Array shapes do not match.')
                value = value + other.value
            else:
                kind = other.kind if source.kind in SCALARS else source.kind
                value = value * other.value if source.kind in SCALARS else other.value * value

        if isinstance(value, sp.MatrixBase):
            value = sp.ImmutableMatrix(value)
        return self._save(MathNode(ident, kind, value, parents, op, coords, metric))

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
        if cmd == 'define':
            return self.define(request)
        if cmd == 'apply':
            return self.apply(request)
        if cmd == 'get':
            return {'ok': True, 'node': self._get(request.get('id')).public()}
        if cmd == 'graph':
            return {'ok': True, 'nodes': [node.public() for node in self.nodes.values()]}
        if cmd == 'operations':
            return {'ok': True, 'operations': {op: sorted(kinds) for op, kinds in OPERATION_SIGNATURES.items()}}
        if cmd == 'reset':
            self.nodes.clear()
            return {'ok': True, 'nodes': []}
        if cmd == 'batch':
            steps = request.get('steps')
            if not isinstance(steps, list) or not 1 <= len(steps) <= MAX_BATCH:
                raise ValueError('Batch requires 1–24 steps.')
            before = self.nodes.copy()
            results = []
            for index, step in enumerate(steps):
                try:
                    if not isinstance(step, dict) or step.get('command') in ('batch', 'reset'):
                        raise ValueError('Nested batches and reset are not allowed.')
                    results.append(self.command(step))
                except Exception as exc:
                    self.nodes = before
                    return {'ok': False, 'failed_step': index, 'error': str(exc)}
            return {'ok': True, 'results': results}
        raise ValueError('Unknown workspace command.')


WORKSPACE = Workspace()


def execute(request):
    """JSON-safe API. Workspace is scoped to this Python interpreter / Web Worker."""
    return WORKSPACE.handle(request)
