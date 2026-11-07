# SPEC — CAS_AZEEM × Calculator 2.0: the merge

Last updated: 2026-10-27 (v3 — rebased on `d3263cf`; 13:27 rulings folded in) · Settled: §1, §3 · Open: §4.2–4.5 · Proposed: §4.6

## 0 Authority and scope

This file governs **the merge only**: how Calculator 2.0 (this repo) becomes the front end of CAS_AZEEM, and the plotting extra. It does not restate the engine.

- **Engine design of record**: *CAS: Status and Perimeter* v0.3 (13 Aug 2026). It is cited here as `[CAS v0.3 §n]`.
  - Readable copy: Drive "CAS_AZEEM — spec pack for Right Hand", doc 01, which is a verbatim extraction.
  - It holds G1–G9, decisions D1–D3, the number system, the kernel, the §6 code-generation constraints and the perimeter.
- **Engine truth**: `STATE.md` in the CAS_AZEEM repo.
  - The repo lives on Nick's machine. Its remote URL is Nick's to confirm (ATL-352).
  - Its 17 Aug snapshot is doc 02 (verbatim). The state after August is in doc 03.
- **Precedence**, which is the CAS rule: the newer dated text wins, and the design record outranks orientation. Where this file and the CAS sources disagree on the engine, the CAS sources win and this file is fixed.
- **Identifiers**: the CAS identifiers (G1–G9, D1–D3, M0–M9, §6.n) keep their meaning everywhere. Merge-only identifiers carry a **W** prefix (§5).
- **Exchange scope** (CLAUDE-NOTE-20261027-04): this spec is drafted by Claude with Nick. The Right Hand executes administration and does not edit or rule on it.

v1 of this file (27 Oct, morning) was reconstructed from memory before the sources were reachable. Its numbering is retired in §5.

## 1 Purpose

CAS_AZEEM is the engine. Its one-sentence goal, the tiebreaker for anything uncovered, is `[CAS v0.3 §1.1]`:

> A symbolic engine whose primitives match how the owner actually reasons about differentials and geometry.

Calculator 2.0 is its front end: the typed workspace and the web, mobile and desktop shells. The name was settled by owner delegation on 27 Oct: **CAS_AZEEM**, with Calculator 2.0 as its front end.

The merge removes SymPy from the calculator's engine path and replaces each feature with a CAS_AZEEM capability, or with an honest gap.

The product's north star (owner, 27 Oct 13:27) is a full ODE-solving library: any tractable ODE or PDE system, on a registration ladder built to be extended. v1.0 (CAS M4–M9) stays ODE-only; PDE takes its own milestone after v1.0.

## 2 Goals added by the merge

These continue the CAS numbering. G1–G9 are unchanged `[CAS v0.3 §1.2]`.

- **G10 — One workspace.** Calculator 2.0's front end runs on CAS_AZEEM. No external system computes anything at runtime on any engine path; SymPy and any other external checker remain as test-time cross-checks only (owner, 27 Oct; scope widened 13:27). Served by W1–W2.
- **G11 — The best plotting of any CAS.** This means Matplotlib (including mplot3d) and Seaborn, through the plotting extra (owner, 27 Oct). Served by W3. The checkable measure is ⟨open⟩, §4.5.

## 3 What carries over from the engine unchanged

Each item below is cited, not restated. Every one binds the front end wherever it touches engine values.

- **ℂ-default with an exact tower and no floats** `[CAS v0.3 §1.3, G2; §6.11]`.
  - The workspace's real coordinates are compatible with this: reality is a declared restriction through assumptions. The calculator already does this, with coordinates as `Symbol(real=True)` and other symbols general.
  - This closes v1 §7 "real coordinates vs D3" as **not a conflict**.
- **No autosimplification, and structural `==` versus a logged `equivalent()`** `[CAS v0.3 D1]`. The rewrite layer (CAS M1, shipped) supplies the invoked, logged rules.
  - Three calculator sites use `simplify(det) == 0` as a zero test (inventory, "Zero tests"). Under D1 each becomes an `equivalent()`/`check()` call that may answer Undetermined (P7, 22 Sep).
- **The external audit DAG** `[CAS v0.3 D2]`. Its authoritative object is the ordered edge log `(before_hash, after_hash, rule)` (doc 02, ruled 17 Aug).
- **Layering** `[CAS v0.3 §1.5]`: core (stdlib, hermetic, LaTeX) / numeric / plot / render.
  - The CAS layering assigned NumPy and SciPy to cas.numeric. The 27 Oct rulings restrict external systems to cross-checks. See §4.4.
- **Constraints §6.1–6.15** `[CAS v0.3 §6]` bind any code generated against CAS_AZEEM. This includes code generated from this repo.

## 4 Merge design

### 4.1 Engine boundary — what exists

Status: Shipped (calculator side), re-read 27 Oct at `d3263cf`; no Python change since `1713a96`.

The calculator already isolates its engine. `src/worker.js` runs Pyodide in a web worker and dispatches JSON through `engine.run_json`:
- legacy requests look like `{"tab", "operation", "values"}`;
- workspace requests look like `{"action": "workspace", "command"}`.

Input goes through a guarded `ast` walker, with no `eval` or `exec`. The authoritative contract for today's engine is docs/API.md. The typed graph is described in docs/UNIFIED_WORKSPACE.md.

### 4.2 Boundary shape ⟨open⟩ — Constraint 3 class (layering) — ATL-373

The CAS_AZEEM core is stdlib-only, so it runs in the same Pyodide worker with no `loadPackage`. The candidate, not ruled, is to keep `run_json` and swap what sits behind it, feature by feature, in W1's order.

How the calculator consumes CAS_AZEEM is still to rule (doc 03 [O]). The options are a package dependency, a vendored copy or a monorepo.

