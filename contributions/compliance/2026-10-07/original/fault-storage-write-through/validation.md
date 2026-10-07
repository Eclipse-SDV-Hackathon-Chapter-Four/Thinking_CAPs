# Native validation and continuation

```sh
git checkout --detach 12dac502616701734f90a61edca1326ae2ac6506
git apply /absolute/path/to/write-through.patch
cargo +nightly-2025-07-14 test --locked -p dfm_lib -p integration_tests --target-dir /tmp/sdv-fault-tests -- --test-threads=1
cargo +nightly-2025-07-14 clippy --locked -p dfm_lib -p integration_tests --all-targets --target-dir /tmp/sdv-fault-tests -- -D warnings
cargo +nightly-2025-07-14 fmt --all --check
```

Use an isolated clean clone/worktree, not the user's original repositories. Preserve Cargo.lock:
its rust_kvs rev is5d9f8225aa5622f52a31003bec937d5ef227dba7 even though the dependency manifest
tracks main. iceoryx2 rev eba5da4b8d8cb03bccf1394d88a05e31f58838dc is likewise locked.
Unit test helper child processes use separate KVS pools; no same-process reuse is called an
OS restart. Query error propagation is checked. Native `get_all_faults` still substitutes defaults
on storage errors; the integration deliberately queries `get_fault`, which propagates them.

Continuation: review flush policy/latency with maintainers; agree how upstream tests should expose
optional durability; run full supported CI/pre-commit once available; consider separate work on
query error semantics rather than advertising `get_all_faults` as a reliable health indicator.
Coordinate a narrow example/test slice with the existing native-fault owner before any publication.
No issue/PR has been filed or message sent. AAOS/FOTA integration and E2E/VIPER are separate,
currently deferred/conditional milestones. Human reproduction signoff remains pending.
