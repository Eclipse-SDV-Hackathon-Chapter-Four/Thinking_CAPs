# Communication #1265 — native Linux integration passed

**Both native Rust COM integration suites passed: six cases, zero failures,
errors or skips.** Tests executed freshly on Linux x86_64 at communication
baseline `8368bfb5b182ae6642d963b58ad4bac5dabc02c3`, with cached test results
disabled. Native Bazel completed in 54.797 seconds; reused build actions do not
mean reused test results.

| Native suite | Executed cases | Result |
| --- | --- | --- |
| `consumer_sync_apis/integration_test:test_com_api_sync` | BigData exchange; mixed primitive values; complex struct values | 3 passed |
| `consumer_async_apis/integration_test:test_com_api_async` | Receive with cancellation; receive without cancellation; stream | 3 passed |

These suites build actual Rust producers and consumers, generated interfaces,
the C++ bridge and production LoLa runtime. Native integration rules package
Ubuntu 24.04 OCI images and execute through the pinned S-CORE integration framework,
OCI loader and Docker SDK. An observed running container had native init enabled,
2 GiB shared memory and its own framework-created bridge. Consumers completed and
exited zero. Producer exit 143 is expected native fixture SIGTERM cleanup, not a
passing producer self-completion claim.

See the [verification report](verification-report.json),
[sync raw log](execution/testlogs/score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test/test_com_api_sync/test.log),
[async raw log](execution/testlogs/score/mw/com/test/basic_rust_api/consumer_async_apis/integration_test/test_com_api_async/test.log),
[correction ledger](correction-ledger.json), [supervisor review](supervisor-review.md)
and [PR draft](pr-description.md). XML, exact case names, commands, configurations,
source hashes and complete failed-attempt records are retained.

## Execution and recovery

Final Fabro run `01M4889N23QQRPB5CHZB2GVF5M`, workflow version
`5e15cc141483a3a45870e62733791fe34440163d5fed8f140a998902c0beb67a`,
succeeded. Graph nodes are commands only, with zero automatic retries and no
human approval nodes. Native model lists are empty and recorded native token
usage is zero. Human engineering acceptance remains outside this run.

This fresh Linux integration scope used its maximum **three fixes**:

1. Shorten the private Unix-socket path after the initial Docker startup refusal.
2. Use an actual short internal RootlessKit state directory after a symlinked
   detached-network-namespace path failed.
3. Pass the existing user DBus session and runtime directory after both native
   suites reported container-startup cgroup errors. The corrected native run
   then passed all six cases. No source, policy or toolchain pin was changed.

The first native run `01M487J7SEV1V42R8QVSX9ZEKA` reported six fixture errors,
zero assertion failures and zero skips. Its 90-subject archive is preserved in
`execution/attempts/first-native-run/`. Its collector could not find unavailable
Bazel convenience symlinks; actual emitted XML was collected independently.
Final successful execution created those symlinks, and its executed collector
captured XML and logs. The packet independently confirms all six expected names
and zero failures/errors/skips from the actual output tree.

All owned Docker and Fabro processes stopped. Shutdown checks measured an
unreachable private Docker API, no running owned process-group members and an
absent socket. The global Docker daemon and its configuration were not changed.
Public image/build data stayed in the SSD-bound workspace; private daemon state,
client configuration and Fabro credentials stayed internal. The native default
Docker socket was mapped to the owned daemon only inside the execution namespace.

Post-run packaging caught an edit to its bound exporter script. The modified
draft was preserved separately and the exact verified launch version restored.
No native repair or test rerun followed. The [refusal record](execution/packaging-draft-refusal.json)
preserves this artifact-preparation deviation.

## Scope and pending review

The patch still changes only the Rust README and identifier-pasting assessment.
It applies cleanly to the selected current baseline. Fresh source selection
verified three upstream changes against the earlier baseline by Git blob and
SHA-256 identities; no upstream code change is authored by this contribution.
The generic Rust issue workflow remains implemented and installed.

The [historical packet](historical-rust-and-copyright/README.md) remains byte-exact:
33 Rust unit/doctest cases passed, two ignored, and 204 copyright findings were
reported on baseline `e3d126c2d7569345cf5f790310702eb00cd86b06`. Those results
were not rerun or promoted to the newer baseline. Copyright findings remain
pending review; current-baseline copyright checking was not part of this run.

This is focused Linux integration coverage. Full repository CI, QNX, sanitizers,
coverage measurement, complete ABI/layout proof, compiler qualification,
communication adoption and authorized offline engineering acceptance remain
unperformed or pending. Native BigData opaque placeholders and sample-count
checks do not verify every payload field or C++ layout.

OCI descriptors and layer hashes are retained in [native OCI subjects](native-oci-subjects.json).
Larger layer bytes remain in the bound build workspace and are not copied into
this portable report packet. Report and raw-test-log integrity can be verified
offline without those layer bytes. No publication, accepted fix, merge or release
is claimed; the issue remains open.
