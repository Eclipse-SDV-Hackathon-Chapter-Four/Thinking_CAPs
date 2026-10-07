# *******************************************************************************
# Copyright (c) 2026 Jefferson Nascimento
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

# AI disclosure: this file was largely generated with an AI assistant and was
# reviewed and tested by the contributor. Assisted-by: Anthropic Claude Opus 5.5

add_executable(doipClientTest src/DoIpClientTransportLayerTest.cpp)

target_link_libraries(
    doipClientTest
    PRIVATE doipClient
            doip
            asyncMockImpl
            util
            utilMock
            cpp2ethernet
            cpp2ethernetMock
            transportMock
            bspMock
            gmock_main
            etl)

gtest_discover_tests(doipClientTest PROPERTIES LABELS "doipClientTest")
