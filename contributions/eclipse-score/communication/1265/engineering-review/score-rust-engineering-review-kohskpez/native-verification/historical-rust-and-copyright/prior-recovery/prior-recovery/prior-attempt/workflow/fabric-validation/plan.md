# Implementation Plan: S-CORE Rust issue workflow

**Date**: 2026-10-05. **Branch**: existing `011-change-impact-and-freshness`.
**Input**: [specification](spec.md). No existing increment files need modification.

## Summary and technical context

Create `.agents/skills/score-rust-workflow/` as the repository-owned procedure and
expose that same directory under the local Codex skills directory using a non-overwriting
symlink. Markdown/YAML instructions and a report template require no runtime dependency.
Validation uses existing frozen Python tooling and the skill-creator validator.
Native builds are outside this authoring task. Scratch uses the shared storage selector.

## Constitution check

S-CORE remains engineering authority. Spec Kit records this bounded maintenance scope.
Fabro remains execution authority; Codex installation confers no Fabro runtime support.
The skill consumes supplied native obligations and drafts decisions, never defines
applicability, qualification, acceptance or approval policy. Reports terminate for offline
human review. No new scheduler, requirements store, live call or publishing action.
Current native profiles/registries/source locks and pre-existing user changes are preserved.

## Research and design

Read pinned S-CORE Rust guidance and process tool-management sources, plus the example
issue and selected communication revision. Record observations in the lazy issue guide
and [source receipts](source-receipts.json). Observations supplement existing locks;
they do not amend them or establish accepted project tailoring.

The entrypoint handles issue-to-packet progression. Conditional references cover native
verification, issue-specific checks and dependency/macro assessment; an optional example
documents #1265's actual baseline. Ordinary Rust defects do not require the example or
dependency comparison unless their impact actually includes those surfaces.
The report template captures acceptance mapping, provenance, expected checks, raw
evidence references, proposed decision and pending engineering acceptance.

## Verification

Resolve/check local reference paths, validate metadata and discovery, perform a read-only
example walkthrough, and run foundation/package checks. Record results and subject
digests in [validation](validation.json) and [acceptance](acceptance.md).
No source code changed: Rust build results and Python regression results are not claimed.
Detailed future issue tasks are created only when that implementation is authorized.
