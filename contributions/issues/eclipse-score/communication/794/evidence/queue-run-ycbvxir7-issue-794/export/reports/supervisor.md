# supervisor.md — Independent read-only review, Issue #794

"Improvement: Remove bazel `tags = ["manual"]` from rust test targets"

- **Repository / issue**: eclipse-score/communication #794
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
- **Runtime / model**: Linux only; DeepSeek Flash only. No QNX task or execution.
- **Reviewer authority**: disposable workspace, file tools only. Shell, delegation,
  publishing, web/retrieval and acceptance tools are blocked; this review executed
  **no** native command and fabricated no evidence. Command stages and raw evidence
  remain outside agent authority.
- **Review method**: bounded (≤200-line) reads of the checked-out BUILD/bzl/bazelrc/
  workflow sources; read of the supplied reports and
  `.rust-queue/reports/native-check-summary.json`; independent re-derivation of the
  issue's acceptance criterion from source. Direct grep was unavailable within the
  boundary, so claims were verified by reading the exact files cited.
- **Headline disposition**: **The issue's source-level premise is already satisfied at
  the reviewed tree; no source patch is owed. The deterministic measurement did NOT
  pass (lint check failed, repeated and unchanged across attempts 0–3), so this run is
  an assessment / blocker record — it is not an implemented issue fix, and native
  engineering acceptance remains PENDING.**

---

## 1. Independent verification of the scope claims

Source was read directly; the prior reports' citations were spot-checked and are
accurate.

| Target (BUILD label) | Rule | `tags = ["manual"]` in the reviewed tree | Reviewer-verified source |
| --- | --- | --- | --- |
| `//score/mw/com/rust/score_com_concept:score_com_concept-test` | `rust_test` | **absent** (Linux `target_compatible_with` only) | `score/mw/com/rust/score_com_concept/BUILD:35-44` |
| `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | `rust_test` | **absent** (Linux `target_compatible_with` only) | `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD:36-46` |
| `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | `rust_test` | **absent**; sanitizer-incompatible `select` | `score/mw/com/example/com-api-example/BUILD:52-74` |
| `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | `rust_doc_test` | **present at `:54`, documented** | `score/mw/com/rust/score_com_concept/BUILD:46-56` |
| `//score/mw/com/rust/score_com_macros:score-com-macros-tests` | `rust_doc_test` | **absent** | `score/mw/com/rust/score_com_macros/BUILD:29-33` |
| `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | `rust_doc_test` | **absent** | `.../com-api-runtime-lola/BUILD:48-53` |
| `rust_unit_test` `_linux`/`_qnx` internals | `rust_test` | `manual` **by macro design** | `quality/unit_testing/unit_testing.bzl:170`, forwarding at `:181-195` |

Conclusions independently confirmed:

1. The two targets named by the issue body ("runtime" and "concept" test target of the
   `score_com` Rust library) carry **no** `manual` tag at the reviewed tree. The issue
   premise is already implemented; removing the tag would be a no-op.
2. The single retained `manual` Rust **test** is the concept doc test; the tag is
   justified in-source by a `rust_doc_test` native-link limitation (it inherits
   `crate_type="lib"`, so `_add_native_link_flags()` skips the linked C++ deps and LLD
   reports undefined symbols). Removing it would inject a known-broken test into
   `bazel test //...`. Keeping it is correct under the "do not remove exclusions to
   obtain cleanliness" rule.
3. `target_compatible_with = ["@platforms//os:linux"]` on the two issue targets is a
   platform gate, not a `manual` tag; it is out of scope for #794 (tracked by #1278).
4. The issue author's comment (2026-10-05) is consistent with the source, but per the
   workflow it is treated as **prose data, corroboration only** — the source, not the
   comment, is the authority above.

> Review note (ambiguity): the issue text "runtime and concept test target" is
> satisfied by `com-api-runtime-lola-tests` and `score_com_concept-test`. The concept
> package also contains `score_com_concept-macros-tests` (doc test), which legitimately
> remains `manual`. The scope reports chose the narrower, source-justified reading. That
> reading is defensible and is recorded here as an interpretation, not a fact the issue
> states.

## 2. Patch / changed-path review

