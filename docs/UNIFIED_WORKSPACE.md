# Unified mathematical workspace (engine API, first iteration)

The calculator now has a **single, opt-in, typed mathematical graph** alongside its
existing tab-based operations. No UI changes are required to use this protocol.
The aim is to make mathematical *objects* composable independently of which
subject traditionally owns their operations.

## Transport

The existing Pyodide worker accepts the same JSON request and response boundary
via the existing calculate message:

- Old requests: {"tab":"calculus","operation":"differentiate","values":{...}}
- New requests: {"action":"workspace","command":"..."}

Nodes live in memory in the Python interpreter owned by the worker. The caller
can use separate requests or send an **atomic batch**. Restarting or resetting
the worker removes workspace nodes. Nothing is yet persisted in the browser.

## Node contracts

Each node has a unique identifier, kind, SymPy value (in memory), parent node
identifiers, originating operation, and mathematical context: real coordinate
chart and optional real symmetric nondegenerate metric. Values never need to be
round-tripped through rendered text for reuse.

Kinds in this first iteration: scalar, scalar_field, vector (contravariant),
covector, matrix. These distinguish compatible operations without requiring a
discipline-specific tab. Available operations:

- Scalar: simplify, expand, factor, conjugate, differentiate, integrate,
  residue, substitute, expectation.
- Scalar field: those scalar operations plus exterior_derivative.
- Vector/covector: simplify, conjugate, substitute, norm_squared, compatible
  addition and scalar multiplication.
- Matrix: simplify, conjugate, substitute, determinant, compatible addition
  and scalar multiplication.
- Compatible objects: add and multiply, each requiring node references.
  A general tensor product, matrix multiplication, and contractions are
  intentionally NOT inferred.

A covector is represented by coordinate components of a 1-form. The exterior
derivative of a scalar field is such a covector. Its squared norm uses the
inverse metric, while a vector's squared norm uses the metric. Complex
components use conjugation. For indefinite metrics the result is a metric
quadratic form, not necessarily a nonnegative Euclidean length.

Coordinates are explicitly real; non-coordinate scalar variables retain
their general SymPy assumptions. Coordinates and metrics must match when
combining context-dependent objects. Substituting a coordinate discards its
old chart and metric context rather than silently inventing an induced metric.
A probability expectation similarly drops the old coordinate context.

## End-to-end example

Request:

~~~json
{
  "action": "workspace",
  "command": "batch",
  "steps": [
    {
      "command": "define", "id": "f",
      "expression": "(x+I*y)^2",
      "coordinates": ["x", "y"],
      "metric": "[[1,0],[0,1]]"
    },
    {
      "command": "apply", "id": "df",
      "source": "f", "operation": "exterior_derivative"
    },
    {
      "command": "apply", "id": "length",
      "source": "df", "operation": "norm_squared"
    },
    {
      "command": "apply", "id": "mean",
      "source": "length", "operation": "expectation",
      "independent": true,
      "normals": {
        "x": {"mean": "0", "std": "1"},
        "y": {"mean": "0", "std": "1"}
      }
    }
  ]
}
~~~

Result: the graph represents the field, 1-form, squared norm
8(x² + y²), and expectation **16**. Here x and y are independent
standard normal variables when computing the expectation.

Commands: define, apply, get, graph, operations, reset, batch. Every successful
define/apply response has a node object containing id, kind, expression for
display, LaTeX, parents and context. Unsupported operations return a structured
error instead of silently stripping the object's type.

The batch rolls back its newly added nodes if any step fails. Limits are
64 nodes per worker, 24 steps per batch, 4 dimensions for coordinate objects,
and the existing guarded expression parser's complexity limits.

## Explicit limits and next work

This is a **kernel foundation, not a full mathematical unification**.

- No abstract manifolds, charts and change-of-basis maps yet.
- No general tensor index algebra, tensor products, pullbacks or covariant
  derivatives in the unified operation layer; the existing geometry plugin
  remains independently available.
- Probability currently supports independent normal substitutions and an
  expectation operation. Correlated variables, measures, and explicit
  distribution nodes will require richer typed contexts.
- No stable persistent graph storage or graph-to-UI projection yet.
- Only real symmetric metrics with provably real components are supported.
- Computation limits on expressions do not provide a hard wall-clock timeout.

Future work should add explicit coordinate transforms, tensor types with
variance/shape, distribution objects and measure context, then introduce
workflow import/export and persistent graph evaluation. The UI should be built
on top of these contracts rather than duplicating discipline-specific logic.
