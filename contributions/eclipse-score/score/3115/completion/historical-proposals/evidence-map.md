# Evidence map and reproduction limits

All packet paths below are relative to this contribution folder. The outer
`artifact-manifest.json` binds retained payload bytes. Copied historical manifests
remain original records; some reference omitted payloads and are not advertised as
complete standalone bundles.

| Evidence | Location | What it establishes |
| --- | --- | --- |
| Issue scope and activity | `evidence/upstream/issue-3115*.json`, `upstream-snapshot.json` | Original request, assignees, captured status and linked activity |
| Existing decision/review | `evidence/upstream/pr-3140*.json`, `proposed-DR-010-infra.rst` | Open proposed DR and reviewers' actual concerns |
| Contribution and DR rules | `evidence/upstream/score-CONTRIBUTION.md`, `score-improvement-pr-template.md`, `process-decision-record-template.rst` | Native contribution route and captured format; not an adopted fabric policy |
| Alternative issue selection | `evidence/upstream/issue-3161.json`, `issue-2850.json`, `issue-2851.json`, `issue-process-805.json` | Adjacent scopes and why #3115 is the selected evaluation contribution |
| Eight tool sources | `evidence/candidates/index.json`, per-repository `capture.json`, `README.md`, `LICENSE` when available | Exact researched source commits, redirects, archive status and original documentation/licenses |
| Fabric identity | `evidence/fabric/source-identity.json`, `git-status.txt`, `working-tree.patch` | HEAD plus dirty/untracked state; no claim that HEAD alone describes the work |
| Source snapshot | `evidence/fabric/source-snapshot.tar.gz`, `source-files.json` | All 1,139 selected source/control/test/doc files; independent archive-member hashing |
| Historical development checks | `evidence/fabric/carried/specs/011-change-impact-and-freshness/evidence/validation/` | Complete selected raw logs/JUnit, including initial failure and later historical pass |
| Earlier development checks | `evidence/fabric/carried/specs/010-misra-quality-and-deviations/evidence/host-full-validation-20261001/` | Historical host validation, source status and command outputs |
| Native catalogue evidence | `evidence/fabric/carried/specs/001-native-process-catalog/evidence/` and `carried/docs/evidence/` | Original selected native exports/build evidence and fixture/probe results |
| Context estimates | `evidence/fabric/carried/specs/011-change-impact-and-freshness/evidence/benchmark/` | Synthetic byte estimates with null provider metrics |
| Live rendering proxies | `carried/specs/011-change-impact-and-freshness/evidence/qualification/` and `projection-qualification/` beneath `evidence/fabric/` | Copied summaries, requests/responses, usage, events, logs and subject bindings; operator scripts/private server state omitted |
| Later native/compatibility findings | Other directories beneath `evidence/fabric/carried/specs/011-change-impact-and-freshness/evidence/` | High-level original reports and failures, explicitly historical and incomplete for full replay |
| Historical-byte inventory | `evidence/fabric/historical-evidence-inventory.json` | Hashes/sizes freshly read for original 011 packets; omitted bytes do not travel here |
| Existing native implementation packets | `evidence/native-contributions.json`; records under `contributions/eclipse-score/` | Preserved in this same repository; fresh byte-integrity results, not test reruns |
| Concrete native proposal | `native/supplement.rst`, `native/supplement.patch` | Proposed addition to the captured PR file; no fabricated new native IDs |

## Snapshot boundaries

The source archive contains source, tests/fixtures, specs/plans/tasks/contracts, architecture,
locks, public skills, selected handoffs and original briefs. It excludes `.git`, caches,
virtualenvs, build tools, distribution artifacts, private server state, operator scripts
and repeated SOME/IP factory bundles. Test fixture keys, if present in checked-in test
data, remain fixtures and cannot grant production authority. Existing history and native
source/build archives stay at their original locations.

The archived fabric docs retain their original links, including workstation paths and
references to omitted history. Such links are provenance hints, not portable dependencies.
This map and the per-file manifests identify exactly which bytes are supplied.

## Verification and future execution

`verify_packet.py` checks outer hashes, safe archive membership, exact source-file closure,
carried-file hashes, candidate completeness, issue/PR identity and referenced native
packet-manifest bytes. The repository verifier independently replays registered contribution
manifests. Neither command executes copied scripts, starts services or makes model calls.

Historical validation results are not rebound to the current uncommitted snapshot.
Any future code execution must allocate a disposable workspace using the fabric storage
procedure, inspect imported hooks/configuration and select checks against the captured
baseline. The native RST patch has only an exact-base application check here; native
Sphinx/Bazel validation and maintainer acceptance remain pending.
