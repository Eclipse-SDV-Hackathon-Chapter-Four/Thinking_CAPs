# Prepare the later hackathon PR

Current evidence supports **two completed local contributions**: a scoped SOME/IP
registration fix and lifecycle configuration deduplication. Diagnostics #16 and
Classic Diagnostic Adapter references still need evidence recovery.

[Assembly verification](verification.json) records the 2026-10-04 integrity checks,
clean SOME/IP patch application and retained lifecycle XML counts.
The current lifecycle entry also retains the approved Fabro/DeepSeek Flash patch,
scoped owner decision and upstream-template PR title/body. Its earlier Codex evidence
remains unchanged. The latest content sync reruns integrity checks, not native tests.

- [ ] Check the competition's actual destination, required format, deadline and eligibility.
- [ ] Review [the registry](../registry.json) and the solved scope of each contribution.
- [ ] Run `python3 scripts/verify_contributions.py` from the repository root.
- [ ] Refresh upstream issue status and record actual native PR links when available.
- [ ] Attach required upstream review/CI/merge evidence as it becomes available.
- [ ] Update [the hackathon PR draft](hackathon-pr-description.md) with the final entry details.
- [ ] Include the portable archive and captured license/notice files in the submission.
- [ ] Review the final repository diff and open the PR to the confirmed destination.

Native upstream PR drafts:

- [SOME/IP prepared PR](../issues/eclipse-score/inc_someip_gateway/84/imported/pr-preparation/pr-description.md).
- [Lifecycle draft PR](../issues/eclipse-score/lifecycle/704/pr-description.md).

Retained evidence logs contain original absolute workstation paths. Those are
provenance; inspect the relative artifact layout and run the portable verifier
without recreating those paths. Native reruns require a disposable baseline checkout,
the patch and pinned tools. If rebasing changes the candidate, capture new affected
verification without overwriting the historical results.
