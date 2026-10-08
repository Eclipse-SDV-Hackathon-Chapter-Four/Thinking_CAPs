from pathlib import Path
import json,shutil,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r)
c=Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/issues/eclipse-score/communication/1265');f=c/'failures'/'fabro-registration';f.mkdir(parents=True,exist_ok=True)
for name in ['workflow-version.json','run-binding.json','server-binding.json','server-shutdown.json','collector.py']:
 shutil.copyfile(r/name,f/name)
(f/'failure.json').write_text(json.dumps({'request':'POST /api/v1/workflow-versions','http_status':422,'run_created':False,'response_body':'not retained; preserve missing diagnostic','source_diagnosis':'Native WorkflowVersion entrypoint denotes graph; supplied workflow.toml disagrees with its workflow.graph=workflow.fabro. fabro-workflow-version/src/lib.rs validates graph closure and graph selection.'},indent=2)+'\n')
p=r/'prepare_run.py';p.write_text(p.read_text().replace("'entrypoint':'workflow.toml'","'entrypoint':'workflow.fabro'"))
p=r/'collector.py';text=p.read_text().replace("'corrections_used':2","'corrections_used':json.loads(Path(binding['correction_ledger']).read_text())['corrections_used']").replace("return 0 if result['exit_code']==0 else 1","return 0 if all(c['status']=='passed' for c in checks if 'exit_code' in c) else 1").replace("'checks_complete':True","'check_inventory_export_complete':True")
p.write_text(text)
ledger=json.loads((c/'correction-ledger.json').read_text());assert ledger['corrections_used']==2
ledger['corrections_used']=3;ledger['entries'].append({'phase':'native_registration','initial_failure':'HTTP422 registering workflow.toml as native wire graph entrypoint; no run created','correction':3,'fix':'Use workflow.fabro as graph entrypoint according to pinned native validator; retain rejected wire and diagnostic gap. Include supervisor review refinements before resealing.','remaining_corrections':0});ledger['native_registration_failures']=1
(c/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
print('Correction3 recorded; no further corrective attempts authorized.')
