# Worked mathematical workflows

Every recipe is mathematical first, software second. Each one has a version-controlled [runnable JSON](examples/) example that the test suite executes against the actual engine. **The subject ordering is arbitrary.** These examples illustrate valid compositions, not preconfigured pathways.

## Run any recipe

From the repository root:

~~~bash
PYTHONPATH=python python3 - <<'PY'
import json
from pathlib import Path
from workspace import Workspace

path = Path("docs/examples/linear_complex_calculus.json")
request = json.loads(path.read_text(encoding="utf-8"))
w = Workspace()
answer = w.handle(request)
assert answer["ok"], answer
for node in w.handle({"command":"graph"})["nodes"]:
    print(node["id"], node["kind"], node["expr"])
PY
~~~

Each example uses a single atomic `batch`. You can also submit its steps one at a time to `Workspace.handle`.

## A. Linear algebra → complex analysis → calculus

Take the determinant of the diagonal matrix with entries 2 and 3 (result 6). Independently compute the residue of `1/(z-2)` at `z=2` (result 1). Add the two scalar results to obtain 7, multiply by `t^2`, differentiate, then integrate with respect to `t`.

The final expression is `7*t^2`. It is defined up to an integration constant in the usual mathematical sense.

[Run the exact JSON example](examples/linear_complex_calculus.json).

**Key idea:** The two branches recombine through compatible scalar objects. The engine does not need a subject switch.

## B. Geometry → tensor operations → coordinate change → calculus

Let `f(x,y)=x*y` on the Euclidean plane. Take its differential, raise its index with the metric, form a mixed-index tensor by tensor product with the original covector, and contract. The contraction is `x^2+y^2`.

Now express it using `x=r*cos(theta)`, `y=r*sin(theta)`. The field becomes `r^2` and its radial derivative is `2*r`.

[Run the exact JSON example](examples/geometry_tensor_calculus.json).

**Key idea:** Chart and metric information survive a sequence of nontrivial typed operations.

## C. Complex-valued field → geometry → probability

On the Euclidean plane, define `f(x,y)=(x+I*y)^2`. Compute the exterior derivative and the squared norm of that covector under the Euclidean metric. The norm is `8*(x^2+y^2)`.

Assuming *independent standard-normal* X and Y, its expectation is **16**.

[Run the exact JSON example](examples/complex_geometry_probability.json).

**Key idea:** Mathematical context is explicit. This is only one example among indefinitely many potential compatible chains.

## D. Transforms → linear algebra → transforms

Begin with the Gaussian `f(x)=exp(-pi*x^2)`, whose Fourier transform under the
2π convention is `exp(-pi*k^2)`. In a separate branch, obtain the determinant
of the diagonal matrix `[[2,0],[0,1]]`. Multiply the spectrum by this scalar
determinant and apply the inverse Fourier transform.

The recovered function is `2*exp(-pi*x^2)`. Every intermediate result is
a reusable, typed graph node with parent references.

[Run the exact JSON example](examples/transform_linear_calculus.json).

**Key idea:** Operations from different subjects can occur in any meaningful
order; no special-case “Fourier → matrix” workflow was implemented.

## Invalid compositions are important too

For contrast, taking `norm_squared` without a metric, adding tensor components expressed in incompatible charts, or contracting a tensor with two upper indices must return an error. **Rejecting invalid mathematics is part of the contract.** See [Troubleshooting](TROUBLESHOOTING.md).

More examples should be added with each new supported operation, accompanied by a regression test. Exact request fields are in the [API reference](API.md).
