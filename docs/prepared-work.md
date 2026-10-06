# Prepared work inventory

All work on 2026-10-04 is preparation, before the stated 6–8 October event.
Integration start revision: a08c5a2 (existing contribution evidence bundle).
Vehicle repositories and local modifications: config/dependencies.lock.json.
Supplied inputs are copied with original content: implementation brief, original strategy,
and Cruise_Control.drawio. The newer user instruction defers FOTA.

New preparation: Spec Kit 0.14.0 scaffold, constitution, F001 audit/specification,
source capability research and subsequent explicitly labelled integration artifacts.
Reused assets: existing CARLA, bridge, S-CORE implementation, OpenSOVD/openDuT and
contribution records. No event-time creation, eligibility, upstream approval or merge is claimed.
Record the real event-start revision here when the event begins; retain actual delta separately.

Preparation checkpoints:

| Revision / artifact | Prepared result |
| --- | --- |
| `a08c5a2` | Existing contribution records and verified artifact inventory committed locally. |
| `a25868e` | F001 audit, actual receiver instrumentation/native OpenSOVD diagnostics, matched local openDuT bench. |
| `6d7bef9` | F004 native reporter/DFM/write-through storage patch and F005 deterministic campaign; 42 fixture-input/native integration assertions passed. |
| F008 handover | Fresh source checkouts/native builds/core self-run passed; shared host/images/LLVM declared. Local upstream patch packet, operator instructions and claim map prepared. |
| F009 startup recovery | Controlled early/late CARLA client comparison; fresh-client retries, explicit test-driver steering and configured-tool fix. Actual physical/native campaign passes46 checks, including67 actuation correlations; fixture regression passes42. |
| `8818b9f` | F010 live dashboard specification/quality checklist and bounded ThreadX/AutoSD feasibility proposal; neither live UI nor proposed runtime integration is claimed as implemented. |
| `e12d489` | Current frozen-source reproduction42 core/46 physical assertions, actual fresh configuration tools and offline source-verified physical replay/browser gates. |
| Presentation/attribution refinement | Eight-minute interview and9:30 browser/print pitch; real browser navigation/layout/print checks. Corrected baseline comparison uses original newline normalization; reproduction caller/host-sharing metadata is explicit. No human rehearsal/signoff claimed. |

Exported upstream changes are `OpenSOVD/patches/receiver-diagnostics/s-core-observation.patch`
and `OpenSOVD/patches/fault-storage/write-through.patch`; their original repositories are
preserved, with implementation isolated in worktrees. The bridge source is unchanged.
CARLA was blocked at the initial handover and resolved in F009. Its physical campaign now
passes; human signoff is pending, AAOS/FOTA user-deferred, and optional
extensions unselected. The [handover](handover.md) links measured evidence and precise
continuation. No event-start revision or event delta is asserted yet.

F009 also found that the original F008 self-run's overlay generation used baseline cached
compiler/schema despite building fresh tools. That historical run still proves fresh native
builds and native campaign acceptance, with this additional shared-asset limitation. F009
fixes tool selection and records the actual fresh compiler/schema paths in real and fixture runs.
