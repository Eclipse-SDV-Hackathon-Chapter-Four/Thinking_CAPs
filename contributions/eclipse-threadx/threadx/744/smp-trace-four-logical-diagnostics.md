# Historical trace affinity diagnostic

Retained history `2026-10-07T141718Z-7a6232fcfcfa` records a trace-build ERROR #7 at Docker affinity `0,1,2,3`. The paired original/candidate proof previously used `0,2,4,6`, a different affinity. Those records must remain distinct.

Reused the verified original-baseline trace executable built from `e73752681bd405deddf247d1cf2b899d502dceaa`, with stock `trace_build`, shared library, `TX_COVERAGE=ON`, GCC 14.2, C99, and `-m32`. The build cache, measured compiler commands, binary/library hashes, baseline tracked status, and compilation evidence were checked and recorded. Execution matched the historical affinity `0,1,2,3` and the same pinned validation image, UID/GID 1000, SYS_NICE, and rtprio 3.

Ten independent runs, each with a ten-second timeout, all passed. The diagnostic stopped at its authorized bound. Therefore **the exact historical four-logical-CPU trace failure was not reproduced on the original baseline**. Its historical profile must not be described as baseline-proven. The paired four-physical-core proof remains evidence that original and candidate can both fail the same assertion under that other profile.

All commands and outcomes are retained under `artifacts/diagnostics/baseline-smp-trace-four-logical`. The digest-bound `artifacts/diagnostics/smp-retained-failures-index.json` explicitly separates historical failures, matching-profile baseline evidence, differing-profile paired evidence, and the fresh complete verification pass. No source, gate, or current verification record was changed.
