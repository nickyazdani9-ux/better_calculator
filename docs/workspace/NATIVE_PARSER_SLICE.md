# Native parser slice (ATL-374)

`python/native_parser.py` is front-end plumbing for SPEC §4.6. It constructs
native CAS_AZEEM nodes through a separately installed wheel. It does not switch
the existing engine, UI, Pyodide runtime, graph renderer, or rule browser to the
native kernel. It is not the complete adapter or native completion milestone.

## Contract

`parse_native(source, names)` returns a native `Expr` or raises
`NativeParseError` for unsupported input. `names` is an explicit mapping from
case-sensitive ASCII identifiers (`[A-Za-z][A-Za-z0-9_]{0,20}`) to native
`Symbol` objects. Bindings preserve the supplied symbol and its assumptions;
aliases are possible by design. No built-in constants or function names exist:
`e`, `pi`, `I`, `sin` and `f` all require explicit bindings. A bound symbol can
appear as either a leaf or a unary function head. Functions are never Python
callables. The caller owns semantic symbol/coordinate registration.

Supported syntax is decimal integers, decimals and scientific notation;
registered names; parentheses; unary `+` and `-`; binary `+`, `-`, `*`, `/`,
`**` or `^`; and single-argument calls such as `f(x)`. Python expression
precedence applies after `^` is replaced by `**`, so `-x^2` is `-(x^2)` and
powers associate rightward. Whitespace follows Python expression syntax.
Implicit multiplication, Unicode names, comments, numeric underscores,
nondecimal bases, complex literals, containers, attributes, subscripts,
comparisons, Python control expressions, keyword arguments and starred
arguments are rejected. Relations and differential syntax are future slices.

Construction is literal: `x+x` remains `Add(x,x)`, grouping is preserved, and
`1/2` becomes `Mul(Number(1),Pow(Number(2),Number(-1)))`. Subtraction and unary
minus use multiplication by `Number(-1)`; unary plus contributes no node.
`1/0` is also constructed literally, without evaluating division. Numeric
literals use `Fraction` of their source token, never the Python AST float
value. Thus `0.1` is exactly one tenth. Native Number canonicalization is the
kernel's existing exact-value behavior, not a parser simplification.

## Resource limits

Input is bounded to 500 source characters, 120 Python AST nodes (including
operators and contexts), AST depth 32 (expression root depth zero), lexical
parenthesis/bracket/brace nesting 32, and 128 supplied bindings. Each numeric
mantissa is limited to 128 digits and its decimal exponent magnitude to 128.
Lexical numeric limits run before `Fraction` conversion and before AST parsing.
The AST is checked iteratively before recursive native construction. The parser
uses neither `eval` nor `sympify` and never calls user-named Python functions.
These limits bound expression text; caller-provided mapping implementations
and already-created native Symbol objects remain trusted application inputs.

## Verification and dependency boundary

The native suite is explicit and requires the private CAS wheel plus pytest
and Hypothesis; absence of the dependency fails collection rather than silently
skipping tests. The existing public calculator CI command selects only
`tests/test_*.py`, so it does **not** currently exercise this optional suite.
Dependency delivery to CI/browser and runtime integration remain follow-up work.

From the calculator repository, in an environment with those dependencies:

```sh
python -m pytest tests/native/test_native_parser.py tests/test_*.py -q
python -m mypy --strict python/native_parser.py
```

Validation on Python 3.12: 247 tests passed (80 native parser cases and 167
existing calculator cases); strict mypy passed against the installed native
wheel with its PEP 561 marker, with no ignored imports. One unrelated installed
AnyIO pytest-plugin deprecation warning was emitted.

Wheel tested: CAS_AZEEM typed-package commit
`03c88489ab04232a1155334b69ec65730b911f89`; wheel
`cas-0.0.1-py3-none-any.whl`, SHA-256
`14e9a7745c15eb169bebe90b259017b3814085d0b8d83a3b0c03e92225c17e34`.
This is local acceptance evidence, not a claim that public CI has the private
package installed or that the native runtime has shipped.
