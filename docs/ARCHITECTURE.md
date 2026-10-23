# Calculator 2.0 architecture

For readers new to the project, start at the [documentation index](README.md).
The [API reference](API.md) is the authoritative current workspace contract.


```
python/plugins/*.py   -- catalog exporter --> assets/catalog.json
          |                                    |
          +-- engine.py (SymPy, guarded AST)    |
                         |                      v
                         +-- worker.js <-- app.js / shared operation forms
                                        |
                         single static dist/ from scripts/build-web.mjs
                                        |
               +------------------------+------------------------+
               |                        |                        |
         GitHub Pages              Capacitor                 Electron
           / PWA             Android and iOS shells      desktop loopback HTTP
```

`node scripts/build-web.mjs` only emits explicitly allowed resources under `dist/`. It does **not** publish `.github`, repository history or test code. The optional `vendor/pyodide/` contains Pyodide 0.29.5 binaries, stdlib, SymPy and all wheel dependencies discovered transitively from the matching Pyodide lockfile. The fetcher checks the wheel SHA-256 where specified. The worker preferentially loads `vendor/pyodide/pyodide.js` before falling back to pinned CDN.

The Electron window uses `sandbox: true`, `nodeIntegration: false`, `contextIsolation: true` and a loopback-bound local HTTP server. The server serves only the `dist/` subtree. No shell/network API is exposed to mathematical plugins. Capacitor hosts the same `dist/` files in platform WebViews. Safari, Chromium and WebViews have different WASM memory/security constraints, so successful builds alone are not sufficient runtime certification.

### Unified graph extension (first iteration)

`python/workspace.py` implements a composable, typed DAG of symbolic
objects. The new `action: workspace` request is dispatched from the existing
`engine.run_json` boundary, and `src/worker.js` preloads this module into
Pyodide. Existing tab/plugin commands remain compatible.

This layer makes mathematical context (coordinates and metric), operation
contracts, and dependency edges explicit. See
[UNIFIED_WORKSPACE.md](UNIFIED_WORKSPACE.md) for the protocol and current limits.

### Add an operation

1. Write a failing `tests/test_engine.py` case for the new mathematical operation.
2. Implement an engine plugin with `register(...)` and `field(...)` metadata.
3. Register the module in `python/plugins.json` and regenerate `assets/catalog.json`.
4. Test new parser pathways and mathematical edge cases.
5. Add plugin source to `sw.js` CORE list, or refactor precache generation in a later iteration.
6. Run the unit suite and browser E2E; assess if native WebView behavioural tests are needed.

### Security, dependency and performance tradeoffs

- Pyodide is itself an interpreter, but user-entered formulae are interpreted by restricted `ast` in `engine.py`, **not** fed to arbitrary `eval`/`exec`.
- Generated Python plugin code is trusted source; it runs with full access to Pyodide virtual filesystem.
- LocalStorage holds calculation history. It is not sent to a remote backend.
- Optional KaTeX loads from jsDelivr if networked; offline falls back to text output.
- Very costly tensor expressions can monopolize the worker; add explicit cancellation/time limits before treating this as untrusted-public-input safe.
- Offline vendoring increases download/install size. It avoids initial CDN reliance for actual mathematics.
