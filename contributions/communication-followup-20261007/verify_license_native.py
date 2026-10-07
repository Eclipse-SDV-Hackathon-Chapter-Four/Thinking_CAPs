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

"""Refresh native analyzer evidence after notices move source line numbers."""
import json
import time

from measure import PACKET, ROOT, bazel


def execute():
    finished = PACKET / "evidence/license-headers-all-build.json"
    while not finished.exists():
        time.sleep(1)
    if json.loads(finished.read_text())["exit_code"]:
        raise RuntimeError("Complete build must pass before extraction")
    database = ROOT / "license-final-production-db"
    checks = [
        ("license-headers-production-extraction", ["run", "//quality/static_analysis:codeql_lint", "--jobs=8", "--",
            "--phase", "create-database", "--database-path", str(database), "--production-targets",
            "--audit-source", "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp",
            "--target", "//score/message_passing", "//score/mw/com"]),
        ("license-headers-native-analyzer-reporting", ["run", "//quality/static_analysis:codeql_lint", "--jobs=8", "--",
            "--phase", "analyze-database", "--database-path", str(database),
            "--output-dir", str(ROOT / "license-final-native-reporting"), "--output-prefix", "communication",
            "--audit-source", "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"]),
    ]
    for name, args in checks:
        record = bazel(name, args)
        if record["exit_code"] or record["changed_during_execution"]:
            raise RuntimeError(name)


if __name__ == "__main__":
    execute()
