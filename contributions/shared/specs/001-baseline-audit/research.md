# F001 research

## Destination and tooling
Decision: existing hackathon repository and installed Spec Kit 0.14.0 Codex skills.
Rationale: selected through session context; no existing setup to overwrite.
Alternatives: another repo or upgraded toolchain would fragment evidence and pins.

## Actual executable context
Decision: inspect S-CORE binaries using the existing Docker image plus source/cache mounts.
Rationale: bazel-bin points into /var/cache/bazel; missing host resolution is not a missing build.
Observed cruise binary SHA-256: 555c319bc5ae7d9af03531bb9768169b49a1f374d26ec0ab1602619dec1eda48.
Alternative: rebuilding first would lose the untouched executable baseline.

## Receiver boundary
Decision: observe actual accepted input events and actual controller state, not Zenoh publisher state.
Rationale: current consumer handlers decode raw native values; state is private and needs minimal
instrumentation. Existing aggregate last_input_time_ cannot attribute a speed-only interruption.
Alternative: log scraping is limited and does not provide per-event freshness.

## Runtime and networking
Decision: bounded read-only preflight before starting any supervisor.
Rationale: run_autoverse.py deliberately kills stale processes; existing Docker containers are stopped.
Current host network/shared /tmp path does not establish openDuT Ethernet transport.
Alternative: treating container presence or ping as function acceptance is incorrect.
See OpenDut/docs/opendut-deployment-research.md and docs/upstream-status.md for source audit.

## AAOS
Decision: defer F006. User will bring FOTA asset later; emulator/APK install is not OTA.
Rationale: explicit user steering supersedes brief's update scheduling.
