# README reproduction audit — external SSD

This is the first audit from 4 October 2026. Its failed attempts are historical;
see the [clean replay report](readme-clean-replay.md) for subsequent corrections
and verification. At this audit's original end, the unpublished branch, Android
startup and early cancellation prevented a complete reproduction claim.

## Test environment and limits

The test workspace is:

```text
/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/autoverse-readme-h1di7u9m
```

This is an ext4 image backed by `/media/jefferson/Lexar/.s-core-build/build-volume-v1.ext4` on the external Lexar SSD. The existing filesystem was used without formatting. Sources, Python environments, downloaded CARLA, native build outputs, Bazel cache, testbench state, dashboard state and evidence reside there.

Ubuntu 22.04, system Python 3.10, Docker, the NVIDIA GPU/driver and the selected Rust toolchain were shared with the reference host. The selected LLVM repository and cached Cargo dependencies were reused explicitly. Fresh native runtime/build images were built from the SSD sources; Docker still uses the shared daemon. This is an agent-operated reproduction on the same machine, **not independent-person signoff or an installation on an empty host**.

A filesystem namespace mapped the SSD home over `/home/jefferson` for home-relative installation recipes, leaving the original home read-only. Component Docker names, the Bazel volume and dashboard port were isolated. The baseline supervisor has fixed names and process cleanup patterns, so its complete command was not launched concurrently against the existing workspace. The managed profile also has fixed subnets and Zenoh port 7447; only one such bench can run on this host at a time.

Docker recipes also use temporary host `/tmp` mounts for runtime sockets and generated overlays. These were not a separate host installation; persisted build and campaign evidence was saved on the SSD.

## Instructions exercised

| README step | What was actually exercised | Result |
| --- | --- | --- |
| Host tools | Python, Docker/Compose, KVM, GPU, Git LFS and `just check-host` | Passed using already installed host tools; system package installation was not repeated |
| Autoverse checkout | Remote branch `dev/sdv-hackathon-2026`, revision `7dccc623`; `vcs import` of all 11 component repositories | Passed |
| Companion checkout | Literal remote clone of `contributions/eclipse-sdv-hackathon` | Failed: remote branch does not exist |
| Continuation after checkout failure | Independent local clone plus preserved unpublished working-tree snapshot, committed only in the SSD checkout | Used to test subsequent instructions; does not establish public reproducibility |
| Python setup | Fresh vehicle environment and dedicated integration `.venv`, core and CARLA requirements, client imports | Passed |
| CARLA installation | `just install-server` with its original download URL | Failed: redirected CDN returned HTTP 403 |
| Corrected CARLA installation | Download from the official 0.9.15 release link, recipe MD5 check, extraction with `just install-server` | Passed; physical campaign uses this new server |
| Zenoh | Independent router, actual subscriber and publisher | Passed: 10 `Hello Autoverse` messages |
| SOME/IP bridge | Git LFS retrieval; new Docker image; container creation, start and stop | Passed |
| Bridge development tests | `ctest --test-dir build` inside the new image | Failed: `mapping_flow` has 13 failed assertions out of 60; `payload_convert` passed |
| S-CORE/native assets | New runtime and development Docker images; fresh native source reproduction in SSD Bazel/Rust outputs | Passed controller build/unit tests, diagnostic build, 12 fault-storage tests and Clippy |
| Baseline-to-campaign transition | First native core campaign while standalone router still listened on all interfaces | Failed: campaign could not bind `172.30.77.1:7447` |
| Corrected transition/core | Stop the separately launched router; repeat native reproduction with fresh native images | Passed: 42 native checks |
| Core regression after assertion fix | CLI campaign with the new timestamp assertion and existing fresh native binaries | Passed: 42 native checks, eight selected scenario verdicts; ten conditional/deferred scenarios skipped |
| Cuttlefish preparation | Fresh `ctl.sh make`, actual Android download/extraction, owned container first start | Preparation passed; start failed during APK install |
| Android readiness | HTTPS, ADB connection/wait, guest logs, APK verification | HTTPS returned 200, but guest remained in U-Boot and ADB was unavailable; Android/APK acceptance failed |
| Complete baseline command | `python3 run_autoverse.py --enable-camera-display --vcu-zenoh` | Blocked by mandatory Android readiness; not claimed as a successful full baseline reproduction |
| Launcher unit tests | Launcher suite | Passed: 9 tests |
| Integration unit tests | Dedicated integration environment, including new stream-loss regressions | Passed: 36 tests |
| Standalone native provider smoke | README command using the newly built binary and explicit fixture observations | Passed: eight diagnosis adapter checks, including outage invalidation and recovery |
| openDuT bench | Release preparation, TLS enrollment, real CARL and two Connected EDGAR peers, GRE and `dut0` attachments | Passed |
| Dashboard/physical campaign | Real Chromium controls, reload during active run, live native diagnosis, direct OpenSOVD discovery, real CARLA and VCU | Passed physical campaign: 46 native checks and 66 sampled controller-to-VCU-to-actor correlation matches |
| Report downloads | Browser report links and actual HTTP downloads | Passed: four verified artifacts |
| Deliberate-failure campaign | Launch through browser, inspect final verdict and restoration | Passed |
| Cancellation during startup | Launch core through browser and cancel while only two applications had started | Cancellation recorded; cleanup stayed `unknown` and retained the active-run reservation |

The steering-wheel setup was not exercised without an attached wheel. The alternative `setup.sh` automation was inspected rather than executed because it changes host packages and shell configuration. Camera/manual-driving operation and a booted Android cluster remain unverified in this reproduction. The current diagnostic campaign intentionally does not require Cuttlefish.

