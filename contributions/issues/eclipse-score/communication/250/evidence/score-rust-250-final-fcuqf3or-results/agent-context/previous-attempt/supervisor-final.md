# Communication #250 — frozen source review, correction 2

The frozen implementation is **not verified**. The first native group failed to build with Rust E0560 before any cases executed; five remaining planned groups are unexecuted. Independent static review identifies a second C++ compilation blocker and coverage/identity limits below. No passing wildcard, cancellation, compatibility or analyzer evidence is established for this source.

This supervisor reviewed source and retained logs read-only. No source/control/ledger edit, build/test, retry, model call or dispatch was performed. Only this report was written. This review does not spend another correction or accept an engineering decision.

## Frozen binding and measured failure

Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Shared storage validation passed. Fresh hashing confirms every one of the 2,883 current measured subjects equals `check-source-subjects.json`, SHA-256 `bc02f75e155744790166426c91ce4d891a02562089ddf4c2f2b7b7c734f2ef9b`. There are 19 changed/added files relative to the 2,878 baseline subjects and no removed baseline subject. The reviewed changes stay within the authorized paths; protected module/lock/license/policy subjects remain unchanged.

`execution/native-result.json` reports one failed test-command group, exit 1, with zero test records. Its checked raw log records `test_com_api_any` FAILED TO BUILD, not a failing test assertion. Effective plan contains six groups; the other five have no passing measurement. The invoked group's collector time is 158.407 seconds; native Bazel time and wrapper timing must not be conflated. Final lifecycle and Flash supervisor are separate later evidence.

## Blocking defects

**S1 — Rust initializer names a nonexistent field.** `com-api-runtime-lola/consumer.rs:1017–1018` constructs `ServiceDiscoveryFuture { find_guard, ... }`, while line 1059 declares `_find_guard`. Raw `check-0.log` independently confirms E0560 at line 1018, recommending `_find_guard`. Align the initializer and declaration in any authorized correction; the owning guard must remain captured by the outer future and stored in the inner future. Merely removing the guard to compile would reintroduce the cancellation leak.

**S2 — new C++ registration macro omits the object type.** `com-api-ffi-lola/registry_bridge_macro.h:824` contains `id##_interface_reg_instance;` at namespace scope. It must declare the registration helper instance; the existing macro at line 782 contains `id##_InterfaceRegistrationHelper id##_interface_reg_instance;`. The new macro is used by BigData and three selector-test registrations, so it is not dead code. This is an independently observed static compilation blocker; the first native command stopped at the Rust error before supplying a C++ diagnostic for it. Preserve this distinction.

## Ownership, semantics and coverage dispositions

**S3 — actual ownership approach is narrower and avoids synthesis.** Contrary to the first plan's Runtime deque proposal, final `ResolveFindAnyIdentifier` uses `IRuntime::resolve` on an explicitly registered configured selector. It accepts exactly one LoLa identifier with an unset instance ID, rejects concrete/malformed/unsupported/ambiguous/unmapped selectors, and forwards that identifier to native FindService/StartFindService. The deployment records are configuration-owned and process-stable; no local copied deployment is returned. This addresses C1 in principle for retained handles/proxies, without a Runtime vtable change or invented UID-to-short-name mapping. It requires one correctly registered configured wildcard per interface; it is not a general binding/version/quality resolver or heterogeneous system discovery.

**S4 — cancellation design is sound in principle after S1.** A `FindServiceStopGuard` is now created immediately after successful start, before returning the outer async block; it owns the native handle and stops once in Drop. This addresses P1's never-polled window in source. New mock cases explicitly cover unmapped error, never-polled drop and polled-pending cancellation. They are unexecuted and exercise a mock stop counter rather than real native callback quiescence. The one-shot future remains distinct from #1261's updating stream. Async no-offer intentionally remains pending and is not awaited by the new empty test.

**S5 — genuine wildcard setup is discriminating, but per-instance use is incomplete.** Separate provider config offers BigData IDs 1 and 2 plus ComplexStruct; the consumer config contains only the first concrete BigData plus a genuine wildcard entry. This is stronger than enumerating two configured Specific entries. The new app asserts two sync and two async builders, strict unmapped/concrete/malformed selector errors, sync no-offer empty success, and Specific compatibility.

However, `consumer_any_apis/consumer_app.rs:166–172` builds only `.next()` from the sync result and drops it; lines 196–205 build/subscribe only `.next()` from the async result. It does not prove distinct actual IDs, successful proxy construction/use for both instances, or specifically the instance absent from consumer configuration. Use both retained builders or explicitly identify/select the absent instance and assert meaningful delivery from it. Both providers currently send the same x sequence, so sample content alone cannot identify which producer was used. The sync build does create a native proxy through Subscriber::new, but it does not receive samples.

