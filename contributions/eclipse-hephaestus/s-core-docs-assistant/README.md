# Hephaestus S-CORE Docs Assistant proposal

Draft [PR #15](https://github.com/eclipse-hephaestus/hephaestus/pull/15) proposes a local documentation assistant pilot with architecture, evidence, a pinned implementation and maintainer decisions. Related [issue #11](https://github.com/eclipse-hephaestus/hephaestus/issues/11) concerns website content; the PR does not close its wider scope.

Branch: `jnsagai/hephaestus:contrib/s-core-chatbot-proposal`.
Implementation baseline: `jnsagai/s-core_bot@72c1fb2cab280e6835513b046013e5abea066c3a`.
The exact upstream base, proposal commit and candidate file hashes are in [proposal-binding.json](proposal-binding.json).

## Scope and results

The proposal describes safe ingestion, immutable snapshots, keyword/vector retrieval, local answer generation and server-owned citations. The first pilot needs a reviewed Hephaestus corpus/export profile, deterministic lookup/provenance cases and independent claim-support review. Hephaestus compatibility, adoption, licensing/dependency review and engineering acceptance remain pending.

Fresh Hugo Extended 0.163.0, inventory/navigation generation and Sphinx 8.2.3 with `-W` passed. The rendered catalog automatically lists the tooling candidate, its proposal link resolves correctly and the Sphinx index lists the proposal. All 18 pinned implementation paths exist. A detached no-commit Git merge with workflow-fabric PR #14 preserved both proposals without conflict; no combined build or authoritative branch merge was performed.

The frozen [remote verification](remote-verification.json) records the published head, three-file scope and Eclipse ECA status. No PR CI build check was attached at capture time; the site-build results are local measurements.

Existing chatbot verification was reused only after the earlier packet's integrity verifier passed and the source baseline matched. The carried full backend run recorded 1230 passed, 4 environment failures and 10 opt-in skips. A corrected setup's timer-module retry recorded 9 passed, covering all four failures; there was no clean full-suite rerun. Frontend tests recorded 76 passed. Model/release records remain historical, with blanket owner review and other original limits. No application tests, model inference or Hephaestus-corpus validation were rerun for this documentation-only PR.

## Retained artifacts

- [Proposal](proposal.md), [PR body](pr-body.md), [patch](proposal.patch) and exact three files under `candidate/`.
- Frozen issue/PR/check snapshots and [provenance](provenance.json).
- `evidence/validation/`: commands, raw logs, dependency pins, tool identity, rendered-content checks and merge check; failed environment/setup attempts remain labelled.
- `evidence/implementation/`: all 18 linked license, dependency, design and historical verification files copied verbatim from the public source baseline.
- `evidence/carried-chatbot/`: original same-source command records/logs, source manifest and verification prose. The full original artifact manifest is retained for provenance; only the enumerated subset was copied here. Its original scope is S-CORE #2850, not Hephaestus acceptance.
- `evidence/upstream/`: contribution guide, license and site-build inputs at the upstream base; the optional absent NOTICE is recorded explicitly.
- [SHA-256 manifest](artifact-manifest.json): every retained file except itself.

This is a proposal record, excluded from completed or accepted implementation counts. The original chatbot and other contribution records are preserved.

Verify the retained packet from any directory:

```bash
python /home/jefferson/Thinking_CAPs/contributions/eclipse-hephaestus/s-core-docs-assistant/verify_evidence.py
```

This checks artifact integrity and recorded bindings. It does not rerun builds or establish engineering acceptance.