## Corrections made

- Added a branch-publication checkpoint instead of assuming a remote implementation exists.
- Added a dedicated integration Python environment and carried its interpreter through dashboard and campaign commands.
- Documented SSD paths, Linux filesystem requirements, shared assets, fixed subnet/port limits and reference-host configuration reuse.
- Replaced the failing CARLA download path in the installation walkthrough with the [official CARLA 0.9.15 release](https://github.com/carla-simulator/carla/releases/tag/0.9.15) download. The 8,386,636,048-byte archive matched MD5 `32fa681fb925cd62951a63977582ea8c`.
- Added the missing standalone-router stop/restart at the transition between baseline and managed campaign.
- Required Android boot completion and APK installation success before declaring the full baseline ready.
- Documented intermittent receiver startup failure and unresolved early-cancellation cleanup.
- Corrected the physical network-loss assertion in `OpenDut/tests/opendut_receiver_smoke.py`. A moving vehicle can produce a final accepted sample between the earlier diagnostic HTTP snapshot and link shutdown. The assertion now requires a reachable, stale receiver whose acceptance timestamp stops within the declared 100 ms scheduling allowance after shutdown. Detector timing uses the final accepted sample. Five regression tests reject continued acceptance, fresh state and missing observations while allowing bounded in-flight delivery. No vehicle, bridge or fault-monitor behavior was changed.

## Preserved attempts and evidence

All fresh audit records are under the SSD workspace's `evidence/`; dashboard campaign artifacts are under `lab/dashboard-state/runs/`. Imported historical contribution evidence inside the companion repository is separate and was not used as proof of this reproduction.

| Attempt | Identity / evidence | Outcome |
| --- | --- | --- |
| Initial native reproduction | `evidence/native-reproduction/` | Build/tests passed, core failed due router conflict |
| Fresh-image native reproduction | `evidence/native-reproduction-second/` | Passed; binary SHA-256 `b70777577e4bc14c7c3d682ed4ba39dc06db6c5b4a199c9d8fcf823a4688ff80` |
| Core regression after assertion fix | `evidence/core-regression-final/` | Passed all 42 native checks |
| First physical run | `a2935c5556ec4368813a16f1a3a77d31` | Real actuation correlation passed; speed-equality assertion raced against link shutdown |
| Second physical run | `0dde5d77e02d46c7801b6eca7bd4701d` | Failed `receiver-through-opendut`; diagnostic observation remained unknown. Root cause remains unresolved |
| Corrected physical run | `f722ee3b0d614cb09c0a6038d1165473` | Passed all 46 native checks; 66 actuation matches |
| Browser deliberate-failure run | `d6cef143e3af4214a5a335cf93753fee` | Passed restoration acceptance |
| Browser early-cancellation run | `d884ab7544344b94b4d06b091d2903b9` | Cancelled; two app cleanup records passed, but the dashboard requires three and retains unresolved state |
| Browser observations/downloads | `evidence/ui-walkthrough-final/` | 21 checks passed through physical run and deliberate cleanup; helper then clicked before the browser had re-enabled Start |
| Separate cancellation walk | `evidence/ui-cancellation/` | Explicitly waited for Start; reproduced the early-cancellation cleanup blocker |

The browser-helper timing mistake was corrected in the separate cancellation walk. It is not counted as a dashboard defect. Earlier failures were retained rather than overwritten by later passing runs.

The integration's initial SSD snapshot was `5bc65740d575aaf95e0c2e05b9b69a3bd0f68b92`; the assertion-fix snapshot is `3177ee9`. Neither local snapshot was pushed. Native builds used S-CORE `93f8ea1e6f76714496c092902e00c9b91c58cdc8` and bridge `0d53a2af8b37121e54d742c6cefd0297dd9e4b92`.

Fresh Docker image identities:

| Asset | Immutable identity |
| --- | --- |
| Bridge | `sha256:8731a7a1f40df00a9bf62535ee5dd540fbc652a61bd6e7272dcac5bd09e7d84a` |
| S-CORE runtime | `sha256:33d36976f9472703c9a120e7662d463e1b906113f28b0da3eb0d7a8603d53ad3` |
| S-CORE development | `sha256:0b8864e83100a25879b0e2ed78f0a3d2f4ecbbd5430cfddc9ba82d5dd730c15b` |

These IDs describe assets built during this audit, not downloadable registry tags. The SSD source trees, logs, failed and passing run artifacts and native build outputs are retained for inspection.

Final teardown stopped the audit dashboard, undeployed and removed the owned bench, and removed the audit's stopped bridge and Cuttlefish containers. No containers with the bench's ownership label remained; dashboard port 8792 and CARLA ports 2100–2102 were closed. `evidence/cleanup.json` records these checks. The cancelled run's unresolved dashboard ledger remains preserved; teardown does not rewrite its historical cleanup verdict. `evidence/summary.json` records the final measured results and document hashes. All 47 README Bash blocks and four embedded Python blocks passed syntax checks.

## Remaining work before a complete reproduction claim

The list below records the original audit's outstanding work. Subsequent work
is recorded in the clean replay report. To make room for the final replay, the
first audit's disposable CARLA installation and installer were removed; its
sources, builds, logs and failed/passing evidence remain preserved.

Publish the implementation and documentation revisions; diagnose fresh Android boot/APK failure; correct or explain the bridge mapping tests; resolve intermittent receiver startup; and make early-cancellation cleanup account for resources actually created. Repeat the affected steps afterward. A new engineer on another machine still needs a verified cold toolchain/cache setup and independent signoff.
