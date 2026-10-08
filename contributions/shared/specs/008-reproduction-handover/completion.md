# F008 completion and convergence

Prepared 4 October 2026. Selected local reproduction/handover work is complete.
Actual second-person acceptance and real CARLA physics remain pending/blocked.

| Intent | Verification |
| --- | --- |
| FR001 / SC001 | `scripts/reproduce_core.py` froze integration6d7bef9, Score93f8ea1 and bridge0d53a2a; source-clean clones, exact receiver patch, fresh Bazel/Rust outputs, controller unit target and native fault tests/Clippy passed. `evidence/f008-reproduction-final` records commands and a successful real native core campaign. Host/images/LLVM are explicitly shared; the implementation agent is the operator. First failed bridge-layout attempt is retained. Human signoff stays pending. |
| FR002 / SC002 | `contributions/fault-storage-write-through` contains the narrow native storage patch/problem/PR draft and reproducible pinned-nightly validation. Patch bytes match the implementation patch. Default flush behavior, opt-in persistence, storage read errors, memory-on-flush-failure and power-loss boundaries are explicit. Full upstream CI, ECA, publication and maintainer agreement are not claimed. |
| FR003–004 | README/setup/scripts/tests entrypoints reflect the actual 42 native assertions, fixture vehicle inputs and eight selected wrapper verdicts. Claim/evidence and prepared-work inventories separate preparation, native integration, self-reproduction and human acceptance. Event-start revision remains unassigned. |
| FR005 / SC003 | `evidence/f008-teardown` passed scoped openDuT undeploy/removal. `evidence/f008-preservation.json` verifies all seven original repository pins/status/diff hashes, selected configurations/images and original stopped containers. No owned containers/networks/volumes or CARLA listeners remain. Private state/build caches are intentionally retained. |
| FR006 / SC004 | Exact baseline recipe, Epic/NVIDIA and null-RHI probes still timed out on actual world/version RPC. Thread investigation does not establish root cause; the main-thread GDB probe hit an internal debugger error. Failed/blocked logs retained. CARLA runtime configuration is now private temporary state; tracked generated configuration is removed. Physics/control acceptance remains blocked. |
| FR007 | `docs/handover.md` contains restart/rehearsal/pitch/evidence and continuation for CARLA, native `/faults`, human signoff, optional extensions and user-deferred FOTA. Recorded fixture fallback is labelled. |

Appropriate final checks: 11 baseline/verdict regressions, retained contribution integrity,
Python compilation, whitespace, handover relative links and patch equality passed in
`evidence/f008-verification.json`. The fresh native build/test campaign is separate evidence;
component tests are not advertised as full upstream CI or independent-person reproduction.
`evidence/f008-carla-private-runtime/verification.json` separately verifies private0700
runtime, blocked-start cleanup, stopped owned server and released ports against the updated
helper; it records the harness's corrected timeout field interpretation.

Constitution convergence: I baseline/bridge preserved; II reused/integration/upstream separated;
III F001–F005 reviewed before this slice; IV native provider/reporter/storage used and route
fallback named; V control/diagnostic processes separated; VI actual receiver provenance and
unavailable integrity explicit; VII executable pins/images/commands recorded; VIII failure,
interruption, history and recovery tested; IX blocked/skipped/fixture outcomes preserved;
X upstream instructions acknowledged with no external action; XI all work prepared and event
delta pending; XII deterministic assertions determine verdicts, with no update activation.

No unresolved buildable gap in this selected local handover slice. Unavailable real simulator
and second contributor remain limitations of the broader implementation goal. The final local
commit includes this review and task record; no publication is authorized or performed.

## Later handover refinement

F009 subsequently resolved physical CARLA acceptance and verified42 core/46 physical
assertions from fresh native builds, including actual fresh compiler/schema execution.
Those artifacts supersede the original CARLA blocker for current demonstration claims;
historical blocked measurements above remain retained.

The eight-minute interview script and9:30 final-pitch deck/notes are now prepared in
`docs/hackathon`. Actual browser checks cover keyboard/button navigation, rehearsal
clock, phone layout, offline-only resource use and error-free execution. Desktop/phone
screenshots were visually inspected. Printing yields exactly seven A4 landscape pages
with all seven slide titles. Evidence links and declared timing totals are verified.
This is material preparation and browser verification, not an actual human rehearsal.

The reproduction helper now records observed hostname/platform/Python identity and
caller-declared operator/host-sharing. Omission remains unknown; no caller inherits
an invented implementation-agent identity or verified original-host claim. Three
actual bounded CLI rejection paths verify these fields without running native builds;
one deliberately declares a different host on this same host to test metadata input,
not to claim a real different-host reproduction. Independent human signoff stays false.
The previously verified native pipeline is unchanged, and historical manifests retain
their original recorded self-run attribution.

The apparent later autoverse preservation mismatch was caused by omitting the
original auditor's universal newline normalization. `f009-preservation-recheck`
uses that auditor and confirms all seven original repository comparisons and locked
config/image/binary/state checks pass without original file edits. All newly appended
local handover tasks are verified; a real person's reproduction/rehearsal and event
eligibility remain external acceptance, not manufactured by automated checks.

## Reproduction process/container failure boundary

An actual isolated Docker-client timeout demonstrated that `--rm` alone does not
remove a container when the client is killed. The reproduction helper now starts
each command in its own process group and terminates it on timeout/interruption,
retaining partial output. Finalization enumerates the exact build/ownership-repair
container, verifies its immutable ID and `sdv.reproduction.run` ownership, then
removes only that ID. Ambiguous identity, unavailable Docker or mismatched ownership
fail without deletion and override an otherwise successful result.

Real timeout probes verify removal and refusal of a differently owned container;
the latter is retained until the probe's separately verified owner removes it.
A controlled external Docker-error fixture verifies that daemon unavailability is
not mistaken for successful absence. Actual child-process and SIGINT/SIGTERM tests
verify termination, captured output, failed manifests and conventional interruption
exits. An actual clean-source native build was started and deliberately interrupted:
the build verdict remains failed, both container cleanup records pass and no owned
containers remain. This is cancellation evidence, not native build acceptance.

The updated process wrapper then passes42 actual native core assertions with cached
validated binaries. Owned testbench teardown and all seven original comparisons pass.
Twenty Python regressions, affected compilation and whitespace checks pass. T015 is
closed; unchanged native components were not rebuilt to claim a new successful build.
The real second contributor and actual human rehearsal remain outstanding acceptance.
