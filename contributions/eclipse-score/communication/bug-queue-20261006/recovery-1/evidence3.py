"""Bounded supplemental native measurements; preserves failed exact reproduction."""
from pathlib import Path
import json
import shutil
import signal
import sys
from native_measure import P, R, guard, measure, sha, write
D=P/'evidence3-results'
def run(label,tree,args,timeout=2400):
    D.mkdir(exist_ok=True);result=measure(D,tree,label,args,timeout);print(json.dumps(result),flush=True);return result

def buildifier_help():
    result=run('buildifier-help',R/'issue-1236',['run','@buildifier_prebuilt//:buildifier','--','--help'],1200)
    write(D/'buildifier-summary.json',result)

def aou_test():
    result=run('external-aou-trlc-validation',R/'aou-consumer',['test','//consumer:component_requirements_test','--nocache_test_results'],1800)
    write(D/'aou-summary.json',{'measurement':result,'fixture':True,'production_config_management_integration':'not_measured'})

def codeql_analyze():
    database=R/'codeql-baseline-v2/nightly';output=R/'codeql-baseline-v2/nightly-reports'
    result=run('codeql-analyze-nightly',R/'baseline-check',['run','//quality/static_analysis:codeql_lint','--','--phase','analyze-database','--database-path',str(database),'--output-dir',str(output),'--output-prefix','baseline-nightly'])
    if output.exists():shutil.copytree(output,D/'codeql-reports',dirs_exist_ok=True)
    counts={};samples=[];locations=0;findings=0;reports=0
    def visit(value,path,rule=None):
        nonlocal locations
        if isinstance(value,dict):
            rule=value.get('ruleId',rule)
            if 'physicalLocation' in value:locations+=1
            if value.get('uri') in {'file:/','file:///',''}:
                uri=value['uri'];counts[uri]=counts.get(uri,0)+1
                if len(samples)<8:samples.append({'pointer':path,'rule_id':rule,'artifact_location':value})
            for key,child in value.items():visit(child,path+'/'+str(key),rule)
        elif isinstance(value,list):
            for i,child in enumerate(value):visit(child,path+'/'+str(i),rule)
    for path in (D/'codeql-reports').rglob('*.sarif'):
        reports+=1;data=json.loads(path.read_text());findings+=sum(len(run.get('results',[])) for run in data.get('runs',[]));visit(data,path.name)
    write(D/'codeql-sarif-summary.json',{'measurement':result,'scope':'Successful exact nightly roots, not the blocked issue-supplied impl/... scope','exact_1104_reproduction':'blocked by traced build-error test shell action','reports':reports,'findings':findings,'physical_locations':locations,'root_or_empty_uris':counts,'bounded_samples':samples,'paths_synthesized':False})

def export():
    summaries={}
    for name in ['buildifier-summary','aou-summary','codeql-sarif-summary']:
        path=D/(name+'.json');summaries[name]=json.loads(path.read_text()) if path.exists() else {'status':'missing'}
    write(D/'summary.json',summaries);write(D/'artifact-manifest.json',{'files':{str(f.relative_to(D)):sha(f) for f in D.rglob('*') if f.is_file() and f.name!='artifact-manifest.json'}})

def main():
    def stop(signum,frame):raise RuntimeError('Supplemental measurement interrupted')
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop);name=sys.argv[1];D.mkdir(exist_ok=True)
    try:guard();globals()[name]();return 0
    except Exception as error:write(D/(name+'-failure.json'),{'reason':str(error)});print(json.dumps({'stage':name,'reason':str(error)}));return 1
if __name__=='__main__':raise SystemExit(main())
