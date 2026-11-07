# Packaged notices and source locations

The build preserves the project's MIT notice at `LICENSE`, the installed pinned
KaTeX package's notice at `licenses/KATEX-LICENSE`, and the unmodified upstream
Pyodide 0.29.5 licence at `licenses/PYODIDE-LICENSE`.

Pyodide source: https://github.com/pyodide/pyodide/tree/05804b32e55628ad2269655f3c5a097fb4a966ee

Exact licence source: https://github.com/pyodide/pyodide/blob/05804b32e55628ad2269655f3c5a097fb4a966ee/LICENSE

The 0.29.5 tag resolved to this commit on 7 November 2026. The preserved file's
SHA256 is `1f256ecad192880510e84ad60474eab7589218784b9a50bc7ceee34c2b91f1d5`.

KaTeX source: https://github.com/KaTeX/KaTeX/tree/v0.16.25

These files are copied into the web bundle consumed by the native shells.
`--require-vendor` refuses missing or empty required notices. The Pyodide copy
is its upstream project licence, not an assertion that every bundled component
has the same licence. Wheel archives retain their original contents.

Remaining release review: inventory and verify all runtime/stdlib, wheel,
font and native-shell notices and source obligations in the actual packaged
artifacts. This patch is not complete third-party licence clearance. Native
CAS_AZEEM is not included or relicensed by this notice set.
