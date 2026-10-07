"""Native evidence refresh, scheduled by a no-model Fabro workflow."""
from pathlib import Path
import json
import shutil
import signal
import sys
import zipfile
from native_measure import P, R, guard, hashes, measure, sha, write

def run(label, tree, args, timeout=1800):
    d=P/'initial-evidence'
    d.mkdir(exist_ok=True)
    result=measure(d,tree,label,args,timeout)
    print(json.dumps(result),flush=True)
    return result

def copyright():
    results=[]
    for name,label in [('baseline-original','original'),('baseline-check','corrected-baseline'),('issue-1031','candidate-1031')]:
        results.append(run('copyright-'+label,R/name,['run','//:copyright.check']))
    write(P/'initial-evidence/copyright-summary.json',{'checks':results,
          'correction':'Native root BUILD inputs //:BUILD and //:MODULE.bazel changed to filesystem names BUILD and MODULE.bazel.',
          'policy':'Native templates and allowed years are unchanged; scanner failures remain failures.'})

def aou():
    consumer=R/'aou-consumer'
    module=consumer/'MODULE.bazel'
    original=module.read_text()
    if 'path = "../baseline-check"' not in original:
        raise ValueError('Expected unmodified negative consumer setup')
    negative=run('aou-external-baseline',consumer,['build','//consumer:component_requirements'])
    text=(P/'initial-evidence/evidence/aou-external-baseline.stderr').read_text(errors='replace')
    negative_visibility=negative['exit_code']!=0 and 'visibility' in text.lower()
    module.write_text(original.replace('path = "../baseline-check"','path = "../issue-1031"'))
    positive=run('aou-external-candidate',consumer,['build','//consumer:component_requirements'])
    target=consumer/'bazel-bin/consumer'
    products=[]
    if target.exists():
        for path in target.rglob('*'):
            if path.is_file() and path.suffix in {'.rst','.json','.lobster'}:
                dest=P/'initial-evidence/aou-products'/path.relative_to(target)
                dest.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(path,dest)
                products.append({'path':str(dest.relative_to(P)),'sha256':sha(dest)})
    write(P/'initial-evidence/aou-summary.json',{'negative':negative,'negative_failed_on_visibility':negative_visibility,
          'positive':positive,'products':products,'separate_main_repository':True,
          'consumer_fixture':True,'actual_config_management_production_integration':'not_measured',
          'engineering_acceptance':'pending_offline_review'})

def archive_summary(database):
    path=database/'src.zip'
    result={'source_archive_present':path.exists(),'named_source':'score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp','matching_entries':[]}
    if path.exists():
        with zipfile.ZipFile(path) as archive:
            entries=archive.namelist()
            result.update(source_count=len(entries),matching_entries=[n for n in entries if n.endswith('/'+result['named_source']) or n==result['named_source']],source_archive_sha256=sha(path))
        dest=P/'initial-evidence'/database.name/'src.zip'
        dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,dest)
    return result

def codeql_create():
    results=[]
    for label,targets in [('nightly',['//score/message_passing','//score/mw/com']),('impl',['//score/mw/com/impl/...'])]:
        database=R/'codeql-baseline'/label
        args=['run','//quality/static_analysis:codeql_lint','--','--phase','create-database','--database-path',str(database),'--target',*targets]
        measured=run('codeql-create-'+label,R/'baseline-check',args,2400)
        summary=archive_summary(database)
        results.append({'scope':label,'measurement':measured,'database':str(database),'source_archive':summary})
    write(P/'initial-evidence/codeql-extraction-summary.json',{'checks':results,'source_selection':'Exact nightly roots for #751 and issue-supplied impl/... for #1104; source content unchanged except copyright input paths.'})

def codeql_analyze():
    database=R/'codeql-baseline/impl'
    result={'status':'not_run_missing_database'}
    creation=json.loads((P/'initial-evidence/codeql-extraction-summary.json').read_text())
    impl=next(c for c in creation['checks'] if c['scope']=='impl')
    if impl['measurement']['exit_code']==0:
        output=R/'codeql-baseline/reports'
        result=run('codeql-analyze-impl',R/'baseline-check',['run','//quality/static_analysis:codeql_lint','--','--phase','analyze-database','--database-path',str(database),'--output-dir',str(output),'--output-prefix','baseline-impl'],2400)
        if output.exists():shutil.copytree(output,P/'initial-evidence/codeql-reports',dirs_exist_ok=True)
    uri_counts={};locations=0
    for f in (P/'initial-evidence/codeql-reports').rglob('*.sarif'):
        sarif=json.loads(f.read_text())
        def visit(v):
            nonlocal locations
            if isinstance(v,dict):
                if 'physicalLocation' in v:locations+=1
                if 'uri' in v and v['uri'] in {'file:/','file:///',''}:uri_counts[v['uri']]=uri_counts.get(v['uri'],0)+1
                for child in v.values():visit(child)
            elif isinstance(v,list):
                for child in v:visit(child)
        visit(sarif)
    write(P/'initial-evidence/codeql-sarif-summary.json',{'measurement':result,'physical_locations':locations,'root_or_empty_uris':uri_counts,'unlocated_paths_are_not_synthesized':True})

def export():
    summaries={}
    for name in ['copyright-summary','aou-summary','codeql-extraction-summary','codeql-sarif-summary']:
        path=P/'initial-evidence'/(name+'.json')
        summaries[name]=json.loads(path.read_text()) if path.exists() else {'status':'missing'}
    write(P/'initial-evidence/summary.json',summaries)
    write(P/'initial-evidence/artifact-manifest.json',{'files':{str(f.relative_to(P/'initial-evidence')):sha(f) for f in (P/'initial-evidence').rglob('*') if f.is_file() and f.name!='artifact-manifest.json'}})
    print(json.dumps({'status':'evidence_exported','summary':str(P/'initial-evidence/summary.json'),'paid_calls':0}))

def main():
    def stop(signum,frame):raise RuntimeError('Evidence collector interrupted')
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    name=sys.argv[1]
    try:
        guard();globals()[name]();return 0
    except Exception as e:
        write(P/'initial-evidence'/(name+'-failure.json'),{'reason':str(e)})
        print(json.dumps({'status':'failed','stage':name,'reason':str(e)}));return 1

if __name__=='__main__':raise SystemExit(main())
