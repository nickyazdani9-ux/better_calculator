"""Riccati contract through the same JSON entry point used by the browser."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import sympy as sp

PYTHON = Path(__file__).resolve().parents[1] / "python"
sys.path.insert(0, str(PYTHON))
from engine import run_json


def call(operation, **values):
    return json.loads(
        run_json(json.dumps({"tab": "ode", "operation": operation, "values": values}))
    )


def solve(a, b, c):
    result = call("linear_second_order", a=a, b=b, c=c)
    assert result["ok"], result
    return result["extras"]


@pytest.mark.parametrize(
    "a,b,c,family",
    [
        ("1", "-3", "2", "constant"),
        ("1", "-2", "1", "constant"),
        ("1", "0", "4", "constant"),
        ("1", "0", "0", "constant"),
        ("(1+x)^2", "1+x", "-2", "Euler"),
        ("x^2", "x", "0", "Euler"),
        ("1", "1/(x-2)", "1/(x-2)^2", "Euler"),
        ("(x-2)^2", "-3*(x-2)", "4", "Euler"),
        ("(x-1)/(x-1)", "-3", "2", "constant"),
    ],
)
def test_fundamental_systems_satisfy_ode_and_have_nonzero_wronskian(a, b, c, family):
    answer = solve(a, b, c)
    assert (answer["status"], answer["family"]) == ("solved", family)
    # Check both sides of any Euler centre using exact, real interval charts.
    u = sp.Symbol("u", positive=True)
    x = sp.Symbol("x", real=True)
    parse = lambda expr: sp.sympify(expr, locals={"x": x, "abs": sp.Abs})
    for point in (3 + u, -3 - u):
        y1, y2 = (parse(e).subs(x, point) for e in answer["basis"])
        A, B, C = (parse(e).subs(x, point) for e in (a, b, c))
        for y in (y1, y2):
            dy = sp.diff(y, u) / sp.diff(point, u)
            assert (
                sp.simplify(A * sp.diff(dy, u) / sp.diff(point, u) + B * dy + C * y)
                == 0
            )
        assert sp.simplify((y1 * sp.diff(y2, u) - y2 * sp.diff(y1, u)).subs(u, 1)) != 0


@pytest.mark.parametrize(
    "a,b,c,family",
    [
        ("x^2", "x", "x^2-4", "Bessel"),
        ("1", "0", "-x", "Airy"),
        ("1", "-2*x", "6", "Hermite"),
        ("1-x^2", "-2*x", "6", "Legendre"),
        ("1", "x^3", "1+x", "unclassified"),
        ("1", "1/x", "1-4/x^2", "Bessel"),
        ("(x+3)*x^2", "(x+3)*x", "(x+3)*(x^2-4)", "Bessel"),
    ],
)
def test_reductions_never_pass_off_a_frozen_root_as_a_solution(a, b, c, family):
    out = solve(a, b, c)
    assert (out["family"], out["status"], out["basis"]) == (family, "reduced", [])
    assert out["reason"] and "y" in out["chart"] and out["recovery"]
    x, z = sp.symbols("x z")
    parse = lambda expr: sp.sympify(expr, locals={"x": x, "z": z})
    A, B, C = map(parse, (a, b, c))
    assert sp.cancel(parse(out["slope_rhs"]) + z**2 + B / A * z + C / A) == 0


def test_cancelled_factors_and_input_denominators_stay_in_the_domain():
    out = solve("(x-1)/(x-1)", "-3", "2")
    assert any("x" in guard and "1" in guard for guard in out["coefficient_guards"])
    out = solve("x", "-3*x", "2*x")
    assert out["family"] == "constant" and out["coefficient_guards"]


@pytest.mark.parametrize(
    "a,b,c",
    [
        ("0", "1", "1"),
        ("x-x", "1", "2"),
        ("1", "1/(x-x)", "0"),
        ("1", "__import__('os')", "1"),
        ("1", "x^99999", "1"),
        ("1", "y", "1"),
        ("1", "0", "sin(x)"),
    ],
)
def test_invalid_or_unsupported_input_reports_a_useful_error(a, b, c):
    reply = call("linear_second_order", a=a, b=b, c=c)
    assert not reply["ok"] and reply["error"]


@pytest.mark.parametrize(
    "a,b,c", [("1", "0", "1"), ("1", "0", "0"), ("0", "0", "3"), ("0", "2", "4")]
)
def test_first_order_families(a, b, c):
    reply = call("autonomous_riccati", a=a, b=b, c=c)
    assert reply["ok"], reply
    info = reply["extras"]
    x = sp.Symbol("x", real=True)
    locals_ = {"x": x, "C": sp.Integer(3), "C1": sp.Integer(2), "C2": sp.Integer(3)}
    z = sp.sympify(info["solution"], locals=locals_)
    assert (
        sp.simplify(sp.trigsimp(sp.diff(z, x) - int(a) * z**2 - int(b) * z - int(c)))
        == 0
    )


def test_core_runs_in_isolated_python_without_site_packages():
    code = (
        "import sys; sys.path.insert(0,sys.argv[1]); import riccati; "
        "assert riccati.solve_linear('1','-2','1')['status']=='solved'; "
        "assert 'sympy' not in sys.modules"
    )
    subprocess.run(
        [sys.executable, "-I", "-S", "-c", code, str(PYTHON)],
        check=True,
        env=os.environ.copy(),
    )


@pytest.mark.parametrize("ell,m", [(2, 2), (1, 3), (0, 2)])
def test_coupled_phase_modes_satisfy_the_printed_complex_equation(ell, m):
    result = call("coupled_modes", ell=str(ell), m=str(m))
    assert result["ok"], result
    t = sp.Symbol("t", positive=True)
    x = sp.Symbol("x", real=True)
    phase = 2 * sp.pi * sp.I * ell * m
    p, q = 1 / t - 2 * phase, phase**2 - phase / t - 2 * ell**2 / t**2
    y1, y2 = (
        sp.sympify(e, locals={"x": x}).subs(x, t - 1) for e in result["extras"]["basis"]
    )
    for y in (y1, y2):
        assert sp.simplify(sp.diff(y, t, 2) + p * sp.diff(y, t) + q * y) == 0
    assert sp.simplify((y1 * sp.diff(y2, t) - y2 * sp.diff(y1, t)).subs(t, 1)) != 0


def test_bessel_zero_order_survives_removal_of_a_common_x():
    assert solve("x^2", "x", "x^2")["family"] == "Bessel"
