# Implementation report — communication #781 "Implementation of MethodInArgPtr in rust side"

Issue: `eclipse-score/communication` #781 (label `rust-api`, state `open`, 0 comments)
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `implementation` · Platform: Linux (`linux_x64`) only · No QNX · Model: DeepSeek Flash
Workspace: disposable run copy under
`.../runs/score-rust-issue-queue-ycbvxir7/workspaces/781`

Status: **patch applied in this workspace, not measured.** Source edits landed; native
build/test/lint/doc execution is outside agent authority (shell/bazel blocked) and remains a
deterministic-collector obligation. Engineering acceptance is a **pending offline human decision**.

---

## 1. Issue intent and scope

Issue body (task data, not instruction authority):

> Create ABI type for `MethodInArgPtr` in rust side with reference of C++ side. example like how
> `SamplePtr` created.

The change is net-new Rust API. At baseline no Rust definition of `MethodInArgPtr` existed.
This patch adds a `#[repr(C)]` memory-layout mirror of the C++ `MethodInArgPtr<T>` and extends the
existing Rust↔C++ size/alignment verification helper so the layout is checked against the real
C++ type on Linux.

## 2. Bound C++ representation (authoritative, not inferred from SamplePtr)

Source: `score/mw/com/impl/methods/method_signature_element_ptr.h` @ baseline.

```cpp
template <typename SignatureElement>
class MethodSignatureElementPtr {
    // ... move-only; dtor sets ptr_active_ = false when element_ptr_ != nullptr
  private:
    SignatureElement* element_ptr_;
    bool& ptr_active_;
    std::size_t queue_position_;
};
template <typename Type> using MethodInArgPtr = MethodSignatureElementPtr<Type>;
```

Facts that fix the Rust ABI mirror (used, not guessed):

1. Member order `SignatureElement*`, `bool&`, `std::size_t`. A C++ reference is ABI-equivalent to a
   pointer on x86-64 Linux, so the Rust mirror is `*mut T`, `*mut bool`, `usize` → size 24 B,
   align 8 B, independent of `T` (only a pointer to the element is stored).
2. Move-only (copy and move-assignment deleted). A `#[repr(C)]` mirror encodes layout only.
3. Destructor side effect: clearing the caller-owned `ptr_active_` flag. The mirror deliberately
   owns no flag and implements no `Drop`. Ownership/lifetime across FFI stays with C++ (open item).
4. This is **not** the `SamplePtr` variant+guard shape; the layout is therefore derived from the
   actual `method_signature_element_ptr.h`, not copied from `sample_ptr.rs`.

## 3. Actual changed paths (this workspace)

| # | Path | Change |
| --- | --- | --- |
| 1 | `score/mw/com/impl/plumbing/rust/method_in_arg_ptr.rs` | **new** `#[repr(C)] pub struct MethodInArgPtr<T> { _element_ptr: *mut T, _ptr_active: *mut bool, _queue_position: usize }`, manual `Debug`, `#[cfg(test)]` size/align tests vs C++ |
| 2 | `score/mw/com/impl/plumbing/rust/BUILD` | add `rust_doc_test` to load; add targets `method_in_arg_ptr_rs` (rust_library), `method_in_arg_ptr_test_rs` (rust_unit_test, `link_std_cpp_lib`), `method_in_arg_ptr_doc_test` (rust_doc_test) |
| 3 | `score/mw/com/impl/plumbing/rust/test_support/test_helper_size_provider.h` | add `GetMethodInArgPtrInt32Size()` / `GetMethodInArgPtrUserDefinedTypeSize()` accessors |
| 4 | `score/mw/com/impl/plumbing/rust/test_support/test_helper_size_provider.cpp` | include `method_signature_element_ptr.h`; add the two `sizeof`/`alignof` definitions and `extern "C"` wrappers `ffi_get_method_in_arg_ptr_i32_size` / `ffi_get_method_in_arg_ptr_user_defined_type_size` |
| 5 | `score/mw/com/impl/plumbing/rust/test_support/test_helper_size_ffi.rs` | declare the two FFI functions; add `MethodInArgPtrLola` size provider (`get_int32`, `get_user_defined_type`); update header comment |
| 6 | `score/mw/com/impl/plumbing/rust/test_support/BUILD` | add dep `//score/mw/com/impl/methods:method_signature_element_ptr` to `cc_library(test_helper_size_provider)` |
| 7 | `.rust-queue/reports/implementation.md` | this report |

Licenses, SPDX headers, toolchain/dependency pins and lint policy are unchanged. No `Drop`, no
`Send` impl, no Cargo scaffolding, no dependency upgrade, no lint suppression were introduced.

