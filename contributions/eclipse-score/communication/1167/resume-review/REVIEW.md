# Offline contribution review: Communication #1167

This is an agent review draft, with engineering acceptance pending. The saved checkpoint and all 21,553 listed artifact hashes were verified. All 2,885 contribution source hashes still match the measured source, and the combined patch exactly matches the current uncommitted candidate diff. The contribution guidelines and license snapshots match the native baseline. No source was changed and no new model call or native run was made.

The saved final run `01M47TK6AQAR009HFM6QDPFV7A` passed the full build, formatting, dedicated integration/schema tests (2/2), and every executed full-suite test (503 passed, 6 skipped). These are **carried measured results**, bound to the unchanged source; they are not new test executions or engineering approval. The full guideline check set remains failing because copyright verification reports 204 findings.

## Test coverage

| API | Observed test behavior | Review status |
| --- | --- | --- |
| OfferService | Two success results, discovery available, and later sample delivery | Missing comparison of discovered state/cardinality before and after the second call |
| StopOfferService | Two calls, subsequent absence, re-offer works, final absence | Missing absence check after the first stop before repeating it |
| StartFindService | Three registrations with separate indexed callbacks discover the service; each handle is stopped | Repeated identical callback arguments and unchanged discovery state are not demonstrated |
| Subscribe | Subscribe twice with the same sample limit, receive 101/102/103; resubscribe and receive 201/202/203 | Measured operational coverage; semantic adequacy remains review-owned |
| Unsubscribe | Two calls, GetNewSamples reports kNotSubscribed, resubscription receives samples | Measured operational coverage; semantic adequacy remains review-owned |

### Review question 01: StartFindService

`main_api_idempotency.cpp:148` constructs a new callback for each index, changing the handler argument on each iteration. The test therefore proves that independent discovery registrations work and can be cleaned up. It does not test repeated identical arguments or establish the unchanged state described in issue #1167. This is a coverage gap, not a finding that the production API is defective.

The pinned native documentation at `candidate/score/mw/com/impl/proxy_base.h:97` describes continuous discovery and a handle controlling the operation. It does not establish that repeated registrations must return equal handles. A reviewer should settle the observable state and registration semantics, then strengthen the test using the same callback and specifier where appropriate. Preserve every valid returned handle for cleanup; do not add an unsupported handle-equality assertion.

### Review question 02: Offer/stop state comparisons

At `main_api_idempotency.cpp:138`, two offers occur before the first availability check. At line 251, two stops occur before absence is checked. Nonempty discovery after both offers could allow duplicate entries; absence after both stops could allow an incorrect first stop to be masked by the second. Checking the relevant discovered state after the first operation and again after the duplicate would make the idempotency claim more direct. No patch was applied during this review.

## Copyright and scope

The measured candidate and baseline-with-path-overlay produce the same 204 normalized findings: 96 missing headers, 93 wrong-format headers, 14 headers preceded by other content, and 1 duplicate. No finding was added by the new test directory. `follow-up/copyright-comparison.json` contains the complete normalized comparison and raw log hashes.

This does not make the copyright command pass or waive the contribution guideline. The untouched baseline checker fails before scanning because its BUILD inputs use label-like strings. The baseline comparison applies only the existing filesystem-path correction, matching the candidate utility change. Its unchanged 2,877-source hash vector was reverified in the earlier follow-up. That baseline result is carried. During this resume, all 2,877 baseline-with-overlay hashes also matched the exported candidate projection, with exactly the eight new test files outside that projection (`baseline-subject-reverification.json`). The original external workspace and tool environment cannot currently be checked again.

The combined contribution patch contains eight test files plus the root BUILD utility correction. Separate reviewable patches are `follow-up/issue-1167-tests.patch` and `follow-up/copyright-checker-paths.patch`. The measured full source includes both. Whether the utility fix should accompany the issue contribution or be proposed separately remains an offline scope decision.

## Six skipped targets

`follow-up/skipped-tests.json` retains every target name. The dual-QEMU example and qnx_dispatch_test explicitly require QNX. typed_memory_test selects QNX only with its typed-shared-memory configuration, otherwise an incompatible constraint. The three Rust targets ending in `_qnx` are QNX counterparts generated by `quality/unit_testing/unit_testing.bzl:149`; the forwarding rule selects the Linux counterpart for the default platform. These declarations explain the qualification scope, but do not constitute QNX execution evidence or human acceptance of the skips.

## Resume limits and remaining work

The saved SSD (UUID `002B-CE31`), image and `/dev/loop27` are unavailable at resume; no matching USB device was observed. Native execution remains stopped, and the bound workspace was not relocated. Reconnect the saved SSD and restore/validate the existing image binding before any native execution. No new run is needed to retrieve the saved passing full-suite result.

The three-attempt supervisor remains exhausted. The original draft plus three correction prompts are retained; maximum authorized Fabro spend is $10, conservative reserved bound $9.437184, billed cost unconfirmed. This resume consumed no additional paid calls and changed no contribution source. ECA verification, review of the coverage gaps, copyright disposition, skipped-test qualification and engineering acceptance remain pending. No PR, publishing, merge or issue closure is authorized or recorded.

The local `PR-DRAFT.md` is prepared for review. Resolve the open questions before submission. Source/evidence digests and the two local review identifiers are in `resume-review/review.json`; those identifiers are local report labels, not invented S-CORE native trace IDs.
