# SPEC — CAS_AZEEM × Calculator 2.0: the merge

Last updated: 2026-11-07 (v4 mirror) · §4.2–4.5 and §6 ruled in STATE.md on 7 November · §4.6 is implementation work, not a completion claim

## 0 Authority and scope

This file governs **the merge only**: how Calculator 2.0 (this repo) becomes the front end of CAS_AZEEM, and the plotting extra. It does not restate the engine.

- **Engine design of record**: *CAS: Status and Perimeter* v0.3 (13 Aug 2026). It is cited here as `[CAS v0.3 §n]`.
  - Readable copy: Drive "CAS_AZEEM — spec pack for Right Hand", doc 01, which is a verbatim extraction.
  - It holds G1–G9, decisions D1–D3, the number system, the kernel, the §6 code-generation constraints and the perimeter.
- **Engine truth**: `STATE.md` in the CAS_AZEEM repo.
  - Native source is available at https://github.com/nickyazdani9-ux/CAS_AZEEM. Its imported snapshot does not restore original Git ancestry; see IMPORT_RECEIPT_20261107.md.
  - Its 17 Aug snapshot is doc 02 (verbatim). The state after August is in doc 03.
- **Precedence**, which is the CAS rule: the newer dated text wins, and the design record outranks orientation. Where this file and the CAS sources disagree on the engine, the CAS sources win and this file is fixed.
- **Identifiers**: the CAS identifiers (G1–G9, D1–D3, M0–M9, §6.n) keep their meaning everywhere. Merge-only identifiers carry a **W** prefix (§5).
- **Exchange scope**: the 7 November delegation in STATE.md supersedes CLAUDE-NOTE-20261027-04's execution-only role. Claude and Right Hand make and record proxy decisions without per-item owner approval.

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
- **G11 — The best plotting of any CAS.** This means Matplotlib (including mplot3d) and Seaborn, through the plotting extra (owner, 27 Oct). Served by W3. The accepted measure is in §4.5; this is a target, not a claim of superiority.

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

### 4.2 Package boundary — settled 7 November — ATL-373

CAS_AZEEM is consumed as a wheel built from the separate engine repository and vendored into the Pyodide bundle at build time. No monorepo and no copied engine implementation in the shell. Keep `run_json` as the front-end boundary and replace supported operations feature by feature.

The engine repository's STATE.md remains authoritative for engine behavior. Its current installed namespace is `cas`; design references to `cas_azeem.plot` and `cas_azeem.licence` describe planned interfaces, not existing modules or an authorised mechanical rename. Native wheel packaging exists; browser vendoring and adapter acceptance are separate work.

### 4.3 Workspace graph and derivation DAG — settled 7 November

The workspace graph is a front-end projection over the native CAS edge log. A workspace node stores the content hash of its value; the CAS DAG is the sole derivation record. Preserve context and replay at the front end without inventing a second mathematical provenance log.

The provisional `edges.jsonl` / `objects.jsonl` persistence proposal remains unimplemented unless verified against the engine; this graph ruling does not implement persistence.

### 4.4 Numerical and plotting boundary — settled 7 November

Option (c) was accepted: NumPy is allowed only in the plotting extra at the drawing boundary. `cas.numeric` and `lower()` are deferred to v1.x and will be stdlib-only or a C extension. The earlier provisional NumPy-lowering proposal is superseded.

No external system computes on an engine path. External systems remain test-time oracles with recorded tool, method and outcome. Numerical simulation proposals in COMMERCIAL_ROADMAP.md do not override this boundary.

### 4.5 Plotting extra (W3) — design settled; implementation open — ATL-375

The closed plotting import list is Matplotlib, mpl_toolkits.mplot3d, Seaborn and NumPy. Floats enter only at the drawing boundary; exact kernel arithmetic remains unchanged.

Accepted measure: **no plot draws across a pole, branch cut or asymptote the kernel already knows**. Enforce this per plot type in `tests/plot/`. This does not claim detection of every unknown singularity.

W3 may proceed independently of native M4 because it touches no kernel code. Actual Pyodide package availability and browser acceptance remain to be verified; the design ruling is not deployment evidence.

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

## 6 Recorded batch rulings — 7 November 2026

Authority: STATE.md Decisions (verbatim source preserved from the Claude Project) and ATL-313 comment `484115d8-6859-4ec5-b335-3607a6eceaf4`. This mirror records settled choices; it does not add new mathematical rulings.

| Item | Recorded decision |
|---|---|
| §4.2 / ATL-373 | Separate engine wheel, vendored into the browser bundle; no monorepo. |
| §4.3 | Workspace graph projects the CAS edge log; content hashes identify values. |
| §4.4 | NumPy only in plotting; numerical lowering deferred to v1.x. |
| §4.5 / ATL-375 | Do not draw across kernel-known poles, branch cuts or asymptotes. |
| Regression tolerance / ATL-372 | Ship W2 feature by feature. Unsupported features show “not available in CAS_AZEEM v1.0”; never silently fall back to an external engine. |
| Licence / ATL-369 | Shell MIT; CAS source-available and separately licensed. Consumer and commercial seat offerings are tiers of one model. Final terms remain a release gate. |
| Windows | Retained as a build target. |
| P1/P2/P4/P7 / ATL-368 | The veto window is closed and the proxy rulings stand. Their original text is still needed for faithful native-plan application; this table does not reconstruct it. |

W4 is open: one billing hub and processor account, per-product storefronts, and an engine-side signed-token check. The STATE interface `cas_azeem.licence.check(token) -> Tier` is a design shape only. Processor activation, final terms and implementation remain unverified. The quoted prices are proposals, not validated revenue.

Structura remains outside scope; it is not reconstructed. The exact native completion-plan files remain missing under ATL-353 / Hub O15. That does not block independent parser, packaging or documentation work with available contracts.
