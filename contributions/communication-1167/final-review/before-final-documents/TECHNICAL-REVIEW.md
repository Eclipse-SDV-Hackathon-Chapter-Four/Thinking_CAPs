# Agent technical review of communication #1167

The user delegated this review to the agent. This is a technical recommendation supported by bound source and measured tool records, not a human engineering acceptance, copyright waiver, ECA attestation or publishing authorization. Current subject is `verification-run/candidate/`, native baseline `e3d126c2d7569345cf5f790310702eb00cd86b06`. The stable pre-optimization fabric, same verified image now attached as loop1, original budget and exhausted three-correction supervisor remain unchanged.

## Conclusion

The earlier offer/stop state comparison and repeated callback coverage gaps are addressed in source. Review found one additional false-positive in the integration harness: the upstream WrappedProcess accepts exit 137/143 by default, allowing an externally interrupted application to count as a pass. The isolated final candidate now explicitly requires exit code 0 after the wrapper context exits. Eight fixture cases using the actual pinned wrapper and fake process exits reproduce the previous behavior and show rejection after correction. These microchecks are not native-readiness evidence; all five required native commands are rerun separately in Fabro `01M4878Q65ENC6PJ5AEJ6NMWB3`. The preceding real test application exited 0, so its previously reported pass remains authentic.

Formatting, focused integration/schema tests and the full build have passed for this corrected harness. Full-suite completion is pending. Copyright still has exactly the 204 normalized baseline findings, with no additions. The agent recommends retaining this scoped test contribution and the separately exported checker utility correction for review, without repairing unrelated existing headers or silently waiving the failed check.

## Source assessment

| Subject | Assessment and evidence |
| --- | --- |
| OfferService | Success checked on both calls; first result must contain the single configured service handle; complete discovered container compared after duplicate call. Main source:146–156. |
| StopOfferService | Discovery must be absent after each stop, then re-offer/final stop demonstrate recovery/cleanup. Main source:291–300. |
| StartFindService | Same callable and instance specifier passed three times. Per-operation callback results are associated by the echoed FindServiceHandle under a mutex and compared with the original complete service container; all returned operations are stopped. Main source:159–219. |
| Subscribe | Identical sample limit on both calls; state remains subscribed immediately after the duplicate; exact first sample sequence is received, followed by later successful resubscription. Main source:235–281. |
| Unsubscribe | Both calls are followed by GetNewSamples rejection with kNotSubscribed; resubscription and a second exact sample sequence verify recovery. Main source:259–286. |
| Callback lifetime/locking | No application mutex is held when StopFindService is called. Native StopFindService locks worker_mutex_; native unit test explicitly checks it blocks until an ongoing handler finishes. Captured results/mutex outlive all stopped operations. Sources: service_discovery_client.cpp:267, service_discovery_client_stop_find_service_test.cpp:212. |
| Failure propagation | Native FailTest uses _Exit(EXIT_FAILURE). Native WrappedProcess wait raises on timeout, and the new harness additionally rejects every nonzero exit, including the default-allowed signal exits. The fixed predicate is checked in before/after negative cases. |
| Scope/configuration | One explicitly configured QM SHM instance; service ID 3431 is unique among current test manifests. New IDs are fixture configuration, not invented process/requirement IDs. Production source, API golden and module lockfile are unchanged. Native schema validation passes. |
| Integration/portability | Uses native pkg_application, integration_test and wrap_exec; finite five-second poll deadlines; native process wait is bounded. C++17/toolchain, format/check commands and native Ubuntu image pins are retained. No QNX runtime or broader safety/compliance qualification is claimed. |

### Discovery semantics

The public FindServiceHandle documentation describes distinct searches (find_service_handle.h:33), and service_discovery.cpp:90 allocates a fresh operation handle. Native tests named CallingStartFindServiceTwiceWithTheSameIdentifierDoesNotAddAnotherWatch, CallingStartFindServiceTwiceWithTheSameIdentifierCallsBothHandlersWhenServiceIsOffered, and CallingStartFindServiceOnOfferedServiceTwiceWithTheSameIdentifierCallsBothHandlers establish the intended distinction: repeated searches share the watch while separate operations retain callbacks. The contribution therefore preserves operation identities and tests unchanged discovered service state with identical caller arguments. It does not assert equal handles or prove all internal resource invariants.

This source-grounded interpretation supports the test shape. Acceptance of the issue's state-invariance intent remains a human-owned engineering decision. Prior review questions 01/02 have an agent disposition of source coverage addressed; no human review status is manufactured. Exact source hashes and case names are in `source-review-bindings.json` and the native-case correspondence records.

## Copyright disposition proposed by the agent

Exactly 204 current normalized findings equal the baseline-with-checker-path-overlay: 96 missing headers, 93 wrong-format headers, 14 headers preceded by other content, and 1 duplicate. The current contribution adds no normalized finding. These remain failed measurements, classified as pre-existing baseline findings rather than false positives, waivers or accepted deviations. The untouched baseline copyright command failed before scanning label-like BUILD/MODULE inputs; the overlay fixes only those paths, and that limitation stays explicit.

The two-file input-string correction in existing BUILD is retained in its own patch so the issue's test change and utility repair can be reviewed independently. The agent recommends treating inherited header repair as separate scope. The original issue's test patch and combined utility/test patch remain available; no scope decision is attributed to a human.

## UI and authority

The UI requested by the user is **fabro_dashboard**, served by fabro-monitor.service at **http://172.18.17.0:8787** on the current Wi-Fi network. The dashboard already shows the dedicated source `someip`, this run and its workflow graph. The native API is http://127.0.0.1:43916, separate from the monitor. No dashboard code/configuration was changed, and no credential is exported to its browser or contribution packet.

No additional model calls, supervisor retries, provider defaults or human nodes are present in the current verification workflow. Native completion routes failures to export; it does not imply all checks pass. ECA status remains unverified and native CONTRIBUTING.md requires it for submission. No PR, merge, issue closure or publication was performed. Repository AGENTS.md states: "Agents draft; deterministic tools measure; authorized humans accept engineering decisions." This report completes the delegated agent review while preserving that human authority.
