# Software unit verification (SWE.4)

## Strategy

| Units | Verification method |
| --- | --- |
| DD-01 … DD-04 contributed `transportRouter` module | **Unit tests** (GoogleTest/gMock) in the OpenBSW unit-test build (`tests-posix-debug`) of the pinned OpenBSW with the module added, exactly as in the upstream pull request. They use the OpenBSW transport and lock mocks, and a fake millisecond clock. Coverage is measured with gcovr, excluding throw and unreachable branches. Target: 100% lines, ≥ 95% branches. The same tests also run with Bazel (`bazel test`). |
| DD-05, DD-07, DD-08, DD-09 gateway units | **Unit tests** (GoogleTest) in the gateway build with `-DZGW_UNIT_TESTS=ON`, linked against the unit sources. |
| DD-06 routing generator | **Unit tests** (pytest) of `gen_routing.py`, with coverage.py. |
| DD-10 … DD-16 OpenBSW-integration and platform units | **Static analysis** (compiler, cppcheck, clang-tidy, complexity) and **review** against the [coding guidelines](../swe3-detailed-design/coding-guidelines.md). Their dynamic behaviour is verified by the SWE.5 integration tests. |

## Unit test cases

The report generator parses this table: ID | Test case | Unit | Verifies | Executable.
*Executable* lists the test names (gtest `Suite.test` or pytest `file::test`),
separated by spaces; `*` matches any characters. A case passes when every
listed test ran and passed.

