"""TDD contracts: pre-existing mathematical operations must compose as typed nodes.

The legacy tab entry points and the unified graph must share the exact symbolic
implementations, without converting intermediate values to display strings.
"""
import json
import sys
from pathlib import Path

import pytest
import sympy as sp

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "python"))

from engine import run_json
from workspace import Workspace, OPERATION_SIGNATURES


def graph(*steps):
    w = Workspace()
    result = w.handle({"command": "batch", "steps": list(steps)})
    assert result["ok"], result
    return w


def test_transforms_and_linear_algebra_form_a_single_typed_workflow():
    w = graph(
        {"command":"define","id":"gaussian","expression":"exp(-pi*x^2)"},
        {"command":"apply","id":"spectrum","source":"gaussian",
         "operation":"fourier","variable":"x","frequency":"k"},
        {"command":"define","id":"mat","kind":"matrix","matrix":"[[2,0],[0,1]]"},
        {"command":"apply","id":"scale","source":"mat","operation":"determinant"},
        {"command":"apply","id":"scaled","source":"spectrum","other":"scale",
         "operation":"multiply"},
        {"command":"apply","id":"recovered","source":"scaled",
         "operation":"inverse_fourier","variable":"k","frequency":"x"},
    )
    x, k = sp.symbols("x k")
    assert sp.simplify(w.nodes["spectrum"].value - sp.exp(-sp.pi*k**2)) == 0
    assert sp.simplify(w.nodes["recovered"].value - 2*sp.exp(-sp.pi*x**2)) == 0
    assert w.nodes["recovered"].parents == ("scaled",)
    assert w.nodes["scaled"].parents == ("spectrum","scale")
    assert w.nodes["recovered"].kind == "scalar"


def test_laplace_and_inverse_laplace_are_reusable():
    w = graph(
        {"command":"define","id":"f","expression":"exp(-t)"},
        {"command":"apply","id":"lap","source":"f",
         "operation":"laplace","variable":"t","frequency":"s"},
        {"command":"apply","id":"inv","source":"lap",
         "operation":"inverse_laplace","variable":"s","frequency":"t"},
    )
    s, t = sp.symbols("s t")
    assert sp.simplify(w.nodes["lap"].value - 1/(s+1)) == 0
    assert sp.simplify(w.nodes["inv"].value.subs(t, 3) - sp.exp(-3)) == 0


def test_matrix_inverse_transpose_and_product_are_typed():
    w = graph(
        {"command":"define","id":"a","kind":"matrix","matrix":"[[1,2],[3,5]]"},
        {"command":"apply","id":"inv","source":"a","operation":"matrix_inverse"},
        {"command":"apply","id":"identity","source":"a","other":"inv",
         "operation":"matrix_multiply"},
        {"command":"apply","id":"transposed","source":"identity",
         "operation":"matrix_transpose"},
    )
    assert w.nodes["identity"].kind == "matrix"
    assert w.nodes["identity"].value == sp.eye(2)
    assert w.nodes["transposed"].value == sp.eye(2)
    assert w.nodes["identity"].parents == ("a","inv")


def test_limit_and_series_feed_existing_unified_calculus():
    w = graph(
        {"command":"define","id":"f","expression":"sin(x)/x"},
        {"command":"apply","id":"at_origin","source":"f",
         "operation":"limit","variable":"x","point":"0","direction":"+-"},
        {"command":"define","id":"exp","expression":"exp(x)"},
        {"command":"apply","id":"series","source":"exp",
         "operation":"series","variable":"x","point":"0","order":4},
        {"command":"apply","id":"derived","source":"series",
         "operation":"differentiate","variable":"x"},
    )
    x=sp.Symbol("x")
    assert w.nodes["at_origin"].value == 1
    assert sp.simplify((w.nodes["derived"].value - (1+x+x**2/2)).removeO()) == 0


