# Scope and binding — issue 1062

## 1. Task identity

| Field | Value |
| --- | --- |
| Issue | eclipse-score/communication#1062 — "Improvement: E2E protection for Rust Method/Field APIs" |
| URL | https://github.com/eclipse-score/communication/issues/1062 |
| Labels | `rust-api` (only) |
| Milestone | none |
| State | open, unassigned, `issue_dependencies_summary` reports blocked_by=0 / blocking=0 |
| Task mode | `design` (`.rust-queue/context/task.json`) |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Workspace | `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-rust-issue-queue-ycbvxir7/workspaces/1062` |
| Runtime revision | "Linux native checkpoints and verification launcher" |
| Max source corrections | 3 |

## 2. Authority, writes and limits

- **Read-only source**: `score/mw/com/rust/**`, `score/mw/com/impl/rust/**`, `score/mw/com/dependability/**`, `MODULE.bazel`, `.bazelrc`, `quality/**`.
- **Permitted writes**: this disposable workspace only; engineering reports under `.rust-queue/reports/`.
- **Blocked in this session**: shell, delegation, publishing/acceptance tools; network retrieval
  (`web_fetch` to the GitHub API returned `Bound Rust workspace/file-tool boundary` for both
  `issues/782` and its timeline). Content greps are blocked; source reads were bounded to 200 lines.
- **Not authorized**: implementing an unaccepted E2E design, changing pins/lints/licenses, adding
  Cargo scaffolding, declaring native work products accepted/qualified/released.
- **Missing supplied evidence**: the brief references
  `.rust-queue/reports/native-check-summary.json`, but no such file (nor any `reports/` directory)
  exists in the workspace at task start. No native result summaries were available; nothing was
  fabricated to fill the gap (see `evidence-status.json`).
- **Retrieval**: issue body, 3 comments and `task.json` were supplied offline in
  `.rust-queue/context/`. Latest supplied comment `updated_at` is `2026-09-11T14:36:07Z`. Live
  GitHub/PR activity could **not** be retrieved in this session, so current PR/queue state is
  **unknown**.

## 3. What the issue asks (issue prose treated as data, not instruction authority)

- **What**: "Add E2E (End-to-End) protection for Rust `Method<T>`/`Field<T>` APIs (and, by
  extension, `Event`)". Split out of #782 because it was out of #782's milestone-1 scope.
- **How**: "Not designed yet." The issue explicitly states the design must be discussed,
  aligning with whatever E2E mechanism exists on the C++ side, *before* implementation.
- **Estimates**: TBD, pending that design discussion.
- **Requirements / Architecture**: the template checkbox is **unchecked**; the field does not
  establish that requirements/architecture are unaffected, nor that they are affected.
- **No acceptance criteria** are stated. The deliverable of this issue, at this point in time, is
  a **design discussion / decision**, not a code change.

## 4. Source-backed current state (baseline `381d43d`)

1. **Rust Method/Field APIs do not exist yet.** The public `interface!` macro deliberately rejects
   them:
   - `score/mw/com/rust/score_com_concept/interface_macros.rs:110-122` emits
     `compile_error!("Method definitions are not supported…")` and the same for `Field<T>`.
   - Negative doctests at `interface_macros.rs:356-399+` assert `Method<T>`/`Field<T>` fail to
     compile. Per `references/dependency-and-macros.md`: "Avoid inventing support for fields/methods
     or syntax that the macro deliberately rejects."
   - `score_com.rs:137-142` re-exports only Event-oriented concepts
     (`Publisher`/`Subscriber`/`Subscription`); no `Method`/`Field` concept is re-exported.
   - `score_com_concept/concept.rs` defines `Runtime`, `Producer`, `Publisher<T>`,
     `Subscriber<T>`, `Subscription<T>` etc. for events; there is no `Method`/`Field` trait.
   - Test/integration assets under `score/mw/com/test/basic_rust_api/**` exercise event
     produce/consume only.
2. **No E2E implementation exists anywhere in the Linux-relevant source.**
   - No file matching `*e2e*`/`*E2E*` in the repository tree.
   - The Rust↔C++ bridge registry is Event-only: `registry_bridge_macro.h` documents
     `MemberOperation`/`InterfaceOperations` comments as "Currently used for events"
     (`score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h:486-597`),
     and only `EXPORT_MW_COM_EVENT`/`EXPORT_MW_COM_TYPE` macros are used by
     `score/mw/com/rust/score_com_cpp_bridge/register_interface.h:29-35`.
