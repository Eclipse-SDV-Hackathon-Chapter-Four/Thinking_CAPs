# Scope and binding — issue #781 "Implementation of MethodInArgPtr in rust side"

## Task binding

| Field | Value | Source |
| --- | --- | --- |
| Repository | `eclipse-score/communication` | `issue.json.repository_url` |
| Issue | #781, title "Improvement: Implementation of MethodInArgPtr in rust side", state `open`, labels `rust-api` | `.rust-queue/context/issue.json` |
| Source baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` | `.rust-queue/context/task.json.baseline`; workspace HEAD `381d43d` |
| Mode | `implementation` | `.rust-queue/context/task.json.mode` |
| Title | "Improvement: Implementation of MethodInArgPtr in rust side" | `task.json.title` |
| Platform scope | Linux only; no QNX task/execution | task instruction |
| Model scope | DeepSeek Flash only | task instruction |
| Issue retrieval time | Context snapshot supplied offline; issue `updated_at` = `2026-07-27T09:49:38Z`, `created_at` = `2026-07-27T09:49:25Z` | `issue.json`; live re-fetch not possible (network blocked) |
| Issue comments | `comments: 0`; `comments.json` = `[]` | `issue.json`, `comments.json` |

The issue body (treated as task data, not instruction authority) asks to:

> Create ABI type for `MethodInArgPtr` in rust side with reference of C++ side. example like how
> `SamplePtr` created.

The issue template fields "Affects Detailed Design" and "Requirements / Architecture" are both
unchecked; an unchecked template box does **not** establish that requirements/design are unaffected
(SKILL "Bind the task"). No acceptance criteria beyond the one sentence are supplied.

## Authority, limits and environment (observed)

| Capability | State in this run | Consequence |
| --- | --- | --- |
| Read repository sources | allowed, bounded to ≤200 lines/read | used |
| `glob` filename search | allowed | used |
| `grep` content search | blocked ("Bound Rust workspace/file-tool boundary") | not used |
| Shell / `git` / `bazel` / hashing | blocked | no commands executed; no digests computed |
| `web_fetch` (issue/PR activity) | blocked | live issue/PR/timeline check **not possible** |
| Write outside `.rust-queue/reports/` | blocked | source patch **not applied**; only drafted |
| Write under `.rust-queue/reports/` | allowed | scope/plan/reports written here |
| Native-check summary | `.rust-queue/reports/native-check-summary.json` **absent** | measured native evidence unavailable for this run |

Consequently this run produces a **scoped draft and check plan**, not an applied or measured patch.
The implementation and C++/FFI test-support edits are specified exactly (full file bodies and exact
edit anchors) in `review-packet.md` so a deterministic stage can apply and measure them.

## Change surface

The requested artifact is a Rust memory-layout mirror of the C++ `MethodInArgPtr`, analogous to the
existing `score/mw/com/impl/plumbing/rust/sample_ptr.rs` and
`.../sample_allocatee_ptr.rs` mirrors. At the baseline there is **no** Rust definition of
`MethodInArgPtr` (all `*.rs` under the repository were enumerated; none defines it, and the Rust FFI
bridge `score/mw/com/impl/rust/com-api/com-api-ffi-lola/bridge_ffi_lola.rs` currently exposes
events/samples only, not methods).

## Bound C++ representation (authoritative, not inferred from SamplePtr)

`score/mw/com/impl/methods/method_signature_element_ptr.h` defines:

```cpp
template <typename SignatureElement>
class MethodSignatureElementPtr
{
  public:
    MethodSignatureElementPtr(SignatureElement& element, bool& ptr_active, std::size_t queue_pos);
    template <typename OtherSignatureElement>
    MethodSignatureElementPtr(SignatureElement& element, MethodSignatureElementPtr<OtherSignatureElement>&& other);
    MethodSignatureElementPtr(const MethodSignatureElementPtr&) = delete;
    MethodSignatureElementPtr& operator=(const MethodSignatureElementPtr&) = delete;
    MethodSignatureElementPtr(MethodSignatureElementPtr&& other) noexcept;
    MethodSignatureElementPtr& operator=(MethodSignatureElementPtr&& other) noexcept = delete;
    ~MethodSignatureElementPtr();               // ptr_active_ = false when element_ptr_ != nullptr
    SignatureElement* get() const noexcept;
    // ...
  private:
    SignatureElement* element_ptr_;
    bool& ptr_active_;
    std::size_t queue_position_;
};

