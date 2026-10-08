# Follow-up source review — Communication #1167

Agent recommendation: retain the revised integration test and separately review the root BUILD checker-path utility. This is an engineering recommendation for PR head `2aead7cd18c96b907e086c8b59797b527f65567d`, not a human acceptance or copyright waiver. Final-source Host verification is recorded under [run 37652549770](../runs/37652549770/1/summary.json); inspect its terminal result rather than extending predecessor results to this source.

| API | Observable acceptance condition in the test |
| --- | --- |
| OfferService | First offer discovers exactly one configured instance; duplicate offer preserves the complete discovered handle container. |
| StopOfferService | Each of two stops leaves service discovery empty; a later offer restores availability. |
| StartFindService | Three calls with the same callback/specifier each report the unchanged service container; all returned operations are stopped. Native distinct operation handles are retained. |
| Subscribe | Same sample limit is used twice; state stays subscribed; subsequent samples match exactly; resubscription after unsubscribe delivers a second exact sequence. |
| Unsubscribe | Each of two unsubscribes makes GetNewSamples return kNotSubscribed; resubscription recovers delivery. |

Repeated-discovery callback state remains in RunApiIdempotencyTest, so extracting CheckRepeatedDiscovery does not shorten the mutex/vector lifetime. Each callback copy captures references to these persistent objects. The instance-specifier reference remains valid because its Result owner spans the whole test. The entry point now stays in the existing anonymous namespace, satisfying internal-linkage and anonymous-namespace checks together. The final correction changes linkage spelling and namespace boundaries only; assertions, finite deadlines, samples and cleanup are preserved.

The integration harness requires exit zero, including rejecting signal exits accepted by the general WrappedProcess helper. Production APIs and all 17 execution controls are unchanged. The native test configuration is QM LoLa on Linux. TSan retains its shared Docker-integration exclusion; no skipped runtime is counted as a pass. QNX is excluded by the user's instruction.

The pinned checker comparison at upstream `cef680454e8586daca9f953084dca33fb3759d0c` has 200 identical inherited findings and zero additions from this contribution; seven header-eligible changed files pass. The two JSON configurations have no native header template. Retaining the failed global check and complete inventory gives maintainers a concrete disposition without fabricating a waiver or attributing later upstream header changes to this PR.

The decision rationale is that observable repeated-call behavior is tested through the real binding, false-positive process outcomes are rejected, introduced lint findings are corrected without changing policies, and independent sanitizer/build evidence accompanies the exact source. This supports review of the scoped contribution; native required statuses, code-owner acceptance, inherited-copyright handling and merge-queue verification remain upstream responsibilities. Original contributor acceptance stays bound to its original measured source.

Reviewed source and execution controls were independently hash-bound on 2026-10-07T16:46:10.014182+00:00. Source archives and the minimal follow-up patch are retained alongside this review.
