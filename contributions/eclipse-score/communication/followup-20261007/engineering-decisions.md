# Native engineering decisions still required

The user has deferred #1031 production safety decisions to a separate Config
Management follow-up. The AoU derivation, received-AoU and safety-record rows
below describe that unresolved follow-up. The current contribution retains the
proposal and measured technical checks; the companion remains a draft and #1031
stays open. Dependency approval and required CI/reviewer checks remain pending.

| Decision / gate | Concrete review input | Required outcome |
| --- | --- | --- |
| Real consumer selection | Public Config Management main, its provider requirements and default LLVM 19.1.0 profile; discovered from #1031 | Owners confirm the intended integration and supported production profiles |
| Dependency migration | Config Management patch: score_tooling 1.2.0 override to 2.3.1; existing LLVM pin retained; native libclang and safety rule API changes | Approve the compatibility/migration and a published Communication dependency containing the public alias |
| AoU derivation | `AdditionalProxyNeedsRegistration@2` derives from `MonotonicSemiDynamicMemoryAllocation@1`, with existing feature link and QM classification retained | Assess actual satisfaction and classification; correct native requirements if needed |
| Received AoUs | Communication `mw_com` dependency imports the complete native set | Assess each applicability, satisfaction or forwarding disposition with engineering rationale; no blanket acceptance |
| Safety records | Full-index stderr and generated inputs: unknown `mitigates`, sample AoU/failure-mode records, missing concrete component implementation links | Replace/disposition placeholders, establish valid root-cause links and real component evidence, then build/test the complete index and check duplicate processing |
| Finding location semantics | Original MIT query, fixed query, original/fixed SARIF and comparison | Accept actual use-site locations for definitions unavailable in the database; primary selection stays intact |
| Analyzer safety / qualification | Issue #751 is safety related; exact native pins, 218-query suite, complete source-coverage manifests | Assess qualified use and finding dispositions in the project's process; successful execution supplies no safety acceptance |
| Copyright | Final complete-repository check results and license-header audit | Complete: both native checks pass; all 2,858 current code files and 13 packet helpers have verified notices. Earlier failures are historical evidence |
| CI and contributor eligibility | Native policies and required-check inventory | Passing required hosted jobs and codeowner approvals; existing ECA evidence retained; strict eligibility must bind the new PR commits |

The agent supplies proposed code and measured evidence. These engineering
decisions require authorized native owners; no approval or accepted safety work
product is represented as complete in this packet.

Workflow basis: [score-rust-workflow SKILL.md](/home/jefferson/.codex/skills/score-rust-workflow/SKILL.md)
states, “authorized humans decide offline.” Here the unresolved legacy safety
records and received-AoU satisfaction/classification need native owner decisions;
the packet preserves the concrete proposal and failed index rather than claiming
those decisions have been made.
