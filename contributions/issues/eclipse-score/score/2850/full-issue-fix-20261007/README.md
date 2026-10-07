# S-CORE #2850 — native MVP fix and PR review artifacts

The issue-body OSS MVP is implemented in docs-as-code. The review packet includes the complete patch/source, 30 search and 10 heldout scenarios, task specifications, CR-001–CR-005 catalog, native coverage/gate integration, structured traces, CI integration, regression tests and measured evidence.

**Ready for local review; not yet ready to merge.** Native impact/qualification applicability and the parallel draft PR #628 need maintainer dispositions. Submitted-revision CI, Eclipse ECA and code-owner approval remain pending. No PR has been published, issue closed, or native work product accepted. [Merge gates](merge-readiness.json) keep those decisions separate from implementation/test results.

The measured source baseline is `102aad30bd373295d275722c3942b392a8eb7149`. The patch also applies cleanly to later observed main `36cdc3f7a56e9651ee51ce91fd183bf3d947dd16`; this is compatibility evidence, with no full-test result transferred to the newer tree.

| Artifact | Location |
| --- | --- |
| Full native patch | [source/native.patch](source/native.patch) |
| Proposed and original source | [current.tar.gz](source/current.tar.gz), [baseline.tar.gz](source/baseline.tar.gz), [source vector](source/source-hashes.json) |
| Issue-to-check mapping | [acceptance mapping](acceptance-mapping.md) |
| Project impact analysis | [impact analysis](impact-analysis.md), [conditional qualification ticket draft](qualification-ticket-draft.md) |
| Native PR template and title | [PR description](pr-description.md), [title](pr-title.txt) |
| Verification and applicable checks | [verification](verification.md), [check inventory](expected-checks.json) |
| Baseline native traces | [Python 3.12 index](evidence/native-runs-py312/evolution_summary.jsonl), [Python 3.14 index](evidence/native-runs-py314/evolution_summary.jsonl) |
| Reproduction and integrity | [reproduce](reproduce.md), [verifier](verify.py), [manifest](artifact-manifest.json) |

Each native baseline matches all 40 declared verdict/impact outcomes. Twenty gate failures per complete cohort are deliberately expected regressions; they are successfully detected, rather than counted as harness failures. The public cohorts include native gate-test seeds and ten snapshot-extraction cases. They do not establish real-agent quality or production incident coverage. Reference-expectation corrections, failed attempts and earlier source vectors remain in the evidence history.

Phase 2 injection sanitization, causal verification, capability tokens and adaptive rollback are explicitly post-MVP in the issue comment and remain separate work. This packet supersedes the earlier chatbot-only assessment for this implementation scope; the original evidence packet and its history are preserved.
