Adds one LoLa integration test covering repeated `OfferService`, `StopOfferService`, `StartFindService`, `Subscribe` and `Unsubscribe` calls. It compares discovered service identity/cardinality after duplicate offers, verifies absence after each stop, checks subscribed state and rejection after each unsubscribe, and verifies sample delivery and recovery with finite deadlines. The harness requires the application to exit 0.

Repeated discovery uses the same callback and instance specifier. Each returned search operation is checked for unchanged discovered service state and stopped; distinct operation handles follow the native implementation and existing watch-sharing/callback tests. Production APIs are unchanged.

The existing copyright checker BUILD/MODULE.bazel input strings are also corrected to filesystem paths. This root BUILD change is isolated from the new test directory for independent review.

Relates to #1167.

Validation on `e3d126c2d7569345cf5f790310702eb00cd86b06` with Bazel 8.7.0 and Ubuntu 24.04.4:

- Full build and formatting pass.
- Dedicated integration/schema tests: 2/2 pass; application exits 0.
- Full suite: 503 pass, 0 fail, 6 platform/configuration targets skipped; QNX runtime was not executed.
- Copyright reports 204 findings identical to the baseline with the checker-path correction, with no added findings. The untouched baseline checker fails before scanning its label-like paths. Inherited header repair remains separate scope; no waiver is claimed.

The published commit preserves the exact measured source tree (`1d790b6182be2fed1794bb287f8f9a868bde685f`). The patch also applies cleanly to upstream `c77751819b8885a902540dbef7f0fe25cf85d51c`, checked 2026-10-07. That newer upstream production subject has not been executed in the local native suite; the results above belong to the explicitly pinned baseline. Upstream CI will validate the proposed merge subject.

The 204 inherited copyright failures remain unresolved and require maintainer disposition or separate remediation. Technical acceptance is limited to the measured Ubuntu scope; no copyright waiver or broader platform qualification is claimed.
