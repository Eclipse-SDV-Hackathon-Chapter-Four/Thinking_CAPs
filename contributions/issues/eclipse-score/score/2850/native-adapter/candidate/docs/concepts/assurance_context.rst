..
   # *******************************************************************************
   # Copyright (c) 2026 Contributors to the Eclipse Foundation
   #
   # See the NOTICE file(s) distributed with this work for additional
   # information regarding copyright ownership.
   #
   # This program and the accompanying materials are made available under the
   # terms of the Apache License Version 2.0 which is available at
   # https://www.apache.org/licenses/LICENSE-2.0
   #
   # SPDX-License-Identifier: Apache-2.0
   # *******************************************************************************
.. _assurance_context:

Task-scoped assurance context
=============================

``score_harness/harness/pinned_context_harness.py`` is a standalone candidate for the
context-retrieval portion of S-CORE issue #2850. Its ``PinnedContextHarness`` class
implements ``get_context(task_spec) -> str`` and
``post_process(agent_output, task_spec) -> dict`` with only stdlib and the repo-local ``AssuranceHarness`` base class.
It can be loaded as a single Python file by a caller, without the chatbot runtime.

Task contract
-------------

The caller authorizes a prepared input file or directory using ``input_path``.
The optional ``consistency_rules`` list contains explicit local file paths.
Relative rule references are relative to the input directory, or the parent of
an input file. Absolute rule references authorize precisely those files. Native IDs
``CR-001`` through ``CR-005`` reference the fixed repo-local
``score_harness/consistency_rules.json`` catalog; only selected rule definitions
are emitted. This prepared JSON is equivalent to the native YAML catalog, and
a regression test checks their equivalence. YAML parsing happens during catalog
preparation and tests, never inside the candidate. Unknown rule IDs fail closed.
Rule descriptor objects are not accepted. The native ``id`` field is carried
as ``task_id``; the optional ``task_id`` field is a fallback.

For example::

   task = {
       "id": "threshold-change",
       "input_path": "/prepared/task-001",
       "consistency_rules": ["CR-005"],
   }
   context = PinnedContextHarness().get_context(task)

Only UTF-8 ``.json``, ``.rst``, ``.md`` and ``.txt`` files are context inputs.
Directories are traversed in lexical order. Unsupported regular files are
ignored. Symlinks (including parent components), special files, parent traversal
and URLs are rejected. Each directory component is opened without following
links. The adapter requires POSIX descriptor-relative file access.
Prepare immutable, task-scoped inputs before execution; a broad corpus is not
an implicit authorization. The adapter does not provide a sandbox for the agent.

Each context artifact contains its scope, source path label, SHA-256 of the
exact input bytes, original content, and ``untrusted_artifact`` trust label.
Input path labels are relative to the input directory; explicit absolute rule
references retain their supplied path. JSON is serialized with sorted keys.
Need IDs, native status/version, link direction, provenance, license notices
and unknown/unverified revision fields are preserved verbatim inside content.
A hash binds bytes and does not authenticate an asserted source commit.
JSON duplicate keys and non-finite numbers are rejected rather than obscured.

A prepared Docs Assistant JSON export can be supplied at this boundary, carrying
its normalized document/entity and provenance fields. The adapter does not load
SQLite, vectors, model services or the assistant's dependencies. Raw Sphinx-needs
JSON and RST can also be supplied directly. It does not resolve referenced source
paths, RST includes, directives, templates, URLs or executable content. Document
text cannot authorize additional reads. No generated artifact IDs are assigned.

Limits are 128 selected files, 2 MiB per file, and 8 MiB of total input bytes.
Missing inputs, malformed UTF-8/JSON, invalid references and exceeded limits
raise exceptions; no partial context is returned. No files are written and no
network, model, subprocess, environment mutation or dynamic execution occurs
while constructing context. ``post_process`` carries inert agent output and the
task ID; it neither executes output nor interprets it as validation evidence.

Verification and boundaries
---------------------------

