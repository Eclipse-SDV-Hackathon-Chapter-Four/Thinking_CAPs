# Scope — Issue #741: Move the Rust Sample example app from com/example to tutorial folder

## 1. Binding

| Field | Value |
| --- | --- |
| Repository | `eclipse-score/communication` |
| Issue | #741 (`https://github.com/eclipse-score/communication/issues/741`), state at snapshot: `open`, labels: `rust-api`, comments: 0 |
| Task mode | `implementation` (`task.json`) |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Workspace | `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-rust-issue-queue-ycbvxir7/workspaces/741` |
| Platform scope | Linux only (`config = linux_x64`, `.bazelrc` → `linux_x64_gcc_15`) |
| Model constraint | DeepSeek Flash only |
| Retrieval time (local) | 2026-10-06 |
| Network / live issue-PR refresh | **Unavailable** — `web_fetch` (GitHub API for issue/timeline) is blocked by the tool boundary; `.rust-queue/context/comments.json` is `[]`. |
| Permitted writes | Only `.rust-queue/reports/**`. Shell, grep, delegation, publishing and acceptance tools are blocked; source-tree writes (`write_file`/`edit_file` outside reports) are rejected by the boundary. |

Command stages and raw evidence are outside agent authority. This report is a **draft/plan**; deterministic command stages apply and measure it. No native evidence is invented here.

## 2. Baseline reconciliation — is it already moved?

**No.** At baseline `381d43d` the example still lives at `score/mw/com/example/com-api-example/`, and `score/mw/com/doc/tutorial/` contains only `BUILD`, `README.md`, `README.rst` and the C++ `chapter_1..chapter_13` packages. No `com-api-example` package exists under the tutorial path. The move has not been performed in this baseline.

### Current example package (13 files)

```
score/mw/com/example/com-api-example/BUILD
score/mw/com/example/com-api-example/USAGE.md
score/mw/com/example/com-api-example/main.rs
score/mw/com/example/com-api-example/tests_using_tokio_runtime.rs
score/mw/com/example/com-api-example/src/lib.rs
score/mw/com/example/com-api-example/src/consumer.rs
score/mw/com/example/com-api-example/src/producer.rs
score/mw/com/example/com-api-example/com-api-gen/BUILD
score/mw/com/example/com-api-example/com-api-gen/com_api_gen.rs
score/mw/com/example/com-api-example/com-api-gen/vehicle_gen.cpp
score/mw/com/example/com-api-example/com-api-gen/vehicle_gen.h
score/mw/com/example/com-api-example/etc/logging.json
score/mw/com/example/com-api-example/etc/mw_com_config.json
```

`score/mw/com/example/` contains no BUILD file of its own; `com-api-example` is the only package in that subtree, so after the move the `example/` directory becomes empty and is removed.

## 3. Requested outcome, restated

- What: move the Rust COM API example app currently at `score/mw/com/example/com-api-example` **under** `score/mw/com/doc/tutorial/`.
- How: not specified by the issue (`_No response_`).
- Impact checkbox: **"Requirements / Architecture are not affected by this change?" = checked.** A checked template box is task data, not independent proof; this report still records the requirement/design reconciliation below.
- Estimate recorded by issue: `0`.
- Origin: PR #736 discussion `r3629386371` (not retrievable live; recorded as the issue's own provenance).

## 4. Proposed change (draft for the deterministic stage)

Target path chosen: `score/mw/com/doc/tutorial/com-api-example/` (keep the existing leaf name `com-api-example`; minimal change, preserves target basenames).

### 4.1 Pure renames (content preserved byte-for-byte)

Replace prefix `score/mw/com/example/com-api-example/` with `score/mw/com/doc/tutorial/com-api-example/` for all 13 files listed in §2. Licenses/notices inside each file are unchanged.

### 4.2 Reference edits required after the rename

The following are the **only** path/native-label references to the moved location found in the package. They are BUILD-derived and doc-derived.

