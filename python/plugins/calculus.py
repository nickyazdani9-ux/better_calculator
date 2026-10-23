import sympy as sp
from math_operations import limit as shared_limit, series as shared_series
from engine import register,field,math_expr,math_symbol,math_int
TAB=('calculus','Calculus','sigma')

def reg(op,label,desc,fields):
    return register(*TAB,op,label,desc,fields)
E=field('expression','f(x)','x^3 + sin(x)')
V=field('variable','Variable','x')
@reg('differentiate','Differentiate','Ordinary or higher derivatives.',[E,V,field('order','Derivative order','1')])
def differentiate(v): return sp.diff(math_expr(v),math_symbol(v),math_int(v,'order',1,12))
@reg('integrate','Integrate','Indefinite or definite integral; leave both bounds blank for indefinite.',[field('expression','Integrand','x^2'),V,field('lower','Lower bound (optional)',''),field('upper','Upper bound (optional)','')])
def integrate(v):
    x=math_symbol(v)
    lo=str(v.get('lower','')).strip(); hi=str(v.get('upper','')).strip()
    if bool(lo)!=bool(hi):raise ValueError('Supply both integral bounds, or neither.')
    return sp.integrate(math_expr(v),(x,math_expr({'expression':lo}),math_expr({'expression':hi}))) if lo else sp.integrate(math_expr(v),x)
@reg('limit','Limit','Two-sided, left, or right limit.',[field('expression','Expression','sin(x)/x'),V,field('point','Approaches','0'),field('direction','Side: +, -, or +-','+-')])
def limit(v):
    side=str(v.get('direction','+-')).strip()
    if side not in ('+','-','+-'):raise ValueError('Direction must be +, -, or +-.')
    return shared_limit(math_expr(v),math_symbol(v),math_expr(v,'point'),side)
@reg('series','Taylor series','Taylor / Laurent expansion around a point.',[field('expression','Expression','exp(x)'),V,field('around','Around','0'),field('order','Terms before O(x^n)','6')])
def series(v):return shared_series(math_expr(v),math_symbol(v),math_expr(v,'around'),math_int(v,'order',1,18))
@reg('partial','Partial derivative','Differentiate with respect to any variable.',[field('expression','Expression','x^2*y+sin(y)'),field('variable','With respect to','y'),field('order','Order','1')])
def partial(v):return differentiate(v)
@reg('ode','First-order ODE','Solve dy/dx = f(x,y). Write the right-hand side using y, not y(x).',[field('expression','dy/dx =','y'),field('variable','Independent variable','x')])
def ode(v):
    x=math_symbol(v); y=sp.Symbol('y'); Y=sp.Function('y')(x)
    f=math_expr(v).subs(y,Y)
    return sp.dsolve(sp.Eq(sp.diff(Y,x),f),Y)


def variable_list(v):
    tokens=[token.strip() for token in str(v.get('variables','')).split(',')]
    if not 1<=len(tokens)<=4 or len(set(tokens))!=len(tokens):
        raise ValueError('Enter 1–4 distinct variables separated by commas.')
    return [math_symbol({'variable':token}) for token in tokens]

@reg('gradient','Gradient','Gradient of a scalar field in coordinate variables.',[field('expression','Scalar field','x^2*y+y^2'),field('variables','Variables','x,y')])
def gradient(v):
    variables=variable_list(v); scalar=math_expr(v)
    return sp.Matrix([sp.diff(scalar,x) for x in variables])

@reg('hessian','Hessian','Matrix of second-order partial derivatives.',[field('expression','Scalar field','x^2*y+y^2'),field('variables','Variables','x,y')])
def hessian(v):
    return sp.hessian(math_expr(v),variable_list(v))

@reg('jacobian','Jacobian','Jacobian of a vector-valued function.',[field('expressions','Vector of expressions','[x*y,x^2+y]'),field('variables','Variables','x,y')])
def jacobian(v):
    raw=math_expr(v,'expressions')
    if not isinstance(raw,list) or any(isinstance(x,list) for x in raw):
        raise ValueError('Vector expressions must look like [x*y,x^2+y].')
    return sp.Matrix(raw).jacobian(variable_list(v))
