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

"""Resume post-extraction checks after the evidence-collector restart."""
import json
from pathlib import Path
import shutil
import zipfile

from measure import PACKET, ROOT, TOOLS, bazel, container_command, run, sha


def execute():
    observer = json.loads((PACKET / "evidence/current-recovered-extraction-wait.json").read_text())
    native_exit = int((PACKET / "evidence/current-recovered-extraction-wait.stdout").read_text().strip())
    assert observer["exit_code"] == native_exit == 0
    assert not observer["changed_during_execution"]
    db = ROOT / "current-production-db"
    coverage = json.loads((db / "compile-source-coverage.json").read_text())
    assert not coverage["missing"]
    files = []
    with zipfile.ZipFile(db / "src.zip") as archive:
        entries = set(archive.namelist())
        for name in coverage["expected_compile_sources"]:
            source = Path(name)
            entry = name.lstrip("/")
            if entry not in entries:
                entry = "./" + entry
            assert entry in entries, name
            import hashlib
            archived_hash = hashlib.sha256(archive.read(entry)).hexdigest()
            assert archived_hash == sha(source), name
            files.append({"source": name, "archive_entry": entry, "sha256": archived_hash})
    recovery = json.loads((PACKET / "extraction-recovery.json").read_text())
    recovery.update(native_exit_code=native_exit, observer_record="evidence/current-recovered-extraction-wait.json",
        stdout_sha256=sha(PACKET / recovery["raw_stdout"]), stderr_sha256=sha(PACKET / recovery["raw_stderr"]),
        archive_sha256=sha(db / "src.zip"), configured_sources=len(files),
        configured_source_hash_mismatches=0, archive_entries=len(entries),
        source_revision=observer["source_baseline"], input_hashes_during_recovery=observer["subject_hashes"],
        coverage_audit="current-compile-source-coverage.json")
    (PACKET / "extraction-recovery.json").write_text(json.dumps(recovery, indent=2) + "\n")
    (PACKET / "current-compile-source-coverage.json").write_text(json.dumps({
        "source_revision": observer["source_baseline"], "kind": "recovered-native-extraction-with-complete-byte-audit",
        "configured_sources": len(files), "missing": [], "hash_mismatches": [], "files": files}, indent=2) + "\n")
    shutil.copy2(db / "src.zip", PACKET / "evidence/current-production-src.zip")
    print("Recovered extraction: all", len(files), "configured sources match final input bytes", flush=True)

    outer = ROOT / "bazel-output/4b9334f3199c06dc7413ff31e3d2964d/external"
    codeql = outer / "+_repo_rules4+codeql_bundle/codeql/codeql"
    pack = outer / "+_repo_rules5+codeql_coding_standards_compiled/pack"
    source = ROOT / "candidate"
    output = ROOT / "current-production-analysis"
    output.mkdir(exist_ok=True)
    assert run("current-complete-locked-suite", container_command([str(codeql), "database", "analyze",
        str(db), str(source / "quality/static_analysis/query_overrides/communication-default.qls"),
        "--search-path=" + str(pack), "--additional-packs=" + str(pack) + ":" + str(pack / ".codeql/libraries"),
        "--threads=4", "--ram=10000", "--format=sarifv2.1.0", "--output=" + str(output / "communication.sarif")]))["exit_code"] == 0
    assert bazel("current-native-analyzer-reporting", ["run", "//quality/static_analysis:codeql_lint", "--jobs=8", "--",
        "--phase", "analyze-database", "--database-path", str(db),
        "--output-dir", str(ROOT / "current-native-reporting"), "--output-prefix", "communication",
        "--audit-source", "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"])["exit_code"] == 0
    assert run("current-native-database-bundle", container_command([TOOLS["codeql"], "database", "bundle", str(db),
        "--output=" + str(ROOT / "current-native-database.zip")]))["exit_code"] == 0
    shutil.copy2(ROOT / "current-native-database.zip", PACKET / "evidence/current-native-database.zip")
    assert bazel("current-module-integration", ["build", "//...", "--jobs=8"], cwd=source / "module_integration_test")["exit_code"] == 0
    assert bazel("current-module-integration-lock", ["mod", "deps", "--lockfile_mode=update"], cwd=source / "module_integration_test")["exit_code"] == 0
    assert bazel("final-source-all-build", ["build", "--config=ci", "//...", "--jobs=8"])["exit_code"] == 0
    assert bazel("final-source-coverage-rule", ["build", "//quality/coverage:coverage_scope", "--output_groups=allowlist", "--jobs=8"])["exit_code"] == 0
    assert bazel("final-source-buildifier-wrapper", ["run", "//tools/lint/buildifier:buildifier_lint", "--jobs=8", "--", "--recursive"])["exit_code"] == 0
    assert bazel("final-source-format", ["run", "//:format.check", "--jobs=8"])["exit_code"] == 0
    bazel("final-source-copyright", ["run", "//:copyright.check", "--jobs=8"])
    assert bazel("final-source-affected-tests", ["test", "--config=ci", "--jobs=8", "--nocache_test_results",
        "//quality/static_analysis:codeql_lint_test", "//tools/lint/buildifier:buildifier_lint_test",
        "//quality/visibility_guard:visibility_guard_test",
        "//score/mw/com/dependability/safety_analysis/aou_forwarding_test:component_requirements_test"],
        runtime_tools=True)["exit_code"] == 0
    print("Resumed verification sequence complete", flush=True)


if __name__ == "__main__":
    execute()
