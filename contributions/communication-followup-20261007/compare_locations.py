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

"""Recheck the portable before/after SARIF location evidence."""
from collections import Counter
from copy import deepcopy
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent


def artifact_locations(value):
    if isinstance(value, dict):
        if "artifactLocation" in value:
            yield value["artifactLocation"]
        for child in value.values():
            yield from artifact_locations(child)
    elif isinstance(value, list):
        for child in value:
            yield from artifact_locations(child)


def uris(value):
    if isinstance(value, dict):
        if "uri" in value:
            yield value["uri"]
        for child in value.values():
            yield from uris(child)
    elif isinstance(value, list):
        for child in value:
            yield from uris(child)


def canonical_location(value, run):
    value = deepcopy(value)
    for artifact in artifact_locations(value):
        if "uri" not in artifact and "index" in artifact:
            artifact.update(run["artifacts"][artifact["index"]]["location"])
        artifact.pop("index", None)
    return value


def primary_findings(sarif):
    return Counter(
        json.dumps(
            [result.get("ruleId"), canonical_location(result.get("locations", []), run),
             result.get("partialFingerprints", {})], sort_keys=True
        )
        for run in sarif["runs"] for result in run.get("results", [])
    )


def located_related_links(sarif):
    output = Counter()
    for run in sarif["runs"]:
        for result in run.get("results", []):
            for link in result.get("relatedLocations", []):
                physical = canonical_location(link.get("physicalLocation", {}), run)
                uri = physical.get("artifactLocation", {}).get("uri", "")
                if uri and uri not in ("file:", "file:/", "file://", "file:///"):
                    output[json.dumps(physical, sort_keys=True)] += 1
    return output


def check():
    before = json.loads((ROOT / "evidence/1104-original.sarif").read_text())
    after = json.loads((ROOT / "evidence/1104-fixed.sarif").read_text())
    placeholders = ("file:", "file:/", "file://", "file:///")
    old_links, new_links = located_related_links(before), located_related_links(after)
    summary = {
        "before_findings": sum(primary_findings(before).values()),
        "after_findings": sum(primary_findings(after).values()),
        "before_empty_file_uris": sum(uri in placeholders for uri in uris(before)),
        "after_empty_file_uris": sum(uri in placeholders for uri in uris(after)),
        "primary_findings_and_fingerprints_preserved": primary_findings(before) == primary_findings(after),
        "original_located_related_links_preserved": not bool(old_links - new_links),
    }
    print(json.dumps(summary, indent=2))
    return (summary["before_findings"] == summary["after_findings"] == 501
            and summary["before_empty_file_uris"] == 281
            and summary["after_empty_file_uris"] == 0
            and summary["primary_findings_and_fingerprints_preserved"]
            and summary["original_located_related_links_preserved"])


if __name__ == "__main__":
    sys.exit(not check())
