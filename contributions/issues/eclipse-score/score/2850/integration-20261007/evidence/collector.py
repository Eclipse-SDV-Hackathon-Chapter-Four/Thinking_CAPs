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

import datetime, hashlib, json, os, subprocess, sys, tarfile, time, urllib.request
from pathlib import Path
sys.path.insert(0, '/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import build_environment, validate_run_root
workspace = Path('/home/jefferson/Thinking_CAPs')
packet = workspace / 'contributions/issues/eclipse-score/score/2850'
out = packet / 'integration-20261007/evidence'
root = Path('/tmp/score-2850-integration-run-path').read_text().strip()
root = Path(root)
validate_run_root(root)
env = dict(os.environ, **build_environment(root), PYTHONDONTWRITEBYTECODE='1')
env.pop('PYTHONPATH', None)
native = root / 'native'
native.mkdir()
records = []
def run(args, cwd=native, required=True):
    validate_run_root(root)
    start = time.time()
    result = subprocess.run(args, cwd=cwd, env=env, text=True, capture_output=True)
    record = dict(command=args, cwd=str(cwd), exit_code=result.returncode,
                  stdout=result.stdout, stderr=result.stderr, duration_seconds=time.time()-start)
    records.append(record)
    (out / 'commands.json').write_text(json.dumps(records, indent=2)+'\n')
    print('exit', result.returncode, ' '.join(args[:6]), flush=True)
    if required and result.returncode:
        raise RuntimeError(result.stderr)
    return result
upstream = {}
for name, suffix in [('pr-628','pulls/628'),('main','commits/main'),('issue-2850','../score/issues/2850')]:
    url = ('https://api.github.com/repos/eclipse-score/docs-as-code/'+suffix) if name != 'issue-2850' else 'https://api.github.com/repos/eclipse-score/score/issues/2850'
    req = urllib.request.Request(url, headers={'User-Agent':'score-contribution-review','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        raw = response.read()
    (out / (name+'.json')).write_bytes(raw)
    upstream[name] = json.loads(raw)
(out / 'retrieval.json').write_text(json.dumps({'retrieved_at':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'urls':['https://api.github.com/repos/eclipse-score/docs-as-code/pulls/628','https://api.github.com/repos/eclipse-score/docs-as-code/commits/main','https://api.github.com/repos/eclipse-score/score/issues/2850']}, indent=2)+'\n')
expected = '4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9'
if upstream['pr-628']['head']['sha'] != expected:
    raise RuntimeError('Draft head changed; existing measured evidence is not transferable')
main_sha = upstream['main']['sha']
run(['git','init','--initial-branch=integration-base'])
run(['git','config','core.hooksPath','/dev/null'])
run(['git','remote','add','origin','https://github.com/eclipse-score/docs-as-code.git'])
run(['git','fetch','--depth=1','origin','refs/heads/harness:refs/remotes/origin/harness','refs/heads/main:refs/remotes/origin/main'])
assert run(['git','rev-parse','origin/harness']).stdout.strip() == expected
assert run(['git','rev-parse','origin/main']).stdout.strip() == main_sha
branch='contrib/score-2850-native-mvp'
run(['git','checkout','-b',branch,expected])
patch = packet / 'native-adapter/patches/0001-score-2850-assurance-harness.patch'
run(['git','apply','--check',str(patch)])
run(['git','apply','--index',str(patch)])
run(['git','diff','--cached','--check'])
changed = run(['git','diff','--cached','--name-only']).stdout.splitlines()
candidate = packet / 'native-adapter/candidate'
expected_changed = sorted(p.relative_to(candidate).as_posix() for p in candidate.rglob('*') if p.is_file())
assert sorted(changed) == expected_changed
hashes = {name:hashlib.sha256((native/name).read_bytes()).hexdigest() for name in changed}
assert hashes == {name:hashlib.sha256((candidate/name).read_bytes()).hexdigest() for name in changed}
binding=json.loads((packet/'native-adapter/evidence/source/binding.json').read_text())
(out/'candidate-tree.json').write_text(json.dumps({'branch':branch,'base':expected,'tree':run(['git','write-tree']).stdout.strip(),'changed_files':hashes,'candidate_files_match':True,'patch_sha256':hashlib.sha256(patch.read_bytes()).hexdigest(),'checkout':str(native),'commit_created':False,'signoff_created':False,'push_performed':False},indent=2)+'\n')
# Compare exact source names in both archived alternatives without executing them.
with tarfile.open(packet/'full-issue-fix-20261007/source/current.tar.gz') as archive:
    alternate={member.name:hashlib.sha256(archive.extractfile(member).read()).hexdigest() for member in archive if member.isfile()}
(out/'alternative-source-comparison.json').write_text(json.dumps({'alternative_packet':'../full-issue-fix-20261007','alternative_archive_sha256':hashlib.sha256((packet/'full-issue-fix-20261007/source/current.tar.gz').read_bytes()).hexdigest(),'has_score_harness':any(n.startswith('score_harness/') for n in alternate),'assurance_python_files':sorted(n for n in alternate if n.startswith('assurance/') and n.endswith('.py')),'selected_native_files':sorted(n for n in changed if n.startswith('score_harness/')),'source_changes_combined':False},indent=2)+'\n')
# A second pristine worktree checks direct applicability to main without altering the selected branch.
main_tree=root/'main-check'
run(['git','worktree','add','--detach',str(main_tree),main_sha])
main_apply=run(['git','apply','--check',str(patch)],cwd=main_tree,required=False)
(out/'direct-main-application.json').write_text(json.dumps({'main':main_sha,'exit_code':main_apply.returncode,'direct_main_patch_compatible':main_apply.returncode==0,'expected_disposition':'Selected patch targets the existing draft harness; this check is not an execution test'},indent=2)+'\n')
(out/'local-status.txt').write_text(run(['git','status','--short','--branch']).stdout)
(out/'verified-checkout.json').write_text(json.dumps({'selected_branch':branch,'selected_pr_base':'harness','eventual_pr_base':'main after #628 integration','head':expected,'main':main_sha,'patch_applies':True,'changed_files':len(changed),'source_changed_since_native_measurement':False,'execution_evidence':'carried only after exact file hashes match; no native tests rerun','upstream_mergeable':upstream['pr-628'].get('mergeable'),'upstream_accepted':False},indent=2)+'\n')
print('selected branch prepared; candidate identical to measured native packet',flush=True)
