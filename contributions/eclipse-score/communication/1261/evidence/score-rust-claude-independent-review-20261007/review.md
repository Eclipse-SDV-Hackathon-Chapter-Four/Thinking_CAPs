# Independent offline review: Rust queue status and #1261 recovery scope

**Reviewer:** Claude (Opus 5.5), outside Fabro, read-only. **Date:** 2026-10-07.
**Classification:** agent technical recommendation. This is not an authenticated human
engineering decision, issue closure, or execution authority. No source edits, builds,
test reruns, native runs, paid dispatches, commits or publication occurred.

Native baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (unchanged).
Issue snapshots describe their retrieval date, not today's GitHub state.

## 1. What I verified before relying on evidence

- Handoff files `011-session-20261007-rust-queue-bounded-results{.md,.json,-prompt.md}`,
  `011-session-20261007-rust-recovery-review.md` and the Claude handover prompt match
  their `-binding.json` SHA-256 values.
- Every payload of ten packets was rehashed against its manifest, and each manifest digest
  matched the handoff (or, for the two ledger-only packets, was recorded fresh here):
  1261 final (152), final-review supplement (6), recovery review (4), 1261 attempt 2 (149),
  250 final (176), 560 Codex (107), 173 refresh (352), original queue (1,543),
  250 discovery `575c85n6` (143) and 560 integration `5sejq8fk` (164). Zero mismatches.
- Correction counters reconcile across sealed ledgers. The original queue packet records
  1 correction each for 250, 560 and 1261. Later ledgers record:
  250: 2 (`575c85n6`), then 3 (`fcuqf3or`). 1261: 2 (`u96hjh42`), then 3 (`hdmk9onj`).
  560: 3 (`5sejq8fk`), plus a separate Codex allowance at 1/3 (`eppa905r`). 173: 2. The sum is
  **35/36**, matching the handoff. **No inconsistency was found.**
- The SSD Linux image `/media/jefferson/11c42dee-…` was mounted as `ext4` rw (loop).
  I read only from it: two baseline blobs via `git show` from an existing workspace, with hooks
  and fsmonitor disabled. Nothing was written there.

Results already in the packets (exact child-case and warning counts for 250/560/173) are
**carried evidence**. Their packets were rehashed in full and their verification summaries
report `passed: true`. The tests were not rerun.

## 2. Status of all 13 issues

| Issue | Topic (snapshot title) | Corrections | Measured state | Disposition |
| --- | --- | --- | --- | --- |
| 1261 | Async stream of newly available services | **3/3 STOP** | Final candidate: GCC error `runtime.cpp:355`; 0/5 tests executed; 3 of 4 groups unexecuted; 0 SARIF; new integration unselected | Failed/incomplete. See §3 |
| 250 | `FindServiceSpecifier::Any` support | **3/3 STOP** | Carried: 6 selected Linux groups passed, 68 child cases, 2 ignored doctests, 4 warnings in 5 library Clippy reports | Partial: configured universe, API/ABI, callback reclamation, trace, qualification open |
| 560 | Subscription state change APIs | 3/3 original, Codex extra **1/3 (2 left, 560-only)** | Carried: 5 groups passed, 14 cases, 2 Clippy warnings; test-code Clippy not measured | Applicability, trace, qualification and acceptance open |
| 173 | External crates in COM-API | 2/3 (sole remaining original slot) | Carried: 39 child cases passed, 2 ignored; published macro source byte-identical | Qualification/adoption decisions open; no defect justifies spending the slot |
| 1265 | `paste` crate usage | 0/0 | Reuse mode; historical contribution pushed under earlier specific authority | No new authority; acceptance pending |
| 1264 | `thiserror` crate usage | 3/3 | Selected tests PASSED; all 3 lint groups exit 1 with the duplicate `clippy_strict` aspect (launcher defect, `operator-findings.md`) | Assessment only (0-byte patch); lint evidence **missing**, not failed by source |
| 1263 | `futures` crate usage | 3/3 | Tests PASSED; 4/4 lint groups failed with the same launcher defect; **no supervisor report** | Assessment only; supervisor review and lint evidence missing |
| 794 | Remove `tags=["manual"]` from Rust tests | 3/3 | Tests PASSED; 4/4 lint groups failed with the launcher defect | **No patch produced** (0 bytes), so the requested change is not implemented |
| 781 | `MethodInArgPtr` on Rust side | 3/3 | Tests PASSED; 4/4 lint groups failed with the launcher defect | Draft patch (10,505 B); ABI/ownership unresolved |
| 782 | Runtime for Rust Method APIs | 3/3 | Tests PASSED; 4/4 lint groups failed with the launcher defect | No patch; assessment only |
| 1062 | E2E protection for Method/Field APIs | 3/3 | Design mode; tests PASSED; 4/4 lint groups failed with the launcher defect | Design assessment only |
| 741 | Move Sample example to tutorial | 3/3 | All 4 query groups exit 7: `no such package 'score/mw/com/doc/tutorial/com-api-example/com-api-gen'` | 852-byte comment-only boundary probe; relocation not done (file tool lacks rename/delete) |
| 490 | Mock Runtime for COM-API | 3/3 | 2 lint groups failed with the launcher defect; test group exit 2 from a Bazel `rules_python` pip module-extension loading error, not an assertion; **no supervisor report** | Draft mock (29,530 B) unverified |

