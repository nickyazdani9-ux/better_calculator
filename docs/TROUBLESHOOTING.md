# Troubleshooting

The API rejects operations when it lacks enough mathematical information; it does not silently guess a metric, chart or probability measure.

| Symptom | Cause | What to do |
| --- | --- | --- |
| `Unknown node` | Referenced node ID does not exist | Use `graph` to inspect existing IDs and create dependencies first |
| `does not accept` | Source node has a type the operation cannot accept | Query `operations`; review [type contracts](API.md#operations) |
| `requires a metric` | Norm/index map needs a metric | Provide an explicit symmetric, nondegenerate, real metric |
| `Incompatible coordinate systems` | Objects belong to different charts | Perform an explicit `change_coordinates` first |
| `Undeclared coordinate assumptions conflict` | Generic symbol named `x` is not the real chart coordinate `x` | Define both objects within the chart or choose distinct variables |
| `singular Jacobian` | Mapping has zero symbolic Jacobian determinant | Provide a locally invertible change of coordinates |
| `Contraction needs one upper and one lower index` | Two upper or two lower index slots | Use a mixed-index tensor |
| Normal distribution error | Missing `independent:true` or invalid/nonpositive standard deviation | Supply the independence assumption and valid `normals` object |
| `Unsupported expression` | Expression parser rejects unsupported syntax | Use explicit multiplication and approved functions; no arbitrary Python |
| Missing graph after refresh | Browser storage unavailable, removed, reset or snapshot rejected | Save explicit `export` files; inspect browser-local storage |
| Long-running computation | SymPy may spend considerable time on symbolic operations | Reduce complexity; there is no hard per-request time budget yet |

## Expression input rules

Use `2*x` rather than `2x`, and `x^2` or `x**2` for powers. Complex `I`, constants `pi`, `E`, `oo` and common functions such as `sqrt`, `sin`, `cos`, `exp`, `log`, `conjugate`, `re`, and `im` are supported. Matrices use `[[1,2],[3,4]]` and vector component lists use `[x,y]`.

The parser is deliberately restricted. You cannot execute Python statements, arbitrary functions, attributes, index expressions, imports or user-authored LaTeX.

## Current limits

- Expression length ≤500 characters and maximum ~120 parser AST nodes.
- List/matrix dimensions up to four; coordinate charts of 1–4 dimensions.
- Workspace size ≤64 nodes and batch size 1–24.
- Versioned snapshots up to ~75,000 serialized characters.
- Local coordinate mappings do not fully validate domain restrictions or global invertibility.
- The unified engine does not yet offer every mathematical operation from legacy tabs.
- No hard computation timeout; very expensive symbolic requests can monopolize the worker.

If something seems wrong, report the **smallest reproducible request**, including the exact JSON, returned error, and expected mathematical result. Follow [documentation maintenance](DOCS_MAINTENANCE.md) to turn this into a regression test.
