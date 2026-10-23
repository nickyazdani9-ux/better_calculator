# Mathematical concepts

Familiarity with vectors, matrices, functions and derivatives is enough to understand the core model.

## A mathematical result is an object

The new engine does not only return text. It returns a **node**: an ID, a symbolic value, a mathematical kind, its parent nodes, its originating operation and context (coordinates and optional metric). Nodes form a directed acyclic graph: a calculation can branch and rejoin. Nothing needs to be retyped from a displayed answer.

## Object kinds

| Kind | Mathematical meaning | Typical origin |
| --- | --- | --- |
| `scalar` | Scalar expression not tied to a chart | `define` without coordinates |
| `scalar_field` | Scalar expression on a declared chart | `define` with coordinates |
| `vector` | Contravariant components, one per chart coordinate | `define` or `raise_index` |
| `covector` | Covariant components, e.g. a one-form | `define` or `exterior_derivative` |
| `matrix` | Generic array without an implied tensor change-of-chart law | `define` with matrix |
| `tensor2` | Rank-two tensor with two variance slots | `tensor_product` |

A generic matrix is **not** automatically a rank-two tensor. A polynomial in `x` is **not** automatically a field on a real coordinate chart. The engine avoids silently imposing those interpretations.

## Context matters

A coordinate chart is an ordered list of **real coordinate symbols**, e.g. `["r","theta"]`. An optional metric is a real, symmetric, nondegenerate matrix in that chart; for the Euclidean plane in polar coordinates, `[[1,0],[0,r^2]]`. A metric supplies index raising/lowering and quadratic norms.

The engine will reject incompatible charts or metrics when combining objects. A generic symbol named `x` does not automatically equal a real chart coordinate `x`; SymPy assumptions distinguish them.

## Chaining: any compatible order

The engine is *not* a pre-wired path between named disciplines. Operations are dispatched by their input kind and requirements:

- `exterior_derivative`: scalar field → covector.
- `raise_index`: covector plus metric → vector.
- `determinant`: matrix → scalar.
- `tensor_product`: two vector/covector objects → rank-two tensor.
- `contract`: mixed-index rank-two tensor → scalar field.
- `add`: compatible kinds and mathematical contexts → new object.

Any supported operation can follow another when its mathematical prerequisites are met. A missing conversion, metric, distribution or connection is an **error**, never an implicit guess.

## Complex values and probability

`I` is the imaginary unit; complex-valued fields are supported on real charts. The squared norm uses a conjugate transpose with metric or inverse metric. In an indefinite metric it need not be nonnegative.

`expectation` currently accepts independent normally distributed variables with explicitly supplied means and provably positive standard deviations. It is not a general probability-measure object or correlated-distribution engine.

## Changing coordinates

For Cartesian `x,y` to polar `r,theta`, supply the **old** coordinate values as functions of the **new** coordinates: `["r*cos(theta)","r*sin(theta)"]`. The engine computes a Jacobian and transforms scalar fields, vectors, covectors, rank-two tensors and any attached metric appropriately.

These are **local** transformations. The engine does not yet track all coordinate-domain boundaries, singular sets, or global manifold atlases; e.g. the polar origin still needs mathematical care.

## Provenance is not proof

Export/import preserves a calculation's validated inputs and graph. This enables reproduction, debugging and branching; it does not establish a formal theorem about every symbolic assumption or global domain. See [the API](API.md) and [worked recipes](RECIPES.md).
