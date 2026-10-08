from pathlib import Path
import hashlib
import json
import os
import shlex
import yaml
from score_sw_fabric.compiler.reader import semantic_digest
from score_sw_fabric.compiler.package import compile_request

P=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167')
D=P/'follow-up/final-verification-run'
S=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha')
PYTHON=str(S/'fabric/.venv/bin/python')
BINARY='/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro'
os.environ['SCORE_FABRO_BIN']=BINARY

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def seal(v):
 v={k:x for k,x in v.items() if k!='digest'}; return {**v,'digest':semantic_digest(v)}
def write(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n')

origin={'kind':'authorized_human_decision','decision_ref':'user-go-post-supervisor-20261006','pointer':'/user_instruction','rationale':'User requested continuation after the completed supervisor; deterministic verification only, no additional paid calls; engineering acceptance pending','source_ref':{'path':'authority.json','sha256':sha(D/'authority.json')}}
refs=['verify','export']
ids=['supervisor-communication1167-'+r for r in refs]
plan=seal({'schema_version':1,'plan_kind':'draft','planning_status':'complete','closure_complete':True,'engineering_readiness':'not_evaluated','target_namespace':'local-operational-communication1167','change':{'id':'communication1167-supervisor'},'semantic_inputs':{'task_authority':sha(D/'authority.json')},'scopes':[],'coverage':[],'findings':[],'instances':[{'instance_id':name,'applicability':'required','effective_disposition':'create','dependency_ids':ids[i-1:i]} for i,name in enumerate(ids)]})
profile=yaml.safe_load((P/'compiler_profile.yaml').read_text());validator=yaml.safe_load((P/'validator_profile.yaml').read_text())
actions=[];support=[]
for ref,ident in zip(refs,ids):
 draft=ref.startswith('draft')
 prompt='''Correct the candidate contribution for eclipse-score/communication issue #1167 using the most recent prepare stage correction packet in the completed-stage output. The packet contains the exact current files, failed checks, allowed paths and pinned native source context. Use the highest attempt number packet as current; earlier packets are historical. Known environment/tooling corrections are already applied. Preserve the five API coverage obligations, native C++17 API signatures, license notices, finite waits, failing exits and the copyright target path correction. Only change paths explicitly listed in that packet. Never reduce or skip mandatory checks, invent IDs, accept engineering decisions, change unrelated source, or claim verification success. If no further scoped correction is supported by the evidence, return an empty files array with the unresolved reason. Return ONLY JSON {"files":[{"path":"relative/path","content":"complete replacement content"}],"rationale":"brief engineering reason"}. No Markdown fences or assumptions array. Put all complete source files before rationale. No tools are available. Do not create another workflow or call another model.'''
 if draft: prompt += '\n\nThe complete current correction packet is embedded directly below; use this content even if earlier command output is a blob reference.\n' + (P/'supervisor/remaining-correction-packet.json').read_text()
 action={'ref':ref,'purpose':prompt if draft else 'Execute frozen host supervisor stage '+ref,'type':'prompt' if draft else 'deterministic_check','label':ref,'instance_ids':[ident],'role':'implementation_drafter' if draft else 'measurement_runner','allowed_inputs':['authority.json','correction-packet.json','native-evidence'],'allowed_paths':[str(P/'candidate'),str(S)],'expected_outputs':[ref+'-result.json'],'data_destinations':['provider.deepseek'] if draft else ['local:contribution-artifacts'],'write_scope':[] if draft else [str(P),str(S)],'tool_profile':'none' if draft else 'frozen-host-collector','model_capability':'bounded-agent-v1' if draft else 'none','budget':{'wall_time_seconds':1200 if draft else 14400,'attempts':1,'tool_calls':0 if draft else 20,'input_tokens':1000000 if draft else 0,'output_tokens':32000 if draft else 0,'cost_microunits':2359296 if draft else 0},'completion_predicate':'Output retained; verification and acceptance remain separate','evidence_expectation':'Native source, response and measured results with hashes; failures preserved','fallible_outcomes':['failure','success'],'prohibited_authority':['approval','trusted_evidence_collection','automatic_approval','replayed_approval'],'support_files':[],'origin':origin}
 if not draft:
  path='commands/'+ref+'.sh';content=shlex.join([PYTHON,str(P/'follow-up/verify_unique_tmp.py'),ref])+'\n';action.update(command_file=path,support_files=[path]);support.append({'path':path,'content':content,'origin':origin})
 actions.append(action)
def edge(a,b,outcome):return {'source':a,'target':b,'type':'failure' if outcome=='failure' else 'success','outcome':outcome,'condition':None,'loop_id':None,'origin':origin}
edges=[edge('start','verify',None),edge('verify','export','success'),edge('verify','export','failure'),edge('export','exit','success'),edge('export','exit','failure')]
mapping=seal({'schema_version':1,'id':'communication1167-post-supervisor-verification','version':1,'plan_version':1,'compiler_profile':profile['id'],'review':{'state':'reviewed','reference':{**origin['source_ref'],'scope':'User-authorized deterministic follow-up; engineering acceptance pending'}},'rules':[{'id':'post-supervisor-zero-model-verification','instance_ids':ids,'actions':actions}],'edges':edges,'loop_policies':[],'fan_groups':[],'support_files':support})
request={'schema_version':1,'inputs':{},'local_paths':{'output_root':'out','protected_roots':[]}}
for name,value in {'plan':plan,'execution_mapping':mapping,'compiler_profile':profile,'validator_profile':validator}.items():
 path='plan.json' if name=='plan' else name+'.yaml';f=D/path;f.write_text(json.dumps(value,indent=2)+'\n' if name=='plan' else yaml.safe_dump(value));request['inputs'][name]={'path':path,'sha256':sha(f),'semantic_digest':value['digest']}
(D/'compile.yaml').write_text(yaml.safe_dump(request));(D/'out').mkdir(exist_ok=True);pkg=compile_request(D/'compile.yaml',D/'out/package.json')
for name,body in pkg['files'].items():
 f=D/'workflow'/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(body)
nodeids={n['label']:n['id'] for n in pkg['manifest']['ir']['nodes'] if n['label'] in refs};write(D/'node-ids.json',nodeids)
f=D/'workflow/workflow.fabro';text=f.read_text()
for label,node in nodeids.items():
 if label.startswith('draft'):
  text='\n'.join(line.replace(' [',' [output_retries=0, fidelity="summary:high", ',1) if line.strip().startswith(node+' [') else line for line in text.splitlines())+'\n'
f.write_text(text)
f=D/'workflow/workflow.toml';f.write_text(f.read_text()+'''\n[run.model]\nprovider = "deepseek"\nname = "deepseek-v4-flash"\n[run.model.fallbacks]\ndeepseek-v4-flash = []\n[run.clone]\nenabled = false\n[run.run_branch]\nenabled = false\npush = false\n[run.agent]\nfabro_tools = false\n''')
write(D/'operational-overlay.json',{'reason':'Finite three-attempt DAG, bound host scripts and full most-recent packet in single-line command output; no repair retries/fallback models, tools or approvals','compiled_package_sha256':sha(D/'out/package.json'),'workflow_sha256':sha(D/'workflow/workflow.fabro'),'entrypoint_sha256':sha(f),'prompt_stages_max':0})
