"""One Flash correction and deterministic per-issue verification, owned by Fabro."""
from pathlib import Path, PurePosixPath
import json
import math
import re
import shutil
import signal
import subprocess
import sys
import time
import zipfile
from native_measure import P, R, C, guard, hashes, measure, sha, write, api

NUMBERS=[1236,751,1104,1031]
ALLOWED={i['issue_number']:i for i in json.loads((P.parent/'queue-record.json').read_text())['items']}

def update(number,status,**fields):
    path=P.parent/'state.json';state=json.loads(path.read_text())
    identifier=(P/'phases/repair-1/native-run-id').read_text().strip()
    for item in state['items']:
        if item['issue_number']==number:item.update(status=status,run_id=identifier,recovery='recovery-1',**fields)
    state.update(status='recovering_correction',active_run_id=identifier,updated_at_epoch=time.time())
    write(path,state)

def admit():
    audit=json.loads((P/'budget-audit.json').read_text())
    if audit['combined_upper_usd_micros']>10_000_000 or audit['new_combined_call_reservation_usd_micros']!=2359296:
        raise ValueError('Recovery exceeds original $10 task authority')
    if sha(P.parent/'budget-ledger.json')!=audit['parent_ledger_sha256']:
        raise ValueError('Original budget history changed')
    if (P/'correction-admission.json').exists():raise ValueError('Combined paid correction already admitted; never reset')
    for name,expected in json.loads((P/'correction-subjects.json').read_text()).items():
        if hashes(R/name)!=expected:raise ValueError('Correction context changed: '+name)
    write(P/'correction-admission.json',{'reserved_new_usd_micros':2359296,'all_calls_upper_usd_micros':audit['combined_upper_usd_micros'],
          'paid_stages_max':1,'output_retries':0,'actual_provider_bill_usd':None,'native_run_id':(P/'phases/repair-1/native-run-id').read_text().strip()})
    for n in NUMBERS:update(n,'pending_correction',stage='admit')

def get_response():
    identifier=(P/'phases/repair-1/native-run-id').read_text().strip()
    state=api('/api/v1/runs/'+identifier+'/state')
    write(P/'correction-native-state.json',state)
    node=json.loads((P/'phases/repair-1/node-ids.json').read_text())['draft']
    values=[v['response'] for k,v in state.get('stages',{}).items() if k.startswith(node+'@') and v.get('response') is not None]
    if len(values)!=1:raise ValueError('Expected one complete correction response')
    raw=values[0]
    if isinstance(raw,str) and re.fullmatch(r'blob://sha256/[a-f0-9]{64}',raw):
        digest=raw.rsplit('/',1)[-1];blob=api('/api/v1/runs/'+identifier+'/blobs/'+digest,raw=True)
        if __import__('hashlib').sha256(blob).hexdigest()!=digest:raise ValueError('Native response digest differs')
        raw=json.loads(blob)
    if not isinstance(raw,str):raise ValueError('Unsupported response type')
    (P/'correction-response.txt').write_text(raw)
    text=raw.strip()
    if text.startswith('```json') and text.endswith('```'):text=text[7:-3].strip()
    result=json.loads(text)
    if not isinstance(result,dict) or set(result)!={'issues','rationale'} or not isinstance(result['rationale'],str):raise ValueError('Correction contract differs')
    if not isinstance(result['issues'],list) or len(result['issues'])!=3 or {v.get('number') for v in result['issues']}!={1236,751,1104}:
        raise ValueError('Expected exactly the three scoped corrections')
    return result

def check_patch(number,patch_text,tree):
    if not isinstance(patch_text,str) or len(patch_text.encode())>180_000:raise ValueError('Patch size/type invalid')
    if not patch_text:return []
    forbidden=['GIT binary patch','Binary files ','rename from ','rename to ','copy from ','copy to ','deleted file mode','new file mode 120000']
    if any(value in patch_text for value in forbidden):raise ValueError('Unsupported binary, rename, deletion or symlink patch')
    raw=patch_text.encode()
    command=['git','-C',str(tree),'apply','--recount','--numstat','-z','-']
    result=subprocess.run(command,input=raw,capture_output=True,check=True)
    paths=[]
    for record in result.stdout.split(b'\0'):
        if not record:continue
        columns=record.decode().split('\t',2)
        if len(columns)!=3 or not columns[0].isdigit() or not columns[1].isdigit():raise ValueError('Unsupported patch entry')
        name=columns[2];path=PurePosixPath(name)
        item=ALLOWED[number]
        if path.is_absolute() or '..' in path.parts or '.git' in path.parts or '\\' in name:
            raise ValueError('Patch path escapes scope')
        if name not in item['allowed_files'] and not any(name.startswith(prefix) for prefix in item['allowed_prefixes']):
            raise ValueError('Patch path outside scope: '+name)
        target=tree/path
        if target.is_symlink() or any(p.is_symlink() for p in target.parents if p!=tree.parent):raise ValueError('Symlink patch refused')
        paths.append(name)
    if not 1<=len(paths)<=16 or len(set(paths))!=len(paths):raise ValueError('Patch file envelope invalid')
    subprocess.run(['git','-C',str(tree),'apply','--recount','--check','--whitespace=error','-'],input=raw,capture_output=True,check=True)
    return paths

