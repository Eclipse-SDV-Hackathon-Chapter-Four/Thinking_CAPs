# Issue acceptance and proposed engineering trace

Source: `cef680454e8586daca9f953084dca33fb3759d0c` in eclipse-score/communication. Original issue bodies and current native contribution/CI sources are preserved in the evidence directory. An unchecked issue-template field is not requirements or safety approval. No native requirement ID is invented here.

| Native issue obligation | Proposed artifact | Verification and review |
| --- | --- | --- |
| #1261: heterogeneous newly available services | `Runtime::find_all_services`, interface-independent descriptor and configured LoLa stream | Configured discovery integration, runtime stream units; upstream scope acceptance pending |
| #1261: service and interface identity | Owned interface name/version, binding and service/observed instance IDs | Distinct-interface and instance observations in stream tests |
| #1261: initial results, errors, lifetime and termination | Concept documentation and user examples; bounded/coalesced pending observations; withdrawal and drop handling | Initial-result, flapping, withdrawal, startup-failure rollback and cancellation regression cases |
| #1261: existing scoped discovery remains | Existing Specific API now selects additive owning FFI; typed Any implementation remains | Runtime regression and Specific/typed Any production integrations |
| #1261: system-wide discovery including unconfigured interface types | Outside the user-selected contribution | Broader issue remains open; no closing keyword in PR draft |
| #250: replace the Any panic with synchronous and asynchronous native discovery | Typed Any bridge, mock/runtime methods, generated service identity and consumer API | Unit cases and production same-interface multiple-instance integration |
| #560: synchronous subscription state | Rust enum/error mapping, generated trampolines and event methods | State mapping/get behavior regression and production integration |
| #560: asynchronous state change handler | Set/unset generated native bridge, Rust callback lifetime and ownership guard | Native rejection/transfer/destruction tests; production handler replacement, unset and transition checks |
| API/ABI compatibility | Unchanged IRuntime, static Runtime extension, external stable deployment storage, additive native symbols | Structural source comparison and legacy mock regression; platform ABI review pending |
| Native strict Rust diagnostics | Named FindServiceError, explicit callback pointer transmute, Copy dereference and test borrow corrections | Maintained Clippy aspect plus explicit test-code analysis; no warning suppression or policy/pin change |
| Native notice invocation | Correct root BUILD source paths | Changed-file and full-tree notice checks reported separately from IP rights review |

Configured discovery enumerates configured service types with a configured LoLa deployment; its deployment supplies the quality level needed by native discovery. A provider instance may be absent from the consumer instance manifest. An interface with no configured deployment, another binding, or an entirely unconfigured interface type is outside this universe. Injected legacy runtimes return an empty universe through the static extension.

Requirements/design impact is proposed for native owner review: discovery selection and observation semantics, heterogeneous identity representation, subscription state/error mapping, callback ownership and cancellation, allocation during configuration/discovery, and concurrency assumptions. The Rust detailed design and user examples are changed alongside implementation. The issue-template assertion for #1261/#250 does not establish that these impacts need no review; #560 explicitly leaves requirements/architecture unaffected status unchecked.

The expected-check matrix maps native workflows to measured local results and omissions. Qualification, the adopted safety/allocation profile, code-owner review, contributor rights, official ECA status and IP Team clearance remain human or hosted acceptance subjects.

The preserved baseline TRLC sources also supply the following native requirement references. These are proposed impact/verification mappings, not accepted Rust safety allocations. The records declare safety B and version 1; their approved/released status and applicability to this Rust contribution are not inferred.

| Native reference | Proposed contribution mapping |
| --- | --- |
| `Communication.FEAT_ServiceDiscovery@1` | Configured discovery and typed Any; native version compatibility remains delegated to native discovery |
| `Communication.BehaviourOfFindService@1` | Synchronous typed Any returns native available handles; empty availability is tested |
| `Communication.BehaviourOfStartFindService@1` | Asynchronous typed Any and configured watches track current availability until stopped |
| `Communication.FindServiceHandler@1` | Native serialization per search is the basis for the Rust FnMut callback invariant |
| `Communication.SubscriptionState@1` | Rust state enum maps native subscribed, pending and not-subscribed values |
| `Communication.SubscriptionStateChangeHandler@1` | Native serialization per event is the basis for the state callback's FnMut invariant |
| `Communication.BehaviourOfSetSubscriptionStateChangeHandler@1` | Native state transitions forwarded through the generated Rust bridge |
| `Communication.CallsToSubscriptionStateChangeHandlerWithKNotSubscribed@1` | Unsubscription transition checks |
| `Communication.CallsToSubscriptionStateChangeHandlerWithkSubscriptionPending@1` | Pending state mapping and callback checks; native reconnection requirements remain owner review subjects |
| `Communication.SubscriptionStateChangeHandlerWithKSubscribed@1` | Successful subscription transition checks |
| `Communication.SubscriptionStateChangeHandlerReturnValue@1` | True retains registration; false removes it; production checks and ownership transfer regression |
| `Communication.BehaviourOfUnsetSubscriptionStateChangeHandler@1` | Unset callback suppression and lifetime handling |
| `Communication.ThreadSafetyOfMethodsFunctionsOfPublicAPI@1` | Assess distinct-instance/same-instance restrictions; no universal Sync guarantee is claimed |
| `Communication.ExplicitLifetimeEndingByAPICalls@1` | Unregistration must end callback invocation; disposal after native teardown and native call completion are distinct obligations |
| `Communication.ImplicitLifetimeEndingByDestructionOfContext@1` | Callback context destruction and cancellation review |

Sources are `evidence/planning/native-requirements/{component_requirements/component_requirements_ipc.trlc,feature_requirements/feature_requirements_ipc.trlc}`, bound to the baseline by `native-requirement-bindings.json`. This table does not assert exhaustive native requirement coverage or qualification. Reviewers must resolve the existing native document-validation findings and accept the final requirement/design/safety impact.
