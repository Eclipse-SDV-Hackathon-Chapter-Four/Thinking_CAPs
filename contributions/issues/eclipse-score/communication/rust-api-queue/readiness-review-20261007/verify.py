#!/usr/bin/env python3
"""Verify packet bytes and carried-evidence bindings without executing native code."""

import hashlib
import json
from pathlib import Path, PurePosixPath


def checked_path(root, relative):
    name = PurePosixPath(relative)
    if name.is_absolute() or ".." in name.parts:
        raise ValueError(f"Unsafe path: {relative}")
    path = root.joinpath(*name.parts)
    if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path leaves packet: {relative}")
    return path


def check(root, files):
    for relative, identity in files.items():
        path = checked_path(root, relative)
        with path.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != identity["sha256"] or path.stat().st_size != identity["size_bytes"]:
            raise ValueError(f"Binding mismatch: {relative}")


def main():
    root = Path(__file__).resolve().parent
    manifest = json.loads((root / "artifact-manifest.json").read_text())
    check(root, manifest["files"])
    present = {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}
    expected = set(manifest["files"]) | {"artifact-manifest.json"}
    if present != expected:
        raise ValueError(f"Packet file inventory differs: {sorted(present ^ expected)}")
    check(root.parent.parent, manifest["carried_evidence"])
    verification = json.loads((root / "verification.json").read_text())
    if verification["engineering_acceptance"] != "pending_offline":
        raise ValueError("This packet cannot attest human engineering acceptance")
    for issue in ("1261", "250", "560"):
        subject = verification["issues"][issue]
        path = checked_path(root, subject["candidate_patch"])
        if hashlib.sha256(path.read_bytes()).hexdigest() != subject["candidate_patch_sha256"]:
            raise ValueError(f"Candidate binding mismatch: {issue}")
    print(json.dumps({"status": "verified", "packet_files": len(manifest["files"]),
                      "carried_evidence_files": len(manifest["carried_evidence"]),
                      "scope": "artifact integrity; no native rerun or human/IP acceptance"}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}))
        raise SystemExit(1)
