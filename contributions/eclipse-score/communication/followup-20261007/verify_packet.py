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

"""Verify every portable review artifact against artifact-manifest.json."""
import hashlib
import json
from pathlib import Path
import sys

root = Path(__file__).resolve().parent
manifest = json.loads((root / "artifact-manifest.json").read_text())
failures = []
listed = {item["path"] for item in manifest["files"]}
for item in manifest["files"]:
    path = root / item["path"]
    if path.is_absolute() and not path.resolve().is_relative_to(root):
        failures.append(item["path"] + ": outside packet")
        continue
    if not path.is_file():
        failures.append(item["path"] + ": missing")
        continue
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    if path.stat().st_size != item["bytes"] or digest.hexdigest() != item["sha256"]:
        failures.append(item["path"] + ": bytes or SHA-256 mismatch")
actual = {str(path.relative_to(root)) for path in root.rglob("*")
          if path.is_file() and "__pycache__" not in path.parts
          and path.name != "artifact-manifest.json"}
failures.extend(name + ": unlisted" for name in sorted(actual - listed))
print(json.dumps({"verified_files": len(manifest["files"]), "failures": failures}, indent=2))
sys.exit(bool(failures))
