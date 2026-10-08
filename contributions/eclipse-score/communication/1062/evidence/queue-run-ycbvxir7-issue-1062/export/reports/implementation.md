# Implementation report — issue 1062

**Issue:** eclipse-score/communication#1062 — *Improvement: E2E protection for Rust Method/Field APIs*
**Mode:** `design` (`.rust-queue/context/task.json`)
**Baseline:** `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
**Platform/config:** Linux only (`--config=linux_x64`, i.e. `linux_x64_gcc_15`)
**Model:** DeepSeek Flash
**Status:** technical deliverable complete; **engineering/safety acceptance NOT claimed**

> This stage deliberately changed **no source file**. The issue states "Not designed yet" and that
> the design must be discussed, aligned with the C++ side, **before** implementation. Writing E2E
> code now would be an unaccepted architecture/safety decision. The required deliverable is therefore
> the dependency/design assessment plus an offline export of the open decisions.

## 1. Actual changed paths

Source tree: **unchanged** (no `score/mw/com/**` edits).

Reports written by this stage (all under `.rust-queue/reports/`):

| Path | Action | Notes |
| --- | --- | --- |
| `.rust-queue/reports/implementation.md` | created | this report |
| `.rust-queue/reports/open-decisions.json` | created / re-exported | OD-1..OD-8; proposal only |

Reports carried unchanged from the scope stage (verified readable this stage):

| Path | Role |
| --- | --- |
| `.rust-queue/reports/scope.md` | scope & binding |
| `.rust-queue/reports/e2e-design-draft.md` | architecture alternatives / requirements / C++ alignment |
| `.rust-queue/reports/check-plan.json` | Linux collector check plan (schema-valid) |
| `.rust-queue/reports/review-packet.md` | offline review packet |

Not written by this stage: any native work product, `native-check-summary.json`, or collector raw
evidence (command stages and raw evidence are outside agent authority).

## 2. Premise check (issue prose treated as data)

- The issue title/premise ("E2E protection for Rust `Method<T>`/`Field<T>` APIs") does **not** match an
  existing baseline surface: neither an E2E mechanism nor Rust `Method`/`Field` APIs exist.
- The Rust `interface!` macro **rejects** methods and fields by design, so E2E cannot attach to them
  yet. This is a hard prerequisite, not an oversight.
- Maintainer comment `5634513270` states the C++ E2E protection/verification API is still being
  designed and will be shared later, that Rust must derive its API from it, and that direct use of the
  AUTOSAR E2E specification is **licence-restricted** in S-CORE.
- Therefore the only issue-scoped action available to an agent is a **design/assessment** deliverable;
  the referenced fork prototype (`5632794860`) is input data, not accepted design/evidence.

## 3. Baseline facts re-verified this stage (bounded reads)

| Claim | Source re-read | Result |
| --- | --- | --- |
| `interface!` rejects `Method<T>`/`Field<T>` | `score/mw/com/rust/score_com_concept/interface_macros.rs:110-122` | confirmed — `compile_error!` for both arms |
| Public re-exports are Event-only | `score/mw/com/rust/score_com.rs:137-142` | confirmed — `Publisher/Subscriber/Subscription/...` only |
| Traits are Event-oriented | `score/mw/com/rust/score_com_concept/concept.rs:89-134` | confirmed — `Runtime::Subscriber`/`Publisher`, no Method/Field trait |
| C++ Method type-erasure / zero-copy | `score/mw/com/design/methods/README.md:74-86` | confirmed — `CreateDataTypeSizeInfoFromTypes<Args...>()`, per-call fixed-size in-arg/return buffers, no E2E layer |
| Feature requirement IDs exist | `score/mw/com/dependability/requirements/feature_requirements/feature_requirements_ipc.trlc` | confirmed — `FEAT_EventType/Method/Field/SafeCommunication/DataCorruption/DataReordering/DataRepetition/DataLoss/ZeroCopy`, ASIL-B where relevant |
| Pins | `MODULE.bazel`, `.bazelrc` | confirmed — `rules_rust 0.68.2-score`, `score_crates 0.0.11`, GCC 15.2.0, `linux_x64`→`linux_x64_gcc_15`, Ferrocene x86_64 linux gnu, clippy aspect `...%clippy_strict` |

## 4. Dependency and macro assessment (`interface!` macro + FFI bridge)

- **Macro contract:** `interface!` supports only `Event<T>`; `Method<T>`/`Field<T>` arms emit
  `compile_error!`. Per `references/dependency-and-macros.md`, support for the deliberately-rejected
  syntax must **not** be invented. Any E2E design that presumes `Method<T>`/`Field<T>` in `interface!`
  is blocked on #782.
- **Generated API surface:** `interface_common!`/`interface_consumer!`/`interface_producer!` generate
  `*Interface/*Consumer/*Producer/*OfferedProducer` via `pastey`; no method/field arm exists to extend.
- **FFI bridge:** `//score/mw/com/rust/score_com_cpp_bridge:register_interface` exposes only
  Event-oriented registration; new export macros would be required for any Method/Field/E2E binding.
  This is the C++-facing alignment point.
- **Failure modes to guard once code exists:** wrong/missing E2E members; type/trait mismatch;
  buffer size/layout drift between Rust layout code and C++ `CreateDataTypeSizeInfoFromTypes`; error
  class divergence from C++.
- **Option comparison (no decision taken):**

| Option | Compatibility/build impact | Provenance/licence | Qualification effort | Disposition |
| --- | --- | --- | --- | --- |
| Retain current API | no break; no E2E | existing Apache-2.0 | new E2E checks needed | insufficient for issue goal alone |
| Adopt/replace with C++-aligned mechanism | depends on C++ buffer/error contract | maintainer-provided, licence-clean | joint Rust/C++ verification | **recommended direction, blocked (OD-4)** |
| Implement internally | bounded to accepted design only | must avoid AUTOSAR-spec licence conflict | full new qualification burden | not viable until design accepted (OD-8) |

## 5. Requirements and native C++ alignment (draft, needs native acceptance)

- E2E protection is **not** its own named requirement. A proposed (not accepted) derivation:
  `FEAT_SafeCommunication@1` (+ `FEAT_CommunicationASILLevel@1`) for safe communication, and
  `FEAT_DataCorruption@1`/`FEAT_DataReordering@1`/`FEAT_DataRepetition@1`/`FEAT_DataLoss@1` for the
  detection classes; `FEAT_Method@1`/`FEAT_Field@1`/`FEAT_EventType@1` for the communication elements.
  Whether new requirement work products are needed is OD-7.
- **C++ alignment is blocked/unknown:** `score/mw/com/design/methods/README.md` and
  `dependability/software_architectural_design/method/README.md` contain **no E2E layer**; the C++
  E2E API, its error classes, profile names and `DataID` conventions are unknown at this baseline.
- **Known Rust-side constraint:** for `Method<T>` the in-arg/return buffers are fixed-size and
  pre-computed by C++, so a Rust-only E2E header is impossible — the size computation must change in
  lockstep on both sides. This is why OD-1/OD-2 cannot be settled by the Rust side alone.

Architecture alternatives A/B/C and the Event-first staging question are recorded in
`e2e-design-draft.md` §4; the choices are exported as OD-1..OD-3.

## 6. Verification, regression and consumer coverage

- No code changed, so no new regression case is warranted **this stage**; adding an E2E test would
  presuppose an unaccepted design. The negative compile-fail doctests that assert `Method<T>`/`Field<T>`
  rejection must **remain** until #782 lands.
- The Linux check plan is `check-plan.json` (collector schema `{checks:[{kind,targets,reason,native_obligation,config}]}`,
  `config = linux_x64`). Every target label was re-checked against real `BUILD` files this stage:

| Check kind | Target(s) (BUILD-derived) |
| --- | --- |
| build | `//score/mw/com/rust/score_com_concept:score_com_concept` |
| build | `//score/mw/com/rust:score_com`, `//score/mw/com/rust:score_com_mock` |
| build | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola`, `.../com-api-ffi-lola:bridge_ffi_rs`, `.../com-api-ffi-lola:bridge_ffi_lola` |
| build | `//score/mw/com/rust/score_com_cpp_bridge:register_interface` |
| test | `//score/mw/com/rust/score_com_concept:score_com_concept-test`, `...:score_com_concept-macros-unit-tests` |
| test | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-tests` |
| test | `//score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test:test_com_api_sync`, `.../consumer_async_apis/integration_test:test_com_api_async` |
| docs | `//score/mw/com/impl/rust/com-api/com-api-runtime-lola:com-api-runtime-lola-doc-tests`, `...:score_com_concept-macros-tests` (`manual`) |
| docs | `//docs/sphinx:sphinx_doc` |
| lint | the three Rust targets above under the pinned `clippy_strict` aspect |
| query | `//score/mw/com/rust:score_com`, `//score/mw/com/rust/score_com_concept:score_com_concept` |

- **Explicit unknown:** there is no Rust `Method`/`Field` E2E test target, because no Rust
  `Method`/`Field` API or BUILD target exists. It is recorded as unknown rather than fabricated.

## 7. Evidence status (preserved, not filled)

- **Missing supplied evidence:** `.rust-queue/reports/native-check-summary.json` is **absent** at this
  stage (glob finds no such file). It is preserved as missing; nothing is fabricated to replace it.
- **No checks executed this stage** — shell/execution is blocked and command stages/raw evidence are
  outside agent authority. All check-plan rows are *planned*, not results.
- **File hashes not computable** in-session (shell blocked).
- **Live GitHub/PR state unknown** — network retrieval blocked; only the offline
  `.rust-queue/context/` snapshot and the workspace reports are authoritative here.
- A prior `.rust-queue/reports/evidence-status.json` exists and is preserved untouched; this stage did
  not re-read it (file-tool boundary), and did not overwrite it.

## 8. Unresolved concerns

1. No accepted E2E design exists; every architecture choice is open (OD-1..OD-3, OD-8).
2. The C++ E2E protection/verification API and its error classes are unpublished (OD-4, OD-5).
3. The Rust `Method<T>`/`Field<T>` API is absent; the macro rejects it (OD-6).
4. Requirement/architecture applicability is undecided (OD-7).
5. Licence constraint forbids contributing an AUTOSAR-spec-derived implementation (OD-8).
6. `Method<T>` buffer-size lockstep between Rust and C++ is a hard cross-language design constraint.
7. No native E2E verification evidence can exist until the design and prerequisites land.

## 9. Technical completion vs engineering acceptance

- **Technical completion:** baseline binding, premise/current-state verification, dependency/macro
  assessment, requirements/C++ alignment draft, alternatives, schema-valid check plan, offline
  decision export and review packet. No source change.
- **Engineering acceptance:** **not claimed.** The E2E design, wire/profile choices, error classes,
  staging and any requirement/safety impact remain pending authorized human review and the C++
  API. Tests/passing checks cannot supply that decision.

## 10. Concrete next action

1. Obtain the C++ E2E protection/verification API; align Rust wire/profile/`DataID`/error-class
   conventions to it (OD-4, OD-5) — blocked externally.
2. Land the Rust `Method<T>`/`Field<T>` API (#782) (OD-6).
3. Accept the E2E design (OD-1..OD-3, OD-7, OD-8), then implement and run the checks in
   `check-plan.json`, adding native E2E regression/consumer cases for corruption/reordering/
   repetition/loss.
