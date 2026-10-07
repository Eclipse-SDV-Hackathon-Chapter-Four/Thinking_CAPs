# Example: communication #1265

Use this as a source-bound discovery/acceptance guide, not an implemented fix or accepted
dependency decision. Re-fetch issue/PR activity and select the actual task baseline first.

[Issue #1265](https://github.com/eclipse-score/communication/issues/1265) requests assessment
of identifier-pasting in the Rust COM interface macros, including dependency qualification
and generated API compatibility. Its inspected state on 2026-10-05 is open.

## Baseline reconciliation

Communication `main` inspected at `e3d126c2d7569345cf5f790310702eb00cd86b06` already uses
`score_com::pastey::paste!` in `score_com_concept/interface_macros.rs`; its BUILD dependency
is `@score_communication_crate_index//:pastey`. MODULE resolves that index through
`score_crates` 0.0.11. The individual crate's resolved version/features and qualification
have not been established by this workflow-authoring task.

Do not substitute `paste` for the observed dependency or claim the issue is solved from
this observation. Determine whether assessment of current `pastey`, history of the
migration, or another selected baseline is needed. Missing historical evidence remains
missing. A code migration may already exist while the required assessment is incomplete.

## Acceptance-to-artifact mapping

| Issue acceptance area | Evidence to collect | Native/draft output |
| --- | --- | --- |
| Dependency pin/features and exact macro usage | Resolved crate index/lock/BUILD/features, invocations, aliases and paste-pattern locations | Baseline/dependency/usage inventory |
| Provenance, license, maintenance and safety relevance | Verified source/checksums/notices, dated maintainer/advisory observations, generator and generated-code failure analysis | Dependency assessment and traced applicability proposal |
| Retain, replace or internal approach | Bounded functionality and comparison across compatibility, maintainability, qualification and verification effort | Proposed detailed-design/dependency decision |
| Qualification artifacts and replacement validation | Applicable native templates/obligations, expected-check inventory, actual old/new downstream API checks or an evidenced no-replacement rationale | Draft qualification records and verification report; offline decisions pending |

Discover exact native instance IDs in the selected project; the labels in this table are
output purposes, not invented S-CORE identifiers. The issue's requirement/architecture
checkbox is not evidence that those artifacts are unaffected.

## Observed macro surface

At this revision, paste operations generate interface, consumer, producer and offered
producer type names. `interface!` supports default/custom interface IDs and a legacy
comma form. It explicitly rejects Method/Field forms. These observations guide scope;
enumerate the full selected source and its consumers before deciding regression cases.
Getter/setter names mentioned by the issue require a source search: do not report them
as observed paste patterns without matching locations.

Test compatibility through `score_com` public re-exports with the actual native compiler,
including generated types/traits, ID constants, representative event types and downstream
producer/consumer use. Discover negative-test support for the rejected forms. Enumerate
the manual macro doctest separately and preserve its documented linking limitation.
Linux results cannot satisfy QNX checks; record this operator's unavailable license and
native test restrictions. Keep acceptance pending even if every executed Linux check passes.

## Example invocation

```text
Use $score-rust-workflow to assess eclipse-score/communication issue #1265.
Pin the selected source and reconcile its dependency with the issue wording.
Prepare the dependency/qualification assessment, option comparison, verification
plan and offline review packet in a storage-bound disposable workspace. Implement
only changes authorized by the issue-solving task; keep acceptance decisions pending.
```

During skill authoring only read-only source discovery was performed. No native build,
crate suitability/qualification decision, issue closure or upstream write occurred.

## Source anchors

- [Macro source](https://github.com/eclipse-score/communication/blob/e3d126c2d7569345cf5f790310702eb00cd86b06/score/mw/com/rust/score_com_concept/interface_macros.rs).
- [Macro dependencies and tests](https://github.com/eclipse-score/communication/blob/e3d126c2d7569345cf5f790310702eb00cd86b06/score/mw/com/rust/score_com_concept/BUILD).
- [Crate-index module pin](https://github.com/eclipse-score/communication/blob/e3d126c2d7569345cf5f790310702eb00cd86b06/MODULE.bazel).
