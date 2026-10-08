import json,os,sys,subprocess,time,hashlib,shutil
from pathlib import Path
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,build_environment
root=Path(__file__).parent
validate_run_root(root)
issue,op,label,*targets=sys.argv[1:]
w=root/'workspaces'/issue
out=root/'evidence'/issue/label
out.mkdir(parents=True,exist_ok=True)
tools=json.loads((root/'linux-tools.json').read_text())
overlays=json.loads((root/'runtime-overlays.json').read_text())['overlays']
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert sha(tools['bazel']['path'])==tools['bazel']['sha256']
namespace=['/usr/bin/bwrap','--die-with-parent','--ro-bind','/','/','--bind',str(root),str(root),'--tmpfs','/home/jefferson','--tmpfs','/tmp','--dir','/tmp/build-home','--proc','/proc','--dev-bind','/dev','/dev']
for row in overlays:
 assert sha(row['source'])==row['source_sha256']
 namespace+=['--ro-bind',row['source'],row['target']]
namespace+=['--chdir',str(w)]
config='clippy' if op=='lint' else 'linux_x64'
cmd=[tools['bazel']['path'],'--batch','--output_user_root='+str(root/'bazel-output'/issue),'build' if op=='lint' else op,'--repository_cache='+str(root/'repository-cache'),'--color=no','--curses=no','--config='+config,'--jobs=4']
if op=='test':cmd+=['--cache_test_results=no','--test_output=errors','--build_event_json_file='+str(out/'events.jsonl')]
cmd+=targets
command=namespace+cmd
env={'PATH':'/usr/sbin:/usr/bin:/sbin:/bin','LANG':'C.UTF-8','HOME':'/tmp/build-home',**build_environment(root)}
source={p.relative_to(w).as_posix():sha(p) for p in w.rglob('*') if p.is_file() and '.git' not in p.parts and not any(s.startswith('bazel-') for s in p.relative_to(w).parts)}
(out/'source-hashes.json').write_text(json.dumps(source,sort_keys=True,indent=2)+'\n')
start=time.monotonic()
with (out/'command.log').open('wb') as log:
 p=subprocess.Popen(command,env=env,stdout=log,stderr=subprocess.STDOUT)
 while p.poll() is None:
  validate_run_root(root);time.sleep(1)
result={'command':command,'environment':env,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-start,'log_sha256':sha(out/'command.log'),'source_hashes_sha256':sha(out/'source-hashes.json'), 'source_drift_paths':[rel for rel,h in source.items() if not (w/rel).exists() or sha(w/rel)!=h]}
(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if op=='test':
 for f in (w/'bazel-testlogs').rglob('test.xml'):
  d=out/'testlogs'/f.relative_to(w/'bazel-testlogs');d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,d)
  if f.with_name('test.log').exists():shutil.copyfile(f.with_name('test.log'),d.with_name('test.log'))
print(json.dumps({'issue':issue,'label':label,'exit_code':p.returncode,'elapsed':result['elapsed_seconds']}))
print((out/'command.log').read_text()[-4000:])
sys.exit(p.returncode)
