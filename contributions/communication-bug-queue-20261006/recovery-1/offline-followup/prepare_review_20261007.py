"""Prepare bound offline review evidence; make no source repairs or model calls."""
import collections
import hashlib
import json
import re
import tarfile
from pathlib import Path

import additional751 as a
import native_measure as n


def main():
    a.guard();folder=a.OUT/'results/751';follow=n.P/'offline-followup'
    target=follow/'751-copyright-subject-review.json'
    if target.exists():
        raise ValueError('Review already prepared; inspect before replay')
    manifest=json.loads((n.P/'review-manifest.json').read_text())
    subjects=['additional-751/results/751/communication-751.patch',
        'additional-751/results/751/evidence/copyright.stderr',
        'additional-751/results/751/evidence/copyright.json',
        'additional-751/results/751/candidate-hashes.json',
        'additional-751/offline-review-index.json',
        'native-source/communication-381d43dec900.tar.gz',
        'offline-followup/REVIEW-ACTIONS.md']
    for name in subjects:
        if n.sha(n.P/name)!=manifest[name]:
            raise ValueError('Review input drift: '+name)
    expected=json.loads((folder/'candidate-hashes.json').read_text())
    if n.hashes(a.TREE)!=expected:
        raise ValueError('Candidate source drift')
    record=json.loads((folder/'evidence/copyright.json').read_text())
    if record['subject_hashes']!=expected or record['exit_code']!=1:
        raise ValueError('Native copyright subject/result differs')
    log=folder/'evidence/copyright.stderr'
    if n.sha(log)!=record['stderr_sha256']:
        raise ValueError('Native diagnostic log drift')
    ansi=re.compile(r'\x1b\[[0-9;]*m');findings=[]
    prefix=str(a.TREE)+'/'
    for line in log.read_text().splitlines():
        clean=ansi.sub('',line)
        if not clean.startswith('ERROR:'):
            continue
        if prefix not in clean:
            raise ValueError('Unmapped native error; retain unknown')
        path=clean.split(prefix,1)[1].split(' ',1)[0].rstrip(',')
        if path not in expected:
            raise ValueError('Diagnostic source is outside the measured subject')
        findings.append({'path':path,'native_diagnostic':clean,
            'native_category':clean.split(' in:',1)[0].removeprefix('ERROR: '),
            'candidate_sha256':expected[path]})
    if len(findings)!=204:
        raise ValueError('Native finding count differs; no incomplete classification')
    baseline=n.P/'native-source/communication-381d43dec900.tar.gz'
    required={v['path'] for v in findings};original={}
    with tarfile.open(baseline) as archive:
        for member in archive:
            name=member.name.removeprefix('./')
            if name in required and member.isfile():
                with archive.extractfile(member) as stream:
                    original[name]=hashlib.sha256(stream.read()).hexdigest()
    for finding in findings:
        finding['pristine_sha256']=original.get(finding['path'])
        finding['byte_identical_to_pristine']=finding['candidate_sha256']==finding['pristine_sha256']
    changed=json.loads((a.OUT/'export-result.json').read_text())['source_paths']
    changed_findings=[v['path'] for v in findings if v['path'] in changed]
    counts=dict(collections.Counter(v['native_category'] for v in findings))
    n.write(target,{'native_run_id':a.identifier(),'native_record_sha256':n.sha(folder/'evidence/copyright.json'),
        'native_log_sha256':n.sha(log),'pristine_archive_sha256':n.sha(baseline),
        'candidate_manifest_sha256':n.sha(folder/'candidate-hashes.json'),
        'findings':findings,'summary':{'findings':len(findings),'categories':counts,
        'byte_identical_to_pristine':sum(v['byte_identical_to_pristine'] for v in findings),
        'findings_in_changed_paths':changed_findings},
        'limits':'Source-byte comparison only; no pristine-baseline analyzer rerun, no waiver or acceptance. Native diagnostics and source paths preserved.',
        'paid_calls':0,'source_changes':0,'engineering_acceptance':'pending_offline_review'})
    if not all(v['byte_identical_to_pristine'] for v in findings) or changed_findings:
        raise ValueError('Baseline attribution is incomplete; review the retained record')
    (follow/'REVIEW-ACTIONS-before-20261007.md').write_text((follow/'REVIEW-ACTIONS.md').read_text())
    actions=(follow/'REVIEW-ACTIONS.md').read_text().replace(
        'One separately authorized expected-order correction applied in an isolated tree; native re-verification running',
        'Extra correction completed: 502 tests passed, 6 skipped; Linux build, formatting, regressions and named-source extraction passed; review remaining coverage/validation limits').replace(
        'Pending final measured result and human review','Measured results exported; human review pending')
    actions+='\nLatest [offline reviewer checklist](REVIEW-CHECKLIST-20261007.md) supersedes the earlier #751 running status. All204 copyright diagnostic subjects match pristine source bytes; this is source comparison, not a baseline analyzer rerun or waiver.\n'
    (follow/'REVIEW-ACTIONS.md').write_text(actions)
    checklist='''# Offline reviewer checklist — 2026-10-07

This is an evidence preparation record, not engineering acceptance. The original three fixes and the separately authorized extra #751 correction are exhausted. This review made no source changes, paid calls or publication.

| Subject | Verified evidence | Review decision or missing evidence |
|---|---|---|
| #751 Linux extraction | Required proxy implementation present; database finalized; 11 regression cases pass; 502 full tests pass, 6 skipped; format/build pass; cumulative patch applies to pristine baseline | Decide whether configured production-root closure resolves the original omission; required-source audit covers one named file, not every production source |
| #751 external coverage | 1,658 source archive entries versus 1,659 previously; explicit projection identifies one absent external `thread_local_guard.cpp`; candidate source members unchanged | Cause and complete external dependency coverage are unproven. Traced-build summaries both report 1,458 processes, 443 internal and 1,015 sandbox actions; counts alone establish no cause |
| #751 query phase | Native measurement records include database creation and source audit | Full query-analysis/SARIF phase was not measured for this candidate. Other issue candidates have different source manifests and cannot supply its fresh analysis evidence |
| #751 QNX | Patch changes the Linux and QNX nightly command lines | QNX execution remains unmeasured; passing Linux checks does not supply QNX evidence |
| Copyright | 204 native findings: 96 missing, 107 wrong format, 1 duplicate. All204 diagnostic subject bytes match pristine source; none name a changed path | Scanner still exits1. No baseline analyzer rerun, exemption, policy change or accepted deviation is implied. Reviewer must resolve the overall failed check through the native process |
| Patch scope | Cumulative #751 patch includes root BUILD scanner-input correction plus CodeQL changes | Review whether the shared scanner-input correction belongs in this contribution or a separate contribution; do not silently remove it because that changes the verified subject |
| #1236 | 27 global buildifier diagnostics have pristine-identical source subjects | Global enforcement remains failed; separate lint-debt scope and authority would be needed |
| #1104 | Exact implementation extraction fails in external `try_build.bash`; supplemental analysis evidence retained | Invocation mechanism and actual lost locations remain unresolved; no external source repair has been authorized |
| #1031 | AoU, visibility and separate-consumer checks pass | Real production Config Management/profile and FMEA/LOBSTER non-duplication remain unmeasured |
| Submission | Pinned native CONTRIBUTING guide and obligations retained; user account jnascimento6p0 | Verify contributor identity/ECA and human engineering acceptance. No queue push, PR, merge or issue closure is authorized |

Reviewer decisions are intentionally unrecorded. Do not treat this checklist or Fabro success as acceptance.

Bound evidence: [latest #751 review](../additional-751/REVIEW.md), [copyright subject comparison](751-copyright-subject-review.json), [CodeQL source comparison](../additional-751/source-archive-projected-comparison.json), [native verification](../additional-751/results/751/verify-result.json), [submission obligations](../submission-obligations.md), [other issue actions](REVIEW-ACTIONS.md). Original native diagnostics, archives and prior failed evidence remain unchanged.
'''
    (follow/'REVIEW-CHECKLIST-20261007.md').write_text(checklist)
    index=json.loads((a.OUT/'offline-review-index.json').read_text())
    index['offline_review_preparation']={'date':'2026-10-07','checklist':'../offline-followup/REVIEW-CHECKLIST-20261007.md',
        'checklist_sha256':n.sha(follow/'REVIEW-CHECKLIST-20261007.md'),'copyright_subject_review_sha256':n.sha(target),
        'query_analysis_measured_for_this_candidate':False,'qnx_measured':False,'engineering_acceptance':'pending_offline_review'}
    n.write(a.OUT/'offline-review-index.json',index)
    with (a.OUT/'REVIEW.md').open('a') as stream:
        stream.write('\n[Reviewer checklist prepared 2026-10-07](../offline-followup/REVIEW-CHECKLIST-20261007.md): all204 copyright diagnostic subjects match pristine bytes and none name a changed path. The check remains failed. Full query analysis for this candidate and QNX execution are unmeasured; acceptance remains pending.\n')
    for name in ['RESUME.md','current-status.md','active-handoff.md']:
        old=(n.P/name).read_text();(follow/(name.removesuffix('.md')+'-before-review-20261007.md')).write_text(old)
        (n.P/name).write_text(old+'\nOffline review preparation completed 2026-10-07. [Reviewer checklist](offline-followup/REVIEW-CHECKLIST-20261007.md) binds remaining decisions and evidence limits. All204 copyright diagnostic subjects match pristine bytes; none name a changed path. Full query-analysis phase for the #751 candidate and QNX remain unmeasured. No new source repair, model call, native run or acceptance occurred.\n')
    (n.P/'review-manifest-before-review-20261007.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n')
    a.guard()
    n.write(a.OUT/'artifact-manifest.json',{'files':{str(p.relative_to(a.OUT)):n.sha(p) for p in a.OUT.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}})
    n.write(n.P/'review-manifest.json',{str(p.relative_to(n.P)):n.sha(p) for p in n.P.rglob('*') if p.is_file() and p.name!='review-manifest.json'})
    print(json.dumps({'copyright_findings':len(findings),'pristine_identical_subjects':len(findings),
        'findings_in_changed_paths':changed_findings,'source_repairs':0,'paid_calls':0,
        'checklist':str(follow/'REVIEW-CHECKLIST-20261007.md'),'acceptance':'pending_offline_review'}))


if __name__=='__main__':
    main()
