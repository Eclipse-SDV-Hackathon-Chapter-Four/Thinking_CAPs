# Acceptance mapping

Native criterion source:
[original #2850 body](evidence/upstream/issue-2850-original.md).
Local IDs below are the chatbot's existing product requirements, not S-CORE requirement IDs.
No native requirement/design IDs were assigned to this proposal.

| #2850 obligation | Existing chatbot artifact / local IDs | Evidence | Remaining work |
| --- | --- | --- | --- |
| Query documentation by filename and artifact ID | Source provenance, exact-ID lookup; SRC-002, RET-003 | F002/F004 verification, source archive, historical exact-ID report | Add task-scoped rule/task catalog indexing and source authorization |
| Context retrieval before agent execution | Retrieval interfaces and evidence packing; RET-001, ANS-001 | F004/F005 records and ADR-007 | Implement the prescribed AssuranceHarness interface and stable context serialization |
| Read only authorized task input and rule references | Safe normalization and containment; SEC-006, SRC-003 | F002 tests/verification | Corpus-wide search is broader than input_path; enforce task-specific allowlist before retrieval |
| No HTTP, DNS or external services in candidate | Local-only product baseline; LOC-001, LOC-005 | Constitution and historical blocked-egress report | Candidate must make no Ollama/HTTP calls, including loopback; use prebuilt authorized lexical/export data |
| Same inputs yield same context; stdlib/repo-local modules only | Lexical retrieval can supply candidates; ADR-004 | Current source and search tests | Chat generation is nondeterministic; NumPy/docutils are external dependencies. Design a stdlib-only consumption boundary; do not claim present conformance |
| CR-001 through CR-005 catalog and checks | Need relationships and snapshot diff | F004/F007 verification | Implement native consistency rules, typed impacts and evidence invalidation; chat comparison is not a gate |
| At least 20 public change scenarios | Chatbot has development/held-out answer suites | eval files in source archive and historical suite reports | Q&A cases are not gate scenarios; build native task corpus with known gate verdicts and impacted IDs |
| Outer loop, trace files, evolution summary | Snapshot/source manifests provide provenance patterns | F003/ADR-006 | Implement native distillation and trace schema; no current outer loop |
| Baseline candidate evaluated with navigable traces | Search/lookup CLI and API exist | Source, F004 docs | Evaluate adapter with native lightweight validation and trace queries |
| Lane A coverage, gate, schema and CI | Chatbot CI tests, lint, types, licenses, traceability | Current logs and copied CI configuration | Run traceability_coverage.py and traceability_gate.py in the agreed target repository; validate schema and run native CI |
| Short guidance with indexed domain docs | AGENTS.md points to CLAUDE.md, traceability and ADRs | Readable project export | Adapt guidance to native domain; current CLAUDE.md does not establish target conformance |
| Phase 2 security comment | Untrusted ingestion, citation validation, recovery, read-only model | F002/F005/F008 records | Threat-specific native tests, validation evidence verification, capability/path enforcement and assurance rollback remain open |

Measured chatbot test success supports reuse evaluation only. It does not make any
native gate, safety argument, tool qualification or engineering acceptance claim.

