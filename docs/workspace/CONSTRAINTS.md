# CONSTRAINTS — CAS_AZEEM × Calculator 2.0: the merge

Last updated: 2026-10-27 (v3)

The engine's code-generation constraints are `[CAS v0.3 §6.1–6.15]`. Drafted constraints 16–18 are pending in the 22 Sep plan (doc 03):
- 16 — accelerator doctrine;
- 17 — simplification doctrine;
- 18 — benchmarks.

They bind any code that touches CAS_AZEEM, including code generated from this repo. This file adds only what the merge needs, and keeps v1's numbering where it was referenced.

## Roles

- **Owner (Nick).** Rules on design and authorises pushes. On the merge he is consulted only for the batch in SPEC §6, and for deadlocks between agents.
- **Coordinator (Right Hand).** Execution only on CAS work (CLAUDE-NOTE-20261027-04):
  - Linear per doc 03 §5;
  - repository administration and history preservation per doc 03 §6;
  - registration of the data.
  It does not draft, edit, interpret or rule on this spec. It owns AWS provisioning (GOV-CLOUD-001).
- **Proxy (Claude).** Drafts this spec with Nick and builds per brief. Also the skeptic PR reviewer (SUBMIT-002).
  - It has read-only access to this repo. It delivers branches as git bundles, and the Right Hand pushes them.

## Deadlock rule (administrative matters only)

- One written round: each side gives its case in five lines or fewer, and says what it forks.
- If that does not settle it, it goes to Nick as one batched question.
- Spec questions never enter this rule. Claude takes them to Nick directly.

## Constraints

1. **Strict TDD; tests never edited to pass** — `[CAS v0.3 §6.1–6.2]`.
2. **Docs in the same commit as the change.**
   - Exception ⟨open⟩: `docs/LEGACY_API.md` is generated and test-enforced in this repo.
   - Proposal: it retires with the legacy tabs at W2. The CAS no-autogeneration rule (16 Aug) binds the CAS repo's `api/`.
3. **Escalation** — `[CAS v0.3 §6.3]`, plus the front-end/engine boundary (SPEC §4.2) and graph identity (§4.3).
4. **Gates.** Green at every commit:
   - this repo's suites;
   - CAS's mypy --strict;
   - the hash battery;
   - a bare-environment core run.
   Exact-head evidence at `d3263cf`, local run by Claude on 27 Oct: Python 85/85 and JS 16/16 pass, with Python 3.13.17, SymPy 1.14.0, pytest 9.1.1 and Node 22.23.4. Playwright e2e was not run. GitHub-hosted CI at that head is still unverified (ATL-13).
5. **Imports — closed list** (owner, 27 Oct; RELAY-04; widened 13:27).
   - Engine paths (CAS core and the workspace back end): stdlib only.
   - CAS_AZEEM is the only engine that produces results. No external system computes anything at runtime.
   - External checkers — SymPy, Mathematica/Wolfram, Maple and any other — run at test or verification time only. In this repo, SymPy (and NumPy or SciPy, if ever used) lives in `tests/oracle/` only.
   - Every cross-check is recorded: which tool checked what, by what method (symbolic, or numerical such as random-point evaluation), and whether it agreed. Nothing is checked silently. This extends CAS constraint 10 (`tests/oracle.py`) from SymPy to any external checker.
   - `cas_azeem.plot` (W3): Matplotlib, mpl_toolkits.mplot3d, Seaborn and NumPy, and nothing else.
   - Any addition escalates.
   - The status of `cas.numeric` is ⟨open⟩, SPEC §4.4.
6. **Ambient state** — closed per the CAS 17 Aug ruling: the session log and the derivative registry. Nothing in the front end adds to it.
7. **Source discipline.** Anything not read from a source carries ⟨verify⟩. Gaps go to SPEC §6, never invented.
8. **Cloud** (proposal). No resource exists before GOV-CLOUD-001 C1–C8, an owner cap and alarms are in place.

## Contribution and licence

- External contributions: closed until the licence is final and a CLA exists (doc 02).
- Licence model (doc 02, 13 Aug, draft pending counsel):
  - noncommercial free forever;
  - a 40-day commercial evaluation per entity;
  - a paid commercial licence, provisionally $995 per seat per year (doc 03 [R]).
- This repo is MIT today, and `docs/COMMERCIAL_ROADMAP.md` proposes separate consumer test prices. Both are SPEC §6, item 6.