For the nine original-queue issues, the per-check classification comes from
`verification-audit.json` and the check logs. The lint-failure-to-duplicate-aspect match is
one to one: 3/3 for 1264, 2/2 for 490 and 4/4 for the rest. **Lint cleanliness is therefore
unknown for those issues, not refuted.** Fixing the launcher is a fabric/operator change. It
does not reset any exhausted budget.

## 3. #1261 independent assessment

### 3.1 Measured blockers (confirmed from sealed evidence)

| ID | Blocker | My verification |
| --- | --- | --- |
| M1 | `runtime.cpp:355:1: error: expected unqualified-id before '{' token` | `check-0.log:859` exact. `runtime.cpp` 291–354 is the new function, and 355–370 is the orphaned merge body. In the exported patch, `-Result<void> Runtime::MergeAdditionalConfiguration(const Configuration& additional_configuration) noexcept` was replaced by `+std::vector<InstanceIdentifier> Runtime::GetConfiguredServiceWildcardIdentifiers()`, which is a diff-splice error. `runtime.h:162` still declares the method. |
| M2 | Dedicated integration unselected | `driver.py:29` reads only `W/.rust-queue/reports/regression-plan.json`. The candidate wrote `score/mw/com/test/basic_rust_api/regression-plan.json`. |
| M3 | Required implementation report absent | Notes exist only at `all_services_stream/implementation.md` in the source tree. |
| M4 | Verification mostly unexecuted | Bazel: "Executed 0 out of 5 tests: 1 fails to build and 4 were skipped" (`check-0.log:873`). Three groups did not run, and there are 0 SARIF reports. Analyzer cleanliness, compatibility and doctests are **unknown**. |

M1 masks every later compile diagnostic. A one-line fix does not show that the rest compiles.

### 3.2 Static concerns (source reading only; not executed)

Agreed with the prior review, rechecked against source:

- **S1 Unbounded queue.** `apply_snapshot` pushes one item per zero→one refcount transition.
  A flapping provider with no polling grows `VecDeque` without limit. The module doc
  (`service_stream.rs:28–29`) says allocations are "bounded by … currently offered
  instances". **The code does not do that, so the doc is inaccurate.**
- **S2 Order-dependent unit assertion.** Lines 327–328 assert `first[0]` is instance 1 and
  `first[1]` is instance 2. Order comes from `HashSet::difference` with `RandomState`, so the
  test will flake. It is a defect even though it never executed.
- **S3 Weak integration.** The consumer accepts `big >= 2 && mixed >= 1 && provider_instance_count >= 2`
  (`consumer_app.rs:80`) and uses sleep-phased provider holds. Its `std::process::exit`
  (lines 121/135/138) bypasses stream `Drop`. It cannot discriminate duplicates, a withdrawal
  boundary or initial versus later offers.
- **S4 Configured-only universe.** `i_runtime.h:50–52` documents this as deliberate. That is
  honest, but it conflicts with criterion 1 ("system-wide").
- **S5 Rust app imports/type inference** (`Builder`, `OfferedProducer`, `LolaRuntimeBuilderImpl`).
  These are unmeasured hypotheses and must not be reported as compiler errors.

New observations and corrections to the prior review:

