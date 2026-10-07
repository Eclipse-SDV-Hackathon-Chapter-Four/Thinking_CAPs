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

"""Finish current-main checks after the in-flight source-bound host test run."""
import json
from pathlib import Path
import shutil
import time

from measure import PACKET, ROOT, TOOLS, bazel, container_command, run


def execute():
    host = PACKET / "evidence/current-native-host-tests.json"
    while not host.exists():
        time.sleep(1)
    result = json.loads(host.read_text())
    if result["exit_code"] or result["changed_during_execution"]:
        raise RuntimeError("Current host tests failed or their inputs changed")

    source = ROOT / "candidate"
    analyzer = source / "quality/static_analysis/codeql_lint.py"
    analyzer.write_text(analyzer.read_text().replace("import sys\n", ""))
    ci = source / "CI.md"
    marker = "Also, it lints the files to ensure the basic Bazel best practices.\n"
    addition = """
The buildifier job in `_linter.yml` checks formatting and rejects buildifier
warnings with the module-pinned tool. Reproduce it locally with
`bazel run //tools/lint/buildifier:buildifier_lint -- --recursive`; its diagnostic output
identifies the offending file and line. Run the positive/negative regression
fixtures with `bazel test //tools/lint/buildifier:buildifier_lint_test`.
The separate `format.check` command checks formatting; this lint job also
enforces the warning policy.
"""
    if addition.strip() not in ci.read_text():
        ci.write_text(ci.read_text().replace(marker, marker + addition))
    (PACKET / "final-source-adjustments.json").write_text(json.dumps({
        "after": "current-native-host-tests", "changes": [
            "Remove unused analyzer import reported by pinned Ruff",
            "Document the buildifier CI job and native reproduction in CI.md"],
        "verification": "Final affected tests, formatting, lint and build follow"}, indent=2) + "\n")

    ruff = Path(TOOLS["external"]) / "rules_multitool++multitool+multitool.ruff.linux_x86_64/tools/ruff/linux_x86_64_archive/ruff-x86_64-unknown-linux-musl/ruff"
    assert run("current-final-ruff", [str(ruff), "check",
        "quality/static_analysis/codeql_lint.py", "quality/static_analysis/codeql_lint_test.py",
        "tools/lint/buildifier/buildifier_lint.py", "tools/lint/buildifier/buildifier_lint_test.py"])["exit_code"] == 0
    assert run("current-final-buildifier", container_command([
        TOOLS["buildifier"], "-mode=check", "-lint=warn", "-r", str(source)]))["exit_code"] == 0
    assert bazel("current-final-affected-tests", ["test", "--config=ci", "--jobs=8", "--nocache_test_results",
        "//quality/static_analysis:codeql_lint_test", "//tools/lint/buildifier:buildifier_lint_test",
        "//quality/visibility_guard:visibility_guard_test",
        "//score/mw/com/dependability/safety_analysis/aou_forwarding_test:component_requirements_test"],
        runtime_tools=True)["exit_code"] == 0
    assert bazel("current-native-format", ["run", "//:format.check", "--jobs=8"])["exit_code"] == 0
    bazel("current-native-copyright", ["run", "//:copyright.check", "--jobs=8"])
    assert bazel("current-all-target-build", ["build", "--config=ci", "//...", "--jobs=8"])["exit_code"] == 0
    assert bazel("current-configured-forwarders", ["cquery", 'deps(kind("_forwarding_test", //...), 1)', "--output=graph"])["exit_code"] == 0

    # Use an unused database path. Extraction is forced and the wrapper audits
    # the configured compile graph; a retained baseline DB is never overwritten.
    assert bazel("current-fresh-production-extraction", ["run", "//quality/static_analysis:codeql_lint", "--jobs=8", "--",
        "--phase", "create-database", "--database-path", str(ROOT / "current-production-db"),
        "--production-targets", "--audit-source", "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp",
        "--target", "//score/message_passing", "//score/mw/com"])["exit_code"] == 0
    outer = ROOT / "bazel-output/4b9334f3199c06dc7413ff31e3d2964d/external"
    codeql = outer / "+_repo_rules4+codeql_bundle/codeql/codeql"
    pack = outer / "+_repo_rules5+codeql_coding_standards_compiled/pack"
    output = ROOT / "current-production-analysis"
    output.mkdir(exist_ok=True)
    assert run("current-complete-locked-suite", container_command([str(codeql), "database", "analyze",
        str(ROOT / "current-production-db"), str(source / "quality/static_analysis/query_overrides/communication-default.qls"),
        "--search-path=" + str(pack), "--additional-packs=" + str(pack) + ":" + str(pack / ".codeql/libraries"),
        "--threads=4", "--ram=10000", "--format=sarifv2.1.0", "--output=" + str(output / "communication.sarif")]))["exit_code"] == 0
    assert bazel("current-native-analyzer-reporting", ["run", "//quality/static_analysis:codeql_lint", "--jobs=8", "--",
        "--phase", "analyze-database", "--database-path", str(ROOT / "current-production-db"),
        "--output-dir", str(ROOT / "current-native-reporting"), "--output-prefix", "communication",
        "--audit-source", "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"])["exit_code"] == 0
    # Existing module test selects its own root; no absolute override is saved.
    assert bazel("current-module-integration", ["build", "//...", "--jobs=8"], cwd=source / "module_integration_test")["exit_code"] == 0
    assert bazel("current-module-integration-lock", ["mod", "deps", "--lockfile_mode=update"], cwd=source / "module_integration_test")["exit_code"] == 0
    print("Current native verification sequence complete", flush=True)


if __name__ == "__main__":
    execute()