@pytest.mark.parametrize("op,tab,legacy_op,values",[
    ("fourier","waves","fourier",{"expression":"exp(-pi*x^2)","variable":"x","frequency":"k"}),
    ("inverse_fourier","waves","inverse_fourier",{"expression":"exp(-pi*k^2)","variable":"k","frequency":"x"}),
    ("laplace","waves","laplace",{"expression":"exp(-t)","variable":"t","frequency":"s"}),
    ("inverse_laplace","waves","inverse_laplace",{"expression":"1/(s+1)","variable":"s","frequency":"t"}),
    ("limit","calculus","limit",{"expression":"sin(x)/x","variable":"x","point":"0","direction":"+-"}),
    ("series","calculus","series",{"expression":"exp(x)","variable":"x","point":"0","order":"5"}),
    ("matrix_inverse","linear","inverse",{"matrix":"[[1,2],[3,5]]"}),
    ("matrix_transpose","linear","transpose",{"matrix":"[[1,2],[3,5]]"}),
]):
def test_same_result_through_legacy_and_unified_entrypoints(op,tab,legacy_op,values):
    w=Workspace()
    kind="matrix" if tab=="linear" else "scalar"
    definition={"command":"define","id":"source","kind":kind}
    definition["matrix" if kind=="matrix" else "expression"]=values["matrix" if kind=="matrix" else "expression"]
    assert w.handle(definition)["ok"]
    args={"command":"apply","id":"output","source":"source","operation":op}
    args.update({k:(int(v) if k=="order" else v) for k,v in values.items()
                 if k not in ("expression","matrix")})
    result=w.handle(args)
    assert result["ok"], result
    legacy=json.loads(run_json(json.dumps({"tab":tab,"operation":legacy_op,"values":values})))
    assert legacy["ok"], legacy
    assert w.nodes["output"].value == sp.sympify(legacy["expr"]) or (
        sp.simplify(w.nodes["output"].value - sp.sympify(legacy["expr"])) == 0
        if kind=="scalar" else False
    )


def test_adapter_validation_and_failed_batch_are_atomic():
    w=Workspace()
    assert w.handle({"command":"define","id":"field","expression":"x^2",
                     "coordinates":["x"],"metric":"[[1]]"})["ok"]
    assert not w.handle({"command":"apply","id":"bad","source":"field",
                         "operation":"fourier","variable":"x","frequency":"k"})["ok"]
    assert w.handle({"command":"define","id":"rect","kind":"matrix",
                     "matrix":"[[1,2,3],[4,5,6]]"})["ok"]
    assert not w.handle({"command":"apply","id":"bad2","source":"rect",
                         "operation":"matrix_inverse"})["ok"]
    assert w.handle({"command":"define","id":"scalar","expression":"sin(x)/x"})["ok"]
    assert not w.handle({"command":"apply","id":"bad3","source":"scalar",
                         "operation":"limit","variable":"x","point":"0","direction":"up"})["ok"]
    before=w.handle({"command":"export"})["snapshot"]
    out=w.handle({"command":"batch","steps":[
        {"command":"apply","id":"good","source":"scalar",
         "operation":"limit","variable":"x","point":"0"},
        {"command":"apply","id":"wrong","source":"scalar","operation":"matrix_inverse"}
    ]})
    assert not out["ok"]
    assert w.handle({"command":"export"})["snapshot"] == before
    assert "good" not in w.nodes


def test_new_registry_operations_survive_snapshot_replay():
    w=graph(
        {"command":"define","id":"f","expression":"exp(-pi*x^2)"},
        {"command":"apply","id":"g","source":"f",
         "operation":"fourier","variable":"x","frequency":"k"},
        {"command":"apply","id":"back","source":"g",
         "operation":"inverse_fourier","variable":"k","frequency":"x"},
    )
    snapshot=w.handle({"command":"export"})["snapshot"]
    fresh=Workspace()
    restored=fresh.handle({"command":"import","snapshot":snapshot})
    assert restored["ok"], restored
    assert fresh.nodes["back"].value == w.nodes["back"].value
    assert fresh.nodes["back"].parents == ("g",)
    assert OPERATION_SIGNATURES["fourier"] == frozenset({"scalar"})
