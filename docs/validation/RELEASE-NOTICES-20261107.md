# Release notice preservation — RH-SHIP-20261107-04

Baseline: `f08a4b53b62621503cc8019064c6643c633afb29`, PR13 integration branch.

The build allowlist omitted the repository MIT licence. KaTeX packaging copied
only its dist directory and omitted the package licence. The new build copies
both notices and a verbatim pinned Pyodide project licence to the shared static
bundle. Release builds fail before replacing output if these required notices
are absent or empty. Native wrappers consume this same bundle.

Synthetic build tests invoke the actual script in a disposable repository with
labelled dummy files. Before implementation all four tests failed: missing
artifact notices and three missing-notice release builds that incorrectly
succeeded. After implementation all four pass. Full local regression run:
20 JavaScript tests and 118 Python tests pass. Catalog regeneration produces no
diff. Python emits one installed pytest/anyio deprecation warning.

[Red log](release-notices-red.txt) · [Green log](release-notices-green.txt)

The source licence was retrieved from official Pyodide commit
`05804b32e55628ad2269655f3c5a097fb4a966ee`, compared with its 0.29.5 tag text,
and preserved byte for byte. Its source and SHA256 are in
[the packaged notice index](../../licenses/README.md). A probe of the pinned
CDN /full/LICENSE URL returned HTTP403; no CDN licence file or aggregate
third-party notice was inferred from it.

Still open: complete runtime/stdlib, wheel, font and native-shell notice/source
obligation audit against actual release artifacts. This change does not provide
full licence clearance, native CAS_AZEEM integration, signing, deployment or
paid validation. Browser/native packaging CI must run on the new revision.
