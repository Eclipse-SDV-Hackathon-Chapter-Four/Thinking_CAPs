# Implementation Plan: F001 — Baseline audit

**Branch**: `contributions/eclipse-sdv-hackathon` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)

## Summary
Inventory the real local stack, verify runtime artifacts in their existing container mount
context, run a bounded smoke check and record precise blockers. Preserve all user changes.

## Technical Context
**Language/Version**: Python 3.10+ standard library; installed Spec Kit 0.14.0.
**Primary Dependencies**: Git, Docker; inspected existing CARLA Python API and S-CORE image.
**Storage**: versioned JSON and Markdown evidence, no secrets or payloads.
**Testing**: unittest for missing prerequisites/verdict aggregation; read-only live preflight.
**Target Platform**: local Linux with nested X-Verse repositories and Docker cache volume.
**Project Type**: integration CLI and documentation.
**Performance Goals**: bounded subprocess/network timeouts; no control-path modification.
**Constraints**: preserve bridge and dirty launcher; FOTA deferred by user on 2026-10-04.
**Scale/Scope**: one development host, six selected repositories, eight feature backlog entries.

## Constitution Check
All twelve principles apply. No bridge or control source changes; no speculative APIs;
inspected versus tested pins distinguished; blocked checks retain nonzero exit; preparation
labelled. Rechecked after design: no deviations.

## Project Structure
```text
scripts/audit_baseline.py
tests/test_baseline_audit.py
config/dependencies.lock.json
docs/{baseline,interfaces,feature-backlog,prepared-work,upstream-status}.md
evidence/<run-id>/{manifest,results}.json
specs/001-baseline-audit/{research,data-model,quickstart,tasks,completion}.md
```

**Structure Decision**: Use existing repository; JSON lock avoids an additional YAML parser.
Spec Kit scaffold installed only after verifying no existing setup. Keep contribution archives intact.

## Complexity Tracking
No violations. Research dispatched via installed speckit-plan Phase 0 research-agent instruction.