The producer offers both BigData instances before ComplexStruct. The consumer starts its query checks once it observes two BigData results, with no barrier confirming ComplexStruct is already offered. Thus exclusion can be vacuous under scheduling. Require observable readiness of the other interface before the exclusion assertion, or retain that limitation. Host timeout bounds the retry loop; it is not an internal discovery deadline or proof of deterministic readiness.

**S6 — identity accessor limits are honest for Any, but query alias is not producer identity.** The additive `try_get_instance_specifier` preserves the old trait signature; LoLa returns an error for Any. The legacy accessor still panics for Any and is explicitly documented, so the patch cannot be described as panic-free for every public accessor. The default fallible method delegates to legacy implementations and does not universally guarantee absence is returned as an error.

For Specific, the stored string is the caller's query specifier, not an identity reported by the remote producer. Native Specific queries can themselves reference a configured wildcard selector and return multiple handles with that same alias. Do not present that alias as a unique authenticated producer specifier. Concrete native IDs remain inside handles; the new Rust regression does not expose/assert them. Adding a private field to the formerly publicly constructible `LolaConsumerBuilder` and mandatory FFIBridge methods also leaves external source-compatibility questions; selected in-repository builds do not prove every downstream implementor/caller remains compatible.

**S7 — native stop is not complete callback allocation reclamation.** Baseline `registry_bridge_macro.h:190` gives the find-service RustBoxedCallable specialization an empty dispose function; `FindServiceCallable` erases a Box and has no Drop. The new invalid-selector async path returns before native callable ownership is created. No proof of boxed callback/state reclamation on failure or stop is supplied. This is an inherited/extended resource-lifetime gap, not another measured failure. Exactly-one stop tests must not imply that every Rust closure/native callback allocation is freed. Broad unsafe cleanup changes would require their own sound ownership analysis; do not apply an unreviewed destructor just to remove the warning.

## Next authorized correction and final review limits

The source ledger confirms #250 correction 2/3 used, one remaining; #1261 remains 1/3, #173 2/3 and the separate #560 Codex allowance 1/3. Only the existing authority can admit a final Flash source correction. Preserve this source, all failed outputs and report hashes before that attempt; this supervisor performs no remediation or relaunch.

Actionable correction priorities are S1/S2 compilation, then discriminating assertions/coverage in S5 and accurate limits in S6/S7. C4 still requires actual positive native results, not merely a regression-plan file. The dedicated target now names real two-case pytest coverage and a real LoLa unit target, but no cases ran. All six planned groups must be accounted for after changed subjects are measured; source differences prohibit carrying the previous #173 results onto this candidate.

The public scope remains typed same-interface Any. #250's broader system-all comment, #1261 heterogeneous stream, qualification/trace/applicability, external compatibility and authorized offline acceptance remain open. No issue closure or clean-analyzer claim is supported.

## Input bindings

| Input | SHA-256 |
| --- | --- |
| `check-source-subjects.json` | `bc02f75e155744790166426c91ce4d891a02562089ddf4c2f2b7b7c734f2ef9b` |
| `workspaces/250/.rust-queue/reports/implementation.md` | `89e4fcbf4641d2ca0e58871dc662c71c3b168d99f0647993cc324378cd99ed55` |
| `workspaces/250/.rust-queue/reports/regression-plan.json` | `ddd20f580ee6656b6b5a289345db995cf547cbcfee4adb07833530342cd51490` |
| `effective-check-plan.json` | `6acc379a655cb79d630909c1ab0c2a0e1c2cc259a9311c5a152c11c271872f3e` |
| `execution/native-result.json` | `b20938471cf97788085454762bff47de80ef52f085d1bd20b66a5516cd95c596` |
| `execution/check-0.log` | `5dd9f0064ca8dd646a28bb02b5a6108052e2510c32830f0113b7cdffcf868ebc` |

## Terminal evidence disposition by Codex

Native Fabro lifecycle succeeded because the graph exported and terminated after check failure. This does not imply source/test success: check@1 failed with E0560, zero tests executed, remaining five groups unexecuted. Native terminal events/projection/state retained; all three native agent stages used only DeepSeek v4 Flash, with no fallback/retry. Original250 now2/3; one correction remains. Source review static C++ macro defect is additional and not a native compiler observation. The packet is reviewable failure evidence; implementation is incomplete. Native engineering acceptance remains pending offline. No issue closure or publishing authorized/performed.
