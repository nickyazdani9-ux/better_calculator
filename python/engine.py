"""Calculator 2.0 CAS kernel. No eval/exec of user math expressions.

Plugins add new mathematical domains with @register, without editing the UI.
Browser worker supplies plugin files from python/plugins.json before this is imported.
"""
import ast
import importlib
import json
import operator
import pkgutil
import re

import sympy as sp

OPERATIONS = {}
TABS = {}
LOADED = False

FUNCTIONS = {
    'sin':sp.sin, 'cos':sp.cos, 'tan':sp.tan, 'asin':sp.asin, 'acos':sp.acos,
    'atan':sp.atan, 'sinh':sp.sinh, 'cosh':sp.cosh, 'tanh':sp.tanh,
    'exp':sp.exp, 'log':sp.log, 'ln':sp.log, 'sqrt':sp.sqrt,
    'abs':sp.Abs, 'Abs':sp.Abs, 'conjugate':sp.conjugate, 're':sp.re,
    'im':sp.im, 'arg':sp.arg, 'gamma':sp.gamma, 'factorial':sp.factorial,
    'sign':sp.sign, 'floor':sp.floor, 'ceiling':sp.ceiling,
}
CONSTANTS = {'pi':sp.pi,'E':sp.E,'e':sp.E,'I':sp.I,'oo':sp.oo,'inf':sp.oo}
BIN_OPS = {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul,
           ast.Div:operator.truediv, ast.Pow:operator.pow}
UNARY_OPS = {ast.UAdd:operator.pos, ast.USub:operator.neg}
MAX_NODES = 120
MAX_LENGTH = 500


def parse_math(value):
    """Parse common mathematical syntax using a tightly restricted Python AST."""
    if not isinstance(value, str) or not value.strip() or len(value) > MAX_LENGTH:
        raise ValueError('Enter a mathematical expression (maximum 500 characters).')
    source = value.replace('^', '**').replace('π', 'pi').replace('∞','oo')
    try:
        tree = ast.parse(source, mode='eval')
    except SyntaxError as e:
        raise ValueError('Invalid mathematical syntax.') from e
    if sum(1 for _ in ast.walk(tree)) > MAX_NODES:
        raise ValueError('Expression is too large.')

    def walk(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            if abs(node.value) > 1000000:
                raise ValueError('Numeric literal is too large.')
            return sp.Integer(node.value) if isinstance(node.value,int) else sp.Float(node.value)
        if isinstance(node, ast.Name):
            if node.id in CONSTANTS:
                return CONSTANTS[node.id]
            if re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]{0,20}',node.id) and not node.id.startswith('_'):
                return sp.Symbol(node.id)
            raise ValueError('Invalid mathematical name.')
        if type(node) in (ast.List, ast.Tuple):
            if len(node.elts) > 4:
                raise ValueError('Lists are limited to four elements.')
            return [walk(el) for el in node.elts]
        if isinstance(node,ast.BinOp) and type(node.op) in BIN_OPS:
            lhs, rhs = walk(node.left), walk(node.right)
            if isinstance(node.op,ast.Pow):
                if rhs.is_number:
                    if rhs.is_real is not True or abs(float(rhs)) > 32:
                        raise ValueError('Numeric powers must be real and have magnitude <= 32.')
            return BIN_OPS[type(node.op)](lhs,rhs)
        if isinstance(node,ast.UnaryOp) and type(node.op) in UNARY_OPS:
            return UNARY_OPS[type(node.op)](walk(node.operand))
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and not node.keywords:
            func = FUNCTIONS.get(node.func.id)
            if func is None or len(node.args)!=1:
                raise ValueError('Unknown function or invalid number of arguments.')
            arg = walk(node.args[0])
            if isinstance(arg,list): raise ValueError('Function arguments must be expressions.')
            return func(arg)
        raise ValueError('Unsupported expression. Use explicit multiplication, e.g. 2*x.')

    try:
        return walk(tree.body)
    except (OverflowError,ZeroDivisionError,TypeError,AttributeError) as e:
        raise ValueError('Invalid or excessively large expression.') from e



