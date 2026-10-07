# Supervisor review — communication #781 "Implementation of MethodInArgPtr in rust side"

Issue: `eclipse-score/communication` #781 (label `rust-api`, state `open`, 0 comments)
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `implementation` · Platform: Linux (`linux_x64`) only · No QNX · Model: DeepSeek Flash
Reviewer role: independent, read-only. This report is the only file written by this review.

**Disposition: NOT a completed/verified issue fix. Patch applied in the workspace with partial
measured verification and one unresolved non-source blocker. Engineering acceptance is
PENDING — an offline human decision that no test, workflow success or agent statement here
can supply.**

---

## 1. Reviewer authority and provenance of claims

| Capability | State in this review | Consequence |
| --- | --- | --- |
| Read sources / BUILD / CI / bazelrc, bounded | used | independent source inspection of scope, patch and root cause |
| `grep`/`glob`, file listing | used | located files only |
| Shell / `git` / `bazel` / hashing | blocked | **no** command run, **no** digest recomputed, subject hash not independently verified |
| Write | only `.rust-queue/reports/` | only this report created; no source, BUILD, CI or `.bazelrc` edited |

Evidence provenance used below is labelled explicitly:

- **REVIEWER-OBSERVED SOURCE** — read directly by this review from the workspace at the baseline.
- **COLLECTOR-SUPPLIED** — `.rust-queue/reports/native-check-summary.json` and the bounded tails
  in the task record. Not independently reproducible in this review because shell is blocked.
- **AGENT ASSERTION** — statements in `scope.md` / `implementation.md` / `correction-{1,2,3}.md`
  / `review-packet.md`. Accepted only where a reviewer-observed source corroborates them.

---

## 2. Independent review of scope

REVIEWER-OBSERVED SOURCE confirms the scope reading:

- `score/mw/com/impl/methods/method_signature_element_ptr.h` defines
  `template<typename Type> using MethodInArgPtr = MethodSignatureElementPtr<Type>` with private
  members, in order, `SignatureElement* element_ptr_; bool& ptr_active_; std::size_t queue_position_;`
  and a move-only contract (copy ctor, copy-assign and move-assign deleted; move ctor exists).
- No Rust definition of `MethodInArgPtr` exists at baseline under `plumbing/rust/*.rs`
  (`common.rs`, `sample_ptr.rs`, `sample_allocatee_ptr.rs`, plus the new file). The issue is
  net-new Rust API, so "feature/API" is the correct issue-type branch.
- Platform scope Linux only is consistent with the cited ABI reasoning (a C++ reference is
  ABI-equivalent to a pointer on the Itanium/x86-64 GCC ABI).

