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
import ast,hashlib,json,os,shutil,subprocess,sys,time
from pathlib import Path
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root,build_environment
p=Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/score/2850');a=p/'integration-20261007/license-audit';r=Path(Path('/tmp/score-2850-integration-run-path').read_text());validate_run_root(r);native=r/'native';tool=p/'native-adapter/evidence/tooling/copyright/cr_checker';env=dict(os.environ,**build_environment(r),PYTHONDONTWRITEBYTECODE='1');env.pop('PYTHONPATH',None)
shutil.copy2(__file__,a/'evidence/final-header-check.py')
names=subprocess.check_output(['git','ls-files'],cwd=native,text=True).splitlines(); cmds=[]
def run(label,args,cwd):
 validate_run_root(r);start=time.time();s=subprocess.run(args,cwd=cwd,env=env,text=True,capture_output=True);(a/'evidence'/f'{label}.log').write_text(s.stdout+s.stderr);cmds.append({'name':label,'command':args,'cwd':str(cwd),'exit_code':s.returncode,'duration_seconds':time.time()-start});print(label,s.returncode,flush=True);assert s.returncode==0,s.stdout+s.stderr
base=[sys.executable,'-B',str(tool/'tool/cr_checker.py'),'--template-file',str(tool/'resources/templates.ini'),'--config-file',str(tool/'resources/config.json')]
run('native-after',base+names,native)
helpers=[]
for f in sorted(p.rglob('*.py')):
 n=f.relative_to(p)
 if n.parts[0]=='full-issue-fix-20261007' or 'candidate' in n.parts or 'tooling' in n.parts or 'native-guidance' in n.parts:continue
 helpers.append(f)
run('packet-scripts-after',base+[str(f) for f in helpers],p)
run('shell-syntax',['bash','-n','prepare_commit.sh'],native)
run('patch-whitespace',['git','diff','--cached','--check'],native)
parsed=[]
for n in names:
 f=native/n
 if f.suffix=='.py':ast.parse(f.read_text());parsed.append(n)
# The YAML content is byte-identical once the inserted native header is removed.
changes=json.loads((a/'evidence/header-changes.json').read_text());h=changes['header'];before_by_name={x['path']:x for x in changes['changes']}
for n in changes['native_header_files']:
 s=(native/n).read_text()
 if s.startswith('#!'):
  first,_,rest=s.partition('\n');original=first+'\n'+rest.removeprefix('\n'+h)
 else:original=s.removeprefix(before_by_name['native/'+n].get('inserted_header',h))
 assert hashlib.sha256(original.encode()).hexdigest()==before_by_name['native/'+n]['before_sha256']
 assert hashlib.sha256(s.encode()).hexdigest()==before_by_name['native/'+n]['after_sha256']
exts={'cpp','c','h','hpp','py','sh','bzl','ini','yml','yaml','BUILD','bazel','rst','rs'}
supported=[n for n in names if Path(n).suffix[1:] in exts or Path(n).name=='BUILD'];unsupported=[n for n in names if n not in supported]
(a/'evidence/checks.json').write_text(json.dumps({'tooling_commit':'31ff8eee214e4e97ef8f5cb46e443273515b63ec','checker_sha256':hashlib.sha256((tool/'tool/cr_checker.py').read_bytes()).hexdigest(),'template_sha256':hashlib.sha256((tool/'resources/templates.ini').read_bytes()).hexdigest(),'config_sha256':hashlib.sha256((tool/'resources/config.json').read_bytes()).hexdigest(),'commands':cmds,'native_tracked_files':len(names),'native_supported_files':supported,'native_without_template':unsupported,'packet_python_files':[f.relative_to(p).as_posix() for f in helpers],'native_python_ast_parsed':parsed,'exact_comment_insertion_verified':True,'native_runtime_tests_rerun':False,'subject_sha256':{n:hashlib.sha256((native/n).read_bytes()).hexdigest() for n in names},'packet_subject_sha256':{f.relative_to(p).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in helpers}},indent=2)+'\n')
print('Licensed native files:',len(supported),'packet scripts:',len(helpers),'Python syntax:',len(parsed))
