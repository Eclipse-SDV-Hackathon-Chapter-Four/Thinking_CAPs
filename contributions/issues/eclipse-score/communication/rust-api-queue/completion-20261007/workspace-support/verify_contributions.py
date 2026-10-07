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

"""Verify retained contribution bytes offline; no native execution or acceptance."""

import argparse
import hashlib
import json
import posixpath
import sys
import tarfile
from datetime import datetime
from pathlib import Path, PurePosixPath


def digest(stream):
    value = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        value.update(chunk)
    return value.hexdigest()


def file_digest(path):
    with path.open("rb") as stream:
        return digest(stream)


def local_path(root, relative):
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe artifact path: {relative}")
    result = root.joinpath(*path.parts).resolve()
    if not result.is_relative_to(root.resolve()):
        raise ValueError(f"Artifact leaves its record: {relative}")
    return result


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def check_manifest(path):
    files = load(path)["files"]
    if not files:
        raise ValueError(f"Empty evidence manifest: {path}")
    if isinstance(files, dict):
        entries = files.items()
    elif isinstance(files, list):
        entries = ((entry["path"], entry) for entry in files)
    else:
        raise ValueError(f"Unsupported manifest file inventory: {path}")
    seen = set()
    for relative, identity in entries:
        if not isinstance(relative, str):
            raise ValueError(f"Invalid manifest path: {path}")
        artifact = local_path(path.parent, relative)
        name = str(artifact)
        if name in seen:
            raise ValueError(f"Duplicate manifest path: {relative}")
        seen.add(name)
        if isinstance(identity, str):
            expected, size = identity, None
        elif isinstance(identity, dict):
            expected = identity["sha256"]
            size = identity.get("size_bytes", identity.get("size"))
            if "size_bytes" in identity and "size" in identity and identity["size_bytes"] != identity["size"]:
                raise ValueError(f"Conflicting artifact sizes: {relative}")
        else:
            raise ValueError(f"Unsupported manifest identity: {relative}")
        if not isinstance(expected, str) or len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            raise ValueError(f"Invalid SHA-256: {relative}")
        if size is not None and (type(size) is not int or size < 0 or artifact.stat().st_size != size):
            raise ValueError(f"Artifact size mismatch: {artifact}")
        actual = file_digest(artifact)
        if actual != expected:
            raise ValueError(f"SHA-256 mismatch: {path.parent / relative}")
    return len(files)


def snapshot_observation(snapshot):
    """Read either the original registry projection or a captured GitHub response."""
    fields = ("url", "issue_number", "state", "captured_on")
    if all(field in snapshot for field in fields):
        return {field: snapshot[field] for field in fields}
    issue = snapshot.get("issue")
    if not isinstance(issue, dict) or not isinstance(snapshot.get("retrieved_at"), str):
        raise ValueError("Unsupported upstream snapshot format")
    url = issue.get("html_url", issue.get("url"))
    number, state = issue.get("number"), issue.get("state")
    if not isinstance(url, str) or type(number) is not int or not isinstance(state, str):
        raise ValueError("Incomplete captured GitHub issue identity")
    captured_on = datetime.fromisoformat(snapshot["retrieved_at"]).date().isoformat()
    return {"url": url, "issue_number": number, "state": state.lower(), "captured_on": captured_on}


def check_archive(root, description):
    archive = local_path(root, description["path"])
    if archive.stat().st_size != description["size_bytes"]:
        raise ValueError(f"Archive size mismatch: {archive}")
    if file_digest(archive) != description["sha256"]:
        raise ValueError(f"Archive SHA-256 mismatch: {archive}")
    portable_path = local_path(root, description["portable_manifest"])
    portable = load(portable_path)["files"]
    if len(portable) != description["expected_portable_entries"]:
        raise ValueError("Portable evidence count mismatch")
    hashes, links = {}, {}
    seen = set()
    with tarfile.open(archive, "r:gz") as bundle:
        for member in bundle:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or path.parts[0] != "review-packet":
                raise ValueError(f"Unsafe archive member: {member.name}")
            if member.name in seen:
                raise ValueError(f"Duplicate archive member: {member.name}")
            seen.add(member.name)
            relative = path.relative_to("review-packet").as_posix()
            if member.isfile():
                with bundle.extractfile(member) as stream:
                    hashes[relative] = digest(stream)
            elif member.issym():
                target = posixpath.normpath(posixpath.join(posixpath.dirname(relative), member.linkname))
                if target.startswith("../") or target.startswith("/"):
                    raise ValueError(f"Unsafe archive symlink: {relative}")
                links[relative] = target
            elif not member.isdir():
                raise ValueError(f"Unsupported archive member: {relative}")
    for relative, target in links.items():
        hashes[relative] = hashes[target]
    # The portable manifest excludes itself; its captured sidecar pins its bytes.
    if hashes.pop("portable-files.json") != file_digest(portable_path):
        raise ValueError("Archive and sidecar portable manifests differ")
    if hashes != portable:
        raise ValueError("Archive entries do not match the portable SHA-256 manifest")
    packet = load(local_path(root, description["review_packet"]))
    sources = packet["source_hashes"]
    if len(sources) != description["expected_candidate_sources"]:
        raise ValueError("Candidate source count mismatch")
    for relative, expected in sources.items():
        matches = [value for name, value in hashes.items() if name.endswith("/source/" + relative)]
        if matches != [expected]:
            raise ValueError(f"Candidate source mismatch: {relative}")
    changed = load(local_path(root, description["candidate_files"]))
    for relative, identity in changed.items():
        if sources.get(relative) != identity["sha256"]:
            raise ValueError(f"Patch candidate identity mismatch: {relative}")
    return {"portable_entries": len(portable), "candidate_sources": len(sources), "changed_files": len(changed)}


