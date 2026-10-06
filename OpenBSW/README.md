# OpenBSW zonal diagnostic gateway

This folder holds the Thinking CAPs **zonal diagnostic gateway**, built on
[Eclipse OpenBSW](https://github.com/eclipse-openbsw/openbsw). It is the
"New Physical ECU Integration" extension from the [repository README](../README.md#new-physical-ecu-integration).

The gateway is a single diagnostic entry point for the zonal ECUs on the
X-Verse CAN bus:

- It receives UDS requests over **DoIP** (ISO 13400-2) from the OpenSOVD
  Classic Diagnostic Adapter (CDA).
- It reads each request's target logical address and routes it:
  - to its own UDS server,
  - over **ISO-TP** (ISO 15765-2) to one CAN ECU, such as the ThreadX rear lighting controller,
  - or to all of them (functional addressing).

```text
SOVD client ─REST─► OpenSOVD ─► CDA ─DoIP─► OpenBSW gateway ─ISO-TP / vcan0─► ThreadX rear lighting (0x1020)
                                              └─► own UDS server (0x1010)   └─► future zonal ECUs (0x1030…)
```

It does not touch the cruise-control use case:

- Cruise diagnostics stay on the S-CORE `sovd_adapter` path (Path A in [demo/README.md](../demo/README.md)).
- The gateway uses only the diagnostic CAN identifiers `0x7DF` and `0x7E1`–`0x7EF`.
- It never joins Zenoh or SOME/IP.

## Status

| Work product | State |
| --- | --- |
| SWE.1 [system](aspice/swe1-requirements/system-requirements.md) and [software](aspice/swe1-requirements/software-requirements.md) requirements | Draft for review, 6 October 2026 |
| SWE.2 [architecture](aspice/swe2-architecture/architecture.md) with PlantUML [views](aspice/swe2-architecture/diagrams/) | Draft for review, 6 October 2026 |
| SWE.3–SWE.6, implementation, tests | Not started |

## Layout

| Path | Content |
| --- | --- |
| `aspice/` | ASPICE SWE work products, in the same layout as [Serial2CAN](../X-Verse/bridges/serial2can/aspice/README.md) and [AZ3166](../ThreadX/az3166/aspice/README.md) |
| `src/`, `config/`, `tests/` | Planned: gateway application, routing table, tests |

## Virtual environment (SIL)

The gateway runs without hardware on the OpenBSW POSIX platform:

- **CAN:** SocketCAN on `vcan0`
- **Ethernet:** lwIP on a TAP device `tap0`. The host is `192.168.0.10`; the ECU is `192.168.0.201`.
- **RTOS:** FreeRTOS POSIX simulation. The `posix-threadx` preset is the ThreadX alternative.

The source, toolchain venv, pip cache, compiler temporaries and build tree all
live on the external ext4 build volume (UUID `11c42dee-…`). This volume is the
loop device over `/media/jefferson/Lexar/.s-core-build/build-volume-v1.ext4`.
The scripts refuse to run when the volume is not mounted, and refuse any path
on the internal root filesystem.

```bash
# once per boot, if the volume is not mounted (loop device + udisks)
udisksctl loop-setup -f /media/jefferson/Lexar/.s-core-build/build-volume-v1.ext4
udisksctl mount -b /dev/loopN           # mounts at /media/jefferson/11c42dee-…

sudo OpenBSW/scripts/net-up.sh          # vcan0 + tap0 (reuses existing ones)
OpenBSW/scripts/bootstrap.sh            # venv, pinned OpenBSW, posix-freertos build
OpenBSW/scripts/run.sh                  # start the POSIX app; Ctrl-C stops it
OpenBSW/scripts/sil-test.sh             # OpenBSW's own SIL suite (uds, enet, docan)
```

**Baseline result (6 October 2026):** OpenBSW `432b9be6`, `posix-freertos`,
104 of 104 tests pass. The suite covers UDS over CAN (`0x7E0`/`0x7E8`) and
over DoIP (`192.168.0.201:13400`), Ethernet, and DoCAN. Evidence and manifest
are in [evidence/sil-baseline](evidence/sil-baseline/).

Findings for the gateway work:

- **The test suite is not safe on a shared `vcan0`.** It transmits on
  `0x7DF`, `0x7E0`/`0x7E1`, `0x600`/`0x601`, `0x558` and 29-bit `0x18DAxxxx`
  ([can-ids.txt](evidence/sil-baseline/can-ids.txt)). Run it only while
  X-Verse is stopped.
- **The CAN interface is hard-coded.** The POSIX platform uses `"vcan0"` in
  `CanSystem.cpp`. SWR-050 (selectable interface) therefore needs a
  gateway-owned platform `CanSystem`, rather than a patch to OpenBSW (SWR-053).

The unmodified reference application sends on CAN `0x558` (a demo frame)
and serves UDS on `0x7E0`/`0x7E8`. Neither collides with X-Verse, which uses
`0x1F0`–`0x1F4` and `0x300`. The gateway will replace the demo traffic with
the routing table's identifiers only (SWR-030).

The OpenBSW revision, the volume and the SIL addresses are pinned in
[dependencies.lock.json](dependencies.lock.json); the host tools are in
[requirements-build.txt](requirements-build.txt). The host CMake 3.22 is too
old for OpenBSW, which needs 3.28 or later, so the venv provides CMake 4.4.

## Dependencies on other items

- **ThreadX rear lighting ECU:** it needs a minimal UDS-on-CAN server (`0x7E1`/`0x7E9`) before end-to-end routing can be shown. That is a separate change to [ThreadX](../ThreadX/README.md).
- **CDA diagnostic description (MDD):** it must declare the gateway and every routed ECU with the logical addresses in the routing table. The CDA rejects anything not in the MDD ([demo/README.md](../demo/README.md)).
- **AZ3166 on hardware:** it needs a new Serial2CAN profile that adds `0x7E1` to `to_serial` and `0x7E9` to `from_serial`. The existing profiles stay unchanged.
