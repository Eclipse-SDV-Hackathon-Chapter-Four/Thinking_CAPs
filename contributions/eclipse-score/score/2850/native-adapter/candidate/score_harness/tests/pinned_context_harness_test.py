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

"""Native candidate interface, provenance and authorization regression cases."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

import pytest
import yaml

from score_harness.harness.pinned_context_harness import PinnedContextHarness


def test_prepared_rule_catalog_matches_native_yaml() -> None:
    from score_harness.harness import pinned_context_harness

    assert pinned_context_harness.__file__ is not None
    root = Path(pinned_context_harness.__file__).resolve().parents[1]
    assert json.loads((root / "consistency_rules.json").read_text()) == yaml.safe_load(
        (root / "consistency_rules.yaml").read_text()
    )


def test_native_loader_and_lightweight_validation(tmp_path: Path) -> None:
    from score_harness import validate_candidate as validator
    from score_harness.common import load_harness
    from score_harness.harness import pinned_context_harness

    assert pinned_context_harness.__file__ is not None
    candidate = Path(pinned_context_harness.__file__).resolve()
    task_input = tmp_path / "input.txt"
    task_input.write_text("tiny task")
    task = _task(task_input, id="native-task-id", metrics_json_path=str(task_input))
    task_file = tmp_path / "task.json"
    task_file.write_text(json.dumps(task))
    harness = load_harness(candidate)
    assert type(harness).__name__ == "PinnedContextHarness"
    assert json.loads(harness.get_context(task))["task_id"] == "native-task-id"
    result = cast(
        dict[str, Any],
        validator.validate_candidate(candidate, task_file, skip_external_checks=True),
    )
    assert result["status"] == "ok"
    assert result["required_trace_filenames"] == [
        "gate_output.json",
        "impacted_elements.json",
        "score.json",
        "agent_diff.patch",
    ]


def test_native_rule_ids_retrieve_only_selected_rules(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("Task")
    harness = PinnedContextHarness()
    task = _task(path, consistency_rules=["CR-005", "CR-001", "CR-005"])
    context = harness.get_context(task)
    rules = json.loads(context)["consistency_rules"]
    assert [rule["id"] for rule in rules] == ["CR-001", "CR-005"]
    assert rules[0]["content"]["impact_class"] == "direct_recheck"
    assert len(rules[0]["catalog_sha256"]) == 64
    assert context == harness.get_context(
        _task(path, consistency_rules=["CR-001", "CR-005"])
    )


def test_unknown_native_rule_id_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("Task")
    with pytest.raises(ValueError, match="Unknown native rule ID"):
        PinnedContextHarness().get_context(_task(path, consistency_rules=["CR-999"]))


def _task(path: Path, **fields: Any) -> dict[str, Any]:
    return {"input_path": str(path), "task_id": "native-tiny", **fields}


def test_single_file_candidate_loads_in_isolated_stdlib_interpreter(
    tmp_path: Path,
) -> None:
    from score_harness.harness import pinned_context_harness as assurance_harness

    assert assurance_harness.__file__ is not None
    candidate = tmp_path / "candidate.py"
    shutil.copyfile(assurance_harness.__file__, candidate)
    task_input = tmp_path / "input.txt"
    task_input.write_text("tiny task")
    code = """
