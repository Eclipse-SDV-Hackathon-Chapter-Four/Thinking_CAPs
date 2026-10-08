# ThreadX contribution: issue #744

This folder contains the Fabro workflow and reviewable artifacts for
[eclipse-threadx/threadx #744](https://github.com/eclipse-threadx/threadx/issues/744).
The work starts from upstream `dev` and targets the same branch. The fix concerns
stack-address truncation when MISRA and stack checking are enabled together on
ports with 64-bit pointers and 32-bit `ULONG`.

The finalized patch passed independent technical and Eclipse process reviews.
All 29 scoped authored or modified files passed the publication license-header
audit, and all 70 workflow tests passed. The user confirmed the review dossier
and `jnsagai@gmail.com` as the ECA commit email; the receipt preserves the actual
messages. Only the approved human-review sentence in three new-file headers
changed after that review.

The final local run passed six focused tests, 807 single-core test instances and
three FreeRTOS tests with the documented constant-name profile. SMP passed
589/590 instances and failed one randomized preemption-threshold test. The same
assertion failed on the unchanged baseline with the same profile and affinity;
the suite remains failed and upstream final-head SMP CI must pass. Historical
failures are retained separately without unsupported waivers.

The companion [documentation PR #107](https://github.com/eclipse-threadx/rtos-docs-asciidoc/pull/107)
and the [kernel PR #799](https://github.com/eclipse-threadx/threadx/pull/799)
are published as drafts. Both final-head Eclipse ECA checks passed. Seven
kernel workflow runs report `action_required`; upstream CI execution and
maintainer approvals remain pending. Remaining requirements are recorded in
[current status](artifacts/current-status.json) and the exported readiness records.
The [human receipt](artifacts/human-review.json) records actual confirmation.
The authorized [intent-to-work comment](https://github.com/eclipse-threadx/threadx/issues/744#issuecomment-6044950779)
is posted; its exact text, permission and URL are retained.

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
| Documentation author | Matching stack-address clarification in rtos-docs-asciidoc | Codex shell/edit tools; one AsciiDoc paragraph and proposed PR text |
| Documentation reviewer | Independent contract, scope and actual rendered-page review | Fresh read-only Codex session; structured verdict on the documentation digest |
| Technical reviewer | Independent C99, pointer width, alignment, MISRA, test and coverage review | Fresh read-only Codex session; structured verdict returned to the driver |
| Eclipse process/IP reviewer | Contribution rules, identity, ECA, AI attribution, dependencies, documentation and PR requirements | Fresh read-only Codex session; explicit legal/human/remote blockers |
| Repair agent | Resolve actual failed checks or review findings | Scoped source/test edits; at most three repairs; fresh verification/reviews afterward |
| PR writer | Cause, resulting behavior, measured validation, limitations and AI disclosure | Read source/evidence and write PR draft files; no publishing authority |

Deterministic Python gates use Git, GitHub CLI/API, Docker, CMake, Ninja, GCC 14,
CTest and gcovr 8.6. They freeze a patch digest, reproduce a failure on the old
production code, run the same regression on the fix, execute host regression
suites serially, and reject stale or failing independent reviews. Agents cannot
replace executed checks with assertions that checks passed.
The license audit rejects missing copyright, license URLs, SPDX identifiers,
attribution changes and malformed new-file AI disclosures. It runs at freeze,
verification and publication; a passing agent review cannot waive it. Current
new-file headers honestly retain pending human review until the contributor
confirms it. Local workflow code follows the repository's Apache-2.0 license,
while upstream kernel/documentation files retain ThreadX's MIT licensing.
Generated build trees remain on loop4 with their original provenance; reports
and diagnostic logs are exported here without redistributing those raw builds.

Registration copies the runner, prompts, Dockerfile and regression design to a
content-addressed, read-only execution directory on loop4. The registered graph
executes that copy and validates every file against its manifest. The Docker
image is pinned by its immutable image ID. Reviews reject verification performed
by a different runner or image.

After successful checks and independent reviews, a Fabro human gate presents
both patches, measured results and proposed PR descriptions. The contributor
must confirm actual review, provenance and their ECA commit email. This is
required before submission, including a draft PR. The driver finalizes only the
approved AI header wording and verifies/reviews that resulting patch again.
Automatic approval and confirmation of a stale patch cannot satisfy this gate.
If the contributor agrees and supplies the email in separate messages, the
conversation adapter preserves those original messages against the existing
native question and invokes the reviewed immutable runner's gates. It records
the actual agreement without inventing a typed `REVIEWED` response.

An intermittent SMP `ERROR #7` was observed in both the candidate and the
unchanged upstream baseline. The workflow preserves any failed local SMP result.
It permits draft preparation only when the same assertion is freshly reproduced
in each failing configuration on unchanged SMP sources with the same compiler,
image and affinity, while all other local gates pass. This state is recorded as
`prepared-with-baseline-failure` with `local_validation_complete=false`.
Successful final-head upstream SMP CI remains required before requesting
upstream review or reporting merge readiness. See
[the baseline diagnostics](smp-baseline-diagnostics.md).
Separate original-code reproductions also cover
[disabled notifications](smp-disable-notify-diagnostics.md) and the historical
[default build](smp-default-diagnostics.md). Each preserves its actual compiler,
feature flags and CPU affinity; the preceding completed record was
`prepared-with-baseline-failure`, not a passing SMP suite.
The [historical trace affinity check](smp-trace-four-logical-diagnostics.md)
passed all ten baseline attempts, so that exact earlier profile has no matching
failure reproduction. The [diagnostic index](artifacts/diagnostics/smp-retained-failures-index.json)
keeps this limitation separate from the current results.
The earlier header-update attempt also failed an
[event-flag timeout assertion](smp-event-flag-timeout-diagnostics.md). Ten bounded
original-code runs passed, so that distinct historical failure has no supported
baseline waiver. Its failed record remains preserved.

The publisher creates linked kernel and documentation draft PRs, and the monitor checks their exact head SHAs,
Eclipse ECA, required regression jobs, applicable additional CI, review decision,
draft state and GitHub's protected-branch merge state. Passing CI and confirmed
contributor review allow marking the drafts ready for upstream review.
**A draft or missing upstream approval is never reported as
ready to merge.** This workflow does not merge PRs or bypass upstream rules.

## Storage and evidence

The mounted `/dev/loop4` filesystem is
`/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0`.

- `threadx-contributions/fabro-storage/`: dedicated Fabro database, run logs,
  workflow versions and engine objects. The server listens on localhost port
  `32277`, independently of the existing Fabro server.
- `threadx-contributions/executions/`: immutable runner/prompt snapshots bound to
  registered workflow versions.
- `threadx-contributions/744/source/`: isolated upstream feature branch.
- `threadx-contributions/744/baseline/`: original-code worktree for negative tests.
- `threadx-contributions/744/docs-source/`: companion documentation feature branch,
  targeting `main` rather than the kernel's `dev`.
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
python3 contributions/eclipse-threadx/threadx/744/workflow/fabro_control.py status
/home/jefferson/.fabro/bin/fabro validate \
  contributions/eclipse-threadx/threadx/744/workflow/workflow.fabro
```

The dedicated server and clean isolated source checkout must exist before
starting a new run:

```bash
python3 contributions/eclipse-threadx/threadx/744/workflow/fabro_control.py launch
```

Recovery entrypoints preserve measured work without pretending a failed run
passed: `launch verify` starts at a new freeze and fresh verification;
`launch validated` requires existing exact-patch verification and starts with
independent reviews; `launch resume` requires successful reviews and prepares
the human dossier. The driver enforces current digests in every case.

After publication, `launch monitor` reassesses the exact existing PR heads and
upstream approvals, exporting current blockers until both PRs are merge-ready.
It performs no new implementation or contributor attestation.

First-failure logs and diagnostics remain on loop4 and are exported. The corrected
GCC 14 image includes 32-bit Linux headers. Local SMP execution is constrained to
four distinct physical cores after an unrestricted randomized test failure and
recorded diagnostic comparisons; acceptance still runs every test once, with no
retries. Local FreeRTOS validation uses the supported `TX_ENABLE_CONST_NAMES`
configuration under GCC 14; the stock default profile remains an upstream CI
requirement. See [compiler diagnostics](compiler-diagnostics.md).

The [open-issue snapshot](artifacts/open-issues.md) lists all 52 issues returned by
the GitHub API on October 7, 2026. [issue-queue.json](issue-queue.json) records the
selected follow-up candidates; [issue-selection.md](issue-selection.md) explains
their relevance to this integration. Only #744 is admitted for implementation.

Read [the process audit](process-audit.md), [regression design](regression-design.md),
and [Fabro execution notes](fabro-notes.md) for exact requirements and limitations.
The captured upstream guide and rulesets are in `evidence/upstream-process/`.
Issue #741 and PR #742 are resolved prerequisites; their fixes must not be
duplicated. The module-manager truncation is separate scope.

ThreadX requires the human contributor to review AI-assisted output before submission and hold a
matching signed ECA. The workflow cannot sign that agreement, certify a human
review, grant an upstream approval, or turn an unavailable check into a success.
