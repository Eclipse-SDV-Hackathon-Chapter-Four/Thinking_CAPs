# Communication contribution follow-up

This packet contains reviewable fixes for #1236, #751 and #1104, the public AoU
API for #1031, and a separate Config Management integration proposal. It does
**not** establish that all four issues or all merge gates are complete.

The submission patch targets Communication
`cef680454e8586daca9f953084dca33fb3759d0c`. The original verification baseline is
`381d43dec900ab6a9076f3f30e7bfbdee019e26e`; current main is 61 commits ahead.
Config Management targets `e82ec2750d7e9a9dd18edbfe6f5a78be57c22d80`.
See [verification.md](verification.md) for measured results and their scope.

| Review input | Artifact |
| --- | --- |
| Communication patch and change summary | [communication.patch](patches/communication.patch), [communication.stat](patches/communication.stat) |
| Companion consumer patch | [config_management.patch](patches/config_management.patch), [config_management.stat](patches/config_management.stat) |
| PR titles and descriptions | [Communication draft](pr-communication.md), [Config Management draft](pr-config-management.md) |
| Acceptance, native requirement IDs, safety and dependency impacts | [acceptance.md](acceptance.md), [engineering-decisions.md](engineering-decisions.md) |
| Required checks, results and omissions | [required-checks.json](required-checks.json), [verification.md](verification.md) |
| Exact changed native files | [native-source/communication](native-source/communication), [native-source/config_management](native-source/config_management) |
| Source, tool, environment and policy bindings | [communication-subject.json](communication-subject.json), [config_management-subject.json](config_management-subject.json), [environment-binding.json](environment-binding.json), [native-policy](native-policy) |
| Complete raw execution records and generated outputs | [evidence](evidence) |
| Portable integrity verification | [artifact-manifest.json](artifact-manifest.json), [verify_packet.py](verify_packet.py) |

The historical packet under `../communication-bug-queue-20261006` is preserved.
Failed attempts, incorrect consumer overrides and superseded source bindings
remain recorded. Baseline analysis is not represented as current-main analysis.

## Reproduction and submission

Use a clean checkout at each revision above, then apply the corresponding patch
with `git apply --check` followed by `git apply`. Do not apply both the baseline
and current Communication patches. The baseline patch is retained for historical
reproduction. Standalone query and helper patches are review extracts already
included in the Communication patch; do not apply them a second time.

Run `python verify_packet.py` to verify this packet. Native build, test, formatting,
lint, analyzer and consumer commands are in [reproduce.md](reproduce.md).

Existing official evidence confirms Jefferson Nascimento’s ECA for a separate
published Communication commit; see [contributor-eligibility.json](contributor-eligibility.json).
Final authorship and strict ECA verification must bind the new native PR commits.
Use the drafts below, run required hosted CI on the final branch, and obtain
native codeowner and safety/dependency review. No identity, signature, ECA
status, reviewer approval, safety acceptance or upstream PR is fabricated here.

The full consumer safety index fails on existing placeholder/legacy safety
records after the required tooling migration. Its remaining AoU dispositions
require Config Management engineering decisions. The consumer draft therefore
remains a draft and must not be used to close #1031. Native copyright failures
and outstanding CI results are also explicit merge blockers.
