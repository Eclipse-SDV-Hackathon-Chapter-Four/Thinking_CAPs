"""Read-only engineering evidence audit and additive portable snapshot. No native execution."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import tomllib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).parent
RUN = ROOT.parent / "score-rust-linux-integration-xfiuopbb"
CONTRIBUTIONS = Path("/home/jefferson/eclipse_sdv_hackathon_2026/contributions")
ISSUE = CONTRIBUTIONS / "issues/eclipse-score/communication/1265"
INPUT = ISSUE / "linux-integration/score-rust-linux-integration-xfiuopbb"
OUTPUT = ISSUE / "engineering-review" / ROOT.name
EXPECTED = "bb7972f22c5bd69db5dc5ade910f8f5e9785890c35738ea857d57daaa691a2c8"


def sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def write(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def load(path: Path):
    return json.loads(path.read_text())


def verify_packet(path: Path, expected: str) -> int:
    manifest = path / "artifact-manifest.json"
    assert sha(manifest) == expected, (manifest, "manifest drift")
    records = load(manifest)["files"]
    for relative, digest in records.items():
        subject = (path / relative).resolve()
        assert subject.is_relative_to(path.resolve())
        assert sha(subject) == digest, (relative, "subject drift")
    return len(records)


validate_run_root(ROOT)
validate_run_root(RUN)
assert not OUTPUT.exists(), "Keep the review additive; never overwrite a sealed review"
count = verify_packet(INPUT, EXPECTED)
assert count == 1359
# Explicit contribution destination; scratch stays on the bound SSD.
OUTPUT.mkdir(parents=True)
shutil.copytree(INPUT, OUTPUT / "native-verification", symlinks=False)
assert verify_packet(OUTPUT / "native-verification", EXPECTED) == count
EVIDENCE = OUTPUT / "review-evidence"
EVIDENCE.mkdir()
for name in ["authority.json", "storage-selection.json", "input-integrity.json", "current-issue.json", "current-paste-metadata.json", "current-pastey-metadata.json", "retrieval-time.json"]:
    shutil.copy2(ROOT / name, EVIDENCE / name)
shutil.copy2(Path(__file__), EVIDENCE / "audit_review.py")

old = INPUT / "historical-rust-and-copyright/prior-attempt"
history = INPUT / "historical-rust-and-copyright"
baseline = load(INPUT / "execution/baseline-hashes.json")
candidate = load(INPUT / "execution/candidate-hashes.json")
historical_baseline = load(history / "execution/baseline-hashes.json")
inventory = load(old / "macro-usage-inventory.json")
patterns = inventory["patterns"]
static_subjects = {}
selected = ["MODULE.bazel", "MODULE.bazel.lock", "score/mw/com/rust/score_com_concept/interface_macros.rs", "score/mw/com/rust/score_com_concept/BUILD", "score/mw/com/rust/score_com/BUILD", "score/mw/com/rust/score_com/lib.rs"]
for relative in selected:
    actual = RUN / "candidate" / relative
    if not actual.is_file():
        static_subjects[relative] = {"status": "not_present_at_selected_path"}
        continue
    digest = sha(actual)
    assert digest == candidate[relative]
    unchanged = digest == baseline[relative] == historical_baseline.get(relative)
    target = EVIDENCE / "current-static-subjects" / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(actual, target)
    static_subjects[relative] = {"sha256": digest, "unchanged_from_historical_baseline": unchanged, "claim": "Fresh byte measurement; no test-result promotion"}
macro = RUN / "candidate" / inventory["path"]
assert sha(macro) == inventory["sha256"]
text = macro.read_text()
assert text.count("score_com::pastey::paste!") == 4
assert sum(len(v) for v in patterns.values()) == 22
for pattern, lines in patterns.items():
    assert [index for index, line in enumerate(text.splitlines(), 1) if pattern in line] == lines
assert sha(RUN / "candidate/MODULE.bazel.lock") == "aaff76815a51a8f2b09705a12e6c197305748669d1724252de3860b25907294c"

archive = old / "sources/crate_index__pastey-0.2.3.crate"
assert sha(archive) == "2ee67f1008b1ba2321834326597b8e186293b049a023cdef258527550b9935b4"
crate = old / "sources/crates/pastey-0.2.3"
cargo = tomllib.loads((crate / "Cargo.toml").read_text())
assert cargo["package"]["version"] == "0.2.3"
assert cargo["package"]["license"] == "MIT OR Apache-2.0"
assert not cargo.get("features") and not cargo.get("dependencies") and not cargo.get("build-dependencies")
dependency = {"crate": "pastey", "version": "0.2.3", "archive_sha256": sha(archive), "resolved_and_declared_features": [], "normal_and_build_dependencies": [], "license": cargo["package"]["license"], "edition": cargo["package"]["edition"], "rust_version": cargo["package"]["rust-version"], "origin": load(crate / ".cargo_vcs_info.json"), "license_hashes": {f: sha(crate / f) for f in ["LICENSE-MIT", "LICENSE-APACHE"]}, "macro_calls": 4, "identifier_occurrences": 22, "patterns": patterns}

expected_cases = {"test_com_api_sync": {"test_bigdata_exchange", "test_mixed_primitives_exchange", "test_complex_struct_exchange"}, "test_com_api_async": {"test_bigdata_async_with_cancellation", "test_bigdata_async_without_cancellation", "test_bigdata_async_stream"}}
integration = []
for name, expected_names in expected_cases.items():
    paths = list((INPUT / "execution/testlogs").rglob(name + "/test.xml"))
    assert len(paths) == 1
    path = paths[0]
    xml = ET.parse(path).getroot()
    cases = list(xml.iter("testcase"))
    assert {case.attrib["name"] for case in cases} == expected_names
    assert len(cases) == 3 and all(not list(case) for case in cases)
    suites = list(xml.iter("testsuite"))
    assert all(int(suite.attrib.get(key, "0")) == 0 for suite in suites for key in ["failures", "errors", "skipped"])
    integration.append({"xml": str(path.relative_to(INPUT)), "sha256": sha(path), "case_names": sorted(expected_names), "passed": 3, "failed": 0, "errors": 0, "skipped": 0, "claim": "Carried native results at 8368bfb5; fresh XML integrity/structure audit only"})

validate_run_root(ROOT)
validate_run_root(RUN)
external = RUN / "bazel-output/e47b4ceef7854d004f6fef7d10e4acf9/external"
tool = external / "score_toolchains_rust++ferrocene_toolchain_ext+ferrocene_x86_64_unknown_linux_gnu"
old_compiler = load(history / "execution/compatibility-preflight.json")["compiler_input_identity"]
driver = tool / "lib/librustc_driver-c236fde3428c5a4d.so"
assert sha(driver) == old_compiler["driver_libraries"][0]["sha256"]
assert sha(tool / "bin/rustc") == old_compiler["rustc"]["sha256"]
for original, name in [(external / "score_toolchains_rust+/MODULE.bazel", "toolchain-MODULE.bazel"), (tool / "BUILD.bazel", "materialized-toolchain-BUILD.bazel")]:
    shutil.copy2(original, EVIDENCE / name)
compiler = {"version_evidence": "native-verification/historical-rust-and-copyright/execution/logs/compatibility2-ferrocene.log", "version_claim": "Carried version report from identical driver and wrapper; no compiler executed during this review", "reported_rustc": "1.94.0-nightly (779fbed05 2025-12-11) (Ferrocene rolling)", "commit": "779fbed05ae9e9fe2a04137929d99cc9b3d516fd", "host_and_selected_target": "x86_64-unknown-linux-gnu", "LLVM": "21.1.5", "builder_release": "1.3.1", "archive_sha256": "6fd7c7053a80463b2bfd24202de02e16959b18ed185c55b738148e9caac42eff", "fresh_driver_sha256": sha(driver), "fresh_rustc_wrapper_sha256": sha(tool / "bin/rustc"), "exact_build_certificate": "not_supplied", "qualification_scope": "not_established; no categorical conclusion about unprovided certificates"}

findings = load(history / "copyright-findings.json")["findings"]
unchanged, different, missing = [], [], []
for finding in findings:
    path = finding["file"]
    current = baseline.get(path)
    if current is None:
        missing.append(path)
    elif current == finding["baseline_sha256"]:
        unchanged.append(path)
    else:
        different.append(path)
copyright = {"historical_findings": len(findings), "records_with_same_current_baseline_file_hash": len(unchanged), "records_with_different_current_baseline_file_hash": len(different), "missing_current_baseline_paths": missing, "different_current_baseline_paths": different, "claim": "Hash correlation only; native copyright check not rerun; all historical dispositions remain pending human review"}

requirements = old / "sources/score-crates/docs/pastey/docs/requirement/component_requirements.trlc"
req_text = requirements.read_text()
ids = re.findall(r"ScoreReq\.CompReq (REQ_COMP_PASTEY_\d+) \{", req_text)
assert len(ids) == 15 and len(re.findall(r"version = 1", req_text)) == 15
assert "status =" not in req_text

retrievals = []
urls = {
    "ferrocene-targets.html": "https://public-docs.ferrocene.dev/main/user-manual/targets/index.html",
    "tool-management-workproducts.rst": "https://raw.githubusercontent.com/eclipse-score/process_description/98d1d5f42dad412a09a888ea25e59c62fa6371ce/process/process_areas/tool_management/tool_management_workproducts.rst",
    "tool-management-attributes.rst": "https://raw.githubusercontent.com/eclipse-score/process_description/98d1d5f42dad412a09a888ea25e59c62fa6371ce/process/process_areas/tool_management/guidance/tool_management_reqs.rst",
    "tool-verification-report-template.rst": "https://raw.githubusercontent.com/eclipse-score/process_description/98d1d5f42dad412a09a888ea25e59c62fa6371ce/process/folder_templates/tools/tool_verification_report_template.rst",
}
for name, url in urls.items():
    validate_run_root(ROOT)
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "S-CORE-offline-engineering-review"})
        with urllib.request.urlopen(request, timeout=20) as response:
            data = response.read(2 * 1024 * 1024)
            status, final_url = response.status, response.url
        path = EVIDENCE / "public-sources" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        retrievals.append({"url": url, "final_url": final_url, "status": status, "captured_at": datetime.now(timezone.utc).isoformat(), "path": str(path.relative_to(OUTPUT)), "bytes": len(data), "sha256": sha(path)})
    except Exception as error:
        retrievals.append({"url": url, "captured_at": datetime.now(timezone.utc).isoformat(), "retrieval_failure": str(error), "claim": "No readiness inferred from unavailable source"})
write(EVIDENCE / "retrieval-receipts.json", retrievals)
write(OUTPUT / "deterministic-review-checks.json", {"audited_at": datetime.now(timezone.utc).isoformat(), "input_packet_sha256": EXPECTED, "input_subjects_verified": count, "copied_input_subjects_verified": count, "patch_sha256": sha(INPUT / "communication-1265.patch"), "current_static_subjects": static_subjects, "dependency": dependency, "integration": integration, "compiler": compiler, "copyright_correlation": copyright, "native_component_requirements": [{"id": "PasteyComReq." + identifier + "@1", "safety": "ASIL B", "status": "not_explicitly_present_in_supplied_TRLC_record"} for identifier in ids], "scope": "Fresh read-only integrity and structural checks; carried native evidence; no new native execution, source repair, or human acceptance"})
print(json.dumps({"output": str(OUTPUT), "input_subjects": count, "integration_case_records_verified": 6, "compiler_version": compiler["reported_rustc"], "copyright_correlation": copyright, "public_sources_retrieved": sum("retrieval_failure" not in item for item in retrievals)}, indent=2))
