"""TDD acceptance tests for durable, guarded workspace graph snapshots."""
import json

import sympy as sp

from workspace import Workspace


def calculation():
    w = Workspace()
    out = w.handle({'command': 'batch', 'steps': [
        {'command': 'define', 'id': 'f', 'expression': '(x+I*y)^2',
         'coordinates': ['x', 'y'], 'metric': '[[1,0],[0,1]]'},
        {'command': 'apply', 'id': 'df', 'source': 'f',
         'operation': 'exterior_derivative'},
        {'command': 'apply', 'id': 'squared', 'source': 'df',
         'operation': 'norm_squared'},
        {'command': 'apply', 'id': 'expected', 'source': 'squared',
         'operation': 'expectation', 'independent': True,
         'normals': {'x': {'mean': '0', 'std': '1'},
                     'y': {'mean': '0', 'std': '1'}}},
    ]})
    assert out['ok'], out
    return w


def test_export_import_recovers_cross_domain_graph_and_result():
    original = calculation()
    exported = original.handle({'command': 'export'})
    assert exported['ok'], exported
    snapshot = json.loads(json.dumps(exported['snapshot']))
    assert snapshot['format'] == 'calculator2.workspace'
    assert snapshot['version'] == 1
    assert len(snapshot['steps']) == 4

    fresh = Workspace()
    imported = fresh.handle({'command': 'import', 'snapshot': snapshot})
    assert imported['ok'], imported
    assert fresh.nodes.keys() == original.nodes.keys()
    for key in original.nodes:
        before, after = original.nodes[key], fresh.nodes[key]
        assert before.kind == after.kind
        assert before.parents == after.parents
        assert before.coords == after.coords
        assert before.metric == after.metric
        assert before.variance == after.variance
        assert before.value == after.value
    assert fresh.nodes['expected'].value == 16
    assert fresh.handle({'command': 'export'})['snapshot'] == snapshot


def test_import_replaces_workspace_not_appends():
    workspace = Workspace()
    assert workspace.handle({'command': 'define', 'id': 'old',
                             'expression': '42'})['ok']
    snapshot = calculation().handle({'command': 'export'})['snapshot']
    out = workspace.handle({'command': 'import', 'snapshot': snapshot})
    assert out['ok'], out
    assert 'old' not in workspace.nodes
    assert workspace.nodes['expected'].value == 16


def test_failed_import_rolls_back_everything_including_journal():
    workspace = calculation()
    original = workspace.handle({'command': 'export'})['snapshot']
    broken = json.loads(json.dumps(original))
    broken['steps'].append({'command': 'apply', 'id': 'bad',
                            'source': 'nonexistent', 'operation': 'simplify'})
    out = workspace.handle({'command': 'import', 'snapshot': broken})
    assert not out['ok'], out
    assert workspace.handle({'command': 'export'})['snapshot'] == original
    assert list(workspace.nodes) == ['f', 'df', 'squared', 'expected']


def test_failed_batch_leaves_no_ghost_commands():
    workspace = Workspace()
    result = workspace.handle({'command': 'batch', 'steps': [
        {'command': 'define', 'id': 'temp', 'expression': 'x'},
        {'command': 'apply', 'id': 'bad', 'source': 'temp',
         'operation': 'raise_index'},
    ]})
    assert not result['ok'], result
    out = workspace.handle({'command': 'export'})
    assert out['ok'] and out['snapshot']['steps'] == []
    assert workspace.nodes == {}


def test_snapshot_is_detached_from_callers():
    workspace = calculation()
    snap = workspace.handle({'command': 'export'})['snapshot']
    snap['steps'][0]['expression'] = '9999'
    snap['steps'][3]['normals']['x']['mean'] = '100'
    assert workspace.nodes['f'].value != 9999
    fresh = workspace.handle({'command': 'export'})['snapshot']
    assert fresh['steps'][0]['expression'] == '(x+I*y)^2'
    assert fresh['steps'][3]['normals']['x']['mean'] == '0'


def test_invalid_versions_or_non_command_payloads_are_not_deserialized():
    workspace = calculation()
    baseline = workspace.handle({'command': 'export'})['snapshot']
    for payload in [
        {'format': 'calculator2.workspace', 'version': 999, 'steps': []},
        {'format': 'not-ours', 'version': 1, 'steps': []},
        {'format': 'calculator2.workspace', 'version': 1, 'steps': [
            {'command': 'reset'}]},
        {'format': 'calculator2.workspace', 'version': 1, 'steps': [
            {'command': 'define', 'id': 'x', 'expression': '__import__("os")'}]},
        {'format': 'calculator2.workspace', 'version': 1, 'steps': [
            {'command': 'define', 'id': 'x', 'expression': '1', 'mystery': 'junk'}]},
    ]:
        out = workspace.handle({'command': 'import', 'snapshot': payload})
        assert not out['ok'], payload
        assert workspace.handle({'command': 'export'})['snapshot'] == baseline


def test_reset_clears_persistent_graph_too():
    workspace = calculation()
    assert workspace.handle({'command': 'reset'})['ok']
    assert workspace.handle({'command': 'export'})['snapshot']['steps'] == []
    assert workspace.handle({'command': 'graph'})['nodes'] == []
