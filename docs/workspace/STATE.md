# STATE — CAS_AZEEM × Calculator 2.0: engine at CAS M3 (shipped); owner delegated all rulings 7 Nov; SPEC §6 batch ruled by proxy; W3 and W4 open; engine track and W2 blocked on repo access only

Last updated: 2026-11-07, 14:40

## Scope

This covers the merge and its commercialisation as of 7 Nov, 14:40:
- the doc set v4: v3 (27 Oct, on PR #13 head `d3263cf`) plus the 7 Nov delegation and the proxy rulings made under it;
- the W1 inventory, re-cited at `d3263cf`;
- the owner directions of 27 Oct (including 13:27) and 7 Nov.

It does not cover:
- engine internals (the CAS_AZEEM repo's STATE.md is authoritative);
- Structura (ATL-370);
- the exchange's other workstreams (ATL-313 holds those).

## Definition of done

W1 (in progress; MILESTONES.md holds the boxes): boxes 1–4 met. Box 5 (SPEC §4 merged, with owner review) is satisfied by the 7 Nov delegation — review is now the proxy's; closes at v4 mirror. Box 6 (close) follows.

W3, W4 open 7 Nov; boxes in MILESTONES.md.

## Decisions

- SymPy, NumPy and SciPy are test oracles only, quarantined under `tests/oracle/` — they are never the engine — owner, 27 Oct (RELAY-04). This refines the morning's "abandoned entirely".
- "SymPy abandoned" meant the Calculator 2.0 prototype, not the test oracle. CAS_AZEEM is the only engine that produces results; no external system computes anything at runtime. Any external checker (SymPy, Mathematica/Wolfram, Maple, others) is allowed at test or verification time only, symbolic or numerical, and every cross-check is recorded — owner, 27 Oct 13:27 (CORRECTION-07). Widens the RELAY-04 line above; CONSTRAINTS 5 carries it.
- Product north star: a full ODE-solving library, ODE and PDE. v1.0 (CAS M4–M9) stays ODE-only; PDE gets its own milestone after v1.0, entry point the method of characteristics — owner, 27 Oct 13:27.
- Plotting is a priority: Matplotlib, mplot3d and Seaborn through `cas_azeem.plot` — G11 — owner, 27 Oct.
- The name is CAS_AZEEM, with Calculator 2.0 as its front end — delegated to Claude by the owner, 27 Oct.
- Specs merge into one set; the merge is handled by Claude with Nick — owner, 27 Oct. On CAS work the Right Hand executes only (CLAUDE-NOTE-20261027-04).
- v1 identifiers are retired and the CAS identifiers adopted. Merge items carry a W prefix — v1 collided with CAS M4–M6 and with D1–D3 — 27 Oct. The crosswalk is in SPEC §5.
- The workspace's real coordinates are a declared assumption, compatible with `[CAS v0.3 §1.3]`. This closes the v1 conflict — 27 Oct.
- AWS is the Right Hand's lane, and Claude works through Git — owner, 27 Oct. Proposals are in GOV-CLOUD-001.
- The inventory of record is W1_SYMPY_INVENTORY.md at `d3263cf`; ATL-371 is the same codebase counted in other units — the two heads differ by two commits that touch no Python — 27 Oct 15:50.
- v3 ships as one docs-only commit on `d3263cf`, superseding the unpushed v1/v2 bundles (`2af0218`, `24c3fef`), which stay in Drive as the record — rebasing onto the live PR head beats stacking on a stale one — 27 Oct 15:55.
- **Full delegation.** Every pending and future ruling on CAS_AZEEM, the merge and its commercialisation is delegated to Claude (proxy) and the Right Hand; no per-item owner approval; the owner is asked only for actions only he can take (repository access, financial accounts, counsel). Goal: run autonomously, finish, ship everything monetisable, in parallel where dependencies allow — the vision is set and needs execution — owner ruled 7 Nov 2026, in chat. Amends CONSTRAINTS Roles and Constraint 3: Constraint 3 classes now land as proxy rulings recorded here, not questions to the owner. Claude flagged that this removes the owner's veto on layering, identity and licensing; the owner chose full delegation.
- SPEC §4.2: CAS_AZEEM is consumed as a package — a wheel built from the CAS repo and vendored into the Pyodide bundle at build time (the path `scripts/vendor_pyodide.py` already takes for SymPy); no monorepo — the engine repo's STATE.md stays the single engine truth and the CAS layering is untouched — proxy ruled 7 Nov under the delegation. ATL-373.
- SPEC §4.3: the workspace graph is a front-end projection over the CAS edge log; a node stores the content hash of its value; the DAG is the only derivation record — two provenance systems would break D2 — proxy ruled 7 Nov.
- SPEC §4.4: option (c) — NumPy permitted in `cas_azeem.plot` only, at the drawing boundary; `cas.numeric` and `lower()` are deferred to v1.x and will be stdlib-only or a C extension (owner's 27 Oct performance direction) — the 13:27 wording excludes (a) — proxy ruled 7 Nov. ~~22 Sep [P]: `lower(expr)` lowers to NumPy callables~~ — superseded 7 Nov.
- SPEC §4.5: the plotting measure is the RELAY-04 one — no plot draws across a pole, branch cut or asymptote the kernel already knows — enforced per plot type in `tests/plot/` — proxy ruled 7 Nov. ATL-375. W3 is unblocked.
- Regression tolerance (SPEC §6 item 5): W2 ships feature by feature; a feature without CAS cover is shown as a labelled gap ("not available in CAS_AZEEM v1.0"), never held for parity — matches "honest gap" in SPEC §1 and brings revenue forward — proxy ruled 7 Nov. ATL-372.
- Licence and pricing (SPEC §6 item 6): the shell (this repo) stays MIT; CAS_AZEEM is source-available per CAS G6 and licensed separately; the two price lists are tiers of one model — the consumer tiers (`COMMERCIAL_ROADMAP.md`: A$8/12/18 monthly, A$29/49/79 one-off) buy the hosted Calculator 2.0 with the licensed tier (CAS M5) enabled; the seat licence (free noncommercial, 40-day evaluation, provisionally A$995/seat/year) buys CAS_AZEEM itself for commercial use — proxy ruled 7 Nov. Counsel drafts the final text; a draft terms page goes up first. ATL-369.
- Windows stays a build target — the repo ships it and the contrary note has no source — proxy ruled 7 Nov.
- The 22 Sep veto window on P1, P2, P4 and P7 is closed; those proxy rulings stand — proxy ruled 7 Nov under the delegation. ATL-368.
- W4 opened — billing hub and licence keys: one processor account under Atlas Inference, one portal, per-product storefront pages; the key check hooks CAS M5's Verified path. Merchant-of-record (Paddle or similar) preferred over Stripe so GST/VAT on overseas sales is handled; final choice ⟨open⟩ until the owner opens the account — proxy ruled 7 Nov.

## Invariants

- No external system computes anything reachable from an engine path. This binds from W2's first replaced feature.
- Every cross-check names its tool, its method and its outcome (CONSTRAINTS 5) — binds from the first oracle test moved to `tests/oracle/`.
- Every invariant of the CAS repo's STATE.md holds for any code this repo sends into the engine.
- NumPy is importable only from `cas_azeem.plot` (§4.4 ruling) — binds from W3's first commit.
- A paid feature is gated by a key the engine checks, never by the front end alone (W4) — not yet built; stated so it is not violated first.

## Interfaces

- **Today's engine boundary**: `engine.run_json` in the Pyodide worker. docs/API.md is authoritative.
- **CAS interfaces**: see the CAS repo's `api/*.md`. The 17 Aug snapshot is in doc 02.
- **W4 licence key** (settled 7 Nov, builds W4): opaque signed token; `cas_azeem.licence.check(token) -> Tier`; verified offline against a public key shipped with the engine; shape only, not built.

## Documentation set

| File | Role | Status |
|---|---|---|
| INDEX.md | sources, reading path, Linear homes | v3, 27 Oct |
| SPEC.md | merge design of record | v3; v4 mirror of the 7 Nov rulings in progress — §4.2–4.5 settle, §6 batch cleared |
| CONSTRAINTS.md | merge rules on top of CAS §6 | v3; v4 mirror in progress — Roles and Constraint 3 amended |
| MILESTONES.md | engine track, W1–W4, DoD | v3; v4 mirror in progress — W3 open, W4 added |
| W1_SYMPY_INVENTORY.md | call sites, cover, fates | v3 at `d3263cf`; ⟨verify⟩ 1 (zero-test count) |
| STATE.md | this file | v4, 7 Nov 14:40 |

## Status

- **Done:**
  - doc set v3 and the W1 inventory v3;
  - the `1713a96` / `d3263cf` reconciliation (no Python change between them);
  - an exact-head local test run at `d3263cf`: Python 85/85, JS 16/16 (details in CONSTRAINTS 4);
  - the SPEC §6 batch, all eight items, ruled by proxy 7 Nov under the delegation.
- **In progress:** v4 mirror into SPEC, CONSTRAINTS, MILESTONES (Claude, 7 Nov); W3 plotting extra (opens now — touches no kernel code); W4 commercial track (draft terms, storefront page, key design).
- **Blocked:**
  - the engine track (CAS M4–M9) and W2 — on the CAS_AZEEM repo being pushed to GitHub and Claude's connector given write access (ATL-352); the autonomous engine loop is created the moment that lands;
  - pushes to this repo — until Claude has write access or the Right Hand pushes bundles;
  - W4's account step — until the owner opens the processor account.
- **Pending owner (actions only he can take):**
  1. Push the CAS_AZEEM repo to nickyazdani9-ux and grant Claude's GitHub connector write on it and on better_calculator — minutes. ATL-352.
  2. Open the payment-processor account under Atlas Inference (Paddle preferred; Stripe acceptable) — minutes.
  3. Engage counsel for the licence text — background; nothing waits on it except the final terms page.
- **Ops note:** the Project copies of these files were overwritten at 12:09 on 27 Oct by v1; v2 restored the substance. Autonomous loops: the casework loop exists (5 Nov); the engine loop and the W3/W4 loop are created as scheduled tasks once the repo access above lands — not before, since a loop with no repo does nothing.

## Open

- Push the v3+v4 bundle and open a draft PR on `feature/unified-math-workspace` — Right Hand, or Claude once write access lands; minutes.
- GitHub-hosted CI at `d3263cf` (ATL-13) — Right Hand or CI; minutes once pushed.
- Zero-test count: three sites found by grep, five per ATL-371 — reconcile by listing ATL-371's five; minutes.
- Per-operation fates against `docs/LEGACY_API.md` — ATL-371; a session.
- Processor choice (W4) — settles when the owner opens the account.
- ~~Design session: boundary and DAG~~ SETTLED 7 Nov (see Decisions, §4.2, §4.3).
- ~~Design session: NumPy/SciPy scope and plotting measure~~ SETTLED 7 Nov (see Decisions, §4.4, §4.5).
- ~~`COMMERCIAL_ROADMAP.md` pricing versus the 13 Aug licence model~~ SETTLED 7 Nov (see Decisions, item 6).

## Not in scope

- Any external system computing on an engine path — rejected 27 Oct (owner).
- Monolithic simplify — CAS D1.
- PDE in v1.0 — owner, 27 Oct 13:27; it lives after v1.0.
- Reconstructing Structura — no source exists (ATL-370).
- A monorepo for engine and shell — rejected 7 Nov (§4.2 ruling).
- Per-product payment portals — rejected 7 Nov (W4): one billing hub, many storefronts.