- **No source diff.** No file under `score/`, `quality/` or any native build path was
  modified; the reviewed BUILD files carry intact Apache-2.0 headers and licenses, and
  the pinned rules/toolchains were not touched. The measured subject hash is byte-identical
  across all four attempts (see §3), consistent with a zero source change.
- **Disposition of the deliverable.** Because the premise is already present at the
  reviewed tree, the correct workflow outcome is a documented assessment, not a
  manufactured edit. The prior reports (`implementation.md`, `correction-1..3.md`) do
  **not** claim a fix; they are assessment/blocker records.
- **This is not an implemented issue fix.** No native work product was changed and the
  deterministic run did not pass. It must not be reported to the user as "issue #794
  fixed".

## 3. Measured evidence review

Supplied evidence: `.rust-queue/reports/native-check-summary.json` (currently the
`check-3` / `attempt: 3` summary) plus the four bounded summaries echoed by the stage
prompts. `engineering_acceptance = "pending"`, `infrastructure_error = null`,
overall `passed: false`, `exit_code: 1`.

| # | kind | target(s) | exit | result |
| --- | --- | --- | --- | --- |
| 1 | query | `//score/mw/com/rust/score_com_concept:all` | 0 | resolves rules (target list only) |
| 2 | build | `//score/mw/com/rust/score_com_concept:score_com_concept` | 0 | rlib produced |
| 3 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-test` | 0 | PASSED |
| 4 | test | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests` | 0 | PASSED |
| 5 | query | `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests` | 0 | resolves `rust_doc_test` (no tags shown) |
| 6 | build | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | 0 | rlib produced |
| 7 | test | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` | 0 | PASSED |
| 8 | docs | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests` | 0 | rustdoc runner generated |
| 9 | docs | `//score/mw/com/rust/score_com_macros:score-com-macros-tests` | 0 | rustdoc runner generated |
| 10 | build | `//score/mw/com/example/com-api-example:com-api-example-lib` | 0 | rlib produced |
| 11 | test | `//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` | 0 | PASSED (6.1s, default config) |
| 12 | lint | `...:score_com_concept`, `...:com-api-runtime-lola` | 1 | **FAIL — Bazel analysis/config error, no source diagnostic** |

Verified evidence bindings:

- `measured_subject_hashes_sha256` = `3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`
  — **identical** for attempts 0, 1, 2, 3.
- `native_result.sha256` per attempt: 0 → `540888a8…b25f87c`, 1 → `fc14ae59…d3ff63d`,
  2 → `2036a143…91bf49b`, 3 → `096dd1e8…5ef8beb`.

### 3.1 The lint failure — observed facts vs. inference

Observed (bounded tail, identical across attempts):

```
WARNING: The following configs were expanded more than once: [_lint]. ...
ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once
...
WARNING: errors encountered while analyzing target '...com-api-runtime-lola', it will not be built.
WARNING: errors encountered while analyzing target '...score_com_concept', it will not be built.
ERROR: command succeeded, but not all targets were analyzed
ERROR: Build did NOT complete successfully
```

Independently re-derived from source:

- `quality/static_analysis/static_analysis.bazelrc:29-30` — `build:clippy` expands
  `--config=_lint` and adds the `clippy_strict` aspect **once**.
- `quality/static_analysis/static_analysis.bazelrc:15-18` — `build:_lint` adds no aspect.
- `.bazelrc:186-188` — imports `static_analysis.bazelrc` once; no other config adds the
  clippy aspect (`.bazelrc` read end-to-end, incl. `try-import` tail at `:199-203`).
- `.github/workflows/_linter.yml:83-86,115-125` — CI deliberately registers the aspect
  once and documents that Bazel rejects duplicate aspect registration.

**Assessment**: with the checked-in configuration registering the aspect exactly once, a
duplicate-registration error is most consistent with the *invoking command* expanding
`--config=clippy`/`--config=_lint` (or passing `--aspects=…%clippy_strict`) more than
once. This matches the prior reports' `correction-1..3` root-cause hypothesis.

**Gap (must be preserved as unproven)**: the exact lint command line is **not** part of
the supplied evidence (only a bounded tail). The duplicate-aspect attribution is a
source-backed *inference*, not a measured fact. It is not established that the
repository's own CI form would fail; equally, it is not proven the harness command was
malformed. The only measured facts are: a lint kind was invoked, and it aborted in
analysis with an aspect-registered-twice error. Treat as a measurement-pipeline /
invocation precondition failure of unknown exact form — not `infrastructure_unavailable`
(`infrastructure_error = null`) and not a defect in the issue's change surface.

