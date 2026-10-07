# Supervisor review — issue 1062

**Issue:** eclipse-score/communication#1062 — *Improvement: E2E protection for Rust Method/Field APIs*
**Mode:** `design` (`.rust-queue/context/task.json`)
**Baseline:** `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
**Platform/config:** Linux only (`linux_x64` → `linux_x64_gcc_15`); no QNX
**Model under review:** DeepSeek Flash
**Review type:** independent, read-only (scope + patch + measured evidence)
**Reviewer authority:** none beyond this report; acceptance is not claimed
**Report scope:** this file only; no source, test, config, policy or check-plan file edited

> **Disposition headline:** the deliverable is a **design/blocker assessment**, not an
> implemented issue fix. There is **no source patch**. Measured verification is **not green**:
> 9 of 10 checks pass, the lint row fails with an invocation-level duplicate-aspect error, and
> engineering acceptance remains **pending**. This report preserves the failed/missing evidence
> and does not upgrade any status.

---

## 1. Patch / changed-path review

| Expected | Observed | Verdict |
| --- | --- | --- |
| Source change implementing E2E for Rust Method/Field | **none** — `score/mw/com/**` unchanged | Correct for a `design`-mode issue whose body states "Not designed yet … design discussion … before implementation" |
| Report artifacts | `scope.md`, `e2e-design-draft.md`, `check-plan.json`, `implementation.md`, `open-decisions.json`, `evidence-status.json`, `review-packet.md`, `correction-1..3.md`, `native-check-summary.json` | Present under `.rust-queue/reports/` |
| Measured subject stability | `measured_subject_hashes_sha256 = 3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996` **identical across attempts 0–3** | Consistent with "no source change"; the subject measured did not move |

**Patch disposition: empty source diff.** The design-mode content is appropriate, but it must
**not** be labelled or accepted as a fix for #1062. The issue's requested outcome (working E2E
protection on Rust `Method<T>`/`Field<T>`) is **not attained and not attainable at this baseline**
(see §5).

I could not independently confirm the empty diff with `git status`/`git diff` (shell blocked), so
this rests on the harness-supplied identical subject hash plus the report inventory.

---

## 2. Measured evidence review (preserved, not re-scored)

Per `.rust-queue/reports/native-check-summary.json` (`attempt: 3`) and the stage outputs:

| # | Kind | Result | Exit |
| --- | --- | --- | --- |
| 1 | build `//score/mw/com/rust/score_com_concept:score_com_concept` | PASS | 0 |
| 2 | build `//score/mw/com/rust:score_com`, `:score_com_mock` | PASS | 0 |
| 3 | build `.../com-api-runtime-lola`, `.../com-api-ffi-lola:bridge_ffi_rs`, `:bridge_ffi_lola` | PASS | 0 |
| 4 | build `//score/mw/com/rust/score_com_cpp_bridge:register_interface` | PASS | 0 |
| 5 | test `.../score_com_concept-test`, `...:score_com_concept-macros-unit-tests` | PASS 2/2 | 0 |
| 6 | test `.../com-api-runtime-lola-tests` | PASS 1/1 | 0 |
| 7 | test `.../consumer_sync_apis/integration_test:test_com_api_sync`, `.../consumer_async_apis/integration_test:test_com_api_async` | PASS 2/2 | 0 |
| 8 | docs `.../com-api-runtime-lola-doc-tests`, `...:score_com_concept-macros-tests` | PASS | 0 |
| 9 | docs `//docs/sphinx:sphinx_doc` | PASS | 0 |
| 10 | **lint** same 3 Rust targets under `clippy_strict` | **FAIL** | **1** |

Retained raw evidence (not rewritten):

| Attempt | `native_result.sha256` | `measured_subject_hashes_sha256` |
| --- | --- | --- |
| 0 | `28c9a8a08112d2698dcbbabf90384cc6a05dce9f4fa6b4da590ba3a4ceb058a2` | `3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996` |
| 1 | `fd882dbaf05022f01006f6583f7ba8edfda2bbc16bfe45a24fc06d1d6301f43a` | (same) |
| 2 | `1d32a0c1f60fa254727681eaa08f9440464107da3baf364440cce3fe4ef4e8f8` | (same) |
| 3 | `a22ea73f8afc189598b3d6b8c70693b7b8d7253c6c434ad7b0aec4d1c3be8d06` | `3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996` |

Authoritative measured subject hash in every attempt:
`3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996`.

**The lint row is a genuine non-zero check result** (`infrastructure_error: null`) and is preserved
as **FAILED**. `passed: false` overall is correct and must stand.

### 2.1 Independent root-cause check of the failing lint row

I re-read the in-repo truth rather than accepting the correction reports verbatim:

- `.bazelrc:188` — imports `quality/static_analysis/static_analysis.bazelrc` **once**
  (lines 186–187 import coverage/sanitizer; 200/203 are unrelated `try-import`s).
- `quality/static_analysis/static_analysis.bazelrc:29-30` — declares the aspect **once**:
  `build:clippy --config=_lint` and
  `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`.
- `build:_lint` (lines 15–18) sets toolchain/output-group/fail-on-violation/keep-going and does
  **not** declare the aspect.

Observed failure signature: `configs expanded more than once: [_lint]` →
`ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once` →
`errors encountered while analyzing target …, it will not be built` → `command succeeded, but not
all targets were analyzed`, `exit 1`.

**Independent conclusion (concurs with corrections 1–3):** the repository lint policy is
single-sourced and correct; the duplicate aspect arises from the **measurement invocation**
(command construction / harness), which is **outside agent authority**. It analysis-aborts before
any Clippy action runs, so it is **not** a source/test defect and is **not repairable by a source
patch**. I did **not** see the exact lint command, so I cannot rule out that the harness intentionally
passes `--config=clippy` plus an explicit aspect; either way the remedy is operator-side
de-duplication, not a repo edit.

**Do not** mark this row green, remove it, downgrade it or re-label it. A fourth identical rerun is
unproductive (unchanged failure on an unchanged subject) — escalate the invocation to the operator.

---

## 3. Independent verification of source claims (bounded reads)

| Claim in scope/implementation/packet | My independent check | Result |
| --- | --- | --- |
| `interface!` rejects `Method<T>`/`Field<T>` | `score/mw/com/rust/score_com_concept/interface_macros.rs:110-122` read | **Confirmed** — `compile_error!` for both arms |
| Public re-exports are Event-only, no `Method`/`Field` concept | `score/mw/com/rust/score_com.rs:137-142` read | **Confirmed** — `Publisher/Subscriber/Subscription/...` only |
| FFI bridge member registry "Currently used for events" | `.../com-api-ffi-lola/registry_bridge_macro.h:576-586` read | **Confirmed** — `MemberOperation`/`InterfaceOperations` comments state events-only |
| No E2E implementation file | recursive name glob `**/*e2e*`, `**/*E2E*` | **Confirmed on filename basis only**; content grep was blocked, so a non-file-named E2E symbol is not excluded |
| Check-plan target labels are real BUILD-derived labels | read `score_com_concept/BUILD`, `score/mw/com/rust/BUILD`, `score_com_cpp_bridge/BUILD`, `com-api-runtime-lola/BUILD`, `com-api-ffi-lola/BUILD`, `consumer_sync_apis/integration_test/BUILD` | **Confirmed** — every label in `check-plan.json` exists |
| Requirement IDs cited (`FEAT_Method/Field/EventType/SafeCommunication/DataCorruption/DataReordering/DataRepetition/DataLoss/ZeroCopy/CommunicationASILLevel/ErrorHandling/FullyMockablePublicAPI/BindingAgnosticPublicAPI`) | `feature_requirements_ipc.trlc` read (full) | **Confirmed** |

`check-plan.json` conforms to the supplied Linux collector schema
(`{"checks":[{"kind","targets","reason","native_obligation","config"}]}`, `config = "linux_x64"`).
9 of its 10 rows actually executed and passed; the 10th (lint) executed and failed. No QNX target
appears. No check is weakened by the plan.

---

## 4. Disposition criteria applied

| Dimension | Assessment | Evidence |
| --- | --- | --- |
| Is this an implemented issue fix? | **No** — design/blocker assessment only | empty source diff; issue body "Not designed yet"; §1 |
| Is the design deliverable internally sound? | **Yes, as a draft** — alternatives A/B/C, prerequisites, proposed requirement derivation, open decisions | `scope.md`, `e2e-design-draft.md` |
| Is the patch behavior-changing? | **No**; no `score/mw/com/**` edit | identical subject hash across attempts |
| Correctness regression risk | **None introduced** (no code change); planned checks are guard rails for a future change | §2, §3 |
| Is verification green? | **No** — lint FAILED; overall `passed: false` | §2 |
| Engineering/safety acceptance | **Pending** — no human decision; tests/workflow success cannot supply it | §7 |

---

## 5. Gap register (as applicable)

**Correctness / API**
- The issue's target APIs (`Method<T>`, `Field<T>`) **do not exist**; the macro rejects them by
  design. E2E cannot attach to a non-existent surface. Hard prerequisite = #782.
- No accepted E2E design exists, so there is no "correct behavior" to implement or test against.

**FFI / wire / ABI**
- The Rust↔C++ bridge is Event-only (`EXPORT_MW_COM_EVENT`/`EXPORT_MW_COM_TYPE`); Method/Field
  FFI export paths are absent.
- For `Method<T>` the in-arg/return buffers are fixed-size and pre-computed by C++
  (`CreateDataTypeSizeInfoFromTypes<Args...>()`); an E2E header cannot be added on the Rust side
  alone — buffer sizing must change in **lockstep** on both sides. This is a hard, currently
  unresolved cross-language constraint.
- Rust E2E error classes are stated by the maintainer to be **restricted to what the unpublished
  C++ API provides**; no independent Rust taxonomy may be invented.

**Concurrency / state machine**
- Whether the provider-side "apply or reject the call based on E2E result" state machine
  (counter-delta tolerance, consecutive-failure counting) is in a first increment is **undecided**;
  so is CRC + `DataID`-only vs full state machine. Async method-call interaction is unaddressed.

**Traceability**
- The requirement mapping is a **proposed** derivation (safe communication, data-loss/corruption/
  reordering/repetition), not an accepted native trace. The issue template checkbox for
  "Requirements / Architecture are not affected" is **unchecked**, i.e. no determination.
- **Minor trace defect to raise:** `check-plan.json`'s query `native_obligation` cites
  `FEAT_StablePublicApi`. That ID is **not defined** in the repository's feature-requirement file
  (`feature_requirements_ipc.trlc`), whose full contents I read. It is either an external/unresolved
  ID or a mis-cited anchor; the plan should cite only repo-resolvable IDs or mark it unknown. The
  companion `FEAT_SupportForMultipleProgrammingLanguages@1` **is** valid.

**Qualification / platform**
- Tool qualification for the selected Ferrocene Linux target is **not established** by this workflow
  (correctly stated, not overclaimed).
- No Method/Field E2E test target exists (correctly recorded as an explicit unknown, not fabricated).
  `score_com_concept-macros-tests` is `manual` and excluded from wildcards.
- Linux-only coverage; no QNX variant is run or claimed (correct for this task).

---

## 6. Missing / unavailable evidence (preserved)

- `native-check-summary.json` was **absent at scope time** and is now present (attempt 3). It is
  preserved, together with the attempt 0–2 outputs and `correction-1..3.md`.
- `.rust-queue/reports/open-decisions.json` and `.rust-queue/reports/evidence-status.json` could
  **not be opened by this reviewer** (file-tool boundary returned "Bound Rust workspace/file-tool
  boundary" on repeated attempts). Their content (OD-1…OD-8) is therefore known only **second-hand**
  via `implementation.md`, `review-packet.md` and the correction reports; I did not independently
  verify the decision records. This is a review-coverage gap, not a fabrication.
- Live GitHub/PR/queue state is **unknown**: network retrieval was blocked, and the workspace holds
  only the offline `.rust-queue/context/` snapshot (latest supplied comment `2026-09-11T14:36:07Z`).
- File hashes/byte sizes for the report manifest are **not computable** here (shell blocked); the
  reviewer could not add hashes. The harness's own subject/result hashes above remain authoritative.

---

## 7. Acceptance status

- **Technical completion (design-mode):** complete — binding, premise check, current-state and
  prerequisite analysis, architecture alternatives, proposed (not accepted) requirement trace, a
  schema-valid Linux check plan, open-decision export and review packet.
- **Engineering / safety acceptance:** **PENDING and unchanged.** The E2E design, wire/profile
  choices, header placement, error classes, staging (Event-first vs unified) and any
  requirement/safety impact remain for authorized humans and for the C++ E2E API. **Passing builds,
  tests, docs and workflow stages do not supply this decision**; the one failing lint row does not
  itself block design work, but it does mean the measured run is not green.
- **Status words:** none of the artifacts were marked qualified/released/accepted by this review, and
  none must be.

---

## 8. Supervisor decision

1. **Accept** the submitted packet as a **design/blocker assessment**; it correctly declines to
   implement an unaccepted E2E design and preserves prerequisites and failures.
2. **Reject any representation of this work as an implemented fix** for #1062.
3. **Keep the lint check FAILED** in the record; treat the cause as an operator-side
   duplicate-aspect invocation. Do **not** weaken, remove or re-label the check.
4. **Carry forward** the open decisions and the C++/Rust prerequisites; no counter reset.
5. **Fix the one trace defect** (`FEAT_StablePublicApi` in `check-plan.json`) when the plan is next
   revised.

## 9. Concrete next action

1. Operator: re-run the lint measurement with the pinned `clippy_strict` aspect supplied **exactly
   once** (single documented `--config=clippy` form); retain attempts 0–3 as history.
2. Obtain the C++ E2E protection/verification API and align Rust wire/`DataID`/error-class
   conventions to it (blocked externally).
3. Land the Rust `Method<T>`/`Field<T>` API (#782).
4. Accept the E2E design (header placement, per-mode profiles, counter/state-machine scope,
   requirement impact), then implement and run the planned checks — adding native
   corruption/reordering/repetition/loss regression cases for Event and, once available, Method/Field.