Scope verdict: **appropriate and narrow.** The issue sentence ("Create ABI type for
`MethodInArgPtr` in rust side with reference of C++ side … like how `SamplePtr` created") is
met by the *shape* of the change. The issue supplies no acceptance criteria beyond that sentence,
no requirement/design/safety IDs, and its template boxes are unchecked; per the workflow those
unchecked boxes do **not** establish that requirements/architecture are unaffected. Impact trace
remains **unknown**, not "none".

---

## 3. Independent review of the patch (source correctness)

REVIEWER-OBSERVED SOURCE. The applied change set is:

| # | Path | Reviewer confirmation |
| --- | --- | --- |
| 1 | `.../plumbing/rust/method_in_arg_ptr.rs` (new) | `#[repr(C)] pub struct MethodInArgPtr<T> { _element_ptr: *mut T, _ptr_active: *mut bool, _queue_position: usize }`, manual `Debug`, `#[cfg(test)]` size/align tests |
| 2 | `.../plumbing/rust/BUILD` | `rust_library method_in_arg_ptr_rs`, `rust_unit_test method_in_arg_ptr_test_rs`, `rust_doc_test method_in_arg_ptr_doc_test` present |
| 3 | `.../test_support/test_helper_size_provider.h` | two `GetMethodInArgPtr*Size()` accessors present |
| 4 | `.../test_support/test_helper_size_provider.cpp` | include + two `sizeof/alignof` bodies + two `extern "C"` wrappers present |
| 5 | `.../test_support/test_helper_size_ffi.rs` | two FFI decls + `MethodInArgPtrLola` provider present |
| 6 | `.../test_support/BUILD` | dep `//score/mw/com/impl/methods:method_signature_element_ptr` present |

Source-level correctness of the ABI mirror:

- **Layout arithmetic is correct.** C++ `{T*, bool&, size_t}` on Linux x86-64 = 24 B / align 8;
  the Rust mirror `{*mut T, *mut bool, usize}` is the same and independent of `T` (only a pointer
  to the element is stored). The two `sizeof`/`alignof` accessors measure the real C++ type, and
  the Rust test compares against them via `verify_size_and_align!` (`test_utils.rs`).
- **The test-support wiring is coherent.** `verify_size_and_align!` emits `"{name} size mismatch!"`
  / `"{name} align mismatch!"`, matching the `should_panic(expected = "size mismatch"/"align mismatch")`
  negative tests. `MethodInArgPtrLola::get_int32/get_user_defined_type` call the new FFI symbols.
- **Precedent followed.** `sample_ptr.rs` uses the same `#[repr(C)]` + private fields + `Debug` +
  `SizeInfo`-based test pattern; the new file mirrors it, not the SamplePtr *layout*.

Residual patch-level concerns (none is a proven defect; all unmeasured):

1. **Measured evidence covers size/align, not field offsets.** The issue text says "memory layout";
   the tests assert `size_of`/`align_of` only. With `#[repr(C)]` and identical member types the
   offsets are determined on this ABI, so the paraphrase is reasonable, but strictly the measured
   assertion does not cover offsets. This is the same limitation as the existing SamplePtr tests.
2. **Crate documentation is attached to a `use` item.** The intended crate doc comment (lines 14–23)
   is an outer `///` immediately preceding `use core::fmt::Debug;`, not a `//!` inner doc. Whether
   rustdoc renders it as crate-level documentation is unverified (the docs check did not execute
   rustdoc — see §5). Minor documentation/trace gap.
3. **Divergence from the SamplePtr analogy on `Send`.** `SamplePtr` carries
   `unsafe impl<T> Send` with a SAFETY rationale; the new type does not. Because the fields are raw
   pointers, `MethodInArgPtr<T>` is auto-`!Send`/`!Sync`. This is defensible (the C++ header does not
   establish thread-transfer semantics for the caller-owned `bool& ptr_active_`), but it is a real,
   unresolved contract decision rather than a settled choice.
4. **`target_compatible_with = no_tsan` is absent** on `method_in_arg_ptr_test_rs` while both
   sibling size tests carry it. The new test does not exercise the sample-ptr race (Ticket-246891),
   so this is likely benign, but it was not reasoned in the reports and no tsan configuration was
   measured. Minor qualification observation.

---

## 4. Issue-acceptance / trace mapping (reviewer disposition)

| Issue criterion | Native obligation | Artifact | Check | Evidence | Reviewer disposition |
| --- | --- | --- | --- | --- | --- |
| ABI type for `MethodInArgPtr` in Rust | Rust library/API build; layout/ABI vs C++ | `method_in_arg_ptr.rs` | build + size/align test | attempts 0–3: build exit 0; test `1 test passes` | **met in shape, verified for size/align only** |
| "with reference of C++ side" | bind to real C++ type | test-support `sizeof`/`alignof` | query + build | query exit 0, helper build exit 0 | met |
| "like how `SamplePtr` created" | convention parity | BUILD/test-support | build/test/docs/lint | lint obligation **unmet**; docs execution **unmeasured** | **partial** |
| Requirement/design/safety trace | native IDs | none | — | no IDs supplied; boxes unchecked | **unknown — not "none"** |

---

## 5. Independent review of the measured evidence

COLLECTOR-SUPPLIED. Latest recorded run is attempt **3** (`native-check-summary.json`),
`kind = measured_native_command`, `passed = false`, `exit_code = 1`,
`infrastructure_error = null`, `engineering_acceptance = "pending"`, subject hash
`29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45` (same value recorded for
attempts 0/1/2 in the task record — reviewer cannot recompute it; shell blocked).

| # | kind | target (BUILD-derived) | attempt-3 exit | Reviewer disposition |
| --- | --- | --- | --- | --- |
| 1 | query | `//score/mw/com/impl/methods:method_signature_element_ptr` | 0 | pass; target + visibility confirmed in `methods/BUILD` |
| 2 | build | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` | 0 | pass |
| 3 | build | `//.../rust/test_support:test_helper_size_provider` | 0 | pass |
| 4 | test | `//.../rust:method_in_arg_ptr_test_rs` | 0 | pass (`1 test passes`) |
| 5 | docs | `//.../rust:method_in_arg_ptr_doc_test` | 0 | **target built only** — tail shows `Build completed successfully` and the `.rustdoc_test.sh` artifact, no `PASSED`/`Executed`; doc-test execution not demonstrated |
| 6 | lint | `//.../rust:method_in_arg_ptr_rs` | 1 | **FAIL — analysis-time aspect duplication** (blocker, see §6) |

Unmeasured / missing obligations (preserved as pending, not passed and not failed):

- `//score/mw/com/impl/plumbing/rust:sample_ptr_test_rs` — **not present** in any recorded run.
- `//score/mw/com/impl/plumbing/rust:sample_allocatee_ptr_test_rs` — **not present** in any recorded run.
- `//score/mw/com/impl/methods:method_signature_element_ptr_test` — **not present** in any recorded run.
  These three matter because the shared `test_support` package (`BUILD`, `.h`, `.cpp`, `.rs`) was
  edited; the regression obligation is therefore unmeasured.

Evidence-bookkeeping gaps found by this review:

- `.rust-queue/reports/check-plan.json` still declares
  `evidence_state.native_check_summary = "absent"` and `executed_checks = 0`, which is **stale**:
  a summary now exists (attempts 0–3). The plan itself is unchanged, which is correct for pinning
  the subject, but its evidence_state paragraph no longer matches on-disk reality.
- `correction-3.md` is labelled "final (3 of 3)" and analyses attempt **2**, while the latest record
  on disk is attempt **3**. Attempt 3 shows the identical lint failure and the identical subject
  hash, so the conclusion is unchanged — but the latest attempt is not covered by any correction file.
- `_probe.txt` is a retained non-deliverable write-capability probe.

Overall measured status: **6 recorded / 5 pass / 1 fail / 3 unmeasured; run passed = false.**

---

## 6. Assessment of the lint blocker classification

REVIEWER-OBSERVED SOURCE corroborates the correction reports' root cause rather than accepting it:

- `quality/static_analysis/static_analysis.bazelrc` defines
  `build:clippy --config=_lint` and `build:clippy --aspects=@score_rust_policies//clippy:linters.bzl%clippy_strict`.
- `.bazelrc` imports `quality/static_analysis/static_analysis.bazelrc` once (line 188) and
  try-imports `.bazelrc.ai_checker` (line 200).
- `.github/workflows/_linter.yml` runs `aspect lint --bazel-flag=--config=ci --bazel-flag=--config=clippy`
  and documents verbatim that the aspect is "deliberately NOT also passed via `--aspect=` … since Bazel
  rejects the same aspect being registered twice".

The recorded failure — `aspect @@score_rust_policies+//clippy:linters.bzl%clippy_strict added more than
once` plus `configs expanded more than once: [_lint]` — is a command/analysis-level defect in how the
lint check was invoked. The subject-executing checks that ran all passed on a byte-identical subject
hash across four attempts. Therefore:

- the clippy aspect **never analysed the subject**, so **no clippy diagnostic exists** to correct;
- the failure is **not** caused by the changed Rust source, BUILD rules, C++ helper or test;
- editing product source to "fix" it would be untruthful and is correctly refused.

One caveat this review records: the classification rests on a **bounded tail**, not the full raw log;
the reviewer cannot see the exact collector command line, so "invocation duplication" is the best
supported explanation, not an independently reproduced one. The requested remedy (register the aspect
exactly once, mirroring `_linter.yml`) is sound and does not weaken the obligation. This is a **check
invocation correction outside agent authority**, and it is the single reason the run is not green.

---

## 7. Gap inventory (as applicable to this change)

- **Correctness / verification**: size + align are measured; **field offsets are not**. Docs target
  built but doc-test not executed. Three regression targets unmeasured.
- **FFI / memory-layout**: layout mirror is correct for Linux x86-64, but the C++ type is move-only
  and its destructor clears the caller-owned `bool& ptr_active_`. The Rust mirror has no `Drop`, no
  constructor and no ownership contract; **nothing wires `MethodInArgPtr` into the method FFI**
  (`com-api-ffi-lola` still covers events/samples only). The ownership/lifetime and destruction
  semantics across the boundary are **open**.
- **Concurrency**: no `Send`/`Sync` decision (fields make it auto-`!Send`/`!Sync`); the aliasing of the
  externally-owned `ptr_active_` flag has no stated synchronization contract. **Open / unknown.**
- **Trace / qualification**: no requirement, design or safety IDs supplied; the unchecked template
  boxes are not evidence of "unaffected". The lint obligation (`clippy_strict`) is **unmet**, so the
  Rust-lint qualification for the new crate is unmeasured. Ferrocene tool qualification for this
  version/target/use is not established by the issue.
- **Scope**: `MethodReturnTypePtr` (same underlying C++ type) is out of scope of #781; placement in
  `plumbing/rust` vs a new `methods/rust` package remains a proposal needing maintainer confirmation.

---

## 8. Disposition

1. The scope is correct and the applied patch is a faithful, precedent-consistent implementation of
   the requested ABI *type*, verified against the real C++ type for size and alignment.
2. **The issue is not demonstrated as resolved.** The run's overall result is `passed = false`
   because the mandatory `clippy_strict` lint obligation never ran on the subject (invocation-level
   aspect duplication), and three regression tests from the plan were never measured.
3. The lint failure is preserved as **failed** evidence; the three regression rows remain **pending**;
   no check was weakened, retargeted or dropped, and no passing evidence was fabricated.
4. This is **not** an implemented-and-verified fix, and the correction files' "blocker" framing is
   the accurate one. Passing the tests that did run does not establish acceptance.
5. **Engineering acceptance: PENDING offline human decision.** This report neither qualifies,
   releases, accepts nor closes anything.

---

## 9. Preserved evidence and manifest

- Preserved unchanged: `scope.md`, `implementation.md`, `check-plan.json`, `review-packet.md`,
  `native-check-summary.json` (attempt 3, lint failed), `correction-1.md`, `correction-2.md`,
  `correction-3.md`, `_probe.txt`.
- Added by this review: `supervisor.md` (this file) only.
- No source, BUILD, CI, `.bazelrc`, license/SPDX header, toolchain/dependency pin or lint policy was
  modified by this review.
- SHA-256 manifest: **not computable in this review** (shell/hashing blocked). Authoritative hashes
  remain the collector-supplied values, e.g. subject
  `29300017566798a8aa4ba3f8a09876982a83a174df2898bdedfca23a09c73d45` and
  `native_result` attempt-3 sha256 `2dc1f405e14b424ca6b65e51369d421609ce2e41838fdeb71b5350f45a3b568b`.
- No credentials are embedded.

---

## 10. Concrete next action

1. Deterministic collector: re-issue the `lint` check so the
   `@score_rust_policies//clippy:linters.bzl%clippy_strict` aspect is registered exactly once
   (mirroring `.github/workflows/_linter.yml`), without a second `--aspects=` and without reading
   `static_analysis.bazelrc` twice.
2. Restore the three unmeasured regression targets
   (`sample_ptr_test_rs`, `sample_allocatee_ptr_test_rs`, `method_signature_element_ptr_test`) to the
   recorded run, and run the `method_in_arg_ptr_doc_test` as a **test**, not merely a build.
3. Re-measure the unchanged subject hash and update `native-check-summary.json`; refresh the stale
   `check-plan.json` `evidence_state`.
4. Submit the open decisions — FFI ownership/destruction of the move-only type, `Send` contract,
   placement, `MethodReturnTypePtr`, and the requirement/design/safety trace — for an authorized
   offline human decision. Until then, engineering acceptance stays **pending**.
