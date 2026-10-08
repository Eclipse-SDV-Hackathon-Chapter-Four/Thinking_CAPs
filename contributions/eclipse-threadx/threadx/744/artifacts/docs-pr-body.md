Companion documentation for eclipse-threadx/threadx#744, targeting `main` in `eclipse-threadx/rtos-docs-asciidoc`.

The `tx_thread_create` Description does not explain the corrected stack-address contract when stack checking and MISRA are both enabled. Added one paragraph describing alignment and pattern reservations within the supplied memory area, preservation of the full stack address, and passing `stack_start` directly as a pointer without a narrowing integer cast. The existing port type-width content from merged docs PR #79 is not duplicated.

Confirmed the wording against the actual `common/src/tx_thread_create.c`: stack checking reduces the usable size for pattern reservations and alignment, and both address conversions use `ALIGN_TYPE` with no MISRA-specific narrowing path. Reviewed the existing regression implementation and red/green evidence; the recorded fixed run passes all six focused tests. Those existing results support the contract and are not a new test run for this documentation change.

Validation: local documentation diff and whitespace checks passed. The candidate rendered successfully with Antora; the generated tx_thread_create page contains the added paragraph. The independent documentation review passed on this patch. Human technical and provenance review was confirmed for this patch. Upstream approval and final-head ECA checks remain pending.

AI assistance: Codex (gpt-6.1-sol) read both contribution guides, the kernel implementation and evidence, authored the documentation paragraph and this PR draft, and checked the local diff. The submitting human remains responsible for reviewing and verifying the contribution.