### 3.2 Central verification gap — the acceptance criterion was not measured

The issue's real outcome is that the two tests are **discovered by `//...`** (i.e. they
are no longer `manual`). The executed `test` checks invoke the targets by **explicit
label**, which runs them regardless of any `manual` tag. The two `query` checks print
rule *kinds* only and do **not** emit `tags`. Therefore:

- The measured evidence establishes that the two tests pass when invoked explicitly.
- It does **not** measure the property the issue is actually about (absence of the
  `manual` tag / wildcard discovery). That property is currently **source-verified only**.
- A conformant check should expose tags, e.g. `bazel query --output=build <label>` or a
  discovery run. This is a proposed addition (§5), not something executed.

This is the most important correctness/coverage gap in the packet and should gate any
readiness claim.

## 4. Gaps by class (as applicable)

- **Correctness / build-tagging**: no source defect found. The requested tag removal is
  already present. No regression test is owed (adding one would duplicate the already-correct
  tagging).
- **FFI / native-link**: the retained `manual` on `score_com_concept-macros-tests`
  masks a real, documented `rust_doc_test` → C++-link (LLD undefined-symbol) limitation.
  It is an **excluded check** and remains unverified. Out of #794 scope; preserved.
- **Concurrency**: the now-enabled
  `com-api-example-tokio-integration-test` is excluded from sanitizer configs via
  `target_compatible_with` (`BUILD:64-67`) because of a LeakSanitizer finding from
  `tokio::...::multi_thread::MultiThread::new` (`asan_ubsan_lsan`) and a TSan data race
  in `<String as Clone>::clone` between the test thread and a `tokio-rt-worker`
  (`tsan_ubsan`). This is a genuine unresolved concurrency/leak qualification gap,
  explicitly deferred. **Pending offline acceptance**; the sanitizer gate is untouched.
