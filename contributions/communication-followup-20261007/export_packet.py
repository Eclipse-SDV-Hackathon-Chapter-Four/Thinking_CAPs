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

"""Export native patches and hash-bound, portable review inputs without committing."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

PACKET = Path(__file__).resolve().parent
ROOT = Path(json.loads((PACKET / "workspace.json").read_text())["root"])


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def export(name, source, upstream_revision):
    index = ROOT / (name + "-export.index")
    if index.exists():
        index.unlink()
    env = {**os.environ, "GIT_INDEX_FILE": str(index)}
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=source, env=env)
    git("read-tree", "HEAD")
    git("add", "--all", ".")
    changed = git("diff", "--cached", "--name-only", "HEAD").decode().splitlines()
    patches = PACKET / "patches"
    patches.mkdir(exist_ok=True)
    patch = patches / (name + ".patch")
    patch.write_bytes(git("diff", "--cached", "--binary", "HEAD"))
    (patches / (name + ".stat")).write_bytes(git("diff", "--cached", "--stat", "HEAD"))
    destination = PACKET / "native-source" / name
    destination.mkdir(parents=True, exist_ok=True)
    for item in changed:
        target = destination / item
        target.parent.mkdir(parents=True, exist_ok=True)
        if (source / item).exists():
            shutil.copy2(source / item, target)
    # Policy inputs are retained independently from changed-file exports.
    policy = PACKET / "native-policy" / name
    policy.mkdir(parents=True, exist_ok=True)
    for item in ["CONTRIBUTING.md", "CI.md", "CODEOWNERS", ".github/CODEOWNERS",
                 ".github/review_checklists.yml", ".bazelversion", ".bazelrc",
                 "MODULE.bazel", "MODULE.bazel.lock", "LICENSE", "NOTICE"]:
        if (source / item).is_file():
            target = policy / item
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(git("show", "HEAD:" + item))
    for item in (source / ".github/workflows").glob("*.yml"):
        target = policy / item.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(git("show", "HEAD:" + str(item.relative_to(source))))
    result = {"repository": name, "upstream_revision": upstream_revision,
              "patch": str(patch.relative_to(PACKET)), "patch_sha256": digest(patch),
              "changed_files": {item: digest(source / item) for item in changed if (source / item).is_file()}}
    (PACKET / (name + "-subject.json")).write_text(json.dumps(result, indent=2) + "\n")
    index.unlink()
    return result


if __name__ == "__main__":
    export("communication", ROOT / "candidate", "cef680454e8586daca9f953084dca33fb3759d0c")
    export("config_management", ROOT / "config-management-consumer-candidate",
           "e82ec2750d7e9a9dd18edbfe6f5a78be57c22d80")
