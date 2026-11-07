"""Reserved mathematical names must not masquerade as workspace variables."""
import pytest
from engine import CONSTANTS, FUNCTIONS
from workspace import Workspace, symbol

@pytest.mark.parametrize("name", sorted(set(CONSTANTS) | set(FUNCTIONS)))
def test_reserved_names_are_rejected_as_variables(name):
    with pytest.raises(ValueError, match="variable name"):
        symbol(name)

def test_e_coordinate_is_rejected_without_creating_constant_field():
    w = Workspace()
    result = w.handle({"command": "define", "id": "f", "expression": "e^2", "coordinates": ["e"]})
    assert not result["ok"]
    assert not w.nodes
    assert w.handle({"command": "export"})["snapshot"]["steps"] == []

def test_ordinary_coordinate_derivative_survives_snapshot_replay():
    w = Workspace()
    assert w.handle({"command": "define", "id": "f", "expression": "u^2", "coordinates": ["u"]})["ok"]
    result = w.handle({"command": "apply", "id": "df", "source": "f", "operation": "differentiate", "variable": "u"})
    assert result["ok"] and result["node"]["expr"] == "2*u"
    fresh = Workspace()
    assert fresh.handle({"command": "import", "snapshot": w.handle({"command": "export"})["snapshot"]})["ok"]
    assert fresh.nodes["df"] == w.nodes["df"]