**`score/mw/com/doc/tutorial/com-api-example/BUILD`** (`//score/mw/com/example/com-api-example/com-api-gen` → `//score/mw/com/doc/tutorial/com-api-example/com-api-gen`, 3 occurrences; plus one env path):

- L22 `deps` of `com-api-example-lib`
- L43 `deps` of `com-api-example`
- L69 `deps` of `com-api-example-tokio-integration-test`
- L38 env value `MW_LOG_CONFIG_FILE`: `"score/mw/com/example/com-api-example/etc/logging.json"` → `"score/mw/com/doc/tutorial/com-api-example/etc/logging.json"`

**`score/mw/com/doc/tutorial/com-api-example/main.rs`**:

- L72 clap default: `default_value = "./score/mw/com/example/com-api-example/etc/mw_com_config.json"` → `./score/mw/com/doc/tutorial/com-api-example/etc/mw_com_config.json`

**`score/mw/com/doc/tutorial/com-api-example/tests_using_tokio_runtime.rs`**:

- L26 doc comment: `bazel test //score/mw/com/example/com-api-example:com-api-example-tokio-integration-test` → `.../doc/tutorial/com-api-example:...`
- L44 `TEST_CONFIG_PATH`: `"./score/mw/com/example/com-api-example/etc/mw_com_config.json"` → `./score/mw/com/doc/tutorial/com-api-example/etc/mw_com_config.json`

**`score/mw/com/doc/tutorial/com-api-example/USAGE.md`**:

- Every occurrence of `score/mw/com/example/com-api-example` → `score/mw/com/doc/tutorial/com-api-example` (11 lines: 55, 67, 74, 77, 80, 83, 86, 89, 104, 107, 111).
- L124 relative link must rebase for the deeper location: `../../impl/rust/com-api/README.md` → `../../../impl/rust/com-api/README.md`. (The link target `score/mw/com/impl/rust/com-api/README.md` does not exist on this baseline — a pre-existing dangling doc link; its *relative base* is still corrected.)

### 4.3 Files that need no content change

- `com-api-gen/BUILD`: its visibility `//score/mw/com:__subpackages__` remains valid (the new path is still under `score/mw/com`); its deps (`//score/mw/com/rust:score_com`, `@score_baselibs//...`) are absolute and unchanged.
- `com-api-gen/com_api_gen.rs`, `com-api-gen/vehicle_gen.cpp`, `com-api-gen/vehicle_gen.h`, `src/*.rs`, `etc/*.json`: no path references.
- `score/mw/com/doc/tutorial/BUILD`: does not reference the example, so it is unaffected (see open item §7.2).

### 4.4 Not required (deliberately out of scope)

- Renaming the C include guard `SCORE_MW_COM_EXAMPLE_COM_API_EXAMPLE_VEHICLE_DATATYPE_H` in `vehicle_gen.h` (cosmetic identifier, not a BUILD/doc reference). Left unchanged to keep the change minimal and behavior-preserving.
- Adding/moving the example into Sphinx docs (`sphinx_docs_library`) — see §7.2, kept OPEN.

## 5. Reference-discovery method and limitation (evidence)

- `grep` and `shell` are blocked by the tool boundary, so an exhaustive cross-repo text search for `com/api/example` / `com-api-example` could **not** be executed. References were discovered by reading the affected package and the surrounding build/doc graph.
- Strength of the negative: the moved targets are leaves. `com-api-example-lib` has default (package-private) visibility; the `rust_binary`/`rust_test` are terminal. `com-api-gen` is exposed only to `//score/mw/com:__subpackages__` and is example-specific. CI lints/tests use `//...` wildcards (`.github/workflows/_linter.yml`, `_build_and_test_gcc15.yml`), not path allowlists. `CODEOWNERS` has no path entries. Therefore no other cross-package label is expected to point at the old package.
- **Residual gap:** an exhaustive machine search was not possible; this negative is reasoned, not measured. A deterministic `bazel query`/workspace text search is the appropriate confirmation (see check-plan).

## 6. Requirements / design / safety reconciliation

