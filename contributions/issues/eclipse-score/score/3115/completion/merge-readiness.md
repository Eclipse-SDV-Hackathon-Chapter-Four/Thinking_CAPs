# Project merge and issue acceptance packet

Native subject `0dc49aad690c1fb15fb1ff3fee825cf05dbb910b` on main `f42e760912e5f99e0db993de717155cc85679f6c` changes only `docs/design_decisions/infrastructure/DR-010-infra.rst`. It preserves `dec_rec__infra__ai_sdlc_tooling`, proposed, version 3. The [patch](native-proposal.patch), [source](DR-010-infra.rst), [comparison](comparison.md), [acceptance mapping](../acceptance-mapping.md) and [verification report](verification-report.json) form the review package.

## Native obligations and actual disposition

| Obligation / source | Artifact or check | Result / remaining gate |
| --- | --- | --- |
| #3115 evaluation and decision record | Native Context, Selection Criteria, Decision, all eight Alternatives, Consequences and Justification | Concrete recommendations authored; authorized content acceptance pending |
| Native DR template | ID, proposed status, version 3, context/decision/tracking/consequences, required prose, Apache-2.0 header | Native docs/schema pass; no fabricated accepted status or native identifier |
| Native engineering impact | New DR only; native export comparison | One DR added; all 925 existing needs unchanged; no runtime/API/requirements/design/safety assumption changes |
| Parallel same-ID #3140 | Reconciliation and Implementation Handoff | Choose one merge vehicle; supersede other proposal or transfer this source; owner decision pending |
| Contribution guide and improvement template | Linked issue, description, closure-on-accepted-merge reference, code owner review | PR description and review request supplied; issue remains open until project accepts |
| ECA / DCO | Live final ECA status and contribution-commits.txt | Signed-off contribution commits; ECA captured for exact final head in publication |
| Documentation workflow | Current candidate docs_check and docs HTML | Pass; zero documentation/schema warnings; carried baseline is separately hash-verified |
| Shared PR checks | copyright.check, format.check, module tidy plus diff, module deps error mode | Pass; exact pinned policy/tool inputs and raw logs retained |
| PR-specific checks | gitlint 0.19.1 and FEP/FCP unit suite | Pass; all 30 unit cases pass; these tests do not perform a human FCP |
| Conditional checks | CI capability detection and label/config sources | Absent pre-commit config/Python uv project pair, disabled module-name step and absent FEP labels explicitly recorded; none silently omitted |
| Main branch ruleset 2965247 | rules.json and ruleset.json | Require one approving review, code owner coverage and passing ECA; stale approvals dismissed on push; extra approval condition for unattributed changes retained in source |
| Hosted workflow execution | Final run snapshots in publication.json | Maintainer must approve fork runs; local results do not claim GitHub CI success |
| Review evidence integrity | Outer packet manifest and artifact-inventory.json | Exact bytes/hash/size bindings; isolated published branch replay validates reference packets; known unrelated shared-workspace/registry limitations retained |

## Scope and human handoff

The DR recommends APM/Spec Kit/Harbor by role, retains the native process and explicitly disposes of all alternatives. Neither the issue's DoD nor the DR template makes comparative execution of every candidate or operational ASIL qualification an unconditional merge artifact. Further evidence becomes required if authorized reviewers request it. Follow-on rollout cases are specified in the native handoff; no deployment approval is inferred.

Required next human actions: review the content and #3140 reconciliation; approve fork workflow execution; satisfy the native CODEOWNERS approval rule; then accept and merge using project authority. Acceptance of this evaluation can resolve #3115 through the PR's closing reference. The contributor has not supplied or synthesized those human decisions.