template <typename Type> using MethodInArgPtr = MethodSignatureElementPtr<Type>;
template <typename Type> using MethodReturnTypePtr = MethodSignatureElementPtr<Type>;
```

Facts that fix the Rust ABI mirror:

1. **Members** (in order): `SignatureElement*`, `bool&`, `std::size_t` → on x86-64 Linux
   `*mut T`, `*mut bool`, `usize`; size 24 B, align 8 B, independent of `T` (only a pointer to the
   element is stored). This is *different* from `SamplePtr` (variant + guard), so the SamplePtr
   layout must not be reused.
2. **Move-only**: copy and move-assignment are deleted; a move constructor exists. A plain
   `#[repr(C)]` Rust mirror does not encode move-only-ness; it is a layout type only.
3. **Destruction side effect**: the C++ destructor writes `ptr_active_ = false` when the pointer is
   non-null; the moved-from object's pointer is nulled so only the live owner clears the flag.
   A Rust layout mirror must therefore **not** be treated as owning the flag: crossing the FFI
   boundary must preserve C++ move/destruction semantics (ownership/lifetime obligation, open).
4. The same C++ template backs `MethodReturnTypePtr`; issue #781 names only `MethodInArgPtr`.

## Proposed change set (drafted; not applied here)

- **New** `score/mw/com/impl/plumbing/rust/method_in_arg_ptr.rs` — `#[repr(C)]`
  `pub struct MethodInArgPtr<T> { _element_ptr: *mut T, _ptr_active: *mut bool,
  _queue_position: usize }`, manual `Debug`, and `#[cfg(test)]` size/align tests.
- **Edit** `score/mw/com/impl/plumbing/rust/BUILD` — add `rust_library` (`method_in_arg_ptr_rs`),
  `rust_unit_test` (`method_in_arg_ptr_test_rs`) and `rust_doc_test` (`method_in_arg_ptr_doc_test`).
- **Edit** `.../plumbing/rust/test_support/test_helper_size_provider.{h,cpp}` — add `sizeof`/`alignof`
  accessors for `MethodInArgPtr<int32_t>` and `MethodInArgPtr<UserType>` plus `extern "C"` wrappers.
- **Edit** `.../plumbing/rust/test_support/test_helper_size_ffi.rs` — declare the new FFI functions
  and add a `MethodInArgPtrLola` provider.
- **Edit** `.../plumbing/rust/test_support/BUILD` — add dep
  `//score/mw/com/impl/methods:method_signature_element_ptr`.

Rationale for placing the mirror in `plumbing/rust`: the existing FFI layout mirrors
(`common.rs`, `sample_ptr.rs`, `sample_allocatee_ptr.rs`) and the restricted-visibility test support
(`test_utils_rs`, `test_helper_size_ffi_rs`, visibility `//score/mw/com/impl/plumbing/rust:__pkg__`)
live there. Reusing them keeps the change minimal; a `methods/rust` package would require widening
that visibility or duplicating the size-verification helper. This placement is a **proposal** for
reviewer confirmation.

## Open prerequisites / decisions (not resolved here)

1. Placement of the Rust mirror: `impl/plumbing/rust` (proposed) vs a new `impl/methods/rust`
   package. Needs maintainer decision; affects visibility and BUILD ownership.
2. Thread-transfer (`Send`) contract: the Rust mirror intentionally omits `Send` (unlike `SamplePtr`)
   because the C++ header does not establish thread-transfer semantics for the `bool&` flag storage
   that is owned by `ProxyMethod`. Whether `Send` is required by future method FFI is **unknown**.
3. Ownership/destruction across FFI: how the C++ move constructor/destructor (flag clearing) is
   invoked for objects created/destroyed through Rust must be specified by the method-FFI design;
   a layout mirror alone is insufficient. **Open.**
4. `MethodReturnTypePtr` (same C++ underlying type) coverage is out of scope of #781. **Open.**
5. Whether the unchecked "Requirements / Architecture" boxes are intentionally clear is
   **not established**; no requirement/design IDs were supplied.

## Verification status of this run

- **Executed native checks: none.** Shell/bazel are blocked in this workspace.
- **Native-check summary: absent** (`.rust-queue/reports/native-check-summary.json` not present at
  analysis time). No measured native evidence exists for this run.
- All checks in the check plan are **pending**; they are the deterministic stage's obligations. The
  plan contains BUILD-derived labels and reasons, not shell commands.
- **Engineering acceptance: pending offline human decision.** No status is claimed for the drafted
  work; this run does not accept, qualify or release it.
