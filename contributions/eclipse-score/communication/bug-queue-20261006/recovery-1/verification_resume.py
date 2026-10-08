"""Zero-model verification/export continuation; source repair admission is absent."""
import hashlib
import json
import os
import signal
import shutil
import subprocess
import sys
import time

import native_measure as n
import repair3 as repair

PHASE = n.P / 'phases/verification-resume'
HELD = n.P / 'phases/repair-3/on-hold-subjects.json'
BASE_GUARD = n.guard
STOP_REQUESTED = False


def guard():
    if STOP_REQUESTED:
        raise SystemExit('Verification continuation interrupted')
    BASE_GUARD()
    for relative, expected in json.loads((PHASE / 'controls.json').read_text()).items():
        if n.sha(n.P / relative) != expected:
            raise ValueError('Continuation control drift: ' + relative)
    ledger = json.loads((n.P / 'native-repair-supervisor.json').read_text())
    if len(ledger['attempts']) != 3 or ledger['further_paid_model_calls'] != 0:
        raise ValueError('Source repair or paid-call authority changed')


def identifier():
    return (PHASE / 'native-run-id').read_text().strip()


def update(number, status, **fields):
    path = n.P.parent / 'state.json'
    state = json.loads(path.read_text())
    for item in state['items']:
        if item['issue_number'] == number:
            item.update(status=status, run_id=identifier(), recovery='recovery-1', **fields)
    state.update(status='verification_continuation', active_run_id=identifier(), updated_at_epoch=time.time())
    n.write(path, state)


def verify_subject(number):
    expected = json.loads(HELD.read_text())[str(number)]
    if n.hashes(n.R / ('issue-' + str(number))) != expected:
        raise ValueError('Held candidate drift: ' + str(number))
    if json.loads((n.P / 'results' / str(number) / 'candidate-hashes.json').read_text()) != expected:
        raise ValueError('Candidate evidence binding differs: ' + str(number))
    return expected


def preserve(number):
    source = n.P / 'results' / str(number)
    target = PHASE / 'previous-results' / str(number)
    if target.exists():
        raise ValueError('Previous results already preserved; do not replay stage')
    shutil.copytree(source, target)
    n.write(target / 'preservation.json', {
        'source': str(source), 'source_repair_run': '01M497MN3CXK842EEAAP765SFQ',
        'continued_by': identifier(), 'files': {
            str(p.relative_to(target)): n.sha(p) for p in target.rglob('*') if p.is_file()
        }, 'purpose': 'Historical records before fresh verification; not overwritten or accepted.'})


def carry(number, label):
    guard()
    tree = n.R / ('issue-' + str(number))
    subject = verify_subject(number)
    source = n.P / 'results' / str(number) / 'evidence' / (label + '.json')
    record = json.loads(source.read_text())
    discovery = hashlib.sha256(subprocess.check_output(
        ['git', '-C', str(tree), 'ls-files', '--stage', '-z'])).hexdigest()
    if record.get('subject_hashes') != subject or record.get('stop_reason'):
        raise ValueError('Incomplete or mismatched carried evidence: ' + label)
    if record.get('exit_code') != 0 or not record.get('finished_at_epoch'):
        raise ValueError('Only complete successful native checks are carried: ' + label)
    if record.get('git_file_discovery_sha256_before') != discovery or record.get('git_file_discovery_sha256_after') != discovery:
        raise ValueError('Carried Git discovery inputs differ or are unknown: ' + label)
    for stream in ['stdout', 'stderr']:
        path = source.with_suffix('.' + stream)
        if n.sha(path) != record[stream + '_sha256']:
            raise ValueError('Carried native log drift: ' + label)
    # Pinned build image, native tools and all frozen controls are rechecked by guard.
    target = PHASE / 'carried-evidence' / str(number) / (label + '.json')
    n.write(target, {**record, 'carried_evidence': True,
        'original_record': str(source.relative_to(n.P)), 'original_record_sha256': n.sha(source),
        'verified_at_epoch': time.time(), 'continued_by': identifier(),
        'binding': 'Exact candidate hashes, Git discovery inputs, log hashes and unchanged frozen tools/controls.'})
    return {'check': label, 'exit_code': 0, 'record': str(target.relative_to(n.P)), 'carried_evidence': True}


