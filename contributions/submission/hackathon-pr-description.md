# Record S-CORE contributions and reproducible evidence for the SDV Hackathon

This submission records two completed local S-CORE contributions with their
native patches, measurements, provenance and license notices:

| Contribution | Evidence | Review status |
| --- | --- | --- |
| [SOME/IP #84 duplicate registration fix](../issues/eclipse-score/inc_someip_gateway/84/README.md) | Verified six-file patch; GCC/Clang regressions; native unit, Linux QEMU and profiling records; complete portable archive | Local scoped approval recorded; upstream review/CI pending; broader #84 work remains |
| [Lifecycle #704 configuration deduplication](../issues/eclipse-score/lifecycle/704/README.md) | Approved Fabro/DeepSeek Flash patch; three equivalent configurations; runfile/package-path checks; 113 passing native cases; complete local upstream PR packet | Owner approval recorded for local patch/advisory responses and PR preparation; upstream review/CI pending |

`contributions/registry.json` tracks issue identity, baseline and PR status. Artifact
manifests and `scripts/verify_contributions.py` allow offline SHA-256 verification,
including the complete SOME/IP portable evidence and candidate source identities.
The native test results are retained original measurements, not new runs performed
while assembling this submission.

The factory demonstrator includes Fabro verification and targeted repair for SOME/IP.
Lifecycle includes actual native Fabro/DeepSeek Flash implementation, focused repair
and advisory review, followed by local owner approval and an upstream-template PR draft.
The earlier zero-provider-call preparation is retained separately. Two legacy raw
transport envelopes are missing; native outputs/usage remain and the corrected
transport's final guarded proof has complete records. Live B1–B5 savings, QNX and full
native impact/export closure remain unmeasured. Diagnostics #16 retains recovered
historical patches and a separate published native PR #40; it is excluded from the
completed-contribution count. CDA #543 is published as native PR #601. Both native
PRs currently fail their actual contributor's ECA check, and diagnostics needs
that author's DCO sign-offs. Jefferson confirmed Claude Opus 5.5 assistance on both.

Before submitting, add the confirmed competition entry details and actual upstream
PR statuses. Local verification, upstream acceptance and full issue closure are recorded
separately. Use [the submission checklist](README.md) to finalize this draft.

Use [the current compliance preparation](../compliance/2026-10-07/README.md) for
corrected submission patches, AI disclosures and unresolved legal/review/IP/native
gates. All unresolved registry candidate flags are false. The lifecycle notice
amendment is a new prepared revision; the original 113-case result and owner decision
remain historical. This draft's compliance correction was assisted by OpenAI Codex.
