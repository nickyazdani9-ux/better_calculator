import sympy as sp
from engine import register,field,math_expr,math_symbol
TAB=('complex','Complex analysis','orbit')
def reg(op,label,desc,fields):return register(*TAB,op,label,desc,fields)
E=field('expression','f(z)','1/(z-2)')
Z=field('variable','Complex variable','z')
@reg('simplify','Simplify complex','Simplify expression with complex variables.',[field('expression','Expression','(1+I)^2')])
def simplify(v):return sp.simplify(math_expr(v))
@reg('parts','Real / imaginary','Extract real, imaginary, modulus, and argument.',[field('expression','Complex expression','3+4*I')])
def parts(v):
    z=sp.simplify(math_expr(v))
    extra={'real':str(sp.re(z)),'imaginary':str(sp.im(z)),'modulus':str(sp.Abs(z)),'argument':str(sp.arg(z))}
    return {'expression':z,'lines':[f'{k}: {value}' for k,value in extra.items()],'extras':extra}
@reg('derivative','Complex derivative','Formal complex differentiation of an analytic expression.',[field('expression','f(z)','exp(z)*sin(z)'),Z])
def derivative(v):return sp.diff(math_expr(v),math_symbol(v))
@reg('residue','Residue','Residue at an isolated singularity.',[E,Z,field('point','Pole location','2')])
def residue(v):return sp.residue(math_expr(v),math_symbol(v),math_expr(v,'point'))
@reg('series','Laurent series','Series about a complex point.',[E,Z,field('point','Center','2'),field('order','Series order','4')])
def series(v):
    from engine import math_int
    return sp.series(math_expr(v),math_symbol(v),math_expr(v,'point'),math_int(v,'order',1,16))
@reg('cauchy_riemann','Cauchy–Riemann','Check Cauchy–Riemann conditions symbolically (necessary, not sufficient alone for analyticity).',[field('expression','f(z)','z^2')])
def cauchy_riemann(v):
    z=sp.Symbol('z'); x,y=sp.symbols('x y',real=True)
    expr=sp.expand_complex(math_expr(v).subs(z,x+sp.I*y))
    u=sp.simplify(sp.re(expr)); w=sp.simplify(sp.im(expr))
    first=sp.simplify(sp.diff(u,x)-sp.diff(w,y))
    second=sp.simplify(sp.diff(u,y)+sp.diff(w,x))
    analytic=first==0 and second==0
    return {'expression':first**2+second**2,'lines':[f'u = {u}',f'v = {w}',f'u_x - v_y = {first}',f'u_y + v_x = {second}',f'CR identities satisfied symbolically: {analytic}'], 'extras':{'analytic':bool(analytic),'first':str(first),'second':str(second)}}
