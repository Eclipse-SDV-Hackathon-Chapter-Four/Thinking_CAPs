# F012 — AutoSD vehicle computer and zonal lighting

Status: implemented and runtime-verified; prepared work on 4 October 2026.
User request: deploy the recommended AutoSD lighting workload and document how to
replicate it. Existing ThreadX implementation is the input asset.

## Scope and requirements

| ID | Required behavior | Acceptance |
| --- | --- | --- |
| ASD001 | Boot actual pinned AutoSD in an owned QEMU/KVM guest | Download/expanded image hashes, guest OS/kernel identity, UEFI boot |
| ASD002 | Run real ThreadX Linux simulation and unchanged pinned Zenoh2CAN | Container/binary identity, FIFO prerequisite check, actual SocketCAN |
| ASD003 | Preserve the Zephyr BCM lighting contract | All 256 status bytes, malformed frames, eight-byte 0x1F4 outputs |
| ASD004 | Connect host vehicle services over Zenoh | Four light states and individual VCU boolean topic |
| ASD005 | Measure actual CARLA actuation | Existing controller/subscribers, actual masks 64/8/72/0, owned actor cleanup |
| ASD006 | Expose separate native OpenSOVD lighting identity | Discovered autosd-host/zonal-lighting App and actual process observations |
| ASD007 | Preserve unknown/unavailable and bounded fault history | Observation expiry, controller stop/restart, optional CAN timeout/recovery |
| ASD008 | Attach actual guest Ethernet to openDuT's managed path | Guest routing/ping, owned TAP relay, matched real CARL/EDGAR/CLEO, GRE capture |
| ASD009 | Disturb and recover the actual managed transport | GRE interruption holds lights while management diagnostics remain reachable; recovery |
| ASD010 | Reboot and restore the deployment | CAN endpoints and transient Podman image reload, active services and recovered commands |
| ASD011 | Remove only owned runtime resources | Actor removal, guest shutdown, relay/TAP cleanup, bench teardown; unrelated resources preserved |
| ASD012 | Provide reproducible environment-independent instructions | Fresh guest overlay, new native Cargo target, separate pinned bridge clone, corrected README |

## Explicit contracts

ThreadX uses avcan0; gateway uses the opposite vxcan endpoint avcan1. Standard
0x1F1/0x1F4 IDs and bit positions are the existing ThreadX/Zephyr contract. Host
CAN interfaces are unrelated. Default timeout is disabled for change-driven VCU
publishing; periodic sources may select a positive timeout. Restarts start OFF.
The bridge deduplicates unchanged inputs; recovery tests reissue current state.

The OpenSOVD lighting provider reads the actual ThreadX process's JSON records,
with guest boot ID and CLOCK_MONOTONIC freshness. Fault history is an explicitly
labelled integration-owned journal; no native DFM or embedded hardware claim is
made. HTTP reads do not participate in ThreadX's control loop.

Managed lighting traffic uses the second guest NIC and actual openDuT GRE path.
Management SSH/diagnostics stay independent. Fixture VCU commands, CARLA actor
actuation, and native diagnostics are distinct evidence sources. The existing
Cruise Control dashboard/Test Manager and its DFM campaign remain separate.

## Verification

[AutoSD artifacts](../../artifacts/README.md) map the requirements to the final
fresh-guest tests, identity/deployment receipts, actual CARLA observations, GRE
traffic, reboot and cleanup. Local reproduction is an implementation-agent
self-run; it is not second-person signoff, production qualification or a judging
result. No paid provider calls, outreach, upstream PR or software update is part
of this slice.
