"""Seal additive review, preserve prior contribution state, then update local registry/handoff."""
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from score_sw_fabric.storage import validate_run_root

root = Path(__file__).parent
run = root.parent / 'score-rust-linux-integration-xfiuopbb'
validate_run_root(root)
validate_run_root(run)
contributions = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions')
packet = contributions / 'issues/eclipse-score/communication/1265/engineering-review' / root.name
assert not (packet/'artifact-manifest.json').exists(), 'Never overwrite a seal'


def sha(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024*1024), b''):
            value.update(chunk)
    return value.hexdigest()


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value,indent=2,sort_keys=True)+'\n')


def load(path):
    return json.loads(path.read_text())


# Discovery follow-up: the re-export is a root .rs file, not a score_com directory.
# Preserve the initial nonexistent-path observations in the audit rather than erase them.
checks = load(packet/'deterministic-review-checks.json')
candidate = load(packet/'native-verification/execution/candidate-hashes.json')
baseline = load(packet/'native-verification/execution/baseline-hashes.json')
historical = load(packet/'native-verification/historical-rust-and-copyright/execution/baseline-hashes.json')
for relative in ['score/mw/com/rust/score_com.rs', 'score/mw/com/rust/BUILD', 'score/mw/com/rust/score_com_concept/lib.rs']:
    actual = run/'candidate'/relative
    digest = sha(actual)
    assert digest == candidate[relative] == baseline[relative] == historical[relative]
    target = packet/'review-evidence/current-static-subjects'/relative
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(actual,target)
    checks['current_static_subjects'][relative] = {'sha256':digest,'unchanged_from_historical_baseline':True,'claim':'Fresh byte measurement of discovered re-export/BUILD source; no test-result promotion'}
write(packet/'deterministic-review-checks.json',checks)

# Independent supervisor precision finding: native build-action reuse is distinct from
# test-result caching; this is an editorial refinement, not a native corrective fix.
report = packet/'README.md'
text = report.read_text()
assert 'with cache use disabled in that execution' in text
report.write_text(text.replace('with cache use disabled in that execution','with cached test results disabled in that execution'))
writer = root/'write_review.py'
writer.write_text(writer.read_text().replace('with cache use disabled in that execution','with cached test results disabled in that execution'))
shutil.copy2(writer,packet/'review-evidence/write_review.py')
supervisor = packet/'review-evidence/supervisor-review.md'
supervisor.write_text(supervisor.read_text()+'''
Final draft review: the supervisor found no trace/status distortion or other blocking overclaim. It requested replacing “cache use disabled” with “cached test results disabled”, because native build actions were reused. That wording was corrected before sealing. The supervisor confirmed the preview/stable-release/library-use distinction is scoped rather than an exact-build certification assertion. The 15 requirement rows and R1–R6 preserve measured consumer results separately from static upstream gaps.
''')
review = load(packet/'engineering-review.json')
review['supervisor_draft_verdict'] = 'sound; cache wording refined before sealing; no native repair'
write(packet/'engineering-review.json',review)

before = packet/'review-evidence/contribution-before-review'
before.mkdir()
for name in ['registry.json','README.md']:
    shutil.copy2(contributions/name,before/name)
registry = load(contributions/'registry.json')
shutil.copy2(Path(__file__),packet/'review-evidence/seal_review.py')
timestamp = datetime.now(timezone.utc).isoformat()
write(packet/'review-provenance.json',{'created_at':timestamp,'authority':'User: do it you; offline engineering review','source_input_packet':'../native-verification (complete sealed input copy)','source_input_manifest_sha256':'bb7972f22c5bd69db5dc5ade910f8f5e9785890c35738ea857d57daaa691a2c8','supervisor':'/root/rust_issue_supervisor','storage_binding':str(root/'storage-selection.json'),'native_reruns':0,'source_repairs':0,'max_native_corrections':3,'native_corrections_used':3,'remaining_native_corrections':0,'human_acceptance':'pending','native_work_product_status_mutations':[],'registry_update':'Agent review complete; native measurements and submission eligibility preserved','secrets':'Private authentication and server state excluded; original retained packet exclusions preserved','portable_scope':'Complete input report/source/log packet retained; large OCI layers remain external with bound descriptors/hashes'})

validate_run_root(root)
files = {}
sizes = {}
for path in sorted(packet.rglob('*')):
    assert not path.is_symlink(), ('Unexpected symlink',path)
    if path.is_file():
        relative = path.relative_to(packet).as_posix()
        files[relative]=sha(path)
        sizes[relative]=path.stat().st_size
