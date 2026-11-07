# Reserved-name regression — RH-SHIP-20261107-04

Baseline: f08a4b53b62621503cc8019064c6643c633afb29.

The workspace accepted `e` as a coordinate, while the shared expression parser
interprets it as Euler's constant. Defining `e^2` on coordinates `["e"]`
returned `exp(2)`, then differentiating with respect to `e` returned zero.
This was an accepted-name ambiguity, not a native CAS_AZEEM defect.

Use the existing engine constant/function registries in workspace variable
validation. Reserved names are rejected before creating nodes or journal steps.
Normal coordinate differentiation and complete snapshot replay remain supported.

Local red: focused regression, 26 failed / 6 passed before the implementation.
Local green: full Python suite, 150 passed (Python 3.12, SymPy 1.14.0);
JavaScript suite, 16 passed. The only Python warning concerned the environment's
pytest plugin deprecation. No browser or hosted-CI result is claimed here.

Meaningful coverage includes all reserved names, the exact `e^2` reproduction
with no mutation on rejection, and an ordinary `u^2 -> 2*u` graph roundtrip.
The source review also covered context merging, chart transforms, tensor
variance, atomic batch/import rollback and strict snapshot field/version rules.
Computation time budgets and full chart-domain models remain documented gaps.
