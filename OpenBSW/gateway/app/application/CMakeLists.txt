# SPDX-License-Identifier: Apache-2.0
#
# Derived from Eclipse OpenBSW executables/referenceApp/application (Apache-2.0).
# Modified for the zonal diagnostic gateway: no demo, SOME/IP, PDU routing,
# storage, middleware or Rust components (SWR-031).

add_executable(
    openbsw-zonal-gw
    src/app/app.cpp
    src/console/console.cpp
    src/logger/logger.cpp
    src/systems/RuntimeSystem.cpp
    src/systems/SysAdminSystem.cpp
    src/systems/SafetySystem.cpp
    src/systems/TransportSystem.cpp
    src/systems/UdsSystem.cpp
    src/systems/EthernetSystem.cpp
    src/systems/DoIpServerSystem.cpp
    src/systems/DoIpClientSystem.cpp
    src/systems/DoCanSystem.cpp
    src/uds/DemoClearDtc.cpp
    src/uds/DemoDtcManager.cpp
    src/uds/DemoReadDtcInfo.cpp
    src/uds/GatewayDiagJobs.cpp
    src/main.cpp)

set_target_properties(openbsw-zonal-gw PROPERTIES SUFFIX ".elf")

# embedded targets: link with the board's generated linker script
if (TARGET startUp)
    get_target_property(LINKER_SCRIPT startUp PROP_LINKER_SCRIPT)
    if (DEFINED LINKER_SCRIPT)
        target_link_options(openbsw-zonal-gw PRIVATE -T ${LINKER_SCRIPT})
    endif ()
endif ()

target_include_directories(openbsw-zonal-gw PRIVATE include)

target_link_libraries(
    openbsw-zonal-gw
    PRIVATE asyncBinding
            asyncConsole
            bspMcu
            configuration
            etl
            etlImpl
            lifecycle
            consoleCommands
            logger
            printf
            loggerIntegration
            main
            stdioConsoleInput
            osRtos
            asyncRtosImpl
            util
            time
            runtime
            safeLifecycle
            safeUtils
            safeWatchdog
            bspUart
            socBsp
            transport
            zonalGateway
            uds
            udsConfigurationImpl
            cpp2can
            docan
            cpp2ethernet
            lwipSocket
            lwipcore
            ethConfiguration
            doip
            doipClient)
