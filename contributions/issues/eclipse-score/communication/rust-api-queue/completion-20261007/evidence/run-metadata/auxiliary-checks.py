# Copyright (c) 2026 Eclipse SDV Hackathon Team
#
# Licensed under the Apache License, Version 2.0.
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path
import subprocess,json,hashlib,datetime,os,signal,time,shutil,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from storage import validate_run_root
validate_run_root(ROOT)
row=json.loads((ROOT/'resolved-ownership-regression/native-result.json').read_text())['checks'][0]
from_index=next(i for i,arg in enumerate(row['command']) if arg.endswith('/tools/bazel'))
namespace=row['command'][:from_index]
startup=row['command'][from_index:from_index+3]
env=row['environment']
output=ROOT/'auxiliary-evidence'; output.mkdir(exist_ok=True)
results=[]
def run(name,args,nested=False):
 validate_run_root(ROOT)
 prefix=list(namespace)
 if nested: prefix[-1]=str(ROOT/'workspaces/integrated/module_integration_test')
 command=prefix+startup+args
 log=output/(name+'.log'); started=time.monotonic()
 with log.open('wb') as stream:
  process=subprocess.Popen(command,env=env,stdin=subprocess.DEVNULL,stdout=stream,stderr=subprocess.STDOUT,start_new_session=True)
  while process.poll() is None:
   validate_run_root(ROOT)
   if shutil.disk_usage(ROOT).free < 2*1024**3:
    os.killpg(process.pid,signal.SIGTERM); process.wait(); break
   time.sleep(.5)
 result={'name':name,'command':command,'environment':env,'exit_code':process.wait(),'elapsed_seconds':round(time.monotonic()-started,3),'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
 results.append(result); (output/'results.json').write_text(json.dumps(results,indent=2)+'\n'); print(name,result['exit_code'],flush=True)
 return result['exit_code']
external=next((ROOT/'bazel-output').glob('*/external'))
identities=[]
for pattern,arguments in [('*ferrocene*/bin/rustc',['--version','--verbose']), ('*ferrocene*/bin/clippy-driver',['--version']), ('gcc_toolchain*/bin/gcc',['--version']), ('toolchains_llvm++llvm+llvm_toolchain_llvm/bin/clang',['--version'])]:
 for tool in external.glob(pattern):
  if not tool.is_file(): continue
  command=namespace+[str(tool),*arguments]
  measured=subprocess.run(command,env=env,stdin=subprocess.DEVNULL,capture_output=True,text=True)
  identities.append({'tool':str(tool),'sha256':hashlib.sha256(tool.read_bytes()).hexdigest(),'command':command,'exit_code':measured.returncode,'stdout':measured.stdout,'stderr':measured.stderr,'qualification':'unknown for adopted version/target/use'})
policy=external/'score_rust_policies+'
for name in ['MODULE.bazel','clippy/strict/clippy.toml','clippy/linters.bzl']:
 tool=policy/name
 if tool.is_file():
  retained=output/'native-policy'/name; retained.parent.mkdir(parents=True,exist_ok=True); retained.write_bytes(tool.read_bytes())
  identities.append({'policy_file':name,'sha256':hashlib.sha256(tool.read_bytes()).hexdigest()})
(output/'native-tool-identities.json').write_text(json.dumps(identities,indent=2)+'\n')
run('resolved-module-graph',['mod','graph'])
run('test-inventory',['query','--output=xml','kind(".*_test rule", //...)'])
run('manual-inventory',['query','--output=label_kind','attr("tags", "manual", //...)'])
plan=json.loads((ROOT/'cfg-test-clippy-plan.json').read_text())['checks'][0]
run('test-clippy-actions',['aquery','--config=linux_x64','--output=jsonproto','--include_commandline',*plan['flags'], 'mnemonic("Clippy", set('+ ' '.join(plan['targets'])+'))'])
# Record actual compiler actions instead of inferring Rust instrumentation from a CI job name.
sanitizer_targets=plan['targets']+['//score/mw/com/impl/rust/com-api/com-api-ffi-lola:callback_ownership_test','//score/mw/com/test/basic_rust_api/subscription_state_apis:subscription-state-apis-tests']
for config in ['asan_ubsan_lsan','tsan']:
 run('sanitizer-actions-'+config,['aquery','--config=linux_x64','--config=ci','--config='+config,'--output=jsonproto','--include_commandline','set('+' '.join(sanitizer_targets)+')'])
lock=ROOT/'workspaces/integrated/module_integration_test/MODULE.bazel.lock'; before=lock.read_bytes()
try:
 run('module-build',['build','--repository_cache='+str(ROOT/'repository-cache'),'--jobs=6','//...'],nested=True)
 run('module-dependencies',['mod','deps','--repository_cache='+str(ROOT/'repository-cache'),'--lockfile_mode=update'],nested=True)
 (output/'module-lock-after.json').write_bytes(lock.read_bytes())
finally:
 lock.write_bytes(before)
 (output/'module-lock-before.json').write_bytes(before)
validate_run_root(ROOT)
(output/'completed.json').write_text(json.dumps({'completed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_patch_sha256':hashlib.sha256((ROOT/'resolved-candidate.patch').read_bytes()).hexdigest()},indent=2)+'\n')
