# Coding guidelines (SWE.3 / SWE.4 static verification)

| ID | Rule | Check |
| --- | --- | --- |
| CG-01 | C++17 as in OpenBSW; no dynamic memory, exceptions or RTTI in gateway and module code | Review; generator greps the sources for `new`, `malloc`, `throw`, `dynamic_cast` |
| CG-02 | Compile warning-free with the OpenBSW flags (GCC 11.4 host build) | Build log of the gateway and of the OpenBSW unit-test build |
| CG-03 | Module code is formatted by the OpenBSW gate: treefmt with clang-format 17, cmake-format and buildifier | `scripts/openbsw-pr.sh format` |
| CG-04 | No clang-tidy findings with the OpenBSW `.clang-tidy` in the module and gateway units without a justified deviation | clang-tidy |
| CG-05 | No cppcheck findings of severity warning, style, performance or portability without a justified deviation | cppcheck 2.7 |
| CG-06 | Cyclomatic complexity ≤ 15 per function; up to 25 for flat validation or dispatch functions, with justification | lizard |
| CG-07 | Shared router state is accessed only under `::async::LockType`; transport-layer calls are made outside the lock | Review |
| CG-08 | Files derived from OpenBSW keep the original copyright and state "Derived from … Modified for …"; new module files carry the OpenBSW copyright template | Generator check; OpenBSW `cr_checker` for the module |

## Justified deviations

The report generator matches these IDs against the analysis findings.

| ID | Tool / rule | Location | Justification |
| --- | --- | --- | --- |
| DEV-01 | clang-tidy `cppcoreguidelines-pro-type-vararg` | `TransportRouter.cpp` logger calls | The OpenBSW `Logger` API is variadic by design. The module uses the same file-level `NOLINTBEGIN/NOLINTEND` as `TransportRouterSimple.cpp` and the DoIP sources. |
| DEV-02 | cppcheck `useStlAlgorithm` | `TransportRouter.cpp` route, slot and tester loops | The loops run under an explicit lock scope and some exit early with side effects; OpenBSW modules use the same raw loops. An algorithm would not reduce complexity. |
| DEV-03 | lizard CCN > 15 | `TransportRouter::validate` (21), `TransportRouter::getTransportMessage` (16), `RoutingTable::validate` (22), `gen_routing.validate` (24) | Flat validation and classification chains; each branch is one configuration rule or one message class. All four are covered by unit tests at 100% of lines. |
| DEV-04 | Private attribute access | `gateway/tests/doip_tester.py` sets `DoIPClient._tcp_sock` timeout | Test code only. doipclient's `read_doip()` otherwise blocks for the socket timeout (2 s), which would invalidate the timing of the integration tests. |
