# Coding guidelines

| ID | Rule | Check |
| --- | --- | --- |
| CG-01 | Python 3.10 language level (the X-Verse interpreter); type annotations on all public functions | mypy (Python 3.10 mode), review |
| CG-02 | Ruff rule set E, F, W, B, UP, SIM, PL, RUF, C4, C90 with line length 120 ([ruff.toml](../../ruff.toml)); tests may use literal protocol values | ruff |
| CG-03 | McCabe complexity ≤ 10 per function | ruff C901 (lizard reported as information, warning above 15) |
| CG-04 | No blocking calls on the CAN receive path; cross-thread hand-over only through bounded queues and events | Review |
| CG-05 | Catch only expected exceptions (`SerialException`, `OSError`, `CanError`, `SlcanError`); no bare `except` | ruff (E722, BLE via review) |
| CG-06 | Every thread is a daemon and is joined on shutdown; every resource (port, bus) is closed | Review, integration tests |
| CG-07 | Each error or drop path increments a named counter that is visible in the statistics | Review, integration tests |

## Deviations

None. All findings of the baseline analysis were fixed in the code. The
complexity findings were removed by refactoring `_read_loop` into
`_open`/`_serve`/`_end_session`, `run` into `_dispatch`, and the codec's
validation into `_check_encodable` and lookup tables. The report generator
lists any new finding.
