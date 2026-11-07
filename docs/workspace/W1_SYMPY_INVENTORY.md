# W1 — SymPy exit inventory

v3, 27 Oct 2026. This was formerly `M4_SYMPY_INVENTORY.md`.

- Taken from `feature/unified-math-workspace` at head `d3263cf` (PR #13).
  - v1 and v2 read `1713a96`. The two commits since (`0bbe88e`, `d3263cf`) touch no file under `python/`, so every Python row below is unchanged. The one non-Python reference that moved is the UI label, now `src/app.js:36`.
- Remapped against the CAS_AZEEM milestones (CAS M0–M3 shipped; M4–M9 per the 22 Sep plan, doc 03).
- Covers W1's definition of done, boxes 1–4.
- ATL-371 holds a first pass by another Claude session at the same head, counted per file and symbol (9 files, 62 symbols) rather than per function. This file is the one of record.

## Summary

- **SymPy imports:**
  - nine runtime imports across seven modules (eight module-level, plus `sympy.stats` inside `workspace.py:396`);
  - also `scripts/vendor_pyodide.py` and nine test files.
- **Browser engine:** the worker loads SymPy with `src/worker.js:22` (`pyodide.loadPackage('sympy')`). The UI label at `src/app.js:36` reads "SymPy online".
- **NumPy and SciPy:** no imports anywhere in the repo's Python.
- **Call sites:** 48 top-level functions call SymPy. The most frequent calls are `simplify` (30), `diff` (19), `Symbol` (9) and `ImmutableMatrix` (8).

## Fates (RELAY-04; scope widened 27 Oct 13:27)

Every runtime call site ends in one of two places.

- **Replace**: rebuilt on CAS_AZEEM once the named CAS milestone has shipped.
- **Gap**: no CAS milestone covers it in v1. The feature is held or withdrawn under the regression ruling (SPEC §6, item 5). SymPy is never kept at runtime.

The nine SymPy test files move to `tests/oracle/`. There they become cross-checks of the replaced features, each recording tool, method and outcome (CONSTRAINTS 5). This is the only place SymPy survives (G10).

## Key

- **M0 ✓, M1 ✓, M2 ✓, M3 ✓**: CAS milestones already shipped. For these the capability exists in the engine.
- **M4–M9**: planned CAS milestones (doc 03 §4).
- **FE**: front-end plumbing, which lives in this repo (SPEC §4.6).

## Call sites

| File:line | Function | SymPy used | Feature | CAS cover | Fate |
|---|---|---|---|---|---|
| python/engine.py:35 | parse_math | Integer, Float, Symbol | expression input | FE parser → kernel trees; decimals → Fraction | Replace |
| python/engine.py:87 | latex_for_input | latex, sympify, Symbol | live LaTeX preview | M0 ✓ `latex()` + FE parser | Replace |
| python/engine.py:167 | math_symbol | Symbol | symbols | M0 ✓ | Replace |
| python/engine.py:182 | parse_matrix | Matrix | matrix input | M6 (G9 matrices) | Replace |
| python/engine.py:191 | metric_data | simplify | metric preprocessing | M5 licensed tier | Replace |
| python/engine.py:238 | calculate | PolynomialError, latex, Expr | dispatch, output | FE + M0 ✓ | Replace |
| python/math_operations.py:10 | transform | fourier/laplace (+ inverses) | integral transforms | none in v1 | Gap |
| python/math_operations.py:22 | limit | limit | limits | limit layer on Ĉ `[CAS v0.3 §3.1]`, not in M4–M9 | Gap |
| python/math_operations.py:28 | series | series | series | none in v1 | Gap |
| python/plugins/basic.py:6 | simplify | simplify | Simplify | M5 (opt-in normal forms, logged) | Replace |
| python/plugins/basic.py:8 | evaluate | simplify | Evaluate | M1 ✓ fold_numbers; M5 beyond | Replace |
| python/plugins/basic.py:10 | approximate | N | numeric value | `cas.numeric` / `lower()` v1.x — SPEC §4.4 | Gap until §4.4 ruled |
| python/plugins/basic.py:14 | factor | factor | Factor | M6 (GCD, rational normal form); full factorisation not in v1 | Replace (partial) |
| python/plugins/basic.py:16 | expand | expand | Expand | M1 ✓ `expand` composite | Replace |
| python/plugins/basic.py:18 | solve | solve, latex | solving | M6 isolate, roots of degree ≤ 2 | Replace (partial) |
| python/plugins/calculus.py:11 | differentiate | diff | Differentiate | M2 ✓ `d`, `partial`, honest dy/dx | Replace |
| python/plugins/calculus.py:13 | integrate | integrate | Integrate | M4 indefinite, M8 definite | Replace |
| python/plugins/calculus.py:28 | ode | dsolve, Function, Eq, diff | ODEs | M3 ✓ degree-1 ladder; M7 Riccati family | Replace |
| python/plugins/calculus.py:41 | gradient | Matrix, diff | gradient | M2 ✓ partial | Replace |
| python/plugins/calculus.py:46 | hessian | hessian | Hessian | M2 ✓ partial (repeated) | Replace |
| python/plugins/calculus.py:50 | jacobian | Matrix | Jacobian | M2 ✓ partial; matrix container M6 | Replace |
| python/plugins/complex_ops.py:8 | simplify | simplify | complex simplify | M5 | Replace |
| python/plugins/complex_ops.py:10 | parts | re, im, Abs, arg, simplify | parts / modulus / argument | M0 ✓ conj; `arg` needs the branch-cut ruling (22 Sep, provisional) | Replace |
| python/plugins/complex_ops.py:15 | derivative | diff | complex derivative | M2 ✓ | Replace |
| python/plugins/complex_ops.py:17 | residue | residue | residues | none in v1 | Gap |
| python/plugins/complex_ops.py:19 | series | series | Laurent/Taylor | none in v1 | Gap |
| python/plugins/complex_ops.py:23 | cauchy_riemann | expand_complex, re, im, diff, simplify | Cauchy–Riemann | M2 ✓ + M5 | Replace |
| python/plugins/geometry.py:10 | geometry | simplify, Rational, diff | metric geometry | M2 ✓ + M5 | Replace |
| python/plugins/geometry.py:16 | curvature | simplify, diff | curvature | M2 ✓ + M5 | Replace |
| python/plugins/geometry.py:22 | ricci_tensor | Matrix, simplify, diff | Ricci | M5 (Schwarzschild Act II) | Replace |
| python/plugins/geometry.py:33 | determinant | factor | metric determinant | M6 (G9) | Replace |
| python/plugins/geometry.py:35 | christoffel | sstr | Christoffels | M2 ✓ (notebook 9, Act I) | Replace |
| python/plugins/geometry.py:44 | ricci | trigsimp, expand_trig | Ricci (trig) | M5 (sin²+cos² in licensed tier) | Replace |
| python/plugins/geometry.py:48 | scalar_curvature | simplify | scalar curvature | M5 | Replace |
| python/plugins/geometry.py:52 | einstein | simplify, Rational | Einstein tensor | M5 | Replace |
| python/plugins/geometry.py:57 | riemann_component | trigsimp, expand_trig | Riemann component | M5 | Replace |
| python/plugins/geometry.py:62 | covariant_derivative | Matrix, simplify, diff | covariant derivative | M2 ✓ + M5 | Replace |
| python/plugins/geometry.py:72 | geodesic | symbols, simplify, Symbol, sstr | geodesic equations | M2 ✓ + M5; solving M3 ✓/M7 | Replace |
| python/plugins/linear.py:14 | eigenvalues | latex, sstr, default_sort_key | eigenvalues | M6: symbolic 2×2 only (G9) | Replace (2×2); larger: Gap |
| python/workspace.py:28 | symbol | Symbol | workspace symbols | M0 ✓ (real = declared assumption) | Replace |
| python/workspace.py:46 | normalise | Symbol | input normalisation | FE | Replace |
| python/workspace.py:54 | scalar_expr | Expr | type check | M0 ✓ | Replace |
| python/workspace.py:61 | context_metric | ImmutableMatrix, simplify | metric context | M6 + M5 | Replace |
| python/workspace.py:78 | change_chart | ImmutableMatrix, MatrixBase, simplify, diff | change_coordinates | M2 ✓ + M5 + M6 | Replace |
| python/workspace.py:133 | public | sstr, latex | node rendering | M0 ✓ | Replace |
| python/workspace.py:238 | define | ImmutableMatrix, Expr | define node | M0 ✓ + M6 | Replace |
| python/workspace.py:279 | apply | simplify, expand, factor, conjugate, diff, residue, integrate, trace, sympy.stats | all typed operations | per the rows above; `expectation` (sympy.stats) none in v1 | Replace / Gap |
| python/workspace.py:470 | handle | PolynomialError | error mapping | FE | Replace |

`python/plugins/waves.py` and `python/plugins/__init__.py` call no SymPy.

## Zero tests (D1 collisions)

`simplify(...) == 0` decides whether something is zero, which D1 forbids as an unlogged, possibly wrong decision. Found by grep at `d3263cf`:

| File:line | Test | CAS replacement |
|---|---|---|
| python/engine.py:201 | `simplify(m.det()) == 0` — singular matrix | `check()` on the determinant; may answer Undetermined (P7); M5 for Verified |
| python/workspace.py:73 | `simplify(matrix.det()) == 0` — degenerate metric | same |
| python/workspace.py:97 | `simplify(jac.det()) == 0` — singular chart change | same |

ATL-371 counts five such sites ⟨verify⟩; the other two need naming before W2 so none is missed.

## Tally

- **Replaceable now**, on CAS M0–M3 as shipped:
  - symbols, numbers and LaTeX;
  - expand and distribute;
  - differentiate, gradient, Hessian and Jacobian;
  - complex derivative;
  - Christoffels;
  - degree-1 ODEs.
- **Waits on CAS M5**, the licensed tier: every `simplify` / `trigsimp` site, 16 functions in all, and the zero tests above. M5 is the main gate for W2.
- **Waits on CAS M4, M6 or M8**: integration, factor, solve, matrices, determinants and eigenvalues.
- **Gaps in v1**:
  - limits (the Ĉ limit layer is unscheduled);
  - series and residues;
  - integral transforms;
  - probability expectation;
  - eigenvalues above 2×2;
  - numeric approximation, until SPEC §4.4 is ruled.
