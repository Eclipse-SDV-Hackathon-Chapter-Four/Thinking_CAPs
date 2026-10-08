# Matched original and candidate SMP diagnostics

Built only `threadx_smp_random_resume_suspend_exclusion_pt_test` from original baseline `e73752681bd405deddf247d1cf2b899d502dceaa`, with stock `trace_build`, `TX_COVERAGE=ON`, `BUILD_SHARED_LIBS=ON`, GCC 14.2, C99, and `-m32`. The image was `sha256:a8a3d92ee0ba622304a79ce1dcc51aba1ad1d0ac52767c71b7c1e158520275cc`. Execution used host CPU affinity `0,2,4,6`, UID/GID 1000, SYS_NICE, and rtprio 3, matching the candidate's four-physical-core diagnostic.

Configure and target build passed. An initial ten independent original-baseline executions each passed with a ten-second timeout. That preliminary experiment did not reproduce a baseline failure. Its exact commands and complete outcomes are preserved under `artifacts/diagnostics/baseline-smp`.

A subsequent paired experiment interleaved an original-baseline execution with a candidate execution, using the same scheduling environment and a ten-second limit for each invocation. The bound was twenty pairs, with early stopping only after a failure was observed in both trees. The experiment stopped after six pairs:

| Pair | Original baseline | Candidate |
| --- | --- | --- |
| 1 | Pass | Pass |
| 2 | Pass | Pass |
| 3 | Pass | Pass |
| 4 | **ERROR #7; exit 1** | Pass |
| 5 | Pass | Pass |
| 6 | Pass | **ERROR #7; exit 1** |

Every result was retained. The same failure is therefore established on unchanged original code and on the candidate. The randomized SMP test's ERROR #7 is a pre-existing intermittent failure under this environment. This diagnostic does **not** make the failed local full SMP suite green and does not replace its required upstream PR check.

The retained historical trace failure used affinity `0,1,2,3`, which differs from this paired experiment's `0,2,4,6`. A separate original-baseline test at the exact historical trace affinity passed all ten bounded runs. That historical affinity therefore has no reproduced baseline failure; do not extend the paired proof into a claim that those profiles are equivalent. The fresh complete 590-test SMP pass is independent evidence and does not depend on classifying every historical CPU profile.

Full Ninja compilation and linking commands were compared. After normalizing only build-directory paths, all commands match exactly, including compiler, definitions, warning settings, C99, `-m32`, event tracing, coverage instrumentation, shared-library linkage, and target source lists. The normalized diff is empty. Both trees have no tracked changes in `common_smp`, `ports_smp`, `test/smp`, `test/shared`, `common/inc`, or the Linux toolchain. The baseline's tracked production source is clean. Untracked focused-regression directories left by a separate #744 experiment are present but unused by SMP.

Mount detail: the candidate source was mounted read-only at `/work`, while the standalone original-baseline build is under writable `/evidence`. Consequently candidate libgcov output writes may fail during process exit, while baseline coverage files can be saved. ERROR #7 is reported during the test before process exit and coverage serialization. This difference is retained explicitly in the evidence rather than omitted from the comparison. No source, test, or driver edits were made.

Exact Docker command arrays, binary/library hashes, full compile/link commands, source state, and all twelve paired logs are in `artifacts/diagnostics/paired-smp`. The original-baseline build survives verifier cleanup at loop4 `evidence/diagnostics/baseline-smp-build`. The complete original and paired evidence stays under loop4 `evidence/diagnostics`.
