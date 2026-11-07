# Release preflight correction and remaining artifact gates — 7 November 2026

Work: RH-SHIP-20261107-06. Base: 8fe56c0dcb3e9c38d74f3cb8ba7d1bdc233697a2.

## Reproduced and fixed
The release build deleted existing output before checking offline Pyodide availability. Missing KaTeX dist and missing required source inputs also destroyed an existing artifact before failing. Required input existence checks now precede output removal.

Synthetic actual-build regression: three new tests failed because dist/previous.html disappeared; four existing tests passed. After correction, all 23 JavaScript and 150 Python tests passed locally; git diff --check passed. Python emitted one external anyio/pytest deprecation warning. No network/customer data used in tests.

Commands: node --test tests/test_release_notices.mjs (red 3 failed / 4 passed); node --test tests/*.mjs (green 23); python -m pytest tests/test_*.py -q (green 150).

Scope: preserves previous output for known missing-input preflight failures. This is NOT transactional replacement: later copy/I/O failure or a concurrent input mutation can still leave partial output. Empty/corrupt runtime validation, full file-type validation, content integrity, and atomic staging/promotion remain separate work.

## Current release evidence
Base CI [run 42350479746](https://github.com/nickyazdani9-ux/better_calculator/actions/runs/42350479746) has 14 successful checks, 3 publication jobs skipped. This is prior/base evidence, not CI for this correction.
The run lists web artifact 13564794025 plus Android, iOS simulator and desktop artifacts. Binary contents were not inspected in this pass. No deployed/signed/paid-validated state is inferred.

## Concrete next artifact acceptance package
Source audit of scripts/vendor_pyodide.py and scripts/build-web.mjs establishes these gaps; it is not blanket legal clearance.

| Component | Current evidence gap | Required closure |
| --- | --- | --- |
| Runtime core | Five core files downloaded without expected hashes; nonempty cached files accepted | Record exact version, source URL and SHA256 per actual core file; validate expected hashes and reject corrupted cache |
| SymPy dependency wheels | Hash verification is optional via entry.get('sha256'); no archive notice inventory | Require well-formed expected hashes; emit transitive package/version/file/hash inventory and retained archive notice paths/hashes |
| Runtime and stdlib | Pyodide root notice retained, component coverage not demonstrated | Inspect actual JS/WASM/stdlib distribution and retained third-party notices; map components to source and notice evidence |
| KaTeX/fonts | Package root notice copied; deployed font coverage not recorded | Match actual files to pinned package and document font provenance/notice coverage without assuming all files share a licence |
| Native wrappers | Build success only; no final packaged dependency notice inventory | Inspect each shipping Electron/Capacitor archive for required notices and source locations; separate unsigned previews from signed/device-verified releases |

Synthetic inventory tests should cover missing hashes, mismatched wheel bytes, corrupted runtime cache, missing notice evidence and valid transitive packages. Actual artifact hashes must bind the acceptance record; synthetic fixture success alone cannot clear real artifacts.

Main currently couples PWA deployment and Android preview publication. A web-only release requires explicit workflow scoping plus its own claims/privacy/onboarding/smoke/rollback acceptance; native coverage cannot silently be treated as complete. Native CAS adapter remains unimplemented.