def verify_1104():
    guard(); verify_subject(1104); preserve(1104)
    update(1104, 'running', stage='remaining_verification')
    checks = [carry(1104, label) for label in [
        'analysis-regressions', 'codeql-create-nightly-projection', 'codeql-analyze', 'format']]
    # Reproduce the unresolved exact-scope extraction failure rather than conceal it.
    checks.append(repair.run_check(1104, 'codeql-create', [
        'run', '//quality/static_analysis:codeql_lint', '--', '--phase', 'create-database',
        '--database-path', str(n.R / 'codeql-candidate/1104'), '--target', '//score/mw/com/impl/...'], 600))
    for label, args in [
        ('copyright', ['run', '//:copyright.check']),
        ('build-all', ['build', '//...']),
        ('test-all', ['test', '//...', '--nocache_test_results'])]:
        guard()
        checks.append(repair.run_check(1104, label, args, 1800))
    # Revalidate actual reports and the native SARIF schema, without model calls.
    schema_python = '/home/jefferson/.pyenv/versions/3.13.13/bin/python3'
    fabric = '/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha/fabric'
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': fabric + '/src:' + str(n.P)}
    checked = subprocess.run([schema_python, str(n.P / 'check_fresh_sarif.py'), 'verification-resume'],
        env=env, capture_output=True, text=True, timeout=120)
    n.write(PHASE/'sarif-revalidation-receipt.json', {'python': schema_python,
        'exit_code': checked.returncode, 'stdout': checked.stdout, 'stderr': checked.stderr})
    if checked.returncode:
        raise ValueError('Bound native SARIF revalidation failed')
    checks.append({'check': 'fresh-native-sarif-preservation-and-schema', 'exit_code': 0,
                   'record': 'results/1104/fresh-sarif-check.json', 'fixture': False})
    guard(); verify_subject(1104)
    result = {'status': 'measured_checks_passed_review_pending' if all(v['exit_code'] == 0 for v in checks) else 'failed_or_missing_checks',
        'targeted_checks': 'failed_or_missing' if any(v['exit_code'] != 0 for v in checks if v['check'] not in {'copyright','format','build-all','test-all'}) else 'passed',
        'checks': checks, 'source_match': True, 'engineering_acceptance': 'pending_offline_review',
        'carried_evidence': 'Explicit per-check labels; full build/tests are fresh after interruption.',
        'native_run_id': identifier(), 'source_repair_run': '01M497MN3CXK842EEAAP765SFQ',
        'pending': ['Offline engineering acceptance; unknown analyzer paths remain unknown.'],
        'sarif_evidence_sha256': n.sha(n.P / 'results/1104/fresh-sarif-check.json')}
    n.write(n.P / 'results/1104/verify-result.json', result)
    logs = n.R / 'issue-1104/bazel-testlogs'
    for path in logs.rglob('*'):
        if path.is_file() and path.name in {'test.log','test.xml'}:
            destination = n.P / 'results/1104/native-testlogs' / path.relative_to(logs)
            destination.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(path, destination)
    update(1104, 'needs_review_or_fix', stage='verification_exported')
    if result['status'] != 'measured_checks_passed_review_pending':
        raise RuntimeError('Native failures retained; continue other verification and export')


def verify_1031():
    guard(); verify_subject(1031); preserve(1031)
    # Phase2 records lack the Git-discovery binding required for carried checks.
    repair.update = update
    repair.verify(1031)


