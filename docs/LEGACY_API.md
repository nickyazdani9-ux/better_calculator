# Legacy calculator API — generated operation catalog

This reference is generated from `assets/catalog.json` by `python3 scripts/export_legacy_docs.py`. Do not edit this table by hand.

The legacy calculator is the current **tab-based** interface. It is not the unified graph API. Calls use `{ "tab": "...", "operation": "...", "values": {...} }` through `engine.run_json`. Inputs to `values` are strings; blank fields and defaults depend on the operation. Use `{ "action": "catalog" }` to retrieve the machine-readable catalog.

Success returns `ok`, `expr`, `text`, `latex`, `lines`, `extras`, `inputs` and `reusable`; failure returns `ok:false` and `error`. A result marked `reusable` only means its scalar text can be reparsed, **not** that tensor/chart context is preserved.

For typed cross-domain workflows use the [unified API](API.md). For a first UI example see [Getting started](GETTING_STARTED.md).

## Calculator (`basic`)

| Operation ID | What it does | Input fields and defaults |
| --- | --- | --- |
| `simplify` | Simplify an exact symbolic expression. | `expression` = `(x^2-1)/(x-1)` |
| `evaluate` | Evaluate with exact arithmetic. | `expression` = `1/3 + 1/6` |
| `approximate` | Numerical approximation. | `expression` = `pi*sqrt(2)`; `digits` = `12` |
| `factor` | Factor a polynomial. | `expression` = `x^2-1` |
| `expand` | Expand algebraic products. | `expression` = `(x+1)^3` |
| `solve` | Solve expression = 0 for a variable. | `expression` = `x^2-4`; `variable` = `x` |

## Calculus (`calculus`)

| Operation ID | What it does | Input fields and defaults |
| --- | --- | --- |
| `differentiate` | Ordinary or higher derivatives. | `expression` = `x^3 + sin(x)`; `variable` = `x`; `order` = `1` |
| `integrate` | Indefinite or definite integral; leave both bounds blank for indefinite. | `expression` = `x^2`; `variable` = `x`; `lower` = ``; `upper` = `` |
| `limit` | Two-sided, left, or right limit. | `expression` = `sin(x)/x`; `variable` = `x`; `point` = `0`; `direction` = `+-` |
| `series` | Taylor / Laurent expansion around a point. | `expression` = `exp(x)`; `variable` = `x`; `around` = `0`; `order` = `6` |
| `partial` | Differentiate with respect to any variable. | `expression` = `x^2*y+sin(y)`; `variable` = `y`; `order` = `1` |
| `ode` | Solve dy/dx = f(x,y). Write the right-hand side using y, not y(x). | `expression` = `y`; `variable` = `x` |
| `gradient` | Gradient of a scalar field in coordinate variables. | `expression` = `x^2*y+y^2`; `variables` = `x,y` |
| `hessian` | Matrix of second-order partial derivatives. | `expression` = `x^2*y+y^2`; `variables` = `x,y` |
| `jacobian` | Jacobian of a vector-valued function. | `expressions` = `[x*y,x^2+y]`; `variables` = `x,y` |

## Complex analysis (`complex`)

| Operation ID | What it does | Input fields and defaults |
| --- | --- | --- |
| `simplify` | Simplify expression with complex variables. | `expression` = `(1+I)^2` |
| `parts` | Extract real, imaginary, modulus, and argument. | `expression` = `3+4*I` |
| `derivative` | Formal complex differentiation of an analytic expression. | `expression` = `exp(z)*sin(z)`; `variable` = `z` |
| `residue` | Residue at an isolated singularity. | `expression` = `1/(z-2)`; `variable` = `z`; `point` = `2` |
| `series` | Series about a complex point. | `expression` = `1/(z-2)`; `variable` = `z`; `point` = `2`; `order` = `4` |
| `cauchy_riemann` | Check Cauchy–Riemann conditions symbolically (necessary, not sufficient alone for analyticity). | `expression` = `z^2` |

## Differential geometry (`geometry`)

| Operation ID | What it does | Input fields and defaults |
| --- | --- | --- |
| `inverse_metric` | Compute g^{ij}. | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]` |
| `determinant` | Compute det(g). | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]` |
| `christoffel` | Nonzero Γ^a_bc for Levi-Civita connection. | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]` |
| `ricci` | Compute R_ij using R^a_bcd = ∂cΓ^a_db − ∂dΓ^a_cb + ... | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]` |
| `scalar_curvature` | Compute R = g^{ij}R_ij. | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]` |
| `einstein` | Compute G_ij = R_ij − (R/2) g_ij. | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]` |
| `riemann_component` | Compute R^a_{bcd} for 0-based index values. | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]`; `a` = `0`; `b` = `1`; `c` = `0`; `d` = `1` |
| `covariant_derivative` | Compute ∇_k V^i for a contravariant vector. | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]`; `vector` = `[0,1]`; `direction` = `r` |
| `geodesic` | Display the equations d²xᵃ/dλ² + Γᵃ_bc dxᵇ/dλ dxᶜ/dλ = 0. | `coordinates` = `r,theta`; `metric` = `[[1,0],[0,r^2]]` |

## Transforms & waves (`waves`)

| Operation ID | What it does | Input fields and defaults |
| --- | --- | --- |
| `fourier` | Convention F(k) = ∫ f(x) exp(-2πi kx) dx. | `expression` = `exp(-pi*x^2)`; `variable` = `x`; `frequency` = `k` |
| `inverse_fourier` | Inverse with the 2π convention. | `expression` = `exp(-pi*k^2)`; `variable` = `k`; `frequency` = `x` |
| `laplace` | One-sided Laplace transform. | `expression` = `exp(-t)`; `variable` = `t`; `frequency` = `s` |
| `inverse_laplace` | Inverse one-sided Laplace transform. | `expression` = `1/(s+1)`; `variable` = `s`; `frequency` = `t` |

## Linear algebra (`linear`)

| Operation ID | What it does | Input fields and defaults |
| --- | --- | --- |
| `determinant` | Exact determinant. | `matrix` = `[[1,2],[3,4]]` |
| `inverse` | Matrix inverse. | `matrix` = `[[1,2],[3,4]]` |
| `transpose` | Transpose a matrix. | `matrix` = `[[1,2],[3,4]]` |
| `eigenvalues` | Eigenvalues and multiplicities. | `matrix` = `[[2,0],[0,3]]` |
| `eigenvectors` | Eigenvectors with algebraic multiplicities. | `matrix` = `[[2,0],[0,3]]` |
| `multiply` | Multiply A × B. | `matrix` = `[[1,2],[3,4]]`; `other` = `[[5,6],[7,8]]` |

