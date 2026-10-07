# Implementation — Issue #741: Move the Rust COM API example to the tutorial folder

Status: **NOT APPLIED — boundary-blocked assessment / change specification.**
Technical completion: change fully specified, not executable with the granted file tools.
Engineering acceptance: **pending** (no authorized human decision; no native evidence).
This report is written inside the disposable workspace only; it is not a published or accepted change.

## 1. Binding

| Field | Value |
| --- | --- |
| Issue / repo | `eclipse-score/communication` #741, state at snapshot `open`, label `rust-api`, 0 comments |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Mode | `implementation` (`task.json`) |
| Platform / model | Linux only (`linux_x64`); DeepSeek Flash |
| Artifact destination | `.rust-queue/reports/**` (reports) — see §6 for probe artifacts left in the source tree |
| Retrieval | 2026-10-06; live GitHub PR/timeline and `web_fetch` **unavailable** (blocked) |

## 2. Baseline reconciliation (is it already moved?)

**No.** At `381d43d` the Rust example still lives in `score/mw/com/example/com-api-example/`
(13 files). `score/mw/com/doc/tutorial/` contains only `BUILD`, `README.rst` and the C++
`chapter_1..chapter_13` packages; there is no `com-api-example` package there.
`score/mw/com/example/` has no BUILD of its own, so after the move it becomes empty and is removed.

Moved set (13 files), source → destination (replacing the prefix
`score/mw/com/example/com-api-example/` with `score/mw/com/doc/tutorial/com-api-example/`):

```
BUILD
USAGE.md
main.rs
tests_using_tokio_runtime.rs
src/lib.rs
src/consumer.rs
src/producer.rs
com-api-gen/BUILD
com-api-gen/com_api_gen.rs
com-api-gen/vehicle_gen.cpp
com-api-gen/vehicle_gen.h
etc/logging.json
etc/mw_com_config.json
```

Licenses/notices inside each file (Apache-2.0 headers, `NOTICE`) are preserved byte-for-byte by a
rename; no content is authored or removed.

## 3. Why the move was not applied within this boundary (measured)

The implementation agent probed the actual tool boundary (evidence recorded here, not fabricated):

1. **No delete/rename primitive.** The granted file tools are read/write/edit/glob only. `write_file`
   creates and overwrites; writing empty content leaves a zero-byte file in place (verified by
   `glob`/`read_file`). There is no tool that removes or renames a path, and `shell` is blocked
   (every shell invocation returns `Bound Rust workspace/file-tool boundary`, including `pwd`).
   A concatenation-avoiding move that leaves the source package behind would keep the old
   `//score/mw/com/example/com-api-example:*` targets alive and duplicate the package — a regression,
   not a move.
2. **Source data files cannot be read.** `read_file` on any `score/**/*.json` — including
   `score/mw/com/example/com-api-example/etc/logging.json` and `etc/mw_com_config.json`, and even
   unrelated tutorial chapter configs — returns the boundary denial. `grep`, `web_fetch` and `.git`
   reads are blocked too. Consequently the two `etc/*.json` files cannot be copied byte-for-byte by
   re-authoring them. (`scope.md` §5 recorded the same shell/grep/`web_fetch` boundary from the scope
   stage; this stage additionally measured that source writes are permitted but deletion is not.)
3. **Consequence.** A faithful move requires (a) removing the 13 source paths and (b) carrying the
   two JSON configs verbatim. Neither (a) nor (b) is possible with the granted tools. Creating the 11
   readable files at the new path would additionally produce a *broken* package (its `BUILD` `data`,
   `env` and Rust sources reference `etc/*.json` that would be missing), so it would break
   `//...` builds while leaving the old package intact. Therefore no duplicate tree was created.

This is a genuine tooling limitation, reported as a gap; it is **not** a claim that the change is
undesirable or already done.

## 4. Exact change specification (for the deterministic command stage)

### 4.1 Renames — content preserved byte-for-byte

Apply the 13 source→destination renames listed in §2. Recommended mechanism: `git mv` (records
renames) or equivalent, then remove the now-empty `score/mw/com/example/` directory.
The deterministic stage must **overwrite/remove the probe placeholder**
`score/mw/com/doc/tutorial/com-api-example/BUILD` before or while placing the moved `BUILD`.

### 4.2 Reference edits required after the rename

Only path/native-label strings that name the moved location change. No Rust/C++ logic changes.

**`score/mw/com/doc/tutorial/com-api-example/BUILD`** (3 labels + 1 env path):

| Line (source numbering) | From | To |
| --- | --- | --- |
| 22 (`com-api-example-lib` deps) | `"//score/mw/com/example/com-api-example/com-api-gen",` | `"//score/mw/com/doc/tutorial/com-api-example/com-api-gen",` |
| 38 (`com-api-example` `env`) | `"score/mw/com/example/com-api-example/etc/logging.json"` | `"score/mw/com/doc/tutorial/com-api-example/etc/logging.json"` |
| 43 (`com-api-example` deps) | `"//score/mw/com/example/com-api-example/com-api-gen",` | `"//score/mw/com/doc/tutorial/com-api-example/com-api-gen",` |
| 69 (`com-api-example-tokio-integration-test` deps) | `"//score/mw/com/example/com-api-example/com-api-gen",` | `"//score/mw/com/doc/tutorial/com-api-example/com-api-gen",` |

**`main.rs`** (clap default, line 72):

