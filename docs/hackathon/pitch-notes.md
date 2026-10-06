# Final pitch notes — 9 minutes 30 seconds

Prepared 4 October 2026. Open [pitch.html](pitch.html) in a browser. Use the Previous/
Next buttons or arrow keys, Home/End for first/last, and Print for an offline copy.
The elapsed clock is a rehearsal aid, not a measured human rehearsal or test timer.
Confirm the event's assigned duration; this script fits the brief's ten-minute cap.

| Slide | Window | Speaking goal |
| --- | --- | --- |
| 1 — Diagnose what the receiver actually consumed | 0:00–1:00 | A stale input can coexist with a reachable service and a running controller. Explain the contributor/operator need and the evidence-first solution. |
| 2 — Keep the vehicle path intact | 1:00–2:15 | Follow CARLA/VCU → original bridge → actual openDuT network → native S-CORE receiver, and the return direction. Diagnosis observes the receiving application in a separate process. Do not imply that every component in the original architecture is deployed. |
| 3 — Disturb, diagnose, recover | 2:15–4:45 | Show a current physical run if ready; otherwise explicitly show the recorded replay. Explain initial unknown, nominal accepted samples, managed interruption, timed fault, held recovery, stalled diagnosis and retained history. State which controls the harness supplies and which come from native Cruise Control. |
| 4 — A narrow, reusable storage contribution | 4:45–6:15 | Explain the cache-only acknowledgement defect, the failing new-process regression, opt-in write-through and native checks. Preserve the default policy and surface backend errors. State the in-memory-on-flush-failure and hardware-durability limits. |
| 5 — Evidence at the level actually verified | 6:15–7:45 | Show42 core/46 physical assertions, source-clean builds with shared host/images/LLVM, native/VCU/actor correlation and cleanup. Ten conditional/deferred checks are skipped, not passed. A human has not yet reproduced the campaign. |
| 6 — A UI and useful extension path | 7:45–8:30 | The requested OpenSOVD Diagnosis/openDuT Test Manager dashboard has a specification with a completed quality checklist; live implementation is pending. ThreadX and AutoSD have useful proposed roles, not deployed components or awarded bonuses. These are continuation items, not present capabilities. |
| 7 — Hand over something another contributor can use | 8:30–9:30 | Point to the patch, campaign, pinned setup and evidence. Ask the audience to assess the bounded contribution and reproduce the core. Explain prepared work, future event-start delta and pending upstream/human steps. |

Total: **570 seconds = 9:30**. Leave the remaining margin for transitions; if a
live launch overruns, switch to the labelled saved replay and retain the live
attempt's actual verdict. Questions use the assigned event Q&A slot, outside this
script's target duration.

## Questions to answer precisely

- **Is this production safety evidence?** No. It is a bounded integration and
  deterministic campaign on actual native components and a simulated physical actor.
- **Is the diagnostic fault proof of why the wire failed?** It proves receiver
  observation loss under this injection, not an independently identified physical cause.
- **Did you rewrite the bridge or controller?** No. Receiver observation is a
  separate exported patch; existing control code and bridge source are preserved.
- **Does recovery automatically re-engage Cruise Control?** That is not claimed;
  the defined monitor recovery policy and application state are separate observations.
- **Are faults exposed through native fault routes?** The current native fault
  library is used, while the history resource is an explicitly labelled App data
  fallback. Upstream native fault routing remains conditional.
- **Is persistence a power-loss guarantee?** No. The demonstrated contract is
  acknowledged write-through and separate-OS-process reload; hardware durability
  and recovery of an in-memory mutation after a flush failure are not guaranteed.
- **Did another person reproduce it?** Not yet. The clean-source self-run shares
  this host/images/LLVM. The signoff form remains pending.
- **Did the update succeed?** AAOS/FOTA was explicitly deferred; there is no update
  claim or simulated update demonstration.
- **Did the community accept the patch?** Local review artifacts and native gates
  are available. Publication, ECA/full CI, owner agreement and merge are pending.
- **What earns technology points?** Verifiable use under the official scorecard.
  openDuT has actual networking evidence. ThreadX/AutoSD are proposed extensions,
  so their potential bonuses are not claimed as earned.
