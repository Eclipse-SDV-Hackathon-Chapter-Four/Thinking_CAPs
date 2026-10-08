# F008 implementation plan
## Technical context
Freeze integration6d7bef9, controller93f8ea1 and bridge0d53a2a; explicit receiver/storage patches.
Clean local Git clones (no hardlinks), fresh native Rust target, fresh Bazel output base with
explicit reused LLVM repository and existing pinned Docker assets. No system dependency updates.
## Constitution check
All twelve principles checked. Explicit reused assets/caches, hash provenance, no bridge edit,
no second-person/event/publication claim, actual assertions and scoped teardown.
## Design
scripts/reproduce_core.py creates NEW ignored owned state and clones immutable pins. Apply
receiver patch; compile controller plus unmodified gateway/daemon/config targets in native image,
run existing cruise unit target, derive flatc/schema paths by cquery/info rather than guessing
cache layout. Build native fault profile from the frozen integration checkout with exported patch
and separate lock. Generate explicit config, reuse deployed local openDuT bench, execute core.
Artifacts record source-clean-before-patch, resulting patch hashes, actual binaries/tool IDs and
shared-host/cached-toolchain provenance. A clean-source self-run is not a second person's run.
README/docs/setup/scripts/tests/handover/reproduction and contribution packet become the truthful
entrypoints. Rehearsal shows actual fixture loss/history/recovery and labels CARLA/AAOS blockers.
Readiness recovery can use exact existing CARLA launch flags in a bounded owned probe, with no
system driver changes. Finish with benchmark teardown and original container/source comparison.
## Touch points
scripts/reproduce_core.py; docs/{handover.md,reproduction.md,claim-evidence.md};
contributions/fault-storage-write-through/; README.md; scripts/README.md; tests/README.md;
docs/setup/README.md; docs/prepared-work.md; evidence/f008-*.

Presentation refinement after F009: add an eight-minute technical interview script
and a standalone final-pitch deck below the brief's ten-minute cap. Use the actual
fresh-build core/physical results, labelled offline replay and bounded storage patch;
AAOS/FOTA remains user-deferred. Add speaker notes and evidence links, readable
functional topology, keyboard slide navigation and print output. Verify in an actual
browser; do not label browser checks as a human rehearsal or second-person run.
Touch points: docs/hackathon/{technical-interview.md,pitch.html,pitch-notes.md,README.md},
docs/handover.md and evidence/f008-presentation-browser/.

Reproduction attribution refinement: the helper must record caller-supplied operator
identity and explicit shared-host declaration rather than hardcoding the implementation
agent and this host for every future caller. Record observed hostname/platform/Python
identity separately. Undeclared operator/host-sharing remains unknown; helper execution
never attests independent human reproduction. Verify declared and undeclared metadata
through a bounded real compiler-identity rejection before cloning/building, without
repeating unchanged native compilation. Keep historical self-run manifests unchanged.

Build-failure cleanup refinement: an actual Docker-client timeout leaves its `--rm`
container running. Each reproduction command will run in its own process group;
timeout/interruption terminates that group, allowing bounded graceful cleanup before
forced termination. Finalization inspects the exact build container's immutable ID
and `sdv.reproduction.run` label before removal; absent containers pass, ownership
mismatch or unavailable Docker fail without deletion. SIGINT/SIGTERM produce explicit
failed/interrupted manifests and cleanup records. Preserve partial command output.
Verify actual timeout/owned removal/unowned refusal/process-tree termination and
signal paths, then a native core regression with cached validated binaries. No new
native build acceptance is inferred from the harmless timeout probes.
The new process-boundary regressions live in `tests/test_reproduction_lifecycle.py`.
