# Team Pre-Work Declaration Status

## Repository Location

```
/Users/purushothamerupuri/Downloads/eclipse_sdv_hackathon_2026-contributions-eclipse-sdv-hackathon/
```

---

## Completed Pre-Work (With Evidence)

### 1. SOME/IP #84 - Duplicate Server Registration

| Field | Value |
|-------|-------|
| **Repository** | eclipse-score/inc_someip_gateway |
| **Issue URL** | https://github.com/eclipse-score/inc_someip_gateway/issues/84 |
| **Status** | `scoped_fix_verified` |
| **Patch** | `someip-84-verified.patch` |
| **Evidence** | 1046 portable files, 269 candidate sources |
| **Review** | Local scoped user approval recorded |
| **Upstream** | Open, PR body prepared |

### 2. Lifecycle #704 - Communication Config Generation

| Field | Value |
|-------|-------|
| **Repository** | eclipse-score/lifecycle |
| **Issue URL** | https://github.com/eclipse-score/lifecycle/issues/704 |
| **Status** | `implemented_locally` |
| **Patch** | `lifecycle-704.patch` |
| **Evidence** | 113 native test cases pass |
| **Review** | Local owner approval recorded |
| **Upstream** | Open, PR body prepared |

---

## Evidence Missing (Needs Recovery During Hackathon)

### 3. Diagnostics #16 - sovd_adapter

| Field | Value |
|-------|-------|
| **Repository** | eclipse-score/inc_diagnostics |
| **Issue URL** | https://github.com/eclipse-score/inc_diagnostics/issues/16 |
| **Status** | `evidence_missing` |
| **What's Missing** | 5 patch files, baseline commit, test results |

**Expected Patches (from original README):**
```
0001-build-bazel-*.patch     - Fix cargo-bazel lock
0002-build-bazel-*.patch     - Expose tokio/serde
0003-feat-diag_api-*.patch   - Re-export types
0004-feat-sovd_adapter-*.patch - DataProvider implementation
0005-feat-opensovd-gateway-*.patch - Wire into gateway
```

**Hackathon Task:** Recover or recreate these patches with evidence

### 4. Classic Diagnostic Adapter (CDA)

| Field | Value |
|-------|-------|
| **Repository** | eclipse-opensovd/classic-diagnostic-adapter |
| **Issue** | Not identified (possibly #543) |
| **Status** | `no_entry` in registry |
| **What's Missing** | Issue number, patches, validation records |

**Hackathon Task:**
- Identify the correct issue (#543 Result vs Option)
- Create patches
- Add to registry

---

## Campaign Evidence (Already Captured)

| Campaign | Checks | Status |
|----------|--------|--------|
| **Core Final** (f005) | 42/42 | PASSED |
| **CARLA Native Final** (f009) | 46/46 | PASSED |

Evidence location: `evidence/f005-core-final/`, `evidence/f009-carla-native-final/`

---

## OpenSOVD Native Provider (Implemented)

| Component | Location | Status |
|-----------|----------|--------|
| **sdv-receiver-diagnostics** | `OpenSOVD/integration/diagnostics/` | Implemented |
| **Fault catalog** | `OpenSOVD/config/faults/` | Implemented |
| **Receiver patches** | `OpenSOVD/patches/receiver-diagnostics/` | Implemented |
| **Fault storage patches** | `OpenSOVD/patches/fault-storage/` | Implemented |

---

## Hackathon Tasks (What To Do During 2 Days)

### Day 1: Evidence Recovery

| Priority | Task | Target |
|----------|------|--------|
| 1 | Recover Diagnostics #16 patches | `contributions/issues/eclipse-score/inc_diagnostics/16/` |
| 2 | Add CDA #543 to registry | `contributions/issues/eclipse-opensovd/classic-diagnostic-adapter/543/` |
| 3 | Run tests and capture evidence | `evidence/` |

### Day 2: Upstream PRs

| Priority | Task | Target |
|----------|------|--------|
| 1 | Submit SOME/IP #84 PR | Already prepared |
| 2 | Submit Lifecycle #704 PR | Already prepared |
| 3 | Submit Diagnostics #16 PR | After recovery |
| 4 | Submit CDA #543 PR | After implementation |

---

## Registry Status Summary

```json
{
  "issues": [
    { "id": "eclipse-score/inc_someip_gateway#84", "status": "scoped_fix_verified", "submission_candidate": true },
    { "id": "eclipse-score/lifecycle#704", "status": "implemented_locally", "submission_candidate": true },
    { "id": "eclipse-score/inc_diagnostics#16", "status": "evidence_missing", "submission_candidate": false },
    { "id": "eclipse-opensovd/classic-diagnostic-adapter#543", "status": "NOT IN REGISTRY", "submission_candidate": false }
  ]
}
```

---

## What We Declare as Pre-Work

| Category | Items | Status |
|----------|-------|--------|
| **Completed fixes with evidence** | SOME/IP #84, Lifecycle #704 | DONE |
| **Native OpenSOVD provider** | sdv-receiver-diagnostics | DONE |
| **Test campaigns** | Core (42), CARLA (46) | DONE |
| **Documentation & architecture** | docs/, specs/ | DONE |
| **Diagnostics #16 implementation** | Patches | NEEDS RECOVERY |
| **CDA #543 implementation** | Not started | TO DO DURING HACKATHON |

---

## Files to Review

| File | Purpose |
|------|---------|
| `contributions/registry.json` | Issue tracking registry |
| `contributions/README.md` | Contribution overview |
| `contributions/EVIDENCE_GAPS.md` | What needs recovery |
| `docs/reproduction.md` | Setup guide |
| `docs/handover.md` | Handover documentation |
| `docs/claim-evidence.md` | Claim/evidence mapping |

---

*Declaration prepared for Eclipse SDV Hackathon 2026*
*Team repository: eclipse_sdv_hackathon_2026-contributions-eclipse-sdv-hackathon*
