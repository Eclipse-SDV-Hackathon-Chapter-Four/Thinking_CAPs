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

"""Assemble final review summaries from retained measurements and native inputs."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tarfile

from export_packet import export
from measure import PACKET, ROOT, sha
from compare_locations import uris


def write(name, value):
    (PACKET / name).write_text(json.dumps(value, indent=2) + "\n")


def assemble():
    if (PACKET / "license-header-audit.json").exists():
        raise RuntimeError("This pre-cleanup collector is retained as evidence. Use refresh_license_packet.py for the final license packet.")
    records = {f.stem: json.loads(f.read_text()) for f in (PACKET / "evidence").glob("*.json")
               if isinstance(json.loads(f.read_text()), dict) and "exit_code" in json.loads(f.read_text())}
    assert records["final-source-affected-tests"]["exit_code"] == 0
    communication = export("communication", ROOT / "candidate", "cef680454e8586daca9f953084dca33fb3759d0c")
    consumer = export("config_management", ROOT / "config-management-consumer-candidate", "e82ec2750d7e9a9dd18edbfe6f5a78be57c22d80")

    apply_checks = []
    for name, source in [("communication", ROOT / "candidate"), ("config_management", ROOT / "config-management-consumer-candidate")]:
        index = ROOT / (name + "-apply-check.index")
        index.unlink(missing_ok=True)
        import os
        env = {**os.environ, "GIT_INDEX_FILE": str(index)}
        subprocess.run(["git", "read-tree", "HEAD"], cwd=source, env=env, check=True)
        result = subprocess.run(["git", "apply", "--check", "--cached", str(PACKET / "patches" / (name + ".patch"))],
                                cwd=source, env=env, capture_output=True, text=True)
        apply_checks.append({"repository": name, "exit_code": result.returncode, "stdout": result.stdout,
                             "stderr": result.stderr, "patch_sha256": sha(PACKET / "patches" / (name + ".patch"))})
        index.unlink()
        assert result.returncode == 0
    write("final-patch-applicability.json", apply_checks)

    reports = ROOT / "current-native-reporting"
    report_stdout = (PACKET / "evidence/current-native-analyzer-reporting.stdout").read_text()
    assert "analysis_report exited with code" not in report_stdout
    assert "Report generation exception" not in report_stdout
    assert (reports / "analysis_reports").is_dir()
    destination = PACKET / "evidence/current-native-reporting"
    destination.mkdir(exist_ok=True)
    for source in reports.rglob("*"):
        if not source.is_file() or "codeql_home" in source.relative_to(reports).parts:
            continue
        target = destination / source.relative_to(reports)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    sarif = json.loads((destination / "communication.sarif").read_text())
    findings = [f for run in sarif["runs"] for f in run.get("results", [])]
    empty = [uri for uri in uris(sarif) if uri in ("file:", "file:/", "file://", "file:///")]
    assert not empty
    summary = {"source_revision": communication["upstream_revision"], "queries": 218,
               "findings": len(findings), "rule_counts": dict(sorted(Counter(f["ruleId"] for f in findings).items())),
               "empty_file_uri_occurrences": len(empty), "sarif_sha256": sha(destination / "communication.sarif"),
               "execution_records": ["current-complete-locked-suite", "current-native-analyzer-reporting"],
               "limits": "Successful complete analysis and reporting; reported MISRA findings are not resolved, accepted or qualified by this execution."}
    write("current-full-suite-summary.json", summary)

    # Export concrete test logs. Native convenience symlinks can point to inner
    # Bazel outputs after a nested invocation, so do not use bazel-testlogs.
    testlogs = ROOT / "bazel-output/4b9334f3199c06dc7413ff31e3d2964d/execroot/_main/bazel-out/k8-fastbuild/testlogs"
    testfiles = [f for f in testlogs.rglob("*") if f.is_file() and f.suffix in (".xml", ".log")]
    with tarfile.open(PACKET / "evidence/current-host-testlogs.tar.gz", "w:gz") as archive:
        for f in testfiles:
            archive.add(f, arcname=str(f.relative_to(testlogs)), recursive=False)
    write("current-host-testlogs-export.json", {"concrete_output": str(testlogs), "files": len(testfiles),
          "note": "Full host run logs plus later affected-test reruns; each execution's original stdout/stderr and source bindings remain separate."})

    inventory = json.loads((PACKET / "required-checks.json").read_text())
    inventory["source_revision"] = communication["upstream_revision"]
    mapping = {
        "buildifier-regression": "final-source-affected-tests", "buildifier-repository": "final-source-buildifier-wrapper",
        "coverage-rule-analysis": "final-source-coverage-rule", "analyzer-regressions": "final-source-affected-tests",
        "full-native-analyzer": "current-native-analyzer-reporting", "native-format": "final-source-format",
        "native-copyright": "final-source-copyright", "host-tests": "current-native-host-tests",
        "host-all-build": "final-source-all-build", "module-integration": "current-module-integration",
        "public-visibility": "final-source-affected-tests", "native-aou-fixture": "final-source-affected-tests",
        "production-dependable-element": "1031-production-traceability-index"}
    for item in inventory["checks"]:
        if item["id"] in mapping:
            item["record"] = mapping[item["id"]]
        if item["id"] == "configured-production-extraction":
            item.update(record="current-recovered-extraction-wait", status="recovered-native-pass-with-complete-source-byte-audit",
                        limit="Collector interrupted after launch. Native exit is zero; all 516 configured compile inputs and 1,698 extant physical archive files hash-match. Two generated temporary XML paths no longer exist; archive bytes retained. See extraction-recovery.json.")
        elif item["id"] == "manual-incompatible-tests":
            item.update(status="accounted-with-explicit-omissions", record="current-configured-forwarders",
                        limit="1,158 rules: 508 direct passes, 7 skips; 265 manual actuals delegated to passing configured forwarders; 264 QNX and 114 other manual rules have no direct pass claimed. See test-dispositions.json.")
        elif "record" in item and item["record"] in records:
            record = records[item["record"]]
            item["status"] = "measured-pass" if record["exit_code"] == 0 else "measured-failure-unresolved"
            item["exit_code"] = record["exit_code"]
            item["measured_source_revision"] = record["source_baseline"]
        if item["id"] == "host-tests":
            item["limit"] = "508 passes, 7 explicit platform skips, no flaky result. Later adjustments are unused-import removal, CI documentation and two comment-only notices; affected tests and final complete build pass. Local process-wrapper environment is not native Linux-sandbox CI equivalence."
        if item["id"] == "host-all-build":
            item["limit"] = "Final source-bound build; earlier current-all-target-build overlapped documentation/header edits and is historical."
        if item["id"] == "production-dependable-element":
            item["limit"] = "Real provider consumption passes on the bound baseline candidate; complete consumer index fails on legacy/placeholder safety records. All received AoUs, maturity/classification, actual implementation links and published dependency pin need native owner decisions."
    inventory["checks"] += [
        {"id": "changed-python-ruff", "source": "_linter.yml; native pinned Ruff and .ruff.toml", "record": "current-final-ruff", "status": "measured-pass", "limit": "Changed Python files only; does not replace hosted aspect lint matrix."},
        {"id": "module-integration-lock", "source": "_build_and_test_gcc15.yml", "record": "current-module-integration-lock", "status": "measured-pass"},
        {"id": "traced-build-error-regression", "source": "#1104 exact-scope tracing compatibility", "record": "1104-complete-bash-helper-regression", "status": "measured-pass-on-baseline", "limit": "Both intentional compiler failures and positive error target traced with all six Bash helpers; current production extraction is separate."}]
    write("required-checks.json", inventory)

    # Retain mismatches explicitly instead of silently carrying historical checks.
    final_hashes = records["final-source-affected-tests"]["subject_hashes"]
    reconciliation = []
    for name, record in sorted(records.items()):
        hashes = record.get("subject_hashes", {})
        is_consumer = "config" in Path(record.get("subject_root", record["cwd"])).name
        reference = consumer["changed_files"] if is_consumer else final_hashes
        mismatch = [f for f, value in hashes.items() if reference.get(f, value) != value]
        reconciliation.append({"record": name, "source_revision": record["source_baseline"],
             "exit_code": record["exit_code"], "changed_during_execution": record.get("changed_during_execution", "not-collected-in-earlier-version"),
             "mismatched_final_subject_files": mismatch,
             "classification": "consumer-bound" if is_consumer else ("historical-baseline" if record["source_baseline"] != communication["upstream_revision"] else "current-revision")})
    write("evidence-reconciliation.json", reconciliation)

    status = {"technical_changes_prepared": True, "merge_ready": False,
              "issue_states": {"1236": "implemented and locally verified; native CI/codeowner acceptance pending",
                               "751": "implemented; current configured production extraction and full suite/reporting verified",
                               "1104": "implemented; location preservation and complete current suite verified",
                               "1031": "public API/fixture implemented; real provider proposal passes; full production integration blocked"},
              "remaining": ["Config Management safety work-product corrections, all AoU dispositions and published API dependency pin",
                            "198 native copyright failures outside final touched-file corrections",
                            "Required hosted sanitizer/aspect/platform results and native Linux-sandbox validation",
                            "Final author/commit ECA binding and native codeowner/safety/dependency approval"],
              "publication": "No PR, comment, merge or release published"}
    write("readiness.json", status)
    text = f"""# Measured verification

