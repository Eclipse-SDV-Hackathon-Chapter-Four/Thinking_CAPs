#!/usr/bin/env python3
"""Check a frozen proposal packet without executing retained artifacts."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "artifact-manifest.json").read_text())
actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and str(p.relative_to(root)) != "artifact-manifest.json" and "__pycache__" not in p.parts}
assert actual == set(manifest["files"]), "Packet file set differs from manifest"
for name, expected in manifest["files"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
binding = json.loads((root / "proposal-binding.json").read_text())
pr = json.loads((root / "pr-snapshot.json").read_text())
assert pr["head"]["sha"] == binding["commit"]
assert pr["base"]["repo"]["full_name"] == binding["upstream_repository"]
assert pr["number"] == 15 and pr["draft"] and pr["state"] == "open"
files = json.loads((root / "pr-files.json").read_text())
assert {f["filename"] for f in files} == set(binding["changed_files"])
for name, expected in binding["changed_files"].items():
    assert hashlib.sha256((root / "candidate" / name).read_bytes()).hexdigest() == expected, name
refs = json.loads((root / "implementation-references.json").read_text())
assert refs["commit"] == binding["implementation_commit"] and len(refs["paths"]) == 18
for name in refs["paths"]:
    assert (root / "evidence/implementation" / name).is_file(), name
for command in json.loads((root / "evidence/validation/commands.json").read_text()):
    assert command["exit_code"] == 0, command["name"]
    log = root / "evidence/validation" / (command["name"] + ".log")
    assert hashlib.sha256(log.read_bytes()).hexdigest() == command["log_sha256"], command["name"]
provenance = json.loads((root / "provenance.json").read_text())
for name, expected in provenance["carried_checks"]["copied_files"].items():
    assert hashlib.sha256((root / "evidence/carried-chatbot" / name).read_bytes()).hexdigest() == expected, name
merge = json.loads((root / "evidence/validation/pr-14-merge-check.json").read_text())
assert merge["candidate_commit"] == binding["commit"] and merge["merge_exit_code"] == 0
print(f"PASS: {len(manifest['files'])} sealed files, three candidate bindings, 18 references, build logs, carried evidence and PR #14 merge check")