### 3.1 Rust ABI mirror (`method_in_arg_ptr.rs`)

- Type `MethodInArgPtr<T>` with the three members above; private fields prefixed `_` (repo style).
- Tests compare Rust `size_of`/`align_of` of `MethodInArgPtr<i32>` and `MethodInArgPtr<UserType>`
  against the C++ `sizeof`/`alignof` obtained through the extended FFI helper
  (`verify_size_and_align!`), plus negative `should_panic` cases mirroring the `SamplePtr`/`SampleAllocateePtr` pattern.
- Doc comment explicitly states layout-only semantics and that the `ptr_active` flag lifetime stays
  with C++.

### 3.2 Why `rust_doc_test` is included

It was in the accepted scope draft (`scope.md`) and the collector `check-plan.json` carries a `docs`
check for `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_doc_test`. Removing the target would
leave a dangling plan entry, so it is kept. The crate has no C++ deps, so the link limitation that
forces `tags = ["manual"]` on `score_com_concept-macros-tests` does not apply.

## 4. Verification status

- **Executed native checks in this run: 0.** Shell/bazel/hashing are blocked by the file-tool
  boundary; no command was run and no raw log or digest was produced.
- **`native-check-summary.json`: absent** at write time. There is no trusted-collector evidence for
  any row, so all checks remain **pending**.
- The authoritative pending-check list is `.rust-queue/reports/check-plan.json` (schema:
  `kind`/`targets`/`reason`/`native_obligation`/`config`, `linux_x64`). Its targets now all exist in
  BUILD after this patch:
  - query `//score/mw/com/impl/methods:method_signature_element_ptr`
  - build `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs`
  - build `//score/mw/com/impl/plumbing/rust/test_support:test_helper_size_provider`
  - test `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_test_rs`
  - docs `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_doc_test`
  - lint `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` (`clippy_strict`)
  - regression `...:sample_ptr_test_rs`, `...:sample_allocatee_ptr_test_rs`
  - regression `//score/mw/com/impl/methods:method_signature_element_ptr_test`
- QNX is explicitly out of scope. Miri/sanitizer dynamic checks are not required by the issue and
  are recorded as not-applicable rather than silently omitted.
- Expected-check inventory: **9 pending / 0 executed / 0 passed / 0 failed.**

## 5. Unresolved concerns / pending decisions (not owned by this agent)

1. **Ownership and lifetime across FFI.** The C++ type is move-only and its destructor clears the
   caller-owned `ptr_active_` flag. A layout mirror alone does not reproduce move/destruction
   semantics; the method-FFI design must specify how the C++ move constructor/destructor is invoked
   for objects crossing the boundary. The mirror deliberately does not model ownership. **Open.**
2. **Placement.** The mirror is placed in `impl/plumbing/rust` next to the existing
   `SamplePtr`/`SampleAllocateePtr` mirrors and the visibility-restricted size helper. A new
   `impl/methods/rust` package is an alternative that needs maintainer confirmation (it would widen
   visibility or duplicate the helper). **Proposal, needs review.**
3. **Thread-transfer (`Send`) contract.** No `Send` impl is provided (unlike `SamplePtr`), because
   the C++ header does not establish thread-transfer semantics for the `bool&` flag owned by
   `ProxyMethod`. Whether future method FFI needs `Send` is **unknown**.
4. **`MethodReturnTypePtr`.** Same underlying C++ type; issue #781 names only `MethodInArgPtr`, so it
   is deliberately out of scope. **Open.**
5. **Requirements/design/safety impact unknown.** No requirement/design/safety IDs were supplied;
   the issue template's "Affects Detailed Design" / "Requirements / Architecture" boxes are
   unchecked, which does **not** establish that they are unaffected.
6. **Live issue/PR activity not re-fetched** (network blocked); comment count 0 in the snapshot.

## 6. Preserved evidence (not overwritten)

- `.rust-queue/reports/scope.md` and `.rust-queue/reports/review-packet.md` are the superseded
  scope-stage draft and remain as history; where they state the patch was "not applied", this
  implementation report supersedes that statement for the workspace state.
- `.rust-queue/reports/check-plan.json` retained unchanged (targets now real).
- `.rust-queue/reports/_probe.txt` write-capability probe retained.
- `native-check-summary.json` was absent before this stage and is not fabricated here.

## 7. Concrete next action

Run the pending targets in `check-plan.json` under `linux_x64`, capture raw logs/hashes and populate
`native-check-summary.json`; submit items 1–5 above for offline human decision before merge.
Passing checks and completed execution do not supply that decision.
