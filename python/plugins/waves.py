import sympy as sp
from engine import register,field,math_expr,math_symbol
TAB=('waves','Transforms & waves','waves')
def reg(op,label,desc,fields):return register(*TAB,op,label,desc,fields)
@reg('fourier','Fourier transform','Convention F(k) = ∫ f(x) exp(-2πi kx) dx.',[field('expression','f(x)','exp(-pi*x^2)'),field('variable','Input variable','x'),field('frequency','Frequency variable','k')])
def fourier(v):return sp.fourier_transform(math_expr(v),math_symbol(v,'variable'),math_symbol(v,'frequency'))
@reg('inverse_fourier','Inverse Fourier','Inverse with the 2π convention.',[field('expression','F(k)','exp(-pi*k^2)'),field('variable','Frequency variable','k'),field('frequency','Output variable','x')])
def inverse_fourier(v):return sp.inverse_fourier_transform(math_expr(v),math_symbol(v,'variable'),math_symbol(v,'frequency'))
@reg('laplace','Laplace transform','One-sided Laplace transform.',[field('expression','f(t)','exp(-t)'),field('variable','Time variable','t'),field('frequency','Laplace variable','s')])
def laplace(v):return sp.laplace_transform(math_expr(v),math_symbol(v,'variable'),math_symbol(v,'frequency'),noconds=True)
@reg('inverse_laplace','Inverse Laplace','Inverse one-sided Laplace transform.',[field('expression','F(s)','1/(s+1)'),field('variable','Laplace variable','s'),field('frequency','Time variable','t')])
def inverse_laplace(v):return sp.inverse_laplace_transform(math_expr(v),math_symbol(v,'variable'),math_symbol(v,'frequency'))