- **N1 Callback retention is inherited from the baseline, and the candidate amplifies it.**
  Baseline `registry_bridge_macro.h:189` (blob `f4c8a3dd`) defines the find-service
  `RustBoxedCallable::dispose(FatPtr) noexcept {}` as empty. Baseline `consumer.rs:950`
  (blob `3292d143`) uses the same `FindServiceCallable::new(transmute(Box<dyn FnMut>))`
  pattern. **Every existing interface-scoped `find_service` already leaks its callback box.**
  The candidate adds two things:
  - one leaked box per configured type per open;
  - each box holding a strong `Arc<StreamState>`, which keeps the whole queue and membership
    maps alive after `Drop`.

  Recovery-plan item 4 merges a candidate-local fix with a baseline-wide ownership change.
  They should be split; see R4 and D3.
- **N2 Mid-vtable insertion.** `GetConfiguredServiceWildcardIdentifiers` is inserted before the
  pure virtual `GetTracingRuntime`. That shifts every later `IRuntime` slot. Appending at the
  end narrows the break but does not remove it. The default body keeps mocks source-compatible.
- **N3 Configuration race and stale cache.** `GetConfiguredServiceWildcardIdentifiers` reads
  `configuration_` under `discovery_identifiers_mutex_`. The static `AddConfiguration` →
  `MergeAdditionalConfiguration` path mutates `configuration_` without that mutex. That is a
  data race unless the native contract limits `AddConfiguration` to initialization before any
  discovery. The cache is also never invalidated. This needs a native contract citation,
  not an assumption.
- **N4 Snapshot assumption.** Withdrawal and re-offer detection assume that every native
  find-service callback delivers the **complete** current handle set for its watch. That
  includes an **empty** container when the last instance withdraws. The unit tests feed
  synthetic snapshots, so they cannot prove this. Only a real LoLa integration phase or a
  native contract can.
- **N5 No runtime error items.** Only `Ok` descriptors are ever enqueued. Native discovery
  failures after start are not surfaced, and the stream never yields `None` before `Drop`.
  Criterion 3 requires these behaviors to be documented, or errors to be added.

Confirmed positive design points:

- `std::deque::push_back` keeps the deployment references behind the identifiers stable.
- Watches are stopped outside the membership lock.
- The find-service trampoline wraps the callback in `catch_unwind` (`bridge_ffi_lola.rs:126`).
- Watch ownership is published before the stream is returned.
- Partial-start rollback stops watches in reverse order.

### 3.3 Assessment of the existing recovery plan

- **Item 1 (restore signature): correct.** The exact baseline line is verified above. Its
  remark about Rust imports is properly labelled static.
- **Item 2 (plan/report paths): correct.** Report placement alone gives no test adequacy.
- **Item 3 (scope): correct.** It requires a human disposition.
- **Item 4: needs splitting** (N1). Do not make native callback reclamation a #1261-only
  prerequisite.
- **Item 5: correct.** Add N4 (empty-snapshot phase) and S2.
- **Item 6: correct.**
- **Missing from the plan:** N2, N3, N5, and the inaccurate boundedness claim in the module doc.

### 3.4 Smallest technically complete recovery scope

"Technically complete" here means every issue criterion has measured evidence under an
**accepted** scope disposition. Human acceptance still remains separate.

**Straightforward repairs.** These are local and need no architecture decision:

| ID | Change | Check that demonstrates it |
| --- | --- | --- |
| R1 | Reinsert `Result<void> Runtime::MergeAdditionalConfiguration(const Configuration& additional_configuration) noexcept` before the orphaned body (after line 354, separated by a blank line) | `//score/mw/com/impl:runtime_test` builds and passes |
| R2 | Emit `regression-plan.json` and the implementation report under `.rust-queue/reports/`. Delete the source-tree plan from the proposal. | The effective plan lists `//score/mw/com/test/basic_rust_api/all_services_stream/integration_test:test_com_api_all_services_stream` and `com-api-runtime-lola-tests` |
| R3 | Compare unordered sets in `apply_snapshot_deduplicates…`: collect `instance_id()`s, sort, compare to `[1, 2]`, and assert name/version/binding on every item | Unit target passes across repeated runs (for example `--runs_per_test`, if native policy allows) |
| R4 | The callback captures `Arc::downgrade(&state)` and no-ops when `upgrade()` fails. This leaves a constant-size leaked box per watch, matching baseline `find_service`, instead of retaining the queue. | Mock test: after the stream is dropped, a callback invocation does not panic or enqueue. Count `Arc::strong_count` before and after. |
| R6 | Correct the module and API docs: honest retention statement (constant per watch per open, inherited dispose gap), configured-only universe, no runtime error items, infinite stream ending only on `Drop` | Doc review; doctest group |
| R7 | Integration rewrite: explicit phases (initially empty, initial offer, later offer, withdrawal including an empty snapshot, re-offer), exact full-identity sets, duplicate-free assertions, normal stream drop instead of `process::exit` | The dedicated integration passes. Seed a duplicate or skip the re-offer to show the test fails. |

