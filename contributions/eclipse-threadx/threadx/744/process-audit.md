# ThreadX #744 contribution process audit

Audited 2026-10-07 against upstream `dev` **e73752681bd405deddf247d1cf2b899d502dceaa** and `master` **93387b0a60382a29579bbad5045c68328e3751df**. Authoritative snapshots are in [evidence/upstream-process](evidence/upstream-process/). No `AGENTS.md` exists in the audited upstream tree. The authenticated account cannot bypass the rulesets; the legacy branch-protection endpoint returned HTTP 404, so the active rulesets are the observed branch requirements.

## Scope and dependencies

[#744](https://github.com/eclipse-threadx/threadx/issues/744) remains open, assigned to `fdesbiens`, with no issue comments at audit time. The single-core `common/src/tx_thread_create.c` still converts a stack pointer through `ULONG` under `TX_MISRA_ENABLE` plus `TX_ENABLE_STACK_CHECKING`. On Linux x86_64 the pointer and `ALIGN_TYPE` are 64 bits while `ULONG` is 32 bits. Preserve full pointer width in both conversion directions and test the actual thread creation behavior.

[#741](https://github.com/eclipse-threadx/threadx/issues/741) is closed and [PR #742](https://github.com/eclipse-threadx/threadx/pull/742) merged into `dev` on 2026-09-16 at **b93d1ee92ff2c3e720d6ed2c5dd7eaf3bdd7e8e2**. That PR fixed all six missing conversion-macro call sites, including SMP and module manager. Do not reimplement it. The module manager's separate `((ULONG) new_stack_start)` alignment truncation remains; #742 explicitly excluded it. Keep that independent defect outside this focused PR unless a separate regression and reviewable scope justify inclusion.

[#532](https://github.com/eclipse-threadx/threadx/issues/532) is a closed umbrella discussion linking #744, pointer callback APIs #771/#772, 64-bit clocks #767, and documentation work. These are context, not prerequisites for #744. No pending blocking dependency or existing #744 fix PR was found by the issue timeline and all-state PR search. Assignment is a coordination signal; upstream asks contributors to comment that they intend to work on an issue. Record coordination without assuming assignment proves another patch exists.

## Contribution requirements

The [current contribution guide](https://github.com/eclipse-threadx/threadx/blob/e73752681bd405deddf247d1cf2b899d502dceaa/CONTRIBUTING.md) requires a feature branch based on `dev` and a PR targeting `dev`; one logical change; C99; surrounding style; no `goto`; no new external dependencies; no new warnings; a regression for new behavior; and explicit MISRA deviations naming the relevant rule. A documentation PR in `rtos-docs-asciidoc` is required for API or behavior changes. Assess whether correcting the existing stack-address contract warrants one, and record the decision.

Commit subjects and PR titles begin with a past-tense verb and fit within 72 characters. Commit bodies explain cause, fix, then validation and wrap at 88 characters. PR descriptions use one line per paragraph. The [PR template](https://github.com/eclipse-threadx/threadx/blob/e73752681bd405deddf247d1cf2b899d502dceaa/.github/PULL_REQUEST_TEMPLATE.md) asks for function-header description/version updates, a test case, and real hardware validation. Mark only verified items; report simulator execution separately and leave hardware unchecked if unavailable.

AI-assisted edits require `Assisted-by: <product> (<model_and_version>) <email>` per applicable commit, using actual tool/model identity and no AI `Co-Authored-By`. Existing C/assembly files without an AI disclosure receive exactly one accepted disclosure line with that file's comment marker. Preserve existing disclosure lines. Add current-year Eclipse contributor copyright below older copyright when required. New C/assembly files use the guide's MIT/CC0 AI header and actual tool/model identity. Human review and provenance responsibility must be satisfied by the submitting contributor; an agent cannot certify an ECA on their behalf. [Eclipse's handbook](https://www.eclipse.org/projects/handbook/#genai) also requires disclosure and human responsibility.

The commit author email must match the contributor's Eclipse account covered by a signed [ECA](https://www.eclipse.org/legal/eca/). The guide says this fulfills DCO sign-off requirements; neither guide nor audited ruleset mandates a separate DCO check or `Signed-off-by` trailer. Do not invent one or fabricate ECA verification.

## Actual checks and readiness

The active [dev ruleset](https://github.com/eclipse-threadx/threadx/rules/23985797) requires **one approving review**, **code-owner review**, and these status contexts:

- `eclipsefdn/eca` from integration 22325.
- `tx / run_tests`.
- `smp / run_tests`.
- `freertos / run_tests`.
- `riscv / run_tests`.

All applicable CI must pass, including path-triggered GCC, clang, selected Cortex-M builds, port consistency, and repository disclosure checks. Current `CODEOWNERS` contains only `@eclipse-threadx/admins`, without a path pattern: it does not establish valid automatic ownership, as reported by [#793](https://github.com/eclipse-threadx/threadx/issues/793). This does not waive the review ruleset. Let GitHub and maintainers determine the necessary review state; agents must not manufacture approval.

The [regression workflow](https://github.com/eclipse-threadx/threadx/blob/e73752681bd405deddf247d1cf2b899d502dceaa/.github/workflows/regression_test.yml) runs unfiltered on PRs to `dev`. Kernel and SMP enforce merged **99% line coverage**. Branch coverage is reported but is not a hard gate. `repo_checks / checks` runs unfiltered but is not listed as a required status in the ruleset. GCC/clang, Cortex-M, port consistency, and Cortex-R52 FVP all trigger for `common/**`. An unavailable FVP URL means builds only, not hardware or FVP execution.

Freshly fetch rules, checks, reviews, mergeability, branch/head SHA, and issue state immediately before readiness. Require passing checks on the final PR head, no unresolved requested changes, necessary human approvals, and a non-draft PR before calling it ready to merge. Preparation complete and externally mergeable are separate states; neither a successful local run nor a clean diff provides human approval or an ECA check.

## Exact local commands

Run from the dedicated upstream checkout, using the reference GCC 14, CMake >=3.13, Ninja, multilib, and gcovr 8.6. Inspect `scripts/install.sh` and `scripts/install_riscv.sh` for dependencies; the latter supplies RISC-V toolchains/QEMU. Avoid running installation on an already-provisioned host unnecessarily.

```bash
CC=gcc-14 TX_COVERAGE=ON scripts/build_tx.sh
CC=gcc-14 TX_COVERAGE=ON scripts/test_tx.sh
CC=gcc-14 TX_COVERAGE=ON scripts/build_smp.sh
CC=gcc-14 TX_COVERAGE=ON scripts/test_smp.sh
CC=gcc-14 scripts/build_freertos.sh
CC=gcc-14 scripts/test_freertos.sh
scripts/build_tx_riscv.sh
scripts/test_tx_riscv.sh
scripts/check_ai_disclosure.sh
scripts/check_ports.sh
scripts/check_gcc.sh --arm-none-eabi /path/to/14.3.rel1/arm/bin \
                     --aarch64-none-elf /path/to/14.3.rel1/aarch64/bin
scripts/check_clang.sh --clang /path/to/ATfE-22.1.0/bin/clang
git diff --check
```

Build before testing. Host test scripts set `CTEST_PARALLEL_LEVEL=1`; coverage collection must also stay serial within a shared checkout. Preserve JUnit, build/test output, merged and per-configuration coverage, warnings, compiler versions, and exact SHA. Default CTest retry is `until-pass:2`; record first failures as well as final status. Use `CTEST_REPEAT_FAIL=1` when a clean first-pass acceptance run is required.

**Stale issue/documentation details:** current ThreadX CMake already contains `misra_build` and `misra_trace_build` (seven configurations total), while SMP has five. Neither ThreadX MISRA configuration enables stack checking, and both host suite projects force `-m32`. Existing MISRA or stack-checking suite success therefore cannot demonstrate #744 is fixed on 64-bit pointers. Add a dedicated native 64-bit regression combining `TX_MISRA_ENABLE` and `TX_ENABLE_STACK_CHECKING`, prove it fails against the unmodified baseline and passes the final patch, and verify stack bounds, aligned/unaligned starts, and thread execution. A compile-only check below is useful but reproduces neither truncation nor runtime safety:

```bash
gcc-14 -std=c99 -Werror -c -DTX_MISRA_ENABLE -DTX_ENABLE_STACK_CHECKING \
    -I common/inc -I ports/linux/gnu/inc common/src/tx_thread_create.c \
    -o /tmp/threadx-744-thread-create.o
```

For reference, inspect [current ThreadX CMake](https://github.com/eclipse-threadx/threadx/blob/e73752681bd405deddf247d1cf2b899d502dceaa/test/tx/cmake/CMakeLists.txt), [SMP CMake](https://github.com/eclipse-threadx/threadx/blob/e73752681bd405deddf247d1cf2b899d502dceaa/test/smp/cmake/CMakeLists.txt), and [test runner](https://github.com/eclipse-threadx/threadx/blob/e73752681bd405deddf247d1cf2b899d502dceaa/test/tx/cmake/run.sh).
