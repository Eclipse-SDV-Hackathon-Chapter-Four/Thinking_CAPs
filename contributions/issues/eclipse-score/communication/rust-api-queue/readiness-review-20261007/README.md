# Communication #1261, #250 and #560: readiness review

This packet addresses the inventory gap “Scope/ABI/warning resolution, applicable
checks, human/IP review.” It contains warning and native-formatting corrections, an explicit scope and
compatibility disposition, native requirement anchors, verification evidence and
an offline decision record. Engineering acceptance remains pending.

[MERGE-ARTIFACTS.md](MERGE-ARTIFACTS.md) answers whether the issues are completely
fixed and maps the live protected merge gates to available and missing artifacts.
The answer is **not yet**; local selected checks do not establish merge readiness.

The source baseline is `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. The request in
this session authorizes this follow-up; historical correction ledgers and sealed
packets remain unchanged. Work uses new disposable copies on a bound external SSD.
The reference repository, original patches and portable branches are preserved.
Supplemental patches apply on top of the original per-issue patch; `candidate.patch`
files apply directly to the baseline with `git apply`. They are separate proposals,
and the original branch bundles do not contain these corrections.

## Measured results

| Issue | Evidence binding | Passing child cases | Ignored | Selected Clippy findings |
| --- | --- | ---: | ---: | --- |
| #1261 | Fresh final candidate; serialized integrations | 105 | 2 | 3 inherited warnings; stream warning removed |
| #250 | Unchanged source; 2,883 hashes match carried measurements | 68 | 2 | 3 inherited warnings and 1 new Any API warning |
| #560 | Fresh final candidate; serialized integrations | 26 | 0 | 3 inherited warnings; application warnings removed |

Both corrected Rust files pass the maintained native formatting check. Native
crate-based test Clippy targets produce noop placeholders, so cfg(test) analysis
remains unresolved. With the separately bound checker-path companion, every
candidate and the baseline have the same 204 copyright findings, with no new or
removed findings. These are selected results, not full merge-gate satisfaction.

## Scope and API/ABI disposition

| Issue | Implemented contract | Proposed disposition | Remaining decision |
| --- | --- | --- | --- |
| #1261 | An infinite, heterogeneous stream over LoLa service types in the configuration loaded when the stream opens. Concrete provider instances can be absent from the consumer manifest. Pending identities coalesce and withdrawal removes unpolled items. | Retain the documented configured-universe contract. Do not claim discovery of unconfigured types or other bindings. | Maintainer D1: whether this satisfies “system-wide,” or requires a separate native enumeration design. D6: whether callback heap allocation is permitted in the operating phase. |
| #250 | Typed `Any` finds instances of one registered interface. Synchronous no-offer returns an empty result. The async operation is one-shot, takes the latest stored snapshot, and can remain pending until an offer arrives. | Keep typed `Any` and heterogeneous discovery as distinct API contracts, with #1261 carrying the latter proposal. This is partial fulfillment of the issue author's broader follow-up. | Maintainer agreement to that split; external implementation/source compatibility and fallible selector/error contract. |
| #560 | State queries and subscription-state handler registration/unset for Rust proxy events, with LoLa and mock implementations. | Preserve the existing state mapping, replacement, handler-false and drop behavior. The warning correction changes only test instrumentation and parity spelling. | Native event-contract trace, registration/unset failures, callback concurrency and FFI ownership review. |

The #250 maintainer comment confirms native LoLa any-semantics; the issue author's
follow-up asks for all services. It does not establish maintainer agreement to
system-wide Rust semantics. Current read-only issue observations are in `inputs/`.

#1261 adds a virtual method at the end of `IRuntime`. Appending preserves earlier
slots but **does not preserve binary compatibility with old implementers**. The
recorded local D4 acceptance already permits appending and documenting that break;
native upstream acceptance is still unknown. The proposal requires rebuilding
implementers and callers from matching headers. Do not mix prebuilt old providers
with new callers. If upstream requires binary compatibility, redesign the enumeration
extension before adoption; the current proposal is not suitable for that requirement.

All three extend Rust traits/FFI surfaces. Adding mandatory methods can break
out-of-tree implementations; #250 also changes builder internals. Selected repository
tests prove only their exercised consumers. New C functions do not establish
whole-library ABI compatibility. These branches overlap and need conflict resolution
and fresh checks when combined or rebased. No combined/current-main claim is made.

## Native trace and verification applicability

Native inputs are retained under `inputs/native-context/`, at the baseline above.
The following are source-discovered anchors, not accepted Rust compliance mappings:

| Issue criterion | Native anchor | Changed surface / check | Applicability gap |
| --- | --- | --- | --- |
| #1261 availability and existing scoped discovery; #250 Any | `Communication.FEAT_ServiceDiscovery@1`, `Communication.ASR_InterProcessCommunication@1`, `Communication.ASR_SafeCommunication@1` (feature TRLC `derived_from` direction is preserved) | Runtime, discovery bridge, Rust traits; runtime/concept units, Any/stream and existing sync/async integrations | Scope, version/quality selection and accepted requirement-to-Rust mapping remain open. The referenced ASRs are links in the inspected TRLC, not independently reviewed assumptions here. |
| Stop/cancel discovery | `Communication.ProxyStopFindService@1`; native service-discovery design's callback/stop contract | Native stop guards, stream drop and cancellation cases | Find-service callback-box reclamation remains baseline-wide; Weak ownership mitigates retention without reclaiming the closure. No exhaustive callback quiescence proof. |
| #560 query / register / unset | `Communication.ProxyEventGetSubscriptionState@1`, `Communication.ProxyEventSetSubscriptionStateChangeHandler@1`, `Communication.ProxyEventUnsetSubscriptionStateChangeHandler@1` | Concept/consumer/FFI; five production scenarios and helper cleanup tests | TRLC declares version 1 and ASIL-B; register/unset include “potentially uncovered” notes. No valid/accepted status or adopted Rust safety profile is inferred. Rust unset's fallible contract needs explicit reconciliation with native C++ `void` semantics. |

The native TRLC declarations have versions and safety fields but no acceptance
status in these blocks. No requirement IDs, statuses, tailoring decisions or
qualification evidence are invented. The full expected-check inventory, measured
results and omissions are in [verification.json](verification.json).

Native `CI.md` and workflows require more than the selected Linux checks: whole
host build/tests, module integration, formatting, Clippy, C++ analysis, sanitizer
jobs and applicable platform/integration variants. QNX licensing/targets, complete
reverse dependencies, ignored manual doctest examples, tool qualification and
coverage applicability must be resolved explicitly. They remain open where unmeasured.

## Warning disposition

The #1261 corrective patch gives the callback conversion an explicit `FatPtr`
destination before creating `FindServiceCallable`. It preserves the boxed callback
representation and ownership limitation; annotation alone is not an FFI soundness
proof. The #560 patch removes the unused per-observation invocation number while
retaining the atomic invocation count used by assertions, and uses
`is_multiple_of(2)` with the selected native compiler. Both corrected files are formatted with the
maintained policy wrapper. Failed pre-format checks and interrupted collection
attempts remain visible alongside the final source-bound measurements.

Inherited warnings stay visible: callback conversion and clone-on-Copy in the
existing consumer, the existing FFI `Result<_, ()>` API, C++ deprecated enum values
and launcher/configuration warnings. #250 additionally introduces another
`Result<_, ()>` warning on its Any bridge method. A typed bridge error should be
designed with the existing Specific API before adoption; no suppression or accepted
exception is supplied by this packet. The explicit crate-based test-target aspect commands create empty noop reports;
they do not establish cfg(test) analysis. That native tool-support gap remains open.
Exact fresh/carried analyzer outcomes are in
`verification.json`. Exit zero never means warning-free analysis.

## Human and IP review

[HUMAN-REVIEW.md](HUMAN-REVIEW.md) gives concrete decisions and required subject
bindings. All decisions are pending unless an existing historical decision is
explicitly referenced. Native `CONTRIBUTING.md` requires an ECA. The declared
Eclipse account's successful official lookup from #1167 is carried in `inputs/`,
with a fresh username lookup recorded separately. This does not validate the
original patches' `jnsagai <jnsagai@gmail.com>` author identity, account linkage or
every contributor's rights. Original author,
license and notice records remain intact. AI-origin disclosure is retained; neither
copyright checks nor an agent review attest ownership, ECA or IP clearance.

No publication, push, GitHub comment, PR, merge or issue closure is authorized by
this packet. Native CODEOWNERS identify review candidates, not authenticated
signatories or completed engineering approval.

## Reproduce and verify

Run `python3 verify.py` from this directory to check the packet and its referenced
original evidence hashes. Native source/tool/environment manifests, exact command
logs and test payloads describe the measurements independently of Fabro. The run
uses a private rootless Docker daemon and read-only host tools with recorded Ubuntu
library overlays. That environment is a scoped compatibility setup, not the full
supported-host CI or a qualified toolchain. Owned runtime shutdown is recorded.

The concrete next action is for the native scope/API owners to decide the listed
contracts and ABI migration, the verification owner to resolve the unrun inventory,
and the contributor/committer to complete ECA/IP and subject-bound engineering review.
