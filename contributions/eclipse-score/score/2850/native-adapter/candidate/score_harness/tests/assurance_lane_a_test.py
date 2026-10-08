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
"""Public corpus replay and regression checks for the deterministic Lane A loop."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from score_harness.consistency import check_impacts, needs
from score_harness.coverage import extract_metrics
from score_harness.evaluate import (
    artifact,
    coverage_args,
    evaluate,
    gate,
    workspace_path,
)
from score_harness.query_runs import read_summary

ROOT = Path(__file__).resolve().parents[2]
CORPUS = ROOT / "score_harness/corpus"


@pytest.mark.parametrize("candidate", ["base_harness", "pinned_context_harness"])
@pytest.mark.parametrize("split,count", [("search", 30), ("heldout", 10)])
def test_native_corpus(candidate: str, split: str, count: int, tmp_path: Path) -> None:
    summary = evaluate(
        ROOT / f"score_harness/harness/{candidate}.py",
        CORPUS,
        tmp_path,
        1,
        split,
        external_checks=False,
    )
    assert summary["tasks_total"] == summary["tasks_correct"] == count
    assert read_summary(tmp_path / "evolution_summary.jsonl") == [summary]
    run = tmp_path / "iteration_001" / candidate
    assert (
        json.loads((run / "meta.json").read_text())["executor"]
        == "snapshot_fixture_replay"
    )
    for trace in (run / "traces").iterdir():
        assert {
            "gate_output.json",
            "impacted_elements.json",
            "score.json",
            "agent_diff.patch",
        } <= {p.name for p in trace.iterdir()}
        score = json.loads((trace / "score.json").read_text())
        assert score["impacts_correct"] and score["gate_verdict_correct"]
        assert len(score["provenance"]["gate_script_version"]) == 64
        assert {
            "execution_timestamp",
            "python_version",
            "environment_hash",
            "responsible_role",
            "escalation_role",
            "waiver_authority",
        } <= score["provenance"].keys()
    with pytest.raises(ValueError, match="append-only"):
        evaluate(
            ROOT / f"score_harness/harness/{candidate}.py",
            CORPUS,
            tmp_path,
            1,
            split,
            external_checks=False,
        )


def test_disjoint_corpus() -> None:
    search = list((CORPUS / "search").glob("*/task.json"))
    heldout = list((CORPUS / "heldout").glob("*/task.json"))
    assert len(search) == 30 and len(heldout) == 10
    search_ids: set[str] = set[str]().union(
        *(
            needs(json.loads(p.with_name("after.json").read_text())).keys()
            for p in search
        )
    )
    heldout_ids: set[str] = set[str]().union(
        *(
            needs(json.loads(p.with_name("after.json").read_text())).keys()
            for p in heldout
        )
    )
    assert not search_ids & heldout_ids
    assert all(p.with_name("spec.md").is_file() for p in search + heldout)


@pytest.mark.parametrize(
    "bad", ["../escape.json", "/etc/passwd", "", "https://example.org/file"]
)
def test_reject_corpus_escape(bad: str, tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        artifact(tmp_path / "task.json", bad)


def test_reject_symlink_artifact(tmp_path: Path) -> None:
    path = tmp_path / "file.json"
    path.write_text("{}")
    (tmp_path / "link.json").symlink_to(path)
    with pytest.raises(ValueError):
        artifact(tmp_path / "task.json", "link.json")


def test_invalid_needs_and_rule() -> None:
    with pytest.raises(ValueError, match="select"):
        needs({"versions": {"v1": {"needs": {}}}})
    with pytest.raises(ValueError, match="must match"):
        needs({"needs": {"A": {"id": "B"}}})
    with pytest.raises(ValueError, match="unknown"):
        check_impacts({"needs": {}}, {"needs": {}}, rules=["CR-999"])


def test_rule_selection_and_new_broken_link() -> None:
    after: dict[str, Any] = {
        "needs": {"R": {"id": "R", "type": "tool_req", "testlink": ["missing"]}}
    }
    assert check_impacts({"needs": {}}, after, rules=["CR-001"]) == []
    assert check_impacts({"needs": {}}, after, rules=["CR-003"]) == [
        {
            "need_id": "R",
            "rule_id": "CR-003",
            "impact_class": "revision_required",
            "reason": "broken_test_reference",
        }
    ]


@pytest.mark.parametrize("tool", ["ruff", "basedpyright"])
def test_missing_validation_tool_fails(
    tool: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    from score_harness.validate_candidate import external_check

    def missing(*args: Any, **kwargs: Any) -> Any:
        raise FileNotFoundError(tool)

    monkeypatch.setattr("score_harness.validate_candidate.subprocess.run", missing)
    assert external_check([tool], "linting_error")[0]["failure_type"] == "missing_tool"


def test_workspace_paths_preserve_read_boundary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("BUILD_WORKSPACE_DIRECTORY", str(tmp_path))
    assert (
        workspace_path(Path("score_harness/corpus"))
        == tmp_path / "score_harness/corpus"
    )
    assert workspace_path(tmp_path / "absolute") == tmp_path / "absolute"


def test_broken_refs_do_not_falsify_coverage_regression(tmp_path: Path) -> None:
    task = CORPUS / "search/search_001/before.json"
    snapshot = json.loads(task.read_text())
    items = needs(snapshot)
    requirement = next(
        need
        for need in items.values()
        if need["type"] == "tool_req" and need.get("implemented") == "YES"
    )
    testcase = next(need for need in items.values() if need["type"] == "testcase")
    requirement["testlink"] = []
    testcase["fully_verifies"] = ["synthetic_missing_requirement"]
    metrics = extract_metrics(snapshot, ["tool_req"])
    args = ["--min-req-test", "0", "--fail-on-broken-test-refs"]
    script = ROOT / "scripts_bazel/traceability_gate.py"
    assert not gate(metrics, tmp_path / "full.json", script, args)["gate_passed"]
    assert gate(metrics, tmp_path / "coverage.json", script, coverage_args(args))[
        "gate_passed"
    ]
    with pytest.raises(RuntimeError):
        gate(metrics, tmp_path / "invalid.json", script, ["--invalid-gate-option"])
