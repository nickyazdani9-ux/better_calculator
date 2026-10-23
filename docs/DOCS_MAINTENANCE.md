# Documentation maintenance — a living contract

We write for readers who know mathematics but may be new to this calculator, Python, SymPy or JSON. Documentation changes alongside implementation, not only before releases.

## Requirements for a feature PR

1. Write a **failing behaviour test first** covering the intended mathematical operation and at least one invalid case.
2. Update [Concepts](CONCEPTS.md) when new mathematical kinds or assumptions are introduced.
3. Update the [API reference](API.md) when any command, parameter, result shape, limit or operation changes.
4. Add or revise a complete, **runnable JSON recipe** under `docs/examples/` when chaining behaviour changes.
5. If legacy plugins/catalog change, run `python3 scripts/export_legacy_docs.py` and commit the changed [legacy reference](LEGACY_API.md).
6. Run `python3 -m pytest tests/test_documentation.py -q`, the regular Python/JavaScript suite, and applicable browser integration tests.

The documentation test checks local links, JSON examples against the real workspace, operation-name coverage against `OPERATION_SIGNATURES`, and the generated legacy reference against the operation catalog.

## Shared legacy/unified implementations

When migrating an existing tab operation into the unified graph, place its
symbolic mathematical implementation in `python/math_operations.py` (or a
suitably shared mathematical module). The original plugin and the typed
workspace must both call it **with SymPy objects directly**, not by rendering
and parsing a result. Keep interface input validation at each boundary.

Add parity tests in `tests/test_operation_unification.py` and an
independently meaningful cross-domain chain. If a new Python module is loaded
in Pyodide, include it in `src/worker.js` and the offline precache in
`sw.js`.

## How to describe a new operation

For each operation, write: purpose in plain language; exact input and output kinds; required context/assumptions; JSON request; mathematical interpretation; limitations; an executable example; and the errors an invalid request should produce.

Keep “available now,” “experimental,” and “planned” clearly separate. A legacy tab capability is **not** evidence that an equivalent graph operation exists. A local chart calculation is **not** a proof of a global coordinate equivalence.

## Compatibility and versions

The exported graph journal currently uses `"format":"calculator2.workspace"` and `"version":1`. When changing the schema, document whether older snapshots still import or require migration. Neither the Python workspace contract nor the private browser-worker messages are guaranteed public SemVer-stable yet.

## Language and review checklist

Prefer words before notation, then include precise notation when it adds clarity. Explain project-specific terms such as “node,” “snapshot” and “worker” at their first appearance. Describe convention choices explicitly (coordinate direction, metric signature, Fourier transform, normal distribution). Every output example should agree with the corresponding test.

Before review:

- [ ] A first-time reader can follow the [quick start](GETTING_STARTED.md).
- [ ] The [reference](API.md) includes all operations in the implementation.
- [ ] All new recipes execute.
- [ ] No dead relative Markdown links.
- [ ] Real limitations and failure modes are documented.
- [ ] Tests and CI pass.

This documentation is **iterative**. Each new capability should make the explanations and examples clearer, not merely longer.
