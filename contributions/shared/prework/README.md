# Eclipse SDV Hackathon 2026 - Pre-Work Declaration

## Declaration Statement

This folder contains all **pre-work** completed before the Eclipse SDV Hackathon Chapter 4 (Oct 6-8, 2026).

This directory contains planning and reference documents. It does not establish
that the rest of the repository was developed during the event. Retained
diagnostics patches include commits dated **2026-09-22**, and campaign evidence
exists under `contributions/shared/evidence/runs/20260925T125437Z`, before the October 6 event start.
These are pre-existing implementations and measurements. Event additions must
be identified by their actual revisions and dates; competition eligibility
requires the organizers' published rules and has not been established.

---

## Pre-Work Contents

### 1. Research & Analysis

| File | Description | Purpose |
|------|-------------|---------|
| `research/ISSUE_553_ANALYSIS.md` | Analysis of OpenSOVD API gaps | Understand what needs fixing |
| `research/CDA_543_ANALYSIS.md` | Analysis of CDA bug | Understand the Option vs Result issue |
| `research/SCORE_OPENSOVD_GAP.md` | S-CORE and OpenSOVD integration gap | Understand Epic #1766 |
| `research/XVERSE_ANALYSIS.md` | X-Verse container analysis | Understand Cruise Control team's setup |

### 2. Architecture Design

| File | Description | Purpose |
|------|-------------|---------|
| `architecture/SYSTEM_ARCHITECTURE.md` | Full 7-layer architecture | Overall system design |
| `architecture/XVERSE_INTEGRATION.md` | X-Verse integration architecture | How X-Verse connects |
| `architecture/DATA_FLOW.md` | Data flow from car to dashboard | Signal path documentation |

### 3. Environment Setup

| File | Description | Purpose |
|------|-------------|---------|
| `setup/ENVIRONMENT_SETUP.md` | Full environment setup guide | How to build everything |
| `setup/DOCKER_SETUP.md` | Docker configuration guide | Container setup |
| `setup/TOOL_REQUIREMENTS.md` | Required tools and versions | Prerequisites |

### 4. Implementation Plans

| File | Description | Purpose |
|------|-------------|---------|
| `plans/HACKATHON_2DAY_PLAN.md` | 2-day hackathon schedule | What to do during hackathon |
| `plans/CONTRIBUTION_PLAN.md` | What we plan to contribute | PR/Issue targets |
| `plans/DEMO_PLAN.md` | Demo implementation plan | What demo will show |

### 5. Presentation Materials

| File | Description | Purpose |
|------|-------------|---------|
| `presentation/HACKATHON_PRESENTATION_V5.pptx` | Final presentation slides | Hackathon pitch |
| `presentation/PRESENTATION_SCRIPT.md` | Speaking notes | What to say |

### 6. Reference Documentation

| File | Description | Purpose |
|------|-------------|---------|
| `reference/FILE_REFERENCE_GUIDE.md` | Documentation file index | Find documents quickly |
| `reference/CONTRIBUTION_FILES_REFERENCE.md` | Source file reference | What files we'll modify |
| `reference/GIT_LINKS.md` | All GitHub repository links | Quick access to repos |

---

## What We Will Do DURING Hackathon

| Contribution | Repository | Type | Status |
|--------------|------------|------|--------|
| CDA #543 | eclipse-opensovd/classic-diagnostic-adapter | Bug fix | Pre-existing patch; published PR #601, review/ECA pending |
| Issue #553 | eclipse-opensovd/opensovd-core | API fixes | To be done Day 1 |
| Issue #16 | eclipse-score/inc_diagnostics | New adapter | Pre-existing implementation; published PR #40, review/ECA/DCO pending |
| Demo | Our repository | Integration | To be done Day 2 |

---

## Team Declaration

The previous assertion that no code or patches existed before the event is
superseded by the retained pre-event evidence above. This correction records
provenance; it supplies no organizer eligibility decision. Preserve original
commit/test dates and distinguish later work from the earlier implementation.

---

## Folder Structure

```
PREWORK_DECLARATION/
├── README.md                          # This file
├── research/
│   ├── ISSUE_553_ANALYSIS.md          # OpenSOVD API gap analysis
│   ├── CDA_543_ANALYSIS.md            # CDA bug analysis
│   ├── SCORE_OPENSOVD_GAP.md          # S-CORE integration gap
│   └── XVERSE_ANALYSIS.md             # X-Verse container analysis
├── architecture/
│   ├── SYSTEM_ARCHITECTURE.md         # Full system design
│   ├── XVERSE_INTEGRATION.md          # X-Verse integration
│   └── DATA_FLOW.md                   # Signal flow
├── setup/
│   ├── ENVIRONMENT_SETUP.md           # Build environment
│   ├── DOCKER_SETUP.md                # Docker config
│   └── TOOL_REQUIREMENTS.md           # Prerequisites
├── plans/
│   ├── HACKATHON_2DAY_PLAN.md         # 2-day schedule
│   ├── CONTRIBUTION_PLAN.md           # What we'll contribute
│   └── DEMO_PLAN.md                   # Demo plan
├── presentation/
│   ├── HACKATHON_PRESENTATION_V5.pptx # Slides
│   └── PRESENTATION_SCRIPT.md         # Speaking notes
└── reference/
    ├── FILE_REFERENCE_GUIDE.md        # Doc index
    ├── CONTRIBUTION_FILES_REFERENCE.md # Source file ref
    └── GIT_LINKS.md                   # GitHub links
```

---

*Prepared for Eclipse SDV Hackathon 2026 - Chapter 4*
*Team: [Your Team Name]*
*Date: October 5, 2026*
