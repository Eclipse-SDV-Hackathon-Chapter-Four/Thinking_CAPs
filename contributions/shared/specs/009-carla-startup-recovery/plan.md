# F009 plan
## Technical context and decisions
Reuse `contributions/shared/scripts/owned_carla.py`, unchanged existing vehicle/VCU classes and native campaign.
Wire diagnostic proves version RPC works in owned null-RHI server; late fresh native Python
client also succeeds. Existing readiness constructs a client before server bind, then reuses
it after connection errors. Diagnose with a controlled early/late/world comparison before
assigning cause. Retry fresh client instances with two worker threads within monotonic deadline.
Use actual NVIDIA/offscreen baseline assets for physical acceptance; null-RHI is only diagnosis.
Initialize plant before starting native diagnostics/controller in CARLA mode. Startup-unknown
assertions still precede publishing; fixture mode order remains unchanged.
## Constitution check
All twelve principles: preserve original sources/bridge; bounded integration-owned changes;
feature artifacts before edits; actual native/physical evidence; separate processes/provenance;
explicit pins/configs; deterministic checks and cleanup; prepared work/human gap; no external
communication, update activation or optional extension.
## Touch points
contributions/shared/scripts/owned_carla.py; contributions/eclipse-opendut/OpenDut/tests/opendut_receiver_smoke.py; meaningful readiness tests;
contributions/shared/specs/009-carla-startup-recovery; evidence/f009-*; contributions/shared/docs/handover.md and claim-evidence.md.
## Verification
Controlled real RPC client comparison, readiness retry/deadline tests, actual owned plant,
real CARLA/native campaign with unchanged required verdicts, fixture regression if deployment
order changes, scoped teardown and original-state checks. No full vehicle claim from version only.

Runtime evidence refinement: the first physical/native campaign's actor moved to61km/h but
stopped before nominal acceptance with pedal/throttle still applied. Supply bounded waypoint
steering as explicit test-driver input on the existing manual steering topic, without altering
X-Verse/control/bridge code or overriding native throttle. Record requested/applied steering
and actor position. Keep all physical/native assertions unchanged. Preserve explicit compiler/
schema configuration during service overlay creation and record the actual executed paths.

Handover refinement: `contributions/shared/scripts/render_campaign_replay.py` and `contributions/shared/templates/campaign_replay.html`
create a standalone offline historical trace playback from saved real campaign observations,
physical samples and event timestamps. Preserve actual verdicts and input hashes. Do not
reclassify historical values as live, interpolate fault health or calculate new runtime verdicts.
