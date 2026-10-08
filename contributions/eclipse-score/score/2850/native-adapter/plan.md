# Implementation and verification plan

Target: disposable native checkout of docs-as-code draft #628 at
4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9. Reference repositories remain untouched.
Scratch allocation and each measured stage use the S-CORE fabric storage guard.

1. Add the native candidate and prepared JSON rule catalog; verify native loader,
   deterministic scoped retrieval and malformed/adversarial filesystem boundaries.
2. Implement pure consistency rules and reverse graph propagation, plus reusable
   goal/support, solution/evidence and parent/child coverage checks. Preserve native
   coverage implementation, gate script, schema and dependency/tool pins.
3. Publish 30 search and 10 held-out static scenarios with independent explicit
   verdict/impact oracles. Include no confidential or historical-defect claims.
4. Add deterministic snapshot execution, schema validation, native gate execution,
   context preservation, diffs, metadata, coverage delta, full provenance and append-only
   summaries. Expose existing index-first query helper for the new trace shape.
5. Make required candidate lint/type tools fail closed. Add native Bazel tests and
   CI replay for baseline and scoped candidate. Keep agent entry guidance navigational.
6. Run pinned lint/format/type/copyright/workflow checks, native Bazel regressions,
   all scenario replays, existing fixture seeds and documentation checks. Preserve raw
   commands, exact subject hashes, stdout/stderr, timings, failures and corrected reruns.
7. Verify patch application to pristine pinned source, export complete candidate,
   baseline archive, trace evidence, native PR template and impact/requirements assessment,
   reproduction instructions and integrity manifests. Record pending human decisions.

Integration repairs: type annotations in the draft's existing harness candidates,
validator/query surface are permitted where required to pass native checks. No lint
suppressions, gate-semantic changes or dependency upgrades are allowed.