**Decision-dependent work.** These need an engineering or architecture decision before
implementation, and authorized humans own them, offline:

| ID | Decision | Options (agent recommendation in bold) |
| --- | --- | --- |
| D1 | Discovery universe vs. "system-wide" | (a) **Accept configured-LoLa scope as a documented narrowing, with an issue-text amendment or follow-up**; (b) native capability for unconfigured types, whose existence is unknown and must be shown from native sources |
| D2 | Buffering and error contract (R5) | (a) **Level-triggered coalescing**: at most one pending item per currently offered identity, removed on withdrawal. The bound is the offered set, so no capacity is invented. Unpolled flaps collapse. (b) Edge history with a capacity and an explicit overflow error item, which needs a human-set capacity. (c) Keep it unbounded: reject. Also decide whether runtime discovery failures surface as `Err` items (N5). |
| D3 | Native find-service callback reclamation | A baseline-wide ownership change in `com-api-ffi-lola`: a non-empty `dispose` plus a proof that native `StopFindService` gives callback quiescence. It affects existing `find_service`. Track it separately from #1261. |
| D4 | `IRuntime`/`FFIBridge` ABI and source compatibility | **Append the virtual at the vtable end** and record an ABI-break disposition, or move enumeration out of `IRuntime` |
| D5 | `AddConfiguration` versus discovery concurrency, and cache invalidation (N3) | Cite the native init-phase contract, or guard `configuration_` consistently and invalidate on merge |
| D6 | Running-phase allocation policy | The callback allocates `HashSet`/`HashMap`/`Vec`. The native policy must be identified. Do not invent one. |

With the recommended options for D1, D2 and D4, the technically complete scope is
**R1–R7 (R5 = coalescing), the D4 append, and D5 resolved by citation or guard.** D3 is
documented and handed off rather than solved inside #1261. Each change has to be measured
once against a bound source vector:

1. runtime/configuration/com-api-runtime-lola unit tests;
2. existing sync/async and C++ FindAny compatibility integration;
3. the dedicated stream integration;
4. the GCC15 macro doctest;
5. five-library Clippy, which needs the duplicate-aspect launcher defect absent from this
   launcher path; this candidate's lint never ran, so that is unverified;
6. QNX and native trace/qualification remain explicit gaps.

The historical 94 passing cases from attempt 2 are **not** evidence for this backend.

### 3.5 Authority required

R1–R7 are all source corrections to #1261, which is at **3/3, STOP**. Even R1 and R2 need a
new run of a changed subject. Executing any of them requires explicit new user authority
that names:

- a new #1261 allowance;
- the editor (the DeepSeek Flash native agent, or a separately authorized Claude/Codex editor;
  Claude has no source-edit authority from this handover);
- the run budget.

The #560 Codex extra allowance (2 left) cannot be transferred. #173's original slot is not
justified by any defect. D1–D6 are human engineering decisions, made offline.

## 4. Unresolved obligations (all issues)

- Human engineering acceptance, native requirement/design/safety trace and qualification
  for all 13 issues. None is closed.
- Lint evidence for 1264, 1263, 794, 781, 782, 1062 and 490 is missing because of the
  duplicate-aspect launcher defect. It needs an operator fix before any future measurement.
- 1263 and 490 lack supervisor reports. 794 and 782 produced no patch. 741 is not
  implemented, because the file tool has no rename/delete. 490's mock is unverified because
  of a dependency-loading failure.
- 1261: everything in §3. 250: configured universe, callback reclamation (shares D3), API/ABI,
  trace and qualification. 560: applicability, trace and test-code Clippy. 173:
  tool-qualification, dependency closure, advisories and adoption decisions.
