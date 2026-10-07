# Scope and binding — eclipse-score/communication issue #173

Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate)

Assessment activity. No source change is proposed or authorized by this task.
Engineering acceptance of the dependency approach remains a pending offline human
decision.

## 1. Task binding

| Item | Value | Source |
| --- | --- | --- |
| Repository | `eclipse-score/communication` | `issue.json` `repository_url` |
| Issue | `#173`, `state: open`, label `rust-api`, type `Task` | `issue.json` |
| Issue `updated_at` | `2026-07-27T11:32:44Z` | `issue.json` |
| Only comment | `2026-07-27T11:32:43Z` by `bharatGoswami8`, body `https://github.com/eclipse-score/score-crates/issues/42` | `comments.json` |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` | `task.json` |
| Mode | `assessment` | `task.json` |
| Workspace | disposable run workspace `.../workspaces/173` | `task.json` |
| Platform | Linux only (QNX excluded by task) | prompt |
| Tool authority | file tools + glob only; shell, grep, web_fetch, delegation, publishing and acceptance tools are blocked (observed boundary) | prompt/observed |

Retrieval: the issue/comment bodies above were supplied in the task envelope. Live
re-fetch of issue/PR/sub-issue activity was **not possible** because `web_fetch`
returned the workspace/file-tool boundary in this session. `issue.json`
`sub_issues_summary` reports `total: 3, completed: 0`; the three sub-issues are not
resolvable locally and remain unknown.

Budget/limits: `max_source_corrections: 3` in `task.json`. No time/byte ceiling was
supplied.

## 2. Issue premise reconciliation (premise is outdated)

Issue prose states: "The COM-API currently utilizes the external **paste** crate for
declarative macros to simplify interface definitions."

At the pinned baseline this is **stale**. The COM-API macro layer already uses
`pastey`, not `paste`:

- `score/mw/com/rust/score_com_concept/interface_macros.rs` — `interface_common!`,
  `interface_consumer!` and `interface_producer!` all expand inside
  `score_com::pastey::paste! { ... }` (lines 134, 146, 163, 195).
- `score/mw/com/rust/score_com_concept/BUILD` — `proc_macro_deps` contains
  `@score_communication_crate_index//:pastey` (line 22).
- `score/mw/com/rust/score_com_concept/lib.rs` — `pub use pastey;` (line 30).
- `score/mw/com/rust/score_com.rs` — `pub use score_com_concept::pastey;` with the
  comment "See eclipse-score/communication/issues/173 - `pastey` replaces `paste` for
  identifier concatenation in the interface macros." (lines 144-146).

Consequence: the retain/paste-vs-pastey migration referenced by the issue **may
already exist** at this baseline. The issue's remaining substance is the policy for
*how uncertified external crates are handled*, which is now tracked outside this
repository by the linked `score-crates#42`. Its content is not available locally.

## 3. Dependency inventory (resolved, local evidence)

Source of resolution: `MODULE.bazel` declares
`bazel_dep(name = "score_crates", version = "0.0.11", repo_name = "score_communication_crate_index")`
(line 41). The generated crate index specs are recorded in `MODULE.bazel.lock`
(entries stamped `bazel mod show_repo 'score_crates'`). Extracted entries:

| Crate | Version | Kind | Edition | Declared features | Source archive | sha256 (index) |
| --- | --- | --- | --- | --- | --- | --- |
| `pastey` | `0.2.3` | proc-macro, no deps | 2018 | (none) | `https://static.crates.io/crates/pastey/0.2.3/download` | `2ee67f1008b1ba2321834326597b8e186293b049a023cdef258527550b9935b4` |
| `thiserror` | `2.0.21` | lib; proc-macro `thiserror-impl 2.0.21` | 2021 | `default`, `std` | `.../thiserror/2.0.21/download` | `09e52cb86a36cede5cb101bf8908837b3e4c6e5e59fe7fd85c23fb56200d189e` |
| `thiserror-impl` | `2.0.21` | proc-macro | 2021 | — | `.../thiserror-impl/2.0.21/download` | `fe5197923287db20a58125f0bc85c062f7f2c892de97b18c356f9efb14b28524` |
| `futures` | `0.3.34` | lib facade | 2018 | `alloc`, `async-await`, `default`, `executor`, `futures-executor`, `std` | `.../futures/0.3.34/download` | `9a31d2a3fbaaeb2af2368bbdd904aa8e812d3c04a1ee10d3171f52d556e5d0a3` |
| `paste` | `1.0.15` | proc-macro + build script | 2018 | (none) | `.../paste/1.0.15/download` | `57c0d7b74b563b49d38dae00a0c37d4d6de9b432382b2892f0574ddcae73fd0a` |
| `quote` | `1.0.47` | proc-macro support | — | — | (index) | — |
| `syn` | `2.0.119` / `3.0.6` | proc-macro support | — | — | (index) | — |

