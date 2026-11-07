# INDEX — CAS_AZEEM × Calculator 2.0 (merge doc set)

This set was instantiated on 2026-10-27 from MetaSpec v1. v2 rebased it the same day on the CAS_AZEEM sources. v3 (27 Oct, 15:50) rebased it on PR #13 head `d3263cf` and folded in the owner's 13:27 rulings. The 7 November v4 mirror applies STATE.md's recorded delegation and batch decisions to SPEC, CONSTRAINTS and MILESTONES. Original imported texts remain in Git history.

## Sources and their grade

| Source | Grade | Where |
|---|---|---|
| CAS Context v1.0 + Status & Perimeter v0.3 (13 Aug) | verbatim | Drive spec pack, doc 01 |
| CAS STATE.md, 17 Aug snapshot | verbatim | doc 02 |
| State after August; 22 Sep v1 plan | Claude's records [R] and proxy rulings [P] | doc 03 |
| Owner rulings, 27 Oct 13:27 (oracle scope; ODE/PDE north star) | verbatim, sent with approval | CLAUDE-CORRECTION-20261027-07 |
| CAS repo STATE.md (live) | authoritative for engine behavior, later than doc 02 | https://github.com/nickyazdani9-ux/CAS_AZEEM ; source imported, original ancestry unverified |
| better_calculator PR #13 at `d3263cf` | read 27 Oct 15:50 | this repo, docs/ and python/ |

The Drive spec pack is "CAS_AZEEM — spec pack for Right Hand (2026-10-27)".

`d3263cf` is two commits ahead of `1713a96`, which v1 and v2 cited. Neither commit touches `python/`, so every Python call site in the inventory is unchanged (`git diff --stat 1713a96 d3263cf`).

## Reading path

1. IMPORT_RECEIPT_20261107.md — source provenance and current reconciliation; STATE.md is retained as the dated verbatim v4 source.
2. SPEC.md — the merge design, with the engine cited rather than restated.
3. CONSTRAINTS.md — the merge rules on top of CAS §6.
4. MILESTONES.md — the CAS M0–M9 engine track and W1–W4 merge/commercial track.
5. STATE.md — the 7 November 14:40 snapshot and decision source. Its source-access/status statements are historical; read the import receipt for superseding evidence.
6. W1_SYMPY_INVENTORY.md — every SymPy call site, its CAS cover and its fate. Formerly M4_SYMPY_INVENTORY.md.

The current interpretation and unimplemented boundaries are recorded separately in RECONCILIATION_20261107.md; STATE.md remains the verbatim historical source.

## Linear homes

- Engine: P-ATL-37 "CAS_AZEEM — Engine" (M4–M9, rulings ATL-367 to ATL-370).
- Merge: P-ATL-4 "Better Calculator" (W1–W4; ATL-371 to ATL-376 and commercial work).
- Coordination queue: ATL-313.

## Conventions

- Identifiers are permanent, and the CAS identifiers keep their meaning.
- Merge identifiers are W-prefixed.
- Retired identifiers are struck through and listed in SPEC §5.
- ⟨verify⟩ means inferred; ⟨open⟩ means unresolved. Routine rulings are delegated under the 7 November authority; only owner-only account/identity actions require Nick.
- Decisions are written as `decision — rationale — date`.
