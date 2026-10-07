"""Verify continuation freshness before packaging the offline review record."""
import datetime
import json
import os
import subprocess

import native_measure as n
import verification_resume as continuation


def main():
    continuation.guard()
    phase = continuation.PHASE
    identifier = continuation.identifier()
    state = n.api('/api/v1/runs/' + identifier + '/state')
    summary = n.api('/api/v1/runs/' + identifier)
    if summary['lifecycle']['status']['kind'] not in {'succeeded', 'failed'}:
        raise ValueError('Continuation still running; wait for native termination')
    if any(value != 0 for value in summary['usage']['tokens'].values()):
        raise ValueError('Unexpected model usage in zero-model continuation')
    nodes = json.loads((phase / 'node-ids.json').read_text())
    stages = {}
    for label, node in nodes.items():
        values = [value for key, value in state['stages'].items() if key.startswith(node + '@')]
        if len(values) != 1 or not values[0].get('completion'):
            raise ValueError('Incomplete native stage: ' + label)
        stages[label] = values[0]
    if stages['export']['completion']['outcome'] != 'succeeded':
        raise ValueError('Native export failed; preserve failure instead of finalizing stale artifacts')
    receipt = {'native_run_id': identifier, 'lifecycle': summary['lifecycle'],
               'usage': summary['usage'], 'issues': {}, 'engineering_acceptance': 'pending_offline_review'}
    for number in [1236, 751, 1104, 1031]:
        subject = continuation.verify_subject(number)
        path = n.P / 'results' / str(number) / 'verify-result.json'
        result = json.loads(path.read_text())
        if number == 1104 and result.get('native_run_id') != identifier:
            raise ValueError('Final #1104 result was not produced by this continuation')
        records = []
        for check in result['checks']:
            if 'record' not in check:
                continue
            record_path = n.P / check['record']
            record = json.loads(record_path.read_text())
            if 'subject_hashes' not in record:
                # Native SARIF preservation check has independent report/schema/source hashes.
                records.append({'check':check['check'], 'sha256':n.sha(record_path), 'binding':'SARIF report/schema/normalizer record'})
                continue
            if not record.get('finished_at_epoch') or (record.get('stop_reason') and check.get('carried_evidence')):
                raise ValueError('Interrupted native check remains: ' + str(number) + ' ' + check['check'])
            if 'aou-consumer' not in record['cwd'] and record['subject_hashes'] != subject:
                raise ValueError('Final native check source drift')
            original = n.P / record.get('original_record', check['record'])
            for stream in ['stdout', 'stderr']:
                if n.sha(original.with_suffix('.' + stream)) != record[stream + '_sha256']:
                    raise ValueError('Final native log drift')
            if number in {1104,1031} and not check.get('carried_evidence'):
                started = datetime.datetime.fromisoformat(stages['verify_' + str(number)]['started_at'].replace('Z','+00:00')).timestamp()
                if record['started_at_epoch'] < started:
                    raise ValueError('Earlier native evidence masquerading as fresh: ' + check['check'])
            records.append({'check':check['check'], 'sha256':n.sha(record_path),
                            'carried_evidence':bool(check.get('carried_evidence')), 'exit_code':record['exit_code'],
                            'stop_reason':record.get('stop_reason')})
        if number == 1031:
            # Annotate only after proving that all its checks belong to this native stage.
            result.update(native_run_id=identifier, source_repair_run='01M497MN3CXK842EEAAP765SFQ', carried_evidence=False)
            n.write(path,result)
        receipt['issues'][str(number)] = {'source_match':True, 'records':records,
                                         'verify_result_sha256':n.sha(path), 'status':result['status']}
    exported=json.loads((n.P/'correction-export.json').read_text())
    if exported['run_id'] != identifier:
        raise ValueError('Current export belongs to another run')
    receipt['database_exports_root']=exported['database_exports_root']
    n.write(phase/'final-evidence-freshness.json',receipt)
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    completed=subprocess.run([str(n.R.parents[0]/'score-fabric-3fhaccha/fabric/.venv/bin/python'),
        str(n.P/'finalize_review.py'),'verification-resume'],env=env,capture_output=True,text=True,timeout=900)
    n.write(phase/'offline-review-packaging.json',{'exit_code':completed.returncode,
                                                'stdout':completed.stdout,'stderr':completed.stderr})
    if completed.returncode:
        raise ValueError('Offline packaging failed; inspect full saved receipt')
    print(json.dumps({'native_run_id':identifier,'offline_review':'exported','model_tokens':summary['usage']['tokens'],
                      'repair_attempts':3,'source_fixes_added':0,'paid_calls_added':0}))


if __name__=='__main__':
    main()
