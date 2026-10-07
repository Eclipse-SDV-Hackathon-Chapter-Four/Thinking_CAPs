# P704 — paired Fabro preparation

The baseline and selected-context packages are prepared without provider calls.
Both native graph/config source sets pass pinned Fabro validation: **nine nodes and
fourteen edges** each. [Equivalence checks](equivalence.json) preserve task intent,
the original six JSON/BUILD inputs, native source IDs, procedural Skills, selected
tools, output/check contracts, one correction visit and human review obligations.

- [Baseline graph](baseline/workflow.fabro), [configuration](baseline/workflow.toml)
  and [context](baseline/context.json).
- [Selected graph](optimized/workflow.fabro), [configuration](optimized/workflow.toml)
  and [context](optimized/context.json).
- [Task envelope](task-envelope.json), [source selection](source-selection.json),
  [output contract](output-contract.json) and [common collector plan](collector-command-plan.json).
- [Native source archive](original-source.tar), [fabric source/lock snapshot](fabric-snapshot.tar.gz),
  [snapshot hashes](fabric-worktree-snapshot.json) and [licenses](source-license/).
- [Workspace/source bindings](workspace-binding.json), [context comparison](context-comparison.json),
  [local probes](local-probes.json), [summary](summary.json) and [remaining admission gaps](admission-gaps.json).
- [Verification](verification.json), [Spec Kit reconciliation](spec-kit-reconciliation.md),
  [final consistency audit](final-audit.json) and [capture manifest](manifest.json).

Baseline prompt: **23,426 bytes**. Selected prompt: **20,184 bytes**, about **13.84%**
less. The shared selected tool schema adds 304 bytes to each estimate. Native wrapper
and complete request overhead have not been measured. These are UTF-8-byte estimates;
live input/cache/output tokens, cost, time and engineering-outcome equivalence remain null.
All mandatory original profile/configuration values stay available in both arms.

## Measured local boundaries

Fourteen actual local probes match their expected outcomes. Two empty disposable workers
receive the complete 740-file original source archive, with all selected hashes checked
and no earlier generated macro. The same stdio MCP declaration exposes bounded source
excerpts in both arms. Nonempty workers, stale source/context, an unselected generic tool,
refused stage admission and a candidate record without an operator instruction are denied.
Source/context mutations used for negative probes were restored exactly. These are local
initialization/service checks; a live native Fabro worker was not created or qualified.

The first native graph validation found missing unconditional fallback edges. Its
[original diagnostics](baseline/native-conformance-first-attempt.json) are retained.
Unexpected outcomes now stop at human review, with an explicit check failure allowing
one correction. The corrected [baseline](baseline/native-conformance.json) and
[selected](optimized/native-conformance.json) validations pass without diagnostics.

## Execution and acceptance boundaries

The full native dependency/expected-set closure remains unresolved. Classification is
therefore `unknown`, and every stage governor refuses with zero available calls. No
private execution instruction, old budget exception, provider meter or Fabro server is
started. Existing server/queue state remains untouched and publication stays deferred.

The prepared command entrypoint deliberately refuses collector execution. Protected model
result extraction/application, fresh native collectors and correction/advisory feedback
are **not wired**. Exact live worker bindings, current model/settings/price evidence,
full payload accounting and new admission limits are also needed. Passing graph syntax
and local probes cannot establish those boundaries or authorize a live trial. P704 remains
an additional pilot; B1–B5 selection and T033 engineering qualification are still open.

## Reproducibility

The [captured preparation](operator-scripts/prepare_pair.py.txt) and
[runtime entrypoint](operator-scripts/pair_runtime.py.txt) are byte-bound records. They
use the actual 172-file fabric worktree snapshot, not just its Git HEAD, and source copies
from native commit `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`. CLI paths in the TOML
identify the selected disposable workspace; later materialization needs a newly hashed
binding rather than silently rewriting these captured files. Collector commands are
explicit templates, not an executable qualified runner.

The previous benchmark-plan packet is unchanged. Its seven then-current control
subjects are preserved byte-for-byte in [prior-plan-controls](prior-plan-controls/),
so later Spec Kit extensions do not erase that historical snapshot. Original reviewed
T032 subjects and approved native/PR packets remain unchanged. The capture manifest and
source archives permit integrity review without a running Fabro installation.

Next: implement and validate the protected result/application/collector and live worker
bindings without provider calls, then assemble the exact fresh admission packet.
