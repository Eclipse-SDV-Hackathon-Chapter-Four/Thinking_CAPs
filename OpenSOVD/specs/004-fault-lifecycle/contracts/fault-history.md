# F004 diagnostic contract
Feature-enabled binary accepts --fault-storage PRIVATE_DIRECTORY and policy options.
Native OpenSOVD App data discovery lists cc.observation and cc.fault-history. The latter is a
supported read-data resource wrapping cached native DFM queries, explicitly not native /faults.
Fault code CC.LostCommunication means accepted speed overdue under configured policy, not
proof of transport silence or physical cause. Source silence means assessment unknown.
Native typed status/counters/timestamps/environment are mapped from actual upstream types.
Reporting publish acceptance is distinct from queried DFM confirmation. Query failure retains
last evidence but marks unavailable and exposes age/error. Recovery changes test_failed without
clearing occurrence history, does not change application engagement. No public clear endpoint.
Storage is explicitly opt-in write-through KVS; flush errors must be surfaced. Prepared tests
prove process restart durability, not power-loss guarantees or storage hardware durability.
