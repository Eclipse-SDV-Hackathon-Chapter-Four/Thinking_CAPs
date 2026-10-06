# Software integration test (SWE.5)

## Strategy

1. **Software integration on the host.** The complete bridge runs on real
   threads, real pyserial and python-can. The serial side is simulated
   Lawicell ECUs on Linux pseudo-terminals; the CAN side is python-can's
   `virtual` bus or the real `udp_multicast` bus. Each test exercises an
   interface (IF-01, IF-02, IF-04, IF-05, IF-06) and the error paths.
   The generator re-executes these tests on every report run.
2. **Hardware/software integration.** The bridge drives the physical MXChip
   AZ3166 with the ThreadX lighting firmware over `udp_multicast`. Procedure:
   [tests/hardware_check.py](../../tests/hardware_check.py). The results are
   recorded in [evidence/hardware-check](../../evidence/hardware-check/results.json),
   and the generator checks that the recorded source hashes match the current code.

## Integration test cases

The report generator parses this table: ID | Test case | Interfaces | Verifies | Test.
`hw:` refers to a check in the recorded hardware run.

| ID | Test case | Interfaces | Verifies | Test |
| --- | --- | --- | --- | --- |
| ITC-01 | Handshake order `C, V, S6, O`; CAN→serial and serial→CAN with filters; ACK counting; `C` on shutdown | IF-01, IF-02, IF-05, IF-06 | SWR-003, SWR-004, SWR-005, SWR-006, SWR-007, SWR-023 | tests/test_bridge.py::test_handshake_both_directions_filters_and_close |
| ITC-02 | Two ECUs: fan-out between ports, not back to the source; extended and remote frames both ways | IF-01, IF-02, IF-05 | SWR-005, SWR-006, SWR-008 | tests/test_bridge.py::test_serial_to_serial_fan_out_and_extended_remote |
| ITC-03 | Unplug: offline drops counted; replug: fresh handshake and traffic | IF-01 | SWR-020, SWR-021, SWR-024 | tests/test_bridge.py::test_reconnects_after_unplug |
| ITC-04 | `udp_multicast`: an ECU's own frame is not looped back; other nodes' frames are delivered | IF-02 | SWR-009, SWR-011 | tests/test_bridge.py::test_udp_multicast_echo_is_not_returned_to_the_ecu |
| ITC-05 | A non-tty device is retried without blocking others; a late device is found by glob | IF-01 | SWR-020 | tests/test_robustness.py::test_unusable_device_is_retried_and_late_glob_device_connects |
| ITC-06 | Failing `bus.send` is counted and fan-out continues | IF-02, IF-05 | SWR-022 | tests/test_robustness.py::test_can_send_error_is_counted_and_fan_out_continues |
| ITC-07 | Serial write failure: one disconnect counted, reconnect with handshake, traffic resumes | IF-01, IF-06 | SWR-020, SWR-024 | tests/test_robustness.py::test_serial_write_failure_triggers_reconnect |
| ITC-08 | FD frames are not written; bus error frames are ignored | IF-02, IF-06 | SWR-010 | tests/test_robustness.py::test_unencodable_frames_are_not_written |
| ITC-09 | CLI process: `--device` override, periodic stats, SIGTERM → `C` and exit 0 | IF-03, IF-04, IF-07 | SWR-012, SWR-023, SWR-024 | tests/test_robustness.py::test_cli_process_runs_and_stops_cleanly_on_sigterm |
| ITC-10 | AZ3166: the state report after open reaches the bus | IF-01, IF-02 | SWR-003, SWR-004, SWR-005 | hw:ecu-state-report-on-open |
| ITC-11 | AZ3166: all 256 status bytes through bridge and ECU; median round trip ≤ 10 ms | IF-01, IF-02 | SWR-005, SWR-006, SWR-030 | hw:all-256-status-bytes-through-bridge |
| ITC-12 | AZ3166: 1 s diagnostic heartbeat forwarded | IF-01, IF-02 | SWR-005 | hw:diagnostic-heartbeat-forwarded |
| ITC-13 | AZ3166: a filtered ID does not reach the ECU | IF-06 | SWR-007 | hw:to-serial-filter |
| ITC-14 | AZ3166: SIGTERM sends `C` to the ECU | IF-04 | SWR-023 | hw:clean-shutdown-closes-ecu |
| ITC-15 | AZ3166: the ECU reports lamps off after the bridge stops | IF-01 | SWR-023 | hw:ecu-fail-safe-after-bridge-stop |

## Pass criteria

- All test cases pass.
- The hardware evidence was recorded with the current sources.
