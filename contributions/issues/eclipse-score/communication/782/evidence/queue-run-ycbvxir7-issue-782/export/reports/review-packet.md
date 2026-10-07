# S-CORE Rust issue review packet — #782

## Scope and binding

- **Issue/repository**: `eclipse-score/communication` #782 "Improvement: Runtime implementation
  for Rust Method APIs" (`open`, label `rust-api`). Retrieval: supplied snapshot only
  (issue updated 2026-09-08; live network was blocked). Source commit:
  `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
- **User authority / limits**: DeepSeek Flash only; Linux only; no QNX task/execution; file
  tools only. Shell, network, delegation, publishing and acceptance tools were blocked. Command
  stages and raw evidence are outside agent authority. Artifact destination:
  `.rust-queue/reports/`.
- **Process/tailoring/requirement/design/policy versions**: The Method requirements/design
  artifacts are **not present at the baseline**; authority is PR #777 (design) and PR #818
  (trait/macro/type-state) as referenced in issue prose/comments — status not re-verifiable
  offline. Prerequisite **#781 status is UNKNOWN**. E2E excluded (#1062). Native IDs for a
  Method requirement/design artifact remain unknown.
- **Source/lock/tool bindings (read at baseline)**: `MODULE.bazel` — `rules_rust 0.68.2-score`,
  `score_crates 0.0.11`, `score_baselibs 0.2.14`, `score_toolchains_rust` (Ferrocene) via
  `@score_toolchains_rust//toolchains/ferrocene`; `.bazelrc` — default `--config=linux_x64`
  → `linux_x64_gcc_15` (Ferrocene `ferrocene_x86_64_unknown_linux_gnu`), QNX configs present but
  out of scope; lint config `quality/static_analysis/static_analysis.bazelrc` (`build:clippy` →
  `@score_rust_policies//clippy:linters.bzl%clippy_strict`). `MODULE.bazel.lock` present
  (not parsed). Exact dependency hashes not computed (no shell).
