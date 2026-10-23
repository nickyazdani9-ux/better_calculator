"""Mathematical invariants for cross-domain chart and tensor composition."""
import sys
from pathlib import Path
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from workspace import Workspace


def execute(*steps):
    w = Workspace()
    out = w.handle({'command': 'batch', 'steps': list(steps)})
    assert out['ok'], out
    return w


def zero(expr):
    assert sp.simplify(expr) == 0


def test_euclidean_cartesian_to_polar_complex_field_chain():
    w = execute(
        {'command': 'define', 'id': 'f', 'expression': '(x+I*y)^2',
         'coordinates': ['x','y'], 'metric': '[[1,0],[0,1]]'},
        {'command': 'apply', 'source': 'f', 'id': 'polar',
         'operation': 'change_coordinates', 'coordinates': ['r','theta'],
         'mapping': ['r*cos(theta)', 'r*sin(theta)']},
        {'command': 'apply', 'source': 'polar', 'id': 'dpolar', 'operation':'exterior_derivative'},
        {'command': 'apply', 'source': 'dpolar', 'id': 'squared', 'operation':'norm_squared'},
    )
    r,t=sp.symbols('r theta', real=True)
    for i in range(2):
        for j in range(2):
            zero(w.nodes['polar'].metric[i,j] - (r**2 if i==j==1 else 1 if i==j==0 else 0))
    zero(w.nodes['polar'].value - r**2*(sp.cos(t)+sp.I*sp.sin(t))**2)
    zero(w.nodes['squared'].value-8*r*r)
    assert w.nodes['polar'].coords == (r,t)


def test_vector_covector_duality_and_transformed_tensor_contraction():
    w = execute(
        {'command':'define','id':'v','kind':'vector','components':'[x,y]',
         'coordinates':['x','y'],'metric':'[[1,0],[0,1]]'},
        {'command':'define','id':'w','kind':'covector','components':'[2*x,3*y]',
         'coordinates':['x','y'],'metric':'[[1,0],[0,1]]'},
        {'command':'apply','id':'pair','source':'v','other':'w','operation':'pair'},
        {'command':'apply','id':'tensor','source':'v','other':'w','operation':'tensor_product'},
        {'command':'apply','id':'contraction','source':'tensor','operation':'contract'},
        {'command':'apply','id':'vp','source':'v','operation':'change_coordinates',
         'coordinates':['r','theta'],'mapping':['r*cos(theta)','r*sin(theta)']},
        {'command':'apply','id':'wp','source':'w','operation':'change_coordinates',
         'coordinates':['r','theta'],'mapping':['r*cos(theta)','r*sin(theta)']},
        {'command':'apply','id':'tp','source':'tensor','operation':'change_coordinates',
         'coordinates':['r','theta'],'mapping':['r*cos(theta)','r*sin(theta)']},
        {'command':'apply','id':'pairp','source':'vp','other':'wp','operation':'pair'},
        {'command':'apply','id':'contractp','source':'tp','operation':'contract'},
    )
    x,y=sp.symbols('x y',real=True)
    r,t=sp.symbols('r theta',real=True)
    zero(w.nodes['pair'].value - (2*x*x+3*y*y))
    zero(w.nodes['contraction'].value - w.nodes['pair'].value)
    zero(w.nodes['vp'].value[0] - r)
    zero(w.nodes['vp'].value[1])
    target = (2*sp.cos(t)**2+3*sp.sin(t)**2)*r*r
    zero(w.nodes['pairp'].value - target)
    zero(w.nodes['contractp'].value - target)
    assert w.nodes['tensor'].variance == ('up','down')
    assert w.nodes['tp'].variance == ('up','down')
    assert w.nodes['pairp'].kind == 'scalar_field'


def test_metric_musical_maps_roundtrip():
    w = execute(
        {'command':'define','id':'w','kind':'covector','components':'[a, b]',
         'coordinates':['r','theta'], 'metric':'[[1,0],[0,r^2]]'},
        {'command':'apply','id':'v','source':'w','operation':'raise_index'},
        {'command':'apply','id':'back','source':'v','operation':'lower_index'},
    )
    a,b=sp.symbols('a b')
    assert w.nodes['v'].kind == 'vector'
    assert w.nodes['back'].kind == 'covector'
    assert list(w.nodes['back'].value) == [a,b]


def test_invalid_tensor_contraction_and_singular_chart_rejected():
    w=Workspace()
    w.define({'id':'v','kind':'vector','components':'[1,2]', 'coordinates':['x','y']})
    w.define({'id':'w','kind':'vector','components':'[3,4]', 'coordinates':['x','y']})
    t=w.handle({'command':'apply','id':'t','source':'v','other':'w','operation':'tensor_product'})
    assert t['ok'],t
    con=w.handle({'command':'apply','id':'bad','source':'t','operation':'contract'})
    assert not con['ok'] and 'upper' in con['error']
    singular=w.handle({'command':'apply','id':'sing','source':'v','operation':'change_coordinates',
                       'coordinates':['u','v'],'mapping':['u','u']})
    assert not singular['ok'] and 'singular' in singular['error']
    blocked=w.handle({'command':'apply','id':'nope','source':'v','operation':'change_coordinates',
                       'coordinates':['u','v'],'mapping':['u','y']})
    assert not blocked['ok'] and 'only on' in blocked['error']
