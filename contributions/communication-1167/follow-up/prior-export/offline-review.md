# Communication issue #1167: offline review packet

Status: draft contribution; required repository checks remain failing. The finite supervisor stopped after all three authorized correction attempts. No further model calls or source corrections are authorized by this run. Engineering acceptance, ECA verification, publishing, merging and issue closure remain pending or unauthorized.

Final measured run: `01M4763VYCDPHEFTXW92SX6ETF`. Fabro completed its export workflow successfully; that status does not signify passing native verification or engineering acceptance.

## Proposed contribution

`communication-1167.patch` contains eight new files under `score/mw/com/test/api_idempotency/` plus a root BUILD correction for copyright-checker file paths. `candidate/` contains the complete uncommitted source tree. Production communication implementation is unchanged.

The dedicated LoLa integration test exercises repeated OfferService and StopOfferService, three StartFindService registrations and cleanup, repeated Subscribe and Unsubscribe, receipt of samples, rejection of receipt while unsubscribed, resubscription and re-offering. It uses the native Docker integration harness and finite five-second polling bounds. Distinct discovery registrations are cleaned up individually; identical handles are not asserted. The root BUILD correction changes label-like copyright inputs to repository-relative filesystem paths.

## Fresh native verification

| Command | Result |
| --- | --- |
| `bazel run //:copyright.check` | FAIL, exit 1: repository-wide missing, malformed and duplicate headers |
| `bazel run //:format.check` | PASS |
| `bazel test //score/mw/com/test/api_idempotency/... --nocache_test_results` | PASS: integration and configuration-schema tests, 2/2 |
| `bazel build //...` | PASS |
| `bazel test //... --nocache_test_results` | FAIL, exit 3: 502 passed, 1 failed, 6 skipped, out of 509 targets |

The sole full-suite test failure is `//quality/visibility_guard:visibility_guard_test`. Its comparison reports 78 expected public targets versus 2 observed, with 76 removed. The nested query collector ignores query failure diagnostics, so an environment/query failure is a possibility; the cause has not been independently confirmed. The golden file was not regenerated.

The copyright log reports no findings under the new `api_idempotency` directory. Outstanding findings are outside that directory. A separate clean-baseline verification was not performed, so these findings are not certified as pre-existing. All failures and skipped tests remain review obligations.

`verify-result.json` binds every fresh check to this final run and the full source hash map. `evidence/` contains raw stdout/stderr, per-command metadata and native test logs/XML. The visibility failure log is `evidence/native-testlogs/quality/visibility_guard/visibility_guard_test/test.log`. `workspace-subject-match.json` records 2,885 matching source files; generated Ruff caches were identified separately. Build action caches were retained, while both test invocations disabled cached test results. No earlier check result was carried forward.

## Provenance and limits

- Stable fabric: `b2aa9a7a49a054621f38e59f3aef6d6e5daf3cce`.
- Native Communication baseline: `e3d126c2d7569345cf5f790310702eb00cd86b06`, branch `test/1167-api-idempotency`.
- Fabro source pin: `1b4fb15281ebb724426f9e480dce48d0100ff79b`.
- Bazel 8.7.0, Ubuntu 24.04.4 container; exact local image ID and measured tool hashes are in `build-environment.json` and supervisor authority files. The local image has no registry digest; no upstream image identity is claimed.
- Disposable build storage remained bound to the registered ext4 `/dev/loop27` volume. Private credentials and server state remained internal. The concurrently optimized fabric checkout and native reference checkout were not modified.
- Original draft plus three supervised correction prompt stages consumed the complete attempt allowance. The earlier failed supervisor stages and orchestration errors are retained under `supervisor-attempts-01/`, `supervisor-attempts-03/` and verification-attempt records. Verification-only continuations made no paid calls or source fixes.
- The authorized configured model was `deepseek-v4-flash` with no fallbacks, and a $10 maximum. Published-capacity reservation for the four prompt stages was $9.437184, including bounded transport retries. This is a conservative reservation, not an invoice. Billed cost is not confirmed; native cost estimates use stale catalogue pricing and are not represented as billed spend. See `final-budget.json` and preserved pricing evidence.

`native-artifacts/` contains the built test executable, datatype libraries and OCI filesystem layer, each hashed and linked to source/run provenance. The layer alone is not a complete standalone container image. Apache licensing and original notices remain in `candidate/LICENSE` and source files. Historical packets, workflow definitions, draft responses, native states and refusal records remain available locally without Fabro.

## Offline reviewer obligations

Review test semantics against issue #1167 and upstream CONTRIBUTING.md, determine and address the copyright and visibility failures, assess the six skipped tests, and verify ECA eligibility. Native source identifiers or requirements were not invented; any traceability and applicability decision remains explicit and pending. Do not interpret successful tests or successful workflow execution as human acceptance. No PR or upstream submission has been made.

The dedicated mobile UI remains available on the same Wi-Fi at http://192.168.13.204:43916 . Its login token remains only in the private local-state file; no credential is included in this packet.
