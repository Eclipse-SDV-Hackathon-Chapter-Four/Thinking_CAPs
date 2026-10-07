# S-CORE and Eclipse SDV contributions

Evidence and artifacts for completed local fixes, their upstream review, and a later
Eclipse SDV Hackathon submission. Inventory captured on **2026-10-04**.

| Project / issue | Contribution | Local result | Upstream / next action |
| --- | --- | --- | --- |
| [SOME/IP #84](issues/eclipse-score/inc_someip_gateway/84/README.md) | Reject duplicate SOCom servers across minor versions | Scoped fix verified; local user approval recorded; patch and full portable evidence retained | Issue open; prepared upstream PR body; broader identifier/discovery work remains |
| [Lifecycle #704](issues/eclipse-score/lifecycle/704/README.md) | Generate three communication configurations from shared definitions | Fabro/DeepSeek Flash patch verified; 113 native cases pass; scoped local owner approval recorded | Issue open; upstream-template PR body and title prepared; upstream review/CI pending |
| [Diagnostics #16](issues/eclipse-score/inc_diagnostics/16/README.md) | Diagnostic API to OpenSOVD provider adapter | Evidence missing in this checkout | Issue open; recover implementation, baseline and original test records |
| [Communication #1265](issues/eclipse-score/communication/1265/engineering-review/score-rust-engineering-review-kohskpez/README.md) | Assess Rust COM identifier-pasting dependency; generic Rust workflow retained | Documentation patch; six Linux integration cases passed; agent engineering review complete, retain pastey0.2.3 recommended | Issue open; exact compiler qualification/adoption and human acceptance pending; historical evidence preserved |
| [Communication #1167](communication-1167/README.md) | Dedicated COM API idempotency integration test | Agent review complete; 503 full-suite tests pass, 6 skipped; 204 inherited copyright findings retained | Issue open; ECA confirmed; formal acceptance pending; push withheld |

The first two rows are completed local implementations with retained measurements.
Upstream review, merge and issue closure have their own statuses. The diagnostics row
is a recovery item and is excluded from the submission's completed-fix count.
The communication assessment was added on **2026-10-06** and is excluded from completed/accepted fix counts.
The inventory covers identifiable contributions in the inspected local factory
handoffs and this repository; add other completed work as its artifacts are recovered.

## Contents

- [registry.json](registry.json): issue identity, scope, baseline, evidence and PR status.
- `issues/<organization>/<project>/<issue>/`: readable record, upstream snapshot,
  provenance, original patches/logs/licenses and SHA-256 artifact manifest.
- [templates/issue.md](templates/issue.md): reusable record for additional issues.
- [Evidence gaps](EVIDENCE_GAPS.md): references still needing original artifacts.
- [Native fault-storage write-through packet](fault-storage-write-through/README.md):
  new local preparation, separate from the historic completed-fix inventory above;
  exported patch, native regressions and upstream PR draft, with publication pending.
- [OpenBSW transportRouter packet](openbsw-transport-router/README.md): prepared upstream
  contribution of a diagnostic gateway router module for Eclipse OpenBSW, checked against the
  OpenBSW and Eclipse Foundation contribution rules ([compliance](openbsw-transport-router/compliance.md))
  on current upstream `main`; feature issue
  [#664](https://github.com/eclipse-openbsw/openbsw/issues/664) open, pull request after the
  committers agree.
- [OpenBSW doipClient packet](openbsw-doip-client/README.md): prepared upstream contribution of
  a DoIP client transport layer, checked against the OpenBSW and Eclipse Foundation contribution
  rules ([compliance](openbsw-doip-client/compliance.md)); feature issue
  [eclipse-openbsw/openbsw#663](https://github.com/eclipse-openbsw/openbsw/issues/663) open,
  related bug reports #660–#662 filed; PR not opened yet.
- [Submission checklist](submission/README.md) and [hackathon PR draft](submission/hackathon-pr-description.md).

## Verify the evidence

From the repository root, with Python 3.10 or later:

```bash
python3 scripts/verify_contributions.py
python3 scripts/verify_contributions.py --json
```

The verifier checks every captured file, the current patches, the lifecycle bundle's original
manifest, every entry in the SOME/IP portable manifest and its 269 candidate source
hashes. It reads archives without unpacking or running their contents. A successful
check establishes artifact integrity against the recorded hashes; it does not rerun
native tests or grant engineering acceptance. Git and the manifests travel with the
bundle; no factory installation or workstation paths are needed for verification.

Lifecycle retains the earlier Codex packet alongside the approved Fabro/DeepSeek Flash
implementation and local upstream PR packet. Current registry references select the
approved Flash patch. Missing legacy envelopes and wider unmeasured checks remain explicit.

## Add or update a contribution

1. Create `issues/<organization>/<project>/<issue>/README.md` using the template.
2. Capture the actual upstream issue URL/status/date and implementation baseline.
3. Copy original patches, test commands, logs, results, relevant licenses and notices;
   keep failed attempts and known gaps. Record their source and SHA-256 hashes in
   `artifact-manifest.json` using the existing `files` mapping format.
4. Add a registry entry and a row above. Use `evidence_missing` until evidence exists,
   `implemented_locally` for measured local work, and `merged_upstream` only with the
   actual merged PR URL. Describe partial issue scope explicitly.
5. Run the verifier. Preserve original evidence bytes when adding newer records;
   refresh manifests only for intentional additions, with the reason in provenance.
6. Update PR/review/merge links and the submission draft as contributions advance.

Keep native code PRs directed to their individual upstream projects. The hackathon
PR can collect the contribution records and evidence in one submission. Organizer
destination, submission format and competition eligibility still need confirmation
against the actual competition instructions before submission.
