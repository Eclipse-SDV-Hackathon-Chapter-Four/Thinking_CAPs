# Copyright (c) 2026 Contributors to the Eclipse Foundation
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Human review pending.
# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Assisted-by: OpenAI Codex (model revision unavailable); human review pending.
import hashlib, json, os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
repo=Path(__file__).resolve().parents[1];root=repo.parent;task=repo/'.llm_tmp';out=task/'evidence';out.mkdir(exist_ok=True)
old=Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-someip84-compliance-959u7rde')
validate_run_root(root);validate_run_root(old)
custom=json.loads((task/'environment.json').read_text());env=os.environ.copy();env.update({k:v for k,v in custom.items() if k!='PATH_PREFIX'});env['PATH']=str(task/'bin')+':'+custom['PATH_PREFIX']+':'+env['PATH']
def hashes():
    names=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard'],cwd=repo,text=True).splitlines()
    return {p:hashlib.sha256((repo/p).read_bytes()).hexdigest() for p in names if (repo/p).is_file() and not p.startswith('.llm_tmp/')}
name=sys.argv[1];argv=sys.argv[2:]
if argv[0]=='bazel':
    argv=[str(task/'bin/bazel'),'--batch',*argv[1:]]
    position=argv.index('--') if '--' in argv else len(argv)
    argv.insert(position,'--repository_cache='+str(old/'bazel-output/cache/repos/v1'))
start=time.time();before=hashes()
with (out/(name+'.stdout')).open('w') as so,(out/(name+'.stderr')).open('w') as se:
    result=subprocess.run(argv,cwd=repo,env=env,stdout=so,stderr=se)
record={'command':argv,'cwd':str(repo),'exit_code':result.returncode,'elapsed_seconds':time.time()-start,'source_hashes_before':before,'source_hashes_after':hashes(),'environment':custom}
(out/(name+'.json')).write_text(json.dumps(record,indent=2)+'\n')
print(name,result.returncode,round(record['elapsed_seconds'],1),flush=True)
print((out/(name+'.stderr')).read_text()[-6500:])
sys.exit(result.returncode)
