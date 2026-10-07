# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,build_environment
p=Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/score/2850')
x=p/'integration-20261007/license-audit'; x.mkdir(exist_ok=False);(x/'evidence').mkdir()
r=Path(Path('/tmp/score-2850-integration-run-path').read_text());validate_run_root(r);env=dict(os.environ,**build_environment(r),PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONPATH',None)
native=r/'native'; tool=p/'native-adapter/evidence/tooling/copyright/cr_checker'; names=subprocess.check_output(['git','ls-files'],cwd=native,text=True).splitlines()
cmd=[sys.executable,'-B',str(tool/'tool/cr_checker.py'),'--template-file',str(tool/'resources/templates.ini'),'--config-file',str(tool/'resources/config.json'),*names]
start=time.time();result=subprocess.run(cmd,cwd=native,env=env,text=True,capture_output=True)
(x/'evidence/native-before.log').write_text(result.stdout+result.stderr)
(x/'evidence/native-before.json').write_text(json.dumps({'command':cmd,'exit_code':result.returncode,'duration_seconds':time.time()-start,'cwd':str(native),'tooling_commit':'31ff8eee214e4e97ef8f5cb46e443273515b63ec','subjects':{n:hashlib.sha256((native/n).read_bytes()).hexdigest() for n in names}},indent=2)+'\n')
print('Initial native header check',result.returncode);print(result.stdout+result.stderr)
