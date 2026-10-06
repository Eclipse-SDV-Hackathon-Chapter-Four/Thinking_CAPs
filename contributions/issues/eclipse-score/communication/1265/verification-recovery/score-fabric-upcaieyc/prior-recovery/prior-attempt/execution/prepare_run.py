from pathlib import Path
import hashlib,json,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r)
python='/home/jefferson/s-core_sw_fabric/.venv/bin/python'
def q(s):return json.dumps(s)
graph='digraph communication1265 {\n graph [goal="Measure documentation assessment against pinned native baseline", on_failure="route"];\n start [type="start"];\n verify [type="command", script='+q(f'{python} {r}/collector.py verify')+', max_retries=0, timeout="21m"];\n export [type="command", script='+q(f'{python} {r}/collector.py export')+', max_retries=0, timeout="1m"];\n exit [type="exit"];\n start -> verify;\n verify -> export [condition="outcome=failed"];\n verify -> export;\n export -> exit;\n}\n'
(r/'workflow.fabro').write_text(graph)
config=f'''_version = 1
[workflow]
graph = "workflow.fabro"
[run]
goal = "Export scoped communication issue 1265 assessment with measured checks and preserved gaps"
working_dir = "{r}/candidate"
[run.clone]
enabled = false
[run.run_branch]
enabled = false
push = false
[run.agent]
fabro_tools = false
'''
(r/'workflow.toml').write_text(config)
wire={'entrypoint':'workflow.fabro','files':{'workflow.fabro':graph,'workflow.toml':config},'workflow_dependencies':{}}
(r/'workflow-version.json').write_text(json.dumps(wire,indent=2)+'\n')
files=['collector.py','workflow.fabro','workflow.toml','workflow-version.json','controls.json','candidate-hashes.json','baseline-hashes.json','tools/bazel','fabro-source-bindings.json']
binding={'files':{n:hashlib.sha256((r/n).read_bytes()).hexdigest() for n in files},'patch_sha256':json.loads((r/'controls.json').read_text())['patch_sha256'],'correction_ledger':'/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265/correction-ledger.json','max_corrections':3,'corrections_used_before_execution':2,'supervisor':'/root/rust_issue_supervisor','paid_calls_authorized':False,'hooks':'none; archive snapshot has no Git hook directory','native_lockfile_mode':'error','native_configuration':'baseline default linux_x64_gcc_15 with registered Ferrocene','no_human_nodes':True}
(r/'run-binding.json').write_text(json.dumps(binding,indent=2)+'\n')
print('Frozen collector, command-only graph and run binding prepared.')
