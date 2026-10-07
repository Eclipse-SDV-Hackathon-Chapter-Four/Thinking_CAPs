# S-CORE Rust issue review packet — #741

Task: `Improvement: Move the Rust Sample example app from com/example to tutorial folder`.
Mode: `implementation` (draft). This packet is the portable, offline-reviewable record.

## Scope and binding

- Issue/repository, retrieval time, source commit and current issue/PR state:
  `eclipse-score/communication` issue #741; snapshot state `open`, label `rust-api`, 0 comments;
  baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`; local retrieval 2026-10-06.
  Live GitHub API/timeline/PR refresh **unavailable** (tool boundary blocks `web_fetch`);
  history-reuse = none (`task.json`).
- User authority, permitted writes/executions, artifact destination and budget limits:
  write scope limited to `.rust-queue/reports/**`; shell/grep/delegation/publishing/acceptance
  blocked; artifacts to `.rust-queue/reports/`; no QNX task or execution; Linux only.
- Process/tailoring/requirement/design/safety/policy versions, hashes and native IDs:
  `.rust-queue/context/score-rust-workflow/SKILL.md` v1.0.0; issue's template asserts
  requirements/architecture unaffected. No native requirement/design/safety/qualification ID
  references the example package (source inspection). Native IDs remain **unknown** where not
  sourced — none invented.
- Source/lock/tool/environment/storage-selection bindings:
  Build system Bazel (`MODULE.bazel`, `MODULE.bazel.lock`, `WORKSPACE`); `.bazelrc`
  `common:linux_x64 -> linux_x64_gcc_15`, Ferrocene `ferrocene_x86_64_unknown_linux_gnu`;
  Rust rules `@rules_rust`. Cargo is not the maintained native build, so no Cargo harness used.
  Tool/binary hashes were **not computed** (no shell/hash tooling inside the boundary).
- Final patch and baseline-to-patched source digest or manifest:
  No patch applied (source writes blocked). Draft change set is in `scope.md` §4;
  file manifest in `scope.md` §2. No digests available.
- Technical completion status; engineering acceptance status and decision references:
  **Technically drafted / not applied.** Engineering acceptance **pending** (no authorized human
  decision; no native evidence). See §"Offline decisions".

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact ID and revision | Changed artifact | Required check | Evidence/hash | Gap or proposed disposition |
| --- | --- | --- | --- | --- | --- |
| App moved out of `score/mw/com/example/` | `query` package/`BUILD` structure at `381d43d` | 13 files removed; empty `example/` gone | `query //score/mw/com/doc/tutorial/com-api-example:all`; assert old label gone | none yet (native-check-summary absent) | pending deterministic stage |
| App present under `score/mw/com/doc/tutorial/` | `//score/mw/com/doc/tutorial/com-api-example/BUILD` | 13 files at new path | `build` moved targets | none yet | pending |
| BUILD labels valid | rust_library/rust_binary/rust_test/cc_library in moved BUILD | `deps` ×3 + `MW_LOG_CONFIG_FILE` env path | `build` + `query` | none yet | pending |
| Runnable content/notices preserved | Apache-2.0 headers in all `.rs`/`.h`/`.cpp`; JSON configs | renames (byte-preserving) | `test` + `build` | none yet | JSON contents not directly readable in boundary; moved verbatim |
| Docs/usage references valid | `USAGE.md`, `main.rs` L72, `tests_using_tokio_runtime.rs` L26/L44 | path strings rebased | `docs //docs/sphinx:sphinx_doc`, `//score/mw/com/doc/tutorial:tutorial_rst` | none yet | pending |
| Rust lint policy preserved | `--config=clippy`, `//:format_test` | moved Rust/BUILD files | `lint` | none yet | pending |

Baseline reconciliation and status: not already moved; no public re-export, lock, pin,
toolchain, API-surface or requirement/design/safety artifact is affected. The change is
location-only plus self-referential path strings; link direction of the moved labels is
internal to the package. Unaffected-claims rationale is in `scope.md` §6.

## Dependency and macro assessment (when applicable)

Not applicable — no dependency, crate pin, feature flag or macro invocation is changed.
The example's `@score_communication_crate_index` deps and `@rules_rust` usage are untouched;
no crate qualification decision is requested or made.

## Verification and expected checks

Full machine-readable plan: `.rust-queue/reports/check-plan.json` (kinds: query, build, test,
docs, lint). No command was executed by this agent (command stages are outside agent authority).

| Check and native obligation/source | Target(s) | Tool/config | Subject hashes | Result/exit code | Raw evidence | Limitation/disposition |
| --- | --- | --- | --- | --- | --- | --- |
| query package resolves | `//score/mw/com/doc/tutorial/com-api-example:all`, `.../com-api-gen:all` | bazel query / linux_x64 | n/a | not run | none | post-move only; also assert old label absent |
| build moved targets | `:com-api-example`, `:com-api-example-lib`, `com-api-gen:com-api-gen`, `com-api-gen:vehicle_gen_cpp` | bazel build / linux_x64 (Ferrocene) | n/a | not run | none | pending |
| integration test | `:com-api-example-tokio-integration-test` | bazel test / linux_x64 | n/a | not run | none | Linux-only; sanitizer configs incompatible; QNX excluded (issues #794, #1278) |
| docs | `//score/mw/com/doc/tutorial:tutorial_rst`, `//docs/sphinx:sphinx_doc` | bazel build / linux_x64 (`-W`) | n/a | not run | none | USAGE.md not in docs; inclusion OPEN |
| clippy | moved Rust targets | aspect lint / `--config=clippy` | n/a | not run | none | pending |
| format | `//:format_test` | rustfmt/buildifier / linux_x64 | n/a | not run | none | pending |

Expected-check inventory: 6 planned checks, 0 executed, 0 failed, 0 unavailable-run,
0 manual/excluded (the Tokio test is Linux-only but not `manual`-tagged in BUILD — see
`scope.md` §7.4). No generated API compatibility was measured on baseline or candidate.
`native-check-summary.json` was absent at write time; this is recorded as missing evidence,
not back-filled.

## Offline decisions and portable evidence

- Proposed engineering decisions and required authorized reviewers/roles:
  (a) confirm target leaf name `com-api-example`; (b) decide whether `USAGE.md`/the sample
  becomes rendered tutorial documentation; (c) confirm no competing upstream PR. Required:
  repository maintainers / CODEOWNERS (§`.github/CODEOWNERS` default owners), Rust API owners.
- Pending acceptance, safety/qualification gaps and missing platform checks:
  acceptance pending; QNX variants intentionally out of scope (no QNX task/execution);
  sanitizer runs excluded by native BUILD for the Tokio test; exhaustive cross-repo text
  search not performed (grep blocked) — negative confirmed by reasoning only.
- Patch, native documents, verification logs and complete packet manifest location:
  `.rust-queue/reports/{scope.md,check-plan.json,review-packet.md}`. Raw native logs would live
  outside agent authority (host) and are currently absent.
- Manifest: relative file path, size and SHA-256 for each included file:
  `scope.md`, `check-plan.json`, `review-packet.md` — size/digest **not computable** in this
  boundary (no shell/hash tooling). Marked unknown rather than fabricated.
- Source/tool/config identities sufficient to understand/reproduce the checks without Fabro:
  baseline `381d43d`; `.bazelrc` configs `linux_x64`/`linux_x64_gcc_15`; `MODULE.bazel` pins;
  `docs/sphinx/BUILD` `sphinx_doc`; `score/mw/com/example/com-api-example/BUILD` targets.
- Concrete next action and scope required:
  apply `scope.md` §4, then run `check-plan.json` on Linux and write
  `.rust-queue/reports/native-check-summary.json`. Human review decides the open items before
  any acceptance/qualification claim.

Do not embed credentials. Passing checks and completed execution do not supply a human
decision. Acceptance remains pending; review occurs outside the workflow.

## Implementation-stage addendum (2026-10-06)

Full detail and the exact change specification: `.rust-queue/reports/implementation.md`.

Boundary re-measured at implementation time (supersedes the scope-stage wording that *all*
source writes were rejected), observed directly as `Bound Rust workspace/file-tool boundary`:

- Source-tree writes **are** permitted (`write_file`/`edit_file` create/modify files).
- **No delete/rename primitive exists**; an empty `write_file` does not remove a file, and every
  `shell` invocation (including `pwd`, `git`, `rm`, `mv`) is denied.
- `grep`, `web_fetch`, `.git` reads, and `read_file` of any source `score/**/*.json` are denied.

Consequence: the 13-file move cannot be completed by this agent. A concatenating copy would leave the
old `//score/mw/com/example/com-api-example:*` package alive and add a broken package (the two
`etc/*.json` files cannot be carried verbatim), so **no duplicate tree was created**. Instead the
change is fully specified for the deterministic stage (renames + the 6 reference-edit groups).

Actual changed paths in this workspace are only boundary-probe artifacts, which the deterministic
stage must remove: `score/mw/com/doc/tutorial/com-api-example/BUILD` (comment-only placeholder) and
`.rust-queue/reports/boundary-test.txt`. No deliverable source change was applied.

Verification unchanged: `check-plan.json` (query/build/test/docs/lint, linux_x64) remains the planned
check set and is valid only after the deterministic stage applies the move.
`native-check-summary.json` remains absent — missing evidence, not back-filled.
Acceptance remains **pending**; open items §7.1–§7.4 of `implementation.md` need human review.
