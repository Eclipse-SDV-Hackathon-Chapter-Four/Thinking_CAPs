# S-CORE Rust issue review packet — communication #781

Issue: "Improvement: Implementation of MethodInArgPtr in rust side"
Repository: `eclipse-score/communication` · Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `implementation` · Platform: Linux (`linux_x64`) only · No QNX.

> **Status of this packet:** technical draft only. No native command was executed in this run
> (shell/bazel are blocked), the source patch is **drafted but not applied** (write outside
> `.rust-queue/reports/` is blocked), and measured native evidence is **absent**. Engineering
> acceptance is a pending offline human decision.

## Scope and binding

- **Issue/repository, retrieval time, source and state:** `eclipse-score/communication` issue #781,
  state `open`, label `rust-api`, `created_at 2026-07-27T09:49:25Z`, `updated_at
  2026-07-27T09:49:38Z`, zero comments. Bound source commit `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
  (`task.json.baseline`, workspace HEAD `381d43d`). The context snapshot was supplied offline;
  live issue/PR/timeline re-fetch was **not possible** (network blocked), so current issue/PR
  activity could not be confirmed and is recorded as a gap.
- **User authority, permitted writes/executions:** file reads allowed (bounded ≤200 lines);
  content `grep` and shell/`git`/`bazel`/hashing blocked; writes permitted only under
  `.rust-queue/reports/`; no publishing/acceptance authority. Artifact destination:
  `.rust-queue/reports/`. No budget ceiling supplied.
- **Process/tailoring, requirements/design/safety/policy versions:** no requirement, design,
  safety or verification IDs were supplied with the task; the issue template leaves "Affects
  Detailed Design" and "Requirements / Architecture" unchecked, which does **not** establish that
  they are unaffected. S-CORE rust coding guideline `doc__rust_coding_guidelines` v1 status `valid`
  (source anchor in `score-rust-workflow/references/native-verification.md`); project applicability
  not established = unknown.
- **Source/lock/tool bindings (from inspected files, not re-resolved by command):** Bazel
  `.bazelversion` present; `MODULE.bazel` pins `rules_rust 0.68.2-score`,
  `score_toolchains_rust 0.10.0`, `score_rust_policies 0.0.5`, `score_crates 0.0.11`; `.bazelrc`
  selects `linux_x64` (default) → `linux_x64_gcc_15` with Ferrocene
  `ferrocene_x86_64_unknown_linux_gnu`; `quality/static_analysis/static_analysis.bazelrc` selects
  `clippy_strict` for `--config=clippy`. Tool *versions* are declared but were not executed/verified
  in this run.
- **Final patch / manifest:** not applied; no digest or source manifest is available because
  hashing tools are blocked. The exact proposed change set is below.
- **Technical completion vs acceptance:** technical draft only; engineering acceptance pending.

## Acceptance and engineering trace

| Issue criterion (verbatim intent) | Native obligation / artifact and revision | Changed artifact | Required check | Evidence / hash | Gap or proposed disposition |
| --- | --- | --- | --- | --- | --- |
| "Create ABI type for `MethodInArgPtr` in rust side" | `#[repr(C)]` layout mirror of C++ `MethodSignatureElementPtr<T>` (member order `element_ptr_`, `ptr_active_`, `queue_position_`), `score/mw/com/impl/methods/method_signature_element_ptr.h`@`381d43d` | new `score/mw/com/impl/plumbing/rust/method_in_arg_ptr.rs` | build + lint + size/align test | none (pending) | Patch drafted here; not applied/measured |
| "with reference of C++ side" | C++ target `//score/mw/com/impl/methods:method_signature_element_ptr` | test-support `cc_library` dep + `sizeof`/`alignof` accessors | query + build + test | none (pending) | Pending native execution |
| "example like how `SamplePtr` created" | Convention of `plumbing/rust/sample_ptr.rs`: `#[repr(C)]` mirror + C++ `SizeInfo` FFI size/align verification + `rust_library`/`rust_unit_test` | `score/mw/com/impl/plumbing/rust/BUILD`, `test_support/*` | build + test + docs + lint | none (pending) | Placement in `plumbing/rust` is a proposal (see open items) |

**Baseline reconciliation / impact notes**

