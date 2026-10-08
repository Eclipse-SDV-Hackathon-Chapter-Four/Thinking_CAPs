"""One separately authorized deterministic correction for #751; no model calls."""
import hashlib
import json
import signal
import shutil
import subprocess
import sys
import time

import native_measure as n
import repair3 as repair

OUT = n.P / 'additional-751'
ROOT = n.R / 'additional-751'
TREE = ROOT / 'issue-751'
PHASE = n.P / 'phases/additional-751'
BASE_GUARD = n.guard
STOP_REQUESTED = False


def identifier():
    return (PHASE / 'native-run-id').read_text().strip()


def guard():
    if STOP_REQUESTED:
        raise SystemExit('Additional #751 attempt interrupted')
    BASE_GUARD()
    for name, expected in json.loads((PHASE / 'controls.json').read_text()).items():
        if n.sha(n.P / name) != expected:
            raise ValueError('Additional attempt control changed: ' + name)
    authority = json.loads((OUT / 'authority.json').read_text())
    if n.sha(n.P / 'native-repair-supervisor.json') != authority['old_round_ledger_sha256']:
        raise ValueError('Original retry history changed')
    if TREE.stat().st_dev != n.R.stat().st_dev or not TREE.resolve().is_relative_to(n.R):
        raise ValueError('Additional candidate left its bound workspace')


def update(number, status, **fields):
    path = n.P.parent / 'state.json'; state = json.loads(path.read_text())
    for item in state['items']:
        if item['issue_number'] == number:
            item.update(status=status, run_id=identifier(), recovery='recovery-1/additional-751', **fields)
    state.update(status='additional_751_running', active_run_id=identifier(), updated_at_epoch=time.time())
    n.write(path,state)


def apply_expected_order():
    guard()
    before = json.loads((OUT / 'source-before.json').read_text())
    if n.hashes(TREE) != before:
        raise ValueError('Additional attempt starting source differs')
    ledger = json.loads((OUT / 'repair-ledger.json').read_text())
    if ledger['maximum_additional_fixes'] != 1 or ledger['attempts'] or ledger['paid_calls'] != 0:
        raise ValueError('Additional source correction already consumed or authority differs')
    patch = OUT / 'expected-order.patch'
    subprocess.run(['git','-C',str(TREE),'apply','--check','--whitespace=error',str(patch)],check=True,capture_output=True)
    ledger['attempts'].append({'attempt':1,'native_run_id':identifier(),'source_repair':'Expected label order only',
        'paid_calls':0,'admitted_at_epoch':time.time(),'patch_sha256':n.sha(patch)})
    n.write(OUT / 'repair-ledger.json',ledger)
    subprocess.run(['git','-C',str(TREE),'apply','--whitespace=error',str(patch)],check=True,capture_output=True)
    after = n.hashes(TREE)
    changed = [key for key in sorted(set(before) | set(after)) if before.get(key) != after.get(key)]
    if changed != ['quality/static_analysis/codeql_lint_test.py']:
        raise ValueError('Source correction changed an unexpected file')
    (OUT/'results/751').mkdir(parents=True,exist_ok=True)
    n.write(OUT/'results/751/candidate-hashes.json',after)
    n.write(OUT/'apply-result.json',{'run_id':identifier(),'changed_paths':changed,'source_before':before,'source_after':after,
        'original_candidate_unchanged':n.hashes(n.R/'issue-751')==before,'paid_calls':0,'old_round_attempts':3,'additional_attempts':1})
    update(751,'expected_order_corrected',stage='apply_expected_order')


def run_check(number, label, args, timeout=1800):
    guard(); folder=OUT/'results/751'
    before_index=n.sha(TREE/'.git/index')
    before_discovery=hashlib.sha256(subprocess.check_output(['git','-C',str(TREE),'ls-files','--stage','-z'])).hexdigest()
    result=n.measure(folder,TREE,label,args,timeout)
    record_path=n.P/result['record']; record=json.loads(record_path.read_text())
    after_discovery=hashlib.sha256(subprocess.check_output(['git','-C',str(TREE),'ls-files','--stage','-z'])).hexdigest()
    if before_discovery != after_discovery:
        raise ValueError('Native Git-discovery input changed')
    record.update(git_index_sha256_before=before_index,git_index_sha256_after=n.sha(TREE/'.git/index'),
        git_file_discovery_sha256_before=before_discovery,git_file_discovery_sha256_after=after_discovery,
        native_run_id=identifier(),carried_evidence=False,additional_authorized_attempt=1)
    n.write(record_path,record)
    guard()
    return result


