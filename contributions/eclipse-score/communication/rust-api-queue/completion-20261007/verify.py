#!/usr/bin/env python3
# Copyright (c) 2026 Eclipse SDV Hackathon Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""Verify retained packet bytes; does not rerun tests or approve engineering work."""
import hashlib
import json
from pathlib import Path


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    root = Path(__file__).resolve().parent
    manifest = root / "artifact-manifest.json"
    expected = (root / "artifact-manifest.sha256").read_text().split()[0]
    assert digest(manifest) == expected, "Manifest identity mismatch"
    entries = json.loads(manifest.read_text())["files"]
    seen = set()
    for entry in entries:
        name = entry["path"]
        path = (root / name).resolve()
        assert path.is_relative_to(root) and path != root, "Escaping artifact path"
        assert path not in seen, "Duplicate artifact path"
        seen.add(path)
        assert path.is_file(), f"Missing artifact: {name}"
        assert path.stat().st_size == entry["size_bytes"], f"Size mismatch: {name}"
        assert digest(path) == entry["sha256"], f"SHA-256 mismatch: {name}"
    identity = json.loads((root / "source-identity.json").read_text())
    assert digest(root / "communication-integrated.patch") == identity["patch_sha256"]
    for entry in identity["files"]:
        assert digest(root / "source" / entry["path"]) == entry["sha256"]
    print(json.dumps({"status": "verified", "files": len(entries),
                      "candidate_commit": identity["candidate_commit"],
                      "scope": "artifact integrity; no native rerun or human acceptance"}))


if __name__ == "__main__":
    main()
