"""Acceptance tests defined before engine implementation (TDD)."""
import json
import sys
from pathlib import Path
import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from engine import calculate, operation_catalog, parse_math


def request(tab, operation, **values):
    return calculate({'tab': tab, 'operation': operation, 'values': values})


def symbolic(tab, operation, expected, **values):
    outcome = request(tab, operation, **values)
    assert outcome['ok'], outcome
    assert sp.simplify(sp.sympify(outcome['expr']) - sp.sympify(expected)) == 0


def test_registry_is_extensible_and_has_required_tabs():
    catalog = operation_catalog()
    assert {'basic', 'calculus', 'complex', 'geometry', 'waves', 'linear'} <= {x['id'] for x in catalog}
    assert all(tab['operations'] for tab in catalog)
    assert all(op['fields'] for tab in catalog for op in tab['operations'])


def test_parser_arithmetic_exact_and_powers():
    assert parse_math('1/3 + 1/6') == sp.Rational(1, 2)
    assert sp.simplify(parse_math('x^2 + 2*x + 1') - (sp.Symbol('x') + 1)**2)==0


@pytest.mark.parametrize('payload', [
    '__import__("os").system("echo nope")',
    '().__class__.__base__',
    'open("/etc/passwd")',
    'x[0]',
    '[x for x in range(9)]',
    '2**999999',
])
def test_parser_rejects_unsafe_expressions(payload):
    with pytest.raises(ValueError):
        parse_math(payload)


def test_calculus_derivative_integral_and_limit():
    symbolic('calculus','differentiate','3*x**2 + cos(x)',expression='x^3+sin(x)',variable='x',order='1')
    symbolic('calculus','integrate','x**3/3',expression='x^2',variable='x',lower='',upper='')
    symbolic('calculus','limit','1',expression='sin(x)/x',variable='x',point='0',direction='+-')


def test_calculus_definite_integral_and_series():
    symbolic('calculus','integrate','2',expression='x',variable='x',lower='0',upper='2')
    result=request('calculus','series',expression='exp(x)',variable='x',around='0',order='4')
    assert result['ok'] and 'x**3/6' in result['expr']


def test_complex_residue_and_cauchy_riemann():
    symbolic('complex','residue','1',expression='1/(z-2)',variable='z',point='2')
    result=request('complex','cauchy_riemann',expression='z^2')
    assert result['ok'] and result['extras']['analytic'] is True
    result=request('complex','cauchy_riemann',expression='conjugate(z)')
    assert result['ok'] and result['extras']['analytic'] is False


def test_complex_parts():
    result=request('complex','parts',expression='3+4*I')
    assert result['ok'] and result['extras']['real']=='3' and result['extras']['imaginary']=='4'


def test_plane_in_polar_coordinates_is_flat():
    metric='[[1,0],[0,r^2]]'
    symbolic('geometry','scalar_curvature','0',coordinates='r,theta',metric=metric)
    result=request('geometry','christoffel',coordinates='r,theta',metric=metric)
    assert result['ok'], result
    assert any('Gamma^r_{theta theta}' in line and '-r' in line for line in result['lines'])
    assert any('Gamma^theta_{r theta}' in line and '1/r' in line for line in result['lines'])


def test_unit_sphere_curvature_and_ricci():
    m='[[1,0],[0,sin(theta)^2]]'
    symbolic('geometry','scalar_curvature','2',coordinates='theta,phi',metric=m)
    res=request('geometry','ricci',coordinates='theta,phi',metric=m)
    assert res['ok'], res
    assert res['expr']=='Matrix([[1, 0], [0, sin(theta)**2]])'


def test_geometry_covariant_derivative():
    res=request('geometry','covariant_derivative',coordinates='r,theta',metric='[[1,0],[0,r^2]]',vector='[0,1]',direction='r')
    assert res['ok'],res
    assert res['expr']=='Matrix([[0], [1/r]])'


def test_laplace_and_fourier():
    symbolic('waves','laplace','1/(s+1)',expression='exp(-t)',variable='t',frequency='s')
    symbolic('waves','fourier','exp(-pi*k**2)',expression='exp(-pi*x^2)',variable='x',frequency='k')


def test_linear_algebra():
    symbolic('linear','determinant','-2',matrix='[[1,2],[3,4]]')
    result=request('linear','eigenvalues',matrix='[[2,0],[0,3]]')
    assert result['ok'] and '2' in result['lines'][0] and '3' in result['lines'][1]


def test_errors_return_structured_failure():
    assert request('calculus','differentiate',expression='x',variable='not a var',order='1')['ok'] is False
    assert request('geometry','scalar_curvature',coordinates='x,y',metric='[[1,0],[0,0]]')['ok'] is False
    assert request('calculus','NOPE',expression='x')['ok'] is False


def test_json_boundary():
    from engine import run_json
    result=json.loads(run_json(json.dumps({'tab':'basic','operation':'simplify','values':{'expression':'2/4'}})))
    assert result['ok'] and result['expr']=='1/2'


def test_symbolic_exponents_supported():
    x,y=sp.symbols('x y')
    assert parse_math('x^y')==x**y


def test_sphere_riemann_component_and_einstein_tensor():
    base={'coordinates':'theta,phi','metric':'[[1,0],[0,sin(theta)^2]]'}
    result=request('geometry','riemann_component',**base,a='0',b='1',c='0',d='1')
    assert result['ok']
    theta=sp.Symbol('theta')
    assert sp.simplify(sp.sympify(result['expr'])-sp.sin(theta)**2)==0
    flat=request('geometry','einstein',**base)
    assert flat['ok'] and flat['expr']=='Matrix([[0, 0], [0, 0]])'


def test_geodesics_and_ode():
    result=request('geometry','geodesic',coordinates='r,theta',metric='[[1,0],[0,r^2]]')
    assert result['ok'] and len(result['lines'])==2
    assert 'd2_r' in result['lines'][0]
    sol=request('calculus','ode',expression='y',variable='x')
    assert sol['ok'] and 'exp(x)' in sol['expr']


def test_wrong_metric_shape_rejected():
    bad=request('geometry','scalar_curvature',coordinates='x,y,z',metric='[[1,0],[0,1]]')
    assert not bad['ok']


def test_multivariate_calculus_gradient_hessian_jacobian():
    values={'expression':'x^2*y + y^2', 'variables':'x,y'}
    result=request('calculus','gradient',**values)
    assert result['ok'] and result['expr']=='Matrix([[2*x*y], [x**2 + 2*y]])'
    hessian=request('calculus','hessian',**values)
    assert hessian['ok'] and hessian['expr']=='Matrix([[2*y, 2*x], [2*x, 2]])'
    jacobian=request('calculus','jacobian',expressions='[x*y,x^2+y]',variables='x,y')
    assert jacobian['ok'] and jacobian['expr']=='Matrix([[y, x], [2*x, 1]])'
