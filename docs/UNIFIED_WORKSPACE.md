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
can use separate requests or send an **atomic batch**. Restarting or resetting the worker removes workspace nodes **unless a previously
exported versioned JSON snapshot is imported again**. The engine supports
validated snapshots, but no automatic browser-side persistence has been wired up.

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

Commands: define, apply, get, graph, operations, reset, batch, export, import. Every successful
define/apply response has a node object containing id, kind, expression for
display, LaTeX, parents and context. Unsupported operations return a structured
error instead of silently stripping the object's type.

The batch rolls back its newly added nodes if any step fails. Limits are
64 nodes per worker, 24 steps per batch, 4 dimensions for coordinate objects,
and the existing guarded expression parser's complexity limits.

## Exporting and restoring a complete workflow

The `export` command returns a JSON-safe snapshot of the **validated command
history**, not a lossy string rendering of its final objects:

~~~json
{"action": "workspace", "command": "export"}
~~~

Save the returned `snapshot` as JSON. To restore it into a fresh engine,
send:

~~~json
{"action": "workspace", "command": "import", "snapshot": {"format": "calculator2.workspace", "version": 1, "steps": []}}
~~~

Replace the empty `steps` with the exact exported steps. Import replays
every step through the guarded calculator grammar. It restores object kinds,
source-node relationships, coordinate charts, metrics and mathematical values
from the original mathematical commands. The previous workspace is replaced
**only if the full replay succeeds**; failure leaves it intact. Snapshots are
limited by schema version, size and node count. An export is detached from the
engine state so subsequent caller changes cannot mutate the saved graph.

**Not yet implemented:** automatic saving to browser localStorage/IndexedDB,
UI controls for selecting stored workspaces, or version migrations beyond v1.

## Coordinate changes and rank-two tensors (next engine slice)

The kernel now supports the following additional operations:

- **change_coordinates** on scalar fields, vectors, covectors and rank-two tensors.
  Pass a new coordinate list and a **mapping of old coordinates as functions of
  new coordinates**, e.g. from Cartesian \`x,y\` to polar \`r,theta\` use
  \`["r*cos(theta)", "r*sin(theta)"]\`. This performs the Jacobian-based
  transformation of components and the metric, including mixed tensor
  variance. It requires a square Jacobian with nonzero symbolic determinant.
  This validates local invertibility **at regular points**, not at singular
  chart boundaries (e.g. polar coordinates at \`r=0\`).
- **raise_index** and **lower_index** map covectors/vectors using the
  explicitly declared metric and its inverse.
- **pair** evaluates the canonical (bilinear, not Hermitian) dual pairing
  between a vector and a covector.
- **tensor_product** combines two vectors/covectors into a rank-two tensor,
  recording whether each index is upper or lower.
- **contract** traces a rank-two tensor only if it has one upper and one
  lower index. Other contractions need an explicit metric operation.

Example (each object has a prior node ID):

~~~json
{
  "action": "workspace",
  "command": "batch",
  "steps": [
    {"command": "define", "id": "v", "kind": "vector",
     "components": "[x,y]", "coordinates": ["x","y"],
     "metric": "[[1,0],[0,1]]"},
    {"command": "apply", "id": "polar_v", "source": "v",
     "operation": "change_coordinates",
     "coordinates": ["r","theta"],
     "mapping": ["r*cos(theta)", "r*sin(theta)"]}
  ]
}
~~~

The transformed vector has components \`[r,0]\` in polar coordinates.
Changing coordinates is not changing the underlying geometric object.

## Explicit limits and next work

This is a **kernel foundation, not a full mathematical unification**.

- Coordinate changes now work for local charts with explicit invertible maps; global manifolds, chart atlases, composition of chart maps, and domain-aware chart validation are not implemented.
- Rank-two vector/covector tensor products and mixed-index traces are supported,
  but general tensor ranks, arbitrary contractions, pullbacks of higher forms,
  Christoffel connections and covariant derivatives are not yet available in
  the unified operation layer; the existing geometry plugin remains available.
- Probability currently supports independent normal substitutions and an
  expectation operation. Correlated variables, measures, and explicit
  distribution nodes will require richer typed contexts.
- JSON snapshot export/import is implemented, but automatic browser storage and graph-to-UI projection are not yet connected.
- Only real symmetric metrics with provably real components are supported.
- Computation limits on expressions do not provide a hard wall-clock timeout.

Future work should add explicit coordinate transforms, tensor types with
variance/shape, distribution objects and measure context, then connect versioned snapshots to durable browser storage and graph evaluation. The UI should be built
on top of these contracts rather than duplicating discipline-specific logic.
