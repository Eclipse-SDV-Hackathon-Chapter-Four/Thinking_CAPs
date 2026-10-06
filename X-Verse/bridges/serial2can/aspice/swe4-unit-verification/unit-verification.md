# Software unit verification (SWE.4)

## Strategy

- **Unit tests (pytest).** They exercise the I/O-free units: the codec
  (DD-01…03), `IdFilter` (DD-04), `EchoGuard` (DD-05), the queueing decisions
  of `enqueue` (DD-09) and configuration handling (DD-12).
- **Static verification on every unit:**
  - ruff with the rule set of [CG-02](../swe3-detailed-design/coding-guidelines.md)
  - mypy in Python 3.10 mode
  - complexity (ruff C901 ≤ 10; lizard for information)
- **Structural coverage.** coverage.py measures line and branch coverage over
  the whole host test suite (unit and integration), including the CLI child
  process. The units with threads and I/O (DD-06…11) get their dynamic
  verification from the SWE.5 tests.

The report generator runs pytest with JUnit XML output. A test case passes
when every parametrised instance of its pytest function passes.

## Unit test cases

The report generator parses this table: ID | Test case | Unit | Verifies | Test.

| ID | Test case | Unit | Verifies | Test |
| --- | --- | --- | --- | --- |
| UTC-01 | All 256 status bytes encode to a 22-byte line and decode to the same message | DD-01, DD-02 | SWR-001, SWR-002 | tests/test_slcan.py::test_status_byte_round_trip |
| UTC-02 | Exact standard, 0-DLC, extended, remote and extended-remote encodings round-trip | DD-01, DD-02 | SWR-001, SWR-002 | tests/test_slcan.py::test_encode_exact |
| UTC-03 | Lower-case hex and a 4-digit timestamp are accepted | DD-02 | SWR-001 | tests/test_slcan.py::test_decode_accepts_lowercase_and_timestamp |
| UTC-04 | 15 malformed lines (length, DLC, range, characters, non-frames) raise `SlcanError` | DD-02 | SWR-001 | tests/test_slcan.py::test_decode_rejects_malformed |
| UTC-05 | Out-of-range IDs, error frames and CAN FD frames are refused | DD-01 | SWR-002, SWR-010 | tests/test_slcan.py::test_encode_rejects_unsupported |
| UTC-06 | Tokens split across chunks; BELL, bare OK, LF handling | DD-03 | SWR-003 | tests/test_slcan.py::test_splitter_tokens_across_chunks |
| UTC-07 | Over-long lines are reported once and the stream recovers | DD-03 | SWR-003 | tests/test_slcan.py::test_splitter_flags_overlong_lines |
| UTC-08 | Exact, masked, extended-only and empty filters | DD-04 | SWR-007 | tests/test_slcan.py::test_id_filter |
| UTC-09 | Extended filter entries default to a 29-bit exact mask | DD-04 | SWR-007 | tests/test_units.py::test_extended_filter_defaults_to_29_bit_mask |
| UTC-10 | One echo cancelled per send; expiry after the window; other payloads unaffected | DD-05 | SWR-009 | tests/test_slcan.py::test_echo_guard_cancels_one_echo_per_send |
| UTC-11 | `enqueue` outcomes: filtered, offline, queued, queue full | DD-09 | SWR-021 | tests/test_units.py::test_enqueue_decisions |
| UTC-12 | Port defaults; unsupported nominal bitrate rejected | DD-09, DD-12 | SWR-012 | tests/test_units.py::test_link_defaults_and_validation |
| UTC-13 | `--device` overrides; malformed overrides and empty port lists rejected | DD-12 | SWR-012 | tests/test_units.py::test_load_config_overrides_and_errors |
| UTC-14 | Duplicate port names rejected | DD-10 | SWR-012 | tests/test_units.py::test_bridge_rejects_duplicate_port_names |
| UTC-15 | All shipped configurations load and validate | DD-12 | SWR-011, SWR-012 | tests/test_units.py::test_shipped_configs_are_valid |

## Pass criteria

- All unit test cases pass.
- No ruff or mypy findings.
- No function above complexity 10.
- At least 90% line and 85% branch coverage over the host test suite.
