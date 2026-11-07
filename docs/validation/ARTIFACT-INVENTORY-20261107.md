# Packaged artifact inventory — 7 November 2026

Work ID: RH-SHIP-20261107-11. Implementation base: calculator
`82c79dfc20c0a62ca3d1b24fc21252214fb96530`.

The offline inventory tool records actual built file paths, byte lengths and
SHA-256 digests. For each wheel it also hashes the root dist-info METADATA,
WHEEL and RECORD members and recognised licence/notice members without
extracting or executing them. Metadata text is deliberately not interpreted as
proof of package identity or licensing. No package code or network is used.

Run after a complete build, while the directory is quiescent:

```sh
python scripts/artifact_inventory.py dist \
  --output /tmp/calculator-artifact-inventory.json \
  --source-revision FULL_40_CHARACTER_COMMIT_SHA
```

The output must be outside the artifact directory so that the receipt cannot
include itself. The source revision is caller-supplied provenance, not an
authenticated source-to-build attestation. Receipts omit timestamps and
absolute build paths; unchanged inputs and revision yield identical JSON.

Exit status:

- `0`: inventory written; required notices and wheel metadata evidence found.
- `2`: inventory written with explicit missing/empty required notices or
  missing wheel METADATA/RECORD/WHEEL evidence.
- `1`: invalid input; no new inventory written. Existing output is preserved.

Filesystem symlinks/nonregular files, unsafe/duplicate wheel member names,
wheel symlinks, unreadable archives and oversized selected evidence are
rejected. Multiple top-level dist-info directories are rejected as ambiguous;
empty METADATA or WHEEL members remain explicit missing evidence. Evidence is
limited to 8 MiB per member and 32 MiB per wheel, with
10,000 members maximum. Files and selected members are hashed in chunks.
The tool is for trusted, static build outputs, not a concurrent/untrusted
filesystem sandbox or a complete validation of every wheel payload member.

## Test evidence

Tests preceded implementation. RED: unittest discovery failed because
`scripts.artifact_inventory` did not exist. Initial GREEN: 17 synthetic tests passed.
Parent review found that required metadata names could be combined across
different dist-info directories. Three new regressions failed (split directory,
extra empty directory, empty required metadata), then passed after the guard
was fixed. Final GREEN: **20 synthetic tests passed**
using Python 3.12.14 and the standard-library unittest runner:

```sh
python -m unittest discover -s tests -p test_artifact_inventory.py -v
```

Cases cover deterministic ordering, changed bytes, exact member hashes,
nonexecution/nonextraction, missing/empty notices, missing wheel evidence,
missing roots, malformed revisions, ambiguous dist-info directories, empty
required metadata, filesystem and archive symlinks, corrupt
archives, traversal and duplicate names, selected-member size bounds, output
location, successful CLI receipts and explicit-gap exit status.

The initial attempted pytest command could not run because pytest was not
installed in the isolated implementation environment; unittest required no
installation. Parent integration and hosted CI results must be recorded
separately. No real packaged-artifact inventory or hosted result is claimed by
this local synthetic receipt.

## Still required before release

The report always says `licence_clearance: false` and
`provenance_authenticated: false`. Finding a licence-like filename does not
establish permission or complete notice/source obligations. Review actual
runtime, stdlib, wheel, font and native-shell obligations and upstream
authenticity. The tool does not prove runtime completeness, parse semantic
metadata validity or verify RECORD entries against package contents. Missing
wheel notice candidates are explicit and need human or
evidence-backed review; they do not silently become licence clearance.

Native CAS is not bundled, copied, relicensed or deployed by this tool. Product
claims, signed releases, browser/offline acceptance and paid validation remain
separate gates.

## Parent integration receipt

Parent reread current contributing instructions and verified every baseline Git
blob against feature head82c79df before integration. No AGENTS.md was present
in that revision's recursive tree. The current web CI job now inventories
`dist` immediately after `build:native` and uploads a separate
`calculator2-web-inventory` artifact retained for 14 days. It binds the supplied
source revision to the actual CI checkout SHA. Publication conditions and
runtime behavior are unchanged. No private CAS code or wheel is introduced.

Parent review found split dist-info directories and empty METADATA/WHEEL could
be counted as complete evidence. Three regression cases failed before the
correction; all 20 inventory tests then passed. Full current integration:
**187 Python tests plus 10 subtests, and 23 JavaScript tests passed locally**.
Catalog regeneration retained exact blob f04de9d5e4d8fc6f8679f3dfaba14ae813d2c856.
Workflow YAML parsed and inventory ordering/output location were checked.
See artifact-inventory-full-python.txt and artifact-inventory-full-js.txt.
The initial full-suite attempt lacked pytest; the test-only dependencies were
installed to a temporary directory before the successful full run.

Hosted exact-head acceptance and the first real bundle inventory remain
pending at this commit. This is implemented and locally tested, not deployed
or paid-validated. Next: inspect successful hosted manifest, reconcile its
actual wheel/runtime/font notices and upstream sources; retain separate native
CAS, signing and payment gates.

## Windows CI correction

Run42371999933 passed three unit platforms but failed the Windows unsafe ZIP
name subtest (job128401865265): ZipInfo normalizes backslashes on Windows.
The fixture now writes the literal adversarial member spelling; the validator
checks orig_filename before platform normalization instead of filename.
An additional test simulates Windows normalization on every test platform.
The corrected full local suite passes **188 tests plus10 subtests**; see
artifact-inventory-portable-python.txt. The21 inventory tests include the new
regression. Production runtime and JS remain unchanged. This supersedes the
initial local-only count above for the corrected head. Hosted rerun pending.

Failure evidence: https://github.com/nickyazdani9-ux/better_calculator/actions/runs/42371999933/job/128401865265
