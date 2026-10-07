# Rust subscription-state API continuation — issue #560

Native Fabro run `01M4927N232FTNWEFCRTJQG7PE` resumed the existing draft on Linux using only DeepSeek
Flash (`deepseek-v4-flash`), with an independent Flash supervisor stage. Native run
status: succeeded; this does not establish issue resolution
or engineering acceptance. Written supervisor present: True.

Lifetime source corrections used: 2/3; remaining: 1.
Historical correction1 and any failed new requests remain counted. Other issue budgets
were not changed. The incoming source map matched all 2186 sealed #560 subjects.
The original source baseline, incoming checkpoint, final source map, full patch,
changed native files, workflow/control hashes, events, failed results and raw Linux
logs are retained. Old reports are historical; inspect current corrections/supervisor.

Read `verification-summary.json` and `issues/560/collection-summary.json` for measured
command outcomes and whether subjects match the final patch. Native build, Rust/FFI
unit tests, existing C++ state-machine tests, existing consumer integration and actual
new callback integration are distinct coverage claims. The current expected target
inventory is in `issues/560/export/reports/check-plan.json`; unexecuted checks remain gaps.
Explicit doctest uses Bazel test; inspect the runnable Rust-example denominator.
Explicit-label query does not establish reverse-dependency completeness. The revised
launcher supports the native clang-tidy configuration for the changed C++ wrapper.

Offline engineering review remains pending, including callback ownership/disposal,
reentrancy/thread guarantees, trace and qualification obligations identified in source
and supervisor output. No issue closure, human acceptance, commit or publishing occurred.
Only the new owned Fabro and rootless Docker runtimes were stopped; proofs are exported.
Credentials/private state stayed internal, source/build work used the bound registered
Linux build image on the external SSD, and reference repositories were read-only.
No QNX execution or model fallback was admitted.
