# F010 implementation and convergence review

Prepared 4 October 2026. The user's latest instruction defers contribution
reproduction for now and admits continued implementation. Second-contributor
signoff remains pending/unattested; AAOS/FOTA remains deferred. No external
publication or awarded bonus is claimed.

## Convergence

Assessed17 FRs,9 success criteria (their buildable obligations),18 acceptance
scenarios across4 user stories,10 edge cases,6 research decisions and12 constitution
principles against the scoped service/browser/runner code. No actionable code gap
remains: missing0, partial0, contradicts0, unrequested0. No convergence task was
appended and the convergence operation did not change existing tasks/application
code. This review is recorded by implementation taskT015 after convergence ended.
No extension hooks are registered.

SC001's timed human identification walkthrough is not recorded. Automated primary
navigation and rendering pass; a human usability timing claim is not inferred.
The separate human reproduction requirement is user-deferred, not satisfied.

## Requirement-to-evidence trace

| Scope | Current implementation / meaningful proof |
| --- | --- |
| FR001–004; US1; SC002–003 | Actual discovered OpenSOVD resources, independent observation/history acquisition, stale/unknown/last-observed timestamps and source/session fields. `f010-native-diagnosis`8 actual-provider tests with explicitly fixture input cover unknown/fresh/stale/new session/service outage/recovery and unsupported history. `f010-live` captures actual receiver and fault data. Control output is unavailable. Fault query loss cannot become current stored fault health. |
| FR005–006/016; US2 AC1–2 | Observed ownership/running gates and bounded CLEO peers/devices/deployments/interfaces. Local TLS/VPN-OIDC-off profile is explicit; only fixed project campaigns are admitted. Actual bench up passes; missing inputs/bench/interpreter produce blocked state with no native pass. Upstream executor is not claimed. |
| FR007; US2 AC3–4; SC004 | Mutex/persisted UUID plus coordinator/bench flock; UUID passed to runner. Actual two-client start returns one202 and one409; two Chromium clients and reload see the same run. CLI admission test is blocked by actual flock. Corrupt/unresolved ledgers inhibit admission. |
| FR008–009; US2 AC5; SC006 | Owned Popen cancellation, queued no-spawn cancellation, bounded termination, native restoration completeness gates and sticky unknown/failed cleanup. Actual cancellation occurs after tunnel-down-complete; execution fails while restoration passes. Owned wait fixture deliberately lacks native evidence: unknown cleanup remains visible and inhibits start. Seven original repository/config/image/state comparisons pass after bench teardown. |
| FR010; US2 AC6; SC005 | Original runner rows/reasons retained; dashboard lifecycle is separate. Passed physical/core, cancelled failed execution, actual preflight blocked and ten deferred/conditional skipped rows remain truthful. Missing runner launch cannot synthesize a runner pass. |
| FR011–013; US3; SC007 | Bounded original timeline/observations and declared clocks; explicit artifact allowlist/hash inventory and unchanged bytes. Live actual download checks match hashes and original bytes. Tamper/missing/symlink/path regressions preserve original verdict independently of integrity and refuse invalid downloads. Historical physical/fixture library and sandboxed hash-checked replay are distinct from live health. |
| FR014; SC009 | Background observation/bench workers and separate native subprocess; browser polling never enters vehicle control. Actual dashboard process SIGSTOP/outage/resume during physical execution invalidates UI health, preserves run identity, and leaves46 physical/native assertions including return actuation passing. No automatic engagement added. |
| FR015; US4; SC001 buildable portion/SC008 | Actual Chromium18 acceptance checks cover keyboard primary navigation, real selection handlers, starts at360/1280, horizontal mobile table/keyboard scroll, historical evidence/download links, text injection and loss/reconnect. Separate14 keyboard start/reload/cancel controls use an explicitly owned wait-process fixture at both widths. Text-labelled states, focus, skip link and responsive layout are inspected. Human timed walkthrough remains unverified. |
| FR017; US4 capability limits | Primary actions are fixed campaign start/cancel, observational browsing and verified evidence retrieval. AAOS/FOTA, direct actuation, fault deletion and public publishing actions are absent. ThreadX/AutoSD are separate proposals, not fake working capabilities. |

## Verification boundaries

`contributions/shared/evidence/f010-review/verification.json` records31 project regressions on Python3.10
and3.13, syntax/whitespace gates and identities of the evidence records. Real core
passes42 native checks; physical passes46. Actual cancellation cleanup passes while
execution fails. Browser acceptance18 and keyboard fixture14 pass. Native adapter8
pass. Owned testbench teardown and original preservation pass. Dashboard can remain
available with unavailable live diagnosis and historical reports while bench is down.

The initial failed browser probes reflect driver issues (evaluation before load,
missing headless focus and an assertion racing the previous blocked result). They
are retained as failed attempts, superseded by explicitly named passed acceptance.
The mobile table readability issue was corrected before the final browser run.

Real native/physical evidence used the service before final ledger/prelaunch/bounded
shutdown refinements. Those refinements are covered by31 current regressions and
current real-browser controlled-fixture tests; native binaries/controller/bridge/VCU
are unchanged. Do not call the interrupted/fixture tests fresh physical builds.
No new-machine/cold-image, human rehearsal, distributed/VPN, hardware ECU or
power-loss acceptance is claimed. Contribution drafts and unrelated edits are
preserved and are not part of this commit.
