#!/usr/bin/env python3
"""Verify this evaluation packet offline without executing its captured contents."""

import hashlib
import json
import sys
import tarfile
from pathlib import Path, PurePosixPath


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def confined(root, relative):
    path = PurePosixPath(relative)
    if not relative or path.is_absolute() or ".." in path.parts:
        raise ValueError(f"Unsafe path: {relative}")
    result = root.joinpath(*path.parts)
    if not result.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Path leaves root: {relative}")
    return result


def check_manifest(manifest):
    files = load(manifest)["files"]
    if not files:
        raise ValueError(f"Empty manifest: {manifest}")
    for relative, expected in files.items():
        if digest(confined(manifest.parent, relative)) != expected:
            raise ValueError(f"SHA-256 mismatch: {manifest.parent / relative}")
    return len(files)


def verify(packet):
    manifest = packet / "artifact-manifest.json"
    payload_count = check_manifest(manifest)
    expected_paths = set(load(manifest)["files"])
    actual_paths = {
        p.relative_to(packet).as_posix()
        for p in packet.rglob("*")
        if p.is_file() and p != manifest
    }
    if expected_paths != actual_paths:
        raise ValueError("Outer manifest does not cover exactly all packet files")

    fabric = packet / "evidence/fabric"
    inventory = load(fabric / "source-files.json")
    expected = inventory["files"]
    observed = {}
    prefix = PurePosixPath(inventory["archive_prefix"])
    with tarfile.open(fabric / inventory["archive"], "r:gz") as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or not member.isfile():
                raise ValueError(f"Unsafe archive member: {member.name}")
            relative = path.relative_to(prefix).as_posix()
            if relative in observed:
                raise ValueError(f"Duplicate archive member: {relative}")
            with archive.extractfile(member) as stream:
                value = hashlib.sha256()
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    value.update(chunk)
                observed[relative] = value.hexdigest()
    if observed != expected:
        raise ValueError("Source archive does not match exact per-file inventory")
    identity = load(fabric / "source-identity.json")
    if len(observed) != identity["source_file_count"]:
        raise ValueError("Source file count mismatch")
    if digest(fabric / inventory["archive"]) != identity["source_archive_sha256"]:
        raise ValueError("Source archive identity mismatch")
    if digest(fabric / "source-files.json") != identity["source_inventory_sha256"]:
        raise ValueError("Source inventory identity mismatch")
    if digest(fabric / "working-tree.patch") != identity["working_tree_patch_sha256"]:
        raise ValueError("Working-tree patch identity mismatch")
    if digest(fabric / "git-status.txt") != identity["status_sha256"]:
        raise ValueError("Git status identity mismatch")
    for relative, value in load(fabric / "carried-files.json")["files"].items():
        if digest(confined(fabric / "carried", relative)) != value:
            raise ValueError(f"Carried-file mismatch: {relative}")

    candidates = load(packet / "evidence/candidates/index.json")
    required = {
        "microsoft/apm", "LobsterTrap/lola", "Mumme-IT/okit", "enthali/syspilot",
        "bmad-code-org/BMAD-METHOD", "github/spec-kit", "useblocks/pharaoh",
        "harbor-framework/harbor",
    }
    if {row["requested_repository"] for row in candidates} != required:
        raise ValueError("Candidate inventory is incomplete")
    for row in candidates:
        folder = packet / "evidence/candidates" / row["requested_repository"].replace("/", "--")
        if load(folder / "head.json")["sha"] != row["source_commit"]:
            raise ValueError("Candidate source commit mismatch")
        if load(folder / "capture.json") != row:
            raise ValueError("Candidate capture mismatch")

    snapshot = load(packet / "upstream-snapshot.json")
    issue = load(packet / "evidence/upstream/issue-3115.json")
    pr = load(packet / "evidence/upstream/pr-3140.json")
    if snapshot["url"] != issue["html_url"] or issue["number"] != 3115:
        raise ValueError("Issue identity mismatch")
    if snapshot["state"] != issue["state"] or snapshot["existing_pr_head"] != pr["head"]["sha"]:
        raise ValueError("Issue/PR snapshot mismatch")

    binding = load(packet / "native/patch-binding.json")
    for relative, key in (
        ("evidence/upstream/proposed-DR-010-infra.rst", "original_file_sha256"),
        ("native/base/docs/design_decisions/DR-010-infra.rst", "original_file_sha256"),
        ("native/proposed-DR-010-infra.rst", "candidate_file_sha256"),
        ("native/supplement.patch", "patch_sha256"),
    ):
        if digest(packet / relative) != binding[key]:
            raise ValueError(f"Native supplement binding mismatch: {relative}")
    if binding["base_commit"] != pr["head"]["sha"]:
        raise ValueError("Native supplement PR base mismatch")

    preparation = packet / "upstream-preparation"
    if preparation.exists():
        report = load(preparation / "verification-report.json")
        envelope = load(preparation / "task-envelope.json")
        commit = load(preparation / "native-commit.json")
        if report["native_baseline"] != envelope["native_baseline"] or commit["baseline"] != report["native_baseline"]:
            raise ValueError("Current native baseline mismatch")
        if digest(preparation / "DR-010-infra.rst") != report["changed_file_sha256"]:
            raise ValueError("Current native candidate mismatch")
        if report["source_hashes"] != envelope["source_hashes"]:
            raise ValueError("Current native input binding mismatch")
        exports = []
        for name in ("baseline-needs.json", "candidate-final-needs.json"):
            data = load(preparation / name)
            exports.append(data["versions"][data["current_version"]]["needs"])
        original, candidate = exports
        delta = report["needs_delta"]
        if len(original) != delta["baseline_count"] or len(candidate) != delta["candidate_count"]:
            raise ValueError("Native export count mismatch")
        if set(candidate) - set(original) != {envelope["native_id"]} or set(original) - set(candidate):
            raise ValueError("Native export identity delta mismatch")
        if any(original[key] != candidate[key] for key in original):
            raise ValueError("Existing native need changed")
        if (preparation / "baseline-warnings.txt").read_bytes() != (preparation / "candidate-final-warnings.txt").read_bytes():
            raise ValueError("Native baseline/candidate diagnostics differ")
        for label in ("baseline-docs-check", "candidate-docs-check", "candidate-final-docs-check", "candidate-html", "candidate-copyright"):
            check = load(preparation / (label + ".json"))
            if digest(preparation / (label + ".log")) != check["log_sha256"]:
                raise ValueError("Native raw log mismatch: " + label)
            if "changed_file_sha256" in check and label != "candidate-docs-check":
                if check["changed_file_sha256"] != report["changed_file_sha256"]:
                    raise ValueError("Native check subject mismatch: " + label)

    repo = packet.parents[4]
    references = load(packet / "evidence/native-contributions.json")
    native_counts = {}
    checked_manifests = {}
    for row in references["packets"]:
        native_manifest = confined(repo, row["manifest"])
        if digest(native_manifest) != row["manifest_sha256"]:
            raise ValueError(f"Native manifest changed: {row['id']}")
        if native_manifest not in checked_manifests:
            checked_manifests[native_manifest] = check_manifest(native_manifest)
        native_counts[row["id"]] = checked_manifests[native_manifest]
    registry = load(repo / "contributions/registry.json")
    entry = next(row for row in registry["issues"] if row["id"] == "eclipse-score/score#3115")
    if entry["issue_url"] != snapshot["url"] or entry["upstream_observed_on"] != snapshot["captured_on"]:
        raise ValueError("New registry entry does not match snapshot")
    if entry["upstream_state"] != snapshot["state"] or entry["submission_candidate"]:
        raise ValueError("New registry status mismatch")
    return {
        "status": "verified",
        "scope": "retained byte integrity and identity; no test execution or engineering acceptance",
        "packet_files": payload_count,
        "source_files": len(observed),
        "candidate_repositories": len(candidates),
        "native_packet_files": native_counts,
        "unique_native_manifests": len(checked_manifests),
        "unique_native_manifest_entries": sum(checked_manifests.values()),
    }


def main():
    try:
        result = verify(Path(__file__).resolve().parent)
    except (OSError, ValueError, KeyError, StopIteration, TypeError, tarfile.TarError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
