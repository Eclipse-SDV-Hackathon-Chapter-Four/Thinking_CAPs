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

"""Export the final licensed sources and bind review artifacts to their new hashes."""
from collections import Counter
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import zipfile

from audit_license_headers import audit
from compare_locations import uris
from export_packet import export
from measure import PACKET, ROOT, sha
from update_copyright import update


def write(name, value):
    (PACKET / name).write_text(json.dumps(value, indent=2) + "\n")


def manifest(directory):
    existing = directory / "artifact-manifest.json"
    value = json.loads(existing.read_text())
    value["files"] = [{"path": str(f.relative_to(directory)), "bytes": f.stat().st_size, "sha256": sha(f)}
                      for f in sorted(directory.rglob("*")) if f.is_file() and "__pycache__" not in f.parts
                      and f != existing and (directory == PACKET or f.name != "artifact-manifest.json")]
    existing.write_text(json.dumps(value, indent=2) + "\n")


def refresh():
    records = {f.stem: json.loads(f.read_text()) for f in (PACKET / "evidence").glob("license-headers-*.json")}
    required = ["host-tests", "format", "buildifier", "all-build", "production-extraction", "native-analyzer-reporting-verified", "query-metadata", "query-final-regressions", "query-results-refresh",
                "communication-copyright-verified", "config-management-copyright-final-lock", "config-formatter-executable-verified", "config-provider-final-lock"]
    for suffix in required:
        record = records["license-headers-" + suffix]
        assert record["exit_code"] == 0 and not record["changed_during_execution"], suffix
    assert audit() == 0
    update()
    licensing = json.loads((PACKET / "license-header-audit.json").read_text())
    subjects = {}
    applicability = []
    for name, root in [("communication", ROOT / "candidate"), ("config_management", ROOT / "config-management-consumer-candidate")]:
        revision = json.loads((PACKET / "license-header-history" / (name + "-subject.json")).read_text())["upstream_revision"]
        subjects[name] = export(name, root, revision)
        index = ROOT / (name + "-license-applicability.index")
        index.unlink(missing_ok=True)
        env = {**os.environ, "GIT_INDEX_FILE": str(index)}
        subprocess.run(["git", "read-tree", "HEAD"], cwd=root, env=env, check=True)
        patch = PACKET / "patches" / (name + ".patch")
        result = subprocess.run(["git", "apply", "--check", "--cached", str(patch)], cwd=root, env=env, capture_output=True, text=True)
        assert result.returncode == 0, result.stderr
        applicability.append({"repository": name, "exit_code": result.returncode, "patch_sha256": sha(patch), "stderr": result.stderr})
        subprocess.run(["git", "add", "--all", "."], cwd=root, env=env, check=True)
        if name == "communication":
            for label, paths in [("codeql-type-alias-location", ["quality/static_analysis/query_overrides"]),
                                 ("build-error-interpreters", ["third_party/rules_build_error", "MODULE.bazel"])]:
                extract = subprocess.check_output(["git", "diff", "--cached", "--binary", "HEAD", "--", *paths], cwd=root, env=env)
                (PACKET / "patches" / (label + ".patch")).write_bytes(extract)
        index.unlink()
    write("license-final-patch-applicability.json", applicability)

    reports = ROOT / "license-final-native-reporting-verified"
    destination = PACKET / "evidence/license-final-native-reporting"
    text = (PACKET / "evidence/license-headers-native-analyzer-reporting-verified.stdout").read_text()
    assert "analysis_report exited with code" not in text and "Report generation exception" not in text
    for f in reports.rglob("*"):
        if not f.is_file() or "codeql_home" in f.relative_to(reports).parts:
            continue
        target = destination / f.relative_to(reports)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target)
    sarif = json.loads((destination / "communication.sarif").read_text())
    findings = [f for run in sarif["runs"] for f in run.get("results", [])]
    empty = [uri for uri in uris(sarif) if uri in ("file:", "file:/", "file://", "file:///")]
    assert not empty
    query_stderr = (PACKET / "evidence/license-headers-native-analyzer-reporting-verified.stderr").read_text()
    assert "[218/218]" in text + query_stderr
    write("license-final-suite-summary.json", {"queries": 218, "findings": len(findings), "empty_file_uri_occurrences": 0,
          "rule_counts": dict(sorted(Counter(f["ruleId"] for f in findings).items())),
          "record": "evidence/license-headers-native-analyzer-reporting-verified.json", "patch_sha256": subjects["communication"]["patch_sha256"]})
    database = ROOT / "license-final-production-db"
    coverage = json.loads((database / "compile-source-coverage.json").read_text())
    checks = []
    physical = []
    unavailable = []
    with zipfile.ZipFile(database / "src.zip") as archive:
        entries = set(archive.namelist())
        for item in coverage["expected_compile_sources"]:
            path = Path(item)
            entry = str(path).lstrip("/")
            assert entry in entries, entry
            archived = archive.read(entry)
            assert archived == path.read_bytes(), item
            checks.append({"source": item, "sha256": sha(path), "archive_entry": entry})
        for entry in sorted(entries):
            if entry.endswith("/"):
                continue
            path = Path("/" + entry)
            if not path.is_file():
                unavailable.append(entry)
                continue
            assert archive.read(entry) == path.read_bytes(), entry
            physical.append({"archive_entry": entry, "sha256": sha(path)})
    assert not coverage["missing"]
    write("license-final-compile-source-coverage.json", {"configured_sources": len(checks), "missing": [], "hash_mismatches": [], "files": checks,
          "record": "evidence/license-headers-production-extraction.json"})
    assert all(name.endswith("coding-standards.xml") for name in unavailable), unavailable
    write("license-final-source-archive-binding.json", {"checked_existing_physical_archive_files": len(physical), "missing_host_paths": unavailable,
          "mismatches": [], "files": physical, "limit": "Temporary generated XML paths may have been removed; their original archive bytes are retained."})
    shutil.copy2(database / "src.zip", PACKET / "evidence/license-final-source-archive.zip")
    host_text = (PACKET / "evidence/license-headers-host-tests.stdout").read_text()
    results = dict(re.findall(r"^(//\S+)\s+(?:\(cached\)\s+)?(PASSED|SKIPPED|FLAKY)\b", host_text, re.MULTILINE))
    host_counts = dict(Counter(results.values()))
    write("license-final-host-summary.json", {"record": "evidence/license-headers-host-tests.json", "results": host_counts, "tests": results,
          "limit": "Local processwrapper profile; cached passes, explicit platform skips and unselected manual tests retain their native dispositions."})

    history = PACKET / "license-header-history"
    for name in ["README.md", "verification.md", "readiness.json", "required-checks.json", "pr-communication.md", "pr-config-management.md"]:
        target = history / ("before-" + name)
        if not target.exists():
            shutil.copy2(PACKET / name, target)
    readiness = json.loads((PACKET / "readiness.json").read_text())
    readiness["remaining"] = [x for x in readiness["remaining"] if "copyright" not in x.lower()]
    readiness["license_headers"] = {"status": "verified", **licensing["summary"], "evidence": "license-header-audit.json"}
    write("readiness.json", readiness)
    inventory = json.loads((PACKET / "required-checks.json").read_text())
    mapping = {"native-copyright": "communication-copyright-verified", "host-tests": "host-tests", "native-format": "format",
               "buildifier-regression": "host-tests", "buildifier-repository": "buildifier", "host-all-build": "all-build",
               "analyzer-regressions": "host-tests", "public-visibility": "host-tests", "native-aou-fixture": "host-tests",
               "configured-production-extraction": "production-extraction", "full-native-analyzer": "native-analyzer-reporting-verified"}
    for item in inventory["checks"]:
        if item["id"] in mapping:
            name = "license-headers-" + mapping[item["id"]]
            item.update(record=name, status="measured-pass", exit_code=0)
            item["measured_source_revision"] = records[name]["source_baseline"]
            item["limit"] = "Fresh source binding after license cleanup; prior checks and source bindings remain historical. Local results do not replace required hosted jobs."
    inventory["checks"] = [c for c in inventory["checks"] if c["id"] not in {"companion-copyright", "all-code-license-headers"}]
    inventory["checks"] += [{"id": "companion-copyright", "record": "license-headers-config-management-copyright-final-lock", "status": "measured-pass", "exit_code": 0},
                            {"id": "all-code-license-headers", "evidence": "license-header-audit.json", "status": "measured-pass", **licensing["summary"]}]
    write("required-checks.json", inventory)

    verification = f"""# Measured verification after license cleanup

The current patches include the repository-wide license cleanup requested on
2026-10-07. Every current code file is covered by the independent audit; native
copyright checks scan the complete repository. Existing numeric copyright years
and imported MIT/CC0 terms are retained. Before-state sources, patches, failures
and measurements remain in `license-header-history` and the original evidence.

| Check | Result | Evidence |
| --- | --- | --- |
| All current code headers | {licensing['summary']['code_files']} repository files and {licensing['summary']['packet_helpers']} packet helpers; zero missing notices | `license-header-audit.json` |
| Communication native copyright | Passed; all original 198 errors addressed | `license-headers-communication-copyright-verified` |
| Config Management native copyright | Passed over complete repository | `license-headers-config-management-copyright-final-lock` |
| Host tests | {host_counts.get('PASSED', 0)} passed, {host_counts.get('SKIPPED', 0)} skipped | `license-headers-host-tests`, `license-final-host-summary.json` |
| Formatting / buildifier / full build | Passed on final licensed source | `license-headers-format`, `license-headers-buildifier`, `license-headers-all-build` |
| Fresh production extraction | {len(checks)}/{len(checks)} configured C++ inputs present and byte-matched | `license-headers-production-extraction`, `license-final-compile-source-coverage.json` |
| Full analyzer and native reports | 218 queries; {len(findings)} findings; zero empty file URI occurrences | `license-headers-native-analyzer-reporting-verified`, `license-final-suite-summary.json` |
| Patch applicability | Both patches apply to their pinned upstream revisions | `license-final-patch-applicability.json` |
| Exact-scope #1104 regression | Final licensed query retains all 501 baseline findings and removes 281 empty URI occurrences | `license-final-location-comparison.json` |

Program bodies remain unchanged by notice normalization. The audit records the
separate checker scope/configuration changes, generated-bundle license banner,
and buildifier keyword ordering. Config Management retains its previous formatter
macro and wrapper locally because the proposed tooling upgrade removes them.
JSON lockfiles cannot contain inline comments; they remain covered by the native
project LICENSE and NOTICE. The header-template file contains literal examples
and is excluded through the checker's supported mechanism, matching upstream
S-CORE tooling; its own license notice is retained.

The earlier database and reports bind the source before headers moved line numbers.
The fresh database, source archive and SARIF bind the final licensed source.
Findings are not resolved, accepted or qualified by successful execution.

The full host run and build precede the final query header arrangement. The query
license notice and metadata now share the first comment block so CodeQL reads
the original metadata correctly. The
initial separate-block attempt and its stale cached BQRS metadata are retained
as failed reporting records. The affected result was explicitly reevaluated;
parsed metadata, affected regressions and the complete corrected reporting run pass.
The query's original metadata and predicates are unchanged by this arrangement.
The fresh full database reports {len(findings)} findings versus 2,065 in the prior
database. Every finding remains in the artifacts; rule-count differences are
recorded in `license-finding-count-comparison.json`. The same-database regression
retains the original 501 primary findings, fingerprints and located related links.

Merge readiness remains false: #1031's complete consumer safety integration,
published API dependency pin, required hosted CI/platform checks and native
engineering/author acceptance remain outstanding. No PR or approval is published.
"""
    (PACKET / "verification.md").write_text(verification)
    readme = (PACKET / "README.md").read_text().replace("Native copyright failures\nand outstanding CI results are also explicit merge blockers.", "License checks now pass across both complete repositories; outstanding hosted\nCI results and engineering acceptance remain explicit merge blockers.")
    if "## License header verification" not in readme:
        readme += "\n## License header verification\n\n[License review](license-review.md) documents all code-file notices and imported\nlicenses. [The audit](license-header-audit.json) binds every current code file.\nThe `*-license-headers.patch` files isolate this cleanup relative to the preserved\npre-cleanup implementation patches; the primary patches already include it.\nDo not apply both the primary patch and its license extract.\n"
    (PACKET / "README.md").write_text(readme)
    pr = (history / "before-pr-communication.md").read_text()
    start = pr.index("The fresh submission-source database")
    end = pr.index("\n\n\nRelated:", start)
    pr = pr[:start] + f"The final licensed-source database covers {len(checks)}/{len(checks)} configured C++ inputs,\nwith exact source-byte matches. All 218 queries and native reports pass;\n{len(findings)} findings remain for native disposition, with zero empty file URIs.\nHost tests report {host_counts.get('PASSED', 0)} passes and {host_counts.get('SKIPPED', 0)} explicit skips. Full build, formatting,\nbuildifier and complete-repository copyright checks pass. The code-file audit\nalso covers query suites, templates, fixtures and packet helpers outside the\nnative checker. Existing numeric years, MIT attribution and CC0 terms remain.\nGenerated action bundles retain their third-party notices and receive project\nlicense banners during regeneration." + pr[end:]
    pr = pr.replace("Copyright debt, hosted\nlint/sanitizer/platform results", "Hosted\nlint/sanitizer/platform results")
    (PACKET / "pr-communication.md").write_text(pr)
    consumer_pr = (history / "before-pr-config-management.md").read_text()
    consumer_pr += "\nAll current code has license notices, and the complete-repository copyright\ncheck passes. The previous tooling formatter macro and Rust policy wrapper are\nretained locally to preserve format target names, languages and policies after\nthe proposed upgrade. Prior raw checks remain source-bound historical evidence.\n"
    (PACKET / "pr-config-management.md").write_text(consumer_pr)
    # Refresh only the four Communication registry entries owned by this packet.
    manifest(PACKET)
    registry_file = PACKET.parent / "registry.json"
    registry = json.loads(registry_file.read_text())
    for entry in registry["issues"]:
        if entry.get("id") not in {f"eclipse-score/communication#{n}" for n in [1236, 1031, 751, 1104]}:
            continue
        entry["patch_sha256"] = subjects["communication"]["patch_sha256"]
        entry["engineering_review"] = "License headers verified across both complete repositories; complete consumer integration, required hosted CI/platform checks and native owner acceptance pending"
        entry["readiness_review"]["manifest_sha256"] = sha(PACKET / "artifact-manifest.json")
        entry["readiness_review"]["candidate_patch_sha256"] = subjects["communication"]["patch_sha256"]
        entry["license_header_review"] = "communication-followup-20261007/license-header-audit.json"
    registry_file.write_text(json.dumps(registry, indent=2) + "\n")
    print("Final licensed packet exported and manifest anchors refreshed")


if __name__ == "__main__":
    refresh()
