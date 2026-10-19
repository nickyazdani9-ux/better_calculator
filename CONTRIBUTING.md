# Contributing

Write a failing unit test first, make the smallest change that passes it, then add an integration test where needed. Run `npm run test:js`, `python -m pytest tests/test_*.py -q`, and `npm run catalog`. Commit updated catalog metadata. Pull requests must pass all four test operating systems; native build workflows additionally require platform toolchains and network access. Do not check in signing keys, `vendor/` binaries or generated `android/`, `ios/`, `dist/` directories.
