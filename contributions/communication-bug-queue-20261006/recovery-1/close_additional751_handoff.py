"""Close the separately authorized attempt, preserving all earlier evidence."""
import datetime
import json
import time

import additional751 as task
import native_measure as n


def main():
    task.guard()
    out=task.OUT; folder=out/'results/751'; identifier=task.identifier()
    index=json.loads((out/'offline-review-index.json').read_text())
    products=json.loads((folder/'native-generated-products-manifest.json').read_text())
    if index['run_id']!=identifier or not products['all_members_verified']:
        raise ValueError('Incomplete offline package')
    comparison=json.loads((out/'source-archive-projected-comparison.json').read_text())
    coverage=index['source_archive_coverage']
    if comparison['new_archive_sha256']!=coverage['archive_sha256']:
        raise ValueError('Source archive comparison is stale')
    index['source_archive_comparison']={
        'record':'source-archive-projected-comparison.json',
        'sha256':n.sha(out/'source-archive-projected-comparison.json'),
        'removed':comparison['removed'],'added':comparison['added'],
        'bytes_changed':comparison['bytes_changed'],
        'candidate_sources_removed':comparison['candidate_sources_removed'],
        'causality':'unproven','complete_external_dependency_coverage':'unproven'}
    index['engineering_products_manifest_sha256']=n.sha(folder/'native-generated-products-manifest.json')
    n.write(out/'offline-review-index.json',index)
    note=('\nThe fresh CodeQL source archive has 1,658 entries versus 1,659 previously. '
          'The [explicit path projection and member hashes](source-archive-projected-comparison.json) '
          'identify one removed external dependency source: '
          '`score_baselibs+/score/mw/log/detail/thread_local_guard.cpp`; no candidate source members '
          'were removed, added or changed in that comparison. The cause of the external difference '
          'and complete external dependency coverage remain unproven. This is retained for offline '
          'review and does not waive missing evidence.\n\n'
          '[Actual native generated engineering products](results/751/native-generated-products-manifest.json) '
          'are archived with every member verified; all build caches remain retained.\n')
    with (out/'REVIEW.md').open('a') as stream:
        stream.write(note)
    with (folder/'PR-DRAFT.md').open('a') as stream:
        stream.write(note.replace('(source-archive-projected-comparison.json)',
                                  '(../../source-archive-projected-comparison.json)').replace(
                                  '(results/751/native-generated-products-manifest.json)',
                                  '(native-generated-products-manifest.json)'))
    historical=n.P/'REVIEW-before-additional-751.md'
    if historical.exists():
        raise ValueError('Review close already prepared; inspect before replay')
    original=(n.P/'REVIEW.md').read_text();historical.write_text(original)
    (n.P/'REVIEW.md').write_text('# Latest additional #751 evidence\n\n'
        'The user-authorized extra deterministic attempt is finished. '
        '[Review the latest isolated #751 candidate](additional-751/REVIEW.md). '
        'The original three attempts and prior #751 failure remain preserved. '
        'The whole-queue assessment below is historical for #751; other issue obligations remain unchanged.\n\n'+original)
    stamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    failed=[r['check'] for r in index['fresh_records'] if r['exit_code']!=0 or r.get('stop_reason')]
    text=f'''# Finished additional #751 handoff

Verified {stamp}. Native run `{identifier}` is terminal: `{index['native_terminal_status']['kind']}`. Export and independently checked offline package completed; engineering acceptance remains pending. [Latest review](additional-751/REVIEW.md), [full native dump](phases/additional-751/terminal-native-dump/), [review index](additional-751/offline-review-index.json).

The one authorized extra correction changed only the expected sorted-label order in `quality/static_analysis/codeql_lint_test.py`. Original source and failed 501-pass/1-fail evidence remain preserved. All additional measurements are fresh and bound to the isolated candidate's source, native Git discovery and full log hashes. {index['native_test_summary']} Targeted checks: `{index['verification']['targeted_checks']}`; overall checks: `{index['verification']['status']}`. Failed fresh checks: {', '.join(failed) or 'none'}. The cumulative patch passes pristine-baseline applicability checks.

Source root: `{task.TREE}`. Storage remains bound to `/dev/loop1`, ext4 UUID `{n.C['volume_uuid']}`, backed by the existing Lexar image; stop on disconnection without relocation. Tool/fabric/source pins, immutable authority and controls remain recorded. The kernel unchecked-filesystem warning remains unresolved; no filesystem health clearance is implied. All build caches are retained.

CodeQL's required proxy implementation is present. The fresh archive has 1,658 entries; comparison against the old 1,659-entry archive identifies one external `thread_local_guard.cpp` member absent. No candidate source member was lost. Cause and complete external dependency coverage remain unproven; see the bound comparison record. Native CodeQL database, generated engineering products, patch, changed source, logs and PR draft are exported under `additional-751/` at the explicit contribution destination.

Authority is exhausted: original ledger remains3/3, separate extra ledger1/1; hashes are bound in the review index. Added paid calls0 and model tokens0. The total cap remains$10; conservative prior audit bound$8.839842, actual provider invoice unknown, original historical reservations unchanged. No further source correction, paid call, publishing, push, PR, merge or issue closure is authorized. Human review remains offline.

Remaining queue obligations: existing copyright findings; #1236's 27 baseline-identical native buildifier warnings; #1104's external extraction script failure and unknown location paths; #1031's unmeasured real production Config Management/FMEA/LOBSTER integration; QNX, contributor identity/ECA and engineering acceptance. No failed or missing evidence is waived. Prior complete handoff: [RESUME-before-additional-751.md](RESUME-before-additional-751.md).

Next action: offline human review of the latest #751 package and remaining queue obligations. Phone dashboard: `http://192.168.13.204:8787` (last verified on the same Wi-Fi).
'''
    for name in ['RESUME.md','current-status.md','active-handoff.md']:
        (n.P/name).write_text(text)
    queue=n.P.parent;handoff=queue/'handoff.md'
    old=handoff.read_text();(queue/'handoff-before-additional-751-completion.md').write_text(old)
    handoff.write_text('# Current finished recovery handoff\n\n'
        f'Additional #751 run `{identifier}` is finished with a bound offline review package. '
        '[Read the verified handoff](recovery-1/RESUME.md). Original3/3, extra1/1, added paid calls0; '
        'human acceptance and remaining evidence gaps are pending. No publishing occurred.\n\n'
        'Historical handoff follows.\n\n'+old)
    state=json.loads((queue/'state.json').read_text())
    state.update(status='finished_review_pending',active_run_id=identifier,resume_requested=False,
        updated_at_epoch=time.time(),note='Additional #751 attempt completed and exported; offline review pending. Retry authority exhausted; no further paid call or publishing authorized.')
    for item in state['items']:
        if item['issue_number']==751:
            item.update(status='additional_attempt_exported_review_pending',stage='verification_exported',
                run_id=identifier,reason='Latest isolated candidate measured; remaining failures and external coverage gap retained for offline review')
    n.write(queue/'state.json',state)
    task.guard()
    n.write(folder/'artifact-manifest.json',{'files':{str(p.relative_to(folder)):n.sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}})
    n.write(out/'artifact-manifest.json',{'files':{str(p.relative_to(out)):n.sha(p) for p in out.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}})
    n.write(n.P/'review-manifest.json',{str(p.relative_to(n.P)):n.sha(p) for p in n.P.rglob('*') if p.is_file() and p.name!='review-manifest.json'})
    print(json.dumps({'run_id':identifier,'failed_fresh_checks':failed,'source_archive_gap':comparison['removed'],
        'products':len(products['files']),'review':str(out/'REVIEW.md'),'paid_calls_added':0,'publishing':False}))


if __name__=='__main__':
    main()