Notes:

- `paste 1.0.15` is **present in the score_crates index** but is **not** referenced by
  any COM-API `BUILD` file inspected; its presence does not establish COM-API usage.
- The generated crate entries declare `target_compatible_with` including
  `x86_64-unknown-linux-gnu`, `aarch64-unknown-linux-gnu`, qnx710 triples and
  `x86_64-unknown-none`. QNX entries are recorded for completeness only; QNX
  execution is out of scope for this task.
- Direct COM-API consumers of these crates (BUILD-derived):
  - `score_com_concept`: `pastey` (proc_macro_deps), `thiserror`, `futures` (deps).
  - `score_com_macros`: `quote`, `syn` (deps).
  - `basic_rust_api/producer_app` and consumers, `com-api-example`: `clap`,
    `futures`; example test also `tokio`.
- Provenance/license/notice texts and upstream advisories were **not** inspected:
  network is blocked and no vendored sources exist in this workspace. Version,
  archive URL and index digest above are the only provenance evidence obtained.
  License name of `pastey`/`thiserror`/`futures` is therefore **unknown** locally.

## 4. Macro surface and paste/`pastey` operations (source-backed)

All identifier concatenation is suffixing a captured `$id:ident` with one fixed
suffix; no prefix composition, case conversion, raw identifiers, or multi-token
schemes are used.

`interface_common!` (`interface_macros.rs:131-155`):
`[<$id Interface>]` for the struct and `[<$id Consumer>]<R>` / `[<$id Producer>]<R>`
associated types; `INTERFACE_ID` is `concat!(module_path!(), "::", stringify!($id))`
or a caller `$uid:expr`.

`interface_consumer!` (`:161-187`): `[<$id Consumer>]<R>` struct with one
`pub $event_name: R::Subscriber<$event_type>` field per event.

`interface_producer!` (`:193-253`): `[<$id Producer>]<R>` and
`[<$id OfferedProducer>]<R>` structs plus their trait impls.

`interface!` (`:80-123`) dispatches to the above and additionally:
- custom `Id = $uid:expr` form (line 89-96),
- legacy comma form `interface $id, { Id = ... }` (line 99-108),
- **explicit rejection** of `Method<T>` and `Field<T>` via `compile_error!`
  (lines 110-122).

`pastey` support operations are limited to the suffix form
`[<...>]` inside `paste!`, i.e. the exact feature subset required for four
generated type-name suffixes.

## 5. Failure modes and detection

- Wrong/missing suffix or hygiene error → generated type names (`{Id}Interface`,
  `{Id}Consumer`, `{Id}Producer`, `{Id}OfferedProducer`) are absent/renamed; Rust
  compilation of any downstream user fails, and the in-crate
  `validation_tests` (`interface_macros.rs:734-1045`) that name the types
  (`VehicleInterface`, `VehicleConsumer`, `…OfferedProducer`, `ABS*`, `Suspension*`,
  `MultiEvent*`) fail.
- Wrong `INTERFACE_ID` string → compiles but is semantically wrong; only the
  `assert_eq!` on `INTERFACE_ID` in `validation_tests`/doctests and downstream
  integration tests detect it.
- Silent drift of an event field name/type → compiles against the macro, may
  compile downstream, and is only caught by consumer/producer integration tests or
  by the `&format!` construction paths at runtime (`:171-183`, `:208-235`).
- Proc-macro supply-chain exposure: `pastey` executes at host compile time; a
  compromised proc-macro could inject identifiers/items into safety-relevant
  generated code while target code still compiles. No native tool
  trust/qualification classification exists for `pastey` locally.

## 6. Native obligations and applicable work products

Applicable native obligations discovered from the baseline sources:

