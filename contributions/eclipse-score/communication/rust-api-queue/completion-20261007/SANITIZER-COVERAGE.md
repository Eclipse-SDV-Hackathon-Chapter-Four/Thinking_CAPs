# Native sanitizer scope and exclusions

The final native address/undefined-behavior/leak sanitizer run passes 509 of 517 selected targets, with eight explicit native skips. All four focused regression targets pass in this configuration. The machine-readable skip inventory is `evidence/run-metadata/asan-test-skips.json`.

Besides the seven platform skips from the ordinary Linux run, the native BUILD file disables `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` under any sanitizer. Its existing comment refers to unresolved #794 Tokio multithread leak/race findings and separate QNX #1278 applicability. The file is byte-identical to the recorded baseline. This contribution does not change that exclusion or mark the omitted test as passing. The ordinary Linux run executes that target successfully.

CHECKS.md records the final thread-sanitizer outcome and all failures/skips. Selected compiler actions are retained to assess actual instrumentation, rather than assuming that a sanitizer workflow name establishes instrumentation of every language or target. Native configuration results do not replace the adopted verification plan or tool/version/target/use qualification.

Thread Sanitizer fails: 404 targets pass, one fails and 112 are skipped out of 517 selected targets. The failing new subscription-state test reports a read/write race involving its stdout-reader String transfer through Rust standard-library mpsc. All five native retries fail. The raw reports remain in evidence/resolved-extended-tsan-full/.

Selected captured Rust actions pass sanitizer flags to the linker but contain no Rust compiler sanitizer instrumentation flag; they do not include the failing application target. The Rust documentation explains that incomplete synchronization instrumentation can produce false positives ([primary documentation](https://doc.rust-lang.org/stable/unstable-book/compiler-flags/sanitizer.html)). Incomplete Rust/standard-library instrumentation is a possible explanation, not an accepted waiver or proven root cause. No control experiment or source correction was made after this finding. The native integration macros impose a no_tsan target constraint; skipped targets are retained in the check inventory and are not counted as passing.

The nested module-graph query also fails with exit 37 because bcr.bazel.build cannot be resolved. Nested module build and dependency checks pass. These outcomes remain separate.