Submission: Communication `{communication['upstream_revision']}` plus the retained
patch; companion Config Management `{consumer['upstream_revision']}`.
Technical changes and portable artifacts are prepared. **Merge readiness is not
established**: #1031's complete production integration still needs native owners.

| Check | Result | Evidence |
| --- | --- | --- |
| Current host suite | 508 passed; 7 skipped; no flaky result | `current-native-host-tests` |
| Final affected tests | 4 passed, including real lint/analyzer regressions, visibility and native AoU fixture | `final-source-affected-tests` |
| Final full build | Passed | `final-source-all-build` |
| Formatting, buildifier warnings and changed Python Ruff | Passed with native pins | `final-source-format`, `final-source-buildifier-wrapper`, `current-final-ruff` |
| Coverage rule / module integration and lock | Passed | `final-source-coverage-rule`, `current-module-integration`, `current-module-integration-lock` |
| Current production extraction | 516/516 configured C++ inputs present and hash-matched; 1,698 extant archive files hash-match | `extraction-recovery.json`, `current-compile-source-coverage.json`, `current-source-archive-binding.json` |
| Complete current analyzer and native reports | All 218 queries; {len(findings)} reported findings; zero empty file URI occurrences | `current-full-suite-summary.json`, `evidence/current-native-reporting` |
| Exact-scope #1104 comparison | 501 findings retained; 281 empty URI occurrences removed; primary findings/fingerprints and valid related links retained | `1104-location-comparison.json`, `compare_locations.py` |
| Real production provider | Build and TRLC validation passed on bound baseline candidate | `1031-provider-native-cc-toolchain`, `1031-production-provider-validation` |
| Complete production consumer index | Failed on legacy/placeholder safety data | `1031-production-traceability-index`, `1031-production-integration-disposition.json` |
| Native copyright | Failed; final touched-file notices corrected; 198 remaining native failures | `final-source-copyright`, `copyright-current-disposition.json` |

