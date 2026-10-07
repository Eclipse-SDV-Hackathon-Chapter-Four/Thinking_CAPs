# Native assurance harness — #2850

Implement every MVP acceptance criterion in eclipse-score/score#2850 against the
actual docs-as-code harness API pinned in draft PR #628, commit
4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9. This dependency is not merged in main.
The contribution is a patch for that draft baseline, not a patch directly for score.

Deliver a stdlib/repo-local, deterministic, read-only AssuranceHarness candidate;
CR-001–005 executable impact checks; checkable goals, V&V solutions and requirements
breakdowns; 30 public search scenarios and 10 separately evaluated held-out scenarios;
unchanged native coverage calculations, gate and evidence schema; lightweight validation;
complete per-task and per-run distilled traces; index-first queries; and mandatory
model-free Lane A CI. Preserve the three native gate-test seeds.

Each public scenario has spec.md, a JSON task oracle and before/after needs snapshots.
IDs are explicitly synthetic fixture IDs, never new approved native requirements.
Replay changes deterministically, retaining the precise diff. No model benchmark or
agent-quality claim follows from fixture replay. Consistency impacts require review;
they do not grant an assurance approval or override the fixed coverage gate.

Keep source IDs, status, links, content, provenance and license metadata intact.
Treat document content as inert untrusted data. Reject path traversal, URL paths,
symlinks, special files, malformed JSON and resource excess at the context boundary.
Do not claim that arbitrary imported Python candidates are sandboxed.

Phase 2 in the separate upstream comment is explicitly post-MVP (capability tokens,
LLM security judges, adaptive rollback); no placeholder issue IDs become requirements.
Native human requirements/design/tool-qualification applicability, ECA/DCO, code-owner
review and upstream CI remain acceptance obligations, not agent-signable artifacts.
