"""Collect genuine fork CI evidence without creating upstream check statuses."""

import argparse
import datetime
import hashlib
import json
import re
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = "jnsagai/communication"
EXPECTED = {
    "GCC15 / Build & Test",
    "Address & Undefined Behavior Sanitizer / Build & Test",
    "Thread Sanitizer / Build & Test",
    "Linters / clang-tidy",
    "Linters / clippy",
    "Linters / ruff",
}


def get(route):
    return json.loads(subprocess.check_output(["gh", "api", route], text=True))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_id", type=int)
    parser.add_argument("--final", action="store_true")
    parser.add_argument("--binding", type=Path, default=HERE,
                        help="Directory with the subject's workspace.json and subject.json")
    options = parser.parse_args()
    binding = options.binding.resolve()
    run = get(f"repos/{REPO}/actions/runs/{options.run_id}")
    jobs = get(f"repos/{REPO}/actions/runs/{options.run_id}/jobs?per_page=100")
    artifacts = get(f"repos/{REPO}/actions/runs/{options.run_id}/artifacts?per_page=100")
    attempt = HERE / "runs" / str(options.run_id) / str(run["run_attempt"])
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    if run["head_sha"] != json.loads((binding / "workspace.json").read_text())["pr_merge_commit"]:
        raise ValueError("Run subject differs from the bound verification merge")
    if run["event"] != "pull_request":
        raise ValueError("Run must use the actual native PR linter policy")
    write(attempt / "run.json", {"retrieved_at_utc": stamp, "response": run})
    write(attempt / "jobs.json", {"retrieved_at_utc": stamp, "response": jobs})
    write(attempt / "artifacts.json", {"retrieved_at_utc": stamp, "response": artifacts})
    summary = {
        "time_utc": stamp,
        "run_url": run["html_url"],
        "run_id": options.run_id,
        "run_attempt": run["run_attempt"],
        "head_sha": run["head_sha"],
        "event": run["event"],
        "binding": str(binding.relative_to(HERE)),
        "status": run["status"],
        "conclusion": run["conclusion"],
        "qnx": "excluded_by_user_and_disabled_in_fork",
        "upstream_gate_statuses_supplied": False,
        "jobs": [],
    }
    for job in jobs["jobs"]:
        current = (next((step["name"] for step in job["steps"] if step["status"] == "in_progress"), None)
                   if job["status"] == "in_progress" else None)
        summary["jobs"].append({
            "id": job["id"], "name": job["name"], "url": job["html_url"],
            "status": job["status"], "conclusion": job["conclusion"], "current_step": current,
        })
        if job["status"] == "completed":
            log = attempt / "logs" / f"{job['id']}.log"
            if not log.exists() or options.final:
                log.parent.mkdir(parents=True, exist_ok=True)
                with log.open("wb") as stream:
                    result = subprocess.run(
                        ["gh", "api", f"repos/{REPO}/actions/jobs/{job['id']}/logs"],
                        stdout=stream, stderr=subprocess.PIPE,
                    )
                if result.returncode:
                    log.unlink(missing_ok=True)
                    write(attempt / "logs" / f"{job['id']}-download-error.json", {
                        "stderr": result.stderr.decode(errors="replace"), "exit_code": result.returncode,
                    })
    if {job["name"] for job in jobs["jobs"]} != EXPECTED:
        raise ValueError("Expected six native non-QNX jobs")
    if options.final:
        if run["status"] != "completed":
            raise ValueError("Final export requires a terminal run")
        missing_logs = [job["id"] for job in jobs["jobs"]
                        if not (attempt / "logs" / f"{job['id']}.log").exists()]
        if missing_logs:
            raise ValueError(f"Complete job logs were not exported: {missing_logs}")
        if artifacts["total_count"]:
            destination = attempt / "artifacts"
            destination.mkdir(exist_ok=True)
            subprocess.run([
                "gh", "run", "download", str(options.run_id), "--repo", REPO,
                "--dir", str(destination),
            ], check=True)
        summary["module_integration_build"] = next(
            (step["conclusion"] for job in jobs["jobs"] if job["name"] == "GCC15 / Build & Test"
             for step in job["steps"] if step["name"] == "Build module_integration_test"), "not_reported",
        )
        summary["downloaded_artifact_count"] = artifacts["total_count"]
        summary["test_summary_lines"] = {}
        summary["new_test_results"] = {}
        summary["lint_findings"] = {}
        expected_tree = json.loads((binding / "subject.json").read_text())["merge_tree"]
        checkout_records = {}
        for job in jobs["jobs"]:
            raw = (attempt / "logs" / f"{job['id']}.log").read_text()
            match = re.search(r"git log -1 --format=%H\s*\n\S+Z\s+([0-9a-f]{40})", raw)
            if not match:
                raise ValueError(f"Job did not log its checkout: {job['name']}")
            checkout = match[1]
            if checkout not in checkout_records:
                checkout_records[checkout] = get(f"repos/{REPO}/git/commits/{checkout}")
            if checkout_records[checkout]["tree"]["sha"] != expected_tree:
                raise ValueError(f"Job checked out a different source tree: {job['name']}")
            clean = re.sub(r"\x1b\[[0-9;]*m", "", raw)
            summary["test_summary_lines"][job["name"]] = [
                line for line in clean.splitlines()
                if re.search(r"Executed \d+ out of \d+ tests|tests? fail", line, re.I)
            ]
            targets = {}
            for line in clean.splitlines():
                match = re.match(r"^\S+Z\s+(//\S+)\s+.*?\b(PASSED|SKIPPED|FAILED|FLAKY)\b", line)
                if match:
                    targets[match[1]] = match[2]
            if targets:
                write(attempt / "test-results" / f"{job['id']}.json", {
                    "job": job["name"], "log": f"logs/{job['id']}.log", "targets": targets,
                })
                summary["new_test_results"][job["name"]] = {
                    name: state for name, state in targets.items() if "/api_idempotency" in name
                }
        write(attempt / "checkout-commits.json", checkout_records)
        summary["verified_checkout_commits"] = list(checkout_records)
        summary["verified_source_tree"] = expected_tree
        for report in sorted((attempt / "artifacts").rglob("*.sarif")):
            diagnostics = [item for group in json.loads(report.read_text()).get("runs", [])
                           for item in group.get("results", [])]
            counts = {}
            for diagnostic in diagnostics:
                level = diagnostic.get("level", "warning")
                counts[level] = counts.get(level, 0) + 1
            summary["lint_findings"][report.name] = {
                "count": len(diagnostics), "levels": counts,
                "new_test_directory_findings": sum(
                    "score/mw/com/test/api_idempotency/" in json.dumps(item) for item in diagnostics),
                "report": str(report.relative_to(attempt)),
            }
    write(attempt / "summary.json", summary)
    if options.final:
        write(attempt / "artifact-manifest.json", {
            "subject": run["head_sha"], "run_attempt": run["run_attempt"],
            "files": {str(path.relative_to(attempt)): sha(path) for path in sorted(attempt.rglob("*"))
                      if path.is_file() and path.name != "artifact-manifest.json"},
        })
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
