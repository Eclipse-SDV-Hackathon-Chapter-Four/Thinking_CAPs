# Eclipse SDV Hackathon 2026 - File Reference Guide

## Quick Reference Table

| # | File Name | Type | Purpose | When to Use |
|---|-----------|------|---------|-------------|
| 1 | HACKATHON_STORY.md | Strategy | Team declaration & scope | Present to coaches |
| 2 | HACKATHON_TECHNICAL_README.md | Technical | Interview preparation | Technical Q&A |
| 3 | HACKATHON_PRESENTATION_V4.pptx | Presentation | Final pitch deck | Hackathon presentation |
| 4 | HACKATHON_USECASE_ARCHITECTURE.md | Architecture | Full system design | Deep dive reference |
| 5 | HACKATHON_COMBINED_ARCHITECTURE.md | Architecture | End-to-end integration | System overview |

---

## Detailed File Descriptions

### 1. Documentation Files

| File | Size | Description | Key Contents | Usage |
|------|------|-------------|--------------|-------|
| **HACKATHON_STORY.md** | 22KB | Team story & scope declaration | Problem statement, solution, 4 contributions, scope boundaries, use case flow | Use when explaining to coaches what you're claiming vs not claiming |
| **HACKATHON_TECHNICAL_README.md** | 65KB | Comprehensive technical documentation | Architecture layers, ISO standards, mw::com patterns, debounce logic, Q&A | Use for interview preparation, technical deep-dives |
| **HACKATHON_USECASE_ARCHITECTURE.md** | 77KB | Full use case architecture | 7-layer stack, data flow, component details, port mappings | Reference for understanding complete system |
| **HACKATHON_COMBINED_ARCHITECTURE.md** | 49KB | Combined PR #488 + Issue #553 + Cruise Control plan | Integration strategy, openDuT testing, demo flow | Understanding how all pieces fit together |
| **HACKATHON_HANDSON_GUIDE.md** | 18KB | Step-by-step hands-on instructions | Build commands, Docker setup, test execution | Actually running the demo |
| **HACKATHON_PRESENTATION_SCRIPT.md** | 16KB | Presentation speaking script | Slide-by-slide talking points | Rehearsing the presentation |

---

### 2. Implementation Plans

| File | Size | Description | Key Contents | Usage |
|------|------|-------------|--------------|-------|
| **Eclipse_SDV_Implementation_Plan.md** | 21KB | Original implementation roadmap | Project phases, milestones, deliverables | Project planning reference |
| **Hackathon_Combined_488_553_CruiseControl_Plan.md** | 39KB | Combined strategy for all contributions | PR #488 gateway, Issue #553 fixes, Cruise Control demo | Understanding integration approach |
| **Hackathon_Issue553_Implementation_Plan.md** | 22KB | Detailed Issue #553 implementation | 8 API fixes, ISO 17978-3 compliance details | Implementing OpenSOVD fixes |
| **ISSUE_553_DETAILED_REPORT.md** | 35KB | Technical analysis of Issue #553 | Code analysis, defects found, fix proposals | Reference for API compliance work |

---

### 3. Presentation Files

| File | Size | Slides | Description | Design |
|------|------|--------|-------------|--------|
| **HACKATHON_PRESENTATION.pptx** | 45KB | 10 | Version 1 - Initial draft | Standard design |
| **HACKATHON_PRESENTATION_V2.pptx** | 43KB | 9 | Version 2 - Black/white theme | Minimalist, no score slide |
| **HACKATHON_PRESENTATION_V3.pptx** | 44KB | 9 | Version 3 - With layer boxes | Black background, stacked layers |
| **HACKATHON_PRESENTATION_V4.pptx** | 46KB | 10 | **FINAL** - Full flow architecture | Complete data flow with arrows |

#### Presentation V4 Slide Contents:

| Slide | Title | Content |
|-------|-------|---------|
| 1 | Title | "Bridging Eclipse SDV for ADAS Diagnostics" |
| 2 | The Problem | S-CORE ✕ OpenSOVD gap, Epic #1766 |
| 3 | Our Solution | Bridge + 4 Contributions |
| 4 | Architecture Flow | **FULL flow diagram with arrows** |
| 5 | Use Case | Speed Signal Loss (6 steps) |
| 6 | Scope Declaration | Our code vs Their code |
| 7 | Technical Highlights | ISO standards, metrics |
| 8 | Live Demo | 60-second demo timeline |
| 9 | Impact | OEMs + Eclipse benefits |
| 10 | Closing | "We bridged the gap. Let's merge it." |

---

### 4. Python Scripts (PowerPoint Generators)

| File | Size | Description | Output |
|------|------|-------------|--------|
| **create_hackathon_ppt.py** | 35KB | Version 1 generator | HACKATHON_PRESENTATION.pptx |
| **create_hackathon_ppt_v2.py** | 28KB | Black/white theme generator | HACKATHON_PRESENTATION_V2.pptx |
| **create_hackathon_ppt_v3.py** | 33KB | Layer boxes architecture | HACKATHON_PRESENTATION_V3.pptx |
| **create_hackathon_ppt_v4.py** | 45KB | **FINAL** - Full flow architecture | HACKATHON_PRESENTATION_V4.pptx |

To regenerate any presentation:
```bash
python3 create_hackathon_ppt_v4.py
```

---

### 5. Subdirectory: sdv-mac-transfer/EclipseHackthon2026/

