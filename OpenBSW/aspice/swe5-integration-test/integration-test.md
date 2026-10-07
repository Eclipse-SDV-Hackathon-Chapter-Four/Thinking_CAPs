# Software integration test (SWE.5)

## Strategy

Integration is bottom-up on the Linux host target (SWR-050):

1. **OpenBSW integration.** The pinned OpenBSW platform and libraries (DoIP, DoCAN, UDS, lwIP, FreeRTOS POSIX port) and the contributed `transportRouter` module are integrated into the gateway executable. It builds warning-free. The OpenBSW SIL suite (`evidence/sil-baseline`) qualifies the unmodified platform underneath.
2. **Gateway integration.** The gateway runs as a process with:
   - CAN on `vcan0` and DoIP over lwIP on `tap0`
   - simulated zonal ECUs ([`sim_ecu.py`](../../gateway/tests/sim_ecu.py)): ISO-TP UDS servers on `0x7E1/0x7E9` and `0x7E2/0x7EA` with normal, silent, response-pending and multi-frame behaviour
   - a simulated Ethernet zonal ECU ([`sim_doip_ecu.py`](../../gateway/tests/sim_doip_ecu.py)): a DoIP entity `0x1040` at `192.168.0.30` (on the host's `lo`, added by `net-up.sh`) with a UDS server and switchable failures: silent, no acknowledgement, NACK, refused activation, closing the connection, refusing connections
   - a DoIP tester ([`doip_tester.py`](../../gateway/tests/doip_tester.py), doipclient 1.1.1)
   - a CAN recorder that captures every frame on `vcan0`

**Test environment:**

- Ubuntu 22.04, GCC 11.4, FreeRTOS POSIX port (the board runs ThreadX; OP-8)
- python-can 4.4.2, can-isotp 2.0.6, doipclient 1.1.1, pytest 8.3.3

Procedure: [`scripts/gateway-it.sh`](../../scripts/gateway-it.sh). It builds the
gateway, records the SHA-256 of the executable, and runs
[`test_routing.py`](../../gateway/tests/test_routing.py),
[`test_doip_routing.py`](../../gateway/tests/test_doip_routing.py) and
[`test_lifecycle.py`](../../gateway/tests/test_lifecycle.py).

Recorded results: [`evidence/gateway-it/results.json`](../../evidence/gateway-it/results.json).
The report generator checks that the recorded executable hash matches the
current build.

3. **Target integration.** The same sources are built for the NXP S32K148EVB
   (Arm GNU Toolchain 14.3.rel1, ThreadX 6.4.3 Cortex-M4 port) and flashed with the PEmicro GDB server over
   OpenSDA. They are tested over the board's 100BASE-T1 Ethernet
   (`192.168.0.200`) with [`test_board.py`](../../gateway/tests/test_board.py).
   No CAN node is attached to the board, so routed CAN requests exercise the
   failure path. The DoIP route `0x1040` reaches the simulated Ethernet ECU on
   the host over the same link, so routing is verified end to end on the
   board.

   Procedure: [`scripts/board-it.sh`](../../scripts/board-it.sh). Recorded results:
   [`evidence/board-gateway-it/results.json`](../../evidence/board-gateway-it/results.json).
   The generator checks them against the current board image.

## Integration test cases

The report generator parses this table: ID | Check | Test case | Interfaces | Verifies.
*Check* is the pytest test name; `board:` marks a test of the board run.

| ID | Check | Test case | Interfaces | Verifies |
| --- | --- | --- | --- | --- |
| ITC-01 | test_local_identification | F190/F195/F18C answered by `0x1010` from source `0x1010` | IF-01, IF-03 | SWR-011, SWR-021 |
| ITC-02 | test_routing_table_did | FD00 equals the routing configuration | IF-01, IF-05 | SWR-022 |
| ITC-03 | test_local_services_and_nrcs | Sessions, TesterPresent (incl. suppressed), NRC 0x11 and 0x31 | IF-01 | SWR-020, SWR-027 |
| ITC-04 | test_physical_routing_to_can_ecu | Request on `0x7E1` padded to 8 bytes; response from `0x1020` | IF-01, IF-02, IF-03, IF-04 | SWR-012, SWR-018 |
| ITC-05 | test_unknown_target_nack | Unknown target → NACK 0x03 | IF-01, IF-03 | SWR-003 |
| ITC-06 | test_multiframe_response_and_transparency | 1003-byte segmented response forwarded byte for byte | IF-02, IF-04 | SWR-014, SWR-018 |
| ITC-07 | test_negative_response_passthrough | Negative response forwarded unchanged | IF-02, IF-04 | SWR-014 |
| ITC-08 | test_response_pending_passthrough | NRC 0x78 then the final response within P2\* | IF-02, IF-04 | SWR-014, SWR-016 |
| ITC-09 | test_large_request | 4095-byte request routed; 4096 → NACK 0x04 | IF-01, IF-02 | SWR-017 |
| ITC-10 | test_busy_route_nack_and_timeout | Second request to a busy route → NACK 0x05; route free after P2; counters | IF-01, IF-03 | SWR-003, SWR-015, SWR-016, SWR-023 |
| ITC-11 | test_parallel_routes | Requests to two routes outstanding at once both complete | IF-01, IF-02 | SWR-015 |
| ITC-12 | test_tester_disconnect_releases_route | Disconnect frees the route at once | IF-01, IF-03 | SWR-004, SWR-041 |
| ITC-13 | test_unsolicited_response_discarded | Unsolicited CAN response reaches no tester and is counted | IF-02, IF-03 | SWR-042 |
| ITC-14 | test_functional_tester_present | One frame on `0x7DF`; one response per node with its own address | IF-01, IF-02 | SWR-013 |
| ITC-15 | test_functional_suppressed_and_too_large | `3E 80` → ACK only; 8-byte functional → NACK 0x04 | IF-01, IF-02 | SWR-013 |
| ITC-16 | test_lost_communication_dtc | 3 timeouts set U0141 (testFailed + confirmed); 19 0A lists both DTCs | IF-01, IF-06 | SWR-024, SWR-025 |
| ITC-17 | test_dtc_passes_and_clears | Response passes the DTC; 14 FFFFFF clears it | IF-01, IF-06 | SWR-024, SWR-025 |
| ITC-18 | test_no_traffic_when_idle | No gateway CAN frame for 2 s without requests | IF-02 | SWR-024, SWR-030 |
| ITC-19 | test_lighting_frames_ignored | `0x1F1`/`0x1F4` traffic changes no gateway counter | IF-02 | SWR-030 |
| ITC-20 | test_can_identifier_discipline | Over the module only diagnostic IDs (plus injected lighting frames) appear | IF-02 | SWR-030 |
| ITC-21 | test_vehicle_announcement | Three announcements 500 ms apart with VIN and `0x1010` | IF-01 | SWR-001 |
| ITC-22 | test_vehicle_identification_requests | Generic, by-VIN and by-EID identification answered | IF-01 | SWR-001 |
| ITC-23 | test_routing_activation_rules | Tester range accepted; unknown source 0x00; type 0x01 → 0x06 | IF-01 | SWR-002 |
| ITC-24 | test_two_testers_at_once | Two simultaneous tester connections | IF-01 | SWR-002 |
| ITC-25 | test_entity_status_and_power_mode | Node type gateway, socket limits, current count; power mode ready | IF-01 | SWR-005 |
| ITC-26 | test_forwarding_latency | 200 round trips; p95 DoIP→CAN and CAN→DoIP ≤ 10 ms | IF-01, IF-02 | SWR-060 |
| ITC-27 | test_periodic_statistics_log | Start-up line with routing-table hash; statistics line within 35 s, consistent with FD01 | IF-08, IF-01 | SWR-054 |
| ITC-28 | test_shutdown | SIGINT → exit 0 within 1 s; no CAN frame afterwards; DoIP after CAN/ISO-TP run levels | IF-08 | SWR-044 |
| ITC-29 | board:test_board_vehicle_announcement | S32K148: announcement after reset with the configured VIN and `0x1010` | IF-01 | SWR-001, SWR-051 |
| ITC-30 | board:test_board_vehicle_identification | S32K148: generic and by-VIN identification | IF-01 | SWR-001 |
| ITC-31 | board:test_board_routing_activation_rules | S32K148: tester range accepted; unknown source and type 0x01 rejected | IF-01 | SWR-002 |
| ITC-32 | board:test_board_entity_status | S32K148: node type gateway, sockets, power mode | IF-01 | SWR-005 |
| ITC-33 | board:test_board_local_uds | S32K148: F190/F18C/F195, FD00, sessions, NRC 0x11/0x31 | IF-01, IF-03 | SWR-011, SWR-020, SWR-021, SWR-022 |
| ITC-34 | board:test_board_rejections | S32K148: unknown target NACK 0x03; 8-byte functional NACK 0x04 | IF-01, IF-03 | SWR-003, SWR-013 |
| ITC-35 | board:test_board_functional_tester_present | S32K148: functional TesterPresent answered by the gateway | IF-01 | SWR-013 |
| ITC-36 | board:test_board_local_latency | S32K148: local UDS round trip p95 ≤ 20 ms over 100BASE-T1 | IF-01 | SWR-051 |
| ITC-37 | board:test_board_route_without_can_peer | S32K148: unacknowledged CAN request keeps the route busy (NACK 0x05), fails, frees the route, counted | IF-01, IF-02 | SWR-015, SWR-016, SWR-018 |
| ITC-38 | board:test_board_lost_communication_dtc | S32K148: three failed requests set U0141; ClearDTC resets it | IF-01, IF-06 | SWR-024, SWR-025 |
| ITC-39 | test_doip_physical_routing | DoIP route: connect, activation (`0x0E10`, `0x00`), request from `0x0E10`, response from `0x1040`; no CAN frame | IF-01, IF-09 | SWR-006, SWR-019, SWR-030 |
| ITC-40 | test_doip_connection_reused | Five requests over one connection and one activation | IF-09 | SWR-006 |
| ITC-41 | test_doip_large_messages | 3000-byte response and 4000-byte request unchanged | IF-01, IF-09 | SWR-014, SWR-017 |
| ITC-42 | test_doip_response_pending | NRC 0x78 then the final response from `0x1040` | IF-09 | SWR-016 |
| ITC-43 | test_doip_negative_response_passthrough | Negative response from the node forwarded unchanged | IF-09 | SWR-014 |
| ITC-44 | test_doip_functional | Functional `3E 00` answered by `0x1010`, the CAN ECU `0x1020` and the DoIP ECU `0x1040` | IF-01, IF-02, IF-09 | SWR-013, SWR-019 |
| ITC-45 | test_doip_alive_check | The node's alive check answered with `0x0E10` | IF-09 | SWR-006 |
| ITC-46 | test_doip_unsolicited_response_discarded | Diagnostic message from the node without a request: dropped and counted | IF-09, IF-03 | SWR-042 |
| ITC-47 | test_doip_node_nack | Node NACK: no response, route free at once, tx_fail counted | IF-09, IF-03 | SWR-019 |
| ITC-48 | test_doip_no_acknowledgement | No acknowledgement: route busy (NACK 0x05) until the 1.5 s budget, connection closed, next request reconnects | IF-01, IF-09 | SWR-006 |
| ITC-49 | test_doip_activation_refused | Refused routing activation fails the request; the route is free | IF-09 | SWR-006 |
| ITC-50 | test_doip_node_closes_connection | The next request after a closure by the node reconnects | IF-09 | SWR-006 |
| ITC-51 | test_doip_node_unreachable | Refused TCP connection fails the request well within the budget; the route is free | IF-09 | SWR-006 |
| ITC-52 | test_doip_lost_communication_dtc | Three unanswered requests set U0142; ClearDTC resets it | IF-01, IF-06 | SWR-024, SWR-025 |
| ITC-53 | board:test_board_doip_routing | S32K148: routing activation from `0x0E10` and a routed request to the Ethernet ECU over 100BASE-T1 | IF-01, IF-09 | SWR-006, SWR-019, SWR-051 |
| ITC-54 | board:test_board_doip_large_and_pending | S32K148: 3000-byte response, 4000-byte request, response pending | IF-01, IF-09 | SWR-014, SWR-016, SWR-017 |
| ITC-55 | board:test_board_doip_functional | S32K148: functional TesterPresent answered by `0x1010` and `0x1040` | IF-01, IF-09 | SWR-013, SWR-019 |
| ITC-56 | board:test_board_doip_latency | S32K148: routed round trip tester → board → DoIP ECU → tester, p95 ≤ 20 ms | IF-01, IF-09 | SWR-051 |
| ITC-57 | board:test_board_doip_node_failures | S32K148: unreachable and silent node fail the requests, three failures set U0142, ClearDTC resets it | IF-01, IF-06, IF-09 | SWR-006, SWR-024, SWR-025 |
| ITC-58 | test_bus_load_pacing | 4095-byte request with STmin 0: ≥ 3 ms between gateway frames, ≤ 10 % in every 1 s window | IF-02 | SWR-032 |
| ITC-59 | test_reachability_routine | Routine F000: `01 00 01` with CAN and DoIP ECUs answering and no ECU on `0x1030`; `00 00 01` with `0x1020` silent; running status before the window ends | IF-01, IF-02, IF-09 | SWR-026 |
| ITC-60 | board:test_board_reachability_routine | S32K148: routine F000 reports the DoIP route reached and the CAN routes (no peer) not reached | IF-01, IF-09 | SWR-026, SWR-051 |

## Pass criteria

- All cases pass with the executable of the current build (POSIX) and the current board image (S32K148).
