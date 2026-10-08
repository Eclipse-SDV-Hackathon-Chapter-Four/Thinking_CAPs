"""Compile bounded recovery phases using the unchanged stable fabric."""
from pathlib import Path
import hashlib
import json
import os
import shlex
import sys
import yaml
from score_sw_fabric.compiler.reader import semantic_digest
from score_sw_fabric.compiler.package import compile_request
from score_sw_fabric.compiler.validator import validate_native

D=Path(__file__).resolve().parent
P=D.parent
F=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha/fabric')
B='/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro'
os.environ['SCORE_FABRO_BIN']=B
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')
def seal(v):v={k:x for k,x in v.items() if k!='digest'};return {**v,'digest':semantic_digest(v)}

def main():
    phase=sys.argv[1]
    output=D/'phases'/phase
    output.mkdir(parents=True,exist_ok=True)
    if (output/'native-run-id').exists():raise ValueError('Registered phase is immutable; do not recreate')
    profile=yaml.safe_load((P/'compiler_profile.yaml').read_text())
    validator=yaml.safe_load((P/'validator_profile.yaml').read_text())
    write(output/'authority.json',json.loads((D/'authority.json').read_text()))
    origin={'kind':'authorized_human_decision','source_ref':{'path':'authority.json','sha256':sha(output/'authority.json')},
            'pointer':'/scope','decision_ref':'user-go-recovery-20261006','rationale':'Authorized execution within original $10; engineering acceptance remains offline and pending.'}
    if phase=='evidence':
        refs=['copyright','aou','codeql_create','codeql_analyze','export'];script=D/'evidence.py'
    elif phase=='evidence-2':
        refs=['aou','codeql_create','codeql_analyze','export'];script=D/'evidence2.py'
    elif phase=='correction':
        refs=['admit','draft','apply','verify_1236','verify_751','verify_1104','verify_1031','export'];script=D/'correction.py'
    else:raise ValueError('Unknown phase')
    ids=['local-recovery-'+phase+'-'+r for r in refs]
    plan=seal({'schema_version':1,'plan_kind':'draft','planning_status':'complete','closure_complete':True,
       'engineering_readiness':'not_evaluated','target_namespace':'local-operational-recovery','change':{'id':'bug-queue-'+phase},
       'semantic_inputs':{'authority':sha(output/'authority.json')},'scopes':[],'coverage':[],'findings':[],
       'instances':[{'instance_id':ident,'applicability':'required','effective_disposition':'create','dependency_ids':ids[i-1:i]} for i,ident in enumerate(ids)]})
    actions=[];support=[]
    for ref,ident in zip(refs,ids):
        draft=ref=='draft'
        a={'ref':ref,'purpose':"{% include 'prompts/correction.j2' %}" if draft else 'Run protected native recovery stage '+ref,
           'type':'prompt' if draft else 'deterministic_check','label':ref,'instance_ids':[ident],
           'role':'implementation_drafter' if draft else 'measurement_runner','allowed_inputs':['authority.json','budget-audit.json','source-bound-evidence'],
           'allowed_paths':[json.loads((D/'configuration.json').read_text())['scratch_root']],
           'expected_outputs':[ref+'-result.json'],'data_destinations':['provider.deepseek'] if draft else ['local:contribution-artifacts'],
           'write_scope':[] if draft else [str(D),json.loads((D/'configuration.json').read_text())['scratch_root'],str(P/'state.json')],
           'tool_profile':'none' if draft else 'frozen-host-collector','model_capability':'bounded-agent-v1' if draft else 'none',
           'budget':{'wall_time_seconds':1800 if draft else 14400,'attempts':1,'tool_calls':0 if draft else 20,
                     'input_tokens':len((D/'correction-prompt.txt').read_bytes()) if draft else 0,'output_tokens':96000 if draft else 0,'cost_microunits':2359296 if draft else 0},
           'completion_predicate':'Drafts/evidence exported; engineering acceptance remains separate.',
           'evidence_expectation':'Exact native commands, hashes, failures, diagnostics and unresolved obligations.',
           'fallible_outcomes':['failure','success'],'prohibited_authority':['approval','trusted_evidence_collection','automatic_approval','replayed_approval'],
           'support_files':[],'origin':origin}
        if draft:
            prompt=(D/'correction-prompt.txt').read_text()
            if '{% endraw %}' in prompt:raise ValueError('Template escape in context')
            path='prompts/correction.j2';a['support_files']=[path]
            support.append({'path':path,'content':'{% raw %}'+json.dumps(prompt,ensure_ascii=False)[1:-1]+'{% endraw %}','origin':origin})
        else:
            path='commands/'+ref+'.sh';a.update(command_file=path,support_files=[path])
            support.append({'path':path,'content':shlex.join(['env','PYTHONDONTWRITEBYTECODE=1',str(F/'.venv/bin/python'),str(script),ref])+'\n','origin':origin})
        actions.append(a)
    def edge(a,b,outcome):return {'source':a,'target':b,'type':'failure' if outcome=='failure' else 'success','outcome':outcome,'condition':None,'loop_id':None,'origin':origin}
    edges=[edge('start',refs[0],None)]
    for a,b in zip(refs,refs[1:]):edges.append(edge(a,b,'success'))
    for ref in refs[:-1]:
        if phase=='correction' and ref.startswith('verify_'):target=refs[refs.index(ref)+1]
        else:target='exit' if ref=='admit' else 'export'
        edges.append(edge(ref,target,'failure'))
    edges += [edge('export','exit','success'),edge('export','exit','failure')]
    mapping=seal({'schema_version':1,'id':'bugqueue-recovery-'+phase,'version':1,'plan_version':1,'compiler_profile':profile['id'],
          'review':{'state':'reviewed','reference':{**origin['source_ref'],'scope':'User operational task authority only; native acceptance pending'}},
          'rules':[{'id':'bounded-recovery-'+phase,'instance_ids':ids,'actions':actions}],'edges':edges,'loop_policies':[],'fan_groups':[],'support_files':support})
    request={'schema_version':1,'inputs':{},'local_paths':{'output_root':'out','protected_roots':[]}}
    for name,v in {'plan':plan,'execution_mapping':mapping,'compiler_profile':profile,'validator_profile':validator}.items():
        path='plan.json' if name=='plan' else name+'.yaml'
        (output/path).write_text(json.dumps(v,indent=2)+'\n' if name=='plan' else yaml.safe_dump(v))
        request['inputs'][name]={'path':path,'sha256':sha(output/path),'semantic_digest':v['digest']}
    (output/'compile.yaml').write_text(yaml.safe_dump(request));(output/'out').mkdir(exist_ok=True)
    def validation(files,entrypoint,profile):
        def runner(cmd,**kwargs):
            result=__import__('subprocess').run(cmd,**kwargs)
            label='version' if 'version' in cmd else 'validate'
            (output/('compiler-'+label+'.stdout')).write_text(result.stdout);(output/('compiler-'+label+'.stderr')).write_text(result.stderr)
            return result
        return validate_native(files,entrypoint,profile,runner=runner)
    package=compile_request(output/'compile.yaml',output/'out/package.json',native_validator=validation)
    for name,content in package['files'].items():
        path=output/'workflow'/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(content)
    nodeids={n['label']:n['id'] for n in package['manifest']['ir']['nodes'] if n['label'] in refs}
    write(output/'node-ids.json',nodeids)
    if phase=='correction':
        f=output/'workflow/workflow.fabro';node=nodeids['draft']
        f.write_text('\n'.join(line.replace(' [',' [output_retries=0, fidelity="summary:high", model="deepseek-flash", provider="deepseek", reasoning_effort="medium", ',1) if line.strip().startswith(node+' [') else line for line in f.read_text().splitlines())+'\n')
    f=output/'workflow/workflow.toml'
    f.write_text(f.read_text()+'''\n[run.model]\nprovider="deepseek"\nname="deepseek-flash"\n[run.model.controls]\nreasoning_effort="medium"\n[run.model.fallbacks]\ndeepseek-flash=[]\n[run.clone]\nenabled=false\n[run.agent]\nfabro_tools=false\n''')
    write(output/'operational-overlay.json',{'package_sha256':sha(output/'out/package.json'),'graph_sha256':sha(output/'workflow/workflow.fabro'),'config_sha256':sha(f),
            'paid_stages_max':1 if phase=='correction' else 0,'native_engineering_acceptance':'pending_offline_review'})
    print(json.dumps({'phase':phase,'workflow':str(output/'workflow/workflow.toml'),'paid_stages':1 if phase=='correction' else 0}))

if __name__=='__main__':main()
