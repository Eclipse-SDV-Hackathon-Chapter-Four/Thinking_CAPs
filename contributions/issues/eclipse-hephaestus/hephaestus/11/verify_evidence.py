#!/usr/bin/env python3
"""Verify the frozen proposal packet, without executing retained artifacts."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
manifest = json.loads((root / "artifact-manifest.json").read_text())
actual = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and p.name != "artifact-manifest.json" and "__pycache__" not in p.parts}
assert actual == set(manifest["files"]), "Packet file set differs from manifest"
for name, expected in manifest["files"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, name
binding = json.loads((root / "proposal-binding.json").read_text())
pr = json.loads((root / "pr-snapshot.json").read_text())
assert pr["head"]["sha"] == binding["commit"]
assert pr["base"]["repo"]["full_name"] == binding["upstream_repository"]
assert pr["draft"] and pr["number"] == 14
files = json.loads((root / "pr-files.json").read_text())
assert {f["filename"] for f in files} == set(binding["changed_files"])
provenance = json.loads((root / "provenance.json").read_text())
assert len(provenance["implementation_files"]) == 16
for name in provenance["implementation_files"]:
    assert (root / "evidence/implementation" / name).is_file(), name
statuses = json.loads((root / "pr-status.json").read_text())["statuses"]
assert any(s["context"] == "eclipsefdn/eca" and s["state"] == "success" for s in statuses)
print(f"PASS: {len(manifest['files'])} retained files; pinned proposal, 16 references and captured ECA success verified")