def latex_for_input(value):
    """Typeset the parsed input tree without simplifying the user's original expression.

    Uses precisely the restricted grammar accepted by parse_math; never interprets
    user input as LaTeX or executes user-supplied Python.
    """
    parse_math(value)  # Validate syntax, allowed calls, complexity and limits first.
    tree = ast.parse(value.replace('^', '**').replace('π', 'pi').replace('∞','oo'), mode='eval')

    def render(node):
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return sp.latex(sp.sympify(node.value)), 5
        if isinstance(node, ast.Name):
            return sp.latex(CONSTANTS.get(node.id, sp.Symbol(node.id))), 5
        if isinstance(node, (ast.List, ast.Tuple)):
            if node.elts and all(isinstance(row, (ast.List, ast.Tuple)) for row in node.elts):
                rows = [' & '.join(render(element)[0] for element in row.elts) for row in node.elts]
                return r'\begin{bmatrix}' + r' \\ '.join(rows) + r'\end{bmatrix}', 5
            return r'\left[' + ', '.join(render(item)[0] for item in node.elts) + r'\right]', 5
        if isinstance(node, ast.UnaryOp):
            content, prec = render(node.operand)
            if prec < 3:
                content = r'\left(' + content + r'\right)'
            return ('-' if isinstance(node.op, ast.USub) else '+') + content, 3
        if isinstance(node, ast.Call):
            name = node.func.id
            arg = render(node.args[0])[0]
            if name == 'sqrt':
                return r'\sqrt{' + arg + '}', 5
            if name in ('abs', 'Abs'):
                return r'\left|' + arg + r'\right|', 5
            if name == 'conjugate':
                return r'\overline{' + arg + '}', 5
            names = {'ln': r'\ln', 'log': r'\log', 'sin': r'\sin', 'cos': r'\cos',
                     'tan': r'\tan', 'asin': r'\arcsin', 'acos': r'\arccos',
                     'atan': r'\arctan', 'exp': r'\exp', 'sinh': r'\sinh',
                     'cosh': r'\cosh', 'tanh': r'\tanh'}
            label = names.get(name, r'\operatorname{' + name + '}')
            return label + r'\left(' + arg + r'\right)', 5
        if isinstance(node, ast.BinOp):
            left, lp = render(node.left)
            right, rp = render(node.right)
            if isinstance(node.op, ast.Pow):
                if lp < 4 or isinstance(node.left, ast.BinOp) and isinstance(node.left.op, ast.Pow):
                    left = r'\left(' + left + r'\right)'
                return left + '^{' + right + '}', 4
            if isinstance(node.op, ast.Div):
                return r'\frac{' + left + '}{' + right + '}', 2
            if isinstance(node.op, ast.Mult):
                if lp < 2: left = r'\left(' + left + r'\right)'
                if rp < 2: right = r'\left(' + right + r'\right)'
                return left + r' \cdot ' + right, 2
            if isinstance(node.op, (ast.Add, ast.Sub)):
                if isinstance(node.op, ast.Sub) and (rp <= 1 or isinstance(node.right, ast.UnaryOp)):
                    right = r'\left(' + right + r'\right)'
                return left + (' - ' if isinstance(node.op, ast.Sub) else ' + ') + right, 1
        raise ValueError('Unsupported mathematical input.')

    return render(tree.body)[0]


def formatted_inputs(values):
    """Return structured, safe, typeset versions of the mathematical input fields."""
    keys = ('expression', 'expressions', 'matrix', 'other', 'metric', 'vector')
    formatted = []
    for key in keys:
        value = values.get(key)
        if isinstance(value, str) and value.strip():
            try:
                formatted.append({'key': key, 'text': value, 'latex': latex_for_input(value)})
            except ValueError:
                # Some operations use different input grammars: retain evaluation errors.
                continue
    return formatted


def math_expr(v, name='expression'):
    return parse_math(v.get(name, ''))


def math_symbol(v, name='variable', default='x'):
    token=str(v.get(name, default)).strip()
    if not re.fullmatch(r'[a-zA-Z][a-zA-Z0-9_]{0,20}',token) or token in CONSTANTS or token in FUNCTIONS:
        raise ValueError(f'{name} must be a variable name (e.g. x).')
    return sp.Symbol(token)


