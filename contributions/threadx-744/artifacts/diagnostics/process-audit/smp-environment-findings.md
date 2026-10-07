# SMP acceptance environment observations

Captured 2026-10-07. Source/build/test files were read only. No additional suite or reproduction was launched during the active acceptance run.

## Findings

- Baseline e73752681bd405deddf247d1cf2b899d502dceaa passed upstream `smp / run_tests` on 2026-10-06: https://github.com/eclipse-threadx/threadx/actions/runs/37442786479/job/112200317485 . GitHub API reports a GitHub-hosted `ubuntu-24.04` runner. The reusable workflow uses the stock install/build/test scripts, serial CTest, and no explicit CPU affinity or real-time-capability grant. The installer installs distribution gcc-multilib; workflow source does not explicitly pin its host GCC version. Do not infer the exact runner CPU/compiler from a workflow label.
- The failing test resumes eight randomly selected threads, drops the controller priority, relinquishes, and then checks `tx_thread_run_count`. A missing count gets one `tx_thread_sleep(1)` retry before ERROR #7. Default Linux SMP timer rate is100Hz, so the nominal retry is one10ms tick. ERROR #7 alone does not establish the cause.
- Port scheduling requests SCHED_FIFO priorities3 scheduler,2 ISR,1 user threads, without checking pthread_setschedparam return status. The timer thread also calls nice(10); actual per-thread policy should be sampled rather than inferred from the launch shell.
- Acceptance Docker container d137afe6bca8 was observed with CAP_SYS_NICE, rtprio3:3, uid/gid1000:1000, affinity0,1,2,3. A live ThreadX test scheduler was observed in FF class at RTPRIO3. This contradicts any inference that acceptance lacked real-time privileges based solely on the host shell, whose RTPRIO limit is0. The preserved later structured process sample caught a test between initialization and therefore contains ordinary-policy processes; it is not evidence of failed RT setup.
- On this i9-14900HX, logical CPUs0-1 share physical core0, and2-3 share physical core4. The first four logical CPUs provide only two physical cores. CPUs0,2,4,6 provide four separate P cores. CPU topology is preserved in host-environment.json.
- During inspection the host load average exceeded98 on32 logical CPUs and CPU pressure some avg10 exceeded70%. Host contention is substantial. Docker CPU affinity does not reserve those CPUs or remove contention, though real-time threads can preempt ordinary workloads.

## Recommendation

Use four distinct physical P cores for a matched baseline/candidate diagnostic, chosen once from physical topology rather than blindly taking the first four logical CPUs. Use the same image, GCC/gcov, RT-capability/limit, affinity, coverage flags, serial CTest, and timeout on both revisions. Preserve every failure and retry. First establish that the unchanged baseline is stable in that environment; if not, do not present a candidate-only pass as acceptance.

For acceptance faithful to upstream CI, an otherwise idle Ubuntu24.04 VM/runner using upstream scripts and reference/compiler versions offers stronger evidence than repeatedly rerunning a heavily loaded development host. If the local port intentionally uses SCHED_FIFO, retain the documented capability/limit rather than changing it opportunistically. Avoid pinning to one CPU: the active test assumes four simulated cores and observed one-CPU diagnostics hung. Do not increase its sleep, change scheduler code, disable it, or introduce an unrelated source fix into #744.

After choosing the environment, run all five SMP configurations serially including trace, not merely the failing binary. Set CTEST_REPEAT_FAIL=1 for a first-pass acceptance result; when reproducing exact upstream retry semantics, separately record the stock until-pass:2 behavior and first failures. Use a single bounded follow-up diagnostic, then defer to uncontended or upstream final-head CI instead of repeatedly searching for a passing run. Final PR readiness still requires actual final-head required CI results.
