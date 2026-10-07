# SPDX-License-Identifier: Apache-2.0
#
# OpenBSW zonal diagnostic gateway. An out-of-tree application on the pinned,
# unmodified Eclipse OpenBSW checkout (OPENBSW_DIR), mirroring the OpenBSW root
# CMakeLists.txt for the referenceApp build with our own application in app/.
#
#   cmake -S OpenBSW/gateway -B <build> -G Ninja -DOPENBSW_DIR=<openbsw checkout>
#   S32K148EVB: add -DBUILD_TARGET_PLATFORM=S32K148EVB
#               -DCMAKE_TOOLCHAIN_FILE=<openbsw>/cmake/toolchains/ArmNoneEabi.cmake
cmake_minimum_required(VERSION 3.28 FATAL_ERROR)

set(CMAKE_CXX_SCAN_FOR_MODULES FALSE)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_C_STANDARD 99)

if (NOT OPENBSW_DIR OR NOT EXISTS "${OPENBSW_DIR}/libs/bsw")
    message(FATAL_ERROR "Set OPENBSW_DIR to the pinned OpenBSW checkout")
endif ()

set(BUILD_TARGET_PLATFORM
    "POSIX"
    CACHE STRING "Target Platform")
set(BUILD_TARGET_RTOS
    "FREERTOS"
    CACHE STRING "Target RTOS")
# OpenBSW libraries only distinguish referenceApp/unitTest builds.
set(BUILD_EXECUTABLE
    "referenceApp"
    CACHE STRING "OpenBSW build flavour")

string(TOLOWER "${BUILD_TARGET_PLATFORM}" OPENBSW_TARGET)
set(OPENBSW_APP_DIR "${CMAKE_CURRENT_SOURCE_DIR}/app")
# Options.cmake of the board sets OPENBSW_PLATFORM (posix, s32k1xx), the OpenBSW
# platform folder; the board folder in app/platforms is the lower-case target name.
include(${OPENBSW_APP_DIR}/platforms/${OPENBSW_TARGET}/Options.cmake)
set(OPENBSW_PLATFORM_DIR "${OPENBSW_DIR}/platforms/${OPENBSW_PLATFORM}")

if (BUILD_TARGET_RTOS STREQUAL "FREERTOS")
    add_compile_definitions(SUPPORT_FREERTOS)
elseif (BUILD_TARGET_RTOS STREQUAL "THREADX")
    add_compile_definitions(SUPPORT_THREADX)
endif ()

get_cmake_property(_all_vars VARIABLES)
foreach (var ${_all_vars})
    if (var MATCHES "^PLATFORM_SUPPORT_" OR var MATCHES "^PLATFORM_CAN")
        if (${var})
            add_compile_definitions(${var}=1)
            message(STATUS "${var} ON")
        endif ()
    endif ()
endforeach ()

project(
    "OpenBSW zonal diagnostic gateway"
    VERSION 0.1.0
    LANGUAGES C CXX ASM)

list(APPEND CMAKE_MODULE_PATH "${OPENBSW_DIR}/cmake/modules")

add_compile_options(
    "$<$<COMPILE_LANG_AND_ID:CXX,GNU>:-Wno-error=stringop-overflow;-Wno-error=maybe-uninitialized>"
)

set(INCLUDE_OPENBSW_LIBS_BSP
    ON
    CACHE BOOL "Include openbsw/libs/bsp/ in build")
add_subdirectory(${OPENBSW_DIR}/platforms ${CMAKE_BINARY_DIR}/openbsw/platforms
                 EXCLUDE_FROM_ALL)
add_subdirectory(${OPENBSW_DIR}/libs ${CMAKE_BINARY_DIR}/openbsw/libs
                 EXCLUDE_FROM_ALL)
target_include_directories(etl BEFORE INTERFACE app/etl_profile)

# OpenBSW platforms/s32k1xx/bsp/bspMcu adds CMSIS relative to CMAKE_SOURCE_DIR,
# which is only right when OpenBSW is the top-level project; add the real paths.
if (TARGET bspMcu)
    target_include_directories(
        bspMcu PUBLIC ${OPENBSW_DIR}/libs/3rdparty/cmsis
                      ${OPENBSW_DIR}/libs/3rdparty/cmsis/m-profile)
endif ()

# The upstream contribution libs/bsw/transportRouter is built from OpenBSW/contrib, so the
# gateway runs exactly the code proposed to OpenBSW.
add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/../contrib/libs/bsw/transportRouter
                 ${CMAKE_BINARY_DIR}/contrib/transportRouter)
add_subdirectory(lib)
add_subdirectory(app)