def apply():
    result=get_response();planned=[]
    for value in result['issues']:
        if not isinstance(value,dict) or set(value)!={'number','patch','rationale'} or not isinstance(value['rationale'],str):raise ValueError('Malformed issue correction')
        number=value['number'];tree=R/('issue-'+str(number))
        paths=check_patch(number,value['patch'],tree)
        planned.append((number,value,paths,tree))
    # All independent patches are checked before any correction source write.
    for number,value,paths,tree in planned:
        folder=P/'results'/str(number);folder.mkdir(parents=True,exist_ok=True)
        write(folder/'model-disposition.json',value)
        if value['patch']:
            (folder/'model.patch').write_text(value['patch'])
            subprocess.run(['git','-C',str(tree),'apply','--recount','--whitespace=error','-'],input=value['patch'].encode(),capture_output=True,check=True)
        write(folder/'candidate-hashes.json',hashes(tree))
        update(number,'correction_applied' if paths else 'assessment_or_recovered_draft',stage='apply',correction_paths=paths)
    write(P/'correction.json',result)
    write(P/'results/1031/candidate-hashes.json',hashes(R/'issue-1031'))

def run_check(number,label,args,timeout=1800):
    d=P/'results'/str(number);d.mkdir(parents=True,exist_ok=True)
    return measure(d,R/('issue-'+str(number)),label,args,timeout)

def lint_checks():
    tree=R/'issue-1236';packages=[p for p in ['tools/lint/buildifier','quality/buildifier'] if (tree/p/'BUILD').exists()]
    patterns=['//'+p+'/...' for p in packages]
    records=[]
    if not patterns:return [{'check':'buildifier-regression','status':'missing_native_regression_package'}]
    records.append(run_check(1236,'buildifier-regression',['test',*patterns,'--nocache_test_results']))
    query='kind("sh_binary|py_binary", //:all union '+ ' union '.join(patterns)+')'
    records.append(run_check(1236,'buildifier-target-discovery',['query',query,'--output=label_kind'],600))
    output=(P/'results/1236/evidence/buildifier-target-discovery.stdout').read_text()
    targets=[line.split()[-1] for line in output.splitlines() if len(line.split())==3 and 'buildifier' in line.split()[-1]]
    if not targets:records.append({'check':'buildifier-enforcement','status':'missing_runnable_target'})
    for i,target in enumerate(targets):records.append(run_check(1236,'buildifier-enforcement-'+str(i),['run',target,'--','--recursive']))
    return records

