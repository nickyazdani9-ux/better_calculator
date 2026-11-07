"""Exact Riccati reductions for rational coefficients in x. Standard library only.

solve_linear(A, B, C) accepts A*y'' + B*y' + C*y = 0. A returned basis
is a fundamental system on each connected regular interval. The Riccati
chart additionally requires y != 0. See docs/ODE.md for the input grammar.
"""

from __future__ import annotations

import ast
from fractions import Fraction as F
from math import isqrt
from typing import TypedDict


# Polynomial coefficients run from the constant term upwards. The zero
# polynomial is the empty tuple. Q[x] suffices for exact family recognition.
Poly = tuple[F, ...]
Rat = tuple[Poly, Poly]
ZERO: Poly = ()
ONE: Poly = (F(1),)
X: Poly = (F(0), F(1))


def _poly(values: list[F]) -> Poly:
    while values and not values[-1]:
        values.pop()
    if len(values) > 65 or any(
        max(c.numerator.bit_length(), c.denominator.bit_length()) > 2048 for c in values
    ):
        raise ValueError("Coefficient expression exceeds the exact arithmetic limits.")
    return tuple(values)


def _scale(p: Poly, k: F) -> Poly:
    return _poly([k * c for c in p])


def _add(p: Poly, q: Poly) -> Poly:
    size = max(len(p), len(q))
    return _poly(
        [
            a + b
            for a, b in zip(
                p + (F(0),) * (size - len(p)), q + (F(0),) * (size - len(q))
            )
        ]
    )


def _mul(p: Poly, q: Poly) -> Poly:
    if not p or not q:
        return ZERO
    if len(p) + len(q) - 2 > 64:
        raise ValueError("Polynomial degree exceeds 64.")
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return _poly(out)


def _divmod(p: Poly, q: Poly) -> tuple[Poly, Poly]:
    if not q:
        raise ValueError("The denominator is identically zero.")
    quotient = [F(0)] * max(0, len(p) - len(q) + 1)
    while len(p) >= len(q):
        k = len(p) - len(q)
        coefficient = p[-1] / q[-1]
        quotient[k] = coefficient
        p = _add(p, (F(0),) * k + _scale(q, -coefficient))
    return _poly(quotient), p


def _gcd(p: Poly, q: Poly) -> Poly:
    while q:
        p, q = q, _divmod(p, q)[1]
    return _scale(p, 1 / p[-1]) if p else ZERO


def _format(p: Poly) -> str:
    terms: list[str] = []
    for degree in reversed(range(len(p))):
        c = p[degree]
        if not c:
            continue
        power = "" if not degree else "x" if degree == 1 else f"x^{degree}"
        value = ("" if abs(c) == 1 else f"{abs(c)}*") + power if power else str(abs(c))
        sign = (" - " if c < 0 else " + ") if terms else ("-" if c < 0 else "")
        terms.append(sign + value)
    return "".join(terms) or "0"


def _reduce(n: Poly, d: Poly) -> Rat:
    if not d:
        raise ValueError("The denominator is identically zero.")
    if not n:
        return ZERO, ONE
    g = _gcd(n, d)
    n, d = _divmod(n, g)[0], _divmod(d, g)[0]
    return _scale(n, 1 / d[-1]), _scale(d, 1 / d[-1])


def _ratio(n: Poly, d: Poly) -> str:
    n, d = _reduce(n, d)
    return _format(n) if d == ONE else f"({_format(n)})/({_format(d)})"


