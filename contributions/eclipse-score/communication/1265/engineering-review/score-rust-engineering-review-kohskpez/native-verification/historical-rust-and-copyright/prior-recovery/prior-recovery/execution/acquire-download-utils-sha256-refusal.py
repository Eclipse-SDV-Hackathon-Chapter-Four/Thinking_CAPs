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
 expected=base64.b64decode(meta['integrity'].split('-',1)[1]).hex();assert meta['integrity'].startswith('sha256-')
 cache=r/'repository-cache'/'content_addressable'/'sha256'/expected/'file'
 print(json.dumps({'expected_archive_sha256':expected,'archive_already_seeded':cache.exists()}))
 if cache.exists():
  assert hashlib.sha256(cache.read_bytes()).hexdigest()==expected
  data=cache.read_bytes();(r/'download-utils-1.2.2.tar.gz').write_bytes(data);records.append({'source':str(cache),'sha256':expected,'status':'hash_verified_cached_archive'})
 else:
  urls=[meta['url'],'https://mirror.bazel.build/'+meta['url'].split('://',1)[1]]
  for url in urls:
   data=fetch(url,'download-utils-1.2.2.tar.gz')
   if data and hashlib.sha256(data).hexdigest()==expected:
    print(json.dumps({'archive_acquired':True,'sha256':expected,'bytes':len(data)}));break
   if data:records[-1]['refusal']='Exact pinned archive SHA256 mismatch';data=None
  else:data=None
 if data and hashlib.sha256(data).hexdigest()==expected:records.append({'readiness':'exact_pinned_archive_acquired','sha256':expected})
finally:
 (r/'download-utils-acquisition.json').write_text(json.dumps({'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'records':records},indent=2)+'\n')
 print(json.dumps({'records':records}))