The restart interrupted the extraction collector after launch. The native
container finished with exit 0, its full log streams survived, and the recovered
database was audited against the configured compilation manifest and final
physical source hashes. The configured-graph and recovery observer input hashes
match exactly. Two temporary generated XML source paths no longer exist; their
archive bytes remain. This is explicitly recovered evidence, not a reconstructed
normal collector record. Subsequent query, report and final source checks have
ordinary source-bound execution records.

The full host suite precedes an unused import removal, CI documentation and two
comment-only copyright corrections. Macro bodies are byte-identical across the
notice additions. Final affected tests, complete build, formatting and lint bind
the final source. Earlier source overlap and invalid consumer repository overrides
are retained and reconciled, not represented as final passes.

`test-dispositions.json` accounts for all 1,158 discovered rules, including 643
manual rules: 265 selected manual actuals execute through passing native
forwarders; 264 QNX and 114 other manual rules have no direct pass claimed.
The seven skips are enumerated in the full test stdout. The local default
process-wrapper sandbox does not establish the project's Linux-sandbox CI
environment. Required hosted sanitizer/aspect jobs and licensed/applicable
platform checks remain outstanding without a waiver.

Successful analyzer execution does not resolve the {len(findings)} MISRA findings
or establish qualified/safety accepted tool use. Native requirements, safety,
dependency and codeowner acceptance remain human decisions. The companion root
still needs a published Communication dependency containing the public API,
correction/disposition of placeholder safety records, and assessed received-AoU
handling before #1031 can be considered complete.

Full commands, raw logs, exit codes, timings, tool/image/source bindings, failed
attempts and generated artifacts are retained. Baseline results remain historical;
see `evidence-reconciliation.json` and `required-checks.json` for their limits.
The immutable prior archive verifies 11,236 retained files without mismatches.
Run `python verify_packet.py` and `python compare_locations.py` for portable checks.
"""
    (PACKET / "verification.md").write_text(text)


if __name__ == "__main__":
    assemble()
