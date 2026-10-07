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
"""Executable CR-001–005 and reusable goal, solution and breakdown checks."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterator
from typing import Any, cast

LINK_FIELDS = ("complies", "supports", "requirements", "children", "evidence")
REQUIREMENT_TYPES = {
    "tool_req",
    "std_req",
    "process_requirement",
    "gd_req",
    "comp_req",
    "feat_req",
}
type NeedMap = dict[str, dict[str, Any]]
type Impact = tuple[str, str, str, str]


def links(value: Any) -> list[str]:
    if isinstance(value, str):
        return sorted({part.strip() for part in value.split(",") if part.strip()})
    if isinstance(value, list):
        items = cast(list[Any], value)
        if all(isinstance(item, str) for item in items):
            return sorted(set(cast(list[str], items)))
    if value is None:
        return []
    raise ValueError("links must be a CSV string or string list")


def needs(snapshot: dict[str, Any]) -> NeedMap:
    if "versions" in snapshot:
        version = snapshot.get("current_version")
        versions = snapshot["versions"]
        if version not in versions:
            raise ValueError("needs export must select its current_version")
        raw = versions[version]["needs"]
    else:
        raw = snapshot["needs"]
    if not isinstance(raw, dict):
        raise ValueError("needs must be an ID-keyed object")
    result = cast(NeedMap, raw)
    for key, value in result.items():
        if not isinstance(value, dict) or value.get("id") != key:
            raise ValueError("need key and id must match")
    return result


def compliance(
    source_id: str, source: dict[str, Any], old: NeedMap, new: NeedMap
) -> Iterator[Impact]:
    for target in links(source.get("complies")):
        if target in old and target not in new:
            yield source_id, "CR-001", "direct_recheck", "complies_target_removed"
        if target not in old or target not in new:
            continue
        if old[target]["type"] != new[target]["type"] and source.get("type") in {
            "gd_guidl",
            "gd_req",
        }:
            yield (
                source_id,
                "CR-002",
                "indirect_propagation",
                "requirement_type_changed",
            )
        if (
            old[target].get("type") == "std_req"
            and source.get("type") == "gd_guidl"
            and old[target].get("content") != new[target].get("content")
        ):
            yield (
                source_id,
                "CR-004",
                "indirect_propagation",
                "standard_content_changed",
            )


def regression(target: str, old: NeedMap, new: NeedMap) -> bool:
    return (
        target in new
        and new[target].get("result") in {"failed", "error"}
        and old.get(target, {}).get("result") not in {"failed", "error"}
    )


def broken_test(target: str, new: NeedMap) -> bool:
    return (
        target not in new
        or new[target].get("type") != "testcase"
        or any(
            ref not in new
            for field in ("fully_verifies", "partially_verifies")
            for ref in links(new[target].get(field))
        )
    )


def test_evidence(
    source_id: str, source: dict[str, Any], old: NeedMap, new: NeedMap
) -> Iterator[Impact]:
    if source.get("type") not in REQUIREMENT_TYPES:
        return
    for target in links(source.get("testlink", source.get("tests"))):
        if broken_test(target, new):
            yield source_id, "CR-003", "revision_required", "broken_test_reference"
        elif regression(target, old, new):
            yield source_id, "CR-003", "revision_required", "test_result_regression"


def goal(
    source_id: str, source: dict[str, Any], old: NeedMap, new: NeedMap
) -> Iterator[Impact]:
    if source.get("type") != "goal":
        return
    for target in links(source.get("requirements")):
        if target in old and (
            target not in new
            or any(
                old[target].get(field) != new[target].get(field)
                for field in ("content", "status")
            )
        ):
            yield source_id, "CR-001", "direct_recheck", "goal_support_changed"


def solution(
    source_id: str, source: dict[str, Any], old: NeedMap, new: NeedMap
) -> Iterator[Impact]:
    if source.get("type") != "solution":
        return
    for target in links(source.get("evidence")):
        if (target in old and target not in new) or regression(target, old, new):
            yield (
                source_id,
                "CR-003",
                "revision_required",
                "solution_evidence_invalidated",
            )


def breakdown(
    source_id: str, source: dict[str, Any], old: NeedMap, new: NeedMap
) -> Iterator[Impact]:
    for target in links(source.get("children")):
        if target in old and (
            target not in new
            or any(
                old[target].get(field) and not new[target].get(field)
                for field in ("testlink", "source_code_link")
            )
        ):
            yield source_id, "CR-005", "direct_recheck", "breakdown_coverage_lost"


def propagate(impact: Impact, new: NeedMap) -> set[Impact]:
    need_id, rule, _, _ = impact
    result = {impact}
    queue = deque([need_id])
    visited = {need_id}
    while queue:
        target = queue.popleft()
        for child_id, child in sorted(new.items()):
            if child_id not in visited and any(
                target in links(child.get(field)) for field in LINK_FIELDS
            ):
                visited.add(child_id)
                queue.append(child_id)
                result.add(
                    (child_id, rule, "indirect_propagation", "argument_dependency")
                )
    return result


def check_impacts(
    before: dict[str, Any],
    after: dict[str, Any],
    *,
    coverage_dropped: bool = False,
    rules: list[str] | None = None,
) -> list[dict[str, str]]:
    old, new = needs(before), needs(after)
    known = {f"CR-{n:03d}" for n in range(1, 6)}
    selected = set(rules) if rules is not None else known
    if selected - known:
        raise ValueError("unknown consistency rule")
    direct: set[Impact] = set()
    for source_id, source in sorted(new.items()):
        for check in (compliance, test_evidence, goal, solution, breakdown):
            direct.update(check(source_id, source, old, new))
    if coverage_dropped:
        direct.add(
            ("gate_verdict", "CR-005", "direct_recheck", "coverage_below_threshold")
        )
    found: set[Impact] = set()
    for impact in direct:
        if impact[1] in selected:
            found.update(propagate(impact, new))
    return [
        dict(need_id=i, rule_id=r, impact_class=c, reason=why)
        for i, r, c, why in sorted(found)
    ]
