# Communication #781: offline engineering review

## Scope and binding

Issue: [#781](https://github.com/eclipse-score/communication/issues/781); original brief and retrieval time in [context/issue-781.json](context/issue-781.json). The issue remained open with zero comments at capture. Original draft base `381d43dec900ab6a9076f3f30e7bfbdee019e26e` is historical; the candidate is based on current main `c77751819b8885a902540dbef7f0fe25cf85d51c`, commit `d39eb127221538d623a3ddb4c8b519396a0528b1`, tree `e4f9e21d8a618b3f751a88c00a6509dea8100333`, branch `feature/781-method-in-arg-ptr-ownership`. See [candidate/source-binding.json](candidate/source-binding.json).

The user's requested engineering follow-up authorizes source fixes, native disposable builds and local contribution artifacts. This is a direct Codex follow-up, not a resumption of exhausted historical Fabro correction loops. No paid calls, subagents or external publication occurred. Reference repositories, active queues and global caches were preserved. Environment/storage identity and exact commands are retained under execution/ and checks/. Technical completion covers the stated issue scope and selected Linux checks; native human acceptance remains pending offline.

## Acceptance and engineering trace

| Issue criterion | Native obligation/artifact and revision | Changed artifact | Check | Evidence | Disposition |
| --- | --- | --- | --- | --- | --- |
| Create ABI type like SamplePtr | Communication.FEAT_SupportForProgrammingLanguageIdioms@1 and FEAT_UseProgrammingLanguageInfrastructure@1 (QM; both derived_from ASR_ProgrammingLanguagesForApplicationDevelopment@1); native MethodInArgPtr C++ header | Rust repr(C), private fields, lifetime marker, Bazel library | Size/alignment on int32/UserType; C++ member representation | final native unit logs | Proposal measured on Linux x86_64; other ABIs unmeasured |
| Resolve ownership | Native methods design and method_signature_element_ptr.h | Exclusive borrows, move-only owner, Drop clears activity only | C++ moved-from destruction while destination alive; Rust move/reassignment; compile-fail lifetime/alias/Send/Sync docs | final unit/doc logs | No safe duplicate owner; no by-value extern C bridge |
| Preserve method argument identity | Communication.MethodInArgPtrMatches@1 (ASIL B); root_causes links preserved to mw_com_fta.BlocksOnCaller, CallBlocksOnCallee, CallBlocksOnUserHandler | Building block only; no caller/callee bridge | C++ representation probe; future method end-to-end checks | final logs, native AoU source | AoU is not discharged here. #782 method runtime and #1062 integration remain separate work |

Native requirement IDs, versions, safety classifications and derived_from/root_causes directions above are copied from the selected baseline. The supplied TRLC records do not contain an acceptance status to inherit. Their contents/statuses are unchanged. No new native requirement ID, approved safety finding, released work product or qualified compiler instance was invented. [native-context](native-context/) contains the source-bound contribution, design, requirements, AoU and testing guidance. Rust packages here use rust_test/rust_doc_test and expose no component coverage lock; this packet's trace is a proposal, not native CompReq or certified coverage evidence. Maintainers must decide any additional native integration/qualification work before acceptance.

## Design, ownership and failure analysis

The owner stores T*, bool* and usize in repr(C), matching the actual C++ `{T*, bool&, size_t}` representation observed on Linux x86_64. PhantomData has zero size and tracks exclusive borrows of both referents. Constructor marks active; Rust move transfers the sole drop obligation; Drop clears active and does not destroy/free T. Fields are private, with no Clone/Copy or unsafe Send/Sync implementation. The only production unsafe operation dereferences the live exclusively borrowed bool in Drop, with its invariant documented.

C++ MethodInArgPtr is non-trivial. A layout match is not permission to pass it by value through extern C or fabricate a C++ object in Rust storage. Native test support reads object bytes using memcpy into a representation record and operates on a separately constructed C++ object. The input pointer, flag pointer and queue position are checked, including the moved-from destructor running before destruction of the destination. A future method bridge must use explicit pointer-based construction/move/destruction and preserve referent lifetimes. There is no method IPC implementation in this change.

A leaked/forgotten Rust owner keeps the activity flag set (ordinary RAII limitation). Panic unwinding runs Drop; abort/leak does not provide cleanup guarantees. This building block is not a safety acceptance or caller/callee identity proof.

## Dependencies and generated APIs

No dependency, toolchain pin, macro implementation, MODULE.bazel or MODULE.bazel.lock changed. Native Rust policies are score_rust_policies 0.0.5 and score_toolchains_rust 0.10.0. Measured compiler is rustc 1.94.0-nightly (779fbed05, Ferrocene rolling, LLVM 21.1.5), host/target x86_64-unknown-linux-gnu; GCC 15.2.0 and Bazel 8.7.0 are bound by versions/hashes. The compiler brand/strict policy does not prove qualification for this version, target or use.

This ABI addition retains the existing native C++ helper and Rust macro/test dependencies; no new third-party library or runtime ownership abstraction is proposed. Native adjacent SamplePtr and SampleAllocateePtr tests run with the changed helper. Dependency replacement/internalization would add unrelated compatibility and qualification scope and is not proposed.

No fresh dated dependency-advisory clearance or qualification classification is claimed. Separate dependency assessments remain applicable. Existing Apache-2.0 source notices are preserved; the new Rust source has the 2026 notice. Provenance records retain the historical AI drafts and this Codex follow-up; actual commit author identity is in the patch and must satisfy ECA.

## Verification and expected checks

5 explicitly selected native test targets passed, 40 cases passed, 0 ignored, zero failed. The doc tests contain one runnable example and five compile-fail ownership/lifetime cases. Clippy passed for the selected library/helper targets; captured aspect output files are empty and native SARIF/report files are retained. Native Rust, C++ (where changed) and BUILD formatting checks passed.

[verification-summary.json](verification-summary.json) links target counts and logs. [expected-checks.json](expected-checks.json) inventories passing, failed, ignored, unrun and remote checks. [checks/final/](checks/final/) contains exact command/environment, input hashes, full logs, test XML and BEP; [checks/lint-verified/](checks/lint-verified/) contains the lint inputs/logs/reports. Final source bytes match both passing test and Clippy manifests; no source drift occurred during either check. These are directly executed local native results, not independent CI/collector acceptance. The original launcher duplicate-aspect problem was avoided by using --config=clippy once, without an explicit duplicate aspect.

Earlier attempts are retained under checks/ with their source manifests and actual exit codes. Old baseline passes are superseded by the passing current-main final group; initial cast and missing-symbol failures were corrected.

Unrun: full //... tests, repository-wide copyright/format checks, official GCC15/QCC, sanitizers, clang-tidy, Clippy/ruff CI statuses and review-checklists. The changed sources have native formatting checks; no repo-wide gate is implied. QNX Rust tests are Linux-only at this baseline per #1278, and other ABI/platform behavior is unmeasured. See [merge-readiness.md](merge-readiness.md) for actual branch rules and pending gates.

## Offline decisions and portable evidence

Proposed decision: Approve the Linux x86_64 representation, exclusive borrowed input/flag lifecycle and pointer-only future FFI boundary. Confirm applicability of MethodInArgPtrMatches@1 to subsequent method integration. Code owners and authorized engineering/safety/qualification reviewers decide applicability and acceptance. Tests do not close MethodInArgPtrMatches, establish release readiness or approve these decisions.

The candidate patch/bundle, changed source and source binding are under candidate/. The portable bundle requires the selected baseline to exist in the recipient clone; [reproduce.md](reproduce.md) supplies setup/check commands. The packet manifest seals all contained files, including historical root records and raw evidence; the contribution folder's manifest additionally seals the current top-level PR artifacts and preserved historical evidence. No credentials are included.

Next action: perform offline review, confirm ECA, publish the reviewed revision as a draft native PR, then obtain the exact required CI/review/merge-queue gates. Any rebase/source edit invalidates this evidence until applicable checks are rerun and bindings resealed.
