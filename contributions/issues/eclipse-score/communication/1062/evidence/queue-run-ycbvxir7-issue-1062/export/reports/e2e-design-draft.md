# E2E protection for Rust Method/Field/Event APIs — DRAFT design alternatives

> **Status: DRAFT / not an accepted design.** Issue #1062 states "Not designed yet"; the E2E
> mechanism and its safety implications require an authorized design discussion and alignment with
> the C++ side. Nothing here is a native artifact, requirement decision, or safety acceptance.
> All items marked *(open)* are exported in `open-decisions.json`.

## 1. Problem framing (source-backed)

The Rust COM API currently exposes only the **Event** publish/subscribe model
(`score/mw/com/rust/score_com_concept/concept.rs`, `interface_macros.rs`). `Method<T>`/`Field<T>`
are deliberately rejected by the `interface!` macro and are not public concepts. E2E
end-to-end protection — detecting corruption, reordering, repetition and loss between
communication partners — is not implemented anywhere in the Linux source tree, neither for the
existing Event path nor for the C++ method path.

Consequently, this issue is a **new feature design problem** with two hard prerequisites
(cf. `scope.md` §5):

1. the Rust `Method<T>`/`Field<T>` API must first exist (#782), and
2. the C++ E2E protection/verification API and its error classes must be available, because
   maintainers stated Rust's error classes "will be restricted to what C++ provides" and that the
   AUTOSAR specification **cannot** be used directly in S-CORE for licensing reasons
   (comment `5634513270`).

## 2. Proposed requirement derivation (draft, needs native acceptance)

E2E protection is not itself a named requirement in the baseline requirement set. The following is a
**proposed** derivation from existing native IDs — it must be reviewed, not assumed accepted:

| Proposed obligation | Native anchor (baseline) | Note |
| --- | --- | --- |
| Rust APIs shall support safe communication for Method, Field and Event | `Communication.FEAT_SafeCommunication@1`; `FEAT_Method@1`, `FEAT_Field@1`, `FEAT_EventType@1` | Safe-communication support up to ASIL-B: `FEAT_CommunicationASILLevel@1` |
| Detect/flag data corruption, reordering, repetition, loss | `FEAT_DataCorruption@1`, `FEAT_DataReordering@1`, `FEAT_DataRepetition@1`, `FEAT_DataLoss@1` | derived_from `ASR_SafeCommunication@1` |
| Error signalling via the S-CORE result mechanism (no exceptions) | `FEAT_ErrorHandling@1`, `ASR_ErrorHandling@1` | Rust side maps to `score_com::Error` and C++-provided classes |
| Zero-copy preservation for large in-args/return values | `FEAT_ZeroCopy@1`, `AllocateInArgsAndReturnValueInMemory` | constrains where an E2E header can live |
| Applicability to both C++ and Rust application developers | `ASR_ProgrammingLanguagesForApplicationDevelopment@1` | cross-language wire compatibility |

**Open**: whether any of the above must be created as new requirement work products, or whether
existing IDs suffice. This is a tailoring/requirements decision for authorized reviewers.

## 3. Native C++ alignment (blocked / unknown)

- `score/mw/com/design/methods/README.md` and
  `score/mw/com/dependability/software_architectural_design/method/README.md` define the C++
  `ProxyMethod` / LoLa `METHOD`-shared-memory model (synchronous call, type-erased byte buffers,
  `CreateDataTypeSizeInfoFromTypes<Args...>()`, `MethodInArgPtr`/`MethodReturnPtr`). **No E2E layer
  is present in either document.**
- The maintainer comment (`5634513270`) says an E2E protection/verification API for C++ is *being
  designed* and will be shared "within the near future", and that Rust must derive its API from it.
  The API, its error classes, wire format, profile names and `DataID` conventions are therefore
  **unknown at this baseline**.
- Anything claiming a specific profile (e.g. AUTOSAR `Profile 4m`, CRC-32/AUTOSAR check value
  `0x1697d06a`) originates from a fork prototype reported in comment `5632794860`; it is
  **not** accepted design and, per `5634513270`, direct AUTOSAR-spec use is license-restricted.

**Blocking dependency**: Rust E2E cannot be finalized until the C++ E2E API and error classes are
published. Until then the safe deliverable is design options + open decisions.

## 4. Architecture alternatives (draft)

### Alternative A — Transparent E2E in the Rust↔C++ FFI boundary (binding-owned buffer)
Mirror the classic "between RTE and network binding" pattern: the Rust runtime/bridge wraps the
user payload, and the C++ binding grows the buffer by the E2E header size so `interface!` users
never name `E2E<_>`.

- **Pros**: user-facing API unchanged; single place to configure; can share one mechanism across
  Method/Field/Event.
- **Cons**: requires lockstep buffer-size changes on both sides — C++
  `CreateDataTypeSizeInfoFromTypes` (per `comment 5632794860`) and the Rust `MethodArgs`-style
  `layout()` must grow together. For `Method<T>` the in-arg/return buffers are fixed-size and
  pre-computed, so a Rust-only change is impossible. Highest coupling to the unavailable C++ API.
- **Depends on**: C++ E2E API (open), Rust Method/Field API (missing).

### Alternative B — E2E carried as a field of the user's wire payload type
The E2E header is part of the serialized data type itself (as prototyped fork-only).

- **Pros**: no C++ buffer-size change needed; works with existing byte-buffer transport.
- **Cons**: contaminates the user's data contract (application sees the header); must be repeated
  for every communication mode; breaks the `CommData`/`ID` stability story; the C++ side still has
  to agree on the layout to interoperate.
- **Depends on**: accepted wire contract (open).

### Alternative C — Payload-level E2E applied independent of communication type
Per comment `5601398184`: implement at "the Rust API payload level … independent of the
communication type, whether it's an Event, Field, Method, or any other mode".

- **Pros**: one shared mechanism and one config schema sized for the widest field set (Method's
  `Xm`-style Message Type/Result/Source ID fields are strictly wider than Event/Field).
- **Cons**: "independent of communication type" must **not** be read as "identical wire format" —
  the Method-specific profile needs strictly more fields. Needs an accepted definition of the shared
  vs. mode-specific portion.
- **Depends on**: accepted design (open).

**Relationship to Event-first staging**: the maintainer recommends focusing on **Event mechanics
first, then Method** (`5634513270`). Alternatively, a single schema sized for Method from the start
avoids a later breaking change. This is an explicit open decision.

## 5. Cross-cutting design constraints to carry into any accepted design

- **FFI/buffer lockstep (Method)**: E2E header placement must keep C++ and Rust size/layout
  computations in agreement; a Rust-only header cannot be added to a fixed-size pre-computed
  Method buffer.
- **Error classes**: Rust E2E error variants must map to C++-provided classes; no independent Rust
  taxonomy may be invented (`5634513270`).
- **Scope of the state machine**: whether the provider-side "apply or reject the call based on E2E
  result" logic (counter-delta tolerance, consecutive-failure counting) is in the first increment,
  or the first pass is limited to CRC + `DataID` checking only (`5632794860`, question 4).
- **Licensing**: no AUTOSAR-spec-derived implementation may be contributed (`5634513270`).
- **Safety neutrality**: none of these choices may be presented as an accepted safety decision.

## 6. Verification implications (for the accepted design)

Any accepted design must extend, not replace, the existing native checks captured in
`check-plan.json`. The minimum future obligations are behavioural: a negative/positive E2E test that
demonstrates detection of corruption/reordering/repetition/loss and correct mapping to C++-provided
error classes, exercised for Event (existing API) and, once available, Method/Field. Until the Rust
Method/Field APIs exist, no Method/Field E2E check target can be named from a real `BUILD` file;
that target is recorded as an explicit unknown rather than fabricated.
