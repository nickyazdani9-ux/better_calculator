# Calculator 2.0

**Extensible SymPy computer algebra system** with local execution and builds for web, Android, iOS, macOS, Windows and Linux. Built from the original Calculator 2.0 PWA, preserving the tab/plugin architecture and themes.

## Current mathematical tabs

Calculator · calculus · complex analysis · differential geometry · transforms and waves · linear algebra. The expression parser is restricted; it does not execute arbitrary Python code. Calculations run locally in a Web Worker with SymPy on Pyodide/WebAssembly, including in the native shells.

## Targets and release artifacts

| Target | CPU | CI artifact | Installability |
|---|---|---|---|
| Web / PWA | All modern browser-supported architectures | `calculator2-web.zip` / GitHub Pages | Chrome/Safari install from HTTPS |
| Android | ARM64, 32-bit ARM and x86 Android devices supported by Android WebView | `calculator2-android.zip` containing debug APK, unsigned AAB | Debug APK sideloadable; AAB requires signing for stores |
| iOS/iPadOS | ARM64 real devices (via PWA); simulator ARM64 and x86_64 | `calculator2-ios-simulator-*.zip` | Simulator apps only; real-device IPA needs Apple signing |
| macOS | Apple Silicon ARM64, Intel x64 | Electron ZIPs | Unsigned previews; notarization/signing needed for frictionless install |
| Windows | x64, ARM64 | Portable Electron executables | Unsigned previews may trigger SmartScreen |
| Linux | x64, ARM64 | Electron tarballs | Extract, run on compatible desktop distribution |

**ARM support is in the native target matrix** for the desktop builds. Pyodide runs as WebAssembly in mobile WebViews; it is not compiled as a platform-specific native Python binary. Supported OS versions and WebAssembly memory limits still apply.

See [platform and signing instructions](docs/CROSS_PLATFORM.md) and [architecture](docs/ARCHITECTURE.md).

## Quick start (web)

Requirements: Python 3.13 or compatible local Python, Node.js 22+ (for packaging), and SymPy/pytest for tests.

```bash
python -m pip install 'sympy>=1.13,<2' 'pytest>=8,<10' 'pyyaml>=6,<7'
npm run test:js
python -m pytest tests/test_*.py -q
npm run vendor                # download pinned Pyodide runtime, wheel deps (requires internet)
npm run build:native          # builds fully vendored static files under dist/
python3 -m http.server 8000 --directory dist
```

Visit `http://localhost:8000/`. The local build ships its math engine, although optional KaTeX typesetting currently uses a CDN; plain-text answers remain available without it. `npm run build:web` is available without a vendored runtime for UI-only development, but native packages and CI require `build:native`.

## Native and desktop builds

```bash
npm install
npm run vendor
npm run build:native
npx cap add android && npx cap sync android      # needs Android SDK/JDK on Linux/macOS/Windows
# cd android && ./gradlew assembleDebug
npx cap add ios && npx cap sync ios              # needs macOS, Xcode 26+, Capacitor 8
# xcodebuild -project ios/App/App.xcodeproj -scheme App ...
npm run desktop:run                             # preview Electron locally
# npx electron-builder --linux --arm64 --publish never
```

Do not manually edit generated native projects without considering that `android/` and `ios/` are regenerated in CI. For customization, add versioned patch scripts or commit native sources later. Production mobile apps must use a unique `appId` and configured store signing.

## GitHub Actions

The main workflow [`.github/workflows/pipeline.yml`](.github/workflows/pipeline.yml) runs:

1. Python maths tests and JavaScript/packaging tests on Linux x64, Linux ARM64, macOS Apple Silicon and Windows x64.
2. Web build with offline Pyodide assets plus a Chromium **real CAS evaluation** integration test.
3. Android debug APK and unsigned AAB builds.
4. iOS Simulator builds on macOS ARM64 and Intel x64.
5. Desktop Electron packages on macOS x64/ARM64, Windows x64/ARM64, Linux x64/ARM64.
6. GitHub Pages deployment **only when browser-tested web build passes**, on pushes to `main`.
7. Tag-triggered (`v*`) preview GitHub Releases after all build jobs pass, collecting all artifacts.

