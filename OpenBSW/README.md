# OpenBSW zonal diagnostic gateway

This folder holds the Thinking CAPs **zonal diagnostic gateway**, built on
[Eclipse OpenBSW](https://github.com/eclipse-openbsw/openbsw). It is the
"New Physical ECU Integration" extension from the [repository README](../README.md#new-physical-ecu-integration).

The gateway is a single diagnostic entry point for the zonal ECUs, on the
X-Verse CAN bus and on Ethernet:

- It receives UDS requests over **DoIP** (ISO 13400-2) from the OpenSOVD
  Classic Diagnostic Adapter (CDA).
- It reads each request's target logical address and routes it:
  - to its own UDS server,
  - over **ISO-TP** (ISO 15765-2) to one CAN ECU, such as the ThreadX rear lighting controller,
  - over **DoIP** to one Ethernet ECU, with the gateway as DoIP client (external test equipment),
  - or to all of them (functional addressing).

```text
SOVD client ─REST─► OpenSOVD ─► CDA ─DoIP─► OpenBSW gateway ─ISO-TP / vcan0─► ThreadX rear lighting (0x1020)
                                              │                             └─► future zonal ECUs (0x1030…)
                                              ├─DoIP client─► Ethernet zonal ECU (0x1040, 192.168.0.30)
                                              └─► own UDS server (0x1010)
```

It does not touch the cruise-control use case:

- Cruise diagnostics stay on the S-CORE `sovd_adapter` path (Path A in [demo/README.md](../demo/README.md)).
- The gateway uses only the diagnostic CAN identifiers `0x7DF` and `0x7E1`–`0x7EF`.
- It never joins Zenoh or SOME/IP.

## Status

The gateway runs on the OpenBSW POSIX platform with DoIP over TAP and DoCAN on
`vcan0`, and on the NXP S32K148EVB with Eclipse ThreadX. It routes through
`transport::TransportRouter`, a new OpenBSW module prepared as an
[upstream contribution](../contributions/openbsw-transport-router/README.md),
and reaches Ethernet ECUs through `doip::DoIpClientTransportLayer`, a second
new module (see [DoIP routes](#doip-routes-ethernet-zonal-ecus)).

| Item | Result |
| --- | --- |
| Unit tests | 122/122: 46 `transportRouter` and 20 `doipClient` (OpenBSW unit-test build; the router also in Bazel), 19 gateway units, 37 generator |
| Module coverage | `transportRouter` 100% lines, 99.1% branches; `doipClient` 94.6% lines |
| Integration tests | 44/44 on the Linux host against simulated CAN ECUs and a simulated Ethernet ECU ([evidence/gateway-it](evidence/gateway-it/results.json)); 16/16 on the S32K148EVB, 6 of them over DoIP to the Ethernet ECU ([evidence/board-gateway-it](evidence/board-gateway-it/results.json)) |
| CAN bus load (SWR-032) | The gateway paces its own frames (≥ 3 ms apart): worst case 9.0 % of 500 kbit/s, measured peak 7.9 % |
| Upstream gates for the modules | `transportRouter`: format, copyright, clang-tidy, Bazel pass. `doipClient` on current upstream `main`: format, copyright, unit tests, clang-tidy, Bazel, docs build and gitlint pass ([packet](../contributions/openbsw-doip-client/README.md)) |
| ASPICE SWE.1–SWE.6 | [report](aspice/report/aspice-swe-report.html): 33/39 requirements verified; 6 partially, waiting only for the live qualification campaigns QTC-12 and QTC-13 |

Open items, all of them visible in the report:

- **Live campaigns not run** (QTC-12, QTC-13):
  - X-Verse + CARLA cruise-control regression with the gateway
  - OpenSOVD → CDA → gateway (needs an MDD for the gateway and its nodes)
- The ThreadX rear lighting ECU answers through the gateway since its UDS-on-CAN
  server (branch `feature/threadx-uds-server`): QTC-14 passed 5/5
  ([evidence/qtc14-threadx](evidence/qtc14-threadx/results.json)).
- CAN routing on the board needs a CAN peer (e.g. a USB-CAN adapter); routing
  on the board is verified over DoIP instead.

## Layout

| Path | Content |
| --- | --- |
| `gateway/app/` | Gateway application, derived from the OpenBSW reference app: DoIP, DoCAN, UDS, lifecycle, POSIX platform |
| `gateway/lib/` | Gateway units: CAN routing table, node monitor, identity; unit tests |
| `gateway/config/routing.yaml`, `gateway/tools/` | Single source of the addressing and its generator (`gen_routing.py`, with tests) |
| `gateway/tests/` | Integration tests: simulated CAN ECUs (`sim_ecu.py`), simulated Ethernet ECU (`sim_doip_ecu.py`), DoIP tester, routing, DoIP routing, lifecycle and board tests |
| `contrib/libs/bsw/transportRouter/` | The contributed OpenBSW router module (same tree as upstream) |
| `contrib/libs/bsw/doipClient/` | The contributed OpenBSW DoIP client module (same tree as upstream) |
| `scripts/` | Volume, network, bootstrap, SIL suite, integration run, upstream PR preparation |
| `evidence/` | OpenBSW SIL baseline and gateway integration runs |
| `aspice/` | ASPICE SWE.1–SWE.6 work products and report generator, in the same layout as [Serial2CAN](../X-Verse/bridges/serial2can/aspice/README.md) and [AZ3166](../ThreadX/az3166/aspice/README.md) |

## Virtual environment (SIL)

The gateway runs without hardware on the OpenBSW POSIX platform:

- **CAN:** SocketCAN on `vcan0`
- **Ethernet:** lwIP on a TAP device `tap0`. The host is `192.168.0.10`; the ECU is `192.168.0.201`.
- **RTOS:** FreeRTOS (POSIX port). The board runs ThreadX. On the PC, OpenBSW's SocketCAN transceiver can deadlock the ThreadX Linux port under heavy host load (see below), so `ZGW_RTOS=THREADX` is available but not the default.

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
OpenBSW/scripts/gateway-it.sh           # build the gateway, run the 28 integration tests, record evidence
OpenBSW/scripts/openbsw-pr.sh all       # upstream gates and patch for the transportRouter contribution
python3 OpenBSW/aspice/tools/generate_report.py   # ASPICE SWE report
```

Run the gateway by hand with
`ZGW_CAN_INTERFACE=vcan0 ZGW_TAP_INTERFACE=tap0 <build>/app/application/openbsw-zonal-gw.elf`.
It answers DoIP at `192.168.0.201` as logical address `0x1010`.

**Baseline result (6 October 2026):** OpenBSW `432b9be6`, `posix-freertos`,
104 of 104 tests pass. The suite covers UDS over CAN (`0x7E0`/`0x7E8`) and
over DoIP (`192.168.0.201:13400`), Ethernet, and DoCAN. Evidence and manifest
are in [evidence/sil-baseline](evidence/sil-baseline/). A `posix-threadx` run
(7 October) also passed 104/104 and sent on the same CAN IDs
([threadx/](evidence/sil-baseline/threadx/)); `sil-test.sh` takes
`ZGW_RTOS=THREADX` to repeat it.

**ThreadX on the PC can deadlock (OP-8).** OpenBSW's POSIX
`SocketCanTransceiver` blocks every signal while it runs, and calls into the
CAN stack, and so into the RTOS, from inside that region. The ThreadX Linux
port suspends and resumes its threads with signals. At a host load above
about 40, the gateway built with ThreadX stopped in 2 of 4 runs: the CAN
thread waited in `_tx_thread_interrupt_control` with its signals blocked.
The FreeRTOS build passed 17 runs in a row at a load of 70 to 130. The
POSIX simulation therefore stays on FreeRTOS; the board runs ThreadX.

Findings for the gateway work:

- **The test suite is not safe on a shared `vcan0`.** It transmits on
  `0x7DF`, `0x7E0`/`0x7E1`, `0x600`/`0x601`, `0x558` and 29-bit `0x18DAxxxx`
  ([can-ids.txt](evidence/sil-baseline/can-ids.txt)). Run it only while
  X-Verse is stopped.
- **The CAN interface is hard-coded.** The POSIX platform uses `"vcan0"` in
  `CanSystem.cpp`. The gateway's own platform `CanSystem` reads
  `ZGW_CAN_INTERFACE` instead, so OpenBSW stays unmodified (SWR-050, SWR-053).

The unmodified reference application sends on CAN `0x558` (a demo frame)
and serves UDS on `0x7E0`/`0x7E8`. Neither collides with X-Verse, which uses
`0x1F0`–`0x1F4` and `0x300`. The gateway sends only on `0x7DF`, `0x7E1` and
`0x7E2`, and accepts only `0x7E9`/`0x7EA` (SWR-030, verified in SWE.5).

The OpenBSW revision, the volume and the SIL addresses are pinned in
[dependencies.lock.json](dependencies.lock.json); the host tools are in
[requirements-build.txt](requirements-build.txt). The host CMake 3.22 is too
old for OpenBSW, which needs 3.28 or later, so the venv provides CMake 4.4.

## DoIP routes (Ethernet zonal ECUs)

A route with `transport: doip` in `routing.yaml` reaches an Ethernet ECU
through the gateway's DoIP client, `doip::DoIpClientTransportLayer`. It is a
new OpenBSW module in `contrib/libs/bsw/doipClient`, because OpenBSW has only
the DoIP server side. It reuses OpenBSW's `DoIpTcpConnection` and send jobs
and plugs into `TransportRouter` on its own bus (`DOIP_NODES`), next to DoCAN:

- The first request to the route opens a TCP connection to the node
  (port 13400) and activates routing with source `0x0E10`, type `0x00`. The
  connection stays open for later requests.
- A request counts as delivered when the node acknowledges it (`0x8002`). A
  NACK, a refused connection or activation, or no acknowledgement within
  1.5 s fails the request at once. The route is freed and the node monitor
  counts the failure (three in a row set the route's DTC, `U0142` for
  `0x1040`).
- Functional requests also go to every DoIP node with active routing.
- The node's alive checks are answered.

The test ECU is `gateway/tests/sim_doip_ecu.py`: a DoIP entity `0x1040` with a
UDS server and switchable failures. It listens on `192.168.0.30`, which
`net-up.sh` adds to the host's `lo`. The host answers ARP for it on `tap0`
and on the board link, so the PC gateway and the S32K148EVB both reach it.
On the board this gives a routed path end to end, without a CAN adapter.

`scripts/doip-client-test.sh` builds the module's unit tests in the pinned
OpenBSW tree (the `tests-posix-debug` preset), applies OpenBSW's format, and
runs gcovr and clang-tidy. With `all` (and `OBSW_BASE` set to upstream `main`)
it also runs the copyright check, Bazel and gitlint, and writes the patch of
the [prepared upstream contribution](../contributions/openbsw-doip-client/README.md).

**OpenBSW finding:** in `DoIpTcpConnection` at `432b9be6`, answering
`headerReceived()` with the discard continuation for a message with an empty
payload (such as an alive check request) leaves the connection unable to read
further messages. The client ends such messages with `endReceiveMessage()`
instead. This is to be reported upstream (OP-7 in SWE.1).

## NXP S32K148EVB board

The S32K148EVB is flashed and debugged over its OpenSDA USB port. It talks
DoIP over its 100BASE-T1 Ethernet (TJA1101) to the host through a media
converter. These tools live on the build volume:

- **GDB server:** PEmicro 10.02 from the `com.pemicro.debug.gdbjtag.pne`
  update site, needing the OpenSDA Linux driver (`pemicro-other-20181128`: udev
  rule `58-pemicro.rules` and `libp64`).
- **Compiler:** Arm GNU Toolchain 14.3.rel1, with the SHA-256 pinned by the
  OpenBSW Dockerfile.

```bash
OpenBSW/scripts/board.sh status                 # debugger, GDB server, console port
OpenBSW/scripts/board.sh flash <elf>            # PEmicro GDB server + OpenBSW flash.gdb
OpenBSW/scripts/board.sh console 10             # board console (OpenSDA CDC, 115200)
OpenBSW/scripts/board-sil-test.sh               # OpenBSW suite against the board over DoIP
```

The host side of the link is the NetworkManager profile `openbsw-board`: 
`192.168.0.20/24` on `enp67s0`, a host route to the board at `192.168.0.200`,
and autoconnect priority 100. Every board reset drops the link, and the
profile comes back on its own afterwards.

**Board RTOS:** Eclipse ThreadX 6.4.3 (Cortex-M4 port, 1 ms tick, stack
checking on), as pinned by OpenBSW. Until `f8193eb9` the board ran FreeRTOS
V10.6.2. `ZGW_RTOS=FREERTOS` still selects it in `board-it.sh` and
`board-sil-test.sh`, and each RTOS has its own board build directory. The PC
simulation stays on FreeRTOS (OP-8).

**Board baseline (7 October 2026):**

- OpenBSW `432b9be6`, unmodified reference app (`s32k148-threadx`)
- **19/19** UDS-over-DoIP and Ethernet tests, with a reset before every test.
  The earlier `s32k148-freertos` run also gave 19/19
  ([freertos/](evidence/board-baseline/freertos/)).
- CAN tests not run (no CAN adapter attached)

Evidence and manifest are in [evidence/board-baseline](evidence/board-baseline/).

**Gateway on the board (7 October 2026, ThreadX):**

- The zonal gateway builds for the S32K148EVB from the same sources. Its
  platform folder is `gateway/app/platforms/s32k148evb`, taken from the
  reference app.
- Flash 197,132 B (Application region). RAM (data + bss) 108,276 B; MainRAM is at 72 %, against
  94 % for the ThreadX reference app.
  - On FreeRTOS the gateway used 66 % of MainRAM.
- All 9 run levels are done 27 ms after reset.
- `scripts/board-it.sh` flashes the board and runs `gateway/tests/test_board.py`.
  Result: **10/10**, the same as on FreeRTOS.
  - DoIP: announcement with the configured VIN, identification, activation
    rules, node type gateway.
  - The gateway's own UDS server and its NACKs.
  - Functional TesterPresent.
  - Without a CAN peer, a routed request leaves the route busy (NACK `0x05`).
    The unacknowledged CAN transmission then fails after about 1 s, the route
    is freed, and the third failure on `0x1030` sets U0141.
- Local UDS round trip: p95 3.2 ms (3.1 ms on FreeRTOS).
- Evidence is in [evidence/board-gateway-it](evidence/board-gateway-it/).

## Dependencies on other items

- **ThreadX rear lighting ECU:** it needs a minimal UDS-on-CAN server (`0x7E1`/`0x7E9`) before end-to-end routing can be shown. That is a separate change to [ThreadX](../ThreadX/README.md).
- **CDA diagnostic description (MDD):** it must declare the gateway and every routed ECU with the logical addresses in the routing table. The CDA rejects anything not in the MDD ([demo/README.md](../demo/README.md)).
- **AZ3166 on hardware:** it needs a new Serial2CAN profile that adds `0x7E1` to `to_serial` and `0x7E9` to `from_serial`. The existing profiles stay unchanged.
