# Historical default-coverage SMP failure comparison

Retained history `2026-10-07T143232Z-7a6232fcfcfa` contains an ERROR #7 failure in `default_build_coverage`. Its SMP test log explicitly records Docker CPU affinity `0,1,2,3`; `verification.json` confirms those CPUs. The historical run was therefore a four-CPU profile, even though its build ran without an affinity override.

A separate original-baseline diagnostic matched that test profile: original revision `e73752681bd405deddf247d1cf2b899d502dceaa`, stock `default_build_coverage`, `TX_COVERAGE=ON`, `BUILD_SHARED_LIBS=ON`, GCC 14.2, C99, and `-m32`, using pinned image `sha256:a8a3d92ee0ba622304a79ce1dcc51aba1ad1d0ac52767c71b7c1e158520275cc`, UID/GID 1000, SYS_NICE, rtprio 3, and Docker affinity `0,1,2,3`. Only `threadx_smp_random_resume_suspend_exclusion_pt_test` and its dependencies were built in loop4 `evidence/diagnostics/baseline-smp-default-build`.

Configure and build passed. Independent baseline executions 1–7 passed. Execution 8 reported **ERROR #7 and exit code 1**. The diagnostic stopped immediately at that first matching failure, within the ten-execution bound. Each invocation had a separate ten-second timeout; every result and log was preserved.

This establishes matched original-baseline proof for the historical default-coverage failure, separately from the trace and disable-notify configurations. It does not change any current acceptance result, waive a failed check, or replace remote PR checks.

The baseline's tracked source remained clean. Recorded source hashes and measured compiler commands include the actual randomized test, SMP thread creation service, Linux port header, and `test/shared/regression/testcontrol_weak_defaults.c`. Definitions include `TX_REGRESSION_TEST`, `TX_SMP_NOT_POSSIBLE`, `TX_THREAD_SMP_ONLY_CORE_0_DEFAULT`, `CTEST`, and `BATCH_TEST`; `TX_DISABLE_NOTIFY_CALLBACKS` and event tracing are absent. The kernel compilation includes coverage instrumentation.

Exact historical command, diagnostic commands, compiler output, source state, and all eight execution logs are mirrored under `artifacts/diagnostics/baseline-smp-default`. Full build evidence remains on loop4 under `evidence/diagnostics/baseline-smp-default`. No source, driver, prompt, gate, frozen record, or current verification file was changed for this diagnostic.
