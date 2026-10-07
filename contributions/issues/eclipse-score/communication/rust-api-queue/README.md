# Communication Rust API queue: shared records

Queue-wide evidence for the 13 `rust-api` issues processed on communication baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e`. QNX #1278 was excluded. Per-issue folders sit next to
this one; #1265 keeps its earlier, separately registered folder.

| Issue | Folder | Branch | State |
| --- | --- | --- | --- |
| #1261 async stream of new services | [1261](../1261/README.md) | `feature/1261-async-service-stream` | Linux checks pass; D1/D6 await maintainers |
| #250 `FindServiceSpecifier::Any` | [250](../250/README.md) | `feature/250-find-service-any` | Linux checks pass |
| #560 subscription state APIs | [560](../560/README.md) | `feature/560-subscription-state-apis` | Linux checks pass |
| #781 `MethodInArgPtr` | [781](../781/README.md) | `draft/781-method-in-arg-ptr` | Draft; ABI/ownership open |
| #490 mock runtime | [490](../490/README.md) | `draft/490-mock-runtime` | Draft; unverified |
| #173 external crates | [173](../173/README.md) | none | Assessment refreshed |
| #1264 `thiserror` | [1264](../1264/README.md) | none | Assessment |
| #1263 `futures` | [1263](../1263/README.md) | none | Assessment |
| #794 manual tags | [794](../794/README.md) | none | Handled upstream by the maintainer |
| #782 method runtime | [782](../782/README.md) | none | Assessment; another contributor active |
| #1062 E2E for methods/fields | [1062](../1062/README.md) | none | Design assessment; upstream C++ design first |
| #741 move example | [741](../741/README.md) | none | Not implemented |
| #1265 `paste` | [1265](../1265/README.md) | earlier record | Assessment (separate record) |

Branches live in the working clone `/home/jefferson/eclipse-score/communication`, and each branch
folder also has a portable `.bundle`. **Nothing has been pushed or submitted.** Each branch merges
cleanly into upstream `main` on its own. The #1261, #250 and #560 branches conflict with each other
(FFI bridge files, `consumer.rs`, `score_com.rs`), and #560 conflicts with the #490 draft (mock
runtime), so rebase whichever merges later.

## Contents of `evidence/`

- `score-rust-issue-queue-ycbvxir7`: queue definition (models, budgets, selection).
- `score-rust-issue-queue-ycbvxir7-linux-execution`: launch records.
- `queue-results-ycbvxir7-top-level`: queue results, verification audit and operator findings.
  This includes the duplicate `clippy_strict` launcher defect that made many lint checks fail.
  Its manifest also lists `issues/<n>/…` entries; those files are stored in the per-issue folders.
- `queue-run-ycbvxir7-issue-1265`: the queue run for #1265.
- `score-rust-claude-independent-review-20261007`: the all-issue status review.

Event streams are stored as `.zst`; see [compressed-evidence.json](compressed-evidence.json).
`artifact-manifest.json` seals this folder.
