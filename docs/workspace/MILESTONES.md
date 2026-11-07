# GOALS & MILESTONES — CAS_AZEEM × Calculator 2.0

Last updated: 2026-10-27 (v3)

- Engine track: CAS M0–M3 shipped; CAS M4 next, per the 22 Sep plan. Linear P-ATL-37.
- Merge track: W1 in progress; W2 and W3 proposed. Linear P-ATL-4.

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
| M1 | DAG + rewrite engine + six rules | Shipped 2ef8f79..80d87ac; owner review pending | doc 02 |
| M2 | Ω: registry, d, as_omega, partial, divide | Shipped 7ddf153, 8f31bdf..b61cbec; 423 tests | doc 02 |
| M3 | Solver interface, degree-1 ladder | Shipped ~20 Aug; 551 tests ⟨verify⟩ against the repo | doc 03 [R] |
| M4 | Integration ladder, indefinite | Next. Gated on applying V1_COMPLETION_PLAN.md to the repo as one commit (ATL-353); the 22 Sep veto window closes at its first use (ATL-368) | doc 03 [P]; CORRECTION-07 |
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
  - [ ] PR #13 content is merged into SPEC §4 (first pass in v1–v3), with Nick's review.
  - [ ] ⟨verify⟩ count reported at close; NEXT.md written; end commit.
- Out of scope: removing any code.
- Note: ATL-371's first pass (another Claude session) counts SymPy symbols per file (9 files, 62 symbols) where this inventory counts calling functions (48). Both are now at `d3263cf`, so they describe one codebase in two units; this file is the one of record. ATL-371's remaining piece — one fate per registered operation in `docs/LEGACY_API.md` — is not in this DoD and stays with ATL-371.

### W2 — Front end on CAS_AZEEM (proposed) — ATL-374

- Purpose: swap `run_json`'s back end feature by feature (Spec §4.2).
- Gated on:
  - Nick's rulings in SPEC §6, items 1, 2 and 5;
  - the CAS remote URL (ATL-352, Nick).
- Each feature lands only once its CAS milestone has shipped. The inventory gives the order. Shippable now on shipped CAS M0–M3:
  - symbols and numbers;
  - expand and distribute;
  - differentiate, gradient, Hessian and Jacobian (via `d` and `partial`);
  - degree-1 ODEs;
  - LaTeX.
- The definition of done is set at open.

### W3 — Plotting extra (proposed; formerly "M6", RELAY-04) — ATL-376

- Purpose: G11 (Spec §4.5).
- Gated on Nick accepting a measure (SPEC §6, item 4; ATL-375).
- Can run alongside CAS M4, because it touches no kernel code.

## Re-cuts

- 27 Oct (v2): the v1 cut (M0–M5, M6 in RELAY-04) is retired and replaced by CAS M0–M9 plus W1–W3.
  - Why: v1 was drafted before the CAS sources were reachable. Its M2/M3 were shown as blocked although both had shipped, and its M4–M6 collided with CAS M4–M6 from the 22 Sep plan.
  - The crosswalk is in SPEC §5. The same cut is in Linear (ATL-367 asks Nick to accept it).
- 27 Oct (v3): no re-cut. A post-v1.0 PDE milestone is noted on the engine track, uncut, per the 13:27 direction.

## Design sessions

These are Nick and Claude only; the Right Hand is not involved (CLAUDE-NOTE-20261027-04).

- **Boundary and DAG** (SPEC §4.2, §4.3) — gates W2.
- **NumPy/SciPy scope and the plotting measure** (SPEC §4.4, §4.5) — gates W3, and CAS v1.x `lower()`.
- **Licensed tier** — already scheduled as CAS M5 (doc 03).
