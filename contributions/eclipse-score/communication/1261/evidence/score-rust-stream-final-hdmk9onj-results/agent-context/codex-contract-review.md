# Communication #1261 — independent contract review, implementation snapshot

The admitted contract contains the key obligations for a useful configured-LoLa heterogeneous updating backend. It does not authorize declaring unqualified system-wide discovery complete. The current implementation is actively changing; all source observations below are snapshots, not frozen source proof or measured passing evidence. Only this report was written; no source/control edits, native execution, retries, model calls or dispatch occurred.

## Authority and controls

Run `01M49MB1BWVT6CKAZ7WZ7JAYM2` uses the bound external SSD; shared storage validation passed. Ledger #1261 is 2/3 used, one remaining. #250 is stopped at 3/3 and its source was not imported; #173 remains 2/3 and the separate Codex #560 allowance 1/3. This review spends no source correction. Human acceptance remains pending offline.

`jobs/1261/task.json` scopes allowed source paths and protects modules, locks, licenses and policy. The graph selects only DeepSeek Flash, has implementation and read-only Flash supervisor nodes with zero retries, file-only guarded tools and no human-wait node. Command checks/export preserve deterministic evidence. The driver requires a dedicated basic_rust_api integration target in regression-plan.json and records actual source vectors, outcomes and missing plan. This syntactic target-presence check does not prove heterogeneous behavior; actual source assertions and native child execution must be independently reviewed. Export routes failures through exit, so a terminal successful lifecycle alone must never override failed/missing native checks or semantic gaps.

Fresh issue #1261 explicitly requires continuously reported services across interfaces, enough service/interface identity, documented initial/error/lifetime semantics, and retained scoped APIs. The previous default NotSupported scaffold is partial. A configured-LoLa universe remains a proposed bounded subset: unconfigured/unknown interfaces and service types added after opening cannot silently be counted as discovered. An accepted universe/qualification decision was not supplied.

## Concrete backend and descriptor obligations

**C1 — enumerate full native interface identity through an explicit API.** Snapshot `configuration.h:154–201` places GetServiceTypes, GetServiceInstances and persisted ForEach helpers under private access. The copy helpers explicitly warn against retained borrowed data. Expose/review a bounded public enumeration extension rather than treating private helpers as callable. GetServiceTypeNames/ServiceIdentifierType::ToString return only names; distinct versions must not collapse. Preserve full ServiceIdentifierType version identity and actual LoLa binding/service id/quality applicability. Runtime/IRuntime additions require mock updates and explicit virtual/ABI compatibility disposition; no downcast of a mock singleton or private configuration shortcut.

**C2 — retain real wildcard deployment ownership.** Native HandleType retains an InstanceIdentifier with borrowed deployment pointers. Temporary enumeration copies, stack-local wildcard deployments or vector elements invalidated by growth cannot back callback/search handles. Existing configuration generations retain stable entries (`configuration.h:247–276`), but synthetic wildcard instance records also need stable owned storage through native stop/quiescence. The existing Runtime.resolve handles one configured InstanceSpecifier and does not independently provide an all-interface wildcard. Never turn discovery into a list of only configured Specific instances: actual provider instance IDs absent from consumer config must be discoverable.

**C3 — owned descriptors with observed identity.** The initial ServiceDescriptor snapshot (`concept.rs:339–393`) contains only &'static str registry interface ID and InstanceSpecifier. This cannot faithfully describe interfaces unknown to Rust registry, duplicate versions or wildcard instances lacking local names. Require owned native interface/type identity including version, binding and concrete HandleType.GetInstanceId; include quality where it affects watch selection/identity. Do not substitute a query alias for remote identity or leak strings to fabricate static lifetimes. Descriptor identity must also be the dedup identity; two services sharing numeric instance ID but differing interface/version/quality must stay distinct. Define whether serialized identifier or separately typed fields carry version, and test equality accordingly.

**C4 — scope configuration evolution honestly.** Existing AddConfiguration merges retained generations; an initial watch universe will not automatically learn future types. Either supply measured refresh semantics or explicitly state opening-time configured-universe limitation. Even enumeration of every configured type does not discover every possible interface on the system. Preserve this limitation against the issue's literal criterion rather than accepting a new universe on the user's behalf.

## Callback, updates and ownership obligations

**C5 — consume complete snapshots and track active membership.** Native StartFindService can synchronously invoke the callback before returning (`service_discovery_client.cpp:767–772`) and suppresses initial empty notifications. Later notifications contain complete current handle sets; changed sets, including empty withdrawal sets, are delivered (`:573–592`). Allocate shared state before start, preserve initial synchronous items, and never terminate merely for initial emptiness. Diff each watch's complete set; removals must clear current membership so re-offer of the same identity yields a new availability item. A permanent global seen-set is incorrect. Overlapping watches/config aliases need global full-identity dedup with per-watch membership or refcounts so one watcher removal does not hide a service still observed elsewhere. Coalescing must not silently discard required remove/re-offer transitions between polls.

