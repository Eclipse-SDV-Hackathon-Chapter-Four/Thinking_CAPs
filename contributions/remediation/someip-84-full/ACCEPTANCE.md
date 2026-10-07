# Issue #84 acceptance and native trace

This is a proposed implementation of the complete use cases described in
https://github.com/eclipse-score/inc_someip_gateway/issues/84, captured in
`upstream-issue.json` against source baseline
`f8a196c3b16d5172d898394ab99b0ed81346d63d`.

| Issue use case | Implementation | Verification |
| --- | --- | --- |
| Service identity = ID + major | `Service_interface_identifier`; equality, ordering, hash; database uses its default hash/equality | `ServiceIdentityTest` and existing connector/runtime tests |
| Offered instance = ID + major + minor + instance | Public `Service_instance_identifier`; equality, ordering, hash include all fields; actual server minor copied into discovery | `FullInstanceIdentityIncludesActualMinorAndInstance`, `ReportsActualMinorOfEachInstanceAndIgnoresOtherServices` |
| Find request = ID + major + optional minor + optional instance | `Find_service_request::matches`; `Runtime::find_service` traverses enabled local server records | 16 `FindServiceCompatibilityTest` boundary pairs, request tests, runtime filter tests |
| Major wildcard is not meaningful for clients | Major stays mandatory and exact; 255 has no sentinel meaning | `IdAndMajorMustMatchExactlyIncluding255` |
| Better compare/index compatible instances | Database and registration project contracts to canonical service identity; offered minor is stored with actual server, not the index | Existing 91 key regressions and runtime duplicate regressions; replacement discovery test |

The optional minor is interpreted as a **minimum compatible minor**, preserving
native client/server behavior (`client minor <= server minor`). This is a proposed
design interpretation, not an additional statement from the issue author.
Discovery is a local synchronous snapshot. Network advertisements and async
subscriptions are not introduced: the selected native Runtime has no API feeding
remote discovery reports. Existing bridges continue requesting remote services.
The issue requests the identifier/request model, not an implementation of network
service discovery or wildcard-major clients.

Native trace: the existing `comp__socom` declaration belongs to
`feat__someip_gateway` and is QM. The new component documentation references those
existing declarations without introducing made-up requirements or changing their
status. Component requirements are an empty scaffold at this baseline; specific
native requirement IDs for version/discovery behavior remain unknown.

API compatibility: the old versioned `Service_interface_identifier` becomes
`Service_interface`; all in-repository connector, gateway, IPC, test and benchmark
callers are migrated. The new canonical identifier has no minor field. The old
internal duplicate key becomes `Service_registration_key`, distinct from public
full instance identity. External Runtime implementations must implement the new
snapshot method. Committer review of this source API migration is pending.

Runtime constraints: caller-owned optional result storage avoids allocation and
user callbacks during discovery; enumeration uses the existing runtime mutex.
Buffers must be valid, writable and not concurrently accessed. Availability is
only guaranteed for the duration of the snapshot. Serialized IPC structures retain
the same fields; compiler/build evidence must validate the migrated consumers.

Technical test results are in `native-results.json`. Passing tests do not confer
native requirement acceptance, committer approval, IP approval or PR merge readiness.
