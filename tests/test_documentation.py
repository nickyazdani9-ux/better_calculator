"""Executable documentation contracts; part of the ordinary Python CI suite."""
import json
import re
import sys
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
sys.path.insert(0, str(ROOT / "scripts"))
from workspace import Workspace, OPERATION_SIGNATURES
from export_legacy_docs import render

DOCUMENTS = (
    "docs/README.md", "docs/GETTING_STARTED.md", "docs/CONCEPTS.md",
    "docs/API.md", "docs/LEGACY_API.md", "docs/RECIPES.md",
    "docs/TROUBLESHOOTING.md", "docs/DOCS_MAINTENANCE.md",
)


def test_documentation_links_exist():
    for relative in DOCUMENTS:
        path = ROOT / relative
        for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
            destination = link.split('#', 1)[0].split('?', 1)[0]
            if destination and not destination.startswith(('http:', 'https:', 'mailto:')):
                assert (path.parent / destination).exists(), f'{relative} -> {link}'


def test_unified_api_reference_matches_operation_registry():
    reference = (ROOT / "docs/API.md").read_text(encoding="utf-8")
    section = reference.split("## Operations\n", 1)[1].split("### Coordinate-change example", 1)[0]
    listed = set(re.findall(r"\| `([a-z_]+)` \|", section))
    assert listed == set(OPERATION_SIGNATURES), (set(OPERATION_SIGNATURES)-listed, listed-set(OPERATION_SIGNATURES))
    for command in ('define', 'apply', 'get', 'graph', 'operations', 'batch',
                    'export', 'import', 'reset'):
        assert f'| `{command}` |' in reference


def test_legacy_reference_is_generated_not_hand_edited():
    catalog = json.loads((ROOT / 'assets/catalog.json').read_text(encoding='utf-8'))
    text = (ROOT / 'docs/LEGACY_API.md').read_text(encoding='utf-8')
    assert text == render(catalog), 'Run python3 scripts/export_legacy_docs.py'


def test_api_json_examples_parse():
    reference = (ROOT / 'docs/API.md').read_text(encoding='utf-8')
    snippets = re.findall(r'~~~json\s*\n(.*?)\n~~~', reference, flags=re.DOTALL)
    assert len(snippets) >= 4
    for snippet in snippets:
        assert isinstance(json.loads(snippet), dict)


def test_recipes_execute_and_restore_exact_graphs():
    expected = {
        'linear_complex_calculus': ('integrated', 7*sp.Symbol('t')**2),
        'geometry_tensor_calculus': ('radial', 2*sp.Symbol('r', real=True)),
        'complex_geometry_probability': ('expected', sp.Integer(16)),
    }
    for name, (node_id, value) in expected.items():
        request = json.loads((ROOT / 'docs/examples' / (name+'.json')).read_text(encoding='utf-8'))
        assert request['command']=='batch' and len(request['steps'])>=4
        workspace=Workspace()
        result=workspace.handle(request)
        assert result['ok'], (name, result)
        assert sp.simplify(workspace.nodes[node_id].value-value)==0, name
        assert workspace.nodes[node_id].parents
        snapshot=workspace.handle({'command':'export'})['snapshot']
        restored=Workspace()
        reply=restored.handle({'command':'import','snapshot':snapshot})
        assert reply['ok'], (name, reply)
        assert restored.handle({'command':'export'})['snapshot']==snapshot
        assert restored.nodes[node_id].parents==workspace.nodes[node_id].parents