**C6 — own every watch and partial failure.** Guards must exist immediately after successful start, before returning a never-polled stream. If watch N fails, stop all earlier successful handles and disposition callback ownership for the failed attempt. Mock unit cases should cover synchronous callback-at-start, zero watches/initial empty pending, duplicate snapshot, removal/re-offer, partial-start failure, never-polled/immediate drop and error without permanent termination. Cancellation must not invoke native stop while holding the Rust callback state mutex if stop waits for callbacks; establish lock order and thread-safe waker/queue access.

**C7 — callback reclamation cannot be inferred from stop.** The inherited find-service specialization has empty dispose (`registry_bridge_macro.h:189`). The native FFI stop wrapper logs native StopFindService failure and still deletes its handle (`registry_bridge_macro.cpp:425–442`). Reusing this erasure does not prove Box/Arc reclamation or failed-stop quiescence. Explicitly own/release newly introduced callback payloads with a sound native completion/quiescence contract, or retain the limitation. Do not add an unreviewed destructor that can free state still reachable by callbacks. Exactly-one stop counters alone cannot establish native safety. Runtime allocation policy also applies to new per-callback descriptors, queues and dedup sets: bound/preallocate capacity or expose policy/application limitations and overflow/error behavior.

## Required real regression evidence

A dedicated native integration must assert one stream contains at least two actual offered interface types, concrete observed identities including a provider ID absent from the consumer's concrete instances, pre-existing offers and initially empty/later offers. Demonstrate delayed addition, withdrawal and re-offer of the same ID, duplicate suppression and cleanup after immediate/drop cancellation. Readiness barriers and bounded process supervision should make these assertions discriminating; sleeps alone cannot prove absence, offered-other-interface readiness or withdrawal observation. No substitute registry enumeration, NotSupported mock, one-interface stream or repeated Specific loop satisfies the proposed backend.

Unit cases are valuable for deterministic dedup/error/partial-start/Drop edges but cannot replace native callback and two-interface integration. Update actual BUILD labels and provide an explicit plan. The selected trusted compatibility plan includes Configuration/Runtime and Rust unit groups, existing sync/async and C++ Any integration, manual GCC15 macro doctests and five-library Clippy. Count actual child XML/stdout cases rather than wrapper records, keep ignored/skipped/missing cases and analyzer warnings visible, and reverify frozen subjects before/after native measurement. Test-code Clippy and unselected platform/ABI/concurrency paths cannot be inferred from selected library checks.

## Pending disposition

The contract is suitable for a bounded proposed implementation if the source meets C1–C7 and real regression obligations. Final source and native measurement review are pending. There is no qualification, closure, authenticated human acceptance or authority to repair #250 through this run. Any unknown API support, impossible allocation/ownership guarantee or broader universe gap must be exported concretely rather than relabeled complete.

## Snapshot input hashes

| Input | SHA-256 |
| --- | --- |
| `jobs/1261/task.json` | `aa615361fa35cac4e3eb3c4a2febcafc933d9a0220e5e73385da806a479e7ac6` |
| `jobs/1261/workflow.fabro` | `b24977a21adaa2824cf2463f12e4c933e5b9f7d5465fd34de185c6cfc7e296b1` |
| `jobs/1261/workflow.toml` | `c37031a5f3d670862cfd53b98b7c4219b89fee4073f944db106c59a0a685547d` |
| `driver.py` | `9de251f1d46b0daaf7be62ab87bdb4ff6224b89cc36c24706b6c5afa31254521` |
| `check-plan.json` | `5f4f5813f0eee76a939a5641d2ab5e19699f750cabd3c8cb6f4c3cea9e951dfc` |
| `correction-ledger.json` | `1b05849b7e7f394f9e342947ccff0a58fb8864c46290469dc9a6becc9bbe742a` |
| `fresh issue` | `7acdd78a15c6b0e4059e82e8bf28b9031d36dad857910fd8c2fae4e71baa461c` |
| `prerequisites` | `8388126d85493d757be6db7afdb8e50fc149f7eea4609a3c6558d7064862b709` |
| `Configuration header snapshot` | `970a3a391bd5afe76b7683ae5b8b0c66579e4ac23262197f132ba38fc86b57c4` |
| `descriptor/concept snapshot` | `4f3776803800e697819535760a5afc22cc119e3b2c8fd2fffeed941da219d336` |
| `native discovery client snapshot` | `9d32e9ab61c1756b5c45e8431707d4c01d573bf8092de7689609e2f64babbfee` |

The source hashes identify inspection snapshots only; active implementation may subsequently change them. No frozen source vector or native result was available for this contract review.