| ID | Test case | Unit | Verifies | Executable |
| --- | --- | --- | --- | --- |
| UTC-01 | Valid configuration passes; invalid routes, global settings and address setups are rejected with the offending route; every error has a text | DD-03 | SWR-010 | `TransportRouterTest.validConfigurationPassesValidation TransportRouterTest.invalidConfigurationsAreRejectedWithTheOffendingRoute TransportRouterTest.invalidGlobalConfigurationsAreRejected TransportRouterTest.everyValidationErrorHasAText TransportRouterTest.invalidAddressSetupsAreRejected` |
| UTC-02 | A transport layer per bus is registered once and can be removed | DD-03 | SWR-010 | `TransportRouterTest.transportLayerOfABusIsRegisteredOnlyOnce` |
| UTC-03 | Requests to the local address go to the local bus in a full-size buffer; local responses return to the tester's learned bus; unknown testers are an error | DD-01, DD-03 | SWR-011 | `TransportRouterTest.requestToLocalAddressGoesToLocalBusWithFullSizeBuffer TransportRouterTest.localResponseGoesBackToTheTestersBus TransportRouterTest.localResponseToAnUnknownTesterIsAnError TransportRouterTest.testerTableRemembersTheLatestBusAndWraps` |
| UTC-04 | Unknown targets give `TPMSG_INVALID_TGT_ADDRESS` and are counted; unknown sources are not accepted | DD-01 | SWR-003 | `TransportRouterTest.unknownTargetIsRejectedAndCounted TransportRouterTest.messagesFromUnknownSourcesAreNotAccepted` |
| UTC-05 | Physical round trip: gateway tester address towards the node, original tester restored, response to the tester, counters and observer | DD-01, DD-02 | SWR-012, SWR-014 | `TransportRouterTest.physicalRequestAndResponseRoundTrip TransportRouterTest.responseBeforeDeliveryConfirmationIsAccepted TransportRouterTest.negativeResponseOtherThanPendingEndsTheRequest TransportRouterTest.requestWithoutProcessedListenerIsRouted` |
| UTC-06 | Two routes outstanding together; a second request to a busy route is rejected (`TPMSG_NO_MSG_AVAILABLE`); no free buffer is rejected | DD-01, DD-03 | SWR-015 | `TransportRouterTest.requestsToTwoRoutesAreOutstandingTogether TransportRouterTest.secondRequestToABusyRouteIsRejected TransportRouterTest.routeRequestWithoutFreeBufferIsRejected` |
| UTC-07 | Requests larger than the route limit are rejected (`TPMSG_SIZE_TOO_LARGE`) | DD-01 | SWR-017 | `TransportRouterTest.requestLargerThanTheRouteLimitIsRejected` |
| UTC-08 | A buffer released before forwarding frees the route; a failed hand-over keeps the tester address; a missing layer is an error; a failed delivery frees the route and reports the node | DD-02, DD-03 | SWR-018 | `TransportRouterTest.bufferReleasedBeforeForwardingFreesTheRoute TransportRouterTest.failedForwardingKeepsTheTesterAddressAndFreesTheRouteOnRelease TransportRouterTest.missingTransportLayerIsAnError TransportRouterTest.failedDeliveryFreesTheRouteAndReportsTheNode` |
| UTC-09 | P2, delivery timeout, NRC 0x78 → P2\*, P2\* expiry, segmented-response budget, timer wrap-around | DD-02 | SWR-016 | `TransportRouterTest.noResponseWithinP2FreesTheRoute TransportRouterTest.unconfirmedDeliveryTimesOut TransportRouterTest.responsePendingIsForwardedAndExtendsToP2Star TransportRouterTest.responsePendingTimesOutAfterP2Star TransportRouterTest.segmentedResponseGetsMoreThanP2 TransportRouterTest.segmentedResponseWithShortP2StarGetsTheTransferBudget TransportRouterTest.deadlinesWorkAcrossTimerWrapAround` |
| UTC-10 | Unsolicited and late responses are discarded and counted; a released tester frees its routes and functional window at once | DD-02 | SWR-041, SWR-042 | `TransportRouterTest.unsolicitedResponseIsDiscardedAndCounted TransportRouterTest.releasedTesterFreesItsRoutesAtOnce TransportRouterTest.releasedTesterClosesItsFunctionalWindow TransportRouterTest.releasingAnotherTesterKeepsSendingRoutesAndFunctionalWindow` |
| UTC-11 | Functional request: local plus one copy per route bus; responses within the window; larger than one frame rejected; copies released on failure or without buffers | DD-01 | SWR-013 | `TransportRouterTest.functionalRequestGoesToLocalAndOncePerRouteBus TransportRouterTest.functionalRequestLargerThanASingleFrameIsRejected TransportRouterTest.functionalCopyThatCannotBeSentIsReleased TransportRouterTest.functionalRequestWithoutFreeBufferReachesOnlyLocal` |
| UTC-12 | Buffers run out and are counted; static pools are restored after release | DD-03 | SWR-043 | `TransportRouterTest.buffersRunOutAndAreCounted` |
| UTC-13 | Statistics saturate at 0xFFFF and reset; router works without an observer | DD-04 | SWR-023 | `TransportRouterTest.statisticsSaturateAndReset TransportRouterTest.routerWorksWithoutObserver` |
| UTC-14 | Gateway routing table: generated configuration valid; 18 invalid tables name the offending route and error | DD-05 | SWR-010 | `RoutingTable.generatedConfigurationIsValid RoutingTable.invalidTablesNameTheOffendingRoute` |
| UTC-15 | Node monitor: DTCs registered; 3 consecutive timeouts set the DTC once; a response passes it and resets the count; unknown routes ignored | DD-07 | SWR-024 | `NodeMonitor.*` |
| UTC-16 | DTC store: registered DTCs supported with testNotCompleted; fault, passed and clear follow the ISO 14229-1 status bits; DTC setting off | DD-08 | SWR-025 | `DtcStore.*` |
| UTC-17 | Identification DIDs come from the configuration; version contains gateway version, OpenBSW revision and routing-table hash | DD-09 | SWR-021 | `GatewayIdentity.*` |
| UTC-18 | Generator: shipped configuration valid; 16 invalid configurations named; header, address table and unchanged-output stability; exit codes | DD-06 | SWR-010, SWR-052 | `test_gen_routing.py::test_shipped_configuration_is_valid test_gen_routing.py::test_hash_changes_with_any_address test_gen_routing.py::test_invalid_configurations_name_the_problem* test_gen_routing.py::test_generated_header_and_address_table test_gen_routing.py::test_invalid_file_fails_with_exit_code_2` |
| UTC-19 | Generator: Serial2CAN profile consistency check, and the unchanged AZ3166 lighting profiles forward no diagnostic IDs | DD-06 | SWR-033, SWR-052 | `test_gen_routing.py::test_serial2can_profile_consistency test_gen_routing.py::test_existing_az3166_profiles_do_not_forward_diagnostics` |

## Pass criteria

- All unit tests pass in the OpenBSW unit-test build, in Bazel, in the gateway unit-test build and in pytest.
- `transportRouter`: 100% line and function coverage, ≥ 95% branch coverage (gcovr, without throw and unreachable branches).
- No open static analysis findings outside the justified deviations.
