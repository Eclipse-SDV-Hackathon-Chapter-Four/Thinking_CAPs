"""Reverify portable #1167 evidence; never execute native builds or grant acceptance."""

import csv
import hashlib
import json
import re
import tarfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent
RUN = ROOT / "final-review/verification-run"
RUN_ID = "01M4878Q65ENC6PJ5AEJ6NMWB3"
SOURCE_HASH = "ddccd8f68c44de2b6de920c42c8999189cc3d1845268d9ce6e8dbad3da860e98"


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path):
    return json.loads(path.read_text())


def require(condition, message):
    if not condition:
        raise ValueError(message)


def normalized_findings(path, cwd):
    findings = []
    for line in path.read_text().splitlines():
        clean = re.sub(r"\x1b\[[0-9;]*m", "", line)
        if clean.startswith("ERROR: "):
            findings.append(clean.removeprefix("ERROR: ").replace(cwd + "/", ""))
    return sorted(findings)


def finding_row(message):
    patterns = {
        "missing_headers": r"Missing copyright header in: (.+), use --fix",
        "wrong_format_headers": r"Wrong copyright format in: (.+) \(similarity",
        "headers_preceded_by_other_content": r"Copyright header in (.+) is preceded",
        "duplicate_headers": r"Duplicate copyright header in: (.+) \(repeated",
    }
    for category, pattern in patterns.items():
        match = re.match(pattern, message)
        if match:
            return {"category": category, "path": match.group(1),
                    "baseline_identical": "true", "message": message}
    raise ValueError(f"Unrecognized copyright finding: {message}")


