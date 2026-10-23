# Unified mathematical workspace API reference

**Status: experimental, engine-only.** This reference covers the code in `python/workspace.py`, reached via `engine.run_json` or the Pyodide Web Worker. This is **not** a network endpoint, stable client library, or yet a graph editor in the UI. For existing tab commands use the [legacy API reference](LEGACY_API.md).

If you are new, start with [Getting started](GETTING_STARTED.md) and [Concepts](CONCEPTS.md).

## Transport and invocation

### Direct Python

~~~python
from workspace import Workspace
w = Workspace()  # isolated, mutable graph
response = w.handle({"command":"define","id":"f","expression":"x^2"})
assert response["ok"], response
~~~

### JSON boundary

`engine.run_json` receives a **JSON string** and returns a **JSON string**. All workspace requests include `"action":"workspace"` here:

~~~python
import json
from engine import run_json
reply = json.loads(run_json(json.dumps({
    "action":"workspace", "command":"define", "id":"f", "expression":"x^2"
})))
assert reply["ok"], reply
~~~

The shared engine-level singleton preserves workspace nodes between JSON requests **within that Python interpreter**. Independent `Workspace()` instances are separate.

### Internal browser Worker

The application uses a private Worker message envelope:

~~~javascript
worker.postMessage({
  type: "calculate", id: 123,
  payload: {action: "workspace", command: "graph"}
});
// Response message: {type:"response", id:123, result:{ok:true, nodes:[...]}}
~~~

Initialization/loading is asynchronous. This Worker protocol is **internal and subject to change**, not a public JavaScript SDK. The application manages worker initialization, local snapshot restore, and background status messages.

## Request commands

| `command` | Required fields (besides `command`) | Result | Effect |
| --- | --- | --- | --- |
| `define` | `id` and object value fields | `node` | New named object |
| `apply` | `id`, `source`, `operation`; operation-specific fields | `node` | New derived object |
| `get` | `id` | `node` | Inspect one object |
| `graph` | none | `nodes` | List all nodes in insertion order |
| `operations` | none | `operations` | Map operation names to accepted input kinds |
| `batch` | `steps` array | `results` or `failed_step` | Execute 1–24 commands atomically |
| `export` | none | `snapshot` | Produce versioned replay data |
| `import` | `snapshot` | `nodes` | Replace graph after validated replay |
| `reset` | none | empty `nodes` | Clear graph and replay history |

### Defining objects

- Every `id` is unique within its workspace, starts with lowercase a–z, and contains up to 32 characters from a–z, 0–9, underscore.
- `kind` is optional and defaults to `scalar`. When coordinates are provided, a scalar becomes a `scalar_field`.
- `expression`: formula string for scalar / scalar field.
- `components`: formula string of a list with one component per coordinate, for `vector` or `covector`; `coordinates` is required.
- `matrix`: formula string of a rectangular list of lists, for `matrix` (up to 4×4).
- `coordinates`: optional list of 1–4 distinct real coordinate names or comma-separated string.
- `metric`: optional matrix string; must match coordinates, be symmetric, nondegenerate, with provably real entries. The engine does not insert a metric for you.
- `tensor2` cannot be directly defined with this command; produce it using `tensor_product`.

Example:

~~~json
{"action":"workspace","command":"define","id":"v","kind":"vector",
 "coordinates":["r","theta"],"components":"[r,0]","metric":"[[1,0],[0,r^2]]"}
~~~

### Applying an operation

`id` is the **new** node, `source` references an existing node, `operation` is its name. Some operations use an existing `other` node; other parameters vary. Successful operations retain parent references. Adding/modifying existing IDs is rejected.

~~~json
{"action":"workspace","command":"apply","id":"df","source":"f",
 "operation":"differentiate","variable":"x","order":1}
~~~

## Operations

The table lists **every currently registered unified operation**. “Accepted” means its primary input *kind* passes the initial type check; the mathematical prerequisites in the final column **still apply**. Query `{"command":"operations"}` for the current machine-readable accepted kinds.