write(packet/'artifact-sizes.json',{'schema_version':1,'scope':'All payload files excluding this inventory and the root manifest; nested manifests included','files':sizes})
files['artifact-sizes.json']=sha(packet/'artifact-sizes.json')
write(packet/'artifact-manifest.json',{'schema_version':1,'kind':'offline_agent_engineering_review','files':files})
for relative,digest in files.items():
    assert sha(packet/relative)==digest
manifest_sha=sha(packet/'artifact-manifest.json')
assert sha(packet/'native-verification/artifact-manifest.json')=='bb7972f22c5bd69db5dc5ade910f8f5e9785890c35738ea857d57daaa691a2c8'
for relative,digest in load(packet/'native-verification/artifact-manifest.json')['files'].items():
    assert sha(packet/'native-verification'/relative)==digest

record = next(item for item in registry['issues'] if item['id']=='eclipse-score/communication#1265')
relative_packet=packet.relative_to(contributions).as_posix()
record['previous_linux_evidence_manifest']=record['evidence_manifest']
record['previous_linux_evidence_manifest_sha256']=record['evidence_manifest_sha256']
record['evidence_manifest']=relative_packet+'/artifact-manifest.json'
record['evidence_manifest_sha256']=manifest_sha
record['record']=relative_packet+'/README.md'
record['engineering_review']='agent_review_complete; retain_locked_pastey_0.2.3_recommended; authorized_human_acceptance_pending'
record['engineering_review_record']=relative_packet+'/engineering-review.json'
record['qualification_review_checklist']=relative_packet+'/qualification-checklist.md'
record['qualification_adoption']='not_established; exact_build_certificate_and_communication_adoption_missing'
record['local_status']='assessment_linux_integration_verified_agent_review_complete'
record['scope']='Documentation assessment of existing pastey0.2.3; six fresh native Linux integration cases passed on8368bfb5. Offline agent engineering review complete with retained qualification/trace findings and retention recommendation. Historical unit/doctest/copyright evidence remains separate; authorized human acceptance and qualification/adoption pending.'
assert record['submission_candidate'] is False
original=load(before/'registry.json')
assert [x for x in original['issues'] if x['id']!=record['id']]==[x for x in registry['issues'] if x['id']!=record['id']]
assert {k:v for k,v in registry.items() if k!='issues'}=={k:v for k,v in original.items() if k!='issues'}
write(contributions/'registry.json',registry)
inventory=contributions/'README.md'
old_row=next(line for line in inventory.read_text().splitlines() if '| [Communication #1265]' in line)
new_row=f'| [Communication #1265]({relative_packet}/README.md) | Assess Rust COM identifier-pasting dependency; generic Rust workflow retained | Documentation patch; six Linux integration cases passed; agent engineering review complete, retain pastey0.2.3 recommended | Issue open; exact compiler qualification/adoption and human acceptance pending; historical evidence preserved |'
assert inventory.read_text().count(old_row)==1
inventory.write_text(inventory.read_text().replace(old_row,new_row))

