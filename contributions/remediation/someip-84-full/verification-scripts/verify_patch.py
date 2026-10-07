# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: Generated with OpenAI Codex; AI portions offered under CC0-1.0.
# Assisted-by: OpenAI Codex (model revision unavailable); human review pending.
from pathlib import Path
import hashlib,json,subprocess,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
repo=Path(__file__).resolve().parents[1];validate_run_root(repo.parent);task=repo/'.llm_tmp'
baseline=json.loads((task/'baseline.json').read_text())['commit']
def run(args,cwd=repo):return subprocess.check_output(args,cwd=cwd,stderr=subprocess.STDOUT)
plain=run(['git','diff','--binary','--full-index',baseline,'HEAD']);mail=run(['git','format-patch','-1','--stdout','--no-signature'])
(task/'full-submission.patch').write_bytes(plain);(task/'full-submission-with-dco.patch').write_bytes(mail)
clone=task/'apply-check'
if clone.exists():raise SystemExit('Apply-check path already exists; do not overwrite')
log=[]
def logged(args,cwd=repo):
 out=run(args,cwd);log.append({'command':args,'cwd':str(cwd),'output':out.decode()});return out
logged(['git','clone','--no-hardlinks','--no-checkout',str(repo),str(clone)])
logged(['git','checkout','--detach',baseline],clone)
logged(['git','apply','--check',str(task/'full-submission.patch')],clone)
logged(['git','-c','user.name=Jefferson Nascimento','-c','user.email=jnsagai@gmail.com','am',str(task/'full-submission-with-dco.patch')],clone)
assert run(['git','diff','--binary','--full-index',baseline,'HEAD'],clone)==plain
assert run(['git','rev-parse','HEAD^{tree}'],clone)==run(['git','rev-parse','HEAD^{tree}'])
files=run(['git','ls-files']).decode().splitlines();hashes={}
for name in files:
 data=(repo/name).read_bytes();assert (clone/name).read_bytes()==data;hashes[name]=hashlib.sha256(data).hexdigest()
assert not run(['git','status','--porcelain'],clone).strip()
record={'baseline':baseline,'prepared_native_commit':run(['git','rev-parse','HEAD']).decode().strip(),'prepared_tree':run(['git','rev-parse','HEAD^{tree}']).decode().strip(),'applied_commit':run(['git','rev-parse','HEAD'],clone).decode().strip(),'plain_patch_sha256':hashlib.sha256(plain).hexdigest(),'mail_patch_sha256':hashlib.sha256(mail).hexdigest(),'plain_patch_applies':True,'mail_patch_diff_identical':True,'all_candidate_sources_match':True,'source_file_count':len(hashes),'source_hashes':hashes,'applied_author':run(['git','show','-s','--format=%an <%ae>'],clone).decode().strip(),'applied_committer':run(['git','show','-s','--format=%cn <%ce>'],clone).decode().strip(),'applied_commit_message':run(['git','show','-s','--format=%B'],clone).decode(),'commands':log,'acceptance':'Hash/apply verification only; not human review or upstream acceptance'}
(task/'evidence/patch-verification.json').write_text(json.dumps(record,indent=2)+'\n');print('Patch and mail verified against fresh baseline:',len(hashes),'source files')