- The issue's template asserts requirements/architecture are unaffected. Source inspection finds no requirement, architecture, design-doc, safety, API-surface or qualification identifier inside the example package; it is a sample app plus a generated interface. No `.lock`, toolchain, `MODULE.bazel`, policy or public API surface file is touched.
- The move changes only package location plus the path strings that name that location. Observable example behavior (producer/consumer, CLI defaults, config discovery, Linux-only Tokio test) is preserved.
- No MISRA-C++ policy transferred to Rust; no lint/toolchain/pin change is proposed.

## 7. Open items / pending decisions (do not self-accept)

1. **Target leaf name.** Chosen `com-api-example`. If maintainers prefer a Rust-specific folder name (e.g. `rust_api_example`), review is required; no native source states the intended name.
2. **Should the example's `USAGE.md` be registered in the Sphinx docs?** The tutorial `sphinx_docs_library` (`//score/mw/com/doc/tutorial:tutorial_rst`) lists only chapter `doc_files`; the moved package is a separate package and is not automatically included. Whether the sample should become tutorial documentation (and if so, as Markdown via myst or converted RST, and how the docs `prefix` is handled) is a documentation-design decision **left OPEN** because the issue only requests the move.
3. **Upstream/PR activity.** Issue is `open` with zero comments; whether a competing PR already performs this move could not be verified (network blocked). Remains a prerequisite/open item.
4. **Doc/comment inconsistency (pre-existing, out of scope):** `tests_using_tokio_runtime.rs` L29 says the tests "are tagged as 'manual'", but BUILD's `com-api-example-tokio-integration-test` has no `tags = ["manual"]`. Only the path string is updated; the tagging claim is not silently "fixed".

## 8. Issue acceptance → artifact → check mapping

| Issue acceptance | Changed artifact | Required check (native label, post-move) |
| --- | --- | --- |
| Example no longer lives under `score/mw/com/example/` | git removals of the 13 old paths; empty `example/` gone | `query` `//score/mw/com/doc/tutorial/com-api-example:all` resolves; old label `//score/mw/com/example/com-api-example:all` no longer resolves |
| Example now under `score/mw/com/doc/tutorial/` | 13 files at new path | `build` `//score/mw/com/doc/tutorial/com-api-example:com-api-example` (+ lib/gen) |
| BUILD labels valid | updated `deps`/env in the moved `BUILD` | `build` + `query` above |
| Docs/usage references valid | `USAGE.md`, `main.rs`, `tests_using_tokio_runtime.rs` path strings | `docs` `//docs/sphinx:sphinx_doc`, `//score/mw/com/doc/tutorial:tutorial_rst` |
| Example still runnable/tested on Linux | unchanged sources + configs | `test` `//score/mw/com/doc/tutorial/com-api-example:com-api-example-tokio-integration-test` |
| Rust API lint/policy preserved | moved Rust sources | `lint` (clippy/format) per check-plan |
| Requirements/architecture unaffected | no req/design/safety artifact touched | rationale in §6; applicability confirmation stays reviewable |

## 9. Evidence status

- Required artifacts written: `.rust-queue/reports/scope.md`, `.rust-queue/reports/check-plan.json`, `.rust-queue/reports/review-packet.md`.
- `native-check-summary.json` was **not present** in `.rust-queue/reports/` at write time. It is the reserved location for deterministic native results; no native run was executed or fabricated by this agent.
- No source-tree edit was possible within the boundary; the implementation is delivered as the exact draft in §4 for a deterministic command stage to apply.

## 10. Next action

1. Deterministic stage applies §4 (rename 13 files, apply the 6 listed edit groups) on the baseline, then re-runs `git status`/`bazel query` to confirm the old package is gone.
2. Run the checks in `check-plan.json` on Linux (`config=linux_x64`); write results to `.rust-queue/reports/native-check-summary.json`.
3. Human reviewers resolve §7.1–§7.3 offline. Until then this is **technically drafted, acceptance pending** — not accepted engineering, not qualified/released.
