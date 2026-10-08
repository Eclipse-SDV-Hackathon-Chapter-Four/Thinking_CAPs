# Historical disable-notify SMP failure comparison

The earlier full SMP execution failed with ERROR #7 in `disable_notify_callbacks_build` under an unrestricted host CPU profile. Evidence for `trace_build` alone cannot classify that separate feature configuration, so this diagnostic tested its original baseline explicitly.

Original baseline `e73752681bd405deddf247d1cf2b899d502dceaa` was built with stock `disable_notify_callbacks_build`, `TX_COVERAGE=ON`, `BUILD_SHARED_LIBS=ON`, GCC 14.2, C99, and `-m32`, using the same pinned validation image, UID/GID 1000, SYS_NICE, and rtprio 3. No Docker CPU affinity override was applied; all 32 host CPUs were available. Only `threadx_smp_random_resume_suspend_exclusion_pt_test` and its dependencies were built in the separate loop4 `evidence/diagnostics/baseline-smp-disable-notify-build` directory.

Configure and build passed. Independent baseline executions 1–4 passed. Execution 5 reported **ERROR #7 and exit code 1**. The diagnostic stopped immediately at that first matching failure, within its ten-execution bound. Every invocation had its own ten-second timeout and retained log; no failure was erased by retries until success.

This establishes matched original-baseline proof for the historical disable-notify failure. It does not make a failed suite pass or waive any current acceptance check. The current final verification results must stand on their own.

The baseline's tracked source remained clean. The evidence records source hashes, base SHA, full exact commands, compiler output, and measured compilation flags, including `test/shared/regression/testcontrol_weak_defaults.c`. Its definitions include `TX_DISABLE_NOTIFY_CALLBACKS`, `TX_REGRESSION_TEST`, `TX_SMP_NOT_POSSIBLE`, `TX_THREAD_SMP_ONLY_CORE_0_DEFAULT`, `CTEST`, and `BATCH_TEST`; event tracing is absent. The kernel compilation includes coverage instrumentation, as required by the matched profile.

Concise evidence is mirrored in `artifacts/diagnostics/baseline-smp-disable-notify`. Full build and run logs remain on loop4 under `evidence/diagnostics/baseline-smp-disable-notify`. No production, test, workflow driver, prompt, or native frozen record was edited for this diagnostic.
