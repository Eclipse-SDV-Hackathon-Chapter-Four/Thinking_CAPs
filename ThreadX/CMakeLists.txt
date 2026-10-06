cmake_minimum_required(VERSION 3.20)
project(threadx_zonal_lights VERSION 1.0.0 LANGUAGES C)
include(FetchContent)
include(CTest)
find_package(Threads REQUIRED)

# Eclipse ThreadX v6.5.1.202602a_rel, MIT licensed. Keep this immutable.
set(THREADX_REVISION b91b03b9e75fa523b17127f9e0eca09dca916459)
set(THREADX_ARCH linux CACHE STRING "ThreadX architecture")
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
target_compile_definitions(threadx PUBLIC TX_LINUX_MULTI_CORE)

add_library(lights_protocol src/lights_protocol.c)
target_include_directories(lights_protocol PUBLIC src)
target_compile_options(lights_protocol PRIVATE -Wall -Wextra -Werror)
add_executable(threadx-zonal-lights src/main.c)
target_compile_definitions(threadx-zonal-lights PRIVATE
    THREADX_REVISION="${THREADX_REVISION}" ZONAL_VERSION="${PROJECT_VERSION}")
target_compile_options(threadx-zonal-lights PRIVATE -Wall -Wextra -Werror)
target_link_libraries(threadx-zonal-lights PRIVATE lights_protocol threadx Threads::Threads rt)
if(BUILD_TESTING)
    add_executable(test_lights_protocol tests/test_protocol.c)
    target_link_libraries(test_lights_protocol PRIVATE lights_protocol)
    target_compile_options(test_lights_protocol PRIVATE -Wall -Wextra -Werror)
    add_test(NAME lights_protocol COMMAND test_lights_protocol)
    # Portable SLCAN codec of the AZ3166 UART-CAN port (az3166/).
    add_executable(test_slcan az3166/tests/test_slcan.c az3166/src/slcan.c)
    target_include_directories(test_slcan PRIVATE az3166/src)
    target_compile_options(test_slcan PRIVATE -Wall -Wextra -Werror)
    add_test(NAME slcan_codec COMMAND test_slcan)
    add_executable(test_slcan_edge az3166/tests/test_slcan_edge.c az3166/src/slcan.c)
    target_include_directories(test_slcan_edge PRIVATE az3166/src)
    target_compile_options(test_slcan_edge PRIVATE -Wall -Wextra -Werror)
    add_test(NAME slcan_codec_edges COMMAND test_slcan_edge)
endif()
