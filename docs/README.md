# Calculator 2.0 — documentation

This guide assumes you know mathematics, not this software.

**Status:** Both the calculator tabs and the typed **Workspace** are available in the application. Workspace supports object creation, compatible operations, provenance inspection, executable examples, automatic device storage and JSON transfer. There is no public hosted HTTP API or drag-and-drop graph editor.

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

**Workspace:** Define mathematical objects as nodes in a graph. Each operation receives an existing object and creates another, carrying mathematical type, coordinate context, and provenance. Use the visible Workspace controls, Python, or the internal Web Worker protocol. The older calculator tabs are not all backed by this graph interface.

A legacy tab operation is not necessarily available as a graph operation. Read the [unified API](API.md) for supported graph operations and [legacy API](LEGACY_API.md) for existing tab operations.

The engine should compose operations in **any mathematically compatible order**. Complex analysis → geometry → probability is only one example, not a built-in path or restriction.

## Living documentation

These pages evolve alongside implementation. Examples are stored as executable JSON and checked in CI; operation names and fields are checked against code. The [maintenance policy](DOCS_MAINTENANCE.md) explains how new features change the docs.
