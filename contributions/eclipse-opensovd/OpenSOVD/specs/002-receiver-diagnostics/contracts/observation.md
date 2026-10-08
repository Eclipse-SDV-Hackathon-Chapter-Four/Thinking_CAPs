# Observation transport

Native C++ builds enable `SCORE_DIAGNOSTIC_SOCKET=/path/receiver.sock` and
`SCORE_BUILD_IDENTITY=<actual-built-artifact-identity>`. Unset socket disables instrumentation.
AF_UNIX SOCK_DGRAM O_NONBLOCK, <=4096 bytes, best-effort: missing/full receiver drops data.
Socket is local and permissions restrict writers; boot ID and session provenance are validated.
Consumer callback records speed receipt/acceptance; control-loop emission carries actual current state.
No network/HTTP dependency in the controller. Native source/fixture mode is recorded by the test runner.
