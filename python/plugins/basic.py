import sympy as sp
from engine import register,field,math_expr,math_symbol

E=field('expression','Expression','(x^2-1)/(x-1)',hint='Use ^ for powers, * for multiplication')
@register('basic','Calculator','calculator','simplify','Simplify','Simplify an exact symbolic expression.',[E])
def simplify(v): return sp.simplify(math_expr(v))
@register('basic','Calculator','calculator','evaluate','Evaluate','Evaluate with exact arithmetic.',[field('expression','Expression','1/3 + 1/6')])
def evaluate(v): return sp.simplify(math_expr(v))
@register('basic','Calculator','calculator','approximate','Decimal','Numerical approximation.',[field('expression','Expression','pi*sqrt(2)'),field('digits','Digits','12')])
def approximate(v):
    from engine import math_int
    return sp.N(math_expr(v),math_int(v,'digits',2,30))
@register('basic','Calculator','calculator','factor','Factor','Factor a polynomial.',[field('expression','Expression','x^2-1')])
def factor(v): return sp.factor(math_expr(v))
@register('basic','Calculator','calculator','expand','Expand','Expand algebraic products.',[field('expression','Expression','(x+1)^3')])
def expand(v): return sp.expand(math_expr(v))
@register('basic','Calculator','calculator','solve','Solve','Solve expression = 0 for a variable.',[field('expression','Expression','x^2-4'),field('variable','Variable','x')])
def solve(v):
    result=sp.solve(math_expr(v),math_symbol(v))
    return {'lines':[str(x) for x in result], 'latex':sp.latex(result)}
