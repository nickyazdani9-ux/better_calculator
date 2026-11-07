# CONSTRAINTS — CAS_AZEEM × Calculator 2.0: the merge

Last updated: 2026-11-07 (v4 mirror of STATE.md Decisions; historical import retained in Git)

The engine's code-generation constraints are `[CAS v0.3 §6.1–6.15]`. Drafted constraints 16–18 are pending in the 22 Sep plan (doc 03):
- 16 — accelerator doctrine;
- 17 — simplification doctrine;
- 18 — benchmarks.

They bind any code that touches CAS_AZEEM, including code generated from this repo. This file adds only what the merge needs, and keeps v1's numbering where it was referenced.

## Roles and decision recording

The 7 November full-delegation ruling in STATE.md supersedes the older execution-only and per-item owner approval roles.

- **Owner (Nick).** Sets goals. Only actions requiring his identity or account control return to him (for example financial-account opening); routine design, implementation and reviewed integration decisions are delegated.
- **Claude (proxy) and Right Hand.** Make and record design decisions within the existing mathematical constraints. A decision must cite the affected invariant, rationale and acceptance evidence. No silent change to node identity, hashing, layering or licensing.
- **Implementer and reviewer.** Use separate review where available, one writer per branch, exact source revisions and explicit acceptance. A missing acknowledgement is never approval or proof of execution.
- **Access.** Repository access is verified per connector. The native source is available; Claude's independent access must not be inferred from Right Hand access. See IMPORT_RECEIPT_20261107.md.
- **Unresolved source gaps.** Preserve missing original-plan text as a gap. Do not manufacture the 22 September plan from summaries; continue independent work whose contract is available.

## Constraints

1. **Strict TDD; tests never edited to pass** — `[CAS v0.3 §6.1–6.2]`.
2. **Docs in the same commit as the change.**
   - Exception ⟨open⟩: `docs/LEGACY_API.md` is generated and test-enforced in this repo.
   - Proposal: it retires with the legacy tabs at W2. The CAS no-autogeneration rule (16 Aug) binds the CAS repo's `api/`.
3. **Design review and recorded proxy rulings** — `[CAS v0.3 §6.3]` classes, including the front-end/engine boundary (SPEC §4.2) and graph identity (§4.3), now go to Claude and Right Hand under the 7 November delegation. Record the ruling and tests; no per-item owner approval. D1, exact arithmetic and provenance remain requirements.
4. **Gates.** Green at every commit:
   - this repo's suites;
   - CAS's mypy --strict;
   - the hash battery;
   - a bare-environment core run.
   Exact-head evidence at `d3263cf`, local run by Claude on 27 Oct: Python 85/85 and JS 16/16 pass, with Python 3.13.17, SymPy 1.14.0, pytest 9.1.1 and Node 22.23.4. Playwright e2e was not run. GitHub-hosted CI at that head is still unverified (ATL-13).
5. **Imports — closed list** (owner, 27 Oct; RELAY-04; widened 13:27).
   - Engine paths (CAS core and the workspace back end): stdlib only.
   - CAS_AZEEM is the only engine that produces results. No external system computes anything at runtime.
   - External checkers — SymPy, Mathematica/Wolfram, Maple and any other — run at test or verification time only. In this repo, SymPy and SciPy live in `tests/oracle/` only. NumPy has the separate plotting-only allowance below; it is not an engine dependency.
   - Every cross-check is recorded: which tool checked what, by what method (symbolic, or numerical such as random-point evaluation), and whether it agreed. Nothing is checked silently. This extends CAS constraint 10 (`tests/oracle.py`) from SymPy to any external checker.
   - `cas_azeem.plot` (W3): Matplotlib, mpl_toolkits.mplot3d, Seaborn and NumPy, and nothing else.
   - Any addition requires a recorded proxy design ruling.
   - `cas.numeric` and `lower()` are deferred to v1.x; they will be stdlib-only or a C extension. NumPy is permitted only at the plotting boundary (SPEC §4.4). The installed native package currently imports as `cas`; the design name `cas_azeem.plot` does not rename existing modules or prove that extra exists.
6. **Ambient state** — closed per the CAS 17 Aug ruling: the session log and the derivative registry. Nothing in the front end adds to it.
7. **Source discipline.** Anything not read from a source carries ⟨verify⟩. Gaps go to SPEC §6, never invented.
8. **Cloud** (proposal). No resource exists before GOV-CLOUD-001 C1–C8, an owner cap and alarms are in place.

## Contribution and licence

- External contributions: closed until the licence is final and a CLA exists (doc 02).
- Licence model (doc 02, 13 Aug, draft pending counsel):
  - noncommercial free forever;
  - a 40-day commercial evaluation per entity;
  - a paid commercial licence, provisionally $995 per seat per year (doc 03 [R]).
- The shell stays MIT and CAS_AZEEM is licensed separately under the source-available model (STATE.md, 7 November). Consumer and seat prices are tiers of one proposed model, not proof of payment validation. Draft licence text remains a release gate; this mirror neither activates it nor grants clearance.