### 4.3 Workspace graph versus the derivation DAG ⟨open⟩ — Constraint 3 class (identity)

The workspace keeps a typed node graph:
- each node carries its parents, operation and context;
- the graph is exported as a replayable command history (`calculator2.workspace` v1).

CAS keeps an edge log keyed by content hash. The provisional persistence is `edges.jsonl` plus `objects.jsonl`, with explicit save and load (doc 03 [P]).

The question is whether a workspace node becomes a content hash with its edges in the CAS log, or whether the graph stays a front-end projection over the log.

### 4.4 NumPy and SciPy after the oracle rulings ⟨open⟩

The 27 Oct rulings say external systems are cross-checks only. The 13:27 form is that CAS_AZEEM is the only engine that produces results, and no external system computes anything at runtime. Two earlier records assumed otherwise:
- the 13 Aug decision placed NumPy and SciPy in `cas.numeric` as an optional extra;
- the 22 Sep provisional `lower(expr)` lowers to NumPy callables (doc 03 [P]).

Options:
- (a) `cas.numeric` is outside "engine" and keeps NumPy and SciPy;
- (b) `cas.numeric` is rebuilt stdlib-only, or deferred;
- (c) NumPy is permitted in `cas.plot` only, at the drawing boundary, which is RELAY-04's reading.

Claude's reading ⟨verify⟩: the 13:27 wording tells against (a) and leaves (b) and (c) standing. That is a reading, not a ruling. This needs Nick.

The repo's `docs/COMMERCIAL_ROADMAP.md` (new at `d3263cf`) lists, at P1, an error-controlled numerical ODE solver for interactive simulation. Whatever §4.4 rules decides how that row is built.

### 4.5 Plotting extra (W3) — Proposed — ATL-375

`cas_azeem.plot` may import Matplotlib, mpl_toolkits.mplot3d, Seaborn, and NumPy (because Matplotlib requires it).
- Floats enter only at the drawing boundary, so `[CAS v0.3 §6.11]` holds.
- All of these run in Pyodide, so the same extra serves the browser builds ⟨verify⟩ (check the Pyodide 0.29.5 package list).

The proposed checkable measure for "best" (RELAY-04) is that **no plot draws across a pole, branch cut or asymptote the kernel already knows**. This needs Nick to accept it or set another measure.

### 4.6 Front-end plumbing — Proposed

**Parser.** CAS has kernel sugar but no string parser. The calculator's guarded `ast` walker is stdlib-only and is reused as the front-end parser, emitting kernel trees instead of SymPy.
- Decimal literals: Python's `ast` turns `0.1` into a lossy float. So the parser reads the literal's source text and builds `Fraction("0.1")`.
- This keeps G2 without refusing decimal input.

**Printer.** None is needed. `latex(expr)` and `_repr_latex_` are kernel interfaces (CAS M0, shipped) and are tested under §6.15.

## 5 Retired v1 identifiers (27 Oct morning)

The v1 identifiers were referenced in SUBMIT notes, Linear and email, so they are retired with a crosswalk rather than deleted.

| v1 (retired 27 Oct) | Now |
|---|---|
| ~~D1 Hermetic core~~ | CAS layering decision + §6.9, §6.10; G10 |
| ~~D2 Leibniz infinitesimals~~ | CAS G1, D3 |
| ~~D3 Exact, ℂ-first~~ | CAS G2, §1.3 |
| ~~D4 No auto-simplification~~ | CAS D1 |
| ~~D5 Provenance by construction~~ | CAS D2, G3; Verified/Undetermined = §5.10 ruling 17 Aug |
| ~~G1–G5 (workspace)~~ | CAS G1–G9 + G10, G11 |
| ~~M4 SymPy exit inventory~~ | W1 |
| ~~M5 Workspace on CAS_AZEEM~~ | W2 |
| ~~M6 plotting extra~~ (RELAY-04) | W3 |
| ~~G6 plotting~~ (RELAY-04) | G11 (G6 is CAS: source-available) |
| ~~§5.1–5.6 restated kernel~~ | `[CAS v0.3 §5]` and doc 02 |

## 6 Open for Nick (batched; Claude raises these directly, never through the exchange)

Linear IDs are where each item is filed for Nick; the ruling lands here and in STATE.md Decisions.

1. §4.2 — how the calculator consumes CAS_AZEEM (package, vendored or monorepo). ATL-373.
2. §4.3 — the workspace graph versus the DAG.
3. §4.4 — NumPy and SciPy after the oracle rulings.
4. §4.5 — the measure for "best plotting". ATL-375.
5. Regression tolerance during W2: ship with features missing, or hold until parity. ATL-372.
6. Licence and pricing. ATL-369.
   - This repo is MIT, while CAS G6 is source-available, so code already published here stays MIT.
   - The options are to keep the shell MIT and licence CAS_AZEEM separately, or to relicense future versions.
   - `docs/COMMERCIAL_ROADMAP.md` (27 Oct) proposes test prices of A$29/49/79 one-off and A$8/12/18 a month. The 13 Aug model is free noncommercial, a 40-day evaluation and a commercial seat licence (provisionally $995 per seat per year). They may describe different tiers; nothing on record says so ⟨open⟩.
   - Counsel is pending in any case.
7. Windows. This repo ships Windows targets (docs/CROSS_PLATFORM.md; `d3263cf` adds Windows previews). A note from memory said no Windows. Confirm which is intended.
8. The veto window on the 22 Sep proxy rulings P1, P2, P4 and P7 (doc 03 §3). ATL-368. It closes at first use, which is CAS M4.

Structura has no record anywhere (doc 03; ATL-370). It is not reconstructed.
