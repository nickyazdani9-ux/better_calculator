# Getting started

You can understand the first calculation in five minutes, even without a programming background.

## 1. Use the existing calculator

In a built or hosted copy of Calculator 2.0, select **Calculus** → **Differentiate**. Enter `x^3+sin(x)`, variable `x` and order `1`; select **Done**. The symbolic result is `3*x**2+cos(x)`.

**Add to worksheet** keeps the step; **Save as PDF** invokes browser print/save. **Use answer** can reuse a scalar's *text*, but does not preserve tensor or metric metadata. The current tabs are not yet the unified workspace interface. See the [repository setup](../README.md#quick-start-web) to build locally.

## 2. Run a typed calculation

With the repository source available and Python installed, from the project root:

~~~bash
python3 -m pip install 'sympy>=1.13,<2'
PYTHONPATH=python python3 - <<'PY'
from workspace import Workspace

w = Workspace()
print(w.handle({"command": "define", "id": "f", "expression": "x^2+1"}))
print(w.handle({"command": "apply", "id": "df", "source": "f",
                "operation": "differentiate", "variable": "x"}))
print(w.handle({"command": "get", "id": "df"}))
PY
~~~

The second result has `ok: True` and `expr: "2*x"`. A **node** is a symbolic mathematical object with an ID. `define` creates `f`; `apply` uses it to create `df`; `get` examines `df` without altering anything.

## 3. Chain across disciplines

This Python batch moves from linear algebra into calculus:

~~~python
from workspace import Workspace
w = Workspace()
reply = w.handle({"command": "batch", "steps": [
    {"command": "define", "id": "m", "kind": "matrix", "matrix": "[[2,0],[0,3]]"},
    {"command": "apply", "id": "d", "source": "m", "operation": "determinant"},
    {"command": "define", "id": "f", "expression": "t^2"},
    {"command": "apply", "id": "g", "source": "d", "other": "f", "operation": "multiply"},
    {"command": "apply", "id": "h", "source": "g", "operation": "differentiate", "variable": "t"}
]})
assert reply["ok"], reply
print(w.nodes["h"].value)  # 12*t
~~~

No mathematical subject has to be selected: output kind and context determine valid operations.

## 4. Save the calculation

~~~python
import json
snapshot = w.handle({"command": "export"})["snapshot"]
with open("my-workspace.json", "w") as f:
    json.dump(snapshot, f, indent=2)

fresh = Workspace()
with open("my-workspace.json") as f:
    restored = fresh.handle({"command": "import", "snapshot": json.load(f)})
assert restored["ok"], restored
~~~

Snapshots replay validated commands, including graph dependencies, rather than reconstructing mathematics from rendered text. In the browser application, workspace graph changes are also saved to *local* browser storage and restored when possible; this is not cloud sync.

## Next

Read [Mathematical concepts](CONCEPTS.md), follow the [recipes](RECIPES.md), then consult the [API reference](API.md) for exact command fields.
