# Merge requirements and available artifacts

These contributions are locally reviewable proposals. None is demonstrated to
completely close its issue or satisfy every merge requirement. Do not submit them
as ready for merge or use automatic issue-closing language yet.

The live `main` rules were read on 2026-10-07 and retained in
`inputs/current-main-rules.json`, with extracted requirements in
`merge-requirements.json`. This observation can change; evaluate the rules again
on the final upstream PR head. Native workflow and contribution instructions are
retained under `inputs/native-context/`. Local checks do not create GitHub statuses.

## What each issue still needs

| Issue | Concrete remaining acceptance work | Available implementation/review artifacts |
| --- | --- | --- |
| #1261 | Maintainer agreement to discovery over configured LoLa types, or an implementation covering the broader system-wide requirement; ABI migration and external implementers; allocation/lifetime review | Full baseline-applicable candidate patch, supplemental warning patch, source manifest, original design changes, native units/integrations/doctests/analyzer evidence and explicit D1/D6 review subjects |
| #250 | Agreement to typed Any as the intended scope, or broader discovery; typed bridge error/warning disposition; external trait implementers and lifetime review | Full unchanged candidate patch, exact 2,883-source binding to carried tests, source manifest, native Any design/tests and SARIF evidence; unresolved new API warning recorded |
| #560 | Accepted native-to-Rust state/get/set/unset contract, error and concurrent callback behavior, FFI ownership review and required full verification | Full baseline-applicable candidate patch, supplemental warning patch, source manifest, production integrations, helper/LoLa units, mock compilation and analyzer evidence |

The patches are independent proposals with overlapping changes. Rebase or combine
them on the chosen upstream head, resolve conflicts, and bind fresh verification
to the resulting commits. Original branch bundles remain historical and omit the
new corrections. The local PR descriptions under `pr-drafts/` describe the final
review subjects and deliberately use “Related to” while acceptance is unresolved.

## Actual protected merge gates

| Required artifact/status | Evidence available here | Remaining artifact/action |
| --- | --- | --- |
| `eclipsefdn/eca` | Official successful lookup for the declared Eclipse username, original author/provenance and license inputs | Successful commit/PR validation for every final contributor identity; username lookup alone does not validate commit email or contribution rights |
| `GCC15 / Build & Test` | Selected Linux targets, raw results and test payloads; explicit omissions | Successful full native CI status on the final PR/merge-group head |
| `QCC - Build & Test` | Platform applicability inventory | Required QNX/QCC build/test status; no applicable exemption is established here |
| `Address & Undefined Behavior Sanitizer / Build & Test` | FFI/lifetime review subjects | Required native sanitizer status |
| `Thread Sanitizer / Build & Test` | Concurrency review subjects | Required native thread-sanitizer status |
| `Linters / clang-tidy` | Changed C++ surfaces and native configuration inputs | Required whole-scope C++ analyzer status and finding disposition |
| `Linters / clippy` | Selected library/binary analysis and warnings, including retained SARIF; test-target commands produce noop placeholders | Required native workflow status and disposition of remaining findings; exit zero from selected aspects is insufficient |
| `Linters / ruff` | Native workflow and Python integration sources in the full patches | Required native workflow status |
| `review-checklists` | Native review configuration/workflow and offline review subjects | Successful native checklist status; no completed human review is attested |
| PR approvals | Baseline CODEOWNERS and `HUMAN-REVIEW.md` | At least one approving review and code-owner review; stale approvals are dismissed on push, with extra approval required for unattributed changes |
| Merge queue | Observed queue configuration | Eligible PR and successful native merge-queue processing with all-green grouping |

The rules allow merge, squash and rebase, and do not require strict up-to-date
status checks. That does not establish source compatibility with the current
upstream branch or remove the need to measure the actual merged candidate.

## Other project instructions and work products

`CONTRIBUTING.md` also requests tests, a clear title/description, issue references,
copyright checking and formatting. `CI.md` and native workflows describe broader
analysis, documentation, module integration and platform verification. These are
tracked in `expected-checks.json`; they are not all presented as protected branch
status contexts. Native requirements/design/safety applicability and qualification
remain explicit review items rather than invented compliance artifacts.

The native copyright invocation fails on the unchanged baseline before scanning
files. `copyright-checker-path-companion.patch` corrects the root source-path
arguments for a separate diagnostic run. Diagnostic findings, when available,
describe that combined diagnostic tree; they do not validate IP rights or silently
alter any candidate patch. Full formatting and the remaining CI inventory are
open unless a result explicitly establishes otherwise in `verification.json`.

The packet supplies candidate patches, source/tool/environment identities, issue
and native-rule snapshots, exact selected execution evidence, warning dispositions,
an applicable-check inventory, PR drafts, human decision subjects and an integrity
manifest/verifier. Missing approvals, rights declarations, qualification evidence,
accepted requirement mappings and remote CI results cannot be authored as facts by
an automated contribution packet. The final status is **engineering acceptance
pending; merge readiness not established**.
