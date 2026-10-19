# Security

Do not enable arbitrary Python execution from user expressions. Expression parsing intentionally uses a constrained AST. Mathematical modules in `python/plugins/` are trusted code, not an untrusted runtime plugin store. Avoid passing secrets through local history, JS bundles or workflow logs. Use repository Actions secrets for signing. Dependency updates and WebView support changes should be tested on all target platforms. Do not publish native packages as secure until real-device testing and workload timeouts have been added.
