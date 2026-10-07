# Supervisor review — Issue #782: Runtime implementation for Rust Method APIs

Independent, read-only review of the scope, patch and measured evidence produced for
`eclipse-score/communication` #782. This report is the only artifact written by the
supervisor stage; no source, test, BUILD, MODULE, license, pin or lint/CI policy was
edited, and no check was run or re-run by this stage.

- **Issue / repository**: #782 "Improvement: Runtime implementation for Rust Method APIs"
  (`open`, label `rust-api`). Context: `.rust-queue/context/{issue,task,comments}.json`.
- **Baseline**: `381d43dec900ab6a9076f3f30e7bfbdee019e26e` (`.rust-queue/context/task.json`).
- **Mode**: `implementation`, `max_source_corrections = 3`, Linux-only checkpoints.
- **Authority**: DeepSeek Flash only; Linux only; no QNX; file tools only. Shell, network/web,
  content search, delegation, publishing and acceptance tools were blocked in this stage.
  Command stages and raw collector evidence remain outside agent authority.
- **Reviewed artifacts**: `scope.md`, `implementation.md`, `check-plan.json`,
  `review-packet.md`, `correction-1.md`, `correction-2.md`, `correction-3.md`,
  `native-check-summary.json`, and bounded reads of the baseline source.

## 1. Verdict

| Dimension | Supervisor finding |
|---|---|
| Scope binding | **Sound.** Issue, baseline, authority limits and milestone exclusions are stated consistently with the context files. |
| Patch | **None, and correctly so.** No native file changed. The measured subject hash is identical across all four check attempts. |
| Measured evidence | **Preserved and internally consistent.** 18/19 checks exit 0 on every attempt; the single failure (check 19, lint) is a Bazel command/config-layer defect, not a source/test defect. |
| Premise vs. baseline | **Confirmed mismatch.** The Rust Method API surface does not exist at `381d43d`; implementing it would require inventing the open #818/#777 contract. |
| Implementation delivered? | **No.** This is a design/blocker assessment. It is **not** an implemented issue fix, and must not be reported as one. |
| Engineering acceptance | **Pending / none claimed.** Correctly held open for offline human decision. |

## 2. Independent verification of the packet's source claims

I re-derived the decisive baseline claims with bounded reads and filename globs; all held.

| Claim (from `scope.md`/`implementation.md`) | Independent observation | Verdict |
|---|---|---|
| No `method.rs` / `LolaMethodCaller` / `LolaMethodHandler` in the LoLa runtime crate | `glob score/mw/com/impl/rust/com-api/com-api-runtime-lola/**/*.rs` → only `consumer.rs`, `lib.rs`, `producer.rs`, `runtime.rs` | Confirmed |
| `lib.rs` exposes only Event modules | `com-api-runtime-lola/lib.rs:28-34` — `mod consumer; mod producer; mod runtime;`, Event-side re-exports only | Confirmed |
| `interface!` still rejects `Method<T>` | `score_com_concept/interface_macros.rs:110-115` — `compile_error!("Method definitions are not supported …")` | Confirmed |
| No Method error variant | `score_com_concept/error.rs:113-128` — Service/Producer/Consumer/Event/Allocate/Receive only | Confirmed |
| No Method re-exports | `score_com.rs:134-142` — no Method/Caller/Handler type | Confirmed |
| No Method FFI trait entries | `bridge_ffi.rs:86-…` — allocatee/sample/skeleton-event/proxy/service-discovery only | Confirmed |
| Callback trampolines are Event/FindService only | `bridge_ffi_lola.rs:32-128` — `mw_com_impl_call_dyn_fnmut`, `…_sample`, `…_find_service`, `…_delete_boxed_fnmut`, all `catch_unwind` + `std::process::abort` | Confirmed |
| No `.rs` under `score/mw/com/**` named `*method*` | `glob` for `score/mw/com/rust/**/*method*` and `score/mw/com/**/method*.rs` → no match | Confirmed |
| Check-plan labels are BUILD-derived | `com-api-runtime-lola/BUILD` has `com-api-runtime-lola`, `-tests`, `-doc-tests`; `com-api-ffi-lola/BUILD` has `bridge_ffi_rs`, `bridge_ffi_lola`, `registry_bridge_macro_cpp` (`cc_library`); `score_com_concept/BUILD` has the three concept targets (`-macros-tests` tagged `manual`) | Confirmed |
| Linux-only constraint honoured | `com-api-runtime-lola/BUILD:39-40,51` and `score_com_concept/BUILD:38-39` set `target_compatible_with = ["@platforms//os:linux"]`; no QNX target in the plan | Confirmed |
| Lint policy as described | `quality/static_analysis/static_analysis.bazelrc:15-18` (`build:_lint`), `:29` (`build:clippy --config=_lint`), `:30` (`--aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`) | Confirmed |

