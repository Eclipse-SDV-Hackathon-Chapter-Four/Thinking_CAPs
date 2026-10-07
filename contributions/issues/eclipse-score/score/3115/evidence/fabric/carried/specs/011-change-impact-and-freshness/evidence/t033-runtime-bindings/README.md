# T033 protected runtime bindings — local qualification

This packet extends the paired P704 preparation with protected worker initialization,
completed-response application, observed-meter result capture, bounded feedback and
fresh candidate collectors. It starts no provider request, meter or Fabro server.

The implementation is in `optimization/paired_runtime.py` and `paired_collector.py`.
Private operator bindings/state remain on internal storage; source/build/cache work
uses the measured mounted Linux image. Full original and candidate file inventories
prevent unrelated source edits. Application permits the supplied four writes and three
deletions, pins the completed raw response/context/native IDs, preserves license
markers, refuses replay and requires fresh failed checks for one correction.

Both [baseline graph](graphs/baseline/workflow.fabro) and
[optimized graph](graphs/optimized/workflow.fabro) pass the pinned offline validator:
14 nodes, 24 edges, no automatic retry and an unanswered human gate. Protected capture,
apply, collector and feedback command nodes are wired; bounded MCP retrieval derives
current source hashes from private state and advertises only `get_source_excerpt`.
The routing/fidelity interface is grounded in the pinned Fabro/Petri source.

The graph bindings deliberately use local-only mode, empty disposable workers and
refused governors. `capture_apply` therefore refuses before observing any provider
result. A future live run must bind its actual native cwd/run, classified native
scope, current instruction/meter and fresh feedback transmission. Native API worker,
paid transport/usage and agent prompt consumption are not newly qualified here.
No engineering acceptance, native expected-set closure, QNX result or B1–B5 savings
is inferred. All paired live metrics remain null; publication remains deferred.

## Fresh native collector exercise

The approved historical Flash patch is an explicit **local replay**, isolated from the
empty graph workers and their original model prompts. It supplies no new DeepSeek output.
Both source copies apply the exact replay contract; fresh commands use separate Bazel
output roots and `--nocache_test_results`. The baseline exercise initially passed 113
cases and every configuration/runfile/package check. The optimized exercise uses the
frozen final collector, including the added full post-command source inventory check.
These are collector checks, not paired model benchmark measurements.

See each arm's `fresh-checks.json`, raw command/output artifacts in `native-checks/`,
[validation results](validation-results.json), [preserved subjects](preserved-subjects.json),
and [source/interface bindings](native-interface-sources.json). Private state references
are local provenance, not authenticated native engineering receipts or protection
against the owning user. The source archive remains the immutable prior packet's
740-file baseline; no reference repository is written or built.

## Retained diagnostics

The initial graph draft had improperly escaped embedded contract quotes; native parsing
refused it. The corrected graphs both validate. Early test runs placed legacy fixture
artifacts outside their configured temporary-root boundary; correcting the test
environment yielded a passing regression run. Original diagnostics are retained; no
production guard was relaxed for those fixtures.