handoff=Path('/home/jefferson/s-core_sw_fabric/docs/handoff/011-session-20261006-rust-engineering-review.md')
assert not handoff.exists()
handoff.write_text(f'''# Rust issue workflow / communication #1265 — engineering review complete

The user requested “do it you” after the Linux integration scope, authorizing the offline engineering review. That review is now complete, with independent read-only supervisor `/root/rust_issue_supervisor`. Recommendation: retain locked pastey0.2.3 as a proposed decision. The issue's four documentation criteria were reviewed. Authorized human acceptance and communication qualification/adoption remain pending; no engineering decision was synthesized.

## Verified current deliverables

- Generic workflow implemented/installed: `.agents/skills/score-rust-workflow/`; installation symlink `/home/jefferson/.codex/skills/score-rust-workflow`. Sealed Spec Kit record remains `specs/011-change-impact-and-freshness/rust-workflow/`, manifest SHA `89d006500fb6b2583f682a18c1cd801a98822801839f352e71a7af59cd5010f0`. No workflow/foundation edits in this review.
- Additive review packet: `{packet}`. Root manifest SHA `{manifest_sha}`, {len(files)} subjects. Contains a complete byte-exact copy of the 1,359-subject Linux packet and older nested evidence. Original seals remain unchanged.
- Documentation patch SHA `eb687c1a36b054315970fdbb2a4833cbb5e9470fb30eb06e67a446ca87951c19`, two Markdown paths, no production Rust/dependency/API changes.
- Selected current integration baseline `8368bfb5b182ae6642d963b58ad4bac5dabc02c3`. Earlier assessment/tests baseline `e3d126c2d7569345cf5f790310702eb00cd86b06` remains explicit.
- Carried current Linux native result: two integration targets/six cases passed, zero failure/error/skip, cached test results disabled. Fabro run `01M4889N23QQRPB5CHZB2GVF5M`, version `5e15cc141483a3a45870e62733791fe34440163d5fed8f140a998902c0beb67a`. No native rerun in review.
- Fresh read-only review checks: all1,359 input/copy subjects, six XML case records, actual unchanged macro/module/lock/BUILD/re-export bytes; current compiler driver/wrapper match the historical version-report subjects; all204 historical copyright file hashes equal current recorded baseline. These checks grant no test-result freshness promotion or acceptance.

## Findings / qualification queue

R1 exact compiler AoU scope: actual `rustc1.94.0-nightly (Ferrocene rolling)`, commit `779fbed05ae9e9fe2a04137929d99cc9b3d516fd`, builder1.3.1, x86_64-unknown-linux-gnu. Exact-build certificate/use-scope evidence is absent; do not equate the Ferrocene name with AoU discharge or categorically assert no custom certificate could exist.

R2 published valid P2/C1/Q classification and architecture need Accepted change-request/safety-plan/qualification/adoption evidence for communication. Preserve native statuses.

R3 upstream environment and one-entry-point rationale need clarification against actual environment handling and three public macro entry points (two doc-hidden aliases). R4 some linked upstream tests omit/directly miss environment, doc output, uppercase and branch observations. R5 generic compile-fail evidence can reject for the wrong reason, and measured Rust result trace remains incomplete. R6 historical204 copyright dispositions remain pending despite unchanged bytes. All15 revision1/ASILB requirements are mapped with no invented lifecycle status.

Full source/path anchors, proposed actions and the native qualification checklist are in README.md, engineering-review.json and qualification-checklist.md. Primary process pin98d1d5f... definitions/templates and public Ferrocene preview guidance are captured with retrieval hashes; neither creates accepted project instances. Tool-generator management applicability remains unresolved without native tailoring.

## Preserve on resume

Review scratch `{root}` bound to backingSSD UUID002B-CE31 and registeredext4 imageUUID11c42dee-73a3-4c2b-ab42-a0440011d9e0, device1793. Validate via score_sw_fabric.storage before access; stop on unplug/remount. Explicit contribution destination honored. Native integration scratch `{run}` has large OCI layers outside the portable packet; descriptors/hashes are retained. Credentials/private server state remain internal.

Native run's max3 fixes used3/remaining0. Prior Rust recovery's max3 also exhausted. No native repair/relaunch authorized by this completed offline review. Docker/Fabro measured stopped previously and none relaunched. First fixture-failure90-subject archive, historical1046-subject/e3 packet (33passed/2ignored and204copyright findings), auxiliary-help cache deviation and packaging-draft refusal/restoration remain preserved. No publishing/merge/issue closure/submission-count change.

Contribution registry selects the additive review seal and records agent review complete, human acceptance pending. Other issues and competition metadata remain identical. Offline contribution verifier receipt is in review scratch; its integrity result does not rerun native tests or evaluate acceptance.

Next concrete input: obtain the exact compiler779fbed05 qualification/certificate/use-scope package, Accepted component change request, adapted safety plan and communication adoption record; disposition R1/R2 under authorized native review and then plan the R3–R6 actions under actual tailoring. Review work requested this turn is complete.
''')
receipt={'packet':str(packet),'manifest_sha256':manifest_sha,'subjects':len(files),'sealed_at':timestamp,'handoff':str(handoff),'handoff_sha256':sha(handoff),'review':'complete_offline_agent_review','human_acceptance':'pending','native_reruns':0,'remaining_native_corrections':0}
write(root/'review-seal-receipt.json',receipt)
write(handoff.with_suffix('.json'),{**receipt,'baseline':'8368bfb5b182ae6642d963b58ad4bac5dabc02c3','historical_baseline':'e3d126c2d7569345cf5f790310702eb00cd86b06','supervisor':'/root/rust_issue_supervisor','corrections_used':3,'max_corrections':3,'scratch':str(root),'storage_backing_uuid':'002B-CE31','storage_image_uuid':'11c42dee-73a3-4c2b-ab42-a0440011d9e0','next_input':'exact_build_compiler_qualification_and_native_communication_adoption_evidence'})
print(json.dumps(receipt,indent=2))
