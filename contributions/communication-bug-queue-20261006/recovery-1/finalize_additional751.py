"""Export the new isolated #751 candidate without replacing earlier evidence."""
import datetime
import json
import os
import subprocess
import tarfile

import native_measure as n
import additional751 as task


def main():
    task.guard();identifier=task.identifier();phase=task.PHASE;out=task.OUT;folder=out/'results/751'
    summary=n.api('/api/v1/runs/'+identifier);state=n.api('/api/v1/runs/'+identifier+'/state')
    if summary['lifecycle']['status']['kind'] not in {'succeeded','failed'}:
        raise ValueError('Additional attempt is still active')
    if any(value!=0 for value in summary['usage']['tokens'].values()):
        raise ValueError('Unexpected model tokens in deterministic attempt')
    nodes=json.loads((phase/'node-ids.json').read_text());stages={}
    for label,node in nodes.items():
        found=[v for k,v in state['stages'].items() if k.startswith(node+'@')]
        if len(found)!=1 or not found[0].get('completion'):
            raise ValueError('Incomplete stage: '+label)
        stages[label]=found[0]
    if stages['export']['completion']['outcome']!='succeeded':
        raise ValueError('Additional export failed; do not claim a complete review package')
    ledger=json.loads((out/'repair-ledger.json').read_text())
    if len(ledger['attempts'])!=1 or ledger['maximum_additional_fixes']!=1 or ledger['paid_calls']!=0:
        raise ValueError('Additional repair ledger differs')
    expected=json.loads((folder/'candidate-hashes.json').read_text())
    if n.hashes(task.TREE)!=expected:
        raise ValueError('New source drift')
    before=json.loads((out/'source-before.json').read_text())
    if n.hashes(n.R/'issue-751')!=before:
        raise ValueError('Original completed candidate drift')
    result=json.loads((folder/'verify-result.json').read_text())
    if result['native_run_id']!=identifier:
        raise ValueError('Additional result belongs to another run')
    fresh_after=datetime.datetime.fromisoformat(stages['verify_751']['started_at'].replace('Z','+00:00')).timestamp()
    records=[]
    for check in result['checks']:
        if 'record' not in check:
            continue
        path=n.P/check['record'];record=json.loads(path.read_text())
        if record['subject_hashes']!=expected or record['started_at_epoch']<fresh_after or not record.get('finished_at_epoch'):
            raise ValueError('Native source/freshness binding differs: '+check['check'])
        for stream in ['stdout','stderr']:
            if n.sha(path.with_suffix('.'+stream))!=record[stream+'_sha256']:
                raise ValueError('Native log drift')
        records.append({'check':check['check'],'record_sha256':n.sha(path),'exit_code':record['exit_code'],
                        'stop_reason':record.get('stop_reason'),'carried_evidence':False})
    coverage=json.loads((folder/'codeql-extraction.json').read_text())
    database=json.loads((out/'database-export.json').read_text())
    if database['source_hashes']['src.zip']!=coverage['archive_sha256']:
        raise ValueError('Database source archive coverage binding differs')
    metadata=task.ROOT/'codeql-candidate/751/codeql-database.yml'
    if n.sha(metadata)!=database['source_hashes']['codeql-database.yml']:
        raise ValueError('Native CodeQL metadata changed')
    finalised=[line for line in metadata.read_text().splitlines() if line.startswith('finalised:')]
    if finalised!=['finalised: true']:
        raise ValueError('CodeQL native database is not finalized')
    baseline=n.P/'native-source/communication-381d43dec900.tar.gz'
    if n.sha(baseline)!=json.loads((n.P/'native-source/manifest.json').read_text())['archive_sha256']:
        raise ValueError('Pristine native source drift')
    pristine=task.ROOT/'review-pristine'
    if pristine.exists():
        raise ValueError('Review preparation already exists; inspect before rerunning')
    pristine.mkdir()
    with tarfile.open(baseline) as archive:
        archive.extractall(pristine,filter='data')
    before_pristine=n.hashes(pristine)
    patch=folder/'communication-751.patch'
    command=['git','-C',str(pristine),'-c','core.hooksPath=/dev/null','apply','--check','--whitespace=error',str(patch)]
    checked=subprocess.run(command,text=True,capture_output=True,timeout=30)
    n.write(folder/'pristine-patch-check.json',{'command':command,'exit_code':checked.returncode,
        'stdout':checked.stdout,'stderr':checked.stderr,'source_archive_sha256':n.sha(baseline),
        'patch_sha256':n.sha(patch),'applied':False,'baseline_unchanged':n.hashes(pristine)==before_pristine})
    if checked.returncode or n.hashes(pristine)!=before_pristine:
        raise ValueError('Cumulative patch fails the pristine source check')
    env={**os.environ,'HOME':'/home/jefferson/.local/state/s-core/fabro/someip84-server/home',
        'FABRO_AUTH_FILE':str(n.AUTH),'FABRO_SERVER':n.SERVER,'FABRO_NO_UPGRADE_CHECK':'true'}
    dump=phase/'terminal-native-dump'
    if not dump.exists():
        completed=subprocess.run(['/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro',
            '--json','dump','--output',str(dump),identifier],env=env,capture_output=True,text=True,timeout=120)
        n.write(phase/'dump-receipt.json',{'exit_code':completed.returncode,'stdout':completed.stdout,'stderr':completed.stderr})
        if completed.returncode:
            raise ValueError('Complete native dump failed')
    n.write(phase/'terminal-native-summary.json',summary);n.write(phase/'terminal-native-state.json',state)
    totals=[line for line in (folder/'evidence/test-all.stdout').read_text().splitlines() if line.startswith('Executed ')]
    test_summary=totals[-1] if totals else 'No complete full-test summary; inspect native failure.'
    n.write(out/'offline-review-index.json',{'run_id':identifier,'source_baseline':n.C['source_commit'],
        'native_terminal_status':summary['lifecycle']['status'],'usage':summary['usage'],'verification':result,
        'native_test_summary':test_summary,'source_archive_coverage':coverage,'fresh_records':records,
        'native_database_finalised':True,'native_database_metadata_sha256':n.sha(metadata),
        'source_manifest_sha256':n.sha(folder/'candidate-hashes.json'),'patch_sha256':n.sha(patch),
        'original_round_ledger_sha256':n.sha(n.P/'native-repair-supervisor.json'),'additional_ledger':ledger,
        'paid_calls_added':0,'actual_provider_invoice':None,'budget_total_usd':10,'published':False,
        'engineering_acceptance':'pending_offline_review'})
    checks='\n'.join('- '+v['check']+': '+str(v.get('exit_code',v.get('status','unknown'))) for v in result['checks'])
    (folder/'PR-DRAFT.md').write_text('''# Draft: Extract and audit production sources in the CodeQL nightly database

The native nightly extraction omitted the required proxy implementation. Select configured production C/C++ targets from the supplied roots' dependency closure, including implementation_deps; deduplicate and sort configured labels; trace the production build and audit the finalized source archive. The filtering regression now expects that deterministic order while retaining its external-label exclusion assertion.

Related issue: https://github.com/eclipse-score/communication/issues/751

This isolated candidate includes the previously documented common root BUILD copyright-input correction. It enables the scanner without changing copyright policy. Original candidates, model output and three-repair history remain preserved; one separately authorized deterministic expected-order correction was made, with no paid call.

## Native validation

'''+checks+'\n\n'+test_summary+'\n\nCumulative patch applies to pristine native source. Exact source, tool/control, Git discovery and log bindings are preserved. Copyright failure and any other failures above remain actionable. Contributor/ECA checks, QNX and engineering acceptance remain pending. No push, PR, merge or issue closure is authorized.\n')
    (out/'REVIEW.md').write_text('# Additional #751 offline review\n\nUser explicitly authorized one extra deterministic correction. The original round remains3/3; this separate round is1/1. No paid model calls, source changes to other candidates, publishing or acceptance occurred.\n\nNative run: `'+identifier+'`. All checks are fresh for the isolated new source tree. '+test_summary+'\n\nTargeted checks: `'+result['targeted_checks']+'`; overall checks: `'+result['status']+'`. Production source archive coverage: '+str(coverage['archive_entries'])+' entries; named proxy implementation present: '+str(coverage['named_source_present'])+'. Cumulative patch applies to the pristine pinned baseline.\n\n[Patch, PR draft and full evidence](results/751/PR-DRAFT.md), [offline review index](offline-review-index.json), [source/database archive manifest](database-export.json). Earlier751 evidence remains under `../results/751/` and the original whole-queue review is [preserved](../REVIEW.md).\n\nCopyright and any remaining failures are not waived. QNX, contributor identity/ECA and offline human acceptance remain pending. Other issue obligations remain unchanged.\n')
    n.write(folder/'artifact-manifest.json',{'files':{str(p.relative_to(folder)):n.sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}})
    n.write(out/'artifact-manifest.json',{'files':{str(p.relative_to(out)):n.sha(p) for p in out.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}})
    print(json.dumps({'run_id':identifier,'targeted_checks':result['targeted_checks'],'all_checks':result['status'],
        'full_tests':test_summary,'patch_applies':True,'additional_attempts':1,'paid_calls':0,'review':str(out/'REVIEW.md')}))


if __name__=='__main__':
    main()
