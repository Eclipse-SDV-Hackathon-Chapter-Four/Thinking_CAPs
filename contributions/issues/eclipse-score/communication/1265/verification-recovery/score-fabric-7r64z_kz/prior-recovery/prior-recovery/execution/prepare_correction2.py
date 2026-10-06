from pathlib import Path
import hashlib,json,shutil,base64,re,tarfile,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r);out=Path(json.loads((r/'contribution.json').read_text())['path'])
trial=r/'correction2';trial.mkdir()
source=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha/bazel-output/cache/repos/v1/content_addressable/sha512')
assert source.stat().st_dev==r.stat().st_dev
files=[]
for payload in source.glob('*/file'):
 assert re.fullmatch('[0-9a-f]{128}',payload.parent.name)
 with payload.open('rb') as f:actual=hashlib.file_digest(f,'sha512').hexdigest()
 assert actual==payload.parent.name,str(payload)
 dest=r/'repository-cache'/'content_addressable'/'sha512'/actual/'file';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(payload,dest)
 markers=[]
 for marker in payload.parent.glob('id-*'):
  assert re.fullmatch('id-[0-9a-f]{64}',marker.name) and marker.is_file() and marker.stat().st_size==0
  shutil.copyfile(marker,dest.parent/marker.name);markers.append(marker.name)
 files.append({'source':str(payload),'destination':str(dest),'bytes':payload.stat().st_size,'hash_algorithm':'sha512','digest':actual,'public_native_cache_markers':markers})
meta=json.loads((r/'download-utils-source.json').read_text());expected=base64.b64decode(meta['integrity'].split('-',1)[1]).hex()
assert any(x['digest']==expected for x in files)
with tarfile.open(r/'download-utils-1.2.2.tar.gz','r:gz') as archive:
 names=archive.getnames()
 assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
 licenses={}
 for member in archive:
  if member.isfile() and member.name.rsplit('/',1)[-1].upper() in {'LICENSE','LICENSE.TXT','COPYING','NOTICE'}:
   data=archive.extractfile(member).read();p=out/'sources'/'download_utils'/member.name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);licenses[member.name]=hashlib.sha256(data).hexdigest()
(r/'sha512-cache-seed.json').write_text(json.dumps({'kind':'verified_immutable_public_cache_payload_copy','algorithm':'sha512','files':files,'count':len(files),'exact_missing_module_SRI':meta,'source_volume_verified':True,'queues_or_private_state_migrated':False,'notices':licenses},indent=2)+'\n')
# Preserve all old programs/configs; new attempt has named programs and output namespace.
p=r/'collector-correction2.py';s=(r/'collector.py').read_text().replace('ROOT=Path(__file__).parent','ROOT=Path(__file__).parent\nATTEMPT=ROOT/"correction2"')
s=s.replace('(ROOT/name).write_text','(ATTEMPT/name).write_text').replace("ROOT/'run-binding.json'","ROOT/'run-binding-correction2.json'").replace("ROOT/'logs'", "ATTEMPT/'logs'")
s=s.replace("ROOT/'verification-results.json'","ATTEMPT/'verification-results.json'")
p.write_text(s)
p=r/'run-native-correction2.py';s=(r/'run_native.py').read_text().replace("private=private_server_root(r,'communication1265_recovery')", "attempt=r/'correction2'\nprivate=private_server_root(r,'communication1265_correction2')")
s=s.replace('(r/name).write_text','(attempt/name).write_text')
for name in ['run-intent.json','workflow-version.json','fabro-wait.log','verification-results.json']:
 s=s.replace("r/'"+name+"'","attempt/'"+name+"'")
s=s.replace('Communication #1265: supervised verification recovery','Communication #1265: verified SHA512 cache correction')
p.write_text(s)
graph=(r/'workflow.fabro').read_text().replace('/collector.py ', '/collector-correction2.py ')
(trial/'workflow.fabro').write_text(graph);(trial/'workflow.toml').write_text((r/'workflow.toml').read_text())
(trial/'workflow-version.json').write_text(json.dumps({'entrypoint':'workflow.fabro','files':{'workflow.fabro':graph,'workflow.toml':(trial/'workflow.toml').read_text()},'workflow_dependencies':{}},indent=2)+'\n')
ledger=json.loads((out/'correction-ledger.json').read_text());assert ledger['corrections_used']==1
ledger['corrections_used']=2;ledger['entries'].append({'correction':2,'phase':'native_dependency_materialization','failure':'Native analysis failed fetching download_utils1.2.2 from GitLab with HTTP502. Initial cache seeding omitted SHA512 namespace.','fix':'Verify public legacy SHA512 payloads and canonical-ID markers; seed owned cache without changing source/locks, native version or checksum.','verified_payloads':len(files),'remaining_corrections':1})
(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
files=['collector-correction2.py','run-native-correction2.py','correction2/workflow.fabro','correction2/workflow.toml','correction2/workflow-version.json','controls.json','candidate-hashes.json','baseline-hashes.json','tools/bazel','fabro-source-bindings.json','worker-preflight.json','tooling-bindings.json','sha512-cache-seed.json','download-utils-source.json','download-utils-1.2.2.tar.gz']
binding=json.loads((r/'run-binding.json').read_text());binding['files']={name:h(r/name) for name in files};binding['corrections_used_before_execution']=2;binding['prior_run']='01M47SYF7DSPAQDMTYWVD31Q40';binding['correction_subject']='immutable native SHA512 cache completeness; production source/locks unchanged'
(r/'run-binding-correction2.json').write_text(json.dumps(binding,indent=2)+'\n')
for name in ['download-utils-source.json','download-utils-1.2.2.tar.gz','download-utils-acquisition.json','sha512-cache-seed.json','acquire-download-utils-sha256-refusal.py','acquire_download_utils.py','prepare_correction2.py']:
 dest=out/'sources'/'dependency-correction'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/name,dest)
print(json.dumps({'verified_sha512_payloads':len(files) if False else len(json.loads((r/'sha512-cache-seed.json').read_text())['files']),'native_correction':2,'remaining_corrections':1,'new_bound_files':len(binding['files'])}))
