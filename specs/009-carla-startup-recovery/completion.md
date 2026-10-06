# F009 completion and convergence
Prepared 4 October 2026. The original physical simulation milestone is now verified.
Second-contributor reproduction is still pending; AAOS/FOTA remains user-deferred.

| Intent | Authoritative verification |
| --- | --- |
| FR001 / US1 | `evidence/f009-client-comparison/manifest.json`: a client created before launch still times out after a fresh client reaches server0.9.15, actual Town10HD_Opt world and advancing frames. Earlier debugger failures/raw RPC investigation are retained. This proves the startup-client defect on this environment, without assigning a GPU root cause. |
| FR002 / SC001 | `wait_for_world` uses fresh two-worker clients on each failure and an absolute monotonic deadline with remaining-time RPC limits. Three regressions cover replacement, deadline and exited server. `f009-physical-plant` records151 actual samples, physical speed above54km/h and private-runtime/server cleanup. |
| FR003 | Plant/transport initializes before native diagnostic/controller startup. Startup-unknown and not-healthy assertions still precede input publishing. This avoids counting engine startup as the selected transport-loss fault. Fixture regression retains42 passing native assertions. |
| FR004 / US2 / SC002 | `f009-carla-native-final` passes46 native/physical assertions and nine selected scenario/runner verdicts; ten conditional/deferred checks skipped. Actual actor/frames/speed/receiver/return/native fault/history restart/stall/recovery recorded. `carla-control-return.json` records67 sampled native-to-VCU-to-subsequent-actor matches with zero operator pedal; required20, window3 samples, tolerance1e-5, actual damping1.2. Two correlation regressions reject misleading positive manual/unrelated controls. Wrapper regression rejects a missing correlation check. No E2E association ID/latency guarantee inferred. |
| FR005 / US3 / SC003 | `f009-bench-down` passes scoped teardown; `f009-preservation.json` verifies all seven original repository/status/diff identities, configuration/image identities, baseline stopped containers, no owned resources or CARLA listeners. Original server binary hash unchanged. Private caches/state retained. Engine shutdown can print a crash-on-exit log; graceful engine exit is not claimed. |
| Executable-input refinement | Overlay variable shadowing originally discarded explicit compiler/schema paths. Fixed without source/gateway changes; actual fresh compiler/schema paths are now recorded and used in the real and fixture runs. Historical F008 clean-source builds/native campaign remain valid with an additional baseline-config-tool sharing limitation, now documented rather than rewriting evidence. Reproduction helper freezes current committed HEAD or an explicit revision for future runs. |
| Physical test-driver refinement | Actor stopped by the first nominal acceptance after earlier movement. Explicit waypoint steering now travels through the existing manual topic; original vehicle/VCU/bridge source untouched. No native throttle override or acceptance relaxation. Operator requests and applied steering/position are recorded. |

Meaningful final Python regressions:17 pass; affected syntax/whitespace and retained artifact
integrity pass (`f009-verification.json`). Native Rust/C++ implementations are unchanged from
the fresh F008 build, and their exact executable identities are recorded in the new campaign.
No duplicate native rebuild was needed for these Python startup/harness changes.

Constitution: I original sources/bridge/baseline preserved; II assets/integration/upstream
separated; III feature specification/plan/tasks preceded implementation and convergence
tasks closed actual gaps; IV existing native libraries/vehicle classes reused; V diagnostics
remain separate from control; VI actual source/clock/physical identity and unavailable E2E
explicit; VII actual tools/images/config/binary hashes recorded and input shadowing corrected;
VIII startup/failure/timeout/stall/history/recovery/cleanup covered; IX prior failed/blocked
evidence retained; X no external communication/publication or driver/system changes;
XI work remains pre-event preparation; XII deterministic native/physical assertions decide
acceptance, with no update activation.

Reviewed five functional requirements, three success criteria, three user stories, all plan
touch points and twelve principles against actual source/evidence. No buildable gap remains
in this slice. The broader requirement REQ017 remains pending a real second contributor.
No public submission, maintainer approval, event-time creation or AAOS update is claimed.

## Current reproduction and recorded replay refinement

The subsequent `f009-reproduction-current` froze committed `0b8a67e`, created clean
source clones and fresh native C++/Rust build directories, and passed controller unit
tests, Rust tests/Clippy and42 native core assertions. Its generated configuration
was then used by the frozen clone's physical runner: `f009-reproduction-physical`
passes46 native/physical assertions with67 zero-pedal actuator correlations. The
executed compiler/schema paths point to the new Bazel output base, and the native
diagnostic binary identity matches the fresh build. The current helper and generated
inputs are now verified together. This remains a shared-host agent self-run.

The standalone `f009-recorded-replay-final/index.html` supplies a historical fallback
with actual saved samples, snapshots, timeline, verdicts and source identities.
Actual browser checks cover rendering, fault-state seeking, terminal unknown state,
play/pause/restart, no live requests and no script errors. Negative gates reject
fixtures, failed physical runs and changed source hashes before creating output.
The browser screenshot was inspected for readable labels, units and historical limits.
This is separate from the specified F010 live dashboard.

The reproduction bench's owned teardown passes and no owned resources or CARLA
listeners remain. The newer preservation record is **partial**: six original
repository revision/status/diff identities and all locked application/configuration,
runtime image, original stopped-container and CARLA binary comparisons pass. The
original autoverse revision and dirty file list match, but its tracked dirty-diff
identity differs from the initial audit. This turn did not edit that repository;
the difference is left intact. Full current workspace preservation is not claimed.

Convergence reviewed the same five FRs, three SCs, three stories, plan decisions
and twelve principles. T012/T013 are verified; one HIGH partial verification gap
remains against SC003, appended as T014 under Phase4. The earlier clean review
describes its original measurement; it is not a claim that the later workspace
snapshot is unchanged. REQ017 human reproduction remains pending independently.

The remaining T014 comparison is now resolved by `f009-preservation-recheck`.
The original auditor uses `subprocess` text mode, normalizing CRLF before stripping
and hashing. The later comparison omitted normalization; the autoverse diff has156
CRLF sequences. Reusing the actual auditor confirms all seven original revision/
status/diff identities match, alongside the six locked configuration hashes, images,
original stopped containers, CARLA binary and absent owned resources/listeners.
The earlier partial record is retained as an audit-method failure, not evidence of
a workspace change. No original file was restored or modified. All F009 tasks are
verified; independent human reproduction remains outside this completed local slice.
