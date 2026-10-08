# Reproduction

## Offline integrity

```sh
PYTHONDONTWRITEBYTECODE=1 python3 contributions/eclipse-score/score/2850/native-adapter/verify_native_packet.py
PYTHONDONTWRITEBYTECODE=1 python3 contributions/eclipse-score/score/2850/verify_packet.py
```

These commands verify hashes, archive contents, final candidate/contract binding,
recorded outcomes and trace files; they do not execute archived source or rerun tests.
They grant no engineering acceptance. The independently maintained, in-progress sibling
`full-issue-fix-20261007/` is explicitly excluded from the parent manifest scope. Source, policy/tool hashes and exact original
commands/logs are retained, including failed attempts and baseline comparisons.

## Native checkout and checks

Use a disposable checkout on a measured writable build volume; configure caches/output
bases for that checkout. Bash commands below assume the review packet absolute path is
stored in `score_packet` and a tool environment in `score_tools`.

```sh
git clone https://github.com/eclipse-score/docs-as-code.git
cd docs-as-code
git fetch origin 4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9
git checkout --detach 4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9
git apply --check "$score_packet/patches/0001-score-2850-assurance-harness.patch"
git apply "$score_packet/patches/0001-score-2850-assurance-harness.patch"

python3 -m venv "$score_tools"
"$score_tools/bin/python" -m pip install ruff==0.15.9 basedpyright==1.39.0
export PATH="$score_tools/bin:$PATH"
bazel run --lockfile_mode=error //:ide_support
bazel test --lockfile_mode=error --test_env=PATH //...
bazel run --lockfile_mode=error //:docs_check
bazel run --lockfile_mode=error //score_harness:validate_candidate -- --candidate score_harness/harness/rule_retrieval_harness.py --task-spec score_harness/spec/task_002_threshold_fail.json

for candidate in base_harness pinned_context_harness; do
  bazel run --lockfile_mode=error //score_harness:outer_loop -- --candidate "score_harness/harness/$candidate.py" --tasks score_harness/spec --output-dir /tmp/score-native-seeds --iteration 1
  bazel run --lockfile_mode=error //score_harness:evaluate -- --candidate "score_harness/harness/$candidate.py" --output-dir /tmp/score-public-runs --split search --iteration 1
  bazel run --lockfile_mode=error //score_harness:evaluate -- --candidate "score_harness/harness/$candidate.py" --output-dir /tmp/score-public-runs --split heldout --iteration 2
done
bazel run --lockfile_mode=error //score_harness:query_runs -- --runs-dir /tmp/score-public-runs --failed-tasks --diff-candidates base_harness pinned_context_harness
```

Use new output directories or iteration numbers on repeats: runs are append-only.
Expected: 4/4 native active tasks, 30/30 search and 10/10 held-out for each candidate,
with zero failed/incorrect outcomes. The inactive example is excluded by its own flag.
Initial dependency/tool hydration needs network; execution makes no model/service calls.
Bazel CLI paths resolve against the workspace, not its symlinked runfiles tree.
The source archive is also available under `evidence/source/`; extracted archives need
real Git metadata and the upstream remote for native source-link documentation tooling.

Changed-code lint/format/type, copyright and actionlint commands are exact in their
retained records. JSON/Markdown syntax, whitespace/conflict/private-key and size checks
are retained as packet syntax validation; native copyright has no JSON/Markdown template.
The native module-tidy command and source-purity result are retained separately.

The actual native IDE-based **whole-project** type check (`.venv_docs/bin/python -m
basedpyright --warnings`) currently returns nonzero with 28 warnings in untouched files.
The pristine draft reports 101 using the same environment; changed-code strict checks
return zero errors/warnings. Do not describe the whole pre-commit suite as passing until
those native baseline findings are resolved or accepted under project policy.
No lints, requirements, locks or fixed gate/metric/schema contracts were relaxed.

The scenario runner computes gate-compatible metrics using the unchanged native
calculation and validates the fixed metrics schema before execution. Raw Sphinx-exported
metrics carry metadata that the schema rejects; originals and the error are retained,
with the schema-valid extraction and a context preserving the complete needs export.
All snapshot scores identify deterministic fixture replay, not agent performance.
