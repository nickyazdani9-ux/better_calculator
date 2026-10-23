"""Cross-domain acceptance tests for the composable mathematical workspace."""
import json
import sys
from pathlib import Path

import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'python'))
from engine import run_json
from workspace import Workspace


def test_geometry_complex_probability_composition():
    workspace = Workspace()
    result = workspace.handle({'command': 'batch', 'steps': [
        {'command': 'define', 'id': 'f', 'expression': '(x+I*y)^2',
         'coordinates': ['x', 'y'], 'metric': '[[1,0],[0,1]]'},
        {'command': 'apply', 'id': 'df', 'source': 'f',
         'operation': 'exterior_derivative'},
        {'command': 'apply', 'id': 'length', 'source': 'df',
         'operation': 'norm_squared'},
        {'command': 'apply', 'id': 'mean', 'source': 'length',
         'operation': 'expectation', 'independent': True,
         'normals': {'x': {'mean': '0', 'std': '1'},
                     'y': {'mean': '0', 'std': '1'}}},
    ]})
    assert result['ok'], result
    assert result['results'][1]['node']['kind'] == 'covector'
    x, y = sp.symbols('x y', real=True)
    assert sp.simplify(workspace.nodes['length'].value - 8*(x*x + y*y)) == 0
    assert workspace.nodes['mean'].value == 16
    assert workspace.nodes['mean'].parents == ('length',)
    assert workspace.nodes['mean'].coords == ()


def test_complex_and_linear_algebra_outputs_can_combine():
    workspace = Workspace()
    result = workspace.handle({'command': 'batch', 'steps': [
        {'command': 'define', 'id': 'f', 'expression': '1/(z-2)'},
        {'command': 'apply', 'id': 'res', 'source': 'f', 'operation': 'residue',
         'variable': 'z', 'point': '2'},
        {'command': 'define', 'id': 'm', 'kind': 'matrix', 'matrix': '[[1,2],[3,4]]'},
        {'command': 'apply', 'id': 'det', 'source': 'm', 'operation': 'determinant'},
        {'command': 'apply', 'id': 'sum', 'source': 'res', 'operation': 'add',
         'other': 'det'},
    ]})
    assert result['ok'], result
    assert workspace.nodes['sum'].value == -1
    assert workspace.nodes['sum'].parents == ('res', 'det')


def test_metric_required_and_coordinates_checked():
    workspace = Workspace()
    assert workspace.handle({'command': 'define', 'id': 'f',
                             'expression': 'x^2', 'coordinates': ['x']})['ok']
    assert workspace.handle({'command': 'apply', 'id': 'df',
                             'source': 'f', 'operation': 'exterior_derivative'})['ok']
    out = workspace.handle({'command': 'apply', 'id': 'n',
                            'source': 'df', 'operation': 'norm_squared'})
    assert not out['ok'] and 'metric' in out['error']
    assert not workspace.handle({'command': 'define', 'id': 'bad',
                                 'expression': 'x', 'coordinates': ['x'],
                                 'metric': '[[0]]'})['ok']
    assert workspace.handle({'command': 'define', 'id': 'other',
                             'expression': 'y', 'coordinates': ['y']})['ok']
    out = workspace.handle({'command': 'apply', 'id': 'invalid',
                            'source': 'f', 'other': 'other', 'operation': 'add'})
    assert not out['ok'] and 'coordinate' in out['error']


def test_batch_failure_is_atomic_and_parser_is_guarded():
    workspace = Workspace()
    out = workspace.handle({'command': 'batch', 'steps': [
        {'command': 'define', 'id': 'first', 'expression': '2'},
        {'command': 'apply', 'id': 'invalid', 'source': 'first',
         'operation': 'determinant'},
    ]})
    assert not out['ok'] and out['failed_step'] == 1
    assert workspace.nodes == {}
    assert not workspace.handle({'command': 'define', 'id': 'attack',
                                 'expression': '__import__("os")'})['ok']


def test_probabilistic_assumptions_are_explicit():
    workspace = Workspace()
    assert workspace.handle({'command': 'define', 'id': 'f', 'expression': 'x^2'})['ok']
    out = workspace.handle({'command': 'apply', 'id': 'mean', 'source': 'f',
                            'operation': 'expectation',
                            'normals': {'x': {'mean': '0', 'std': '1'}}})
    assert not out['ok'] and 'independent' in out['error']


def test_unscoped_symbols_not_mistaken_for_real_coordinates():
    workspace = Workspace()
    workspace.define({'id': 'field', 'expression': 'x', 'coordinates': ['x']})
    workspace.define({'id': 'symbol', 'expression': 'x'})
    out = workspace.handle({'command': 'apply', 'id': 'sum', 'source': 'field',
                            'other': 'symbol', 'operation': 'add'})
    assert not out['ok'] and 'assumptions' in out['error']


def test_workspace_json_boundary_and_legacy_calculator():
    assert json.loads(run_json(json.dumps({'action': 'workspace',
                                          'command': 'reset'})))['ok']
    definition = json.loads(run_json(json.dumps({
        'action': 'workspace', 'command': 'define',
        'id': 'a', 'expression': 'x^2'})))
    assert definition['ok'] and definition['node']['kind'] == 'scalar'
    answer = json.loads(run_json(json.dumps({
        'action': 'workspace', 'command': 'apply', 'id': 'b',
        'source': 'a', 'operation': 'differentiate', 'variable': 'x'})))
    assert answer['ok'] and answer['node']['expr'] == '2*x'
    legacy = json.loads(run_json(json.dumps({
        'tab': 'basic', 'operation': 'evaluate',
        'values': {'expression': '1/3+1/6'}})))
    assert legacy['ok'] and legacy['expr'] == '1/2'