| Path | Description | Key Contents |
|------|-------------|--------------|
| `docs/architecture.md` | System architecture documentation | Layer definitions, component diagrams |
| `docs/research.md` | Research findings | S-CORE + OpenSOVD analysis |
| `docs/faultsink-design.md` | Fault sink design | DTC handling approach |
| `docs/implementation-plan.md` | Implementation roadmap | Task breakdown |
| `docs/integration-plan.md` | Integration strategy | How components connect |
| `docs/limitations.md` | Known limitations | Scope constraints |
| `docs/hands-on.md` | Hands-on instructions | Demo setup |
| `docs/hackfest/solution-plan.md` | Hackfest solution | Strategy document |
| `docs/hackfest/scorecard-alignment.md` | Scoring alignment | How to maximize points |
| `docs/hackfest/upstream-outreach.md` | Upstream communication | PR/Issue strategy |
| `docs/hackfest/candidate-tasks.md` | Task candidates | What to work on |
| `docs/hackfest/strategy-evaluation.md` | Strategy analysis | Approach evaluation |
| `docs/hackfest/prepared-code-declaration.md` | Pre-prepared code | What was done before hackathon |
| `docs/tasks/cda-543-results-not-options.md` | CDA #543 fix | Bug fix details |
| `demo/opendut/README.md` | openDuT demo setup | Testing configuration |
| `demo/live/server.py` | Live demo server | Python HTTP server |
| `demo/replay/build.py` | Demo replay builder | Recording playback |
| `demo/README.md` | Demo overview | How to run demos |
| `evidence/*/verdict.md` | Test run verdicts | Pass/fail records |
| `evidence/*/FINDINGS.md` | Test findings | Detailed results |
| `STATUS.md` | Project status | Current state |

---

### 6. Subdirectory: sdv-mac-transfer/cruise-control-poc/

| Path | Description | Key Contents |
|------|-------------|--------------|
| `docs/limitations.md` | POC limitations | What's not implemented |
| `contributions/shared/docs/interfaces.md` | Interface definitions | API contracts |
| `docs/design-note-1766.md` | Epic #1766 design | Answering the call |
| `docs/prepared-code-declaration.md` | Pre-prepared code | Declaration for hackathon |
| `docs/PLAN.md` | POC plan | Implementation roadmap |
| `docs/rebuild/GUIDE.md` | Rebuild guide | How to rebuild from scratch |
| `cc-app/README.md` | Cruise Control app | Application docs |
| `gateway/README.md` | Gateway component | mw::com gateway |
| `web/serve.py` | Web server | Dashboard server |
| `stretch/mwcom-bridge/README.md` | mw::com bridge | Bridge implementation |
| `third_party/inc_diagnostics/` | S-CORE diagnostics fork | PR #16 code |
| `contributions/shared/evidence/runs/*/verdict.md` | Test verdicts | Test results |

---

### 7. Subdirectory: sdv-mac-transfer/forks/opensovd-core/

| Path | Description | Key Contents |
|------|-------------|--------------|
| `README.md` | OpenSOVD core | Main documentation |
| `CONTRIBUTING.md` | Contribution guide | How to contribute |
| `docs/architecture.md` | Architecture | System design |
| `docs/testing.md` | Testing guide | How to test |
| `docs/development.md` | Development guide | Setup instructions |
| `docs/ci.md` | CI/CD docs | Pipeline info |
| `opensovd-server/README.md` | Server component | SOVD gateway server |
| `opensovd-cli/gateway/README.md` | CLI gateway | Command-line tools |
| `opensovd-mocks/README.md` | Mock components | Test mocks |
| `tests/*.py` | Test files | Python tests |
| `examples/server/simple/README.md` | Simple example | Getting started |

---

## File Usage by Scenario

### Scenario 1: Presenting to Hackathon Coaches

| Order | File | Purpose |
|-------|------|---------|
| 1 | HACKATHON_PRESENTATION_V4.pptx | Visual presentation |
| 2 | HACKATHON_STORY.md | Scope declaration |
| 3 | HACKATHON_PRESENTATION_SCRIPT.md | Speaking notes |

### Scenario 2: Technical Interview Preparation

| Order | File | Purpose |
|-------|------|---------|
| 1 | HACKATHON_TECHNICAL_README.md | All technical details |
| 2 | HACKATHON_USECASE_ARCHITECTURE.md | Architecture deep-dive |
| 3 | ISSUE_553_DETAILED_REPORT.md | API fix specifics |

### Scenario 3: Running the Demo

| Order | File | Purpose |
|-------|------|---------|
| 1 | HACKATHON_HANDSON_GUIDE.md | Setup instructions |
| 2 | demo/live/server.py | Start the server |
| 3 | contributions/shared/evidence/runs/*/verdict.md | Verify results |

### Scenario 4: Understanding the Integration

| Order | File | Purpose |
|-------|------|---------|
| 1 | HACKATHON_COMBINED_ARCHITECTURE.md | Full integration view |
| 2 | Hackathon_Combined_488_553_CruiseControl_Plan.md | Strategy |
| 3 | docs/architecture.md | Technical details |

---

## Key Contributions Summary

| Contribution | Repository | File Reference |
|--------------|------------|----------------|
| **PR #16** (sovd_adapter) | eclipse-score/inc_diagnostics | third_party/inc_diagnostics/ |
| **Issue #553** (8 API fixes) | eclipse-opensovd/opensovd-core | forks/opensovd-core/ |
| **CDA #543** (Bug fix) | eclipse-opensovd/classic-diagnostic-adapter | docs/tasks/cda-543-results-not-options.md |
| **Demo** (Cruise Control) | Our repository | demo/, cc-app/, gateway/ |

---

## Quick Commands

```bash
# Generate latest presentation
python3 create_hackathon_ppt_v4.py

# Open presentation
open HACKATHON_PRESENTATION_V4.pptx

# View all documentation files
ls -la *.md

# Check file sizes
du -sh *.md *.pptx
```

---

*Document prepared for Eclipse SDV Hackathon 2026*