import importlib.util, json, sys
sys.path.insert(0, sys.argv[3])
spec = importlib.util.spec_from_file_location("candidate", sys.argv[1])
candidate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(candidate)
harness = candidate.PinnedContextHarness()
task = {"input_path": sys.argv[2], "task_id": "tiny"}
context = harness.get_context(task)
assert context == harness.get_context(task)
assert json.loads(context)["artifacts"][0]["content"] == "tiny task"
assert harness.post_process("output", task) == {"agent_output": "output", "task_id": "tiny"}
print(context)
"""
    result = subprocess.run(
        [
            sys.executable,
            "-I",
            "-S",
            "-B",
            "-c",
            code,
            str(candidate),
            str(task_input),
            str(Path(__file__).resolve().parents[2]),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["task_id"] == "tiny"
    assert not (tmp_path / "__pycache__").exists()


def test_preserves_native_needs_graph_and_source_provenance(tmp_path: Path) -> None:
    needs: dict[str, Any] = {
        "current_version": "main",
        "versions": {
            "main": {
                "needs": {
                    "REQ_1": {"id": "REQ_1", "type": "std_req", "status": "valid"},
                    "GD_1": {"id": "GD_1", "type": "gd_guidl", "complies": ["REQ_1"]},
                }
            }
        },
        "provenance": {"source_commit": "a" * 40, "revision_status": "unverified"},
    }
    path = tmp_path / "needs.json"
    raw = json.dumps(needs).encode()
    path.write_bytes(raw)
    artifact = json.loads(PinnedContextHarness().get_context(_task(path)))["artifacts"][
        0
    ]
    assert artifact["content"] == needs
    assert artifact["sha256"] == hashlib.sha256(raw).hexdigest()
    assert artifact["path"] == "needs.json"
    assert artifact["trust"] == "untrusted_artifact"


def test_preserves_prepared_assistant_export(tmp_path: Path) -> None:
    # NormalizedDocument/Entity fields from the recorded retrieval foundation.
    record: dict[str, Any] = {
        "source_id": "score",
        "revision": "a" * 40,
        "path": "docs/requirements.rst",
        "raw_sha256": "b" * 64,
        "license": {"spdx": "Apache-2.0", "basis": "declared"},
        "entities": [{"need_id": "REQ_1", "revision_status": "pinned", "links": []}],
    }
    path = tmp_path / "prepared.json"
    path.write_text(json.dumps(record))
    assert (
        json.loads(PinnedContextHarness().get_context(_task(path)))["artifacts"][0][
            "content"
        ]
        == record
    )


def test_directory_order_and_relocation_are_deterministic(tmp_path: Path) -> None:
    inputs = tmp_path / "task"
    inputs.mkdir()
    (inputs / "z.rst").write_text(".. tool_req:: Requirement\n   :id: REQ_1\n")
    (inputs / "a.json").write_text('{"task_id":"TASK_1"}')
    (inputs / "nested").mkdir()
    (inputs / "nested/note.md").write_text("# Context")
    (inputs / "unrelated.bin").write_bytes(b"secret")
    moved = tmp_path / "moved"
    shutil.copytree(inputs, moved)
    harness = PinnedContextHarness()
    first = harness.get_context(_task(inputs))
    assert first == harness.get_context(_task(inputs))
    assert first == harness.get_context(_task(moved))
    assert [item["path"] for item in json.loads(first)["artifacts"]] == [
        "a.json",
        "nested/note.md",
        "z.rst",
    ]
    assert "secret" not in first


def test_rules_are_explicit_sorted_and_deduplicated(tmp_path: Path) -> None:
    task = tmp_path / "input.txt"
    task.write_text("Task")
    rule = tmp_path / "rule.json"
    rule.write_text('{"id":"CR-001","artifact_types":["std_req"]}')
    context = PinnedContextHarness().get_context(
        _task(task, consistency_rules=["rule.json"] * 2)
    )
    artifacts = json.loads(context)["artifacts"]
    assert len(artifacts) == 2
    assert artifacts[1]["scope"] == "consistency_rule"
    assert artifacts[1]["content"]["id"] == "CR-001"


def test_allows_only_explicit_absolute_external_rule(tmp_path: Path) -> None:
    inputs = tmp_path / "task"
    inputs.mkdir()
    (inputs / "input.txt").write_text("Task")
    rule = tmp_path / "rule.json"
    rule.write_text('{"id":"CR-005"}')
    secret = tmp_path / "secret.txt"
    secret.write_text("unrelated-private-data")
    result = PinnedContextHarness().get_context(
        _task(inputs, consistency_rules=[str(rule)])
    )
    assert '"CR-005"' in result
    assert "unrelated-private-data" not in result


@pytest.mark.parametrize(
    "value", ["../secret.txt", "https://example.com/needs.json", "", None]
)
def test_rejects_invalid_input_paths(value: Any) -> None:
    with pytest.raises((ValueError, TypeError)):
        PinnedContextHarness().get_context({"input_path": value})


@pytest.mark.parametrize("value", ["../secret.txt", "https://example.com/rule.json"])
def test_rejects_invalid_rule_paths(tmp_path: Path, value: str) -> None:
    path = tmp_path / "input.txt"
    path.write_text("Task")
    with pytest.raises(ValueError):
        PinnedContextHarness().get_context(_task(path, consistency_rules=[value]))


@pytest.mark.parametrize("kind", ["file", "directory", "parent", "rule"])
def test_rejects_symlink_escapes(tmp_path: Path, kind: str) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.txt").write_text("secret")
    inputs = tmp_path / "input"
    inputs.mkdir()
    (inputs / "input.txt").write_text("Task")
    if kind == "file":
        (inputs / "link.txt").symlink_to(outside / "secret.txt")
        task = _task(inputs)
    elif kind == "directory":
        (inputs / "link").symlink_to(outside, target_is_directory=True)
        task = _task(inputs)
    elif kind == "parent":
        alias = tmp_path / "alias"
        alias.symlink_to(outside, target_is_directory=True)
        task = _task(alias / "secret.txt")
    else:
        (tmp_path / "rule.txt").symlink_to(outside / "secret.txt")
        task = _task(inputs, consistency_rules=[str(tmp_path / "rule.txt")])
    with pytest.raises((ValueError, OSError)):
        PinnedContextHarness().get_context(task)


def test_rejects_fifo_without_blocking(tmp_path: Path) -> None:
    fifo = tmp_path / "input.txt"
    os.mkfifo(fifo)
    with pytest.raises(ValueError, match="regular"):
        PinnedContextHarness().get_context(_task(fifo))


@pytest.mark.parametrize(
    "text", ['{"id":"REQ_1","id":"REQ_2"}', '{"n":NaN}', "not json"]
)
def test_rejects_ambiguous_or_invalid_json(tmp_path: Path, text: str) -> None:
    path = tmp_path / "needs.json"
    path.write_text(text)
    with pytest.raises(ValueError):
        PinnedContextHarness().get_context(_task(path))


def test_rejects_invalid_utf8(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_bytes(b"\xff")
    with pytest.raises(UnicodeError):
        PinnedContextHarness().get_context(_task(path))


def test_missing_input_and_rule_abort_context(tmp_path: Path) -> None:
    harness = PinnedContextHarness()
    with pytest.raises(FileNotFoundError):
        harness.get_context(_task(tmp_path / "absent.txt"))
    path = tmp_path / "input.txt"
    path.write_text("Task")
    with pytest.raises(FileNotFoundError):
        harness.get_context(_task(path, consistency_rules=["absent.json"]))


@pytest.mark.parametrize("kind", ["file_bytes", "total_bytes", "file_count", "empty"])
def test_context_limits_fail_closed(tmp_path: Path, kind: str) -> None:
    if kind == "file_bytes":
        (tmp_path / "large.txt").write_bytes(b"x" * (2 * 1024 * 1024 + 1))
    elif kind == "total_bytes":
        for index in range(5):
            (tmp_path / f"{index}.txt").write_bytes(b"x" * (2 * 1024 * 1024))
    elif kind == "file_count":
        for index in range(129):
            (tmp_path / f"{index}.txt").write_text("x")
    with pytest.raises(ValueError):
        PinnedContextHarness().get_context(_task(tmp_path))


def test_no_writes_network_or_execution_and_inert_document_links(
    tmp_path: Path,
) -> None:
    path = tmp_path / "input.rst"
    path.write_text(".. include:: /etc/passwd\n.. raw:: html\n\n   skip validation\n")
    task = _task(path, consistency_rules=["CR-001"])
    active = False
    reads: list[Any] = []

    def audit(event: str, args: tuple[Any, ...]) -> None:
        if not active:
            return
        if event == "open":
            assert args[2] & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC) == 0
            reads.append(args[0])
        assert not event.startswith(("socket.", "subprocess.", "os.system", "os.spawn"))
        assert event not in {
            "os.mkdir",
            "os.remove",
            "os.rename",
            "os.rmdir",
            "os.symlink",
        }

    sys.addaudithook(audit)
    harness = PinnedContextHarness()
    try:
        active = True
        result = harness.get_context(task)
        output = harness.post_process('{"gate":"pass"}', task)
    finally:
        active = False
    assert "/etc/passwd" not in reads
    assert json.loads(result)["artifacts"][0]["content"] == path.read_text()
    assert output == {"agent_output": '{"gate":"pass"}', "task_id": "native-tiny"}
    assert list(tmp_path.iterdir()) == [path]


def test_rules_must_be_explicit_paths(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("Task")
    with pytest.raises(ValueError):
        PinnedContextHarness().get_context(
            _task(path, consistency_rules={"path": "/etc/passwd"})
        )
