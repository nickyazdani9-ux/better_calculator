# Native parser CI acceptance contract
Work RH-SHIP-20261107-10, 7 November 2026. Status: reviewable integration specification; no workflow installed or executed by this change.

## Source evidence and scope
- Calculator integration baseline: [82c79df](https://github.com/nickyazdani9-ux/better_calculator/tree/82c79dfc20c0a62ca3d1b24fc21252214fb96530).
- Parser candidate: [PR23](https://github.com/nickyazdani9-ux/better_calculator/pull/23), 07702bd3319aa6dae35672e20c5174019d2a75a9. Its NATIVE_PARSER_SLICE.md records 82 native cases plus 167 existing cases locally, not hosted native acceptance.
- Native typed-wheel baseline: private CAS_AZEEM 57ad1432b2baa21763ddc8fb435684b38b00d915, .github/workflows/ci.yml.
- Calculator pipeline.yml runs tests/test_*.py only. Its green status cannot cover tests/native.
- SPEC 4.2 requires a separately built wheel; no monorepo. SPEC 6 requires honest gaps and no external runtime fallback. This contract does not switch run_json/worker/UI or approve private source distribution.

## Proposed placement and trust boundary
Implement a manual, reviewed native-parser-consumer job in the PRIVATE CAS repository first. This avoids giving the public calculator workflow private-repository credentials or publishing the private wheel in public artifacts. Existing private native CI builds a dependency-free wheel, checks installed smoke/typing and retains it for 14 days.

Inputs are two complete immutable commit SHAs: native_source_sha and calculator_source_sha. Repository identities are fixed literals, never caller-supplied URLs. A reviewed allowlist/receipt must match both SHAs before execution; branch names, PR numbers and moving tags are not sufficient authorization. A fork or an updated PR head does not inherit acceptance. The public calculator code executes only after exact-source review, with no deployment authority, no secrets passed to test steps and no persisted checkout credential. Do not use pull_request_target to execute PR code.

Keep public status reporting separate from test execution. Initially publish only a manually reconciled canonical receipt; installing a bot/check reporter requires separate access setup. Do not place an outbound private-repo token in the process environment running calculator tests. No permissions, secrets or accounts are created by this specification.

## Job sequence
1. Resolve both reviewed SHA inputs; verify checked-out HEADs exactly equal them. Record workflow revision and Python/tool versions. Refuse unknown/unreviewed inputs before dependency installation or tests.
2. Run native validation at the selected native revision. Build the wheel from that checkout using its pinned build tools. Record actual wheel filename, size and SHA256. Do not reuse the parser document's historical local hash as an expected hash for a fresh build; byte reproducibility has not been established.
3. Create an isolated environment outside both checkouts. Install that wheel with --no-index --no-deps. Verify import resolves to the environment's site-packages, not the source tree; verify the PEP561 marker. Keep build provenance and wheel digest together.
4. Install the explicit test-only dependencies in the test environment. Start with the versions already in native CI: pytest9.2.0, hypothesis6.170.15, mypy2.4.1 and sympy1.14.0; add only dependencies justified by current calculator tests. These are source pins, not a promise of future availability. Never package test oracles as native runtime dependencies.
5. From the calculator checkout, run the explicit native test path and existing regression suite. Do not let the top-level wildcard substitute for the native suite:

    python -m pytest tests/native/test_native_parser.py tests/test_*.py -q
    python -m mypy --strict --no-incremental python/native_parser.py

   Confirm mypy resolves the installed typed wheel rather than a local cas directory or ignored imports. Run on Python3.12 and3.13 as the native CI matrix does. Capture collection counts and exit codes. Native dependency absence must fail, not skip.
6. Keep detailed logs, wheel and private reports inside the private repository. Inspect logs for private content before any external summary. Public/canonical receipt contains only approved revision identifiers, check outcomes, counts and an access-controlled run link; do not upload wheel bytes, private source, environment dumps or customer data to public calculator artifacts.
7. Parent reviews the exact run and records acceptance against the pair of source SHAs. A later native or parser revision invalidates that pair's applicability. Do not label the adapter/browser migration complete from parser-only acceptance.

## Required negative and positive acceptance cases
| ID | Case | Required result |
|---|---|---|
| NC01 | Missing/private wheel unavailable | Native collection fails; no skip-based green |
| NC02 | Requested SHA differs from checkout/review receipt | Refuse before execution |
| NC03 | Unreviewed fork/head or arbitrary repository URL | Refuse |
| NC04 | Wheel bytes differ from recorded build digest | Refuse installation |
| NC05 | Import accidentally resolves to checkout | Fail installed-boundary check |
| NC06 | PEP561 marker absent/ignored import used | Typing gate fails |
| NC07 | Native tests not collected | Fail despite top-level suite success |
| NC08 | Supported reviewed pair | Explicit native+regression tests and strict typing pass on both Python versions |
| NC09 | Parser or native SHA changes after green run | Require new pair-specific evidence |
| NC10 | Report/artifact publication | No private wheel/source or credentials in public outputs |

All NC cases are NOT_RUN under this contract. Existing local parser tests and native packaging checks are separate prior evidence. Implement synthetic rejection tests for dispatch/receipt validation without real secrets.

## Integration and rollback
Land workflow changes on a sole-writer private branch after current native instructions and budget/access review. Run only within existing authorized CI capacity; this document does not authorize new spending. If private workflow execution or artifact access is unavailable, record the exact failure; never silently move the wheel to a public repository. Disable the new job or revert its isolated commit if it fails trust-boundary acceptance; retain prior successful native checks. No product deployment is part of this work.

## Remaining gates
This contract supplies an implementable job/receipt boundary, not verified credentials, current artifact access or a completed run. Workflow implementation, reviewed SHA allowlist mechanism, exact private execution capability and budget remain to be verified by the native owner. Runtime adapter, per-operation inventory, licensing/source-distribution acceptance, browser/offline tests and paid entitlement checks remain separate. The exact O15 historical plan is not reconstructed and does not block this independent parser verification package.
