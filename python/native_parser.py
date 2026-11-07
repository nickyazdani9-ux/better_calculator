"""Bounded calculator syntax to literal CAS nodes; see NATIVE_PARSER_SLICE.md.

This front-end module never evaluates input or performs algebra. Callers supply
all symbol bindings, including single-argument function heads.
"""
from __future__ import annotations

import ast
from collections.abc import Mapping
from fractions import Fraction
import io
import re
import tokenize

from cas.core import Add, Apply, Expr, Mul, Number, Pow, Symbol

MAX_LENGTH = 500
MAX_NODES = 120
MAX_DEPTH = 32
MAX_DIGITS = 128
MAX_EXPONENT = 128
MAX_NAMES = 128
_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,20}\Z")
_NUMBER = re.compile(r"(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


class NativeParseError(ValueError):
    """Input is outside the supported grammar or exceeds a resource limit."""


def _number(text: str) -> Fraction:
    # Bound both mantissa and exponent *before* constructing a Fraction.
    if not _NUMBER.fullmatch(text):
        raise NativeParseError("Only decimal numeric literals are supported")
    parts = re.split('[eE]', text)
    if sum(c.isdigit() for c in parts[0]) > MAX_DIGITS:
        raise NativeParseError("Numeric literal has too many digits")
    if len(parts) == 2:
        exponent = parts[1].lstrip('+-').lstrip('0') or '0'
        if len(exponent) > 3 or int(exponent) > MAX_EXPONENT:
            raise NativeParseError("Numeric exponent exceeds limit")
    return Fraction(text)


def _preflight(source: str) -> None:
    depth = 0
    try:
        for token in tokenize.generate_tokens(io.StringIO(source).readline):
            if token.type == tokenize.NUMBER:
                _number(token.string)
            elif token.type == tokenize.NAME and not _NAME.fullmatch(token.string):
                raise NativeParseError("Only ASCII symbol names are supported")
            elif token.type == tokenize.COMMENT:
                raise NativeParseError("Comments are not supported")
            elif token.type == tokenize.OP:
                if token.string in ('(', '[', '{'):
                    depth += 1
                    if depth > MAX_DEPTH:
                        raise NativeParseError("Nesting exceeds limit")
                elif token.string in (')', ']', '}'):
                    depth -= 1
    except (tokenize.TokenError, IndentationError, UnicodeError) as exc:
        raise NativeParseError("Invalid expression syntax") from exc


def parse_native(source: str, names: Mapping[str, Symbol]) -> Expr:
    """Parse +, -, *, /, powers, unary signs and unary symbol calls.

    Names are explicit, case-sensitive ASCII bindings. There are no implicit
    constants, functions or multiplication. Division remains a literal tree.
    """
    if not isinstance(source, str) or not source.strip() or len(source) > MAX_LENGTH:
        raise NativeParseError("Expression must contain 1–500 characters")
    if len(names) > MAX_NAMES:
        raise NativeParseError("Too many symbol bindings")
    bindings = dict(names)
    for name, symbol in bindings.items():
        if not isinstance(name, str) or not _NAME.fullmatch(name) or not isinstance(symbol, Symbol):
            raise NativeParseError("Bindings must map ASCII names to native Symbols")
    source = source.strip().replace('^', '**')
    _preflight(source)
    try:
        tree = ast.parse(source, mode='eval')
    except (SyntaxError, ValueError, RecursionError, UnicodeError) as exc:
        raise NativeParseError("Invalid expression syntax") from exc
    pending: list[tuple[ast.AST, int]] = [(tree, 0)]
    count = 0
    while pending:
        node, depth = pending.pop()
        count += 1
        if count > MAX_NODES or depth > MAX_DEPTH:
            raise NativeParseError("Expression tree exceeds limit")
        pending.extend((child, depth + 1) for child in ast.iter_child_nodes(node))

    def convert(node: ast.AST) -> Expr:
        if isinstance(node, ast.Name):
            if node.id not in bindings:
                raise NativeParseError(f"Unknown symbol: {node.id}")
            return bindings[node.id]
        if isinstance(node, ast.Constant):
            text = ast.get_source_segment(source, node)
            if text is None:
                raise NativeParseError("Numeric source is unavailable")
            return Number(_number(text))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
            child = convert(node.operand)
            return child if isinstance(node.op, ast.UAdd) else Mul(Number(-1), child)
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow)):
            left, right = convert(node.left), convert(node.right)
            if isinstance(node.op, ast.Add):
                return Add(left, right)
            if isinstance(node.op, ast.Sub):
                return Add(left, Mul(Number(-1), right))
            if isinstance(node.op, ast.Mult):
                return Mul(left, right)
            if isinstance(node.op, ast.Div):
                return Mul(left, Pow(right, Number(-1)))
            return Pow(left, right)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and len(node.args) == 1 and not node.keywords:
            if node.func.id not in bindings:
                raise NativeParseError(f"Unknown function symbol: {node.func.id}")
            return Apply(bindings[node.func.id], convert(node.args[0]))
        raise NativeParseError(f"Unsupported syntax: {type(node).__name__}")

    return convert(tree.body)
