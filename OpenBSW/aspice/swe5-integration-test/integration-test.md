# Software integration test (SWE.5)

## Strategy

Integration is bottom-up on the Linux host target (SWR-050):

1. **OpenBSW integration.** The pinned OpenBSW platform and libraries (DoIP, DoCAN, UDS, lwIP, FreeRTOS POSIX) and the contributed `transportRouter` module are integrated into the gateway executable. It builds warning-free. The OpenBSW SIL suite (`evidence/sil-baseline`) qualifies the unmodified platform underneath.
2. **Gateway integration.** The gateway runs as a process with:
   - CAN on `vcan0` and DoIP over lwIP on `tap0`
   - simulated zonal ECUs ([`sim_ecu.py`](../../gateway/tests/sim_ecu.py)): ISO-TP UDS servers on `0x7E1/0x7E9` and `0x7E2/0x7EA` with normal, silent, response-pending and multi-frame behaviour
   - a DoIP tester ([`doip_tester.py`](../../gateway/tests/doip_tester.py), doipclient 1.1.1)
   - a CAN recorder that captures every frame on `vcan0`

**Test environment:**

- Ubuntu 22.04, GCC 11.4, FreeRTOS POSIX core
- python-can 4.4.2, can-isotp 2.0.6, doipclient 1.1.1, pytest 8.3.3

Procedure: [`scripts/gateway-it.sh`](../../scripts/gateway-it.sh). It builds the
gateway, records the SHA-256 of the executable, and runs
[`test_routing.py`](../../gateway/tests/test_routing.py) and
[`test_lifecycle.py`](../../gateway/tests/test_lifecycle.py).

Recorded results: [`evidence/gateway-it/results.json`](../../evidence/gateway-it/results.json).
The report generator checks that the recorded executable hash matches the
current build.

## Integration test cases

The report generator parses this table: ID | Check | Test case | Interfaces | Verifies.
*Check* is the pytest test name.

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

## Pass criteria

- All cases pass with the executable of the current build.
