from pathlib import Path
import hashlib,json,shutil,stat,tarfile,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r)
out=Path(json.loads((r/'contribution.json').read_text())['path']);ledger=json.loads((out/'correction-ledger.json').read_text());assert ledger['corrections_used']==0
shutil.copyfile(r/'compatibility-preflight.json',r/'compatibility-preflight-mode-refusal.json');shutil.copyfile(r/'preflight_compatible.py',r/'preflight-mode-refusal.py')
rows=json.loads((r/'runtime-overlays.json').read_text());byname={x['archive_member']:x for x in rows['overlays']};restored=[]
with tarfile.open(r/'runtime-provenance/ubuntu-noble-oci-amd64-root.tar.gz') as archive:
 for member in archive:
  if member.name in byname:
   assert member.isfile() and not member.mode & 0o7000
   row=byname[member.name];p=Path(row['source']);before=stat.S_IMODE(p.stat().st_mode);p.chmod(member.mode & 0o777);row['mode']=member.mode & 0o777;restored.append({'path':row['source'],'before':before,'after':row['mode'],'archive_member':member.name})
assert len(restored)==13
(r/'runtime-overlays.json').write_text(json.dumps(rows,indent=2)+'\n')
ledger['corrections_used']=1;ledger['entries'].append({'correction':1,'failure':'Directnamespacegetconfpreflight exec Permissiondenied; library extractor omitted archivefile modes, making ELFloader nonexecutable.','fix':'Restore exact13regular library modes from verified Canonical archive and validate modes/hosthashes at bind.','remaining_corrections':2});(out/'correction-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
(r/'runtime-mode-correction.json').write_text(json.dumps({'restored':restored,'source_bytes_changed':False,'host_mode_changes':False,'correction':1},indent=2)+'\n')
p=r/'collector.py';s=p.read_text();needle=' for name,expected in json.loads((ROOT/\'candidate-hashes.json\').read_text()).items():';assert s.count(needle)==1
s=s.replace(needle," for row in json.loads((ROOT/'runtime-overlays.json').read_text())['overlays']:\n  assert (Path(row['source']).stat().st_mode & 0o777)==row['mode'],'Runtime mode drift'\n  assert digest(Path(row['target']))==row['host_original_sha256'],'Host library drift'\n"+needle);p.write_text(s)
p=r/'preflight_compatible.py';s=p.read_text().replace("'compatibility-glibc'","'compatibility2-glibc'").replace("'compatibility-ferrocene'","'compatibility2-ferrocene'").replace("'compatibility-bazel'","'compatibility2-bazel'").replace('logs/compatibility-ferrocene.log','logs/compatibility2-ferrocene.log').replace('logs/compatibility-glibc.log','logs/compatibility2-glibc.log').replace("'corrections_used':0","'corrections_used':1");p.write_text(s)
b=json.loads((r/'run-binding.json').read_text());b['corrections_used_before_execution']=1
for name in ['collector.py','runtime-overlays.json','runtime-mode-correction.json']:
 with (r/name).open('rb') as f:b['files'][name]=hashlib.file_digest(f,'sha256').hexdigest()
(r/'run-binding.json').write_text(json.dumps(b,indent=2)+'\n');validate_run_root(r)
print('Correction1 applied: exact archive modes restored; two remaining.')