def verify_751():
    guard()
    repair.P=OUT; repair.R=ROOT; repair.update=update; repair.run_check=run_check
    try:
        repair.verify(751)
    finally:
        result_path=OUT/'results/751/verify-result.json'
        if result_path.exists():
            result=json.loads(result_path.read_text());result.update(native_run_id=identifier(),
                additional_authorized_attempt=1,old_round_attempts=3,original_candidate_preserved=True)
            n.write(result_path,result)


def export():
    guard(); folder=OUT/'results/751'
    expected=json.loads((folder/'candidate-hashes.json').read_text())
    if n.hashes(TREE)!=expected:
        raise ValueError('Additional candidate changed after verification')
    held=json.loads((OUT/'source-before.json').read_text())
    if n.hashes(n.R/'issue-751') != held:
        raise ValueError('Original completed candidate changed')
    result=json.loads((folder/'verify-result.json').read_text())
    if result.get('native_run_id') != identifier():
        raise ValueError('Additional verification is missing; do not export older results')
    changed=subprocess.check_output(['git','-C',str(TREE),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()
    allowed=repair.ALLOWED[751]
    paths=[name for name in changed if name=='BUILD' or name in allowed['allowed_files'] or any(name.startswith(prefix) for prefix in allowed['allowed_prefixes'])]
    (folder/'communication-751.patch').write_bytes(subprocess.check_output(['git','-C',str(TREE),'diff','--binary','--',*paths]))
    for name in paths:
        target=folder/'changed-source'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(TREE/name,target)
    source=ROOT/'codeql-candidate/751'
    if source.exists():
        before=n.hashes(source); target=OUT/'native-codeql-751.tar.gz';temporary=OUT/'native-codeql-751.tar.gz.tmp'
        command=['tar','--use-compress-program=gzip -1','-cf',str(temporary),'-C',str(source.parent),source.name]
        with (OUT/'database-export.stderr').open('wb') as error:
            process=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=error,start_new_session=True)
            try:
                while process.poll() is None:
                    guard()
                    if shutil.disk_usage(OUT).free<64*1024*1024:
                        raise OSError('Explicit artifact destination has less than64MiB free')
                    time.sleep(1)
                if process.returncode or n.hashes(source)!=before:
                    raise ValueError('Additional database packaging failed or source drifted')
                temporary.replace(target)
            except BaseException:
                if process.poll() is None:
                    process.terminate();process.wait(timeout=10)
                raise
        n.write(OUT/'database-export.json',{'source':str(source),'source_hashes':before,
            'archive':str(target),'archive_sha256':n.sha(target),'bytes':target.stat().st_size,
            'command':command,'engineering_acceptance':'pending_offline_review'})
    n.write(OUT/'export-result.json',{'native_run_id':identifier(),'issue':751,'source_paths':paths,
        'verification':result['status'],'targeted_checks':result['targeted_checks'],
        'original_round_history_preserved':True,'paid_calls':0,'published':False,'engineering_acceptance':'pending_offline_review'})
    n.write(folder/'artifact-manifest.json',{'files':{str(p.relative_to(folder)):n.sha(p) for p in folder.rglob('*') if p.is_file() and p.name!='artifact-manifest.json'}})
    update(751,'additional_attempt_exported_review_pending',stage='exported')


def main():
    def stop(signum,frame):
        global STOP_REQUESTED
        STOP_REQUESTED=True;raise KeyboardInterrupt('Additional #751 attempt interrupted')
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop);n.guard=guard
    stage=sys.argv[1]
    if stage not in {'apply_expected_order','verify_751','export'}:
        raise ValueError('Unapproved additional stage')
    try:
        guard();globals()[stage]()
        print(json.dumps({'stage':stage,'status':'completed','paid_calls':0}))
    except Exception as error:
        n.write(PHASE/(stage+'-failure.json'),{'reason':str(error),'time_epoch':time.time()})
        print(json.dumps({'stage':stage,'status':'failed','reason':str(error)}));return 1
    return 0


if __name__=='__main__':
    raise SystemExit(main())