def codeql_checks(number):
    records=[]
    records.append(run_check(number,'analysis-regressions',['test','//quality/static_analysis/...','--nocache_test_results'],900))
    database=R/'codeql-candidate'/str(number);output=R/'codeql-candidate'/('reports-'+str(number))
    targets=['//score/message_passing','//score/mw/com'] if number==751 else ['//score/mw/com/impl/...']
    selection=['--production-targets','--audit-source','score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp'] if number==751 else []
    records.append(run_check(number,'codeql-create',['run','//quality/static_analysis:codeql_lint','--','--phase','create-database','--database-path',str(database),*selection,'--target',*targets],600 if number==1104 else 2400))
    if number==1104 and records[-1]['exit_code']!=0:
        database=R/'codeql-candidate/1104-nightly'
        records.append(run_check(number,'codeql-create-nightly-projection',['run','//quality/static_analysis:codeql_lint','--','--phase','create-database','--database-path',str(database),'--target','//score/message_passing','//score/mw/com'],2400))
        records[-1]['scope']='Diagnostic nightly projection; failed exact impl/... check is retained above.'
    coverage={'source_archive_present':(database/'src.zip').exists(),'named_source_present':False}
    if (database/'src.zip').exists():
        with zipfile.ZipFile(database/'src.zip') as archive:
            names=archive.namelist();needle='score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp'
            coverage.update(named_source_present=any(n.endswith('/'+needle) or n==needle for n in names),archive_entries=len(names),archive_sha256=sha(database/'src.zip'))
        dest=P/'results'/str(number)/'native-codeql';dest.mkdir(parents=True,exist_ok=True);shutil.copyfile(database/'src.zip',dest/'src.zip')
    write(P/'results'/str(number)/'codeql-extraction.json',coverage)
    if number==751:records.append({'check':'named-production-source-extracted','exit_code':0 if coverage['named_source_present'] else 1,'fixture':False})
    if number==1104 and records[-1]['exit_code']==0:
        records.append(run_check(number,'codeql-analyze',['run','//quality/static_analysis:codeql_lint','--','--phase','analyze-database','--database-path',str(database),'--output-dir',str(output),'--output-prefix','candidate-1104'],2400))
        if output.exists():shutil.copytree(output,P/'results/1104/native-codeql/reports',dirs_exist_ok=True)
        invalid=[];locations=0;report_count=0
        def visit(value,path):
            nonlocal locations
            if isinstance(value,dict):
                if 'physicalLocation' in value:locations+=1
                if value.get('uri') in {'file:/','file:///',''}:invalid.append({'report':str(path),'uri':value['uri']})
                for child in value.values():visit(child,path)
            elif isinstance(value,list):
                for child in value:visit(child,path)
        for report in output.rglob('*.sarif'):
            report_count+=1;visit(json.loads(report.read_text()),report.relative_to(output))
        write(P/'results/1104/codeql-sarif.json',{'reports':report_count,'physical_locations':locations,'root_or_empty_uris':invalid,'paths_synthesized':False})
        records.append({'check':'native-sarif-location-uris','exit_code':0 if report_count and not invalid else 1,'fixture':False})
    return records

def verify(number):
    tree=R/('issue-'+str(number));folder=P/'results'/str(number)
    expected_path=folder/'candidate-hashes.json'
    if not expected_path.exists():raise ValueError('No admitted correction source')
    expected=json.loads(expected_path.read_text())
    if hashes(tree)!=expected:raise ValueError('Candidate changed before checks')
    update(number,'running',stage='verify')
    records=[]
    if number==1236:records+=lint_checks()
    if number in {751,1104}:records+=codeql_checks(number)
    if number==1031:
        records += [run_check(number,'aou-target',['build','//score/mw/com/dependability/safety_analysis:aous']),
                    run_check(number,'visibility',['test','//quality/visibility_guard:visibility_guard_test','--nocache_test_results'])]
        records.append(measure(folder,R/'aou-consumer','external-consumer-lock',['mod','deps','--lockfile_mode=update'],1800))
        records.append(measure(folder,R/'aou-consumer','external-aou-trlc-validation',['test','//consumer:component_requirements_test','--nocache_test_results'],1800))
        for name in ['MODULE.bazel','MODULE.bazel.lock','consumer/BUILD','consumer/component_requirements.trlc']:
            source=R/'aou-consumer'/name
            if source.is_file():
                dest=folder/'external-consumer-fixture'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
    for label,args in [('copyright',['run','//:copyright.check']),('format',['run','//:format.check']),('build-all',['build','//...']),('test-all',['test','//...','--nocache_test_results'])]:
        records.append(run_check(number,label,args,1800))
        if label=='build-all' and records[-1]['exit_code']!=0:
            text=(folder/'evidence/build-all.stderr').read_text(errors='replace')
            if any(word in text for word in ['Error downloading','Failed to fetch','no such package']):
                records.append({'check':'test-all','status':'not_run_dependency_failure'});break
    source_match=hashes(tree)==expected
    pending=['Offline engineering acceptance; no issue closure is inferred.']
    if number==1031:pending.append('Actual Config Management production integration and complete FMEA/LOBSTER non-duplication remain outside the artificial separate-module consumer test.')
    if number==1104:
        disposition=json.loads((folder/'model-disposition.json').read_text())
        if not disposition['patch']:pending.append('No source-backed correction proposed; use baseline reproduction evidence and assessment, not a fabricated file path.')
    general={'copyright','format','build-all','test-all'}
    focused=[value for value in records if value.get('check') not in general]
    targeted_status='passed' if focused and all(value.get('exit_code')==0 for value in focused) else 'failed_or_missing'
    status='measured_checks_passed_review_pending' if source_match and all(v.get('exit_code')==0 for v in records) else 'failed_or_missing_checks'
    write(folder/'verify-result.json',{'status':status,'targeted_checks':targeted_status,'checks':records,'source_match':source_match,'pending':pending,'engineering_acceptance':'pending_offline_review','carried_evidence':False})
    logs=tree/'bazel-testlogs'
    if logs.exists():
        for path in logs.rglob('*'):
            if path.is_file() and path.name in {'test.xml','test.log'}:
                dest=folder/'native-testlogs'/path.relative_to(logs);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,dest)
    update(number,'draft_checks_passed_review_pending' if status=='measured_checks_passed_review_pending' else 'needs_review_or_fix',stage='verification_exported')
    if status!='measured_checks_passed_review_pending':raise RuntimeError('Failed or missing native checks retained')

