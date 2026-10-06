# SPDX-License-Identifier: Apache-2.0
# ThreadX zonal lighting controller for the MXChip AZ3166 (STM32F412RG).
# Configure with: cmake -S az3166 -B build-az3166 -G Ninja \
#   -DCMAKE_TOOLCHAIN_FILE=az3166/cmake/arm-none-eabi.cmake
cmake_minimum_required(VERSION 3.20)
project(threadx_zonal_lights_az3166 VERSION 1.0.0 LANGUAGES C ASM)
include(FetchContent)

if(NOT CMAKE_C_COMPILER_ID STREQUAL "GNU" OR NOT CMAKE_SYSTEM_PROCESSOR STREQUAL "arm")
    message(FATAL_ERROR "Use -DCMAKE_TOOLCHAIN_FILE=cmake/arm-none-eabi.cmake")
endif()
set(ZONAL_TIMEOUT_MS 0 CACHE STRING "Input timeout in ms (0 holds the latest state)")

# Same immutable Eclipse ThreadX revision as the Linux controller (MIT licensed).
set(THREADX_REVISION b91b03b9e75fa523b17127f9e0eca09dca916459)
set(THREADX_ARCH cortex_m4 CACHE STRING "ThreadX architecture")
set(THREADX_TOOLCHAIN gnu CACHE STRING "ThreadX compiler")
set(TX_USER_FILE "${CMAKE_CURRENT_SOURCE_DIR}/src/tx_user.h" CACHE FILEPATH "ThreadX settings")
FetchContent_Declare(threadx
    GIT_REPOSITORY https://github.com/eclipse-threadx/threadx.git
    GIT_TAG ${THREADX_REVISION})
FetchContent_MakeAvailable(threadx)
execute_process(COMMAND git -C "${threadx_SOURCE_DIR}" rev-parse HEAD
    OUTPUT_VARIABLE THREADX_ACTUAL_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE
    COMMAND_ERROR_IS_FATAL ANY)
if(NOT THREADX_ACTUAL_REVISION STREQUAL THREADX_REVISION)
    message(FATAL_ERROR "ThreadX source does not match the pinned revision")
endif()
execute_process(COMMAND git -C "${threadx_SOURCE_DIR}" diff --quiet HEAD
    RESULT_VARIABLE THREADX_DIRTY)
if(NOT THREADX_DIRTY EQUAL 0)
    message(FATAL_ERROR "ThreadX tracked sources have local modifications")
endif()

set(WARNINGS -Wall -Wextra -Werror)
add_executable(threadx-zonal-lights-az3166
    src/startup.c
    src/tx_initialize_low_level.S
    src/board.c
    src/display.c
    src/slcan.c
    src/main.c
    ../src/lights_protocol.c
    third_party/ssd1306/font7x10.c)
set_target_properties(threadx-zonal-lights-az3166 PROPERTIES SUFFIX ".elf" C_STANDARD 11 C_EXTENSIONS ON)
# compat/ provides <linux/can.h> so the Linux lights_protocol.c builds unchanged.
target_include_directories(threadx-zonal-lights-az3166 PRIVATE src compat ../src)
target_compile_definitions(threadx-zonal-lights-az3166 PRIVATE
    THREADX_REVISION="${THREADX_REVISION}" ZONAL_VERSION="${PROJECT_VERSION}"
    ZONAL_TIMEOUT_MS=${ZONAL_TIMEOUT_MS})
target_compile_options(threadx-zonal-lights-az3166 PRIVATE
    $<$<COMPILE_LANGUAGE:C>:${WARNINGS}> -Os -g)
target_link_options(threadx-zonal-lights-az3166 PRIVATE
    -T${CMAKE_CURRENT_SOURCE_DIR}/src/az3166.ld
    -Wl,-Map=$<TARGET_FILE_DIR:threadx-zonal-lights-az3166>/threadx-zonal-lights-az3166.map
    -Wl,--print-memory-usage)
target_link_libraries(threadx-zonal-lights-az3166 PRIVATE threadx)
add_custom_command(TARGET threadx-zonal-lights-az3166 POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:threadx-zonal-lights-az3166>
        $<TARGET_FILE_DIR:threadx-zonal-lights-az3166>/threadx-zonal-lights-az3166.bin
    COMMAND ${CMAKE_SIZE} $<TARGET_FILE:threadx-zonal-lights-az3166>
    VERBATIM)
