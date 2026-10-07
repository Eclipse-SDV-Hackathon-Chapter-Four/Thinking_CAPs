# Open Vehicle Lifecycle feature backlog

Prepared on 2026-10-04. User instruction: defer AAOS FOTA until its asset is brought later.

| ID | Priority | Status | Next acceptance / dependency |
|---|---|---|---|
| F001 baseline audit | P0 | audit complete; original live gate subsequently resolved in F009 | Pins, source interfaces, upstream audit and preserved initial runtime blockers |
| F002 receiver diagnostics | P0 | implemented; real receiver L2 verified | Minimal S-CORE instrumentation + native OpenSOVD provider; unknown/stale contract tests, live sample comparison |
| F003 openDuT testbench | P0 | implemented; real two-peer local Ethernet verified | Isolated two-peer Linux environments, interface attachments and real traffic evidence |
| F004 fault lifecycle | P0 | implemented; native IPC/storage/history verified | Build reporter/DFM, receiver watchdog, query mapping; native HTTP faults conditional |
| F005 campaign/evidence | P0 | implemented; 42 fixture checks and 46 real CARLA/native checks pass | Native lifecycle and physical control-path evidence; explicit harness operator inputs |
| F006 AAOS update | deferred by user | deferred | Wait for real FOTA asset; no substitute installer or simulated successful update |
| F007 optional extension | P1 | deferred | Select at most one after stable core, maintainer-aligned scope |
| F008 reproduction/handover | P0 | clean-source self-run passed; local handover prepared | Actual second-person signoff deferred by user; source/build/cache boundaries and contribution packet documented |
| F009 CARLA startup recovery | P0 | actual world/actor/native campaign verified | Fresh startup clients, test-driver steering and explicit compiler paths; human signoff still pending |
| F010 diagnosis/test dashboard | P1 | implemented; actual native/physical/cancellation verified | Browser OpenSOVD diagnosis and openDuT-managed project campaigns; dual-client state and scoped evidence download |
| F011 ThreadX zonal lighting | P1 | implemented; real ThreadX Linux port/CAN/CARLA verified | [CAN contract and standalone deployment](../demo/X-Verse/external_hackathon_ecus/ThreadX/README.md) |
| F012 AutoSD vehicle computer | P1 | implemented; fresh guest, native lighting diagnostics and actual managed GRE/CARLA verified | [Component specification](../AutoSD/specs/vehicle-computer/spec.md), [deployment guide](../AutoSD/README.md) and [evidence](../AutoSD/artifacts/README.md) |

See specs/001-baseline-audit for F001. Each later feature gets its own Spec Kit artifacts
when admitted; do not roll all features into a single specification.
Primary proposed contribution: receiver-to-OpenSOVD integration example/tests. Existing owner
of #156 retains native fault routing scope; no outreach or public PR has been sent.

See [handover.md](handover.md) for the verified native/physical slice, resolved CARLA client startup,
reproduction and continuation. F007 remains unadmitted; the primary integration is verified and human reproduction
is deferred by the user. Runtime additions use bounded component specifications.
The user's newer ThreadX/AutoSD implementation requests are covered by F011/F012;
the [feasibility proposal](optional-runtime-integration.md) remains historical.
No judging result or awarded bonus is established. F008's prepared local
deliverables do not complete the human acceptance. F009 verifies the selected physical campaign;
it is not a real AAOS-update or broader vehicle safety acceptance.

The user added F010 explicitly: [dashboard specification](../specs/010-diagnosis-test-dashboard/spec.md)
and [completed quality checklist](../specs/010-diagnosis-test-dashboard/checklists/requirements.md).
The saved campaign replay is historical evidence, not this live dashboard.

The latest instruction skips second-contributor reproduction for now and admits
F010 implementation. See [dashboard.md](dashboard.md) for actual UI/run/evidence
behavior. The signoff form remains empty; no independent human reproduction is claimed.
