# Path B manual run — 2026-09-22T14:12:57+02:00

## G1: components
["tmcc3000","hovr4000","fsnr2000","flxcng1000","jgwt5000","flxc1000"]

## Clear sim fault memory
200
## Faults before injection (SOVD)
{"items":[{"code":"01E240","scope":"FaultMem","fault_name":"Code1","severity":0,"status":{"test_failed":false,"test_failed_this_operation_cycle":false,"pending_dtc":false,"confirmed_dtc":false,"test_not_completed_since_last_clear":false,"test_failed_since_last_clear":false,"test_not_completed_this_operation_cycle":false,"warning_indicator_requested":false,"mask":"00"}},{"code":"01E244","scope":"FaultMem","fault_name":"Code6","severity":0,"status":{"test_failed":false,"test_failed_this_operation_cycle":false,"pending_dtc":false,"confirmed_dtc":false,"test_not_completed_since_last_clear":false,"test_failed_since_last_clear":false,"test_not_completed_this_operation_cycle":false,"warning_indicator_requested":false,"mask":"00"}},{"code":"039447","scope":"FaultMem","fault_name":"Code2","severity":0,"status":{"test_failed":false,"test_failed_this_operation_cycle":false,"pending_dtc":false,"confirmed_dtc":false,"test_not_completed_since_last_clear":false,"test_failed_since_last_clear":false,"test_not_completed_this_operation_cycle":false,"warning_indicator_requested":false,"mask":"00"}},{"code":"01E243","scope":"FaultMem","fault_name":"Code5","severity":0,"status":{"test_failed":false,"test_failed_this_operation_cycle":false,"pending_dtc":false,"confirmed_dtc":false,"test_not_completed_since_last_clear":false,"test_failed_since_last_clear":false,"test_not_completed_this_operation_cycle":false,"warning_indicator_requested":false,"mask":"00"}},{"code":"01E242","scope":"FaultMem","fault_name":"Code4","severity":0,"status":{"test_failed":false,"test_failed_this_operation_cycle":false,"pending_dtc":false,"confirmed_dtc":false,"test_not_completed_since_last_clear":false,"test_failed_since_last_clear":false,"test_not_completed_this_operation_cycle":false,"warning_indicator_requested":false,"mask":"00"}},{"code":"01E241","scope":"FaultMem","fault_name":"Code3","severity":0,"status":{"test_failed":false,"test_failed_this_operation_cycle":false,"pending_dtc":false,"confirmed_dtc":false,"test_not_completed_since_last_clear":false,"test_failed_since_last_clear":false,"test_not_completed_this_operation_cycle":false,"warning_indicator_requested":false,"mask":"00"}}]}

## Inject DTC 0x007001 status 0x2F (sim :8181)
201
## Sim fault memory
[{"id":"7001","status":{"testFailed":true,"testFailedThisOperationCycle":true,"pendingDtc":true,"confirmedDtc":true,"testNotCompletedSinceLastClear":false,"testFailedSinceLastClear":true,"testNotCompletedThisOperationCycle":false,"warningIndicatorRequested":false},"statusMask":"2F","emissionsRelated":false,"snapshots":[],"extendedData":[]}]

## Faults after injection (SOVD :20002, CDA reads the ECU via UDS 0x19 over DoIP)
{
  "message": "Bad payload: No DTC with code 7001 found in DTC references",
  "error_code": "vendor-specific",
  "vendor_code": "bad-request"
}

# Retry with a DTC defined in the MDD — 2026-09-22T14:13:09+02:00
## Clear sim
200
## Inject 0x01E240 status 0x2F
201
## SOVD faults (active only)
[
  {
    "code": "01E240",
    "scope": "FaultMem",
    "fault_name": "DTC Code 1",
    "severity": 0,
    "status": {
      "test_failed": true,
      "test_failed_this_operation_cycle": true,
      "pending_dtc": true,
      "confirmed_dtc": true,
      "test_not_completed_since_last_clear": false,
      "test_failed_since_last_clear": true,
      "test_not_completed_this_operation_cycle": false,
      "warning_indicator_requested": false,
      "mask": "2F"
    }
  }
]
## Clear sim again (cleanup)
200
## SOVD faults after clear (active only)
[]