def _parse(source: str, guards: set[str]) -> Rat:
    if not isinstance(source, str) or not 0 < len(source.strip()) <= 200:
        raise ValueError("Enter a coefficient in x (1 to 200 characters).")
    expr = source.strip().replace("^", "**")
    try:
        tree = ast.parse(expr, mode="eval")
    except (SyntaxError, RecursionError) as exc:
        raise ValueError(
            "Use rational expressions in x, such as (x+1)^2 or 1/x."
        ) from exc
    if sum(1 for _ in ast.walk(tree)) > 80:
        raise ValueError("Coefficient expression is too large.")

    def guard(p: Poly) -> None:
        if not p:
            raise ValueError("The denominator is identically zero.")
        if len(p) > 1:
            guards.add(_format(p))

    def read(node: ast.AST) -> Rat:
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return _poly([F(node.value)]), ONE
        if isinstance(node, ast.Name) and node.id == "x":
            return X, ONE
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            n, d = read(node.operand)
            return (_scale(n, F(-1)) if isinstance(node.op, ast.USub) else n), d
        if isinstance(node, ast.BinOp):
            a, b = read(node.left)
            if isinstance(node.op, ast.Pow):
                power = node.right
                negative = isinstance(power, ast.UnaryOp) and isinstance(
                    power.op, ast.USub
                )
                if isinstance(power, ast.UnaryOp) and isinstance(
                    power.op, (ast.USub, ast.UAdd)
                ):
                    power = power.operand
                if (
                    not isinstance(power, ast.Constant)
                    or type(power.value) is not int
                    or power.value > 12
                ):
                    raise ValueError("Use an integer power between -12 and 12.")
                if negative and power.value:
                    guard(a)
                    a, b = b, a
                n, d = ONE, ONE
                for _ in range(power.value):
                    n, d = _mul(n, a), _mul(d, b)
                return n, d
            c, d = read(node.right)
            if isinstance(node.op, (ast.Add, ast.Sub)):
                if isinstance(node.op, ast.Sub):
                    c = _scale(c, F(-1))
                return _reduce(_add(_mul(a, d), _mul(c, b)), _mul(b, d))
            if isinstance(node.op, ast.Mult):
                return _reduce(_mul(a, c), _mul(b, d))
            if isinstance(node.op, ast.Div):
                guard(c)
                return _reduce(_mul(a, d), _mul(b, c))
        raise ValueError("Use integers, fractions, x, parentheses and +, -, *, /, ^.")

    return read(tree.body)


class LinearResult(TypedDict):
    status: str
    family: str
    basis: list[str]
    coefficient_guards: list[str]
    slope_rhs: str
    chart: str
    recovery: str
    reason: str
    licence: str


def _times(f: str, g: str) -> str:
    if "0" in (f, g):
        return "0"
    if f == "1":
        return g
    if g == "1":
        return f
    return f"({f})*({g})"


def _root(value: F) -> str:
    a, b = isqrt(value.numerator), isqrt(value.denominator)
    return (
        str(F(a, b))
        if a * a == value.numerator and b * b == value.denominator
        else f"sqrt({value})"
    )


def _modes(p: F, q: F, s: str) -> tuple[list[str], list[str]]:
    """Real fundamental system of U'' + p U' + q U, and its s-derivatives."""
    alpha, delta = -p / 2, p * p / 4 - q

    def exponential(k: str) -> str:
        return "1" if k == "0" else f"exp({_times(k, s)})"

    if delta > 0:
        d = _root(delta)
        if d.startswith("sqrt"):
            rates = [f"{alpha} + {d}", f"{alpha} - {d}"] if alpha else [d, f"-{d}"]
        else:
            rates = [str(alpha + F(d)), str(alpha - F(d))]
        basis = [exponential(k) for k in rates]
        return basis, [_times(k, f) for k, f in zip(rates, basis)]
    a = str(alpha)
    envelope = exponential(a)
    if delta == 0:
        return [envelope, _times(s, envelope)], [
            _times(a, envelope),
            _times(envelope, f"(1 + {_times(a, s)})"),
        ]
    b = _root(-delta)
    phase = _times(b, s)
    u, v = _times(envelope, f"cos({phase})"), _times(envelope, f"sin({phase})")
    return [u, v], [
        f"({_times(a, u)}) - ({_times(b, v)})",
        f"({_times(b, u)}) + ({_times(a, v)})",
    ]


def _multiple(p: Poly, a: Poly) -> F | None:
    k = p[-1] / a[-1] if p else F(0)
    return k if p == _scale(a, k) else None


