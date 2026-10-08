# SPDX-License-Identifier: Apache-2.0
#
# Platform-independent gateway library: CAN routing table, node monitor and identity.
# Routing itself is the contributed OpenBSW module transportRouter. RoutingConfig.h is generated from config/routing.yaml.

find_package(Python3 REQUIRED COMPONENTS Interpreter)

set(GATEWAY_ROUTING_YAML "${CMAKE_CURRENT_SOURCE_DIR}/../config/routing.yaml")
set(GATEWAY_GEN_DIR "${CMAKE_BINARY_DIR}/generated")
set(GATEWAY_ROUTING_HEADER "${GATEWAY_GEN_DIR}/gateway/RoutingConfig.h")

add_custom_command(
    OUTPUT ${GATEWAY_ROUTING_HEADER} ${GATEWAY_GEN_DIR}/routing-table.json
    COMMAND ${Python3_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/../tools/gen_routing.py
            ${GATEWAY_ROUTING_YAML} --out ${GATEWAY_GEN_DIR}
    DEPENDS ${GATEWAY_ROUTING_YAML} ${CMAKE_CURRENT_SOURCE_DIR}/../tools/gen_routing.py
    COMMENT "Generating gateway routing configuration from routing.yaml")
add_custom_target(gatewayRoutingConfig DEPENDS ${GATEWAY_ROUTING_HEADER})

execute_process(
    COMMAND git -C ${OPENBSW_DIR} rev-parse --short=8 HEAD
    OUTPUT_VARIABLE OPENBSW_REVISION
    OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET)

add_library(zonalGateway src/gateway/GatewayIdentity.cpp src/gateway/NodeMonitor.cpp
                         src/gateway/RoutingTable.cpp)
add_dependencies(zonalGateway gatewayRoutingConfig)
target_include_directories(zonalGateway PUBLIC include ${GATEWAY_GEN_DIR})
target_compile_definitions(
    zonalGateway PRIVATE GATEWAY_VERSION="${PROJECT_VERSION}"
                         OPENBSW_REVISION="${OPENBSW_REVISION}")
target_link_libraries(
    zonalGateway
    PUBLIC transportRouter transport etl
    PRIVATE util)

# Host unit tests of the gateway units (SWE.4): -DZGW_UNIT_TESTS=ON
if (ZGW_UNIT_TESTS)
    enable_testing()
    include(GoogleTest)
    set(INSTALL_GTEST OFF CACHE BOOL "" FORCE)
    add_subdirectory(${OPENBSW_DIR}/libs/3rdparty/googletest
                     ${CMAKE_BINARY_DIR}/googletest EXCLUDE_FROM_ALL)
    add_executable(
        gatewayUnitTest test/GatewayUnitTest.cpp
                        ${CMAKE_CURRENT_SOURCE_DIR}/../app/application/src/uds/DemoDtcManager.cpp)
    target_include_directories(
        gatewayUnitTest PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/../app/application/include)
    target_link_libraries(gatewayUnitTest PRIVATE zonalGateway util etl gtest_main)
    target_compile_options(zonalGateway PRIVATE --coverage)
    target_link_options(zonalGateway INTERFACE --coverage)
    target_compile_options(gatewayUnitTest PRIVATE --coverage)
    target_link_options(gatewayUnitTest PRIVATE --coverage)
    gtest_discover_tests(gatewayUnitTest PROPERTIES LABELS "gatewayUnitTest")
endif ()
