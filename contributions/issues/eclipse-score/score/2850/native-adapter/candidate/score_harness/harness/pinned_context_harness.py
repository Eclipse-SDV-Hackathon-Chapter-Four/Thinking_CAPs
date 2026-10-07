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

"""Single-file, deterministic context adapter for score#2850.

Task input is a UTF-8 file or directory of prepared JSON/RST/Markdown/text.
``consistency_rules`` is an optional list of native rule IDs or explicit file
paths, relative to the input directory (or the input file's parent). Paths in document content,
RST includes, provenance and URLs are never followed. The caller owns scope
authorization; document text cannot expand that scope.

Requires POSIX descriptor-relative file access. No model or third-party imports.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
from pathlib import Path
from typing import Any, cast

from score_harness.harness.base_harness import AssuranceHarness

_SUFFIXES = {".json", ".rst", ".md", ".txt"}
_MAX_FILES = 128
_MAX_FILE_BYTES = 2 * 1024 * 1024
_MAX_TOTAL_BYTES = 8 * 1024 * 1024


def _path(value: Any, base: Path | None = None) -> Path:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ValueError("Expected a non-empty local path")
    if "://" in value:
        raise ValueError("URLs are not task inputs")
    path = Path(value)
    if ".." in path.parts:
        raise ValueError("Parent traversal is not permitted")
    if not path.is_absolute():
        path = (base or Path.cwd()) / path
    return path


def _open(path: Path) -> int:
    """Open every component without following links, including parent links."""
    descriptor = os.open(path.anchor, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for component in path.parts[1:]:
            child = os.open(
                component,
                os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=descriptor,
            )
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _files(descriptor: int, prefix: str = "") -> list[str]:
    """Enumerate a pinned directory; reject links and special files."""
    found: list[str] = []
    for name in sorted(os.listdir(descriptor)):
        relative = prefix + name
        mode = os.stat(name, dir_fd=descriptor, follow_symlinks=False).st_mode
        if stat.S_ISDIR(mode):
            child = os.open(
                name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=descriptor
            )
            try:
                found.extend(_files(child, relative + "/"))
            finally:
                os.close(child)
        elif stat.S_ISREG(mode):
            if Path(name).suffix in _SUFFIXES:
                found.append(relative)
        else:
            raise ValueError("Task input contains a link or special file")
        if len(found) > _MAX_FILES:
            raise ValueError("Too many context files")
    return found


def _reject_constant(value: str) -> Any:
    raise ValueError(f"Non-finite JSON constant: {value}")


def _object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _artifact(path: Path, scope: str, label: str) -> tuple[dict[str, Any], int]:
    if path.suffix not in _SUFFIXES:
        raise ValueError("Unsupported context file extension")
    descriptor = _open(path)
    with os.fdopen(descriptor, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise ValueError("Context references must be regular files")
        raw = stream.read(_MAX_FILE_BYTES + 1)
    if len(raw) > _MAX_FILE_BYTES:
        raise ValueError("Context file exceeds byte limit")
    text = raw.decode("utf-8")
    content = (
        json.loads(text, parse_constant=_reject_constant, object_pairs_hook=_object)
        if path.suffix == ".json"
        else text
    )
    return {
        "scope": scope,
        "path": label,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "trust": "untrusted_artifact",
        "content": content,
    }, len(raw)


def _inputs(path: Path) -> tuple[Path, list[tuple[Path, str, str]]]:
    descriptor = _open(path)
    try:
        if stat.S_ISDIR(os.fstat(descriptor).st_mode):
            names = _files(descriptor)
            return path, [(path / name, "input", name) for name in names]
        return path.parent, [(path, "input", path.name)]
    finally:
        os.close(descriptor)


def _rules(
    references: list[str], base: Path
) -> tuple[list[dict[str, Any]], list[tuple[Path, str, str]], int]:
    ids = sorted({ref for ref in references if re.fullmatch(r"CR-\d{3}", ref)})
    paths = sorted(set(references) - set(ids))
    selected: list[dict[str, Any]] = []
    size = 0
    if ids:
        # Native rule IDs reference this fixed, prepared catalog. Do not parse YAML
        # or discover files from document content at context construction time.
        catalog_path = Path(__file__).resolve().parent.parent / "consistency_rules.json"
        catalog, size = _artifact(
            catalog_path, "consistency_rule", "consistency_rules.json"
        )
        content = catalog["content"]
        if not isinstance(content, dict) or not isinstance(content.get("rules"), list):
            raise ValueError("Invalid native rule catalog")
        indexed: dict[str, dict[str, Any]] = {}
        definitions = cast(list[Any], content["rules"])
        for rule in definitions:
            if not isinstance(rule, dict) or not isinstance(rule.get("id"), str):
                raise ValueError("Invalid native rule definition")
            definition = cast(dict[str, Any], rule)
            rule_id: str = definition["id"]
            if rule_id in indexed:
                raise ValueError("Duplicate native rule ID")
            indexed[rule_id] = definition
        for rule_id in ids:
            if rule_id not in indexed:
                raise ValueError(f"Unknown native rule ID: {rule_id}")
            selected.append(
                {
                    "id": rule_id,
                    "catalog_path": "consistency_rules.json",
                    "catalog_sha256": catalog["sha256"],
                    "trust": "untrusted_artifact",
                    "content": indexed[rule_id],
                }
            )
    return (
        selected,
        [(_path(ref, base), "consistency_rule", ref) for ref in paths],
        size,
    )


class PinnedContextHarness(AssuranceHarness):
    """Context preparation only; native Lane A tools retain verdict authority."""

    def get_context(self, task_spec: dict[str, Any]) -> str:
        """Return canonical JSON with exact artifact content and byte hashes.

        No timestamps or generated need/rule IDs are added.
        Errors abort the whole operation instead of returning partial context.
        """
        base, inputs = _inputs(_path(task_spec["input_path"]))
        rules: list[Any] = task_spec.get("consistency_rules", [])
        if not isinstance(rules, list) or not all(isinstance(r, str) for r in rules):
            raise ValueError(
                "consistency_rules must be a list of rule IDs or file paths"
            )
        selected_rules, rule_files, catalog_size = _rules(cast(list[str], rules), base)
        inputs.extend(rule_files)
        if not inputs or len(inputs) + bool(selected_rules) > _MAX_FILES:
            raise ValueError("Expected between 1 and 128 context files")
        artifacts: list[dict[str, Any]] = []
        total = catalog_size
        for path, scope, label in inputs:
            artifact, size = _artifact(path, scope, label)
            artifacts.append(artifact)
            total += size
            if total > _MAX_TOTAL_BYTES:
                raise ValueError("Context exceeds total byte limit")
        return json.dumps(
            {
                "schema_version": "1",
                "task_id": task_spec.get("id", task_spec.get("task_id")),
                "artifacts": artifacts,
                "consistency_rules": selected_rules,
            },
            sort_keys=True,
            ensure_ascii=True,
            allow_nan=False,
            separators=(",", ":"),
        )

    def post_process(
        self, agent_output: str, task_spec: dict[str, Any]
    ) -> dict[str, Any]:
        """Keep output inert. No verdict or validation claim is inferred from it."""
        if not isinstance(agent_output, str):
            raise ValueError("agent_output must be text")
        return {
            "agent_output": agent_output,
            "task_id": task_spec.get("id", task_spec.get("task_id")),
        }
