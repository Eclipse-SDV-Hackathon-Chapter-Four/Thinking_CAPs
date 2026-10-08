"""Prepare truthful final documentation after terminal contributor-fork checks."""

import datetime
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUN_ID = 37652549770
BINDING = HERE / "anonymous-namespace"


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    summary = json.loads((HERE / f"runs/{RUN_ID}/1/summary.json").read_text())
    info = json.loads((BINDING / "workspace.json").read_text())
    copyright_result = json.loads((BINDING / "copyright/comparison.json").read_text())
    headers = json.loads((BINDING / "license-header-audit.json").read_text())
    assert headers["pr_head"] == info["pr_head"] and headers["exact_matches"] == 7
    assert summary["status"] == "completed" and summary["conclusion"] == "success"
    assert len(summary["jobs"]) == 6 and all(j["conclusion"] == "success" for j in summary["jobs"])
    assert summary["verified_source_tree"] == info["source_tree"]
    assert summary["module_integration_build"] == "success"
    assert summary["downloaded_artifact_count"] == 3
    assert all(r["new_test_directory_findings"] == 0 for r in summary["lint_findings"].values())
    for name, expected in {
        "GCC15 / Build & Test": "507 tests pass and 7 were skipped",
        "Address & Undefined Behavior Sanitizer / Build & Test": "506 tests pass and 8 were skipped",
        "Thread Sanitizer / Build & Test": "404 tests pass and 110 were skipped",
    }.items():
        assert expected in summary["test_summary_lines"][name][-1]
    for name, targets in summary["new_test_results"].items():
        assert len(targets) == 2
        assert all(state == ("SKIPPED" if name.startswith("Thread") and "/integration_test:" in target
                             else "PASSED") for target, state in targets.items())
    assert copyright_result["identical_normalized_findings"]
    assert copyright_result["candidate_only_findings"] == []
    stamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    head = info["pr_head"]
    tree = info["source_tree"]
    run_url = summary["run_url"]
    counts = {k: v["count"] for k, v in summary["lint_findings"].items()}
    table = "\n".join(
        f"| {j['name']} | Pass | [Job]({j['url']}) |" for j in summary["jobs"]
    )
    measurements = "\n".join(
        f"- {job}: {lines[-1].split('Z ', 1)[-1]}"
        for job, lines in summary["test_summary_lines"].items() if lines
    )
    result = {
        "time_utc": stamp,
        "native_pr_url": "https://github.com/eclipse-score/communication/pull/1335",
        "native_pr_head": head,
        "verified_upstream_baseline": info["pr_base"],
        "verified_source_tree": tree,
        "verification_run": summary,
        "introduced_lint_findings": 0,
        "copyright": copyright_result,
        "license_header_audit": "anonymous-namespace/license-header-audit.json; all seven eligible contribution files exactly match native templates",
        "qnx": "excluded_by_user; upstream rules not waived",
        "native_required_host_statuses_supplied_by_fork": False,
        "contributor_follow_up": "complete",
        "merge_ready": False,
        "remaining_upstream_actions": [
            "maintainer approves native Host workflow and required contexts execute",
            "code-owner approval of final PR source",
            "maintainer disposition of inherited copyright failures",
            "merge queue verifies the eventual merge source",
        ],
        "later_main_changes": "anonymous-namespace/upstream-advance.json; not claimed tested",
        "human_acceptance": "original measured tree only; no follow-up acceptance synthesized",
        "provider_model_calls": 0,
        "original_supervisor": "unchanged and exhausted",
    }
    write(HERE / "completion-result.json", result)
    body = f"""Adds a QM LoLa integration test on Linux for repeated `OfferService`, `StopOfferService`, `StartFindService`, `Subscribe` and `Unsubscribe` calls. It compares discovered service identity/cardinality, verifies absence after each stop, checks subscription state and rejection after each unsubscribe, and verifies sample delivery and recovery with finite deadlines. The harness requires application exit 0. Production APIs are unchanged.

Repeated discovery uses the same callback and instance specifier. Distinct search-operation handles follow the native implementation; every operation must report unchanged discovered service state and is stopped. Callback storage remains alive for the whole test. Follow-ups resolve all introduced clang-tidy findings without changing assertions, execution controls or suppression settings.

Root BUILD also fixes the existing copyright checker input paths for BUILD/MODULE.bazel. This utility change is isolated from the new test directory for separate review.

Relates to #1167.

[Final-source fork Host verification]({run_url}) passes all six native non-QNX jobs for PR head `{head}`, merged with upstream `{info['pr_base']}` (source tree `{tree}`).

{measurements}
- Separate module integration build passes.
- Clang-tidy, clippy and Ruff pass with zero findings in the new test directory. Native formatter and strict Eclipse ECA validation pass.

TSan retains the shared native Docker-integration exclusion (Ticket-249859); its new schema test passes. The new runtime and schema tests pass under GCC15 and ASan/UBSan/leak. The report artifacts contain {counts.get('clang-tidy.sarif', 0)} clang-tidy warnings and {counts.get('clippy.sarif', 0)} clippy warnings outside the new test, and {counts.get('ruff.sarif', 0)} Ruff findings. Failed/superseded predecessor attempts remain preserved.

Direct pinned-checker comparison at the verified baseline reports {copyright_result['candidate_count']} identical inherited copyright findings and zero PR additions; the full check remains failed. Seven header-eligible contribution paths pass; two JSON configurations have no native header template. No waiver is claimed.

Every header-eligible changed file exactly matches the project's Eclipse copyright/license template, including `SPDX-License-Identifier: Apache-2.0`; existing creation years are retained. JSON configurations remain valid JSON. AI assistance: the original draft used DeepSeek deepseek-v4-flash, and review/corrections/verification used OpenAI Codex. Native human maintainer review remains required before merge.

QNX is excluded from contributor verification as requested. Upstream main advanced during verification; those later changes are not claimed tested by this fork run. Native Host workflow approval, required upstream statuses, code-owner approval, inherited copyright handling and the merge queue remain maintainer-owned. Fork results do not supply the required upstream GitHub statuses.
"""
    (BINDING / "PR-BODY-final.md").write_text(body)
    write(BINDING / "pr-body-final-request.json", {"body": body})
    document = f"""# Communication #1167 — contributor follow-up complete

[PR #1335](https://github.com/eclipse-score/communication/pull/1335) has final head `{head}`. All six non-QNX jobs pass in [final-source fork Host run {RUN_ID}]({run_url}). The follow-ups resolve the original three clang-tidy warnings and the subsequent anonymous-namespace preference; final reports have zero findings in the new test directory. Native formatting and strict Eclipse ECA validation pass.

| Native job | Result | Evidence |
| --- | --- | --- |
{table}

{measurements}

The separate module integration build passes. New runtime/schema tests pass under GCC15 and ASan/UBSan/leak. TSan passes the schema test and retains the project's existing Docker-integration exclusion (Ticket-249859); its runtime skip is not represented as a pass. QNX is excluded as requested. The reports retain {counts.get('clang-tidy.sarif', 0)} clang-tidy and {counts.get('clippy.sarif', 0)} clippy warnings outside the new test, and {counts.get('ruff.sarif', 0)} Ruff findings.

## Source and verification artifacts

The run verifies final PR head `{head}` merged with pinned upstream `{info['pr_base']}`, tree `{tree}`. The new test uses a QM LoLa configuration on Linux; these results do not assert other bindings, safety configurations or QNX execution. Every job's actual checkout/tree is verified from complete logs and GitHub immutable commit objects. All 17 native execution controls are unchanged. [Run summary](runs/{RUN_ID}/1/summary.json), [six complete logs](runs/{RUN_ID}/1/logs/), [three native report artifacts](runs/{RUN_ID}/1/artifacts/), [test-result inventories](runs/{RUN_ID}/1/test-results/) and [run digest manifest](runs/{RUN_ID}/1/artifact-manifest.json) are retained.

[Final source binding](anonymous-namespace/subject.json), [native-head source archive](anonymous-namespace/native-head-source.tar.gz), [verified merge archive](anonymous-namespace/verified-merge-source.tar.gz), [archive verification](anonymous-namespace/source-archive-verification.json), [combined patch](anonymous-namespace/combined.patch), [namespace correction](anonymous-namespace/anonymous-namespace.patch), [formatter result](anonymous-namespace/format.json), [ECA validation](anonymous-namespace/eca-validation-result.json) and [execution controls](anonymous-namespace/execution-plan.json) make the result reviewable. Archive verification explicitly binds the tracked symlink and its target. Production APIs, assertions, callback storage lifetimes, finite deadlines and application exit-zero requirement are unchanged by the lint corrections.

Upstream main advanced during verification. [Eight subsequent documentation/tutorial commits](anonymous-namespace/upstream-advance.json) and the later native merge snapshot are retained separately; this fork run does not claim to verify that later merge tree. Native workflow and merge-queue checks must verify the eventual merge subject.

## Copyright and human disposition

[Fresh pinned-checker comparison](anonymous-namespace/copyright/comparison.json) reports {copyright_result['candidate_count']} identical baseline/candidate findings, zero PR additions/removals, both exit 1. [Changed-file check](anonymous-namespace/copyright/changed-files.json) passes the seven header-eligible paths; two JSON configurations have no native template. [Inherited inventory](anonymous-namespace/copyright/inherited-findings.csv) retains all findings: 96 missing, 89 wrong-format, 14 preceded and one duplicate. These are direct executions of pinned score_tooling 2.3.1 with the carried native Python/rapidfuzz runtime, not fresh Bazel invocation claims. The upstream change before the pinned baseline removed five earlier findings and added one (net 204 → 200). No inherited-header repair or waiver was performed.

[Exact license-header audit](anonymous-namespace/license-header-audit.json) independently verifies all seven eligible PR paths against the native template at the beginning of each file, including a single Apache-2.0 SPDX identifier and NOTICE reference. The root BUILD retains its original 2024 creation year; the six new header-eligible files use 2026. The two JSON files remain valid JSON. The [Eclipse handbook](https://www.eclipse.org/projects/handbook/#ip-copyright-headers) permits the project's generic contributor header and calls for headers where technically feasible. The PR description also discloses the actual AI assistance: DeepSeek deepseek-v4-flash for the draft and OpenAI Codex for review/corrections/verification. No human acceptance of the follow-up is invented.

Jefferson Nascimento's [original human acceptance](../acceptance-review/human-decision.json) remains bound to the original measured tree and 503-test run. It is preserved without extending acceptance to these follow-ups or substituting for native code-owner approval. The original paid supervisor and budget remain exhausted and unchanged; no additional provider-model calls occurred.

## Remaining upstream steps

The native Host workflow remains approval-gated and the contributor lacks upstream write permission. ECA and review-checklists pass. Maintainers must approve native workflow execution, obtain successful required upstream contexts, review the final source, determine inherited copyright handling and use the merge queue. QNX remains subject to upstream rules despite its exclusion from this contributor verification. Fork results do not create upstream required statuses. No merge, release, issue closure or additional reviewer message was performed.

## Preserved attempts

[Run 37637574398](runs/37637574398/1/summary.json) retains the initial source's build/sanitizer/linter results and failed clang-tidy SARIF-upload step. Its unchanged report was independently accepted and processed through the fork's Code Scanning API; the failed job was not relabeled. [Run 37644643394](runs/37644643394/1/summary.json) retains the cancelled upstream-refresh attempt. [Run 37645549862](runs/37645549862/1/summary.json) passed all six jobs but reported the final new-test namespace warning, which this final source corrects. Each attempt retains its own source bindings, raw logs and digest manifest.

The temporary [fork verification PR #1](https://github.com/jnsagai/communication/pull/1) is closed after exporting final results. Scheduled, QNX and unrelated workflows remain disabled in the fork; the original enabled/all Actions permissions are restored. [Completion record](completion-result.json) distinguishes measured contributor completion from pending upstream acceptance. The refreshed portable inventory binds the final packet and preserves all predecessor evidence.
"""
    (HERE / "README.md").write_text(document)
    (ROOT / "CURRENT-STATUS.md").write_text(
        "# Communication #1167 — non-QNX contributor work complete\n\n"
        f"[PR #1335](https://github.com/eclipse-score/communication/pull/1335), head `{head}`, now has "
        f"[all six non-QNX fork Host jobs passing]({run_url}) with zero lint findings in the new test. "
        "GCC15 passes 507 tests (seven skipped) and module integration; ASan/UBSan/leak passes 506 (eight skipped); "
        "TSan passes 404 (110 skipped under native exclusions). New runtime/schema tests pass under GCC15 and ASan. "
        "QNX is excluded as requested.\n\n"
        f"The exact verified merge tree is `{tree}` on upstream `{info['pr_base']}`. Later upstream changes are "
        "recorded separately and await native CI. Source archives, patches, full logs, three native lint reports, "
        "test inventories, unchanged controls, formatting and ECA proof are in the [final verification packet](non-qnx-verification/README.md).\n\n"
        "Copyright remains failed with 200 identical findings on the pinned baseline, zero PR additions. "
        "Seven header-eligible contribution files pass; two JSON files have no native header template. "
        "The original scoped human acceptance is preserved on its original source, without a follow-up acceptance or copyright waiver.\n\n"
        "The PR remains unmerged: maintainers must approve native workflow execution, obtain required upstream statuses, "
        "approve the final source through code-owner review, determine inherited copyright handling and use the merge queue. "
        "Fork results do not satisfy upstream required contexts automatically. All predecessor evidence and the exhausted paid supervisor remain unchanged.\n"
    )
    handoff_path = ROOT / "session-handoff.json"
    handoff = json.loads(handoff_path.read_text())
    handoff.update({
        "time_utc": stamp,
        "historical_native_publication_head": "a8e81c795b7f45e663d608a33c5e358cfd765ea9",
        "native_publication_head": head,
        "latest_host_verification": run_url,
        "latest_host_verified_tree": tree,
        "latest_host_verified_base": info["pr_base"],
        "latest_host_verification_result": "six fork jobs pass; zero introduced lint findings",
        "latest_non_qnx_packet": "non-qnx-verification/README.md",
        "latest_copyright_comparison": "200 identical findings on pinned verification baseline; full check failed",
        "task_status": "non_qnx_contributor_follow_up_complete_upstream_acceptance_pending",
        "next_obligation": "Maintainers approve native workflow execution and final source; required upstream checks, copyright handling and merge queue remain",
        "qnx_follow_up": "excluded explicitly by user; native rules not waived",
        "latest_host_full_suite": {"passed": 507, "skipped": 7, "failed": 0},
        "host_workflow_status": "native approval gated; contributor fork six jobs success",
        "current_verified_source_binding": "non-qnx-verification/anonymous-namespace/subject.json",
        "current_portable_artifact_root": str(ROOT),
        "latest_disposable_workspace": "non-qnx-verification/anonymous-namespace/workspace.json",
        "human_acceptance_source": "original measured source only",
        "new_provider_model_calls_for_non_qnx_follow_up": 0,
    })
    write(handoff_path, handoff)
    with (ROOT / "RESUME-HANDOFF.md").open("a") as out:
        out.write(f"\n## Completed non-QNX follow-up — {stamp}\n\nRead CURRENT-STATUS.md and non-qnx-verification/README.md first. Native PR head {head}; final fork run {RUN_ID} passes all six jobs, zero new-test lint findings. GCC15 507/7, ASan 506/8, TSan 404/110, module integration passes. QNX excluded. Tree {tree} is bound to upstream {info['pr_base']}; later main changes remain untested by this fork run. Full logs, source archives, reports, test inventories, controls, ECA and 200 baseline-identical failed copyright findings are retained. Maintainers own native CI approval/statuses, code-owner acceptance, copyright handling and merge queue. Original human decision/source and exhausted supervisor are preserved; do not reset any paid budget or historical storage binding. New scratch root: {info['run_root']}; validate its own saved storage before reuse.\n")
    readme_path = ROOT / "README.md"
    old = readme_path.read_text()
    marker = "<!-- latest-non-qnx-follow-up -->"
    if marker not in old:
        readme_path.write_text(old.split("\n", 1)[0] + "\n\n" + marker + "\n"
            f"Latest: [PR #1335](https://github.com/eclipse-score/communication/pull/1335) has all six non-QNX fork Host jobs passing, 507 GCC15 tests and zero new-test lint findings. [Final packet](non-qnx-verification/README.md) includes the revised source, sanitizer results, complete reports and 200 inherited copyright findings on its pinned baseline. Native CI approval, code-owner review, copyright handling and merge queue remain pending; original acceptance/evidence below are historical.\n\n" + old.split("\n", 1)[1])
    merge_readme = ROOT / "merge-readiness/README.md"
    old = merge_readme.read_text()
    if marker not in old:
        merge_readme.write_text(old.split("\n", 1)[0] + "\n\n" + marker
            + "\nThis audit is the retained 14:20 snapshot. The [final non-QNX follow-up](../non-qnx-verification/README.md) now supplies all six passing fork jobs and final-source evidence; native workflow approval and upstream acceptance remain pending. Raw historical gate records below are preserved.\n\n" + old.split("\n", 1)[1])
    index = ROOT.parent / "README.md"
    lines = index.read_text().splitlines()
    for n, line in enumerate(lines):
        if line.startswith("| [Communication #1167]"):
            lines[n] = "| [Communication #1167](communication-1167/README.md) | COM API idempotency integration test | Six non-QNX fork Host jobs pass; 507 GCC15 tests; zero new-test lint findings; 200 inherited copyright findings on pinned baseline | [PR #1335 open](https://github.com/eclipse-score/communication/pull/1335); ECA passed; native workflow approval, code-owner review, copyright handling and merge queue pending |"
    index.write_text("\n".join(lines) + "\n")
    gaps = ROOT.parent / "EVIDENCE_GAPS.md"
    lines = gaps.read_text().splitlines()
    for n, line in enumerate(lines):
        if line.startswith("Communication #1167 now has native"):
            lines[n] = "Communication #1167 has [PR #1335](https://github.com/eclipse-score/communication/pull/1335) with all six non-QNX fork Host jobs passing, zero lint findings in the new test, official ECA validation and full final-source artifacts. The pinned-baseline copyright comparison remains failed with 200 identical inherited findings and zero PR additions. Native workflow approval/required statuses, code-owner approval, copyright handling and merge queue remain pending; later upstream changes are not claimed tested by the fork. QNX is excluded by the user, without waiving upstream rules. Original human acceptance remains tied to the original measured source. [Final records](communication-1167/CURRENT-STATUS.md) preserve all attempts."
    gaps.write_text("\n".join(lines) + "\n")
    print(json.dumps({"prepared_final_packet": True, "head": head, "run": run_url}))


if __name__ == "__main__":
    main()
