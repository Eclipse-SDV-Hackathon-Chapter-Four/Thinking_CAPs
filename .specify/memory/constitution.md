<!-- Sync impact: template -> 1.0.0, initial adoption of twelve principles.
Added execution constraints and workflow; no principles removed.
spec-template.md, plan-template.md and tasks-template.md reviewed: compatible.
Installed Codex skills reviewed. No deferred constitution placeholders. -->
# Open Vehicle Lifecycle Constitution

## Core Principles

### I. Preserve the vehicle baseline
Implementation MUST preserve the CARLA/S-CORE control return path and MUST NOT modify
the existing Zenoh/SOME-IP bridge source. Deployment changes require comparison evidence.

### II. Separate assets and contributions
Records MUST distinguish reused assets, integration changes and upstream contributions.
Upstream changes MUST be reviewable in isolated patches or checkouts.

### III. Deliver incremental slices
Each feature MUST have a specification, plan, tasks, verification and convergence review.
One slice MUST be reviewed before dependent implementation starts.

### IV. Reuse upstream implementations
Native providers, fault reporting and storage MUST be evaluated before replacements.
Fallbacks MUST name concrete blockers and accurately limit their claims.

### V. Respect process boundaries
Control, observation, diagnostics, test networking and installation MUST have explicit
contracts. HTTP service latency MUST NOT synchronously block the control loop.

### VI. Bind observations to provenance
Results MUST identify actual source, target, units, clock and available identity.
Missing integrity checks MUST be unavailable; derived state MUST be labelled.

### VII. Pin executable inputs
Revisions, dirty state, configuration hashes, tool versions and image IDs MUST be recorded.
Inspected pins MUST NOT be described as compatible until tested.

### VIII. Test failures and recovery
Meaningful tests MUST cover selected contract boundaries, timeout and recovery,
service loss, cleanup and update denial as features are admitted.

### IX. Preserve unknown and blocked outcomes
Missing observations MUST remain unknown; unavailable environments MUST produce blocked
or skipped outcomes. Fixtures and process startup alone cannot establish vehicle E2E success.

### X. Follow upstream requirements
Changes MUST follow affected repositories' instructions, licenses and mandatory checks.
External communication and publication require explicit user authorization.

### XI. Declare prepared work
Pre-event work MUST be labelled preparation. Records MUST capture actual event start
revision and delta; neither eligibility nor maintainer approval is assumed.

### XII. Use deterministic acceptance
Verdicts MUST use explicit assertions. Activation MUST require fresh stationary,
disengaged and authorized maintenance evidence plus independent post-install checks.
No LLM may determine runtime acceptance or activation.

## Execution Constraints

Use eclipse_sdv_hackathon_2026 and Spec Kit 0.14.0 Codex skills. Preserve unrelated
changes. Keep payloads, images, secrets and unrelated captures out of Git.
E2E, native updates and VIPER remain conditional.

## Development Workflow

Specify -> plan -> tasks -> implement -> converge per feature. Maintain backlog and
requirement-to-test evidence links. Precise environment blockers are valid audit results,
but not completion of the corresponding live integration milestone. Local reversible
implementation is already authorized by the user's implementation request.

## Governance

These principles govern integration artifacts subject to user instructions. Amendments
require rationale, version update and dependent-artifact review. Major versions change
principles incompatibly; minor versions add obligations; patches clarify.
Each feature review MUST check all principles and record unresolved deviations.

**Version**: 1.0.0 | **Ratified**: 2026-10-04 | **Last Amended**: 2026-10-04
