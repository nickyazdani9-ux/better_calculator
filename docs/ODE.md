# Differential equations

Open **Differential equations** in the calculator. The second-order form takes the three coefficients of `A(x) y″ + B(x) y′ + C(x) y = 0`. The output includes either two independent solutions or the exact reduced equation and the reason the solver stopped.

| Operation | Inputs | Output |
|---|---|---|
| `linear_second_order` | `a`, `b`, `c` as rational functions of x | General basis on each regular interval for constant or shifted Euler coefficients. Bessel, affine Airy, physicists’ Hermite and ordinary Legendre profiles receive a family label and Riccati reduction. Other supported inputs receive the general reduction. |
| `autonomous_riccati` | Rational constants `a`, `b`, `c` | General local real solutions of `z′ = a z² + b z + c`, including equilibria and the linear degeneration. |
| `coupled_modes` | Integer Fourier index `ell` and positive integer coupling `m` | A complex fundamental system for the paper’s coupled cone equation, with the repeated mode at `ell=0`. |

Write fractions as `1/3`, products as `2*x` and powers as `x^2`. The expression grammar accepts integer literals, the real variable `x`, parentheses, the four arithmetic operations and integer powers from −12 to 12. Exact arithmetic and input-size limits are enforced. The symbolic reduction applies wherever the original inputs are defined and the leading coefficient is nonzero. Further require `y != 0` for `z = y′/y`. The basis for the linear equation itself can cross a zero. On either side of a shifted Euler singularity the real coordinate is `log(abs(x-h))`.

From the repository root, the standalone component uses only the Python standard library.

~~~sh
PYTHONPATH=python python3 - <<'PY'
from riccati import solve_linear
for abc in [('1', '-2', '1'), ('(1+x)^2', '1+x', '-2'), ('x^2', 'x', 'x^2-4')]:
    answer = solve_linear(*abc)
    print(answer['family'], answer['status'], answer['basis'] or answer['slope_rhs'])
PY
~~~

For the repeated-root input the basis is `exp(x)` and `x*exp(x)`. For Bessel order two the result represents `dz/dx = -z² - z/x - 1 + 4/x²`. An empty basis with status `reduced` records a successful equation transformation. It makes no elementary-solvability or boundary-value claim. Each result includes its domain and the mathematical rule used.

The public worker interface is `engine.run_json`. Its response exposes the same mathematical data under `extras`. Existing calculator domains retain their normal dependencies. SymPy is used as an independent substitution and Wronskian oracle in the ODE tests. The standalone Python solver has its own tests and the Lean module checks the mathematical identities underlying it.

[Revised manuscript and formal companion](https://github.com/nickyazdani9-ux/mathematical-physics/pull/3) · [Pinned Lean source](https://github.com/nickyazdani9-ux/mathematical-physics/blob/8fca27f684eb320e043c3fc2bce4cc0b817de266/mathematics/riccati_odes/RiccatiZoo.lean)
