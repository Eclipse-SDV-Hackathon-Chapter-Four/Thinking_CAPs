from pathlib import Path
import ast,hashlib,json,sys,subprocess
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r)
out=Path(json.loads((r/'contribution.json').read_text())['path']);ledger=json.loads((out/'correction-ledger.json').read_text());assert ledger['corrections_used']==2
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
previous=json.loads((r/'run-binding-copyright.json').read_text())
for name,want in previous['files'].items():assert h(r/name)==want,name
wrapper=r/'copyright-label-wrapper.sh';wrapper.chmod(0o755);p=subprocess.run(['/bin/bash','-n',str(wrapper)],capture_output=True,text=True);assert p.returncode==0,p.stderr
s=(r/'collector-copyright.py').read_text().replace("ATTEMPT=ROOT/'copyright-recovery'","ATTEMPT=ROOT/'copyright3-recovery'").replace("ROOT/'run-binding-copyright.json'","ROOT/'run-binding-copyright3.json'").replace("'native-copyright-correction2'","'native-copyright-correction3'").replace("'corrections_used':2","'corrections_used':3")
needle="'--curses=no','//:copyright.check']";assert s.count(needle)==1;s=s.replace(needle,"'--curses=no','--run_under='+str(ROOT/'copyright-label-wrapper.sh'),'//:copyright.check']")
s=s.replace("'native_copyright_Markdown_coverage':'excluded_by_native_templates'","'native_copyright_Markdown_coverage':'excluded_by_native_templates','native_invocation_workaround':'resolve //:BUILD and //:MODULE.bazel to workspace-relative pathspecs; original target failures preserved'")
(r/'collector-copyright3.py').write_text(s);ast.parse(s)
s=(r/'run-copyright.py').read_text().replace("attempt=r/'copyright-recovery'","attempt=r/'copyright3-recovery'").replace("'communication1265_copyright2'","'communication1265_copyright3'").replace('Communication #1265: copyright prerequisite recovery','Communication #1265: copyright pathspec normalization');(r/'run-copyright3.py').write_text(s);ast.parse(s)
trial=r/'copyright3-recovery';trial.mkdir()
graph=(r/'copyright-recovery/workflow.fabro').read_text().replace('/collector-copyright.py ','/collector-copyright3.py ');(trial/'workflow.fabro').write_text(graph);(trial/'workflow.toml').write_text((r/'workflow.toml').read_text())
(trial/'workflow-version.json').write_text(json.dumps({'entrypoint':'workflow.fabro','files':{'workflow.fabro':graph,'workflow.toml':(trial/'workflow.toml').read_text()},'workflow_dependencies':{}},indent=2)+'\n')
ledger['corrections_used']=3;ledger['status']='ready_final_copyright_workaround_run';ledger['entries'].append({'correction':3,'failure':'Nativechecker forwards //:BUILD and //:MODULE.bazel literalBazel label strings into gitls-files; gitrefuses //:BUILD outsideworkspace.','fix':'Bazel8.7 source-supported run_under argument wrapper resolves exacttwo rootlabels to BUILD andMODULE.bazel, retaining checker/template/config and allscope paths; no native source/policychange; original target failures preserved.','remaining_corrections':0});(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
b={**previous,'files':dict(previous['files']),'corrections_used_before_execution':3,'fresh_check_scope':'native checker with explicitly documented argument normalization; default target failure preserved'}
for name in ['collector-copyright3.py','run-copyright3.py','copyright-label-wrapper.sh','copyright3-recovery/workflow.fabro','copyright3-recovery/workflow.toml','copyright3-recovery/workflow-version.json','copyright-recovery/verification-results.json','copyright-recovery/run-final.json','logs/native-copyright-correction2.log','documentation-license-inspection.json']:
 b['files'][name]=h(r/name)
b['external_tools']={'/bin/bash':h(Path('/bin/bash'))};b['wrapper_mode']=0o755
(r/'run-binding-copyright3.json').write_text(json.dumps(b,indent=2)+'\n');validate_run_root(r)
print(json.dumps({'binding_sha256':h(r/'run-binding-copyright3.json'),'files':len(b['files']),'corrections_used':3,'remaining':0}))
