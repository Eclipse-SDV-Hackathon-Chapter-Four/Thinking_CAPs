# Open Eclipse ThreadX issues

Snapshot: 2026-10-07. 52 open issues returned by the GitHub API.

| Issue | Title |
| --- | --- |
| [#479](https://github.com/eclipse-threadx/threadx/issues/479) | Update the diagram in README.MD |
| [#497](https://github.com/eclipse-threadx/threadx/issues/497) | Validate and improve draft coding conventions |
| [#515](https://github.com/eclipse-threadx/threadx/issues/515) | New Architecture Support: V850/RH850 for Eclipse ThreadX |
| [#528](https://github.com/eclipse-threadx/threadx/issues/528) | README.md points to archived https://github.com/eclipse-threadx/rtos-docs/blob/main/rtos-docs/ instead of https://github.com/eclipse-threadx/rtos-docs-asciidoc |
| [#557](https://github.com/eclipse-threadx/threadx/issues/557) | Implement mprotect()-based module isolation for the Linux/GNU simulation port (and Windows equivalent) |
| [#577](https://github.com/eclipse-threadx/threadx/issues/577) | Verify hard-coded TX_THREAD offsets in port assembly at compile time |
| [#585](https://github.com/eclipse-threadx/threadx/issues/585) | Module converter utilities misparse ELF files when built for a 64-bit host |
| [#586](https://github.com/eclipse-threadx/threadx/issues/586) | FreeRTOS layer selects interrupt primitives by compiler rather than by target, breaking hosted GCC builds |
| [#587](https://github.com/eclipse-threadx/threadx/issues/587) | FreeRTOS layer passes pointers through ULONG, which truncates where ULONG is narrower than a pointer |
| [#588](https://github.com/eclipse-threadx/threadx/issues/588) | xTaskCreate reports success when tx_thread_resume fails, unlike xTaskCreateStatic |
| [#605](https://github.com/eclipse-threadx/threadx/issues/605) | Add .sh example build scripts for the ARMv7-A SMP ports (A5, A7, A9) |
| [#619](https://github.com/eclipse-threadx/threadx/issues/619) | Green Hills port tests for Cortex-A5, A7, A8 and A9 compare against golden files that do not exist |
| [#628](https://github.com/eclipse-threadx/threadx/issues/628) | POSIX compatibility layer does not work on 64-bit ports |
| [#650](https://github.com/eclipse-threadx/threadx/issues/650) | The CLZ lowest-set-bit optimisation has never run under GCC or armclang |
| [#651](https://github.com/eclipse-threadx/threadx/issues/651) | Object name parameters are CHAR * rather than const CHAR * |
| [#668](https://github.com/eclipse-threadx/threadx/issues/668) | Cortex-R52 has no CI that executes its regression suite |
| [#669](https://github.com/eclipse-threadx/threadx/issues/669) | Cortex-R52 region 16 can be programmed directly, without the per-switch PRSELR and ISB |
| [#670](https://github.com/eclipse-threadx/threadx/issues/670) | Thumb-state modules are unvalidated on the Cortex-R52 module port |
| [#671](https://github.com/eclipse-threadx/threadx/issues/671) | The S32Z280 example BSP comments contradict the code and each other |
| [#678](https://github.com/eclipse-threadx/threadx/issues/678) | The CI work on dev has never reached master, and that merge is the only chance to test the Pages publish path |
| [#679](https://github.com/eclipse-threadx/threadx/issues/679) | Three open pull requests to dev are gated by no regression suite, because their branches predate the trigger |
| [#680](https://github.com/eclipse-threadx/threadx/issues/680) | SMP next-priority lookup shifts by an unvalidated priority, then checks the range afterwards |
| [#681](https://github.com/eclipse-threadx/threadx/issues/681) | The GCC port check skips the RISC-V ports, which assemble cleanly but are covered by nothing |
| [#682](https://github.com/eclipse-threadx/threadx/issues/682) | The GCC and clang port checks fail only on a failed compilation, so port warnings can accumulate unseen |
| [#683](https://github.com/eclipse-threadx/threadx/issues/683) | ci_cortex_m duplicates the GCC check for four cores, and can only be retired if stage 5 grows a second shape |
| [#684](https://github.com/eclipse-threadx/threadx/issues/684) | Branch coverage is around 78% in both suites and is enforced by nothing, because fail_below_min compares the line rate only |
| [#685](https://github.com/eclipse-threadx/threadx/issues/685) | How to run the port checks and the regression suites is undocumented, and the traps are the expensive part |
| [#702](https://github.com/eclipse-threadx/threadx/issues/702) | Support TX_ENABLE_STACK_CHECKING for module threads |
| [#703](https://github.com/eclipse-threadx/threadx/issues/703) | Document the SPSel = 0 / SP_EL0 requirement of the ARMv8-A ports |
| [#710](https://github.com/eclipse-threadx/threadx/issues/710) | Add SMP support for Armv8-R (Cortex-R52 / Cortex-R82) |
| [#712](https://github.com/eclipse-threadx/threadx/issues/712) | The Cortex-R52 port's FVP suite is never executed in CI |
| [#733](https://github.com/eclipse-threadx/threadx/issues/733) | Implement FileX support for ThreadX modules |
| [#744](https://github.com/eclipse-threadx/threadx/issues/744) | _tx_thread_create truncates the stack start pointer under TX_MISRA_ENABLE on ports where ALIGN_TYPE is wider than ULONG |
| [#750](https://github.com/eclipse-threadx/threadx/issues/750) | The SMP MISRA shim reports five conversion warnings the monoprocessor copy does not |
| [#752](https://github.com/eclipse-threadx/threadx/issues/752) | ThreadX SMP Linux port deadlocks on a lost mutex wake-up, and the regression suite hangs because of it |
| [#755](https://github.com/eclipse-threadx/threadx/issues/755) | Port to GD32F450i Generic ARM M4 |
| [#756](https://github.com/eclipse-threadx/threadx/issues/756) | ThreadX SMP discards the execute list rebalance that tx_thread_relinquish asks for, starving a ready thread |
| [#757](https://github.com/eclipse-threadx/threadx/issues/757) | ThreadX SMP Linux port leaks a critical section level on unprotect, wedging the process while the tick keeps running |
| [#764](https://github.com/eclipse-threadx/threadx/issues/764) | Investigate AddressSanitizer-like diagnostics for ThreadX |
| [#765](https://github.com/eclipse-threadx/threadx/issues/765) | Normalize the copyright line to the project's accepted form |
| [#767](https://github.com/eclipse-threadx/threadx/issues/767) | Add optional 64-bit system clock APIs |
| [#768](https://github.com/eclipse-threadx/threadx/issues/768) | The SMP Linux port cannot exercise the kernel-enter core-ready wait loop, and a regression hook masks that in coverage |
| [#769](https://github.com/eclipse-threadx/threadx/issues/769) | Add a GCC port for the Infineon AURIX TC375 |
| [#770](https://github.com/eclipse-threadx/threadx/issues/770) | Support module-manager kernels in CMake builds |
| [#771](https://github.com/eclipse-threadx/threadx/issues/771) | Add opt-in pointer context APIs for threads and timers |
| [#772](https://github.com/eclipse-threadx/threadx/issues/772) | Evaluate a source-only void * callback mode |
| [#778](https://github.com/eclipse-threadx/threadx/issues/778) | Add first-class ThreadX support to MCUboot |
| [#780](https://github.com/eclipse-threadx/threadx/issues/780) | Make TX_ENABLE_CONST_NAMES the default in 6.6 |
| [#788](https://github.com/eclipse-threadx/threadx/issues/788) | Build and run the RISC-V64 Erbium example in CI |
| [#792](https://github.com/eclipse-threadx/threadx/issues/792) | Linux port mutex retry in #754 crashes NetX Duo's nx_secure_tls_coverage_test |
| [#793](https://github.com/eclipse-threadx/threadx/issues/793) | The CODEOWNERS entry has no path pattern, so it assigns no owners |
| [#795](https://github.com/eclipse-threadx/threadx/issues/795) | TX_SAFETY_CRITICAL: undocumented, untested, and incompatible with the certified configurations |