- The requested Rust type does not exist at baseline. Enumeration of every `*.rs` in the workspace
  found no `MethodInArgPtr` definition; the Rust↔C++ FFI bridge (`com-api-ffi-lola`) covers
  events/samples only. So this is net-new API, not a behavior correction.
- Link direction: Rust consumes the C++ type's layout (Rust depends on C++), matching `SamplePtr`.
- The C++ type is **move-only** with a destructor side effect; the Rust mirror deliberately models
  *layout only* and does not claim ownership of the `ptr_active_` flag. This ownership/lifetime
  boundary is not resolved by the issue and is carried as an open obligation.
- Requirements/design/safety: no IDs supplied and unchecked template boxes provide no evidence;
  impact **unknown**, not asserted as none.

## Proposed implementation (drafted patch, exact)

### 1. New file `score/mw/com/impl/plumbing/rust/method_in_arg_ptr.rs`

```rust
/********************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

/// This crate gives the same memory layout as `MethodInArgPtr` in the C++ implementation.
///
/// The C++ type is defined in `score/mw/com/impl/methods/method_signature_element_ptr.h` as
/// `MethodInArgPtr<Type> = MethodSignatureElementPtr<Type>`.
///
/// It can be used for FFI bindings where `MethodInArgPtr` is needed. It does not provide any
/// functionality beyond memory layout compatibility: in particular the C++ type is move-only and
/// its destructor clears the referenced `ptr_active` flag. Lifetime management of that flag stays
/// with the C++ side and must be performed through the C++ operators, not by dropping this
/// layout-only Rust mirror.
use core::fmt::Debug;

/// Memory layout mirror of `score::mw::com::impl::MethodSignatureElementPtr<SignatureElement>`.
///
/// The C++ members, in declaration order, are:
/// `SignatureElement* element_ptr_; bool& ptr_active_; std::size_t queue_position_;`
/// A C++ reference is ABI-equivalent to a pointer, so `ptr_active_` is mirrored as `*mut bool`.
#[repr(C)]
pub struct MethodInArgPtr<T> {
    // `SignatureElement* element_ptr_`
    _element_ptr: *mut T,
    // `bool& ptr_active_`
    _ptr_active: *mut bool,
    // `std::size_t queue_position_`
    _queue_position: usize,
}

impl<T> Debug for MethodInArgPtr<T> {
    fn fmt(&self, f: &mut core::fmt::Formatter<'_>) -> core::fmt::Result {
        f.debug_struct("MethodInArgPtr").finish()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use test_helper_size_ffi_rs::MethodInArgPtrLola;
    use test_utils_rs::*;

    #[test]
    fn test_method_in_arg_ptr_int32_size() {
        let cpp_size = MethodInArgPtrLola::get_int32();
        verify_size_and_align!(MethodInArgPtr<i32>, cpp_size, "MethodInArgPtr<i32>");
    }

    #[test]
    fn test_method_in_arg_ptr_user_defined_type_size() {
        let cpp_size = MethodInArgPtrLola::get_user_defined_type();
        verify_size_and_align!(MethodInArgPtr<UserType>, cpp_size, "MethodInArgPtr<UserType>");
    }

    #[test]
    fn test_method_in_arg_ptr_layout_independent_of_element_type() {
        let int32_size = MethodInArgPtrLola::get_int32();
        let user_defined_type_size = MethodInArgPtrLola::get_user_defined_type();
        assert_eq!(int32_size.size, user_defined_type_size.size, "MethodInArgPtr size depends on element type!");
        assert_eq!(
            int32_size.align, user_defined_type_size.align,
            "MethodInArgPtr alignment depends on element type!"
        );
    }

    #[test]
    #[should_panic(expected = "size mismatch")]
    fn test_negative_method_in_arg_ptr_size_mismatch() {
        let cpp_size = MethodInArgPtrLola::get_int32();
        let incorrect = cpp_size.size + 1;
        assert_eq!(incorrect, cpp_size.size, "MethodInArgPtr size mismatch!");
    }

    #[test]
    #[should_panic(expected = "align mismatch")]
    fn test_negative_method_in_arg_ptr_align_mismatch() {
        let cpp_size = MethodInArgPtrLola::get_int32();
        let incorrect = cpp_size.align + 1;
        assert_eq!(incorrect, cpp_size.align, "MethodInArgPtr align mismatch!");
    }
}
```

