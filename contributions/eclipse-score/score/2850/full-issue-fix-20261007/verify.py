"""Verify this portable packet without running its candidate or native source code."""

import hashlib
import json
from pathlib import Path
import re
import tarfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent
BASELINE = "102aad30bd373295d275722c3942b392a8eb7149"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(name):
    return json.loads((ROOT / name).read_text())


def source_files():
    files = {}
    with tarfile.open(ROOT / "source/current.tar.gz") as archive:
        for member in archive:
            require(member.isfile(), "Current source archive must contain regular files only")
            name = Path(member.name)
            require(not name.is_absolute() and ".." not in name.parts, "Unsafe source archive path")
            require(member.name not in files, "Duplicate source archive entry")
            stream = archive.extractfile(member)
            require(stream is not None, "Missing source archive data")
            files[member.name] = stream.read()
    require({name: sha(data) for name, data in files.items()} == read("source/source-hashes.json"), "Current source vector mismatch")
    baseline = read("source/baseline-hashes.json")
    require(baseline["commit"] == BASELINE, "Wrong native baseline")
    for name in [".bazelversion", "MODULE.bazel", "MODULE.bazel.lock", "src/requirements.txt", "src/requirements_py314.txt", "scripts_bazel/traceability_gate.py", "scripts_bazel/traceability_metrics_schema.json", "src/extensions/score_metamodel/metamodel.yaml", "src/extensions/score_metrics/traceability_metrics.py"]:
        require(sha(files[name]) == baseline["files"][name], f"Fixed native contract changed: {name}")
    return files


def verify_runs(store, files):
    tasks = {task["task_id"]: task for task in json.loads(files["assurance/corpus/index.json"])["tasks"]}
    require(len(tasks) == 40, "Expected 40 public scenarios")
    require(sum(task["split"] == "search" for task in tasks.values()) == 30, "Search split mismatch")
    require(sum(task["split"] == "heldout" for task in tasks.values()) == 10, "Heldout split mismatch")
    observed = set()
    index = [json.loads(line) for line in (store / "evolution_summary.jsonl").read_text().splitlines()]
    require(len(index) == 2, "Run index must include separate search and heldout evaluations")
    for iteration, split in [("001", "search"), ("002", "heldout")]:
        run = store / iteration / "baseline"
        summary = json.loads((run / "score.json").read_text())
        require(summary["split"] == split and summary["tasks"] == summary["matches_expectation"], "Baseline expectation failures")
        for path in sorted((run / "traces").iterdir()):
            row = json.loads((path / "score.json").read_text())
            task = tasks[row["task_id"]]
            require(task["split"] == split and row["task_id"] not in observed, "Task split or uniqueness error")
            observed.add(row["task_id"])
            require(row["gate_verdict"] == task["expected_gate_verdict"], "Native verdict mismatch")
            require(row["matches_expectation"] and row["expected_impacted_ids"] == sorted(task["expected_impacted_ids"]), "Expected impact list mismatch")
            impacts = json.loads((path / "impacted_elements.json").read_text())
            require(sorted({item["need_id"] for item in impacts}) == sorted(task["expected_impacted_ids"]), "Observed impact list mismatch")
            require(all(item["impact_class"] in {"direct_recheck", "indirect_propagation", "revision_required"} for item in impacts), "Invalid impact class")
            require((path / "agent_diff.patch").exists() and "coverage_delta" in row, "Missing diff or coverage delta")
            gate = json.loads((path / "gate_output.json").read_text())
            require(gate["status"] == row["gate_verdict"] and gate["exit_code"] == (0 if gate["status"] == "pass" else 2), "Native gate status mismatch")
            for suffix in ["stdout", "stderr"]:
                require(sha((run / "raw" / f"{row['task_id']}.{suffix}").read_bytes()) == gate[suffix + "_sha256"], "Raw gate output binding mismatch")
            for name, digest in row["input_hashes"].items():
                source = f"assurance/corpus/{task['input_path']}/{name}"
                require(sha(files[source]) == digest, "Task source hash mismatch")
            provenance = row["provenance"]
            for key, name in [("gate_script_version", "scripts_bazel/traceability_gate.py"), ("candidate_sha256", "assurance/candidates/baseline.py"), ("rule_catalog_sha256", "assurance/rules.json"), ("corpus_index_sha256", "assurance/corpus/index.json"), ("coverage_script_sha256", "scripts_bazel/traceability_coverage.py")]:
                require(provenance[key] == sha(files[name]), f"Provenance source mismatch: {key}")
            require(bool(re.fullmatch(r"[0-9a-f]{64}", provenance["environment_hash"])), "Invalid environment hash")
            require(all(provenance[key] for key in ["execution_timestamp", "python_version", "responsible_role", "escalation_role", "waiver_authority"]), "Incomplete provenance")
    require(observed == set(tasks), "Missing evaluated tasks")
    return len(observed)


def main():
    manifest = read("artifact-manifest.json")
    actual = {path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*") if path.is_file() and path.name != "artifact-manifest.json"}
    require(actual == set(manifest["files"]), "Packet inventory mismatch")
    for name, record in manifest["files"].items():
        data = (ROOT / name).read_bytes()
        require(len(data) == record["bytes"] and sha(data) == record["sha256"], f"Packet hash mismatch: {name}")
    files = source_files()
    evaluated = verify_runs(ROOT / "evidence/runs", files)
    for tag in ["312", "314"]:
        store = ROOT / f"evidence/native-runs-py{tag}"
        require(verify_runs(store, files) == 40, "Incomplete native CLI evaluation")
        for kind in ["tests", "build"]:
            record = read(f"evidence/checks/docs-all-{kind}-py{tag}-sealed-final.json")
            require(record["baseline_commit"] == BASELINE and record["exit_code"] == 0 and record["source_unchanged_during_check"], "Invalid native check receipt")
            require(record["subject_hashes"] == read("source/source-hashes.json"), "Native check source vector differs from exported source")
        logs = ROOT / f"evidence/checks/docs-all-tests-py{tag}-sealed-final"
        xmls = list(logs.rglob("test.xml"))
        require(len(xmls) == 26, "Missing native test target reports")
        for path in xmls:
            tree = ET.parse(path)
            require(not list(tree.iter("failure")) and not list(tree.iter("error")), "Failed native test report")
    for label in ["docs-precommit-runtime-final", "docs-precommit-doc-final", "docs-render-spacing-final", "docs-patch-replay-sealed"]:
        record = read(f"evidence/checks/{label}.json")
        require(record["exit_code"] == 0, f"Required check did not pass: {label}")
    print(json.dumps({"integrity": "verified", "packet_files": len(actual), "source_files": len(files), "evaluated_scenarios_per_baseline": evaluated, "native_python_versions": ["3.12", "3.14"], "native_test_targets_per_version": 26, "native_acceptance": "pending", "merge_ready": False}, indent=2))


if __name__ == "__main__":
    main()
