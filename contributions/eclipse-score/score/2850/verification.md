# Verification entrypoint

[Native verification](native-adapter/verification.md) records native checks, corpus and build-backed results, failed attempts, the baseline typing comparison, raw logs and source/config hashes. [Native reproduction](native-adapter/reproduce.md) supplies the commands.

The current [license audit](integration-20261007/license-audit/README.md) passes the pinned checker for all 164 supported native files and all 15 packet scripts. The three header-only Python package files pass pinned Ruff lint/format; all 85 native Python files parse, shell syntax passes, exact comment insertion is proven, and the 191-file patch applies cleanly with nine fixed contracts preserved.

The original 185 implementation files are byte-identical to the runtime-tested patch. Six baseline files now include license comments, so the complete current tree has a new byte identity. The 274-case runtime/typing results remain bound to their original pre-header sources; runtime tests were not rerun for these comment-only edits. Current [source bindings](integration-20261007/evidence/binding-validation.json) and manifests reflect the newer tree. Direct application to main remains rejected, with fresh output retained; the initial PR base is `harness`.

The prior chatbot report remains in [history](native-adapter/evidence/history/prior-verification.md) and `evidence/checks/`. Pre-header source, patch and collector bytes are retained in the license-audit archives. No integrity check supplies upstream acceptance.
