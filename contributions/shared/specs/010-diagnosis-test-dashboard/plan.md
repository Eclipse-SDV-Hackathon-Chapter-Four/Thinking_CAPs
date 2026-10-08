# Implementation Plan: Diagnosis and Test Management Dashboard

**Branch**: `contributions/eclipse-sdv-hackathon` | **Date**: 2026-10-04
**Spec**: [spec.md](spec.md)

## Summary

Implement observational diagnosis and deterministic campaign management in a local
browser. Reuse native OpenSOVD discovery, openDuT CLEO observations and the project
runner. Persist authoritative run identity; show cancellation and cleanup separately;
retain immutable historical verdicts and downloadable evidence.

## Technical Context

**Language/Version**: Python 3.10+, vanilla browser JavaScript/HTML/CSS.
**Primary Dependencies**: Python standard library; existing /usr/bin/python3 native
campaign dependencies, pinned openDuT0.10.2, native diagnostic executable.
**Storage**: private .local dashboard ledger/run directories; explicitly registered
historical evidence and SHA256 identities. No credentials served.
**Testing**: unittest contract/failure/concurrency tests, actual Chromium browser
at 360/1280 widths, actual native and CARLA campaigns and cancellation.
**Target Platform**: current Linux host, localhost/SSH-forwarded browser.
**Project Type**: local web service and browser UI.
**Performance Goals**: observation acquisition poll0.5s; new successful snapshots
visible within2s, outage invalidation within5s; cached HTTP responses independent
of vehicle control. No fabricated timing claim when native service is absent.
**Constraints**: one campaign per bench, two browser clients, bounded responses,
fail closed on unresolved cleanup/restart, no arbitrary commands/vehicle actions.
**Scale/Scope**: one configured receiver/bench; three admitted campaigns; bounded
result/event browsing and streaming downloads. AAOS/FOTA excluded.

## Constitution Check

Pre-design and post-design gates pass: I baseline/bridge untouched; II integration
owned source only; III this slice specifies/plans/tasks/tests/reviews; IV actual
upstream providers and managed bench reused; V background workers/process separation;
VI provenance/unknown fields retained; VII run inputs pinned by existing manifests;
VIII concurrency, stale/outage, restart, cancellation, cleanup and integrity tests;
IX blocked/skipped/fixtures remain explicit; X no upstream publishing; XI prepared
work labelled; XII runner assertions remain deterministic. No justified violations.

## Project Structure

```text
integration/dashboard/{service.py,web/index.html,web/app.js,web/style.css}
scripts/run_dashboard.py
config/dashboard/local.example.json
tests/test_dashboard.py
tests/dashboard_browser_smoke.py
evidence/f010-*/
specs/010-diagnosis-test-dashboard/{research.md,data-model.md,contracts/api.md,quickstart.md,tasks.md}
```

Extend scripts/run_campaign.py with optional validated run ID and bench admission
lock. Add an append-only live event journal to OpenDut/tests/opendut_receiver_smoke.py;
final reports and algorithms are unchanged. Source layout avoids a new package
manager and preserves existing vehicle integrations. See research and API contract.
