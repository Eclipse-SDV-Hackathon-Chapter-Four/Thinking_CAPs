# Public change corpus

30 search scenarios and 10 held-out scenarios. Each directory contains Spec Kit-style
spec.md, a machine-readable task.json with explicit oracles, and immutable before/after
needs snapshots. Fixtures are synthetic public data, not historical field defects.
The existing spec/task_002–004 and fixtures/ remain the three native gate-test seeds.

Search covers removal/rename, type/content/status changes, forward and reverse test
references, failed/error results, graph cycles/fan-out, CSV links, implementation filters,
partial coverage and exact threshold boundaries, no change, unrelated change, and repair.
Held-out IDs, snapshots and combined changes are disjoint from search; evaluate them only
after freezing the candidate. Their outcomes are public; this is an OSS reproducibility
split, not a concealed model benchmark. A passing replay does not measure agent quality.

Run python -m score_harness.evaluate --candidate score_harness/harness/pinned_context_harness.py.
Use --split heldout --iteration 2 for the separate held-out run. Oracles are static fixture
expectations; the evaluator never derives expected impacts with the implementation.
