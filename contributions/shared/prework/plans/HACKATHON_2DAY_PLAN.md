# Eclipse SDV Hackathon 2026 - Pre-Work vs 2-Day Hackathon Plan

## Rules Understanding

| Phase | Timing | What's Allowed |
|-------|--------|----------------|
| **Pre-Work** | Before Oct 6 | Research, design, documentation, environment setup |
| **Hackathon** | Oct 6-8 (2 days) | Actual coding, PRs, issues, integration, demo |

---

## PRE-WORK (Already Done - Declaration)

### What We Prepared Before Hackathon

| Item | Type | Status | Evidence |
|------|------|--------|----------|
| Architecture design | Documentation | Done | `ARCHITECTURE_WITH_XVERSE.md` |
| Research on S-CORE, OpenSOVD | Research | Done | `HACKATHON_TECHNICAL_README.md` |
| Understanding Issue #553 gaps | Analysis | Done | `ISSUE_553_DETAILED_REPORT.md` |
| Understanding CDA #543 bug | Analysis | Done | `docs/tasks/cda-543-results-not-options.md` |
| Environment setup guide | Documentation | Done | `FULL_ENVIRONMENT_SETUP.md` |
| Presentation slides | Documentation | Done | `HACKATHON_PRESENTATION_V5.pptx` |
| File reference guide | Documentation | Done | `CONTRIBUTION_FILES_REFERENCE.md` |

### What We DID NOT Do (Reserved for Hackathon)

- NO actual code written for contributions
- NO PRs submitted
- NO issues commented/claimed
- NO patches created
- NO demo implementation

---

## 2-DAY HACKATHON PLAN

### Day 1 (Oct 6) - Morning (4 hours)

#### Hour 1-2: Setup & Claim Issues

| Task | Owner | Deliverable |
|------|-------|-------------|
| Clone all repos locally | All | Working dev environment |
| Comment on Issue #553 (claim it) | Member 1 | GitHub comment |
| Comment on Issue #543 (claim it) | Member 2 | GitHub comment |
| Set up X-Verse container | Member 3 | Running Docker |

```bash
# Clone repos
git clone https://github.com/eclipse-opensovd/opensovd-core
git clone https://github.com/eclipse-opensovd/classic-diagnostic-adapter
git clone https://github.com/eclipse-score/inc_diagnostics
```

#### Hour 3-4: Start CDA #543 Fix (Guaranteed Quick Win)

| Task | File | Change |
|------|------|--------|
| Add error variants | `cda-main/src/mdd.rs` | Add `StorageUnavailable`, `MissingPayload`, etc. |
| Fix `load_mdd_paths_from_storage` | `cda-main/src/mdd.rs:256` | `Option` → `Result` |
| Fix `build_diagnostic_database` | `cda-main/src/mdd.rs:431` | `Option` → `Result` |
| Fix `create_ecu_manager` | `cda-main/src/mdd.rs:476` | `Option` → `Result` |
| Run tests | - | `cargo test --locked --lib` |

**Target:** PR submitted by lunch

---

### Day 1 (Oct 6) - Afternoon (4 hours)

#### Hour 5-6: Issue #553 - OpenSOVD API Fixes (Start)

| Fix # | File | Issue | ISO Reference |
|-------|------|-------|---------------|
| 1 | `opensovd-core/src/data.rs` | Mode.value mandatory | §7.4 |
| 2 | `opensovd-core/src/bulkdata.rs` | Category enum | §8.2 |
| 3 | `opensovd-server/src/routes/discovery.rs` | Discovery endpoint | §6.1 |
| 4 | `opensovd-server/src/routes/entities/component.rs` | Restart endpoint | §7.8 |

#### Hour 7-8: Continue Issue #553 + Start Demo

| Fix # | File | Issue | ISO Reference |
|-------|------|-------|---------------|
| 5 | `opensovd-server/src/routes/entities/area.rs` | Area listing | §7.2 |
| 6 | `opensovd-server/src/routes/entities/app.rs` | App metadata | §7.3 |
| 7 | `opensovd-server/src/routes/error.rs` | Error format | §9.1 |
| 8 | `opensovd-server/src/routes/version.rs` | Version endpoint | §6.2 |

**Parallel Track:** Start cruise control demo setup

---

### Day 1 Evening (Optional 2 hours)

| Task | Deliverable |
|------|-------------|
| Test Issue #553 fixes | All 8 fixes verified |
| Run `cargo clippy` | No warnings |
| Prepare PR description | Draft PR ready |

---

### Day 2 (Oct 7) - Morning (4 hours)

#### Hour 1-2: Submit PRs + Start PR #16 (sovd_adapter)

