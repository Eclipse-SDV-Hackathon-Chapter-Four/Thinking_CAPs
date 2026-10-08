"""Refresh nested packet bindings after exporting the additional CI evidence."""

import datetime
import argparse
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
HEADERS = ROOT / "repository-license-headers"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def inventory(directory, exclude=()):
    return {str(path.relative_to(directory)): sha(path)
            for path in sorted(directory.rglob("*"))
            if path.is_file() and not path.is_symlink()
            and "__pycache__" not in path.parts
            and str(path.relative_to(directory)) not in exclude}


def refresh_known(manifest, base):
    data = json.loads(manifest.read_text())
    data["files"] = {name: sha(base / name) for name in data["files"]}
    write(manifest, data)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id", type=int)
    parser.add_argument("--attempt", type=int, default=1)
    options = parser.parse_args()
    summary = json.loads((HERE / f"runs/{options.run_id}/{options.attempt}/summary.json").read_text())
    if summary["status"] != "completed":
        raise ValueError("Final packet refresh requires terminal CI evidence")
    header_result = json.loads((HEADERS / "result.json").read_text())
    if header_result["missing_code_headers"] != 0 or header_result["native_code_header_check_exit"] != 0:
        raise ValueError("Repository code-header checks must pass")
    header_manifest = HEADERS / "artifact-manifest.json"
    write(header_manifest, {
        "kind": "repository_wide_code_license_header_contribution",
        "pr_url": header_result["pr_url"], "pr_head": header_result["pr_head"],
        "source_tree": header_result["source_tree"],
        "code_paths_audited": header_result["code_paths_audited"],
        "files": inventory(HEADERS, exclude=("artifact-manifest.json",)),
    })
    refresh_known(ROOT / "submission/publication/artifact-manifest.json",
                  ROOT / "submission/publication")
    submission = ROOT / "submission/artifact-manifest.json"
    refresh_known(submission, submission.parent)
    acceptance = ROOT / "acceptance-review/artifact-manifest.json"
    refresh_known(acceptance, ROOT)
    write(HERE / "artifact-manifest.json", {
        "kind": "additional_native_host_ci_and_copyright_evidence",
        "run_url": summary["run_url"], "run_attempt": summary["run_attempt"],
        "source_tree": summary["verified_source_tree"],
        "qnx": "excluded_by_user",
        "files": inventory(HERE, exclude=("artifact-manifest.json",)),
    })
    main_manifest = ROOT / "artifact-manifest.json"
    data = json.loads(main_manifest.read_text())
    data["files"] = {name: sha(ROOT / name) for name in data["files"]}
    for name, digest in inventory(HERE).items():
        data["files"]["non-qnx-verification/" + name] = digest
    for name, digest in inventory(HEADERS).items():
        data["files"]["repository-license-headers/" + name] = digest
    data["status"] = "non_qnx_and_repository_code_headers_exported_upstream_acceptance_pending"
    data["latest_host_verification"] = summary["run_url"]
    data["repository_code_header_pr"] = header_result["pr_url"]
    write(main_manifest, data)
    session = json.loads((ROOT / "session-artifact-manifest.json").read_text())
    session.update({
        "sha256": sha(main_manifest), "status": data["status"],
        "time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "verified_file_count": len(data["files"]),
        "latest_host_verification": summary["run_url"],
        "repository_code_header_pr": header_result["pr_url"],
        "packet_count_evidence": "all current root inventory entries freshly hash-bound; original native packet retained",
    })
    write(ROOT / "session-artifact-manifest.json", session)
    for manifest, base in [
        (main_manifest, ROOT), (header_manifest, HEADERS),
        (HERE / "artifact-manifest.json", HERE),
        (acceptance, ROOT), (submission, submission.parent),
        (ROOT / "submission/publication/artifact-manifest.json", ROOT / "submission/publication"),
    ]:
        entries = json.loads(manifest.read_text())["files"]
        for name, expected in entries.items():
            if sha(base / name) != expected:
                raise ValueError(f"Invalid binding in {manifest}: {name}")
    print(json.dumps({"root_inventory_files": len(data["files"]),
                      "new_packet_files": len(json.loads((HERE / "artifact-manifest.json").read_text())["files"]),
                      "header_packet_files": len(json.loads(header_manifest.read_text())["files"]),
                      "root_manifest_sha256": session["sha256"]}))


if __name__ == "__main__":
    main()
