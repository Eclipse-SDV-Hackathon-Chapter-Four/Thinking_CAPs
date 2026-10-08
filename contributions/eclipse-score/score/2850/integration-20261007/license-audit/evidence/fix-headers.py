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
import ast,hashlib,io,json,shutil,subprocess,sys,tarfile
from pathlib import Path
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
p=Path('/home/jefferson/Thinking_CAPs/contributions/issues/eclipse-score/score/2850');a=p/'integration-20261007/license-audit';r=Path(Path('/tmp/score-2850-integration-run-path').read_text());validate_run_root(r);native=r/'native'
header=(p/'native-adapter/candidate/score_harness/harness/pinned_context_harness.py').read_text().split('\n\n',1)[0]+'\n\n'
nh=['.github/score/.copier-answers.yml','copier.yml','prepare_commit.sh','src/__init__.py','src/extensions/__init__.py','src/extensions/score_metamodel/checks/__init__.py']
helper=[]
for f in p.rglob('*.py'):
 n=f.relative_to(p)
 if n.parts[0]=='full-issue-fix-20261007' or 'candidate' in n.parts or 'tooling' in n.parts or 'native-guidance' in n.parts:continue
 if 'SPDX-License-Identifier:' not in f.read_text()[:2000]:helper.append(f)
items=[('native/'+n,native/n) for n in nh]+[('packet/'+f.relative_to(p).as_posix(),f) for f in sorted(helper)]
records=[]
with tarfile.open(a/'evidence/pre-header-files.tar.gz','w:gz') as t:
 for n,f in items:
  data=f.read_bytes();info=tarfile.TarInfo(n);info.size=len(data);info.mode=0o644;t.addfile(info,io.BytesIO(data))
 for f in [p/'native-adapter/evidence/source/binding.json',p/'native-adapter/evidence/patch-application.json',p/'native-adapter/patches/0001-score-2850-assurance-harness.patch',p/'native-adapter/manifest.json',p/'integration-20261007/decision.json',p/'integration-20261007/evidence/candidate-tree.json',p/'integration-20261007/evidence/binding-validation.json']:
  data=f.read_bytes();info=tarfile.TarInfo('prior-bindings/'+f.relative_to(p).as_posix());info.size=len(data);info.mode=0o644;t.addfile(info,io.BytesIO(data))
for n,f in items:
 before=f.read_text();first,sep,rest=before.partition('\n');after=first+'\n\n'+header+rest if before.startswith('#!') else header+before
 # Exact insertion proof: no original bytes removed, including shebang.
 if before.startswith('#!'):assert after==first+'\n\n'+header+rest
 else:assert after.removeprefix(header)==before
 if f.suffix=='.py':assert ast.dump(ast.parse(before),include_attributes=False)==ast.dump(ast.parse(after),include_attributes=False)
 f.write_text(after)
 records.append({'path':n,'before_sha256':hashlib.sha256(before.encode()).hexdigest(),'after_sha256':hashlib.sha256(after.encode()).hexdigest(),'change':'license comment insertion only','python_ast_unchanged':True if f.suffix=='.py' else None})
for n in nh:
 dest=p/'native-adapter/candidate'/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(native/n,dest)
subprocess.run(['git','add','--',*nh],cwd=native,check=True)
(a/'evidence/header-changes.json').write_text(json.dumps({'native_header_files':nh,'packet_helper_files':len(helper),'header':header,'changes':records,'prior_native_measurement':'retained; native source revision now differs only by the six declared license-comment insertions','originals_archive':'pre-header-files.tar.gz','originals_archive_sha256':hashlib.sha256((a/'evidence/pre-header-files.tar.gz').read_bytes()).hexdigest()},indent=2)+'\n')
shutil.copy2('/tmp/score-2850-header-audit.py',a/'evidence/audit-initial.py');shutil.copy2('/tmp/score-2850-fix-headers.py',a/'evidence/fix-headers.py')
print('Added native headers:',len(nh),'packet script headers:',len(helper))
