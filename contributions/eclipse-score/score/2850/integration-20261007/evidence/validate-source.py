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

import hashlib,json,os,subprocess,sys
from pathlib import Path
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,build_environment
p=Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/score/2850')
e=p/'integration-20261007/evidence'; root=Path(Path('/tmp/score-2850-integration-run-path').read_text()); validate_run_root(root)
native=root/'native'; env=dict(os.environ,**build_environment(root)); records=[]
def run(args):
 validate_run_root(root); r=subprocess.run(args,cwd=native,env=env,text=True,capture_output=True); records.append({'command':args,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr}); assert r.returncode==0,r.stderr; return r.stdout.strip()
b=json.loads((p/'native-adapter/evidence/source/binding.json').read_text()); selected=json.loads((e/'candidate-tree.json').read_text())
expected={Path(n).relative_to(Path(n).parts[0]).as_posix():h for n,h in b['archive_files'].items()}; expected.update(b['changed_files'])
names=run(['git','ls-files']).splitlines(); assert set(names)==set(expected)
actual={n:hashlib.sha256((native/n).read_bytes()).hexdigest() for n in names}; assert actual==expected
assert {n:actual[n] for n in b['unchanged_contracts']} == b['unchanged_contracts']
assert not run(['git','diff','--name-only']); assert run(['git','write-tree'])==selected['tree']; assert run(['git','rev-parse','HEAD'])==b['commit']; assert run(['git','branch','--show-current'])==selected['branch']
(e/'binding-validation.json').write_text(json.dumps({'verified':True,'all_native_tracked_files':len(names),'tracked_file_sha256':actual,'fixed_contracts':b['unchanged_contracts'],'unchanged_contracts_match':True,'all_measured_source_files_match':True,'no_unstaged_tracked_changes':True,'commands':records,'runtime_tests_rerun':False,'engineering_acceptance':'pending'},indent=2)+'\n')
print('Full native source identity verified:',len(names),'tracked files;',len(b['unchanged_contracts']),'fixed contracts')
