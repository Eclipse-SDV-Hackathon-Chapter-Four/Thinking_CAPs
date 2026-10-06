# Feature Specification: S-CORE Rust issue workflow

**Date**: 2026-10-05. **Status**: Scoped procedural addition; engineering acceptance pending.
**Authority**: User request to create a Rust workflow suitable for S-CORE, using
[communication #1265](https://github.com/eclipse-score/communication/issues/1265) as an example.
This authorizes workflow authoring and local validation, not implementation of that issue.
The user clarified that the workflow must be generic for Rust issues across S-CORE;
#1265 is an optional example, not the entrypoint's scope or a required dependency stage.

## User scenarios and verification

### US1 — Resolve a Rust issue against the actual native baseline (P1)
An engineer invokes `score-rust-workflow` with a repository, issue and permitted scope.
The procedure binds issue/source revisions, discovers native build and engineering
obligations, implements authorized changes, measures checks and exports an offline packet.
Verification: a read-only walkthrough of #1265 must notice existing `pastey` usage,
select Bazel rather than fabricate a Cargo workspace, and retain qualification gaps.

### US2 — Assess a compile-time dependency (P1)
The engineer inventories the resolved dependency and generated API, compares retention,
replacement and internal implementation, and drafts applicable qualification records.
Verification: every acceptance criterion of #1265 maps to evidence and an artifact;
an unknown crate version, safety relevance or qualification decision stays unresolved.

## Functional requirements

- RW-001: Provide a discoverable Codex skill with lazy references and a usage example.
- RW-002: Bind native baseline, policies, issue activity, hooks, storage and write scope;
  stop on disconnection/drift. Preserve reference repositories and original work.
- RW-003: Discover Bazel/Ferrocene/native lint, test and documentation configurations;
  use Cargo only where native manifests/configuration support it. Do not weaken locks.
- RW-004: Route defects, API/features, unsafe/FFI, concurrency, platform/build, dependency
  and documentation issues to relevant checks. Cover ownership/FFI/unsafe/error impacts according to supplied
  obligations, preserving requirement/design/safety/verification trace and native statuses.
- RW-005: Cover exact macro patterns, resolved version/features, provenance, licensing,
  maintenance, qualification applicability, alternatives and generated API compatibility.
- RW-006: Export complete hash-bound evidence, failures, unavailable checks and proposed
  engineering decisions for offline review; terminate without runtime approval nodes.
- RW-007: Distinguish procedural delivery from validated runtime/language qualification;
  leave existing registries, source locks, active queues and human markers unchanged.

## Success criteria

The skill validates structurally; linked resources exist; the issue walkthrough covers
all four acceptance criteria; source observations have pinned URLs/digests; repository
foundation and packaging checks are recorded. No runtime scheduling, model call or
upstream mutation is required. Native engineering acceptance is not a delivery criterion.

## Edge cases and assumptions

Already-changed dependencies trigger baseline reconciliation rather than duplicate migration.
Missing licenses, toolchain capabilities, native IDs or expected checks remain gaps.
Manual/excluded tests are explicitly enumerated. QNX capability cannot be inferred from Linux;
this operator has no QNX license, so unavailable checks are recorded without reacquisition.
The deliverable is a procedural skill, with no claim of Fabro activation or Rust qualification.