The native test target is::

   bazel test --lockfile_mode=error \
     //score_harness/tests:pinned_context_harness_test \
     //scripts_bazel/tests:traceability_gate_test

The candidate provides context only. Lane A metrics production, threshold gate,
evidence-schema validation, structured trace writing, run-history queries and
candidate evaluation remain the caller's responsibility. The draft harness's
``validate_candidate.py``, ``outer_loop.py`` and ``query_runs.py`` can load and
evaluate this candidate without changes to their code. Tests exercise native
needs and prepared-export data as fixtures; they do not establish source
synchronization, real-model accuracy, engineering acceptance, or completion of
the parent issue's rule catalog and public scenario corpus.

Executable consistency and change scenarios
-------------------------------------------

The public catalog defines CR-001 through CR-005. ``consistency.py`` executes
checks against explicit before/after needs snapshots and follows reverse argument
links with a visited set, including cyclic graphs. CR-001 flags removed or renamed
compliance targets; CR-002 flags guideline claims after requirement type changes;
CR-003 flags broken test references and test-result regressions; CR-004 flags
standard content changes; CR-005 flags native gate coverage regression. Each impact
retains the need ID, rule ID, class and reason. ``gate_verdict`` is the explicit
non-need sentinel for a coverage gate impact; all other IDs come from the snapshot.

Reusable blocks also check a goal's requirement content/status/removal, a solution's
removed or regressed V&V evidence, and a parent's lost child coverage. These blocks
use CR-001, CR-003 and CR-005 respectively. An impact is a review obligation, not an
automatic approval or waiver. The native gate remains authoritative for coverage;
its verdict and consistency impact correctness are recorded separately.

``corpus/`` contains 30 public search scenarios and 10 separate held-out scenarios,
with Spec Kit-style ``spec.md``, explicit JSON oracles and before/after snapshots.
IDs are synthetic test data. The native three metrics-fixture seeds remain available.
The evaluator uses the existing metamodel metric implementation, validates the native
metrics schema and executes the unchanged gate for both snapshots. No model or external
service is used. No historical defect or agent-performance claim is made.

Snapshot trace store
--------------------

Run ``bazel run //score_harness:evaluate -- --candidate
score_harness/harness/pinned_context_harness.py --output-dir /tmp/assurance-runs``.
Evaluate the baseline with ``harness/base_harness.py``. Use ``--split heldout
--iteration 2`` after freezing the candidate. Existing iteration/candidate directories
cannot be overwritten. Full candidate validation precedes evaluation and missing
lint/type tools fail validation. Unit tests separately exercise the interface.

The deterministic snapshot executor records the actual before/after diff as
``agent_diff.patch``, explicitly labelled ``snapshot_fixture_replay``. Each task
also has ``gate_output.json``, ``impacted_elements.json`` and ``score.json`` plus
context, schema-validated metrics and separate raw gate logs. Run metadata records
hypothesis, expected outcome, change mode, tool/input hashes, candidate validation
and split. Scores record coverage deltas, timestamp, interpreter and environment
hash, gate script hash, artifact hashes and responsibility/escalation/waiver roles.
No fabricated human decisions are emitted.

Start navigation with ``evolution_summary.jsonl``. ``query_runs.py`` supports top
candidates, failed tasks and candidate differences. The required native test workflow
runs both candidates and splits and uploads trace artifacts even after failure.
Local execution verifies its commands; GitHub branch protection and remote CI results
are maintainer decisions and must be checked before merge.

Build-backed native seed
------------------------

The legacy outer loop also runs the active build-backed native task after the
documentation check produces ``_build/needs.json``. It extracts schema-valid
metrics from that snapshot through the unchanged metamodel calculation and uses
the fixed gate. The original docs exporter includes extra metadata not accepted
by the fixed gate schema; original generated output is retained as source evidence.
Task input paths are normalized lexically by the trusted runner; symlink components
remain visible to the candidate's rejection checks. Bazel CLI entrypoints resolve
user paths against ``BUILD_WORKSPACE_DIRECTORY``.
