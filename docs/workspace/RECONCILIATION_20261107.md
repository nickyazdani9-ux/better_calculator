# Workspace v4 reconciliation — 7 November 2026

## Source and scope

The imported `STATE.md` v4 is preserved verbatim as a historical source snapshot: 10911 UTF-8 bytes, MD5 `f3df5bd6ff8b7ce5ae0991d7d13519c2`. Baseline commit `7ab5d082e3d43c2d53fb171022fa8b4f763320e5` preserves the original v3 mirrors and source receipt. This follow-through changes SPEC, CONSTRAINTS, MILESTONES and INDEX to reflect decisions already recorded in STATE; it does not revise the engine design.

## Current interpretation

| Area | Recorded decision / evidence | Remaining work |
|---|---|---|
| Authority | STATE's 7 November delegation supersedes per-item owner design approval. | Record proxy rationale, invariant and acceptance evidence; account/identity actions still require the account holder. |
| Package boundary | Separate native wheel; no monorepo. Native packaging PR3 merged at `ea84f1e80029f410147f22ae5dc08ffb217e5cb5`. | Browser vendoring, adapter and deployment acceptance. A wheel is not a migrated browser. |
| W1 | Historical inventory remains tied to `d3263cf`. | Current per-operation inventory and remaining acceptance. |
| W2 | Feature-by-feature replacement; honest unsupported results; D1, exact arithmetic and native derivation evidence. | Parser work is only a first slice. No completed W2 or native browser operation is claimed by this reconciliation. |
| Graph | Workspace projection over native edge log; content hashes identify values. | Verify implementation; do not add a second mathematical provenance record. |
| W3 | NumPy only at plotting boundary; no drawing across kernel-known poles, branch cuts or asymptotes. | Plot implementation, per-plot acceptance and browser package checks. Numeric lowering remains deferred to v1.x. |
| W4 | One billing hub, account and engine-side signed-token design; consumer and seat tiers share one model. | Payment activation, signed-key implementation, final terms and commercial acceptance. Prices remain proposals. |
| Windows | Retained target. | Build and release evidence. |
| Native plan | P1/P2/P4/P7 veto window closed; rulings stand. | Exact original 22 September plan text still missing (ATL-353 / O15); do not reconstruct it from summaries. |

The installed native namespace is `cas`. The STATE names `cas_azeem.plot` and `cas_azeem.licence.check(token) -> Tier` are proposed interfaces, not existing-module claims or rename instructions.

## Validation scope

Documentation-only reconciliation. STATE and the historical SymPy inventory are unchanged. No Python, JavaScript, native engine, tests or deployment configuration is changed. Runtime completion requires its own implementation and evidence.
