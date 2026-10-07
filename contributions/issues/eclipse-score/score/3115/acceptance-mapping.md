# Issue acceptance and merge mapping

#3115 asks which of eight options best fit S-CORE and defines its DoD as “Decision Record done for the topic.” Native version 3 now supplies a concrete, reasoned selection by role rather than only promising a future evaluation. Native status remains `proposed` until an authorized project decision; acceptance and issue closure are pending.

| Obligation | Artifact / evidence | Disposition |
| --- | --- | --- |
| Packaging comparison | Native DR and [comparison](completion/comparison.md): APM, Lola, OKIT | Recommend APM, fallback Lola, isolated OKIT prototyping; exact source/version and limitations stated |
| SDLC/harness comparison | Spec Kit, Syspilot, BMAD, Pharaoh in the native DR/table | Recommend Spec Kit for integration development; native engineering remains S-CORE; explicit deferred/reuse dispositions for all alternatives |
| Evaluation framework | Harbor in the native DR/table | Recommend as shared benchmark driver; native checks and authorized reviews govern outcomes |
| Problem, criteria and decision rationale | Context, Selection Criteria, Decision, Alternatives, Consequences and Justification in the native DR | Authored; semantic acceptance remains with reviewers |
| Real native experience and limitations | Original fabric/native packets; historical failures and measured proxies | Retained with source bindings; no fresh qualification or comparative execution claim |
| Native format, identity, license and impact | `dec_rec__infra__ai_sdlc_tooling`, proposed, version 3; Apache-2.0; current infrastructure path | Candidate checked against native tooling; changes only the new DR; no requirement/design/interface/safety assumption edits |
| Reconcile #3140 | Native Reconciliation and Implementation Handoff | Merge one same-ID representation; supersede the other PR, or transfer this source into #3140; no other contributor branch modified |
| Native documentation validation | [Current report](completion/verification-report.json) | Final candidate results bound to version 3; previous inherited failure was fixed upstream by `6122462` and retained as history |
| Contribution identity | Signed-off commits and live ECA status in publication | DCO signed; ECA reported for the exact final native commit |
| Branch merge rules | `completion/rules.json`, ruleset 2965247 | Require one approving review, code-owner coverage and ECA; approvals absent at initial capture |
| Configured CI | `completion/native-guidance`, common reusable CI and local check records | Record each executed, carried, conditional or hosted-pending check; local success is separate from GitHub execution |
| Complete review record | [Merge readiness](completion/merge-readiness.md), source patch, logs, exports, SHA-256 inventory | Contributor material prepared; required human decisions remain explicitly pending |

## Completion boundary

The issue's published DoD does not itself mandate executing all eight tools, proving organization-wide adoption or qualifying an operational safety tool. This PR recommends the tool combination on the available labelled evidence. Reviewers may require further comparative evidence before acceptance; those requests must be addressed if made. Packaging rollout, native-context prototypes and qualified production use are explicit follow-on implementation work, not fabricated completed obligations.

A maintainer must approve the evaluation content, reconcile the parallel proposal and authorize merge. Hosted workflows still require maintainer approval to run. No review, qualification, merge or issue closure is inferred from passing local checks.
