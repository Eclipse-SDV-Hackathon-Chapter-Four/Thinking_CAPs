# ThreadX contribution: issue #744

This folder contains the Fabro workflow and reviewable artifacts for
[eclipse-threadx/threadx #744](https://github.com/eclipse-threadx/threadx/issues/744).
The work starts from upstream `dev` and targets the same branch. The fix concerns
stack-address truncation when MISRA and stack checking are enabled together on
ports with 64-bit pointers and 32-bit `ULONG`.

The workflow is running. Its registration, run identifier, and current status are
saved under [artifacts](artifacts/). A running workflow is not a completed or
merge-ready contribution. The final [readiness assessment](artifacts/readiness.json)
will list external checks and human requirements that remain outstanding.

## Agents and tools

Every agent is a fresh **Codex CLI** session using **`gpt-6.1-sol` with High
reasoning**, with no model fallback. Fabro orchestrates those sessions as command
stages. This avoids substituting another model when its installed native model
catalog lacks the requested offering. Explicit invocation records and JSONL
traces live on loop4; Fabro also records stage outcomes. CLI token usage is in
those traces, not Fabro's native inference counter.

| Role | Responsibility | Tools and boundaries |
| --- | --- | --- |
| Issue/dependency planner | Current issue, related merged work, scope and acceptance plan | Codex shell/read/edit tools; source reading and evidence writing |
| Kernel/regression implementer | Minimal pointer-preserving fix and behavioral regression | Codex shell/apply-patch tools; scoped source/tests and evidence |
| Technical reviewer | Independent C99, pointer width, alignment, MISRA, test and coverage review | Fresh read-only Codex session; structured verdict returned to the driver |
| Eclipse process/IP reviewer | Contribution rules, identity, ECA, AI attribution, dependencies, documentation and PR requirements | Fresh read-only Codex session; explicit legal/human/remote blockers |
| Repair agent | Resolve actual failed checks or review findings | Scoped source/test edits; at most three repairs; fresh verification/reviews afterward |
| PR writer | Cause, resulting behavior, measured validation, limitations and AI disclosure | Read source/evidence and write PR draft files; no publishing authority |

Deterministic Python gates use Git, GitHub CLI/API, Docker, CMake, Ninja, GCC 14,
CTest and gcovr 8.6. They freeze a patch digest, reproduce a failure on the old
production code, run the same regression on the fix, execute host regression
suites serially, and reject stale or failing independent reviews. Agents cannot
replace executed checks with assertions that checks passed.

The publisher creates a draft PR, and the monitor checks its exact head SHA,
Eclipse ECA, required regression jobs, applicable additional CI, review decision,
draft state and mergeability. **A draft or missing approval is never reported as
ready to merge.** This workflow does not merge PRs or bypass upstream rules.

## Storage and evidence

The mounted `/dev/loop4` filesystem is
`/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0`.

- `threadx-contributions/fabro-storage/`: dedicated Fabro database, run logs,
  workflow versions and engine objects. The server listens on localhost port
  `32277`, independently of the existing Fabro server.
- `threadx-contributions/744/source/`: isolated upstream feature branch.
- `threadx-contributions/744/baseline/`: original-code worktree for negative tests.
- `threadx-contributions/744/evidence/`: agent traces, command logs, builds,
  snapshots, reviews and PR assessment.
- This repository's `artifacts/`: exported patch, validation logs, review
  decisions, workflow/run bindings, PR text/status and SHA-256 manifest.

Authentication remains outside this repository. No API keys, bearer tokens,
refresh tokens, or Fabro bootstrap credentials belong in contribution artifacts.
The Docker verification image is managed by the host Docker daemon; compilation
outputs are bind-mounted onto loop4.

## Inspect and run

```bash
python3 contributions/threadx-744/workflow/fabro_control.py status
/home/jefferson/.fabro/bin/fabro validate \
  contributions/threadx-744/workflow/workflow.fabro
```

The dedicated server and clean isolated source checkout must exist before
starting a new run:

```bash
python3 contributions/threadx-744/workflow/fabro_control.py launch
```

Read [the process audit](process-audit.md), [regression design](regression-design.md),
and [Fabro execution notes](fabro-notes.md) for exact requirements and limitations.
The captured upstream guide and rulesets are in `evidence/upstream-process/`.
Issue #741 and PR #742 are resolved prerequisites; their fixes must not be
duplicated. The module-manager truncation is separate scope.

ThreadX requires the human contributor to review AI-assisted output and hold a
matching signed ECA. The workflow cannot sign that agreement, certify a human
review, grant an upstream approval, or turn an unavailable check into a success.