def math_int(v, name, minimum=0, maximum=20):
    try: value=int(v.get(name,''))
    except (TypeError,ValueError): raise ValueError(f'{name} must be an integer.')
    if not minimum<=value<=maximum:
        raise ValueError(f'{name} must be between {minimum} and {maximum}.')
    return value


def parse_matrix(value):
    raw=parse_math(value)
    if not isinstance(raw,list) or not raw or not all(isinstance(row,list) for row in raw):
        raise ValueError('Use matrix notation [[a,b],[c,d]].')
    if len(raw)>4 or len(raw[0])>4 or any(len(row)!=len(raw[0]) for row in raw):
        raise ValueError('Matrices must be rectangular and at most 4×4.')
    return sp.Matrix(raw)


def metric_data(v):
    names=[name.strip() for name in str(v.get('coordinates','')).split(',')]
    if not 1<=len(names)<=4 or len(set(names))!=len(names):
        raise ValueError('Enter 1–4 distinct coordinate names separated by commas.')
    coords=[math_symbol({'variable':name}) for name in names]
    m=parse_matrix(v.get('metric',''))
    if m.shape!=(len(coords),len(coords)):
        raise ValueError('Metric size must match the number of coordinates.')
    if m != m.T:
        raise ValueError('The metric must be symmetric.')
    if sp.simplify(m.det())==0:
        raise ValueError('Metric must be nondegenerate (determinant ≠ 0).')
    return coords,m


def field(key,label,default='',kind='text',hint=''):
    return dict(key=key,label=label,default=default,kind=kind,hint=hint)


def register(tab,name,icon,op,label,description,fields):
    def attach(fn):
        if tab not in TABS:
            TABS[tab]={'id':tab,'name':name,'icon':icon,'operations':[]}
        if (tab,op) in OPERATIONS:
            raise RuntimeError(f'Duplicate operation {tab}/{op}')
        TABS[tab]['operations'].append(dict(id=op,label=label,description=description,fields=fields))
        OPERATIONS[(tab,op)] = fn
        return fn
    return attach


def load_plugins():
    global LOADED
    if LOADED: return
    import plugins
    for item in sorted(pkgutil.iter_modules(plugins.__path__), key=lambda it:it.name):
        if not item.name.startswith('_'):
            importlib.import_module('plugins.'+item.name)
    LOADED=True


def operation_catalog():
    load_plugins()
    preferred=['basic','calculus','complex','geometry','waves','linear']
    return [TABS[tab] for tab in preferred if tab in TABS] + [t for k,t in TABS.items() if k not in preferred]


def calculate(request):
    try:
        load_plugins()
        tab=request['tab']; op=request['operation']; values=request.get('values',{})
        fn=OPERATIONS.get((tab,op))
        if not fn:
            raise ValueError('Unknown operation.')
        if not isinstance(values,dict):
            raise ValueError('Invalid operation values.')
        raw=fn(values)
        if not isinstance(raw,dict): raw={'expression':raw}
        expression=raw.get('expression')
        lines=raw.get('lines',[])
        extra=raw.get('extras',{})
        if expression is not None:
            plain=str(expression)
            latex=sp.latex(expression)
        else:
            plain='\n'.join(lines)
            latex=raw.get('latex','')
        reusable = False
        if expression is not None:
            try:
                parsed_result = parse_math(plain)
                reusable = isinstance(parsed_result, sp.Expr)
            except (ValueError, TypeError, OverflowError):
                pass
        return {'ok':True,'expr':plain,'latex':latex,'text':plain,'lines':lines,
                'extras':extra,'inputs':formatted_inputs(values),'reusable':reusable}
    except (ValueError,TypeError,KeyError,ZeroDivisionError,NotImplementedError,sp.PolynomialError) as e:
        return {'ok':False,'error':str(e)}
    except Exception as e:
        return {'ok':False,'error':f'Could not evaluate expression: {type(e).__name__}: {e}'}


def run_json(payload):
    """Only interface needed by Pyodide / browser worker."""
    request=json.loads(payload)
    if request.get('action')=='workspace':
        from workspace import execute
        return json.dumps(execute(request))
    if request.get('action')=='catalog':
        return json.dumps({'ok':True,'catalog':operation_catalog()})
    return json.dumps(calculate(request))
