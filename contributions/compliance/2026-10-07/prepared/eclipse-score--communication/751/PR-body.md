# Prepared draft — human review required

# Draft: Extract and audit production sources in the CodeQL nightly database

The native nightly extraction omitted the required proxy implementation. Select configured production C/C++ targets from the supplied roots' dependency closure, including implementation_deps; deduplicate and sort configured labels; trace the production build and audit the finalized source archive. The filtering regression now expects that deterministic order while retaining its external-label exclusion assertion.

Related issue: https://github.com/eclipse-score/communication/issues/751

This isolated candidate includes the previously documented common root BUILD copyright-input correction. It enables the scanner without changing copyright policy. Original candidates, model output and three-repair history remain preserved; one separately authorized deterministic expected-order correction was made, with no paid call.

## Native validation

- analysis-regressions: 0
- codeql-create: 0
- named-production-source-extracted: 0
- copyright: 1
- format: 0
- build-all: 0
- test-all: 0

Executed 502 out of 508 tests: 502 tests pass and 6 were skipped.

Cumulative patch applies to pristine native source. Exact source, tool/control, Git discovery and log bindings are preserved. Copyright failure and any other failures above remain actionable. Contributor/ECA checks, QNX and engineering acceptance remain pending. No push, PR, merge or issue closure is authorized.

The fresh CodeQL source archive has 1,658 entries versus 1,659 previously. The [explicit path projection and member hashes](../../source-archive-projected-comparison.json) identify one removed external dependency source: `score_baselibs+/score/mw/log/detail/thread_local_guard.cpp`; no candidate source members were removed, added or changed in that comparison. The cause of the external difference and complete external dependency coverage remain unproven. This is retained for offline review and does not waive missing evidence.

[Actual native generated engineering products](native-generated-products-manifest.json) are archived with every member verified; all build caches remain retained.


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)
- OpenAI Codex (version not retained)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
