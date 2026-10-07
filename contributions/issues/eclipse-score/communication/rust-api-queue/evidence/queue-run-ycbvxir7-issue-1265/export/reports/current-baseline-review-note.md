# Current-baseline review note — communication #1265

Agent-authored note. It records how historical evidence is carried onto the current task
baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. It grants no qualification and no
acceptance; it changes no native ID, status or UID.

## Subjects and comparison method

The offline engineering review was measured at `8368bfb5b182ae6642d963b58ad4bac5dabc02c3`
(integration) and `e3d126c2d7569345cf5f790310702eb00cd86b06` (original assessment / Rust
unit+doctest). The current task baseline is `381d43de…`. Because shell/collector tools are
outside agent authority here, the agent performed a **content-level** comparison of the
current source against the recorded static facts; it could not recompute SHA-256. Fresh
hash measurement is delegated to the Linux collector through `check-plan.json`.

| Recorded static subject | Recorded at review | Agent content check at `381d43de` | Disposition |
| --- | --- | --- | --- |
| `interface_macros.rs` — 4 `paste!` blocks at lines 134/146/163/195; 22 occurrences of `[<$id Interface>]`(6) `[<$id Consumer>]`(5) `[<$id Producer>]`(7) `[<$id OfferedProducer>]`(4) | `sha256 0e45ce44…` | Matches line-for-line at the same source lines and occurrence indices | Carried as content-verified; **hash re-measurement pending** |
| `score_com_concept/lib.rs` — `#[doc(hidden)] pub use pastey;` | `sha256 1defeaf3…` | Re-export present; `mod interface_macros` present | Carried as content-verified; hash pending |
| `score_com_concept/BUILD` — `proc_macro_deps` includes `@score_communication_crate_index//:pastey`; Linux-only `score_com_concept-test`; manual `score_com_concept-macros-tests` | `sha256 5feb1d24…` | Matches | Carried as content-verified; hash pending |
| `score/mw/com/rust/BUILD` / `score_com.rs` — public re-export crate; forwards `pastey` | `sha256 a602e3fc…` / `dee9ecb8…` | `pub use score_com_concept::pastey;` with the #173 comment present | Carried as content-verified; hash pending |
| `MODULE.bazel` / `MODULE.bazel.lock` — `score_crates` 0.0.11 as `score_communication_crate_index` | `sha256 35b34ba4…` / `aaff7681…` | `bazel_dep(name = "score_crates", version = "0.0.11", repo_name = "score_communication_crate_index")` present | Carried as content-verified; hash pending |

No current-baseline path was recorded as differing or missing in the historical
`current_static_subjects` block; this note neither confirms nor refutes that at `381d43de`
by hash. Anyone relying on the carried facts after a fresh collector run must bind the
collector's recomputed hashes.

## Carried native results (historical, not promoted)

- **Six Linux integration cases at `8368bfb5`** — `consumer_sync_apis/integration_test:test_com_api_sync`
  (3 passed) and `consumer_async_apis/integration_test:test_com_api_async` (3 passed), zero
  failures/errors/skips, cached results disabled in that execution. XML hashes
  `f94164a2…` and `b8ad40c9…`. These remain **carried evidence**; the task envelope sets
  `native_results_promoted_to_current_baseline: false`.
- **33 passed / two ignored Rust unit+doctest cases at `e3d126c2`** — historical only.

The `check-plan.json` targets are the current-baseline subjects proposed for fresh Linux
measurement; running them does not retroactively promote the historical results, and would
start a new measurement on `381d43de` rather than resume the exhausted `8368bfb5` run.

## Budget and run-state

The inherited native run already consumed **three of three** corrective fixes (remaining 0).
This note does not reset that budget and does not rerun that run. There is no active native
run. QNX is excluded from this Linux-only task.

## Pending offline acceptance

The retained decision remains a **proposal** (retain locked `pastey 0.2.3`). R1–R6 gaps,
the compiler-certificate/use-scope package, the Accepted component change request, the
communication adoption/safety-plan records, the current-baseline copyright disposition and
the tool-management applicability determination all remain open for authorized humans. No
qualification, certification or acceptance is asserted here.