- Native Rust build + unit tests + downstream compilation + rustdoc/lint
  (`references/native-verification.md`, "Rust library/API" and "Macro or
  dependency" rows).
- Macro/dependency checks: actual host/target compilation, supported
  positive/negative invocation cases, generated API compatibility, resolved
  dependency inventory (`native-verification.md`; `dependency-and-macros.md`).
- CI policy: "Build everything and run unit tests (x86-64 linux)", "Linting for
  Rust (x86-64 linux)" (clippy via `--config=clippy`), "Formatting of Rust files",
  "API checks" and "Generate and deploy documentation" (`CI.md`).
- Native external-dependency tool: `//quality/dependency_compatibility_checker`
  builds a green/orange/red matrix for *Bazel module* versions; its
  `config.yaml` currently lists `bazel`, `rules_cc`, `rules_python`, `rules_rust`
  and does **not** cover Rust crates such as `pastey`/`thiserror`/`futures`.

Referenced native work-product types from the process pin
`98d1d5f42dad412a09a888ea25e59c62fa6371ce` (`wp__tlm_plan`,
`wp__tool_verification_report`, version 1, status `valid`) are **type definitions,
not instances**. No instance files exist in this workspace; applicability to
`pastey`/`thiserror`/`futures` is **unknown** and no confidence/qualification
decision is made here.

## 7. Options assessment (proposal only — decision not made)

| Option | Compatibility / build impact | Provenance / license / maintenance | Qualification & verification effort | Proposed rationale / gaps |
| --- | --- | --- | --- | --- |
| **Retain `pastey 0.2.3`** | No build/lock change; already compiled by `score_com_concept` and re-exported by `score_com`. Only suffix-paste used. | Version/digest known from index; **license, upstream maintenance and advisories unknown locally**. | Reuse existing native tests/doctests + downstream targets; add dependency/tool justification per `dependency-and-macros.md`. | Lowest churn and matches current baseline; blocked on the cross-repo certification decision (`score-crates#42`) and missing license/provenance inspection. |
| **Replace with `paste 1.0.15`** (index-present) | Would restore the crate named in the issue; requires BUILD + `lib.rs`/`score_com.rs` re-export edits. | Index entry exists but no COM-API usage; upstream suitability not established locally. | Full re-run of macro positive/negative + downstream API checks. | Contradicts the observed migration; not recommended without new evidence. |
| **Integrate into the repo (issue option 1)** | Vendor/import macro logic; new maintained code in-repo. | Removes one external proc-macro provider but moves maintenance + license/notice burden in-tree. | Native design/maintenance ownership + full verification. | Maps to issue option 1; significant bounded work, no authority here. |
| **Hand-written implementation (issue option 2)** | Reimplement only suffix concatenation for four suffixes; touches all three `interface_*` macros. | Removes `pastey` entirely; internal code still carries qualification obligations. | Must reproduce hygiene/diagnostics and re-run all macro tests/doctests + downstream. | Maps to issue option 2; feasible in principle but not authorized and higher maintenance. |

Candidate recommendation (reviewable, **not** an accepted decision): retain
`pastey 0.2.3` at this baseline and route the "integrate vs. manual" policy
decision through `score-crates#42` and the native tool/qualification work products,
because (a) the baseline already depends on `pastey` and only a narrow,
well-covered suffix capability is exercised, and (b) this task holds no authority
to change dependencies or accept a qualification. All three options remain open.

## 8. Gaps and unknowns (preserved)

- `.rust-queue/reports/native-check-summary.json` **does not exist** in this
  workspace (no `reports/` dir existed before this task). Native result summaries
  are therefore **missing** and not carried into this assessment.
- No native test/build/query/lint was executed: shell and measurement tooling are
  outside agent authority. All `check-plan.json` entries are *planned*, not run.
- `pastey`/`thiserror`/`futures` license, notice, upstream maintenance and any
  advisories were not verified (network blocked, no vendored sources).
- `score-crates#42` (the linked policy/certification issue) could not be fetched;
  its scope/status is unknown.
- Native tool work products (`wp__tlm_plan`, `wp__tool_verification_report`) have
  no project instances here; applicability unknown.
- Rust has no in-repo API-surface lock equivalent to the C++
  `//score/mw/com:api_surface_test`; Rust generated-API stability relies on
  downstream compilation targets only.
- QNX checks are recorded as unavailable by task policy, not evaluated.
- File hashes/sizes for the review-packet manifest cannot be computed (no shell);
  they must be supplied by the deterministic collector.

## 9. Acceptance status

Technical assessment: drafted (this document + `check-plan.json` +
`review-packet.md`). Native engineering acceptance: **pending offline human
decision**; no requirement/design/safety sign-off, no certification, no
qualification status and no confidence decision is asserted.

See `check-plan.json` for the native BUILD-derived check plan and
`review-packet.md` for the acceptance trace, expected checks and offline
decisions.
