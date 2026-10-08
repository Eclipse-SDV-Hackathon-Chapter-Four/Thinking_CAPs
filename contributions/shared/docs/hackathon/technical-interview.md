# Eight-minute technical interview

Prepared 4 October 2026. This is a rehearsal script for the implementation in this
repository, not a record of a human rehearsal. Confirm the assigned slot with the
organizers. AAOS/FOTA is deferred by the user; no update step is demonstrated.

| Time | Presenter action | Evidence and claim |
| --- | --- | --- |
| 0:00–1:00 | State the problem: a running diagnostic service does not prove that the vehicle receiver has fresh inputs. Show the existing vehicle/control path and separate diagnosis/fault processes. | The actual receiver is instrumented; the existing bridge and control algorithm are reused. [Functional view](pitch.html#slide-2), [receiver patch](../../OpenSOVD/patches/receiver-diagnostics/s-core-observation.patch). |
| 1:00–2:00 | Run the already prepared physical campaign or open its live evidence view. Show actual motion, accepted receiver speed, target/engagement and returned native control. Explain harness pedal/engagement/steering and native/VCU throttle. | [Physical results](../../evidence/f009-reproduction-physical/results.json), [actuation correlation](../../evidence/f009-reproduction-physical/native/carla-control-return.json). A positive throttle value alone is insufficient. |
| 2:00–3:00 | Show the owned GRE interruption, increasing accepted-data age and the debounced lost-communication fault while diagnosis remains reachable. Distinguish loss of the selected flow from a claim about its physical root cause. | [Recorded events](../../evidence/f009-reproduction-physical/native/events.json), [actual diagnostic responses](../../evidence/f009-reproduction-physical/native/requests.json). Declared monitor budgets: 300 ms age, 100 ms debounce, 150 ms held recovery. |
| 3:00–4:00 | Restore traffic and show freshness/recovery with fault history retained. Show diagnosis stalled while control return continued, and the diagnostic/DFM process restart retaining native history. | Assertions establish the selected lifecycle. Recovery does not assert automatic Cruise Control re-engagement. Native fault history uses labelled App data; native fault routes remain conditional. |
| 4:00–5:00 | Open the small storage patch. Explain the original cache-only acknowledgement and the opt-in write-through acknowledgement. Show the original failing new-process regression and the patched native gates. | [Contribution packet](../../OpenSOVD/contributions/fault-storage-write-through/README.md), [original failure](../../OpenSOVD/evidence/f004-unpatched-process-restart.txt), [native tests](../../OpenSOVD/evidence/f004-native-nightly-tests.txt). Process-restart persistence, not hardware/power-loss durability. |
| 5:00–6:00 | Show frozen revisions, image/config/binary identities, clean-source builds, result categories and owned teardown. Identify preparation, fixtures, real simulation and pending second-person signoff. | [Current source reproduction](../../evidence/f009-reproduction-current/verification.json), [preservation recheck](../../evidence/f009-preservation-recheck/verification.json), [signoff](../reproduction-signoff.json). No public submission or maintainer approval is claimed. |
| 6:00–8:00 | Questions. Use the detailed architecture, recorded timeline and patch on demand. Finish with the reusable integration and the exact next acceptance. | [Original architecture](../architecture/Cruise_Control.drawio), [claim map](../claim-evidence.md). A real second contributor must run and sign the documented campaign. |

The windows total **8:00**, including **2:00 for questions**. The final pitch has
its own [9:30 deck and notes](pitch-notes.md); the two formats are not interchangeable.

## Live prerequisites and fallback

Follow [reproduction.md](../reproduction.md) before the interview. Use new output
directories, freshly generated private openDuT state and validated image/source/tool
inputs. Prepare native builds before the timed interview. The documented runner
uses actual CARLA when `--scenario carla` is selected; it never substitutes fixture
input for that scenario. Allow the bounded launch to complete before describing
its observations as live. The Test Manager dashboard is specified, not implemented.

```sh
/usr/bin/python3 scripts/run_campaign.py --config .local/campaign.json --scenario carla --output evidence/interview-physical
```

Say “live” only for the current run. If the environment is unavailable, open the
[saved physical replay](../../evidence/f009-recorded-replay-final/index.html), say
“recorded run, prepared 4 October”, and inspect the saved verdicts. It performs no
live requests or injection and cannot establish current vehicle health. If only the
fixture campaign is available, state that vehicle input is a fixture while the
receiver, fault components and managed network are real.

The live campaign performs scoped application/link cleanup; the separate bench
teardown is still required. After the presentation, inspect the current results
and run the documented owned `down` operation. A failed or blocked live attempt
stays failed or blocked even if its saved fallback looks successful.
