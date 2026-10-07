# *******************************************************************************
# Copyright (c) 2026 Jefferson Nascimento
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

add_library(
    doipClient
    src/doip/client/DoIpClientConnection.cpp
    src/doip/client/DoIpClientLogger.cpp
    src/doip/client/DoIpClientTransportLayer.cpp)

target_include_directories(doipClient PUBLIC include)

target_link_libraries(doipClient PUBLIC doip transport cpp2ethernet etl)
