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

"""Execute local checks in the bound disposable workspace; retain complete evidence."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import time

sys.path.insert(0, "/home/jefferson/s-core_sw_fabric/src")
from score_sw_fabric.storage import build_environment, validate_run_root

PACKET = Path(__file__).resolve().parent
ROOT = Path(json.loads((PACKET / "workspace.json").read_text())["root"])
TOOLS = json.loads((PACKET / "tools.json").read_text())


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run(label, command, cwd=None, env=None):
    validate_run_root(ROOT)
    evidence = PACKET / "evidence"
    evidence.mkdir(exist_ok=True)
    record_path = evidence / (label + ".json")
    if record_path.exists():
        raise FileExistsError(record_path)
    cwd = Path(cwd or ROOT / "candidate")
    revision = ("e82ec2750d7e9a9dd18edbfe6f5a78be57c22d80" if cwd.name.startswith("config")
                else "381d43dec900ab6a9076f3f30e7bfbdee019e26e")
    upstream_binding = cwd / ".git" / "score-upstream-revision"
    if upstream_binding.is_file():
        revision = upstream_binding.read_text().strip()
    record = {"command": command, "cwd": str(cwd), "started_at": time.time(),
              "carried_evidence": False, "source_baseline": revision,
              "collector_sha256": sha(Path(__file__))}
    subject_root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=cwd, text=True).strip())
    files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=subject_root, text=True).splitlines()
    root_binding = subject_root / ".git" / "score-upstream-revision"
    if root_binding.is_file():
        record["source_baseline"] = root_binding.read_text().strip()
    record["subject_root"] = str(subject_root)
    record["subject_hashes"] = {name: sha(subject_root / name) for name in files if (subject_root / name).is_file()}
    stdout, stderr = evidence / (label + ".stdout"), evidence / (label + ".stderr")
    with stdout.open("wb") as out, stderr.open("wb") as err:
        process = subprocess.Popen(command, cwd=cwd, env={**os.environ, **build_environment(ROOT), **(env or {})}, stdout=out, stderr=err)
        try:
            while process.poll() is None:
                validate_run_root(ROOT)
                time.sleep(1)
        except BaseException:
            process.terminate()
            process.wait()
            raise
    record.update(exit_code=process.returncode, finished_at=time.time(),
                  stdout_sha256=sha(stdout), stderr_sha256=sha(stderr))
    record["subject_hashes_after"] = {name: sha(subject_root / name) for name in files if (subject_root / name).is_file()}
    record["changed_during_execution"] = [name for name, value in record["subject_hashes"].items()
                                           if record["subject_hashes_after"].get(name) != value]
    record_path.write_text(json.dumps(record, indent=2) + "\n")
    print(label, process.returncode, flush=True)
    return record


def container_command(command, cwd=None, runtime_tools=False):
    validate_run_root(ROOT)
    for name in ["container-home", "container-tmp", "container-var-tmp", "tools"]:
        (ROOT / name).mkdir(exist_ok=True)
    old = Path(TOOLS["old_root"])
    args = ["docker", "run", "--rm", "--read-only", "--network", "host", "--user", "1000:1000",
            "--cpus", "8", "--memory", "16g", "--cap-add", "SYS_ADMIN",
            "--security-opt", "seccomp=unconfined", "--security-opt", "apparmor=unconfined",
            "--mount", f"type=bind,source={ROOT},target={ROOT}",
            "--mount", f"type=bind,source={old},target={old},readonly",
            "--mount", f"type=bind,source={ROOT / 'container-tmp'},target=/tmp",
            "--mount", f"type=bind,source={ROOT / 'container-var-tmp'},target=/var/tmp",
            "--workdir", str(cwd or ROOT / "candidate"), "--env", "HOME=" + str(ROOT / "container-home"),
            "--env", "PATH=" + str(ROOT / "tools") + ":/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"]
    if runtime_tools:
        docker_cli = shutil.which("docker")
        socket_path = Path("/var/run/docker.sock")
        args += ["--group-add", str(socket_path.stat().st_gid),
                 "--mount", f"type=bind,source={docker_cli},target=/usr/bin/docker,readonly",
                 "--mount", f"type=bind,source={socket_path},target={socket_path}",
                 "--mount", f"type=bind,source={ROOT / 'tools/bazel'},target=/usr/local/bin/bazel,readonly"]
    environment = build_environment(ROOT)
    environment.pop("TEST_TMPDIR", None)
    for key, value in environment.items():
        args += ["--env", key + "=" + value]
    return args + ["--entrypoint", command[0], "sha256:8332c7a66af3f1cfdb04ce803ce4b7711a976fb2bcbdda3cdae598c96c11fa88", *command[1:]]


def bazel(label, args, cwd=None, runtime_tools=False):
    command = [str(Path(TOOLS["old_root"]) / "tools/bazel-8.7.0"),
               "--output_user_root=" + str(ROOT / "bazel-output"), "--batch", *args]
    return run(label, container_command(command, cwd, runtime_tools), cwd)


if __name__ == "__main__":
    bazel(sys.argv[1], sys.argv[2:])