The contributor-reported `todo!()` `method.rs` is indeed absent from the baseline tree,
so the packet's conclusion that it belongs to the unmerged #818 branch is consistent with
the supplied snapshot. PR #777/#818 merge state and prerequisite #781 status remain
**unknown** offline (network blocked) and are correctly recorded as unknown, not resolved.

## 3. Patch review

**There is no patch.** The implementation report, all three corrections and the review
packet state that zero native files were modified, and the measured evidence corroborates
this: `measured_subject_hashes_sha256` is
`3626732016f0c96f8b5c23d3406ab1b2571fce2f09ddbc6f5e4cb36b56f03996` for every attempt
(0–3). An unchanged subject hash across all attempts is direct evidence that the intermediate
"fix" stages introduced no source change.

This is the correct disposition for a premise mismatch: the issue asks to implement a
contract whose design (#818) is still under review and not admitted to the baseline. Writing
Rust `Method` traits, an `interface!` arm, an FFI ABI or registry registration entries would
require inventing the API/ABI owned by the open design, which the workflow forbids. **The
no-patch outcome is therefore a blocker, not a completed fix.**

## 4. Measured evidence review

Source: `.rust-queue/reports/native-check-summary.json` (current snapshot = `attempt: 3`,
`native-result.json` = `…/jobs/782/execution/check-3/native-result.json`,
sha256 `79f02361c1f0c58aad2c64a40a7c3be74ac3e1dc0984f39bee2755f608cd2105`), plus the
attempt outputs supplied with the stage history.

| Attempt | native-result sha256 | Subject hash | Outcome |
|---|---|---|---|
| 0 | `854eb26d…d1033` | `3626…3996` | 18 pass / 1 fail (lint) |
| 1 | `e42c79f9…e2cf` | `3626…3996` | 18 pass / 1 fail (lint) |
| 2 | `afb60ee7…8dd0` | `3626…3996` | 18 pass / 1 fail (lint) |
| 3 | `79f02361…2105` | `3626…3996` | 18 pass / 1 fail (lint) |

- `infrastructure_error = null` and `engineering_acceptance = "pending"` on every attempt;
  the overall envelope is `passed = false`, `exit_code = 1`, driven solely by check 19.
- Checks 1–18 (query, 8 build, 7 test, 3 docs) exit 0. The test results include real
  execution (e.g. `test_com_api_sync` PASSED in ~26–30 s, `test_com_api_async` PASSED in
  ~24–30 s, `com-api-example-tokio-integration-test` PASSED in ~6 s). These are trusted
  collector evidence for the **Event** surface at the unchanged baseline.
- Check 19 (lint) exits 1 during Bazel **analysis**, with:
  `WARNING: … configs were expanded more than once: [_lint]` followed by
  `ERROR: aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than once`.
  There is **no clippy diagnostic** in the tail. This is a command/config-layer (harness)
  defect: the lint config chain (`clippy` → `--config=_lint` → the single `clippy_strict`
  aspect) is expanded more than once by the invocation. The repository defines the aspect
  exactly once (`static_analysis.bazelrc:30`), and the two lint targets are valid labels
  that built successfully as checks 2 and 6. **No repository file is implicated, and the
  packet correctly refuses to weaken the native lint policy to force a green result.**

Supervisor assessment of the evidence handling: **acceptable.** Failed results are retained
in sequence, attempts are not reset, the missing raw logs / collector summary for earlier
stages are preserved as missing (no fabricated hashes), and no passing evidence is reused
under a new label. `review-packet.md` and `scope.md` describe the plan as *proposed* checks,
not executed evidence — consistent with the actual state at the time they were written.

## 5. Consistency and quality observations

1. **Attempt-bookkeeping lag (minor, not fabrication).** The current
   `native-check-summary.json` is `attempt: 3`, but `correction-3.md` narrates
   `attempt 2` (there is no correction narrating attempt 3). Because the summary is a
   single overwritten snapshot from which attempt 0/1/2 figures cannot be re-derived, the
   earlier corrections' quoted attempt numbers rest on the stage inputs, not on a
   versioned archive in the workspace. All four attempts share an identical subject hash
   and identical check outcomes, so the lag does not change the disposition; it is a
   traceability caveat worth noting.
2. **Correction budget exhausted with no source correction.** This is defensible here
   because the failing check is not source-remediable within agent authority and the issue
   is independently gated on a missing design prerequisite. It does mean no further
   automated correction can be attempted in this run.
3. **Traceability IDs remain unknown by necessity.** No Method requirement/design artifact
   ID exists at the baseline; PR #777/#818 and prerequisite #781 are supplied only as issue
   prose/snapshot. The packet marks these unknown rather than inventing lookalike IDs —
   correct.
4. **Check-plan is appropriately conservative.** Every "reason" ties to a source-backed
   obligation, and every `native_obligation` that depends on the open design is explicitly
   marked unknown. Labels were independently re-verified against the actual BUILD files.
5. **`bridge_ffi_mock` is exercised indirectly** (runtime tests depend on it) but is not a
   standalone planned check; that is acceptable because the runtime test target pulls it in.

## 6. Correctness / FFI / concurrency / trace / qualification gaps

These are the gaps the packet identifies, restated with the supervisor's disposition. None
is resolved.

- **Correctness**: not assessable. No Method implementation exists; the only observable
  Method behavior at baseline is the deliberate `compile_error!` rejection and its
  `compile_fail` test. No positive Method path has ever compiled at this revision — **gap
  (blocked)**.
- **FFI**: no Rust Method `extern "C"` symbol, no `FFIBridge` method entry, and no C++
  method member-operation/registration macro exist at baseline. Representation/ABI,
  allocation ownership, callback reentrancy/`Send`, teardown/single-dispose, error mapping
  and the `catch_unwind`+abort unwind boundary for Methods are all undefined in Rust —
  **gap (blocked on design)**.
- **Concurrency**: sync-vs-real-async dispatch is undecided (issue #767 guidance to fix it
  in the C++ backend first). This choice changes the queue/ownership model and cannot be
  fixed at the Rust layer — **gap (open decision)**.
- **Trace**: the issue criterion → native obligation → artifact chain is broken at the
  design artifact, which does not exist at the baseline; prerequisite #781 is unconfirmed;
  PR #777/#818 status is not retrievable offline — **gap (unknown, correctly preserved)**.
- **Qualification**: nothing is qualified, released or accepted. "All checks green for the
  Event surface" cannot qualify a Method implementation that does not exist — **gap
  (human decision required)**.

## 7. Acceptance boundary

- **Technical status**: implementation **blocked / pending** at `381d43d`. The run delivers
  a source-bound assessment and a preserved, source-derived check plan. It does **not**
  implement #782.
- **Engineering acceptance**: **none claimed, pending offline human review.** Passing checks,
  a green collector run or workflow success cannot supply the required decision. No native
  work product is marked qualified/accepted/released.
- **Failed/missing evidence preserved**: the lint failure (check 19) is retained in all
  attempts; earlier missing collector summaries and unavailable file hashes are recorded as
  missing rather than fabricated.

## 8. Recommended next actions (outside this stage's authority)

1. **Harness/command owner**: assemble the lint invocation so the `clippy`/`_lint` config
   chain is expanded exactly once (do not combine duplicate `--config=_lint` /
   `--config=clippy` with an explicit `--aspects=…clippy_strict`), then re-run check 19.
   The other 18 checks already pass and must not be regressed. No repository change is the
   right remedy.
2. **Maintainer/design owner**: land or admit the #818 Method design (and the #777 design)
   at an authorized revision, and confirm prerequisite **#781** status.
3. **Then**: re-scope the implementation against that design — expected surfaces are the
   `score_com_concept` Method trait/type-state + `interface!` arm + error reason;
   `com-api-runtime-lola/method.rs`; `com-api-ffi-lola` FFI trait and `extern "C"` symbols
   with `catch_unwind`+abort trampolines; and the C++ registry method macro — and execute
   the preserved `check-plan.json` through the trusted Linux collector.
4. Resolve the sync-vs-async dispatch decision (issue #767) before finalizing ownership and
   queue semantics; keep E2E (#1062) and QNX (#1278) out of scope.

## 9. Supervisor conclusion

The packet is honest, source-faithful and internally consistent about what it did and did
not do. Its central claim — that the issue cannot be implemented at the selected baseline
because the Method design/contract is absent — is independently corroborated by the source
tree and by the fact that the measured subject hash never changed. The single measured
failure is a harness/command-config defect, correctly diagnosed and preserved rather than
papered over by weakening lint policy.

**Disposition: blocker/design assessment accepted as a faithful record — NOT an implemented
issue fix. Issue #782 remains open and unimplemented. Engineering acceptance remains
pending an offline human decision.**
