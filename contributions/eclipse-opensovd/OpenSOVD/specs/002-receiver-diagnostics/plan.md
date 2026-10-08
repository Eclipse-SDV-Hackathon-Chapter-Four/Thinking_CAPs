# Implementation Plan: F002 — Receiver diagnostics

**Branch**: `contributions/eclipse-sdv-hackathon` | **Date**: 2026-10-04 | **Spec**: [spec.md](spec.md)

## Summary
Instrument the actual C++ receiver/controller in an isolated upstream worktree. Send small
nonblocking Unix datagram observations to a native Rust OpenSOVD provider with a timestamped
cache. Preserve bridge source and controller state policy; expose derived freshness separately.

## Technical Context
**Language/Version**: C++17 and Rust 2024, installed stable Rust 1.98.1 compatibility build.
**Primary Dependencies**: Existing S-CORE Bazel pins; OpenSOVD core/providers/models/server at
e25fa30d1bdcb6726e3b4c4ec5d683b783e7c1af; Tokio, serde, schemars via Cargo.lock.
**Storage**: in-memory latest observation; immutable test evidence, no new fault lifecycle yet.
**Testing**: C++ nonblocking transport tests; Rust clock/provenance/freshness/cache tests; HTTP fixture
and real receiver integration where the cached build/toolchain permits.
**Target Platform**: Linux co-located CLOCK_MONOTONIC, shared boot ID and explicit source session.
**Project Type**: native diagnostic service plus isolated upstream instrumentation patch.
**Performance Goals**: observation at control cadence, <4 KiB nonblocking send; HTTP reads cache.
**Constraints**: no source changes to existing bridge/original controller checkout; no live claims from fixtures.
**Scale/Scope**: one receiver, one speed input, one OpenSOVD app; configurable provisional budgets.

## Constitution Check
Twelve principles checked: native source provenance and unknown states explicit; no HTTP on
control path; no bridge changes; isolated upstream patch; prepared work labelled. FOTA deferred.
Post-design: no deviations. Datagrams may be dropped and availability then becomes stale.

## Project Structure
```text
contributions/eclipse-opensovd/OpenSOVD/integration/diagnostics/{Cargo.toml,Cargo.lock,src/lib.rs,src/main.rs}
contributions/eclipse-opensovd/OpenSOVD/patches/receiver-diagnostics/s-core-observation.patch
contributions/eclipse-opensovd/OpenSOVD/scripts/run_diagnostics.sh
contributions/eclipse-opensovd/OpenSOVD/tests/diagnostic_http_smoke.py
contributions/eclipse-opensovd/OpenSOVD/specs/002-receiver-diagnostics/{research,data-model,quickstart,tasks,completion}.md
```
Upstream worktree: /home/jefferson/sdv-score-diagnostics; base 93f8ea1e6f76714496c092902e00c9b91c58cdc8.

**Structure Decision**: Cargo git dependencies pin upstream and are reproducible; scripts may
use local path patches for audited checkout only through explicit configuration. Native OpenSOVD
implements HTTP/discovery; do not reimplement speculative SOVD routes.

## Complexity Tracking
No violations. Source-session/source build identity not derived from an unverified Git revision.
