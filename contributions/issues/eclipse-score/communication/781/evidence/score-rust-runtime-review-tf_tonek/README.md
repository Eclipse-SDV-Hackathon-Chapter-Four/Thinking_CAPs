# Rust queue runtime review and evidence refresh

Corrected the operator launcher to load the native lint rc once and added an explicit
`doctest` operation that invokes native Bazel test. The new bound Linux workspace
preserves #781's exact exported source: all 2187 source hashes match before/after.
Fresh native doctest and Clippy commands both exited 0. Clippy's actual aspect output
is retained. The doctest target executed, but contains zero runnable examples; this
is not additional behavioral coverage. Five original ABI unit cases are carried with
verified source/log hashes. Native acceptance and remaining FFI/trace findings are pending.

The revised host guard permits only registered native JSON source files within a
16KiB operator byte ceiling. Protected evidence and general shell access remain
blocked. A hash-checked file relocation helper was implemented and exercised on
synthetic fixtures, including traversal, symlink, source-drift and whole-plan checks.
Thirteen host boundary checks passed, and its CLI dry run passed. These fixtures do
not prove native issue readiness. The helper is not yet wired/qualified in a Fabro
workflow and was not applied to #741, whose three-slot source budget is exhausted.

All old workflows, sealed packets and budgets remain unchanged. No paid model request,
new target-source correction, acceptance, commit or publication occurred. Only the new
owned rootless Docker runtime was started for verification; it is stopped with proof
retained. No Fabro server was started. Source/tool/config/storage/evidence hashes, raw
native logs, Bazel events, analyzer outputs and the runtime correction diffs are here.

The draft review separates #560's concrete FnMut mutability compile error from Python
metadata-download failures in #490/#1261. #1261's default NotSupported method does not
implement the requested discovery stream. #490's global event bus needs independent
isolation and multi-subscriber review. Missing prior supervisor artifacts remain gaps.
A host PyPI HTTP diagnostic returned 200; it is not a Bazel result or proof that the
previous failed download completed. No speculative transport workaround was applied.

| Issue | Used / max source fix attempts | Remaining | Review and disposition |
|---|---|---|---|
| #1265 | 0/0 | 0 | Assessment/report: review source/trace/qualification gaps; no automatic issue closure or acceptance. |
| #1264 | 3/3 | 0 | Assessment/report: review source/trace/qualification gaps; no automatic issue closure or acceptance. |
| #1263 | 3/3 | 0 | Written supervisor missing despite succeeded stage; retain actual output; zero correction slots remain. |
| #794 | 3/3 | 0 | Assessment/report: review source/trace/qualification gaps; no automatic issue closure or acceptance. |
| #781 | 3/3 | 0 | Fresh unchanged-source doctest and Clippy passed; carry exact-hash five-case ABI test. Field offsets, ownership/Send decisions and native trace remain review topics. |
| #782 | 3/3 | 0 | Assessment/report: review source/trace/qualification gaps; no automatic issue closure or acceptance. |
| #1062 | 3/3 | 0 | Assessment/report: review source/trace/qualification gaps; no automatic issue closure or acceptance. |
| #741 | 3/3 | 0 | Only a comment-only boundary probe was applied. Relocation helper is a proposed host capability, not an applied issue fix or validated Fabro stage. Zero correction slots remain. |
| #560 | 1/3 | 2 | Compiler E0596 at consumer.rs:724; FnMut callback parameter at721 lacks mut binding. Two correction slots remain. Callback ownership/disposal and threading need review beyond compilation. |
| #490 | 3/3 | 0 | Last validation stopped on Python metadata download. Shared process-wide event queues and draining delivery need independent isolation/multiple-subscriber review. Zero source correction slots remain. |
| #250 | 1/3 | 2 | No source patch; wildcard/backend applicability unresolved. Two slots remain; failed correction and review preserved. |
| #1261 | 1/3 | 2 | API-contract proposal only: find_all_services default returns NotSupported and no backend override is added. Last validation stopped on Python metadata download; two slots remain, backend/design prerequisite unresolved. |
| #173 | 2/3 | 1 | Dependency-strategy assessment; one slot remains; failed correction/supervisor requests retained. |

Any subsequent Fabro work must inherit these counters and use DeepSeek Flash only.
A verification-only refresh does not manufacture additional source-correction authority.
Native source engineering review is still offline; operator checks are not acceptance.

Next step: apply a Flash correction for #560 within its two remaining slots, with native
callback tests and required review, after binding a follow-up run to this reviewed scope.
Recommended model: deepseek-flash — user-required for any subsequent Fabro agents.
