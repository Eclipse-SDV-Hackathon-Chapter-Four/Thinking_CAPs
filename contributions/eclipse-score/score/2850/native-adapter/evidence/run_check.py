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

import hashlib, json, os, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, "/home/jefferson/s-core_sw_fabric/src")
from score_sw_fabric.storage import validate_run_root, build_environment
root = Path(__file__).resolve().parent
native = root / "draft-native"
def subjects():
    paths = sorted(set([str(p.relative_to(native)) for area in ["score_harness", "scripts_bazel", "docs/concepts", ".github/workflows"] for p in (native/area).rglob("*") if p.is_file() and p.suffix in {".py", ".json", ".yaml", ".yml", ".rst", ".md"} and "__pycache__" not in p.parts] + ["BUILD", "score_harness/BUILD", "score_harness/tests/BUILD", "score_harness/harness/BUILD", "scripts_bazel/BUILD", "pyproject.toml", "MODULE.bazel", "MODULE.bazel.lock", "src/requirements.txt"]))
    return {path: hashlib.sha256((native / path).read_bytes()).hexdigest() for path in paths}
def run(name, command):
    validate_run_root(root)
    env = dict(os.environ, **build_environment(root))
    env.update(PYTHONPATH=str(native)+":"+str(root/"draft-bazel-output/external/rules_python+"), PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PATH=str(root/"verification-venv/bin")+":"+"/home/jefferson/s-core_sw_fabric/.venv/bin:"+env["PATH"])
    before = subjects()
    started = time.time()
    with (root / "checks" / (name+".log")).open("w") as log:
        result = subprocess.run(command, cwd=native, env=env, stdout=log, stderr=subprocess.STDOUT)
    after = subjects()
    record = {"name":name,"command":command,"cwd":str(native),"exit_code":result.returncode,"duration_seconds":time.time()-started,"subject_sha256":before,"subjects_unchanged":before==after,"source_commit":"4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9","environment_overrides":{key:env[key] for key in ["PYTHONPATH","PYTHONDONTWRITEBYTECODE","PYTEST_DISABLE_PLUGIN_AUTOLOAD","PATH","TMPDIR","UV_CACHE_DIR"]}}
    (root / "checks" / (name+".json")).write_text(json.dumps(record,indent=2)+"\n")
    print(name,result.returncode,flush=True)
    if result.returncode: print((root/"checks"/(name+".log")).read_text()[-7000:],flush=True)
    return result.returncode
if __name__=="__main__":
    sys.exit(run(sys.argv[1],sys.argv[2:]))