| Operation | Accepted source kinds | Additional fields / contract | Output |
| --- | --- | --- | --- |
| `simplify` | all six kinds | SymPy simplification, componentwise for arrays | same kind |
| `expand` | scalar, scalar_field | expand algebraically | same kind |
| `factor` | scalar, scalar_field | factor expression | same kind |
| `conjugate` | all six kinds | conjugate scalar or each component | same kind |
| `differentiate` | scalar, scalar_field | `variable` required; integer `order` from 1 to 12, default 1 | same kind |
| `integrate` | scalar, scalar_field | `variable` required; optionally both `lower` and `upper` formula strings for definite integral | same kind |
| `residue` | scalar, scalar_field | `variable` (complex symbol), optional `point` formula string (default 0); chart coordinate is disallowed as residue variable | same kind |
| `exterior_derivative` | scalar_field | requires declared coordinates | covector |
| `norm_squared` | vector, covector | requires metric; conjugate transpose; uses metric for vector, inverse metric for covector | scalar_field |
| `determinant` | matrix | must be square | scalar or scalar_field |
| `substitute` | all six kinds | `variable` and formula-string `expression`; replacing a chart coordinate discards old chart/metric; geometric arrays then become matrices | potentially changed kind |
| `expectation` | scalar, scalar_field | `independent:true`; `normals` object with 1–4 named normal variables, each with `mean` / `std` formula strings; positive std required | scalar (drops chart context) |
| `add` | all six kinds | `other` node; only matching scalar kinds or compatible same-kind arrays; tensors must also match variance, shape and chart | compatible kind |
| `multiply` | all six kinds | `other` node; scalar × scalar, or scalar × vector/covector/matrix/tensor2; **not** general matrix multiplication | compatible kind |
| `pair` | vector, covector | `other` node must be opposite kind; canonical **bilinear** dual pairing (no Hermitian conjugation) | scalar_field |
| `tensor_product` | vector, covector | `other` vector/covector in same chart; records both upper/lower slots | tensor2 |
| `contract` | tensor2 | only one-up/one-down rank-two contraction; trace of components | scalar_field |
| `raise_index` | covector | requires metric; uses inverse metric | vector |
| `lower_index` | vector | requires metric | covector |
| `change_coordinates` | scalar_field, vector, covector, tensor2 | `coordinates` new coordinate names; `mapping` **list of old coordinates as functions of new**; local nonsingular Jacobian; both charts must use different coordinate names | same kind with new chart/metric |
| `fourier` | scalar | `variable` (input), `frequency` (output); two-sided Fourier convention with exponent -2πikx | scalar |
| `inverse_fourier` | scalar | `variable` (frequency), `frequency` (output coordinate); inverse of same 2π convention | scalar |
| `laplace` | scalar | `variable` (time), `frequency` (Laplace variable); unilateral Laplace transform; convergence conditions suppressed | scalar |
| `inverse_laplace` | scalar | `variable` (Laplace variable), `frequency` (time); inverse unilateral transform | scalar |
| `limit` | scalar | `variable`, optional `point` formula (default 0), `direction` one of `+`, `-`, `+-` (default `+-`) | scalar |
| `series` | scalar | `variable`, optional `point` formula (default 0), integer `order` 1–18 (default 6); includes order term | scalar |
| `matrix_inverse` | matrix | source must be square and invertible | matrix |
| `matrix_transpose` | matrix | swaps matrix row/column dimensions | matrix |
| `matrix_multiply` | matrix | `other` matrix node with compatible dimensions; conventional matrix product | matrix |

“all six kinds” means scalar, scalar_field, vector, covector, matrix, tensor2. Rank-two tensor variance is stored as the ordered pair `["up","down"]`, `["down","up"]`, etc.

### Shared operation adapters (first integration slice)

The operations `fourier`, `inverse_fourier`, `laplace`, `inverse_laplace`,
`limit`, `series`, `matrix_inverse`, `matrix_transpose`, and
`matrix_multiply` use the **same SymPy implementation functions as the
legacy tab operations**. They accept typed source values without reparsing
any formatted result strings.

For now, integral transforms, limits and series accept **unscoped scalar nodes
only**. A `scalar_field` with declared chart/metric cannot be silently
reinterpreted as a frequency-domain field; a future coordinate/dual-space
model will make those transitions explicit.

The Fourier convention is

```text
F(k) = ∫ f(x) exp(-2*pi*I*k*x) dx
```