def export():
    guard()
    rows = []
    for number in repair.NUMBERS:
        verify_subject(number)
        tree = n.R / ('issue-' + str(number)); folder = n.P / 'results' / str(number)
        modified = subprocess.check_output(['git','-C',str(tree),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()
        allowed = repair.ALLOWED[number]
        paths = [name for name in modified if name == 'BUILD' or name in allowed['allowed_files'] or any(name.startswith(prefix) for prefix in allowed['allowed_prefixes'])]
        if paths:
            # All source files are already intent-to-add from repair3; export does not alter candidates.
            (folder / ('communication-' + str(number) + '.patch')).write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','--binary','--',*paths]))
            for name in paths:
                target = folder / 'changed-source' / name
                target.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(tree / name,target)
        result = json.loads((folder/'verify-result.json').read_text())
        if number in {1236,751}:
            historical = PHASE/'carried-complete-results'/str(number)
            historical.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(folder/'verify-result.json', historical/'verify-result.json')
            for check in result['checks']:
                if 'record' in check:
                    record_path=n.P/check['record']; record=json.loads(record_path.read_text())
                    if record.get('subject_hashes') != json.loads(HELD.read_text())[str(number)] or record.get('stop_reason'):
                        raise ValueError('Completed repair3 evidence drift: '+str(number)+' '+check['check'])
                    for stream in ['stdout','stderr']:
                        if n.sha(record_path.with_suffix('.'+stream))!=record[stream+'_sha256']:
                            raise ValueError('Completed native log drift')
                    check['original_record_sha256']=n.sha(record_path)
                check['carried_evidence']=True
                check['original_native_run_id']='01M497MN3CXK842EEAAP765SFQ'
            result.update(carried_evidence=True, continued_by=identifier(),
                original_native_run_id='01M497MN3CXK842EEAAP765SFQ',
                carry_scope='Complete repair3 verification, including all measured failures. Sources and log hashes match; no new acceptance is inferred.')
            n.write(folder/'verify-result.json',result)
        rows.append({'issue':number,'verification':result['status'],'paths':paths,'engineering_acceptance':'pending_offline_review'})
        n.write(folder/'artifact-manifest.json',{'files':{str(p.relative_to(folder)):n.sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}})
    import package_native
    # Preserve the earlier archives; export current databases into this continuation.
    package_native.P = PHASE / 'exports'
    package_native.P.mkdir(exist_ok=True)
    databases = package_native.export_databases()
    n.write(n.P/'correction-export.json',{'databases':databases,'database_exports_root':str(package_native.P),
        'run_id':identifier(),'source_repair_run':'01M497MN3CXK842EEAAP765SFQ','results':rows,
        'actual_provider_bill_usd':None,'all_calls_upper_usd_micros':json.loads((n.P/'budget-audit.json').read_text())['combined_upper_usd_micros']})
    for suffix,label in [('', 'summary'),('/state','state'),('/stages?page%5Blimit%5D=100','stages')]:
        n.write(PHASE/('export-native-'+label+'.json'),n.api('/api/v1/runs/'+identifier()+suffix))
    state=json.loads((n.P.parent/'state.json').read_text())
    state.update(status='recovery_finished_review_pending',active_run_id=identifier(),notes='Verification continuation and exports completed. Failures remain explicit; offline acceptance pending; no extra source fix or paid call.')
    n.write(n.P.parent/'state.json',state)


def main():
    def stop(signum, frame):
        global STOP_REQUESTED
        STOP_REQUESTED = True
        raise KeyboardInterrupt('Verification continuation interrupted')
    signal.signal(signal.SIGTERM,stop)
    signal.signal(signal.SIGINT,stop)
    n.guard = guard
    stage=sys.argv[1]
    if stage not in {'verify_1104','verify_1031','export'}:
        raise ValueError('Continuation excludes source patching and model admission')
    try:
        guard(); globals()[stage]()
        print(json.dumps({'stage':stage,'status':'completed','paid_calls':0,'source_fixes':0}))
    except Exception as error:
        n.write(PHASE/(stage+'-failure.json'),{'reason':str(error),'time_epoch':time.time()})
        print(json.dumps({'stage':stage,'status':'failed','reason':str(error)})); return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
