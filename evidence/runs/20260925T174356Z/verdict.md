# Demo run 20260925T174356Z

| Path | Assertion | Expected | Observed | Verdict |
|---|---|---|---|---|
| A | gateway serves diag_api resources | `cabin_temp,sensor_fault_status,sensor_stuck` | `cabin_temp,sensor_fault_status,sensor_stuck` | **PASS** |
| A | no demo.* ids left | `0` | `0` | **PASS** |
| A | fault status before injection | `passed` | `passed` | **PASS** |
| A | injection accepted | `204` | `204` | **PASS** |
| A | status right after injection | `prefailed` | `prefailed` | **PASS** |
| A | status after debounce | `failed` | `failed` | **PASS** |
| A | stuck reading is frozen | `21.8` | `21.8` | **PASS** |
| A | status after clear | `passed` | `passed` | **PASS** |
| B | active faults before injection | `none` | `none` | **PASS** |
| B | injection accepted | `201` | `201` | **PASS** |
| B | CDA reports the DTC over SOVD | `01E240/2F` | `01E240/2F` | **PASS** |
| B | active faults after clear | `none` | `none` | **PASS** |

Debounce qualified after 5.21 s. Raw responses in `raw/`, timeline in `timeline.log`.

**Overall: PASS** (12 assertions)