```
default_value = "./score/mw/com/example/com-api-example/etc/mw_com_config.json"
→
default_value = "./score/mw/com/doc/tutorial/com-api-example/etc/mw_com_config.json"
```

**`tests_using_tokio_runtime.rs`**:

- line 26 doc comment:
  `bazel test //score/mw/com/example/com-api-example:com-api-example-tokio-integration-test`
  → `bazel test //score/mw/com/doc/tutorial/com-api-example:com-api-example-tokio-integration-test`
- line 44 `TEST_CONFIG_PATH`:
  `"./score/mw/com/example/com-api-example/etc/mw_com_config.json"`
  → `"./score/mw/com/doc/tutorial/com-api-example/etc/mw_com_config.json"`

**`USAGE.md`**:

- Replace `score/mw/com/example/com-api-example` with `score/mw/com/doc/tutorial/com-api-example`
  on lines 55, 67, 74, 77, 80, 83, 86, 89, 104, 107, 111 (11 occurrences).
- Rebase the relative link on line 124 for the deeper location:
  `../../impl/rust/com-api/README.md` → `../../../impl/rust/com-api/README.md`.
  (The target `score/mw/com/impl/rust/com-api/README.md` does not exist at this baseline — a
  pre-existing dangling link. Its relative base is corrected; the link is not "fixed" by inventing a file.)

### 4.3 Files needing no content change

- `com-api-gen/BUILD`: `visibility = ["//score/mw/com:__subpackages__"]` still matches the new path;
  deps are absolute.
- `com-api-gen/com_api_gen.rs`, `com-api-gen/vehicle_gen.cpp`, `com-api-gen/vehicle_gen.h`,
  `src/*.rs`, `etc/*.json`: no path references. The C include guard
  `SCORE_MW_COM_EXAMPLE_COM_API_EXAMPLE_VEHICLE_DATATYPE_H` is a cosmetic identifier and is left
  unchanged (minimal, behavior-preserving). `crate_name = "com_api_gen"` is unchanged, so the
  auto-generated `Exhaust` ID `com_api_gen::Exhaust` is unaffected.
- `score/mw/com/doc/tutorial/BUILD`: does not reference the example; `tutorial_rst`/`tutorial_samples`
  list only chapter packages, so it is not automatically changed (docs registration stays OPEN — §7.2).

## 5. Effect / safety reconciliation (unchanged from scope assessment)

- The change is location-only plus self-referential path strings. Observable producer/consumer
  behavior, CLI defaults, config discovery and the Linux-only Tokio test are preserved.
- No requirement, architecture, design, safety, API-surface, lock, pin or toolchain artifact is
  touched. No MISRA-C++ policy is transferred to Rust. Native IDs: none sourced inside the example
  package; remaining **unknown** rather than invented.
- `MW_LOG_CONFIG_FILE` and the config default are workspace-relative paths; with `bazel run` the
  working directory is the workspace root, so both must name the new location (handled in §4.2).

## 6. Actual changed paths in this workspace

Only boundary-probe artifacts were created; no deliverable source change was applied
(see §3). These two paths are **not** part of the intended change and must be removed by the
deterministic command stage (the agent cannot delete files):

| Path | What it is | Required action |
| --- | --- | --- |
| `score/mw/com/doc/tutorial/com-api-example/BUILD` | comment-only placeholder package created to probe source writes; defines no targets | remove/replace when applying §4 |
| `.rust-queue/reports/boundary-test.txt` | probe file proving empty write does not delete | remove |

No other source path was modified; the old example tree is byte-identical to baseline.

## 7. Unresolved concerns / open items (do not self-accept)

1. **Target leaf name.** `com-api-example` was kept (minimal change). No native source states an
   intended Rust-specific name; maintainer confirmation required.
2. **Docs registration OPEN.** The moved `USAGE.md` is not in any `sphinx_docs_library`; whether the
   Rust sample becomes rendered tutorial documentation (and how the docs `prefix` is handled) is a
   documentation-design decision the issue does not make.
3. **Competing upstream work unverifiable** (network blocked). Whether a PR already performs the move
   could not be checked.
4. **Pre-existing doc/comment inconsistencies** (out of scope, not silently fixed):
   `tests_using_tokio_runtime.rs` L29 claims the tests are tagged `manual`, but the BUILD target has
   no `manual` tag; the `USAGE.md` L124 link target is absent.
5. **Boundary limitation.** No delete/rename tool and no source `.json` reads mean the move cannot be
   completed by this agent; the deterministic command stage (or an extended boundary) is required.

## 8. Next action

1. Deterministic stage applies §4 (13 renames + the edits in §4.2), removes the probe artifacts in §6,
   then asserts the old label `//score/mw/com/example/com-api-example:all` no longer resolves.
2. Run the checks in `.rust-queue/reports/check-plan.json` on Linux (`config=linux_x64`) and write
   `.rust-queue/reports/native-check-summary.json`.
3. Human reviewers decide §7.1–§7.4 offline. Acceptance remains **pending**; no qualification/release
   claim is made.

## 9. Evidence status

- `native-check-summary.json` is **absent** (no native command was executed by this agent; command
  stages are outside agent authority). Recorded as missing evidence, not back-filled.
- `check-plan.json` remains valid: all targets are the post-move, BUILD-derived labels; no QNX target.
- Probe denials (`Bound Rust workspace/file-tool boundary`) were observed directly for: all `shell`
  invocations, all `grep`, `web_fetch`, `.git` reads, and `read_file` of source `.json` files.
