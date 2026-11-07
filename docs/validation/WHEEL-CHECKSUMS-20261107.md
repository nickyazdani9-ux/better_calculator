# Mandatory wheel checksums — 7 November 2026
Work RH-SHIP-20261107-08. Base 611cf70692526143c8a7780584f15eb51561aea8.

## Behavior
Previously entry.get('sha256') allowed a missing checksum to disable wheel verification. Vendoring now resolves the complete dependency closure, validates every checksum as a 64-character hexadecimal string, normalizes case, then begins wheel downloads. packages_for remains unchanged.

## Synthetic evidence
New tests/test_vendor_hashes.py exercises the real vendor entry point using local file URLs and synthetic data only.
Red before correction: 15 failed, 2 passed (17 cases).
Green: python -m pytest tests/test_*.py -q: 167 passed; node --test tests/*.mjs: 23 passed. git diff --check passed. One external anyio/pytest deprecation warning.
Cases cover missing, empty, malformed and nonstring root/transitive hashes before ANY wheel download, mismatched bytes not installed, corrupted cached wheel replaced with verified bytes, and valid uppercase hashes.
Parent reviewed the complete two-file implementation/test change: no blocking finding for this bounded scope.

## Limits and next gates
This checks wheel bytes against the supplied lockfile, not authenticity of that lockfile. Core runtime and lockfile downloads/cache provenance remain unchanged. This is not a full artifact inventory or licence clearance, atomic directory replacement, native CAS adapter, deployment or paid validation.
Next: exact-head hosted CI; integrate when green, then implement actual artifact inventory with runtime provenance and retained wheel/runtime/native notices. Use RELEASE-PREFLIGHT-20261107.md acceptance matrix. Do not infer production readiness from synthetic fixtures.