Note: no explicit `Send` impl is drafted (unlike `SamplePtr`) — see open decision #2. No `Drop`
impl is drafted — see open decision #3.

### 2. Edit `score/mw/com/impl/plumbing/rust/BUILD`

- Change load:
  `load("@rules_rust//rust:defs.bzl", "rust_library")`
  → `load("@rules_rust//rust:defs.bzl", "rust_doc_test", "rust_library")`
- Append:

```starlark
rust_library(
    name = "method_in_arg_ptr_rs",
    srcs = ["method_in_arg_ptr.rs"],
    visibility = [
        "//score/mw/com:__subpackages__",
    ],
    deps = [],
)

rust_unit_test(
    name = "method_in_arg_ptr_test_rs",
    srcs = ["method_in_arg_ptr.rs"],
    features = ["link_std_cpp_lib"],
    deps = [
        "//score/mw/com/impl/plumbing/rust/test_support:test_helper_size_ffi_rs",
        "//score/mw/com/impl/plumbing/rust/test_support:test_utils_rs",
    ],
)

rust_doc_test(
    name = "method_in_arg_ptr_doc_test",
    crate = ":method_in_arg_ptr_rs",
)
```

### 3. Edit `score/mw/com/impl/plumbing/rust/test_support/test_helper_size_provider.h`

Add to `class TestSizeProvider` after `GetMockBindingSamplePtrSize()`:

```cpp
    /// Get size info for MethodInArgPtr<int32_t>
    static SizeInfo GetMethodInArgPtrInt32Size() noexcept;

    /// Get size info for MethodInArgPtr<UserType>
    static SizeInfo GetMethodInArgPtrUserDefinedTypeSize() noexcept;
```

### 4. Edit `score/mw/com/impl/plumbing/rust/test_support/test_helper_size_provider.cpp`

- Add include after `#include "score/mw/com/impl/plumbing/sample_ptr.h"`:

```cpp
#include "score/mw/com/impl/methods/method_signature_element_ptr.h"
```

- Add, in namespace `score::mw::com::impl`, after `GetMockBindingSamplePtrSize()`:

```cpp
SizeInfo TestSizeProvider::GetMethodInArgPtrInt32Size() noexcept
{
    return {sizeof(score::mw::com::impl::MethodInArgPtr<int32_t>),
            alignof(score::mw::com::impl::MethodInArgPtr<int32_t>)};
}

SizeInfo TestSizeProvider::GetMethodInArgPtrUserDefinedTypeSize() noexcept
{
    return {sizeof(score::mw::com::impl::MethodInArgPtr<UserType>),
            alignof(score::mw::com::impl::MethodInArgPtr<UserType>)};
}
```

- Add, in the `extern "C"` block, after `ffi_get_mock_binding_sample_ptr_size`:

```cpp
score::mw::com::impl::SizeInfo ffi_get_method_in_arg_ptr_i32_size() noexcept
{
    return score::mw::com::impl::TestSizeProvider::GetMethodInArgPtrInt32Size();
}

score::mw::com::impl::SizeInfo ffi_get_method_in_arg_ptr_user_defined_type_size() noexcept
{
    return score::mw::com::impl::TestSizeProvider::GetMethodInArgPtrUserDefinedTypeSize();
}
```

### 5. Edit `score/mw/com/impl/plumbing/rust/test_support/test_helper_size_ffi.rs`

- Update the file header comment mention to include `MethodInArgPtr`.
- Add inside `unsafe extern "C" { ... }` after the sample-ptr declarations:

```rust
    // FFI bindings for method_in_arg_ptr.rs struct types
    // Safety: These functions are safe to call as they are read-only accessors that return constant size information
    // with no side effects or undefined behavior risks.
    safe fn ffi_get_method_in_arg_ptr_i32_size() -> SizeInfo;
    safe fn ffi_get_method_in_arg_ptr_user_defined_type_size() -> SizeInfo;
```

- Append at end of file:

```rust
/// C++ size provider for MethodInArgPtr types
pub struct MethodInArgPtrLola;

impl MethodInArgPtrLola {
    pub fn get_int32() -> SizeInfo {
        ffi_get_method_in_arg_ptr_i32_size()
    }

    pub fn get_user_defined_type() -> SizeInfo {
        ffi_get_method_in_arg_ptr_user_defined_type_size()
    }
}
```

