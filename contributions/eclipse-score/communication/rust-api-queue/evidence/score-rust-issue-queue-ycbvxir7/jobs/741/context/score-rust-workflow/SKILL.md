---
name: score-rust-workflow
description: Resolve Rust issues across Eclipse S-CORE repositories, from defects and API changes to unsafe/FFI, concurrency, dependencies and documentation, using native requirements, verification and offline engineering review.
metadata:
  version: "1.0.0"
---

# S-CORE Rust issue workflow

Deliver a scoped patch or assessment, measured verification results and a portable
offline review packet. A documentation/qualification issue may require no code change.
Read only the references needed for the selected activity.

The same workflow applies across S-CORE modules. Begin with the issue's actual change
surface, not a communication-specific template. Read [issue-specific checks](references/issue-types.md)
when planning a defect, API, unsafe/FFI, concurrency, platform or documentation change.
Dependency assessment is conditional; example #1265 is optional guidance for that class.

## Bind the task

1. Establish the issue/repository, source commit, requested outcome, permitted write paths,
   artifact destination and execution/network/budget limits. Fetch current issue/PR activity
   when available and record retrieval time; preserve the original issue text separately.
   Check whether the issue's premise still matches the chosen source. A label or unchecked
   issue-template field does not establish safety relevance or unchanged requirements.
2. Read applicable `AGENTS.md`, native contribution/CI guidance and the supplied process,
   tailoring, requirements, architecture, safety assumptions and verification obligations.
   In the fabric, read its constitution, active increment and handoff. Spec Kit governs
   fabric changes; keep target engineering artifacts in the native repository's format.
   Use baseline-bound Context Manifest/task envelope when supplied. Missing native IDs
   remain unknown: discover them from selected sources rather than create lookalikes.
3. Preserve user changes, original brief, licenses and reference repositories. Create
   native build/edit work only in a disposable copy. Inspect Git hooks, native build
   rules, imported configs and executable setup scripts before execution. Bind initial
   source/lock/policy/tool hashes and the planned change/check scope.
4. Allocate scratch with `score-fabric storage` / `score_sw_fabric.storage`; use
   `new_run_root`, `build_environment` and `validate_run_root`. Prefer the measured writable
   external SSD/Linux image, with internal fallback only for new allocations. Validate
   the same binding before each stage and stop if disconnected/remounted. Keep credentials
   and private server state internal. Do not alter global caches or active queues.

## Plan the native change

Identify the affected native functions, API users, build-time generators and runtime
paths, including FFI and generated-code consumers. Preserve IDs, status, link direction,
source revision and license notices in the trace. Derive expected checks/work products
from native obligations, with a source and disposition for every omission; unresolved
applicability blocks readiness without preventing useful bounded research.

Discover `MODULE.bazel`, its lock and BUILD rules before assuming Cargo exists. Select
compiler/target/lint/release configurations from that baseline. Ferrocene's name alone
does not prove tool qualification for the selected version, target or use.
Read [native verification](references/native-verification.md) before configuring checks.

For a crate, procedural macro or generated API issue, read
[dependency and macro assessment](references/dependency-and-macros.md). For communication
#1265 specifically, also read [the source-bound example](references/communication-1265.md).

Draft the smallest change plan with issue acceptance → native obligation → changed
artifact → check → reviewer mapping. For Rust behavior changes, inspect affected
ownership/lifetimes, unsafe invariants, FFI layout/ABI, concurrency, failure handling,
allocation and panic/unwind behavior as required by the supplied constraints. Record
requirement/design/safety impacts and reasons; do not transfer MISRA C++ policy to Rust.
Choose a proposed implementation using the task's authority. Retain/replace/internal
dependency decisions remain reviewable proposals until accepted by authorized humans.

## Implement and measure

Change only authorized paths in the disposable copy. Preserve native lint profiles,
toolchain pins and supported feature/target combinations; a pin change must be explicit
and traced. Do not introduce Cargo scaffolding, upgrade dependencies or suppress lints
just to make a check succeed. Add regression cases for the actual failure or compatibility
risk, using native test rules; avoid tests that merely duplicate the implementation.

Run the selected checks through the bound environment. Separate agent assertions,
directly executed local checks, trusted collector evidence and fixtures. Retain exact
commands/configs, tool identities, inputs, exit codes, timings and complete raw logs on
the host. Supply bounded summaries and file/hash references to the model. Count manual,
excluded, unsupported and failed checks in the expected-check inventory. Reuse evidence
only after verifying subject hashes and label it carried evidence.

Before broadening a failing run, determine whether the subject changed or a relevant
concern remains. Honor supplied attempt/time/byte ceilings and stop on their exhaustion
or a repeated unchanged failure. Do not invent operational budgets or self-authorize
paid calls. For a required human decision, export the current proposal and evidence and
terminate the run; use no human/wait-for-approval nodes in Fabro.

## Export and terminate

Use [the report template](assets/review-packet.md) for issue acceptance mapping, trace,
dependency/qualification findings, patch, expected checks and pending decisions. Adapt
sections to the task while retaining gaps. Hash-bind all packet files and external raw
evidence to the exact final baseline/patch/configuration; exclude secrets. Preserve
failed attempts and outdated evidence as history. A stale report is not fresh evidence.

Report technical completion separately from native engineering acceptance. An agent may
recommend; deterministic tools measure; authorized humans decide offline. Do not mark
native work products qualified/released/accepted or close safety findings without the
required human decision. Tests, clean analyzers and Fabro success cannot supply it.

This is a Codex procedure. Fabro owns execution/run state when an explicitly admitted
runtime uses it; installation does not register or validate Fabro language support.
It grants no authority to comment, publish a PR, merge, release or deploy. Finish with
the packet location, measured outcomes, unresolved obligations and concrete next action.
