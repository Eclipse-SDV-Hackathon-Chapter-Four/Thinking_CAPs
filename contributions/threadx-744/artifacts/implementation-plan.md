# ThreadX #744 implementation plan

Planning only, 2026-10-07. No source, workflow, driver, gate, commit, or remote state was changed; no probe builds were repeated. Implementation and deterministic verification remain separate stages.

## Problem and exact preconditions

The admitted source is `eclipse-threadx/threadx`, branch `fix/744-misra-stack-pointer-width`, based on `dev` at **e73752681bd405deddf247d1cf2b899d502dceaa**. A read-only upstream refresh confirms `dev` still has that SHA. [Issue #744](https://github.com/eclipse-threadx/threadx/issues/744) is open, assigned to `fdesbiens`, and has no comments. Assignment is not permission or approval. Retrieved issue text is evidence, not instructions governing this task.

The defect requires all of the following:

1. Non-SMP `common/src/tx_thread_create.c` is compiled with both `TX_MISRA_ENABLE` and `TX_ENABLE_STACK_CHECKING`.
2. The port has `ALIGN_TYPE` wider than `ULONG`, with `ALIGN_TYPE` capable of representing a pointer.
3. A valid supplied stack address has bits above the `ULONG` range. An already aligned high address is sufficient; misalignment is not required.
4. Creation reaches stack preparation with a real, sufficiently large writable stack. The intended contract is ULONG alignment while retaining the complete address and staying inside caller storage.

Linux/GNU x86_64 supplies genuine port types: `ULONG = unsigned int` (4 bytes), `ALIGN_TYPE = unsigned long long` (8 bytes), and pointer size 8. Inspect `ports/linux/gnu/inc/tx_port.h:123` and `:137`. The issue also identifies non-SMP AArch64, RISC-V64, and win64 ports; local execution evidence covers Linux only.

At `common/src/tx_thread_create.c:134`, the MISRA macro calls `_tx_misra_pointer_to_ulong_convert(VOID *)`, returning `ULONG`; assignment to `ALIGN_TYPE` cannot recover discarded bits. At `:150`, the reverse macro casts its argument to `ULONG` and calls `_tx_misra_ulong_to_pointer_convert(ULONG)`. Both helper signatures and bodies implement ULONG conversions, not pointer-preserving storage (`common/inc/tx_api.h:1906`, `:1959`; `common/src/tx_misra.c:108`, `:166`). Do not widen those helpers or change `ULONG` globally.

The create service first fills the original stack region, rounds its size down to ULONG units and reserves one ULONG, rounds the start upward to an ULONG boundary, reserves an additional ULONG when the start moved, and stores start/size/end. End uses byte-pointer helpers rather than the ULONG integer conversion. It then calls the port stack builder and sets `tx_thread_stack_highest_ptr` to the returned stack pointer. The Linux builder computes an aligned fake stack pointer from the stored end and dereferences the word below it (`ports/linux/gnu/src/tx_thread_stack_build.c:125`); corrupt creation metadata therefore becomes a real invalid access. The `_txe_thread_create` wrapper checks arguments but does not repair the narrowed address.

## Equivalents, dependencies, and supersession

The refreshed issue, comments, issue timeline, all-state PR searches for `744`, `MISRA`, `stack`, and `stack pointer truncat`, and refreshed PR #742 are saved in `planner-upstream-refresh.json`. Earlier detailed linked-issue/PR evidence is in `planner-upstream-snapshot.json` (2026-10-07 12:49:52 UTC). The refresh began at 13:04:07 UTC. No superseding #744 implementation was found within these searches; this is an evidence-bounded finding, not a guarantee about unlinked private work. The timeline contains assignment only. Search hit #597 concerns AArch64 build scripts and is unnecessary for this correction.

[PR #742](https://github.com/eclipse-threadx/threadx/pull/742), merged at **b93d1ee92ff2c3e720d6ed2c5dd7eaf3bdd7e8e2**, is an ancestor of the admitted base. It fixed six missing-macro sites, including simulator stack builders, `common_smp/src/tx_thread_create.c`, and module-manager creation. Its description explicitly excludes #744. It is an already merged build prerequisite for the full native MISRA simulator probe, not a patch to redo.

SMP creation now uses full-width inline casts at `common_smp/src/tx_thread_create.c:135` and `:147`, with alignment arithmetic in `ALIGN_TYPE`. Its helper contracts remain ULONG-based where explicitly named that way. Native Linux SMP is LP64: its `ULONG` is `unsigned long`, and default `ALIGN_TYPE` is `ULONG`; it does not reproduce the non-SMP Linux width mismatch. SMP needs compatibility checks, not a production edit for #744. The issue body's SMP compile-failure claim predates #742.

Module-manager creation also has #742's casts, but still narrows `new_stack_start` to `ULONG` in its alignment expression at `common_modules/module_manager/src/txm_module_manager_thread_create.c:298`. That is a distinct defect, including outside MISRA mode, explicitly excluded by #742. Keep it outside #744. The manager also documents different module/kernel stack-checking behavior at `:330`.

PR #747 added two MISRA configurations but intentionally left #744 unresolved. PRs #746, #749, and #751 fix trace declarations, Linux trace timestamps, and SMP shim diagnostics respectively. PRs #705, #727, #666, and #732 address simulator fake-stack alignment, stack-analysis bounds, existing misaligned-stack coverage, and random fill preservation. They are already merged context, not new work or outstanding dependencies. Their SHAs and base ancestry are recorded in `dependencies.json` and existing ancestry evidence.

[PR #105](https://github.com/eclipse-threadx/threadx/pull/105) proposed removing an ULONG cast from alignment arithmetic, not the two MISRA conversions. Upstream reports it closed and unmerged; its returned candidate SHA is absent from this checkout. Current single-core alignment arithmetic already lacks that cast. Do not describe #105 as merged or superseding #744.

#741 is closed by #742. #532 is closed umbrella context. Its linked #587/#628 compatibility layers, #771/#772 callback APIs, and #767 clock facility are unnecessary prerequisites. Changing callbacks, trace storage, global type widths, module-manager arithmetic, or clocks would fold unrelated work into this fix. Documentation PR rtos-docs-asciidoc#79 is already merged type-width context, not evidence that #744's documentation requirement is met. See `dependencies.json` for individual classifications, URLs, and available SHAs.

## Existing native evidence, reused

Read `native-planner-probe/stack_create_probe.c`, its `CMakeLists.txt`, and every `run-*.log`. The probe links the real ThreadX library and real MISRA shim, uses supported `TX_TIMER_PROCESS_IN_ISR` to avoid timer-thread creation before logging, and wraps `_tx_thread_stack_build` only to log before calling the real implementation. It checks creation metadata, a scalar callback argument, initial stack bounds, and real worker sleep/wake/completion. It asserts the width mismatch and a real high address. No kernel stubs are involved in this existing probe.

| Existing run | Observation |
| --- | --- |
| `run-red-aligned.log` | Both flags: `0x6386b48ba080` becomes `0xb48ba080`; builder receives size 8188 and truncated end `0xb48bc07b`; exit -11 (SIGSEGV). |
| `run-red-misaligned.log` | Both flags: `0x5f12f33ec081` should become `0x5f12f33ec084`, but builder receives `0xf33ec084`, size 8184; exit -11. |
| `run-control-aligned.log`, `run-control-misaligned.log` | MISRA disabled, stack checking enabled: correct full-width start/end and sizes 8188/8184; real creation and sleep/wake pass, exit 0. |
| `run-no-check-aligned.log`, `run-no-check-misaligned.log` | MISRA enabled, stack checking disabled: shim diagnostic still shows a lossy ULONG round trip, but creation keeps the supplied pointer and size 8192; scheduling passes, exit 0. |

All logs report widths 4/8/8 and actual addresses above `0xffffffff`. This isolates the faulty combination. These controls are not green evidence for a fixed tree. `gdb-red.log` reports ptrace prohibited and no stack/registers; do not claim a debugger backtrace. Builds were not repeated in this planning stage.

## Exact proposed files and smallest production change

Production edit: **`common/src/tx_thread_create.c` only**, replacing the two MISRA/non-MISRA conversion selections with the same form already used by SMP:

```c
    new_stack_start =  (ALIGN_TYPE) ((VOID *) stack_start);
    /* Existing alignment and size adjustment stay here.  */
    stack_start =  (VOID *) ((ALIGN_TYPE) updated_stack_start);
```

Remove both surrounding `TX_MISRA_ENABLE` conditionals. Preserve the alignment expression, guard reservations, fill order, and every other branch. Add a concise explicit pointer/integer conversion deviation comment naming MISRA C:2012 Rule 11.6 and applicable edition equivalents, explaining that the port-defined alignment type preserves the address. Formal MISRA analysis remains pending. Update function-header change history/version according to the actual upstream release convention; do not invent a release identifier. Preserve the existing copyright and single AI-disclosure line.

Proposed regression additions:

- `test/tx/cmake/thread_create_stack/CMakeLists.txt`: independent Linux/GNU native C99 project, CTest registration, genuine port includes, no inherited `-m32`.
- `test/tx/thread_create_stack/threadx_thread_create_stack_test.c`: behavioral metadata harness and small scheduler/port recorders.

No changes to `tx_api.h`, either `tx_misra.c`, SMP production sources, assembly shims, port types, or module manager are needed. Replacing the branches with the ALIGN_TYPE macros alone would not compile under MISRA: both macros exist only in the non-MISRA header branch. Adding new MISRA helpers would expand the patch into both headers, C shims, and assembly-shim obligations identified by #747; it is unnecessary.

CI integration is still required: the standalone directory is not reached by current workflows. The minimal proposed future integration is explicit native configure/build and CTest invocations from `scripts/build_tx.sh` and `scripts/test_tx.sh`, preserving existing suite execution, status propagation, serial timing, and coverage gates. Those two driver paths would be integration edits in the implementation stage, **not edits authorized or performed by this planning stage**. Keep workflows and gates unchanged. A reviewed integration must ensure `tx / run_tests` actually executes the native lane; a manually passing standalone CTest run cannot satisfy that requirement. If later-stage scope excludes driver edits too, carry this as an unresolved integration requirement rather than silently claiming CI coverage.

## Behavioral regression and expected red/green

Use the researched `regression-design.md` in the contribution folder as design evidence. Compile the actual create service and actual `common/src/tx_misra.c` with both flags and the Linux/GNU types. Use function/data sections and GNU linker garbage collection to exclude unused shim services, rather than replacing conversion helpers. `tx_misra.c` defines `TX_THREAD_INIT`; avoid duplicate globals, including in the non-MISRA control target. Standalone `thread_transition` and `module_manager` projects demonstrate the repository's recorder technique, but their existing shims are not substitutes for the real MISRA conversion implementation.

Call `_tx_thread_create` with `TX_DONT_START`. Stub only port/scheduler boundaries with exact upstream prototypes: `_tx_thread_stack_build`, interrupt disable/restore, preemption check/resume, shell entry, and timeout. The stack-builder recorder must never dereference or do pointer arithmetic on the possibly truncated metadata. It supplies a safe pointer derived from the original allocation, records start/end/size, and lets creation return so assertions expose the wrong values. Inspect any additional linker-required globals or boundaries rather than copying kernel algorithms. Leave event tracing and random fill disabled for this focused lane. On the old tree, even byte-pointer end calculation from a narrowed address is not a valid storage contract; this is a red behavioral test, not a sanitizer-clean baseline promise.

Allocate writable host storage with padding and ULONG alignment. Require native 64-bit pointers, `sizeof(ALIGN_TYPE) > sizeof(ULONG)`, adequate ALIGN_TYPE width, and actual input address above `(ULONG)~0`. Reject missing preconditions explicitly; a low address or 32-bit build must not pass as defect coverage. Use offsets `0 .. sizeof(ULONG)-1` and sizes 8192 and 8193, with all allocations comfortably above `TX_MINIMUM_STACK`. Compute expected alignment with remainder and byte offset, independently of the production mask.

For each case, assert:

- `TX_SUCCESS`, `TX_SUSPENDED`, `TX_THREAD_ID`, and retained scalar creation parameters.
- Stored and recorded start equals the first ULONG-aligned address at/after input, including every high address bit.
- Effective size equals `N - N % sizeof(ULONG) - sizeof(ULONG)`, subtracting one more ULONG if the start moved.
- End equals expected start plus effective size minus one, within caller storage; highest pointer equals the safe builder-supplied pointer.
- Initial fill covers the supplied region and padding sentinels remain unchanged; created-list count/links are valid, interrupt posture balances, and preemption disable returns to its initial value.

Maintain live control blocks for list checks or reset only harness-owned state between independent cases. Compare pointer equality or integer values in the pointer-capable type; avoid relational comparisons involving invalid/unrelated pointers.

Expected **red**: unchanged admitted base compiles, but the both-flags metadata test exits nonzero for every high-address case; do not accept only a source-string match or a compile failure. Existing full-simulator SIGSEGV evidence already establishes the runtime consequence. Expected **green**: the identical harness and expectations pass after only the two-conversion production correction. For 8192-byte input, aligned start reserves four bytes (8188 usable) and misaligned start reserves eight (8184 usable); 8193 rounds to the same effective sizes. A native non-MISRA stack-checking control also passes. A stack-checking-disabled MISRA control retains input start/size. Supplement fixed-tree metadata verification with the existing real Linux creation/sleep/wake probe in the verification stage; no new red probe build is needed now.

Preserve source SHA/diff, compiler versions, feature flags, widths, addresses, configure/build/CTest logs, exit codes, and test enumeration. Red and green must use identical test code and separate build directories. These deterministic results are planned, not yet demonstrated.

## Portability and feasible local checks

The casts rely on the existing port contract that ALIGN_TYPE can represent pointers. Pointer/integer conversion is implementation-defined C behavior requiring an explicit MISRA deviation; no claim of certification follows from a successful build. Preserve ULONG-sized stack guards and the power-of-two alignment assumption. Tiny invalid stacks, integer overflow at address-space limits, trace's intentional ULONG fields, callback pointer transport, and module-manager arithmetic require independent scope and evidence.

Existing `planner-tool-inventory.json`, `planner-create-compile-matrix.json`, `planner-m4-compile-matrix.json`, and `planner-smp-clang-compile-qualified.json` document feasible local checks: GCC 11.4 and clang 12 native builds, CMake 3.22/Ninja, and ARM GCC 10.3 Cortex-M4 compile checks. Create-service GCC configurations compile with all four feature combinations on both kernels; this does not detect #744. Clang SMP C99 `-Werror` initially fails on an existing repeated TX_THREAD typedef; the separately recorded `-Wno-typedef-redefinition` lane passes and must remain labeled qualified. No unrelated header fix belongs here.

`native-planner-probe/multilib.log` shows missing `bits/libc-header-start.h`, exit 1. Consequently current standard Linux `-m32` ThreadX, SMP, and FreeRTOS suites are unavailable locally without provisioning multilib. GCC 14 and gcovr 8.6 are absent (installed gcovr is 5.0); local versions cannot establish reference-toolchain or coverage-gate compliance. Missing: AArch64 GNU toolchain, Arm Toolchain for Embedded 22.1.0, both RISC-V cross compilers/QEMU targets, Cortex-R52 FVP, and Windows MSVC. ARM GCC 10.3 compile-only evidence is not ARM 14.3.rel1 qualification or target execution. Do not install toolchains or run the full suites during this planning stage.

Already recorded baseline checks in `planner-local-checks.json`: AI disclosure, `check_ports.sh --no-regen --quiet`, and `git diff --check` passed on the unchanged base. The no-regeneration port check is a subset of upstream regeneration checks. None establishes patched-tree acceptance. The later feasible subset is native deterministic red/green, fixed real simulator scheduling, GCC/clang feature matrix, Cortex-M4 compile matrix with installed toolchain, disclosure, no-regeneration port consistency, and diff checks. Record unavailable full checks as unavailable, never passed.

## Upstream PR requirements and outstanding evidence

Read repository `CONTRIBUTING.md`, `README.md`, `SECURITY.md`, PR template, all seven directly triggered workflows plus reusable regression template, and branch evidence `admission.json`/`upstream-rules.json`. Existing `process-audit.md` supplies policy research. No applicable AGENTS.md was found. README delegates contributions to CONTRIBUTING and describes library composition; SECURITY requires private reporting for newly discovered vulnerabilities. This plan does not infer exploitability or send reports.

Use a feature branch based on `dev`, target `dev`, and keep one logical #744 change. C99, surrounding style, no goto, no external dependencies, explicit MISRA deviations, appropriate headers, no new reference-toolchain warnings, and an actual regression are required. Commit/PR subjects start with a past-tense verb, at most 72 characters; commit bodies explain cause/fix/validation at 88-column wrapping; PR paragraphs use one physical line. Use actual tool/model identity in the `Assisted-by` trailer, preserve existing disclosure, and use the guide's new-file MIT/CC0 attribution. Human provenance review must actually happen before certifying it.

CONTRIBUTING's behavior-change criterion calls for a companion documentation PR in `rtos-docs-asciidoc`; plan a short #744-specific stack-pointer preservation/configuration clarification. Its URL/SHA do not yet exist. It is required future contribution work, not supplied by unrelated merged docs #79. No API/ABI signature or global type change is planned. The PR checklist requests function-header/version updates, a bug test, and real-hardware validation; only check items with evidence. Simulator scheduling is not hardware validation, and real hardware remains unavailable.

Observed dev ruleset [23985797](https://github.com/eclipse-threadx/threadx/rules/23985797) requires one approving review, code-owner review, and final-head statuses `eclipsefdn/eca`, `tx / run_tests`, `smp / run_tests`, `freertos / run_tests`, and `riscv / run_tests`. ECA lookup artifacts do not verify author-email match on a future final commit. Guide states matching ECA fulfills DCO sign-off; do not invent an additional DCO gate. No ECA, approval, coordination comment, or remote PR exists for this plan. The guide asks for an intent-to-work comment, but this session explicitly prohibits contact, so record coordination as outstanding without sending it.

Full applicable workflow checks for a `common/**` change:

| Workflow | Required execution/evidence |
| --- | --- |
| `regression_test.yml` / `regression_template.yml` | Unfiltered dev PR: ThreadX seven configurations, SMP five, FreeRTOS, RISC-V/QEMU. Build before test. TX/SMP merged nonempty line coverage >=99%; branch coverage reported, not gated. Include the native #744 lane via reviewed integration. |
| `gcc_check.yml` | Arm GNU 14.3.rel1 AArch32 and AArch64 assembly/C/examples and invalid R52 options. Build/link evidence, not runtime. |
| `clang_check.yml` | Arm Toolchain for Embedded 22.1.0 assembly/C/examples. Host clang 12 is not equivalent. |
| `ci_cortex_m.yml` | CMake/Ninja builds for Cortex-M0/M3/M4/M7 on Arm GNU 14.3.rel1. |
| `ports_arch_check.yml` | Both port consistency/regeneration jobs. No-regeneration local checks cover a subset. |
| `r52_fvp.yml` | R52 default/features image builds and FVP execution when repository model URL is configured. Unset model URL means execution skipped, even if green. |
| `repo_checks.yml` | Unfiltered repository AI-disclosure check. |

Reference commands are in `process-audit.md`: `CC=gcc-14 TX_COVERAGE=ON scripts/build_tx.sh` then `scripts/test_tx.sh` with the same environment; equivalent SMP pair; FreeRTOS build/test pair; RISC-V build/test pair; `check_gcc.sh` with both pinned cross-toolchains; `check_clang.sh` with ATfE; and repository/port checks. Keep timing-sensitive CTest and coverage serial, preserve first failures despite default `until-pass:2`, and use `CTEST_REPEAT_FAIL=1` for first-pass acceptance evidence. Do not modify retry policy or coverage thresholds.

Before any later readiness statement, refresh upstream issue/base state, final PR SHA, actual statuses, reviews and mergeability. All applicable CI, final-head ECA, human/code-owner approval, human provenance review, documentation work, and any required target-validation disclosure remain outstanding. Planning completion is not implementation completion or merge readiness.
