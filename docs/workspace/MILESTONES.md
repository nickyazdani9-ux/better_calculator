# GOALS & MILESTONES — CAS_AZEEM × Calculator 2.0

Last updated: 2026-11-07 (v4 mirror; implementation status distinguished from design decisions)

- Engine track: CAS M0–M3 shipped; CAS M4 next, per the 22 Sep plan. Linear P-ATL-37.
- Merge track: W1 inventory reconciliation open; W2 implementation open; W3/W4 design released for work. Linear P-ATL-4. No feature is marked implemented by this documentation mirror.

## Telos

Mathematics, then physics, then chemistry, as one instrument. The engine's tiebreaker is `[CAS v0.3 §1.1]`.

Product north star (owner, 27 Oct 13:27): a full ODE-solving library — any tractable ODE or PDE system — on a registration ladder built to be extended.

## Goals

- CAS G1–G9 `[CAS v0.3 §1.2]`, unchanged. G6 was amended 13 Aug to source-available.
- G10 — one workspace on CAS_AZEEM; external systems compute nothing at runtime and stay as test-time cross-checks only. Served by W1–W2.
- G11 — the best plotting of any CAS (Matplotlib, mplot3d, Seaborn). Served by W3.

## Anti-goals

- Feature parity with SymPy, Sage or Mathematica. CAS judges itself against the owner's standards `[CAS v0.3 §7]`.

## Engine track (CAS_AZEEM repo — its STATE.md is authoritative)

| M | Name | Status | Source |
|---|---|---|---|
| M0, M0.1 | Kernel | Shipped a3a8e00, 325d1ab; reviewed: passed | doc 02 |
| M1 | DAG + rewrite engine + six rules | Shipped 2ef8f79..80d87ac; source snapshot reported owner review pending; review now delegated | doc 02 |
| M2 | Ω: registry, d, as_omega, partial, divide | Shipped 7ddf153, 8f31bdf..b61cbec; 423 tests | doc 02 |
| M3 | Solver interface, degree-1 ladder | Shipped ~20 Aug; 551 tests ⟨verify⟩ against the repo | doc 03 [R] |
| M4 | Integration ladder, indefinite | Next native milestone. Exact completion-plan text must be recovered before its verbatim application (ATL-353/O15); the veto window was closed by the 7 November delegation (ATL-368) | doc 03 [P]; CORRECTION-07 |
| M5 | Licensed tier (normal forms, equivalent, Verified path) | Planned | doc 03 [P] |
| M6 | Polynomial and rational views; G9 matrices | Planned | doc 03 [P] |
| M7 | Riccati family rungs | Planned | doc 03 [P] |
| M8 | Definite integration | Planned | doc 03 [P] |
| M9 | G8 completion; tag v1.0 | Planned | doc 03 [P] |
| — | PDE (first entry: method of characteristics) | After v1.0; not yet cut | owner, 27 Oct 13:27 |

- The standing definition of done for M4–M9 is in doc 03 §4. It is not copied here.
- The development pause from 7 Sep was reversed on 22 Sep.

## Merge track

### W1 — SymPy exit inventory (in progress; formerly "M4", 27 Oct) — ATL-371

- Purpose: turn G10 into a checklist. Spec §4.
- Definition of done:
  - [x] Every SymPy import and call site is listed with file:line and the feature it backs (W1_SYMPY_INVENTORY.md, at `d3263cf`; Python identical to `1713a96`).
  - [x] Each site is mapped to the CAS milestone that covers it, or marked as a gap. Remapped in v2 against CAS M0–M9.
  - [x] Each site is sorted into one of two fates (RELAY-04): replaced by CAS_AZEEM, or kept as an oracle test. Done in the inventory's Fate column, v2.
  - [x] NumPy and SciPy call sites are inventoried. There are none anywhere in the repo's Python at `d3263cf` (checked with grep, 27 Oct).
  - [ ] Review the reconciled SPEC §4 mirror against current implementation. The 7 November delegation replaces per-item owner review with proxy review.
  - [ ] ⟨verify⟩ count reported at close; NEXT.md written; end commit.
