# Calculator 2.0 — documentation

This guide assumes you know mathematics, not this software.

**Status:** The existing calculator tabs are usable in the application. The unified mathematical workspace is an **experimental, engine-only API** on the feature branch. There is no stable public HTTP API or polished graph editor yet.

## Where to start

| Goal | Guide |
| --- | --- |
| Make a first calculation, then run a typed workflow | [Getting started](GETTING_STARTED.md) |
| Understand nodes, object types, metrics and chaining | [Mathematical concepts](CONCEPTS.md) |
| Follow real workflows in multiple subject orders | [Worked recipes](RECIPES.md) |
| Look up exact JSON commands and results | [Unified API reference](API.md) |
| See all operations in the existing tab calculator | [Legacy API reference](LEGACY_API.md) |
| Decode a rejected operation or unexpected output | [Troubleshooting](TROUBLESHOOTING.md) |
| Understand the internals | [Architecture](ARCHITECTURE.md) and [design notes](UNIFIED_WORKSPACE.md) |
| Contribute improvements to the docs | [Documentation maintenance](DOCS_MAINTENANCE.md) |

## Two interfaces, one direction

**The application today:** Select a subject tab, choose an operation, enter an expression, and calculate. See [Getting started](GETTING_STARTED.md).

**The new engine:** Define mathematical objects as nodes in a graph. Each operation receives an existing object and creates another, carrying mathematical type, coordinate context, and provenance. Use it through Python or the internal Web Worker protocol. The older tabs are **not yet backed by this graph interface**.

A legacy tab operation is not necessarily available as a graph operation. Read the [unified API](API.md) for supported graph operations and [legacy API](LEGACY_API.md) for existing tab operations.

The engine should compose operations in **any mathematically compatible order**. Complex analysis → geometry → probability is only one example, not a built-in path or restriction.

## Living documentation

These pages evolve alongside implementation. Examples are stored as executable JSON and checked in CI; operation names and fields are checked against code. The [maintenance policy](DOCS_MAINTENANCE.md) explains how new features change the docs.
