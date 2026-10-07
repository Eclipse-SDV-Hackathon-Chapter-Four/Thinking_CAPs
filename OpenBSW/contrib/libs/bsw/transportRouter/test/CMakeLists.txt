# *******************************************************************************
# Copyright (c) 2026 Jefferson Nascimento
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

add_executable(transportRouterTest src/TransportRouterTest.cpp)

target_link_libraries(
    transportRouterTest
    PRIVATE transportRouter
            asyncMockImpl
            gmock_main
            transportMock
            utilMock
            etl)

gtest_discover_tests(transportRouterTest PROPERTIES LABELS
                                                    "transportRouterTest")
