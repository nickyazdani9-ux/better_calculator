"""Explicit native suite: requires the separately installed CAS_AZEEM wheel."""
from fractions import Fraction
import sys
from pathlib import Path

import pytest
from hypothesis import given, strategies as st

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'python'))
from cas.core import Add, Apply, Mul, Number, Pow, Symbol
from native_parser import NativeParseError, parse_native

X, Y, F = Symbol('x'), Symbol('y'), Symbol('f')
NAMES = {'x': X, 'y': Y, 'f': F}

@pytest.mark.parametrize(('source', 'expected'), [
    ('x+x', Add(X, X)),
    ('x*x', Mul(X, X)),
    ('x+(y+x)', Add(X, Add(Y, X))),
    ('x+y+x', Add(Add(X, Y), X)),
    ('x-y', Add(X, Mul(Number(-1), Y))),
    ('x/2', Mul(X, Pow(Number(2), Number(-1)))),
    ('1/2', Mul(Number(1), Pow(Number(2), Number(-1)))),
    ('0.1', Number(Fraction(1, 10))),
    ('1.25e-2', Number(Fraction(1, 80))),
    ('.5', Number(Fraction(1, 2))),
    ('2.', Number(2)),
    ('-x^2', Mul(Number(-1), Pow(X, Number(2)))),
    ('(-x)^2', Pow(Mul(Number(-1), X), Number(2))),
    ('x^y^2', Pow(X, Pow(Y, Number(2)))),
    ('x^-2', Pow(X, Mul(Number(-1), Number(2)))),
    ('+x', X),
    ('f(x)', Apply(F, X)),
])
def test_literal_construction(source: str, expected: object) -> None:
    assert parse_native(source, NAMES) == expected

@pytest.mark.parametrize('source', [
    '__import__("os")', 'x.__class__', 'x[0]', '[x]', '(x,y)',
    '{x:y}', '{x}', 'lambda: x', '[x for x in y]', 'x if y else x',
    'True', 'False', 'None', '"x"', 'b"x"', '1j', '0x10', '1_000',
    'x==y', 'x<y', 'x%y', 'x//y', 'x@y', 'x and y', 'x|y',
    'f(x=y)', 'f(*x)', 'f(**x)', 'f()', 'f(x,y)', '(x:=1)',
    'open(x)', 'sin(x)', 'z', '2x', 'x; y', 'x # comment', '\\x',
    '1e999999999', '1e-999999999', '9'*129, '-'*65+'x',
    '('*65+'x'+')'*65, '+'.join(['x']*100), 'x'*501,
])
def test_rejects_unsupported_or_unbounded_input(source: str) -> None:
    with pytest.raises(NativeParseError):
        parse_native(source, NAMES)

def test_names_are_explicit_not_constants_or_python_functions() -> None:
    e = Symbol('e', frozenset({'real'}))
    assert parse_native('e', {'e': e}) == e
    with pytest.raises(NativeParseError):
        parse_native('e', NAMES)
    # A call is a literal Apply to a supplied Symbol, never Python invocation.
    assert parse_native('f(x)', NAMES) == Apply(F, X)

@pytest.mark.parametrize('source', ['', ' ', '\n', '(', 'x+'])
def test_invalid_syntax(source: str) -> None:
    with pytest.raises(NativeParseError):
        parse_native(source, NAMES)

@given(st.integers(min_value=0, max_value=10**8), st.integers(min_value=0, max_value=8))
def test_decimal_exactness_and_determinism(mantissa: int, places: int) -> None:
    source = f'{mantissa}e-{places}'
    first = parse_native(source, NAMES)
    assert first == Number(Fraction(mantissa, 10**places))
    assert first.content_hash == parse_native(source, NAMES).content_hash

def test_invalid_symbol_bindings() -> None:
    with pytest.raises(NativeParseError):
        parse_native('x', {'__x': X})


def test_rejects_non_symbol_binding() -> None:
    with pytest.raises(NativeParseError):
        parse_native('x', {'x': object()})


def test_bounds_supplied_namespace() -> None:
    with pytest.raises(NativeParseError):
        parse_native('x', {f'n{i}': X for i in range(129)})


@pytest.mark.parametrize('source', ['K', '𝒙', 'f(𝒙)', 'x' * 22])
def test_rejects_unicode_normalization_and_long_names(source: str) -> None:
    with pytest.raises(NativeParseError):
        parse_native(source, {'K': X, 'x': X, 'f': F})


@pytest.mark.parametrize('source', ['1e128', '1e-128', '9' * 128])
def test_numeric_limits_accept_boundary(source: str) -> None:
    assert parse_native(source, NAMES) == Number(Fraction(source))


def test_zero_division_is_literal_not_evaluated() -> None:
    assert parse_native('1/0', NAMES) == Mul(Number(1), Pow(Number(0), Number(-1)))