| Task | Target |
|------|--------|
| Submit CDA #543 PR | https://github.com/eclipse-opensovd/classic-diagnostic-adapter/pull/NEW |
| Submit Issue #553 PR | https://github.com/eclipse-opensovd/opensovd-core/pull/NEW |
| Start sovd_adapter code | `third_party/inc_diagnostics/` |

#### Hour 3-4: PR #16 - sovd_adapter Implementation

| File | Lines | Purpose |
|------|-------|---------|
| `sovd_adapter/src/lib.rs` | ~300 | Main adapter |
| `sovd_adapter/src/data_provider.rs` | ~200 | DataProvider trait |
| `sovd_adapter/src/fault_provider.rs` | ~150 | Fault/DTC provider |
| `sovd_adapter/src/component.rs` | ~100 | Component registration |
| `sovd_adapter/src/types.rs` | ~80 | Type definitions |
| `sovd_adapter/src/error.rs` | ~70 | Error handling |

---

### Day 2 (Oct 7) - Afternoon (4 hours)

#### Hour 5-6: Demo Integration

| Component | Task |
|-----------|------|
| X-Verse | Verify gatewayd, someipd, cruise_control running |
| cruise_bridge | Connect to TCP :7700 |
| cruise_diag | Implement fault detection |
| sovd_adapter | Wire to OpenSOVD |

#### Hour 7-8: Dashboard + Final Testing

| Task | Deliverable |
|------|-------------|
| Dashboard HTML | Live speed + DTC display |
| End-to-end test | Signal loss → DTC → Dashboard |
| Record demo video | 60-second demo |
| Final PR cleanup | All PRs submitted |

---

### Day 2 Evening - Presentation Prep

| Task | Time |
|------|------|
| Rehearse presentation | 30 min |
| Verify all PRs submitted | 15 min |
| Prepare Q&A answers | 30 min |
| Final demo run | 15 min |

---

## Deliverables Checklist

### Code Contributions (During Hackathon)

| # | Contribution | Repository | PR/Issue | Lines | Day |
|---|--------------|------------|----------|-------|-----|
| 1 | CDA #543 fix | classic-diagnostic-adapter | PR | ~230 | Day 1 AM |
| 2 | Issue #553 (8 fixes) | opensovd-core | PR | ~770 | Day 1 PM |
| 3 | PR #16 sovd_adapter | inc_diagnostics | PR | ~900 | Day 2 AM |
| 4 | Demo | Our repo | Commit | ~800 | Day 2 PM |
| **Total** | | | | **~2,700** | |

### Evidence to Collect

| Evidence | Format | When |
|----------|--------|------|
| PR URLs | Links | After each submission |
| GitHub screenshots | PNG | After PR submission |
| Demo video | MP4 | Day 2 evening |
| Test logs | TXT | After each test run |
| Dashboard screenshot | PNG | Day 2 PM |

---

## Timeline Summary

```
DAY 1 MORNING (4h)
├── Setup repos (1h)
├── Claim issues on GitHub (30min)
└── CDA #543 fix + PR (2.5h) ✓ QUICK WIN

DAY 1 AFTERNOON (4h)
├── Issue #553 fixes 1-4 (2h)
├── Issue #553 fixes 5-8 (1.5h)
└── Start demo setup (30min)

DAY 2 MORNING (4h)
├── Submit CDA #543 PR (30min)
├── Submit Issue #553 PR (30min)
└── PR #16 sovd_adapter (3h)

DAY 2 AFTERNOON (4h)
├── Demo integration (2h)
├── Dashboard (1h)
└── Testing + video (1h)

DAY 2 EVENING
└── Presentation prep (1.5h)
```

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| CDA #543 takes longer | It's the simplest - do first |
| Issue #553 has conflicts | Check latest main branch first |
| X-Verse doesn't start | Have backup simulation mode |
| PR not merged in time | Submission counts, not merge |
| Demo fails | Record backup video early |

---

## Commands Quick Reference

```bash
# CDA #543
cd classic-diagnostic-adapter
cargo build --release
cargo test --locked --lib
cargo clippy --all-targets -- -D warnings

# Issue #553
cd opensovd-core
cargo build --release
cargo test
cargo clippy

# PR #16
cd inc_diagnostics
cargo build --release -p sovd_adapter

# Demo
cd demo/X-Verse/external_hackathon_ecus/OpenSOVD/gateway/harness
cargo build --release
python3 demo/live/server.py
```

---

## Success Criteria

| Metric | Target |
|--------|--------|
| PRs submitted | 3 (CDA, opensovd-core, inc_diagnostics) |
| Lines of code | ~2,700 |
| Demo working | Yes |
| Presentation ready | Yes |
| All team members contributed | Yes |

---

*Plan prepared for Eclipse SDV Hackathon 2026 (Oct 6-8)*
