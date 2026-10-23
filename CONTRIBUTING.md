# Contributing

Write a failing unit test first, make the smallest change that passes it, then add an integration test where needed. Run `npm run test:js`, `python -m pytest tests/test_*.py -q`, and `npm run catalog`. Commit updated catalog metadata. Pull requests must pass all four test operating systems; native build workflows additionally require platform toolchains and network access. Do not check in signing keys, `vendor/` binaries or generated `android/`, `ios/`, `dist/` directories.

## Documentation changes

Documentation is part of each feature, not something saved for the release.
See [Documentation maintenance](docs/DOCS_MAINTENANCE.md). When an operation or
parameter changes, update [API.md](docs/API.md) and add a runnable recipe when
appropriate. The new `tests/test_documentation.py` checks reference coverage,
relative links and executable recipes. Regenerate the legacy API reference with
`python3 scripts/export_legacy_docs.py` after editing tab operations.
