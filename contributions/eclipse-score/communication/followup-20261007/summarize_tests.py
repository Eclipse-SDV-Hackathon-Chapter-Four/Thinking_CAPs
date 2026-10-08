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

"""Account for discovered, executed, delegated and unavailable native tests."""
from collections import Counter
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent


def summarize():
    discovery = json.loads((ROOT / "current-test-denominator.json").read_text())
    stdout = (ROOT / "evidence/current-native-host-tests.stdout").read_text()
    executed = dict(re.findall(r"^(//\S+)\s+(PASSED|SKIPPED|FLAKY)\b", stdout, re.M))
    graph = (ROOT / "evidence/current-configured-forwarders.stdout").read_text()
    rules = {item["label"]: item for item in discovery["tests"]}
    forwarded = {}
    for left, right in re.findall(r'"([^"\n]+)" -> "([^"\n]+)"', graph):
        parents = re.findall(r"(//[^\s\\]+) \([a-f0-9]+\)", left)
        children = re.findall(r"(//[^\s\\]+) \([a-f0-9]+\)", right)
        for parent in parents:
            if rules.get(parent, {}).get("kind") != "_forwarding_test":
                continue
            for child in children:
                if rules.get(child, {}).get("manual") and executed.get(parent) in ("PASSED", "FLAKY"):
                    forwarded.setdefault(child, []).append(parent)
    tests = []
    for item in discovery["tests"]:
        item = dict(item)
        label = item["label"]
        if label in executed:
            item["disposition"] = executed[label].lower()
        elif label in forwarded:
            item["disposition"] = "selected-manual-test-executed-through-passing-forwarder"
            item["passing_forwarders"] = sorted(set(forwarded[label]))
        elif "@platforms//os:qnx" in item["declared_constraints"]:
            item["disposition"] = "not-executed-in-linux-profile-qnx-obligation-outstanding"
        elif item["manual"]:
            item["disposition"] = "manual-not-directly-selected-no-pass-claimed"
        else:
            item["disposition"] = "unaccounted-nonmanual-test"
        tests.append(item)
    summary = {"source_revision": discovery["source_revision"],
               "host_record": "evidence/current-native-host-tests.json",
               "configured_forwarder_record": "evidence/current-configured-forwarders.json",
               "unconfigured_rules": len(tests), "manual_rules": sum(t["manual"] for t in tests),
               "direct_host_results": dict(Counter(executed.values())),
               "dispositions": dict(Counter(t["disposition"] for t in tests)),
               "limits": "Passing forwarders execute their configured manual actual dependency; this is not a second separately selected test execution. QNX, skipped and unselected rules are not reported as passed.",
               "tests": tests}
    assert not any(t["disposition"] == "unaccounted-nonmanual-test" for t in tests)
    (ROOT / "test-dispositions.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "tests"}, indent=2))


if __name__ == "__main__":
    summarize()