### 6. Edit `score/mw/com/impl/plumbing/rust/test_support/BUILD`

Add to `cc_library(name = "test_helper_size_provider", ... deps = [...])`:

```starlark
        "//score/mw/com/impl/methods:method_signature_element_ptr",
```

(License headers, SPDX identifiers and existing license/pin policy are preserved; no dependency
pin, toolchain pin or lint policy is changed.)

## Verification and expected checks

No check has been executed in this run. The deterministic stage obligations (targets and reasons,
no shell commands) are in `check-plan.json` in this directory. Summary:

| Check / native obligation/source | Target/config | Subject | Result | Evidence | Limitation |
| --- | --- | --- | --- | --- | --- |
| Query C++ ABI source target (FFI boundary, `issue-types.md`) | `//score/mw/com/impl/methods:method_signature_element_ptr`, `linux_x64` | C++ header @`381d43d` | **not run** | none | execution outside authority |
| Build new Rust ABI mirror (`native-verification.md` Rust library/API) | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs` (proposed), `linux_x64` | drafted file | **not run** | none | target not yet declared |
| Build extended C++ size provider | `//score/mw/com/impl/plumbing/rust/test_support:test_helper_size_provider`, `linux_x64` | edited cpp/h | **not run** | none | — |
| Rust↔C++ size/align test | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_test_rs` (proposed), `linux_x64` | Rust mirror vs C++ | **not run** | none | requires `link_std_cpp_lib` |
| Rustdoc test | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_doc_test` (proposed), `linux_x64` | drafted crate | **not run** | none | doc obligation unestablished |
| Clippy `clippy_strict` | `//score/mw/com/impl/plumbing/rust:method_in_arg_ptr_rs`, `linux_x64` | drafted crate | **not run** | none | — |
| Regression SamplePtr size test | `//score/mw/com/impl/plumbing/rust:sample_ptr_test_rs`, `linux_x64` | shared test_support | **not run** | none | — |
| Regression SampleAllocateePtr size test | `//score/mw/com/impl/plumbing/rust:sample_allocatee_ptr_test_rs`, `linux_x64` | shared test_support | **not run** | none | — |
| Regression C++ type unit test | `//score/mw/com/impl/methods:method_signature_element_ptr_test`, `linux_x64` | C++ header | **not run** | none | — |

Expected-check inventory accounting: **9 pending**, 0 executed, 0 passed, 0 failed, 0 succeeded
from cached/carried evidence. Miri/sanitizer dynamic checks are **not** required by the issue and
are recorded as not-applicable (not silently omitted). `native-check-summary.json` is absent, so
there is no trusted-collector evidence for any row. No check was measured on baseline vs candidate
because no candidate exists on disk.

## Offline decisions and portable evidence

- **Proposed engineering decisions (require authorized reviewers):**
  1. Accept the three-member layout mirror `*mut T / *mut bool / usize` as the Rust ABI for
     `MethodInArgPtr<T>`.
  2. Resolve placement (`impl/plumbing/rust` proposed vs new `impl/methods/rust`).
  3. Decide the thread-transfer (`Send`) contract.
  4. Specify ownership/destruction across FFI for the move-only C++ type.
- **Pending acceptance / safety / missing platform checks:** native build/test/lint never ran;
  QNX explicitly out of scope; dynamic analysis not required; ownership/lifetime boundary open.
- **Patch / native docs / verification logs location:** patch is embedded above (not applied);
  `scope.md`, `check-plan.json` and this packet are under `.rust-queue/reports/`.
- **Manifest:** SHA-256 digests and file sizes are **unavailable** — hashing/shell tools are
  blocked in this workspace. Files in this packet directory:
  `scope.md`, `check-plan.json`, `review-packet.md`, plus the write-capability probe
  `_probe.txt` (cannot be deleted with the available file tools). External raw evidence: none.
- **Reproduction identities:** branch baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`;
  configs `linux_x64` (build), `clippy` (lint); targets as in `check-plan.json`.
- **Concrete next action and scope:** apply the drafted edits, then run the pending targets in
  `check-plan.json` under `linux_x64`, capture raw logs and hashes, and update
  `native-check-summary.json`; submit items 1–4 above for offline human decision before merging.

*No credentials are embedded. Passing checks and completed execution would not supply a human
decision; this packet is exported for review outside the workflow.*