def export():
    identifier=(P/'phases/repair-1/native-run-id').read_text().strip();results=[]
    for number in NUMBERS:
        tree=R/('issue-'+str(number));folder=P/'results'/str(number);folder.mkdir(parents=True,exist_ok=True)
        # Root BUILD includes the explicitly documented copyright input correction.
        modified=subprocess.check_output(['git','-C',str(tree),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()
        allowed=ALLOWED[number]
        paths=[name for name in modified if name=='BUILD' or name in allowed['allowed_files'] or any(name.startswith(prefix) for prefix in allowed['allowed_prefixes'])]
        if paths:
            subprocess.run(['git','-C',str(tree),'-c','core.hooksPath=/dev/null','add','--intent-to-add','--',*paths],check=True,capture_output=True)
            (folder/('communication-'+str(number)+'.patch')).write_bytes(subprocess.check_output(['git','-C',str(tree),'diff','--binary','--',*paths]))
            for name in paths:
                dest=folder/'changed-source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(tree/name,dest)
        verification=json.loads((folder/'verify-result.json').read_text()) if (folder/'verify-result.json').exists() else {'status':'not_run'}
        results.append({'issue':number,'verification':verification['status'],'paths':paths,'engineering_acceptance':'pending_offline_review'})
        write(folder/'artifact-manifest.json',{'files':{str(f.relative_to(folder)):sha(f) for f in folder.rglob('*') if f.is_file() and f.name!='artifact-manifest.json'}})
    for suffix,label in [('', 'summary'),('/state','state'),('/stages?page%5Blimit%5D=100','stages')]:
        try:write(P/('native-correction-'+label+'.json'),api('/api/v1/runs/'+identifier+suffix))
        except Exception as error:write(P/('native-correction-'+label+'-failure.json'),{'reason':str(error)})
    from package_native import export_databases
    databases=export_databases()
    write(P/'correction-export.json',{'databases':databases,'run_id':identifier,'results':results,'actual_provider_bill_usd':None,'all_calls_upper_usd_micros':json.loads((P/'budget-audit.json').read_text())['combined_upper_usd_micros']})
    state=json.loads((P.parent/'state.json').read_text());state.update(status='recovery_finished_review_pending',
       notes='Recovery exports complete. Native failures and missing evidence remain visible; offline engineering acceptance pending. Actual billing unknown; audited upper bound under original $10 cap.')
    write(P.parent/'state.json',state)

def main():
    def stop(signum,frame):raise RuntimeError('Recovery interrupted')
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    stage=sys.argv[1]
    try:
        guard()
        if stage.startswith('verify_'):verify(int(stage.split('_')[1]))
        else:globals()[stage]()
        print(json.dumps({'stage':stage,'status':'completed','engineering_acceptance':'pending_offline_review'}));return 0
    except Exception as error:
        write(P/(stage+'-failure.json'),{'reason':str(error),'time_epoch':time.time()})
        print(json.dumps({'stage':stage,'status':'failed','reason':str(error)}));return 1

def get_response():
    value=json.loads((P/'repair-1/canonical-correction.json').read_text())
    for issue in value['issues']:
        expected=json.loads((P/'repair-1'/str(issue['number'])/'preparation.json').read_text())['source_hashes_before']
        if hashes(R/('issue-'+str(issue['number'])))!=expected:raise ValueError('Repair subject changed')
    ledger=P/'native-repair-supervisor.json'
    if ledger.exists():raise ValueError('This repair attempt already admitted; never reset')
    write(ledger,{'maximum_fixes_retries':3,'attempts':[{'attempt':1,'phase':'repair-1','native_run_id':(P/'phases/repair-1/native-run-id').read_text().strip(),'paid_model_calls':0}],'further_paid_model_calls':0,'engineering_acceptance':'pending_offline_review'})
    return value

if __name__=='__main__':raise SystemExit(main())