- Out of scope: removing any code.
- Note: ATL-371's first pass (another Claude session) counts SymPy symbols per file (9 files, 62 symbols) where this inventory counts calling functions (48). Both are now at `d3263cf`, so they describe one codebase in two units; this file is the one of record. ATL-371's remaining piece — one fate per registered operation in `docs/LEGACY_API.md` — is not in this DoD and stays with ATL-371.

### W2 — Front end on CAS_AZEEM (implementation open) — ATL-374

- Purpose: swap `run_json`'s back end feature by feature (Spec §4.2).
- Design gates settled in STATE.md on 7 November: wheel package boundary, graph projection and labelled gaps. Native source is available in the private CAS_AZEEM repository. Do not wait on a repeated source-upload approval.
- Delivery acceptance remains per feature: restricted parser to native nodes, tested wheel integration, native operation and DAG evidence, and browser acceptance. No runtime external-engine fallback.
- Unsupported features are labelled “not available in CAS_AZEEM v1.0”; parity is not required.
- Each feature lands only once its CAS milestone has shipped. The historical inventory identifies these candidates against shipped CAS M0–M3; each still needs current native API and integration acceptance:
  - symbols and numbers;
  - expand and distribute;
  - differentiate, gradient, Hessian and Jacobian (via `d` and `partial`);
  - degree-1 ODEs;
  - LaTeX.
- A feature is complete only with tests against the installed native wheel, exact arithmetic and literal-tree/provenance preservation, rejected unsafe input, honest unsupported results, and browser-level integration evidence. This operational checklist implements the recorded boundary; it does not expand native mathematical coverage.

### W3 — Plotting extra (design open for implementation; formerly "M6", RELAY-04) — ATL-376

- Purpose: G11 (Spec §4.5).
- Measure accepted 7 November (ATL-375): do not draw across poles, branch cuts or asymptotes the kernel already knows. Per-plot tests live in `tests/plot/`.
- Plotting-only NumPy scope is settled. Native `cas` namespace remains unchanged; `cas_azeem.plot` is the planned design boundary, not proof of an existing extra.
- Can run alongside CAS M4, because it touches no kernel code.

### W4 — Billing hub and licence keys (design open; not implemented)

- One processor account under Atlas Inference, one portal, per-product storefronts.
- Proposed signed token checked offline by the engine against a shipped public key; no front-end-only paid-feature enforcement.
- Consumer and commercial seat offerings are tiers of one model. Shell MIT and CAS source-available remain distinct.
- Account activation and final terms are release dependencies. Neither payment handling nor a key checker is implemented by these documents.
- Price proposals and provider preference in STATE.md remain hypotheses until an account and commercial acceptance evidence exist.

## Re-cuts

- 27 Oct (v2): the v1 cut (M0–M5, M6 in RELAY-04) is retired and replaced by CAS M0–M9 plus W1–W3.
  - Why: v1 was drafted before the CAS sources were reachable. Its M2/M3 were shown as blocked although both had shipped, and its M4–M6 collided with CAS M4–M6 from the 22 Sep plan.
  - The crosswalk is in SPEC §5. The same cut is in Linear (ATL-367 asks Nick to accept it).
- 27 Oct (v3): no re-cut. A post-v1.0 PDE milestone is noted on the engine track, uncut, per the 13:27 direction.

## Design follow-through

The boundary/DAG and plotting/numerical questions were settled by proxy on 7 November under full delegation. They no longer require a separate owner design session. Keep decisions and evidence in STATE.md and the current work item.

The licensed tier remains native CAS M5, not implemented by this mirror. The exact 22 September completion plan remains missing; its detailed rulings are not invented here. W1's historical inventory at `d3263cf` still needs current per-operation reconciliation before it can describe today's migration coverage.