and the Laplace transform is one-sided (t ≥ 0). As in the existing tab,
the Laplace transform currently returns its expression without convergence
conditions. Ensure those conditions hold when interpreting the result.
Some transforms or series may remain unevaluated or include symbolic order
terms; the graph retains those objects rather than claiming numerical answers.

A `matrix_multiply` operation is **different from `multiply`**:
`multiply` is scalar multiplication or scalar products, while
`matrix_multiply` explicitly composes two compatible matrices.

Example:

~~~json
{"action":"workspace","command":"apply","id":"spectrum","source":"gaussian",
 "operation":"fourier","variable":"x","frequency":"k"}
~~~

See [the transform/matrix recipe](RECIPES.md#d-transforms--linear-algebra--transforms).

### Coordinate-change example

~~~json
{"action":"workspace","command":"apply","id":"polar_v","source":"cartesian_v",
 "operation":"change_coordinates",
 "coordinates":["r","theta"],
 "mapping":["r*cos(theta)","r*sin(theta)"]}
~~~

The mapping says `x = r*cos(theta)` and `y = r*sin(theta)`. The inverse map is **not** what this field expects. Transformations are locally valid where the Jacobian is invertible; the engine does not prove global invertibility or track excluded chart boundaries.

### Expectation example

~~~json
{"action":"workspace","command":"apply","id":"mean","source":"squared",
 "operation":"expectation","independent":true,
 "normals":{"x":{"mean":"0","std":"1"},"y":{"mean":"0","std":"1"}}}
~~~

The engine requires the random variables to occur in the expression. Distribution parameters cannot depend on those declared random variables. Correlated distributions and general measures are **not** implemented.

## Result shapes

A successful `define` or `apply` result contains `ok:true` and `node`:

~~~json
{"ok":true,"node":{
  "id":"df","kind":"scalar","expr":"2*x","latex":"2 x",
  "parents":["f"],"operation":"differentiate","variance":[],
  "context":{"coordinates":[],"metric":null}
}}
~~~

`expr` is a **display string**, not a recommended serialization format. `latex` is for typesetting. Use the **node ID** as the source of subsequent operations; never parse the previous displayed expression to recover mathematical type.

A failure returns `{"ok":false,"error":"..."}`. An atomic batch failure additionally reports a zero-based `failed_step`. Inspect these fields rather than assuming exceptions are thrown.

## Workflows, snapshots, and storage

A `batch` takes steps (only ordinary `define`/`apply` and non-nested safe commands; do not nest `batch` or `reset`) and either commits all results or rolls back. The intended normal use is arrays of `define` and `apply`.

~~~json
{"action":"workspace","command":"batch","steps":[
 {"command":"define","id":"f","expression":"x^2"},
 {"command":"apply","id":"df","source":"f","operation":"differentiate","variable":"x"}
]}
~~~

`export` returns a snapshot of **validated commands** in the shape:

~~~json
{"format":"calculator2.workspace","version":1,"steps":[
 {"command":"define","id":"f","expression":"x^2"}
]}
~~~

Send this as `snapshot` in `import`. The engine validates and replays the full journal. If replay fails, the old workspace remains unchanged. Browser-local persistence uses key `calculator2.workspace.v1`. It is not automatically synced between devices and it does not guarantee migration across schema versions.

## Expression grammar and limits

Input strings use explicit multiplication (`2*x`), `^` or `**` for powers, `I` for imaginary unit, and a restricted set of functions such as `sin`, `cos`, `exp`, `log`, `sqrt`, `conjugate`. No arbitrary Python, function definitions, indexing, attributes, or executable LaTeX. See [Troubleshooting](TROUBLESHOOTING.md).

Current limits: expressions ≤500 characters and approximately 120 parser AST nodes; arrays up to four elements per dimension; coordinate dimension 1–4; maximum 64 nodes per workspace, 24 steps per batch, and 75,000 characters per JSON snapshot. These are resource guards, **not** a hard computation time limit.

## Legacy calculator API is separate

The original API is `{"tab":"calculus","operation":"differentiate","values":{...}}`. It returns `ok`, `expr`, `latex`, `text`, `lines`, `extras`, `inputs`, and `reusable`, not typed workspace nodes. `{"action":"catalog"}` returns its complete operation registry. See [Legacy API](LEGACY_API.md) for exact names, fields and defaults.

No automatic bridge presently promotes every legacy output into a typed workspace node. That integration is future M1 work.
