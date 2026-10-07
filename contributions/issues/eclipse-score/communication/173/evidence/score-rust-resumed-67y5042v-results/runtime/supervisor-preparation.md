# Communication #173 — independent supervisor preparation

This is a read-only preparation review for the resumed dependency assessment. It recommends scope and dispositions; it does not report the new native run as verified, qualify a component or supply human acceptance. No source edits, builds, runs or source-budget expenditure were performed by this supervisor. Only this report was written.

## Baselines and freshness

The communication baseline remains `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Its `MODULE.bazel:41` consumes the `score_crates` index module version `0.0.11`. The fresh documentation snapshot is separately pinned to score-crates commit `ee5f1a4f02dcfaa01d7a5e23ec68fd51590a66f8`. That snapshot's own `MODULE.bazel:15` labels its module `0.0.7`; this literal is not evidence that communication changed its resolved index or adopted the current snapshot. Do not silently substitute the fresh documentation commit for the dependency source pin.

Read-only verification confirms all 19 fetched score-crates artifacts match both recorded SHA-256 and Git blob identities, and all 12 fetched crate archives and retained manifest/license/source-text identities match `context/crate-provenance.json`. Shared storage validation succeeds for this SSD-bound root. `context/carried-source-verification.json` reports 2,186 unchanged communication subjects; that operator assertion is not independently rehashed by this preparation review. Historical test results are not carried as fresh results here.

The original issue premise refers to `paste`, while the inspected baseline uses `pastey` in `score_com_concept/BUILD:22` and its macro expansions/re-exports. The selected lock records retain `pastey 0.2.3` with no enabled features, `thiserror/thiserror-impl 2.0.21`, and `futures` family `0.3.34`. Fresh package manifests identify `MIT OR Apache-2.0` licensing; Pastey's MSRV is 1.54, thiserror's 1.77 and the futures facade's 1.71. These resolve historical unknown archive/license facts; they do not establish advisories, maintenance suitability, accepted license compliance or qualification.

## What #42 and the native records establish

`context/score-crates-42.json` records the epic closed on 2026-07-09. Its acceptance criterion is availability and review of Pastey qualification-related artifacts. The 2026-06-18 maintainer comment in `score-crates-42-comments.json` explicitly says S-CORE prepares artifacts for distributor/integrator qualification and does not qualify platform components. #42 concerns Pastey; it is not a general accepted policy or qualification result for thiserror, futures or all external crates. Communication #173 remains open in the supplied API capture.

Fresh sources under `context/score-crates/` provide:

- `docs/pastey/docs/component_classification.rst:18–33`: native ID `doc__pastey_crate_comp_class`, status `valid`, safety `ASIL_B`, and specifically crate version `0.2.3`. The matching crate version supports relevance to the selected Pastey archive.
- The same classification's Step 5, lines 225–231: safety-plan adaptation is conditional on an accepted change request; Q selects the processes for qualification. Preserve its P=2, C=1, CLAS_OUT=Q source assertion without converting it into authenticated integration acceptance.
- `docs/pastey/docs/safety_analysis/aou.trlc:17–24`: `PasteyAoU.PasteyRustCompilerCertified`, version 1, requires the compiler used to build Pastey to be safety certified up to ASIL B. `failure_modes.trlc` defines `PasteyFailureModes.UncertifiedRustCompiler`, version 1.
- Requirements `RustCrateSysReq.ASR_RUST_CRATE@1`, `PasteyFeatReq.FEAT_PASTEY_001@1` and `PasteyComReq.REQ_COMP_PASTEY_001` through `015`, all version 1. These native records do not acquire a new status or approval from this assessment.
- `docs/pastey/tests/pastey_test.rs`: requirement trace annotations and positive tests, plus negative cases expressed as compile-fail doctests. `docs/pastey/tests/BUILD:16–38` separates `pastey_test` from `pastey_doc_test`; running the unit target alone does not execute the negative doctests.
- `docs/pastey/docs/BUILD:33–43`: the `pastey` dependable-element target references requirements, architecture, analysis, AoU and tests. Target/source presence is not a generated trace report.

Concrete remaining qualification gaps: no accepted adoption/safety-plan change is established; no exact compiler-version/target/use certificate or safety-manual applicability is demonstrated by the fresh documentation; no generated LOBSTER report is supplied by this preparation review. Classification lines 236–243 assert trace completeness, note the Rust test-result parsing limitation, and describe certified Ferrocene/core/std usage. Retain these as upstream assertions; fresh compiler identity and local test success alone cannot discharge the compiler AoU or demonstrate applicability of all stated library assurances. Cases relying on `env!` also prevent a general claim that environment has no effect on all Pastey features, even though COM's selected suffix-only usage is narrower.

## Native check scope

The new four-group `check-plan.json` is a useful bounded assessment scope: concept and macro unit tests; explicitly selected manual macro doctests; native sync/async integration suites; Clippy on concept and public facade. Preserve expected cases, exclusions, failures and warnings separately. Require raw XML/log evidence for each suite and zero missing cases; process exit alone is insufficient. Confirm actual analyzer execution rather than configuration selection or action-cache presence.

The frozen original `execution/check-1/native-result.json` contains seven successful query/build checks, one successful concept test, then exit 2 for macro-unit tests. Its raw `check-8.log` ends with a rules_python module-extension loading failure. This is missing macro behavioral evidence, not a demonstrated failing macro assertion. Rerunning the relevant tests is justified. The old prose saying no native checks or no qualification sources were available describes its author's historical boundary and must not become the fresh conclusion.

Doctests are required to substantiate compile-fail behavior. The communication macro doctest is tagged manual with a native link limitation at `score_com_concept/BUILD:49–54`; selection does not guarantee execution. If it fails or remains excluded, retain that gap. Communication integration demonstrates selected generated API paths, not every Pastey requirement. The fresh score-crates Pastey tests are source evidence unless their own selected rules are actually run; no upstream coverage percentage or full requirement verification follows from COM tests.

The four groups do not measure the entire original plan: derive-macro doctests, all downstream/examples, complete reverse dependencies, full formatting/API surface checks, all transitive dependency behavior or qualification trace generation remain unmeasured unless separately supplied and hash-verified. QNX and other targets remain excluded. Label these scope gaps instead of expanding the run or consuming another issue's budget without authority.

## Authority and disposition

No retain/replace/internal implementation is accepted here. A bounded recommendation to retain the existing Pastey pin can be assessed using its now-available evidence while keeping integration adoption, host proc-macro trust, tool/component applicability and general external-crate policy decisions pending offline. DeepSeek Flash output is an agent assessment, not an acceptance or deterministic measurement.

The resumed state preserves #173 at 2/3 source corrections, #250 at 1/3 and #1261 at 1/3. The separately authorized #560 Codex allowance remains 1/3 used and is not transferable. This preparation review consumes none of those corrections. Await the final measured evidence for independent terminal review; preserve frozen packets, current source/lock/policy pins and historical failures.