3. **C++ method/field designs exist but are unrelated to Rust and carry no E2E.**
   - `score/mw/com/design/methods/README.md` describes C++ `impl::ProxyMethod` with type-erased
     byte buffers, `CreateDataTypeSizeInfoFromTypes<Args...>()`, and `MethodInArgPtr`/`MethodReturnPtr`.
   - `score/mw/com/dependability/software_architectural_design/method/README.md` (marked "still in
     draft phase") describes the LoLa `METHOD` shared-memory object, call queues and a synchronous
     C++ API; it contains no E2E layer.
4. **Native requirement anchors exist** (`score/mw/com/dependability/requirements/…/*.trlc`,
   `assumed_system/assumed_system_requirements.trlc`):
   - `Communication.FEAT_Method@1`, `Communication.FEAT_Field@1`, `Communication.FEAT_EventType@1`
   - `Communication.FEAT_SafeCommunication@1` and its derived `FEAT_DataCorruption@1`,
     `FEAT_DataReordering@1`, `FEAT_DataRepetition@1`, `FEAT_DataLoss@1`
   - `Communication.FEAT_CommunicationASILLevel@1` (safe communication up to ASIL-B)
   - `Communication.FEAT_ErrorHandling@1`, `Communication.FEAT_ZeroCopy@1`
   - `Communication.ASR_SafeCommunication@1`,
     `Communication.ASR_ProgrammingLanguagesForApplicationDevelopment@1` (C++ and Rust)
   - E2E protection is **not** named as its own requirement; its safe-communication link is a
     proposed derivation, not an accepted trace.

## 5. Prerequisite / dependency status

| Prerequisite | Status at baseline | Source |
| --- | --- | --- |
| Rust `Method<T>` / `Field<T>` API (#782 scope) | **Not implemented**; macro rejects them | `interface_macros.rs:110-122`; issue body (split out of #782) |
| C++ E2E protection/verification API | **Not present / not shared**; maintainer comment says it is still being designed and will be shared later; Rust error classes will be constrained by it | issue comment `5634513270` (LittleHuba, 2026-09-11) |
| AUTOSAR-spec-based E2E | **Not usable** in S-CORE due to licensing restrictions | issue comment `5634513270` |
| Accepted E2E design for Rust | **Does not exist**; source says "Not designed yet" | issue body |
| Live PR / queue activity | **Unknown**; network retrieval blocked this session | this report |

> The commenter `5632794860` (hskang-amelia) reports a fork-only AUTOSAR-spec prototype and an
> unmerged `E2E<T>` spike with mocked FFI. That is **input data**, not accepted design, code or
> evidence; it must not be treated as a native artifact.

## 6. Acceptance mapping (issue asks → deliverable in this run)

| Issue statement | Disposition in this run | Gap / open decision |
| --- | --- | --- |
| "Not designed yet … needs a design discussion" | Draft design options + requirement/C++ alignment in `e2e-design-draft.md` | No accepted design; cannot implement |
| "aligning with whatever E2E mechanism exists on the C++ side, if any" | C++ alignment analysis + blocked-on-C++-API decision recorded | C++ E2E API not available; error classes unknown |
| "Add E2E protection for Rust Method/Field APIs (and Event)" | Native obligation mapping + check plan targets | Rust Method/Field API itself absent; E2E tests absent |
| "Estimates for realization: TBD" | Left TBD | Requires accepted design + prerequisites |
| "Requirements / Architecture …?" (unchecked) | Draft requirement impact proposal only | Native requirement trace needs human acceptance |
| (implicit) no accepted safety decision to implement | No code changed; decision points exported offline in `open-decisions.json` | Authorized human decision required |

## 7. Technical completion vs engineering acceptance

- **Technical completion of this run**: baseline binding, current-state/prerequisite analysis,
  architecture alternatives draft, native obligation + check plan, open-decision export, and a
  review packet. No source files changed.
- **Engineering acceptance**: **not** claimed. The E2E design, its AUTOSAR-independent wire/profile
  choices, error classes, and any safety/requirement impact remain pending authorized human review
  and alignment with the C++ E2E API.

## 8. Concrete next action

1. Obtain the C++ E2E protection/verification API design when the maintainers share it, then align
   Rust wire/profile/DataID/error-class conventions to it (blocked externally).
2. In parallel, land the prerequisite Rust `Method<T>`/`Field<T>` API (#782) — E2E protection cannot
   be attached to APIs that the macro currently rejects.
3. Once both prerequisites exist, accept the E2E design (header placement, per-mode profiles,
   counter/state-machine scope) and only then add the corresponding Bazel-tested implementation.