def solve_linear(a_input: str, b_input: str, c_input: str) -> LinearResult:
    guards: set[str] = set()
    (an, ad), (bn, bd), (cn, cd) = [
        _parse(t, guards) for t in (a_input, b_input, c_input)
    ]
    if not an:
        raise ValueError("A is identically zero. Supply a second-order equation.")
    if len(an) > 1:
        guards.add(_format(an))
    # Remove common factors for recognition only. The original domain survives.
    a, b, c = _mul(an, _mul(bd, cd)), _mul(bn, _mul(ad, cd)), _mul(cn, _mul(ad, bd))
    common = _gcd(_gcd(a, b), c)
    a, b, c = [_divmod(poly, common)[0] for poly in (a, b, c)]
    a, b, c = [_scale(poly, 1 / a[-1]) for poly in (a, b, c)]
    out: LinearResult = dict(
        status="reduced",
        family="unclassified",
        basis=[],
        coefficient_guards=[f"{g} != 0" for g in sorted(guards)],
        slope_rhs=f"-z^2 - ({_ratio(b, a)})*z - ({_ratio(c, a)})",
        chart="z = y'/y on y != 0; at a simple zero use w = y/y'.",
        recovery="y(x) = y(x0)*exp(integral(z(t), t=x0..x)) on a zero-free interval.",
        licence="RiccatiZoo.leading_coeff_iff",
        reason="The reduction is exact. A fundamental system has not been established.",
    )
    p, q = _multiple(b, a), _multiple(c, a)
    if p is not None and q is not None:
        out.update(
            {
                "status": "solved",
                "family": "constant",
                "basis": _modes(p, q, "x")[0],
                "reason": "Both normalized coefficients are constant.",
                "licence": "Constant-coefficient fundamental-system theorem",
            }
        )
        return out
    t: Poly = ()
    if len(a) == 2:
        t = a
    if len(a) == 3:
        trial = (a[1] / 2, F(1))
        if _mul(trial, trial) == a:
            t = trial
    if t and (not b or len(b) < len(a)) and (not c or len(c) + 1 < len(a)):
        p, q = _multiple(_mul(t, b), a), _multiple(_mul(_mul(t, t), c), a)
        if p is not None and q is not None:
            s = f"log(abs({_format(t)}))"
            out.update(
                {
                    "status": "solved",
                    "family": "Euler",
                    "basis": _modes(p - 1, q, s)[0],
                    "reason": f"In s = {s} the characteristic polynomial is r^2 + ({p - 1})*r + ({q}).",
                    "licence": "Euler change of variable and constant-coefficient fundamental-system theorem",
                }
            )
            return out
    # x B = A and x² C/A = k² x² - nu², also when nu = 0.
    bessel_q, bessel_den = (
        _reduce(_mul(_mul(X, X), c), a)
        if len(a) <= 3 and len(b) < len(a) and len(c) <= 3 and _mul(X, b) == a
        else (ZERO, ONE)
    )
    if (
        bessel_den == ONE
        and len(bessel_q) == 3
        and bessel_q[1] == 0
        and bessel_q[2] > 0
    ):
        out["family"] = "Bessel"
    elif a == ONE and not b and len(c) == 2:
        out["family"] = "Airy"
    elif a == ONE and b == _scale(X, F(-2)) and len(c) <= 1:
        out["family"] = "Hermite"
    elif a == (F(-1), F(0), F(1)) and b == _scale(X, F(2)) and len(c) <= 1:
        out["family"] = "Legendre"
    if out["family"] != "unclassified":
        out["reason"] = (
            f"{out['family']} family. The constant and Euler rules do not furnish a basis here. "
            "Boundary data select a named solution; frozen roots alone do not solve the flow."
        )
    return out


class FirstOrderResult(TypedDict):
    solution: str
    domain: str
    licence: str


def solve_autonomous(a_text: str, b_text: str, c_text: str) -> FirstOrderResult:
    """General real local solutions of z' = a*z^2 + b*z + c, including equilibria."""
    coeff = []
    for s in (a_text, b_text, c_text):
        n, d = _parse(s, set())
        if len(n) > 1 or d != ONE or "x" in s:
            raise ValueError("Autonomous coefficients must be rational constants.")
        coeff.append(n[0] if n else F(0))
    a, b, c = coeff
    if not a:
        solution = f"C*exp(({b})*x) - ({c / b})" if b else f"C + ({c})*x"
        return dict(
            solution=solution,
            domain="All real x; C is arbitrary.",
            licence="First-order linear equation",
        )
    basis, slopes = _modes(-b, a * c, "x")
    u = f"C1*({basis[0]}) + C2*({basis[1]})"
    du = f"C1*({slopes[0]}) + C2*({slopes[1]})"
    return dict(
        solution=f"-({du})/(({a})*({u}))",
        domain=f"{u} != 0. C1 and C2 are not both zero; a common scale cancels.",
        licence="z = -u'/(a*u), u'' - b*u' + a*c*u = 0",
    )


class CoupledResult(TypedDict):
    basis: list[str]
    domain: str
    licence: str


def solve_coupled(ell_text: str, m_text: str) -> CoupledResult:
    """Fourier modes of the paper's coupled metric on 1 + x > 0."""
    try:
        ell, m = int(ell_text), int(m_text)
    except (ValueError, TypeError) as exc:
        raise ValueError("The Fourier index and coupling must be integers.") from exc
    if not (abs(ell) <= 1000 and 1 <= m <= 1000):
        raise ValueError("Use |ell| <= 1000 and a positive coupling m <= 1000.")
    s = "log(1+x)"
    envelope, _ = _modes(F(0), F(-2 * ell**2), s)
    phase = f"exp(({2 * ell * m})*pi*I*x)" if ell else "1"
    return dict(
        basis=[_times(phase, y) for y in envelope],
        domain="1 + x > 0",
        licence="Gauge reduction to Euler; RiccatiZoo.coupled_mode_solves_iff",
    )
