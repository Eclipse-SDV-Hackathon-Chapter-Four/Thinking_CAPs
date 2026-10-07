# Operator observations on the execution boundary

These are collected source/command observations, not engineering acceptance or a
replacement for a missing Flash supervisor review. No current queue controls, source
corrections, budgets or run IDs were changed to resolve these findings.

## Clippy configuration failure

The pinned native `.bazelrc` imports `quality/static_analysis/static_analysis.bazelrc`
at line 188. The launcher also passes this same file as an explicit `--bazelrc` startup
argument. The imported config defines `build:clippy --aspects=...%clippy_strict`.
Raw lint commands report both duplicate rc reads and
`aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once`.
The duplicate configuration is an operator launcher problem, not a proven Rust source
defect. Any future launcher revision should load this native configuration once and
measure it against a pinned subject. Existing lint failures remain failures; successful
builds/tests do not provide missing lint evidence. Already exhausted budgets are not
reset by this finding.

Sources: `provenance/linux_launcher.py`, `provenance/native-configs/.bazelrc`,
`provenance/native-configs/quality/static_analysis/static_analysis.bazelrc`, and
command log references in `verification-audit.json`.

## Relocation capability and source configuration reads

The registered file-tool guard allows `read_file`, `write_file`, `edit_file`, `glob`
and bounded search, but has no delete/rename capability. It also rejects native source
`.json` reads under the same suffix rule used for raw evidence. Issue #741 needs a file
relocation and native example configuration reads; this boundary was too restrictive
for that operation. Its exported patch is a comment-only boundary-probe BUILD file,
not the requested relocation and not a candidate fix to adopt. The supervisor retains
the unapplied move specification and the missing acceptance checks.

A future authorized workflow revision needs scoped relocation support and bounded
reads of native configuration files while continuing to protect credentials and
collector-owned evidence. No current source was moved by the operator to conceal this
failure or bypass the Flash-only constraint.

Sources: `provenance/tool_guard.py`, #741's exact patch, measured command logs,
and `issues/741/export/reports/supervisor.md`.

## Missing written reviews and documentation measurements

A successful supervisor stage does not establish that its required report was written.
Missing `supervisor.md` artifacts remain flagged in `verification-audit.json` and the
README table; `gaps/` preserves their actual native stage outputs. No replacement review
was synthesized. Likewise, `docs` invokes build rather than executing Rust doctests;
its success must not be reported as a passing doctest execution.

Next step: review these runtime findings and issue dispositions before authorizing any
new run or accepting a patch.
Recommended model: deepseek-flash — required for any future Fabro agent work.
