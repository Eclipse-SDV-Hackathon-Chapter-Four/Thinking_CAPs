# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
"""Lane A outer loop: immutable public change fixtures, no model or network.

A snapshot executor replays the specified before/after change. It does not claim
agent performance. Native coverage and gate semantics remain unchanged.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from jsonschema_rs import Draft202012Validator

from score_harness.common import load_harness
from score_harness.consistency import check_impacts
from score_harness.coverage import extract_metrics
from score_harness.validate_candidate import validate_candidate


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.write_text(
        json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8"
    )


def artifact(task_path: Path, value: str) -> Path:
    """Corpus references are local immutable files inside one scenario directory."""
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts or not value:
        raise ValueError("corpus references must be local paths without traversal")
    result = task_path.parent / relative
    if result.is_symlink() or not result.is_file():
        raise ValueError(f"missing or symlink corpus artifact: {value}")
    if not result.resolve().is_relative_to(task_path.parent.resolve()):
        raise ValueError("corpus artifact escaped its scenario")
    return result


def gate(
    metrics: dict[str, Any], path: Path, script: Path, args: list[str]
) -> dict[str, Any]:
    schema = json.loads(
        script.with_name("traceability_metrics_schema.json").read_text()
    )
    Draft202012Validator(schema).validate(metrics)
    dump(path, metrics)
    process = subprocess.run(
        [sys.executable, str(script), "--metrics-json", str(path), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    # Raw output is collector evidence, separated from proposer trace fields.
    path.with_suffix(".stdout.log").write_text(process.stdout)
    path.with_suffix(".stderr.log").write_text(process.stderr)
    if process.returncode not in (0, 2) or process.stderr.strip():
        raise RuntimeError(f"gate infrastructure failed ({process.returncode})")
    return {
        "gate_passed": process.returncode == 0,
        "gate_returncode": process.returncode,
        "metrics_sha256": sha(path),
        "schema_valid": True,
    }


def coverage_delta(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for kind, values in after["metrics_by_type"].items():
        previous = before["metrics_by_type"].get(kind, {}).get("requirements", {})
        result[kind] = {
            key: values["requirements"][key] - previous.get(key, 0)
            for key in ("with_test_link_pct", "with_code_link_pct", "fully_linked_pct")
        }
    return result


def validate_before_run(
    candidate: Path,
    task_path: Path,
    output: Path,
    iteration: int,
    external_checks: bool,
) -> dict[str, Any]:
    first = json.loads(task_path.read_text())
    tiny = dict(
        first,
        input_path=str(artifact(task_path, first["after"])),
        needs_json_path=str(artifact(task_path, first["after"])),
    )
    # A real cheap validation happens before any full evaluation. Tests exercise
    # the interface without spawning linters; CI and CLI require their tools.
    output.mkdir(parents=True, exist_ok=True)
    validation_file = output / f".validation-{candidate.stem}-{iteration}.json"
    dump(validation_file, tiny)
    try:
        validation = validate_candidate(
            candidate, validation_file, skip_external_checks=not external_checks
        )
    finally:
        validation_file.unlink()
    if validation["status"] != "ok":
        raise ValueError(f"candidate validation failed: {validation}")
    return validation


def evaluate(
    candidate: Path,
    corpus: Path,
    output: Path,
    iteration: int,
    split: str,
    *,
    external_checks: bool = True,
) -> dict[str, Any]:
    candidate = candidate.resolve()
    corpus = corpus.resolve()
    output = output.resolve()
    root = Path(__file__).resolve().parent.parent
    script = root / "scripts_bazel/traceability_gate.py"
    tasks = sorted((corpus / split).glob("*/task.json"))
    if not tasks:
        raise ValueError("empty corpus split")
    if iteration < 1 or not re.fullmatch(r"[A-Za-z0-9_-]+", candidate.stem):
        raise ValueError("invalid iteration or candidate name")
    run = output / f"iteration_{iteration:03d}" / candidate.stem
    if run.exists():
        raise ValueError("append-only run already exists; use a new iteration")
    harness = load_harness(candidate)
    validation = validate_before_run(
        candidate, tasks[0], output, iteration, external_checks
    )
    run.mkdir(parents=True)
    (run / "traces").mkdir()
    tool_subjects = {
        "candidate": sha(candidate),
        "gate": sha(script),
        "metrics_schema": sha(script.with_name("traceability_metrics_schema.json")),
        "metrics_implementation": sha(
            root / "src/extensions/score_metamodel/traceability_metrics.py"
        ),
        "rules": sha(root / "score_harness/consistency_rules.json"),
        "checks": sha(Path(__file__).with_name("consistency.py")),
        "evaluator": sha(Path(__file__)),
        "locks": sha(root / "src/requirements.txt"),
    }
    environment: dict[str, Any] = {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "subjects": tool_subjects,
    }
    environment_hash = hashlib.sha256(
        json.dumps(environment, sort_keys=True).encode()
    ).hexdigest()
    dump(
        run / "meta.json",
        {
            "hypothesis": "Task-scoped rule context supports reproducible change review",
            "expected_outcome": "native verdicts and impacts match the published fixture oracles",
            "what_changed": "deterministic replay of each public before/after snapshot",
            "executor": "snapshot_fixture_replay",
            "split": split,
            "validation": validation,
            "environment": environment,
            "external_checks": external_checks,
        },
    )
    score_validator = Draft202012Validator(
        json.loads(Path(__file__).with_name("trace_score.schema.json").read_text())
    )
    results: list[dict[str, Any]] = []
    for task_path in tasks:
        task = json.loads(task_path.read_text())
        task_id = task["id"]
        if not re.fullmatch(r"[A-Za-z0-9_-]+", task_id) or task_id in {
            r["task_id"] for r in results
        }:
            raise ValueError("unsafe or duplicate task ID")
        if task["split"] != split:
            raise ValueError("split mismatch")
        before_path, after_path = (
            artifact(task_path, task[field]) for field in ("before", "after")
        )
        before, after = (
            json.loads(path.read_text()) for path in (before_path, after_path)
        )
        trace = run / "traces" / task_id
        trace.mkdir()
        scoped = dict(task, input_path=str(after_path), needs_json_path=str(after_path))
        context = harness.get_context(scoped)
        if not isinstance(context, str) or context != harness.get_context(scoped):
            raise ValueError("candidate context must be a deterministic string")
        (trace / "context.json").write_text(context)
        if not isinstance(harness.post_process("", scoped), dict):
            raise ValueError("candidate post_process must return an object")
        types = task.get("metric_types", ["tool_req"])
        before_metrics, after_metrics = (
            extract_metrics(snapshot, types) for snapshot in (before, after)
        )
        before_gate = gate(
            before_metrics, trace / "before_metrics.json", script, task["gate_args"]
        )
        after_gate = gate(
            after_metrics, trace / "metrics.json", script, task["gate_args"]
        )
        coverage_gate = gate(
            after_metrics,
            trace / "coverage_metrics.json",
            script,
            coverage_args(task["gate_args"]),
        )
        dropped = before_gate["gate_passed"] and not coverage_gate["gate_passed"]
        impacts = check_impacts(
            before, after, coverage_dropped=dropped, rules=task["consistency_rules"]
        )
        actual = [
            {key: impact[key] for key in ("need_id", "rule_id", "impact_class")}
            for impact in impacts
        ]

        def order(item: dict[str, str]) -> tuple[str, str, str]:
            return item["need_id"], item["rule_id"], item["impact_class"]

        impacts_correct = sorted(actual, key=order) == sorted(
            task["expected_impacts"], key=order
        )
        gate_correct = after_gate["gate_passed"] == (task["expected_verdict"] == "pass")
        dump(
            trace / "gate_output.json",
            dict(after_gate, before_gate_passed=before_gate["gate_passed"]),
        )
        dump(trace / "impacted_elements.json", impacts)
        patch = "".join(
            difflib.unified_diff(
                before_path.read_text().splitlines(True),
                after_path.read_text().splitlines(True),
                fromfile="before/needs.json",
                tofile="after/needs.json",
            )
        )
        (trace / "agent_diff.patch").write_text(patch)
        provenance: dict[str, Any] = {
            "execution_timestamp": datetime.now(UTC).isoformat(),
            "python_version": platform.python_version(),
            "environment_hash": environment_hash,
            "gate_script_version": tool_subjects["gate"],
            "task_spec_sha256": sha(task_path),
            "before_sha256": sha(before_path),
            "after_sha256": sha(after_path),
            "responsible_role": task.get("responsible_role", "pr_creator"),
            "escalation_role": task.get("escalation_role", "harness_maintainer"),
            "waiver_authority": task.get("waiver_authority", "release_approver"),
        }
        score: dict[str, Any] = {
            "task_id": task_id,
            "gate_passed": after_gate["gate_passed"],
            "expected_verdict": task["expected_verdict"],
            "gate_verdict_correct": gate_correct,
            "impacts_correct": impacts_correct,
            "verdict_correct": gate_correct and impacts_correct,
            "coverage_delta": coverage_delta(before_metrics, after_metrics),
            "provenance": provenance,
            "executor": "snapshot_fixture_replay",
            "context_sha256": sha(trace / "context.json"),
        }
        score_validator.validate(score)
        dump(trace / "score.json", score)
        results.append(score)
    summary: dict[str, Any] = {
        "candidate": candidate.stem,
        "iteration": iteration,
        "split": split,
        "tasks_total": len(results),
        "tasks_correct": sum(r["verdict_correct"] for r in results),
        "timestamp": datetime.now(UTC).isoformat(),
        "environment_hash": environment_hash,
    }
    summary["pass_rate"] = summary["tasks_correct"] / summary["tasks_total"]
    dump(
        run / "score.json",
        dict(
            summary,
            coverage_delta={r["task_id"]: r["coverage_delta"] for r in results},
            provenance=tool_subjects,
        ),
    )
    with (output / "evolution_summary.jsonl").open("a") as stream:
        stream.write(json.dumps(summary, sort_keys=True) + "\n")
    return summary


def workspace_path(path: Path) -> Path:
    workspace = os.getenv("BUILD_WORKSPACE_DIRECTORY")
    return Path(workspace) / path if workspace and not path.is_absolute() else path


def coverage_args(args: list[str]) -> list[str]:
    result = [
        arg
        for arg in args
        if arg not in {"--fail-on-broken-test-refs", "--require-all-links"}
    ]
    if "--require-all-links" in args:
        result.extend(
            [
                "--min-req-code",
                "100",
                "--min-req-test",
                "100",
                "--min-req-fully-linked",
                "100",
                "--min-tests-linked",
                "100",
            ]
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--corpus", type=Path, default=Path("score_harness/corpus"))
    parser.add_argument("--output-dir", type=Path, default=Path("score_harness/runs"))
    parser.add_argument("--iteration", type=int, default=1)
    parser.add_argument("--split", choices=("search", "heldout"), default="search")
    args = parser.parse_args()
    result = evaluate(
        workspace_path(args.candidate),
        workspace_path(args.corpus),
        workspace_path(args.output_dir),
        args.iteration,
        args.split,
    )
    print(json.dumps(result, indent=2))
    if result["tasks_correct"] != result["tasks_total"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
