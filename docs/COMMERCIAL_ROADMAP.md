# Calculator 2.0: commercial product hypotheses

Research date: 27 October 2026. This is a proposed roadmap, not a claim of
Wolfram feature parity, superiority, market share or validated willingness to pay.

## The first market to win

Start with people doing repeated undergraduate engineering and mathematical
physics work on a phone and laptop. The product promise to test is: **keep the
whole calculation, understand its assumptions, and pick up where you left off**.
The existing typed workspace, local execution and portable snapshots support
that direction. A broad technical-computing replacement is a much larger goal.

## What Wolfram already supplies

| Existing competitor capability | Product implication | Primary source |
| --- | --- | --- |
| Broad symbolic and numerical computation, visualisation, notebooks, cloud integration and natural-language interfaces | A nicer calculator alone is insufficient. Benchmark complete user tasks. | [Mathematica](https://www.wolfram.com/mathematica/) |
| Step-by-step solutions, practice problems, photo input in mobile apps, downloadable results and file analysis | These are established product expectations, not unique differentiators. | [Wolfram Alpha Pro plans](https://www.wolframalpha.com/pro/pricing) |
| Symbolic calculations with quantities and units | Units must have real algebraic semantics; decorating numbers with unit labels is inadequate. | [Units documentation](https://reference.wolfram.com/language/tutorial/SymbolicCalculationsWithUnits.html) |
| An AI product ecosystem, including local/cloud MCP and agent APIs | An AI chat box or generic tool endpoint is not a defensible claim of novelty. | [Wolfram product navigation](https://www.wolfram.com/mathematica/) |

## Features worth testing

These are proposals. Their proposed advantages require user studies and
head-to-head testing; we have not established that competitors lack them.

| Priority | Feature | Concrete user workflow | Acceptance gate |
| --- | --- | --- | --- |
| P0 | Reliable offline workspace | Calculate on a train, close the app, reopen the complete thread | Fresh install computes and typesets offline; relaunch restores results and assumptions; export/import parity |
| P0 | Interruptible computation | Stop a difficult integral without losing prior work | Cancel and time budget terminate the worker; last committed graph restores; no partial writes |
| P0 | Fast start and accessibility | Enter a calculation immediately with keyboard or screen reader | Measure cold-start percentiles on named low/mid/high-range Android devices; complete all workflows without a mouse |
| P1 | Checkable derivation steps | Expand a solution into justified transformations | Each supported step has rule, domain, assumptions and independent algebraic/residual checks; unproved equivalence is marked explicitly |
| P1 | Interactive simulation linked to symbolic work | Derive an ODE, vary a parameter, view trajectories and residuals | Error-controlled solver, convergence studies, event handling and explicit stiff/non-stiff support; results retain source equation and settings |
| P1 | Units and uncertainty through a calculation | Change measurements and see propagated uncertainty | Dimensional rejection tests, correlated-input support, declared linearisation/Monte Carlo method and reproducible seeds |
| P1 | Assumption and singularity inspector | See why a result changes over real/complex or positive domains | Assumptions are attached to objects; poles, branch cuts and chart restrictions are surfaced where supported |
| P1 | Open reproducibility bundle | Share an experiment that another person can rerun | Versioned graph, engine versions, inputs, outputs and tolerances; export JSON plus executable Python and typeset report |
| P2 | Notebook/code interoperability | Move between GUI calculations and Python/Jupyter | Lossless supported-subset roundtrip; unsupported constructs are reported without executing arbitrary imported code |
| P2 | Verified AI input assistant | Say a problem, review the parsed interpretation, run deterministic maths | Show interpretation before execution; constrain operations; never treat generated prose as a proof or numerical result |
| P2 | Domain workbenches | Repeated circuit, mechanics, geometry or signal-processing tasks | One complete validated workflow per workbench with reference problems and editable assumptions |
| P2 | Team review and collaboration | Review an equation change and compare dependent results | Named revisions, semantic diffs, reproducible recomputation and explicit permissions |

## Release sequence

1. Ship a clearly labelled preview with the real CAS, visible workspace, saved
   sessions, offline typesetting and downloadable platform builds. Keep physical
   device acceptance, production signing and stores as separate gates.
2. Complete computation cancellation, mobile startup measurement, and a stable
   signed update path. These are release requirements before selling reliability.
3. Build one simulation workflow and one verified derivation workflow. Publish
   reproducible tests before marketing comparative performance claims.
4. Recruit 10–15 target users for recorded task studies. Measure completion rate,
   correction rate, median time, saved-work recovery and repeat use against each
   participant's current tool. Obtain explicit consent for recordings/telemetry.
5. Run a paid pilot only after users repeatedly complete valuable work. Separate
   students, individual professionals and teams; do not infer demand from downloads.

## Commercial experiments

Proposed pricing tests, in AUD and not published offers: compare a one-time
offline edition at A$29/A$49/A$79 with an optional professional plan at
A$8/A$12/A$18 per month. Test separate team pricing only when collaboration exists.
Do not lock access to a user's saved mathematics behind an expired subscription.
Local computation, optional paid collaboration/compute and open exports are a
product-positioning hypothesis, not an established competitive advantage.

Acquisition experiments: excellent searchable worked examples, downloadable
reproducible notebooks, short task demonstrations and engineering-course pilots.
Every landing-page claim should link to a working example or benchmark. Measure
activation (a saved and reopened calculation), four-week retention, support load,
conversion, refund rate and contribution margin. No campaigns or spending are
authorised merely by this document.

## Benchmark design

Build a versioned set covering exact algebra, limits, symbolic integration,
linear algebra, transforms, chart-dependent geometry and numerical ODEs. Include
domain restrictions, singular inputs, unevaluated expressions and adversarial
syntax. Record hardware, versions, cold/warm startup, elapsed time, memory,
correctness method and failure category. A matching output string alone is not
proof of equivalence. Neither a passing narrow test set nor generated screenshots
establishes general superiority over Mathematica or Wolfram Alpha.

## Explicitly outside the current preview

General numerical simulation/PDE tooling, arbitrary-rank tensors, global chart
domains, a complete probability measure model, automatic derivation proofs,
live collaboration, cloud sync, payment integration and app-store readiness.
The recovered source is the unified CAS branch of `better_calculator`; no separate
Casasim source repository has been identified in the connected project records.
