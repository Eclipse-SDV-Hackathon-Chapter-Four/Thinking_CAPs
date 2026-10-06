from pathlib import Path
import json,urllib.request,urllib.error,hashlib,base64,datetime
r=Path(__file__).parent
records=[]
def fetch(url,name):
 try:
  with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'score-rust-workflow'}),timeout=30) as response:data=response.read(64*1024*1024+1)
  assert len(data)<=64*1024*1024
  (r/name).write_bytes(data);records.append({'url':url,'status':200,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'artifact':name});return data
 except Exception as e:
  records.append({'url':url,'error_type':type(e).__name__,'error':str(e)});return None
try:
 raw=fetch('https://bcr.bazel.build/modules/download_utils/1.2.2/source.json','download-utils-source.json');assert raw
 meta=json.loads(raw);print(json.dumps(meta))
 algorithm,encoded=meta['integrity'].split('-',1);assert algorithm in {'sha256','sha512'};expected=base64.b64decode(encoded).hex();assert len(expected)==hashlib.new(algorithm).digest_size*2
 cache=r/'repository-cache'/'content_addressable'/algorithm/expected/'file'
 legacy=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha/bazel-output/cache/repos/v1/content_addressable')/algorithm/expected/'file'
 if not cache.exists() and legacy.exists():
  assert hashlib.new(algorithm,legacy.read_bytes()).hexdigest()==expected
  cache.parent.mkdir(parents=True,exist_ok=True);cache.write_bytes(legacy.read_bytes());records.append({'source':str(legacy),'algorithm':algorithm,'digest':expected,'status':'verified_immutable_legacy_payload'})
 print(json.dumps({'expected_archive_sha256':expected,'archive_already_seeded':cache.exists()}))
 if cache.exists():
  assert hashlib.new(algorithm,cache.read_bytes()).hexdigest()==expected
  data=cache.read_bytes();(r/'download-utils-1.2.2.tar.gz').write_bytes(data);records.append({'source':str(cache),'sha256':expected,'status':'hash_verified_cached_archive'})
 else:
  urls=[meta['url'],'https://mirror.bazel.build/'+meta['url'].split('://',1)[1]]
  for url in urls:
   data=fetch(url,'download-utils-1.2.2.tar.gz')
   if data and hashlib.new(algorithm,data).hexdigest()==expected:
    print(json.dumps({'archive_acquired':True,'sha256':expected,'bytes':len(data)}));break
   if data:records[-1]['refusal']='Exact pinned archive SHA256 mismatch';data=None
  else:data=None
 if data and hashlib.new(algorithm,data).hexdigest()==expected:records.append({'readiness':'exact_pinned_archive_acquired','sha256':expected})
finally:
 (r/'download-utils-acquisition.json').write_text(json.dumps({'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records},indent=2)+'\n')
 print(json.dumps({'records':records}))