- **Platform**: both issue targets and the doc/example targets remain Linux-only
  (`@platforms//os:linux`); QNX coverage is absent by design (#1278) and out of scope.
- **Trace / native IDs**: no requirement/design/verification identifiers were found in
  the touched build files; the issue template's two impact boxes are unchecked. These
  remain **unknown** and must not be fabricated.
- **Qualification**: no tool-qualification claim is made or supported; Ferrocene is the
  selected Rust toolchain in the build config but its qualification for this workflow
  was not assessed.
- **Evidence freshness / staleness**: `scope.md` and `implementation.md` state that
  `.rust-queue/reports/native-check-summary.json` "does not exist". That statement was
  true at their authoring time but is **superseded** — the collector later supplied the
  file (now `attempt: 3`). The stale statement is preserved as history, not corrected in
  place.

## 5. Check-plan conformance and proposed additions

The existing `.rust-queue/reports/check-plan.json` conforms to the required Linux schema:
every entry has `kind` in `{query,test,build,docs,lint}`, BUILD-derived `targets`,
a `reason`, a `native_obligation`, and `config: "linux_x64"`; no QNX entries. Labels are
source-backed.

Proposed additions (proposals only — **not executed**, subject to collector authority):

```json
{"checks":[
  {"kind":"query",
   "targets":["//score/mw/com/rust/score_com_concept:score_com_concept-test",
              "//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests",
              "//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests"],
   "reason":"Acceptance requires that the issue-scope tests are no longer manual (wildcard-discoverable) while the documented LLD-limited doc test remains manual. A plain label query does not emit tags, so it cannot confirm this; use --output=build/--output=jsonproto to expose effective tags.",
   "native_obligation":"Wildcard CI discovery in .github/workflows/_build_and_test_gcc15.yml (`bazel test --config=ci //... --build_tests_only`); `manual` targets are excluded from `//...`.",
   "config":"linux_x64"},
  {"kind":"test",
   "targets":["//score/mw/com/example/com-api-example:com-api-example-tokio-integration-test"],
   "reason":"Confirm the source-asserted sanitizer SKIP (target_compatible_with select on @score_cpp_policies//sanitizers/flags:any_sanitizer) under an asan/tsan config; the supplied evidence only shows the default-config PASS, so the SKIP behavior is currently source-asserted, not measured.",
   "native_obligation":".github/workflows/_address_sanitizer.yml (`--config=asan_ubsan_lsan`) and _thread_sanitizer.yml (`--config=tsan`); the target must report SKIPPED, not run.",
   "config":"asan_ubsan_lsan|tsan"}
]}
```

(The second entry's `config` deliberately names the sanitizer configs; the collector
schema example shows `linux_x64`, so the collector must normalize this to a supported
value or reject it. It is flagged as a scope question, not a valid native label.)

## 6. Acceptance and disposition

- **Source premise**: satisfied (already implemented at the reviewed tree).
- **Measured run**: **not passed** — 11/12 checks pass, the lint check fails in analysis
  for a repeated, unchanged, invocation-level reason. Per the workflow, the run stopped
  on the repeated unchanged failure rather than broadening.
- **Engineering acceptance**: **PENDING**. The supplied `engineering_acceptance` is
  `"pending"` and nothing here overrides it. Passing tests, clean analyzers and workflow
  success cannot supply acceptance; authorized humans decide offline.
- **Not qualified / not accepted / not released**: no native work product is marked
  accepted or closed. The Tokio sanitizer follow-up remains open.
- **Prior reports are assessment/blocker records**, not an implemented issue fix. This
  review does not elevate them.

## 7. Preserved evidence and unresolved items

- **Failures preserved**: four `check` attempts (0, 1, 2, 3) all `passed:false`; the
  `check-0..2` native-result hashes are retained in `correction-1..3.md`; the current
  `native-check-summary.json` holds `check-3`. Nothing was overwritten or re-labelled.
- **Missing/uncertain evidence preserved**: exact lint command line absent (root cause
  inferred); sanitizer-SKIP not measured; wildcard-discovery/tag property not measured;
  requirement/design/verification native IDs unknown.
- **Pending offline acceptance preserved**: Tokio multi-thread LSan/TSan findings and
  the decision to fix or suppress them (outside #794 acceptance).
- **No QNX** execution or tasking; no credentials or secrets embedded; licenses/pins/lint
  policy left intact.

## 8. Concrete next action

1. (Collector authority, outside agent) Re-run the `lint` obligation with the
   `clippy_strict` aspect registered exactly once, matching
   `.github/workflows/_linter.yml:115-125`:
   `aspect lint --bazel-flag=--config=ci --bazel-flag=--config=clippy -- //...`
   (or an equivalent single-`--config=clippy` build that adds no explicit `--aspects`).
   Record the exact command and raw log — the current inference needs the command to
   become established evidence.
2. (Collector authority) Add a tag-exposing query (or `//...` discovery) so the actual
   acceptance property (non-`manual`, wildcard-discoverable) is measured, not inferred;
   and measure the example test's SKIP under a sanitizer config.
3. (Authorized humans) Decide the Tokio LSan/TSan follow-up; native engineering
   acceptance of #794 remains pending until the required human decision.

## 9. Manifest

No source files changed by this review. No file digest is computable within the
file-tool boundary (no shell/hash tooling); binding is by exact repository-relative
path and baseline commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.

- Reviewer artifact: `.rust-queue/reports/supervisor.md` (this file).
- Read-only reviewed inputs: `.rust-queue/context/{issue,task,comments}.json`,
  `.rust-queue/context/score-rust-workflow/SKILL.md` and references
  (`issue-types.md`, `native-verification.md`), `.rust-queue/reports/{scope.md,
  implementation.md, check-plan.json, correction-1..3.md, native-check-summary.json}`,
  and source under `score/mw/com/rust/score_com_concept/BUILD`,
  `score/mw/com/impl/rust/com-api/com-api-runtime-lola/BUILD`,
  `score/mw/com/example/com-api-example/BUILD`,
  `score/mw/com/rust/score_com_macros/BUILD`,
  `score/mw/com/impl/plumbing/rust/BUILD`,
  `quality/unit_testing/unit_testing.bzl`,
  `quality/static_analysis/static_analysis.bazelrc`, `.bazelrc`,
  `.github/workflows/_linter.yml`.