Optional [signed Android](.github/workflows/android-signed.yml) and [signed iOS](.github/workflows/ios-signed.yml) workflows require platform signing secrets documented in `docs/CROSS_PLATFORM.md`. iOS IPA export requires a paid Apple Developer account, distribution certificate and provisioning profile; this does **not** automatically upload to TestFlight or the App Store.

**CI has been defined and statically validated locally but has not run on GitHub yet.** Actual native builds must be verified on hosted runners after pushing. There is currently no committed npm lockfile because npm registry access was unavailable in this build environment; dependency versions are directly pinned in `package.json`, but for stronger supply-chain reproducibility generate and commit `package-lock.json` on a networked machine, then switch workflow installs to `npm ci`.

### Create a hosted repository

```bash
gh auth login
gh repo create calculator-2 --public --source=. --remote=origin --push
```

Then go to **Settings → Pages → Build and deployment → Source: GitHub Actions**. GitHub may require repository settings/permissions for Pages or Actions; the workflows cannot set those on your behalf.

## Extending the maths

Create `python/plugins/my_topic.py`, register operations with `@register` from `python/engine.py`, add the module to `python/plugins.json`, run `npm run catalog` to refresh `assets/catalog.json`, add it to the shell asset list in `sw.js`, then add SymPy tests. The frontend automatically exposes its tab, operation selector and input fields.

If additional dependencies are required in Pyodide, amend `scripts/vendor_pyodide.py` roots, regenerate the vendored assets, and add dependency tests. Avoid loading untrusted third-party plugin code into the mathematical worker: plugins are Python modules that execute inside Pyodide.

## Test strategy and limitations

- Tests precede new packaging scripts and enforce file/layout, scope control, dependency resolution, math and HTTP-server behaviour.
- Python unit tests exercise real SymPy, including polar flatness and sphere curvature.
- Browser E2E (CI only) evaluates a derivative in actual Chromium + Pyodide.
- CI builds produce platform artifacts, **but the current pipeline does not yet execute automated UI tests on physical iOS/Android devices or native desktop apps**.
- Some symbolic expressions may be resource-intensive. There is no hard computation interrupt or memory budget yet.

MIT licensed; see [LICENSE](LICENSE).

## Unified mathematical workspace (engine-only preview)

A typed mathematical graph is now available through the existing JSON CAS boundary
with `{"action":"workspace"}`. It permits cross-domain chains with persistent
in-worker object references, declared coordinate systems and metrics, and
explicit probability assumptions. For example, a complex scalar field can
be differentiated as a 1-form, have its metric squared norm computed, and
then be passed into a normal-distribution expectation — without converting
intermediate results back into text.

See [unified workspace architecture](docs/UNIFIED_WORKSPACE.md) for the full
JSON protocol, a worked example, safety constraints, and limits. The original
calculator UI and all existing tab operations remain unchanged; graphical
workflow editing is deferred until the kernel contracts are established.

## Typeset working and worksheets

Enter ordinary expressions using `^` for powers and `*` for multiplication.
Press **Done** to evaluate. The result panel shows the original entered
expression as typeset mathematics, followed by the separately typeset answer.
The text copy button still copies the exact SymPy result.

Select **Use answer** to put a reusable scalar result into the expression
field for the next operation. Select **Add to worksheet** to collect multiple
calculations as a worked example; the worksheet stays available as you switch
operations and domains. **Save as PDF** opens the browser's Print / Save as
PDF dialog. This exports the worksheet if it contains steps, otherwise the
latest result. Explanatory derivation steps are not automatically generated.

The input display is produced from the same restricted expression grammar
as the evaluator; no user-supplied LaTeX or executable Python is interpreted.
