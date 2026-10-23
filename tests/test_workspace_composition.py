"""Composability is driven by object compatibility, never by a fixed subject order.

These acceptance cases deliberately mix mathematical families in unrelated
sequences, branch intermediate results, and rejoin them using typed references.
"""
import sys
from pathlib import Path
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from workspace import Workspace


def chain(*steps):
    w=Workspace()
    response=w.handle({'command':'batch','steps':list(steps)})
    assert response['ok'], response
    return w


def test_complex_to_linear_to_algebra_to_calculus_in_any_sequence():
    w=chain(
        {'command':'define','id':'meromorphic','expression':'1/(z-2)'},
        {'command':'apply','id':'residue','source':'meromorphic',
         'operation':'residue','variable':'z','point':'2'},
        {'command':'define','id':'matrix','kind':'matrix','matrix':'[[2,0],[0,3]]'},
        {'command':'apply','id':'det','source':'matrix','operation':'determinant'},
        {'command':'apply','id':'seven','source':'residue','other':'det','operation':'add'},
        {'command':'define','id':'polynomial','expression':'t^2'},
        {'command':'apply','id':'product','source':'seven','other':'polynomial',
         'operation':'multiply'},
        {'command':'apply','id':'derivative','source':'product','operation':'differentiate',
         'variable':'t'},
        {'command':'apply','id':'integral','source':'derivative','operation':'integrate',
         'variable':'t'},
    )
    t=sp.Symbol('t')
    assert sp.simplify(w.nodes['integral'].value-7*t**2)==0
    assert w.nodes['product'].parents==('seven','polynomial')
    assert w.nodes['derivative'].parents==('product',)
    assert w.nodes['integral'].operation=='integrate'


def test_geometry_tensor_to_calculus_reverses_previous_example():
    w=chain(
        {'command':'define','id':'f','expression':'x*y',
         'coordinates':['x','y'],'metric':'[[1,0],[0,1]]'},
        {'command':'apply','id':'df','source':'f','operation':'exterior_derivative'},
        {'command':'apply','id':'v','source':'df','operation':'raise_index'},
        {'command':'apply','id':'tensor','source':'v','other':'df','operation':'tensor_product'},
        {'command':'apply','id':'trace','source':'tensor','operation':'contract'},
        {'command':'apply','id':'polar','source':'trace','operation':'change_coordinates',
         'coordinates':['r','theta'],
         'mapping':['r*cos(theta)','r*sin(theta)']},
        {'command':'apply','id':'derived','source':'polar','operation':'differentiate','variable':'r'},
    )
    r, theta=sp.symbols('r theta',real=True)
    assert sp.simplify(w.nodes['derived'].value-2*r)==0
    assert w.nodes['tensor'].variance==('up','down')
    assert w.nodes['polar'].kind=='scalar_field'
    assert w.nodes['derived'].coords==(r,theta)


def test_unrelated_branch_results_can_merge_and_invalid_merge_is_blocked():
    w=chain(
        {'command':'define','id':'x','expression':'x'},
        {'command':'apply','id':'squared','source':'x','other':'x','operation':'multiply'},
        {'command':'apply','id':'derived','source':'squared',
         'operation':'differentiate','variable':'x'},
        {'command':'apply','id':'integrated','source':'derived',
         'operation':'integrate','variable':'x'},
        {'command':'define','id':'matrix','kind':'matrix','matrix':'[[1,0],[0,5]]'},
        {'command':'apply','id':'five','source':'matrix','operation':'determinant'},
        {'command':'apply','id':'joined','source':'integrated',
         'other':'five','operation':'add'},
    )
    x=sp.Symbol('x')
    assert sp.simplify(w.nodes['joined'].value-x*x-5)==0
    assert w.nodes['joined'].parents==('integrated','five')
    invalid=w.handle({'command':'apply','id':'invalid','source':'joined',
                      'other':'matrix','operation':'add'})
    assert not invalid['ok']
    assert 'invalid' not in w.nodes


def test_snapshot_of_arbitrary_chain_restores_all_references():
    initial=chain(
        {'command':'define','id':'m','kind':'matrix','matrix':'[[4,0],[0,2]]'},
        {'command':'apply','id':'det','source':'m','operation':'determinant'},
        {'command':'define','id':'function','expression':'z/(z-1)'},
        {'command':'apply','id':'complex','source':'function',
         'operation':'residue','variable':'z','point':'1'},
        {'command':'apply','id':'added','source':'det','other':'complex','operation':'add'},
        {'command':'apply','id':'factored','source':'added','operation':'factor'},
    )
    snapshot=initial.handle({'command':'export'})['snapshot']
    restored=Workspace()
    assert restored.handle({'command':'import','snapshot':snapshot})['ok']
    assert restored.nodes['factored'].value==9
    assert restored.nodes['added'].parents==('det','complex')
    assert restored.handle({'command':'export'})['snapshot']==snapshot
