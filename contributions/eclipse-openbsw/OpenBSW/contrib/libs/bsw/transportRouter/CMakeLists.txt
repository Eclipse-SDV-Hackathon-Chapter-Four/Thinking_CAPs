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
    transportRouter
    src/transport/TpGatewayLogger.cpp src/transport/routing/TransportRouter.cpp
    src/transport/routing/TransportRouterStatistics.cpp)

target_include_directories(transportRouter PUBLIC include)

target_link_libraries(transportRouter PUBLIC transport etl)