def main():
    require(sha(RUN / "candidate-hashes.json") == SOURCE_HASH, "Source vector changed")
    source = load(RUN / "candidate-hashes.json")
    require(len(source) == 2885, "Unexpected source count")
    for relative, expected in source.items():
        require(sha(RUN / "candidate" / relative) == expected, f"Source changed: {relative}")
    preparation = load(ROOT / "submission/preparation-result.json")
    require(preparation["source_binding_sha256"] == SOURCE_HASH, "Submission subject differs")
    require(load(ROOT / "submission/candidate-hashes.json") == source, "Submission vector differs")
    require(sha(ROOT / "submission/source.tar.gz") == preparation["archive_sha256"], "Archive changed")
    with tarfile.open(ROOT / "submission/source.tar.gz", "r:gz") as archive:
        archived = {}
        for member in archive.getmembers():
            if member.isfile():
                stream = archive.extractfile(member)
                require(stream is not None, "Archive member unreadable")
                archived[member.name.removeprefix("./")] = hashlib.sha256(stream.read()).hexdigest()
        require(archived == source, "Archive subject differs")
    for name in ["communication-1167.patch", "issue-1167-tests.patch", "copyright-checker-paths.patch"]:
        require((ROOT / "submission" / name).read_bytes() == (RUN / name).read_bytes(), f"Patch differs: {name}")
    frozen = load(RUN / "frozen-inputs.json")
    for relative, expected in frozen.items():
        require(sha(RUN / relative) == expected, f"Frozen control changed: {relative}")
    checks = {}
    for name in ["build-all", "format", "focused", "test-all", "copyright"]:
        record = load(RUN / "evidence" / f"{name}.json")
        require(record["subject_sha256"] == source, f"Check subject differs: {name}")
        require(record["fabro_run_id"] == RUN_ID, f"Check run differs: {name}")
        for stream in ["stdout", "stderr"]:
            require(sha(RUN / "evidence" / f"{name}.{stream}") == record[f"{stream}_sha256"], f"Log changed: {name}.{stream}")
        require(record["exit_code"] == (1 if name == "copyright" else 0), f"Unexpected result: {name}")
        checks[name] = {"exit_code": record["exit_code"], "evidence": "carried_hash_reverified"}
    test_log = (RUN / "evidence/test-all.stdout").read_text()
    require("Executed 503 out of 509 tests: 503 tests pass and 6 were skipped." in test_log, "Suite summary differs")
    skips = re.findall(r"^(//\S+)\s+SKIPPED$", test_log, re.M)
    require(skips == load(RUN / "skipped-tests.json")["skipped_targets"], "Skip inventory differs")
    app = RUN / "evidence/native-testlogs/score/mw/com/test/api_idempotency/integration_test/api_idempotency_test/test.log"
    require("Application [main_api_idempotency] exit code: [0]" in app.read_text(), "Application exit differs")
    products = load(RUN / "native-artifacts/manifest.json")
    require(products["source_sha256"] == SOURCE_HASH and not products["missing_products"], "Product subject differs")
    for relative, record in products["files"].items():
        path = RUN / "native-artifacts" / relative
        require(sha(path) == record["sha256"] and path.stat().st_size == record["bytes"], f"Product changed: {relative}")
        require(record["run_id"] == RUN_ID, f"Product run differs: {relative}")
    baseline = load(ROOT / "follow-up/baseline-copyright-path-overlay.json")
    require(baseline["exit_code"] == 1, "Baseline check result differs")
    for stream in ["stdout", "stderr"]:
        require(sha(ROOT / "follow-up" / f"baseline-copyright-path-overlay.{stream}") == baseline[f"{stream}_sha256"], "Baseline log changed")
    require(all(source.get(path) == expected for path, expected in baseline["subject_sha256"].items()), "Baseline overlay projection differs")
    extra = sorted(set(source) - set(baseline["subject_sha256"]))
    require(len(extra) == 8 and all(path.startswith("score/mw/com/test/api_idempotency/") for path in extra), "Unexpected extra source")
    before = normalized_findings(ROOT / "follow-up/baseline-copyright-path-overlay.stderr", baseline["cwd"])
    current = load(RUN / "evidence/copyright.json")
    after = normalized_findings(RUN / "evidence/copyright.stderr", current["cwd"])
    comparison = load(ROOT / "follow-up/copyright-comparison.json")
    require(before == after == comparison["baseline_findings"], "Copyright findings differ")
    rows = [finding_row(message) for message in after]
    categories = dict(Counter(row["category"] for row in rows))
    require(categories == comparison["categories"] and len(rows) == 204, "Copyright inventory differs")
    require(not any(row["path"] in extra for row in rows), "New test has a copyright finding")
    decision_file = OUT / "human-decision.json"
    human_status = "pending"
    if decision_file.exists():
        decision = load(decision_file)
        require(decision["source_binding_sha256"] == SOURCE_HASH, "Human decision subject differs")
        human_status = decision["status"]
    with (OUT / "copyright-findings.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["category", "path", "baseline_identical", "message"])
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "status": "portable_evidence_reverified",
        "baseline": preparation["baseline"], "run_id": RUN_ID,
        "source_binding_sha256": SOURCE_HASH, "staged_git_tree": preparation["staged_git_tree"],
        "source_files_verified": len(source), "baseline_overlay_files_verified": len(baseline["subject_sha256"]),
        "new_test_files": extra, "frozen_controls_verified": len(frozen),
        "native_products_verified": len(products["files"]), "checks": checks,
        "full_suite": {"passed": 503, "failed": 0, "skipped": 6}, "skipped_targets": skips,
        "copyright": {"exit_code": 1, "count": 204, "categories": categories,
                      "identical_normalized_findings": True, "added": 0, "removed": 0,
                      "baseline_limitation": "filesystem-path overlay; untouched checker fails before scanning",
                      "proposed_disposition": "retain failed check; inherited header repair as separate scope",
                      "human_disposition": human_status, "waiver": False},
        "new_native_runs": 0, "new_paid_calls": 0, "human_acceptance": human_status,
    }
    (OUT / "evidence-verification.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": result["status"], "source_files": len(source),
                      "copyright_findings": len(rows), "added_findings": 0, "human_acceptance": human_status}))


if __name__ == "__main__":
    main()