def verify(root, selected_issues=None):
    registry = load(root / "registry.json")
    if registry["schema_version"] != 1:
        raise ValueError("Unsupported registry schema")
    if selected_issues is not None:
        selected_issues = set(selected_issues)
        unknown = selected_issues - {issue["id"] for issue in registry["issues"]}
        if unknown:
            raise ValueError(f"Unknown requested issues: {', '.join(sorted(unknown))}")
    results, seen = [], set()
    for issue in registry["issues"]:
        identity = issue["id"]
        if identity in seen:
            raise ValueError(f"Duplicate issue: {identity}")
        seen.add(identity)
        if selected_issues is not None and identity not in selected_issues:
            continue
        for field in ("record", "upstream_snapshot", "pr_draft"):
            if issue.get(field) and not local_path(root, issue[field]).is_file():
                raise ValueError(f"Missing {field}: {identity}")
        snapshot = snapshot_observation(load(local_path(root, issue["upstream_snapshot"])))
        if snapshot["url"] != issue["issue_url"] or snapshot["issue_number"] != issue["issue_number"]:
            raise ValueError(f"Upstream issue identity mismatch: {identity}")
        if snapshot["state"] != issue["upstream_state"] or snapshot["captured_on"] != issue["upstream_observed_on"]:
            raise ValueError(f"Upstream observation mismatch: {identity}")
        result = {"issue": identity, "local_status": issue["local_status"], "captured_files": check_manifest(local_path(root, issue["evidence_manifest"]))}
        if issue["submission_candidate"] and not issue.get("patch"):
            raise ValueError(f"Submission candidate has no patch: {identity}")
        if issue.get("patch"):
            if file_digest(local_path(root, issue["patch"])) != issue["patch_sha256"]:
                raise ValueError(f"Patch SHA-256 mismatch: {identity}")
        if issue.get("original_manifest"):
            result["original_files"] = check_manifest(local_path(root, issue["original_manifest"]))
        if issue.get("readiness_review"):
            review = issue["readiness_review"]
            manifest = local_path(root, review["manifest"])
            if file_digest(manifest) != review["manifest_sha256"]:
                raise ValueError(f"Readiness manifest SHA-256 mismatch: {identity}")
            result["readiness_files"] = check_manifest(manifest)
            if file_digest(local_path(root, review["candidate_patch"])) != review["candidate_patch_sha256"]:
                raise ValueError(f"Readiness candidate SHA-256 mismatch: {identity}")
        if issue.get("archive"):
            result.update(check_archive(root, issue["archive"]))
        results.append(result)
    return {"status": "verified", "scope": "retained artifact integrity; native tests not rerun; engineering acceptance not evaluated", "issues": results}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1] / "contributions", help="Contribution directory (default: this repository's contributions/)")
    parser.add_argument("--json", action="store_true", help="Print a machine-readable result")
    parser.add_argument("--issue", action="append", help="Verify only this exact registry issue ID; repeat for multiple issues")
    args = parser.parse_args()
    try:
        result = verify(args.root.resolve(), args.issue)
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError) as exc:
        result = {"status": "failed", "error": str(exc)}
        print(json.dumps(result, indent=2) if args.json else f"FAILED: {exc}")
        return 1
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for issue in result["issues"]:
            print(f"Verified {issue['issue']}: {issue['captured_files']} captured files; {issue['local_status']}")
        print("Retained evidence hashes verified for the reported issues. Native tests were not rerun; engineering acceptance is not evaluated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