- **Final patch**: none. Baseline-to-patched digest is identical (no source edits).
- **Technical completion**: **blocked/assessed**. Engineering acceptance: **not claimed / pending
  offline** (design prerequisite unresolved).

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact ID and revision | Changed artifact | Required check | Evidence/hash | Gap or proposed disposition |
|---|---|---|---|---|---|
| Implement LoLa Runtime per designed Method traits | Design PR #777 + #818 (UNKNOWN status); no baseline artifact | none | build `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola` | source findings (scope.md §3) | **Blocked**: trait contract absent; must not invent. Land #818 first. |
| Align with existing Event backend pattern | Event runtime/FFI pattern at baseline (observed) | none | `com-api-runtime-lola-tests`, doc-tests | scope.md §3 Finding A | Pattern observable; Method application unknown. |
| Implement required FFI APIs for external interop | C++ Method backend exists; Rust-facing ABI unknown | none | build `:bridge_ffi_lola`, `:bridge_ffi_rs`, `:registry_bridge_macro_cpp` | scope.md §3 Finding B | **Open**: no Method FFI symbols at baseline; ABI/callback/error/unwind contract undefined in Rust. |
| Linux-only verification | BUILD `target_compatible_with=["@platforms//os:linux"]`; #1278 | n/a | Linux test targets in check-plan.json | BUILD files | Method tests do not exist yet. |
| E2E protection not in milestone | Issue comment decision (#1062) | n/a | excluded | comments.json | Separate ticket; not implemented here. |

Baseline reconciliation: the issue premise ("design created … implement as per designed interface
trait") does **not** match the selected baseline, because neither the Rust Method trait layer nor
the `com-api-runtime-lola/method.rs` placeholders referenced in the comments exist at
`381d43d`. Rollback/no-op is therefore the only source-faithful action until the design lands.

## Dependency and macro assessment (only the macro surface applies)

- The change would touch the `interface!` declarative macro in `score_com_concept`
  (currently a `compile_error!` arm for `Method<T>`), but **no new crate/dependency** is
  introduced by this scoped assessment, so crate replacement/qualification is not applicable.
- Macro failure mode to preserve/add: incorrect generation could yield wrong accessor names or
  missing Method members. At baseline the compiler/test detects the unsupported arm via
  `compile_error!` and the `compile_fail` doctest `interface_macro_with_Method`
  (`interface_macros.rs:356-386`). Any future Method arm must keep unsupported-syntax rejection.
- No host-executed generator change is proposed here.

## Verification and expected checks

Full machine-readable plan: `.rust-queue/reports/check-plan.json` (19 checks: 1 query, 8 build,
7 test, 3 docs, 1 lint; all `config=linux_x64`, all targets BUILD-derived).

| Check and native obligation/source | Command/config/tool/target/features | Subject hashes | Result/exit code | Raw evidence/hash | Limitation/disposition |
|---|---|---|---|---|---|
| Abstraction crate build | not executed | unknown | **unmeasured** | none (collector summary absent) | No commands executed (agent authority boundary) |
| FFI bridge build incl. Method symbols | not executed | unknown | **unmeasured** | none | ABI undefined at baseline |
| Runtime crate build | not executed | unknown | **unmeasured** | none | Implementation gated on #818 |
| Runtime/mock unit tests | not executed | unknown | **unmeasured** | none | Method tests absent |
| Macro/concept compile tests | not executed | unknown | **unmeasured** | none | Method arm absent |
| Downstream example / integration tests | not executed | unknown | **unmeasured** | none | Linux only; sanitizer caveat #794 |
| rustdoc/doc-tests | not executed | unknown | **unmeasured** | none | Manual target enumerated |
| clippy_strict lint | not executed | unknown | **unmeasured** | none | Aspect config observed only |

- Distinguish evidence classes: everything above is a **proposed check**, not trusted collector
  evidence, direct local execution, or carried evidence.
- Generated-API compatibility was **not** measured on baseline or candidate.
- Explicitly unrun/blocked: all build/test/query/docs/lint checks (tools outside authority).
- Missing evidence preserved: `.rust-queue/reports/native-check-summary.json` is **absent**;
  no summary or raw logs were available.

## Offline decisions and portable evidence

- **Proposed engineering decisions and required reviewers**: (1) Do not implement before the
  #818 Method design is admitted into the source baseline — owner: design/backend maintainers
  (`bharatGoswami8`, `LittleHuba` per comments). (2) Confirm prerequisite **#781** status —
  owner: issue maintainer. (3) After design lands, re-run this scope and the checks in
  `check-plan.json` — owner: implementing contributor + CI.
- **Pending acceptance / gaps**: design PR #777/#818 merge state; #781 status; Rust Method FFI
  ABI, callback/teardown/error/unwind contract; sync-vs-async dispatch decision (issue #767);
  Method E2E (#1062) and QNX (#1278) deferred.
- **Patch, documents, evidence location**: no patch. Reports under `.rust-queue/reports/`:
  `scope.md`, `check-plan.json`, `review-packet.md`. No external raw evidence.
- **Manifest** (relative path; SHA-256 unavailable — hashing requires shell, which was blocked):

  | File | SHA-256 |
  |---|---|
  | `.rust-queue/reports/scope.md` | not computed |
  | `.rust-queue/reports/check-plan.json` | not computed |
  | `.rust-queue/reports/review-packet.md` | not computed |

- **Source/tool/config identities**: baseline `381d43d…`; `MODULE.bazel` pins above; `.bazelrc`
  `linux_x64`/Ferrocene; `static_analysis.bazelrc` clippy_strict; BUILD labels in `check-plan.json`.
- **Concrete next action**: authorised reviewer lands/admits the #818 Method design and confirms
  #781; then re-open implementation against that revision and execute the check plan through the
  trusted collector.

Do not embed credentials. Passing checks and completed execution do not supply a human decision.
This packet is exported for offline human review.
