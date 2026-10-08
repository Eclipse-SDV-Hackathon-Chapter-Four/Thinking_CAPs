/********************************************************************************
 * Copyright (c) 2025 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Derived from Eclipse OpenBSW executables/referenceApp/application/src/app/app.cpp.
// Modified for the zonal diagnostic gateway: lifecycle limited to runtime, safety,
// CAN/Ethernet drivers, transport (ZonalRouter), DoCAN, DoIP, UDS and sysadmin.
// No demo, SOME/IP, PDU routing, storage, middleware or Rust components (SWR-031).

#include "app/app.h"
#include "bsp/Uart.h"
#include "busid/BusId.h"
#include "console/console.h"
#include "lifecycle/StaticBsp.h"
#include "logger/logger.h"
#include "reset/softwareSystemReset.h"
#include "systems/DoCanSystem.h"
#include "systems/DoIpServerSystem.h"
#include "systems/EthernetSystem.h"
#include "systems/RuntimeSystem.h"
#include "systems/SafetySystem.h"
#include "systems/SysAdminSystem.h"
#include "systems/TransportSystem.h"
#include "systems/UdsSystem.h"
#include "uds/GatewayDiagJobs.h"

#include <app/appConfig.h>
#include <async/AsyncBinding.h>
#include <etl/alignment.h>
#include <etl/print.h>
#include <gateway/GatewayIdentity.h>
#include <gateway/NodeMonitor.h>
#include <lifecycle/LifecycleLogger.h>
#include <lifecycle/LifecycleManager.h>
#include <systems/ICanSystem.h>
#include <systems/IEthernetDriverSystem.h>
#include <time/TimestampProvider.h>

#include <cstdint>

alignas(32)::async::internal::Stack<safety_task_stackSize> safetyStack;

namespace systems
{
extern ::can::ICanSystem& getCanSystem();
extern ::ethernet::IEthernetDriverSystem& getEthernetSystem();
} // namespace systems

namespace platform
{
extern void platformLifecycleAdd(::lifecycle::LifecycleManager& lifecycleManager, uint8_t level);
extern StaticBsp& getStaticBsp();
} // namespace platform

namespace app
{
using bsp::Uart;
using ::util::logger::LIFECYCLE;
using ::util::logger::Logger;

using AsyncAdapter        = ::async::AsyncBinding::AdapterType;
using AsyncRuntimeMonitor = ::async::AsyncBinding::RuntimeMonitorType;
using AsyncContextHook    = ::async::AsyncBinding::ContextHookType;

constexpr size_t MaxNumComponents         = 16;
constexpr size_t MaxNumLevels             = 9;
constexpr size_t MaxNumComponentsPerLevel = MaxNumComponents;

using LifecycleManager = ::lifecycle::declare::
    LifecycleManager<MaxNumComponents, MaxNumLevels, MaxNumComponentsPerLevel>;

char const* const isrGroupNames[ISR_GROUP_COUNT] = {"test"};

AsyncRuntimeMonitor runtimeMonitor{
    AsyncContextHook::InstanceType::GetNameType::create<&AsyncAdapter::getTaskName>(),
    isrGroupNames};

LifecycleManager lifecycleManager{
    TASK_SYSADMIN,
    ::lifecycle::LifecycleManager::GetTimestampType::create<
        &::bsw::time::TimestampProvider::getTimestampUs32Bit>()};

::etl::typed_storage<::systems::RuntimeSystem> runtimeSystem;
::etl::typed_storage<::systems::SysAdminSystem> sysAdminSystem;
::etl::typed_storage<::systems::SafetySystem> safetySystem;
::etl::typed_storage<::systems::EthernetSystem> ethernetSystem;
::etl::typed_storage<::transport::TransportSystem> transportSystem;
::etl::typed_storage<::docan::DoCanSystem> doCanSystem;
::etl::typed_storage<::doip::DoIpServerSystem> doipServerSystem;
::etl::typed_storage<::uds::UdsSystem> udsSystem;
::etl::typed_storage<::uds::DtcSink> dtcSink;
::etl::typed_storage<::gateway::NodeMonitor> nodeMonitor;
::etl::typed_storage<::uds::ReadRoutingTable> readRoutingTable;
::etl::typed_storage<::uds::ReadRoutingStatistics> readRoutingStatistics;

// VIN for DoIP vehicle announcement and identification responses (SWR-001).
void provideVin(::etl::span<uint8_t, ::doip::VIN_LENGTH> const vin)
{
    auto const configured = ::gateway::identity::vin();
    for (size_t i = 0U; i < vin.size(); ++i)
    {
        vin[i] = (i < configured.size()) ? configured[i] : static_cast<uint8_t>(' ');
    }
}

// Releases a disconnected tester's pending requests in the router (SWR-041).
class TesterConnectionMonitor : public ::doip::IDoIpServerConnectionStateCallback
{
public:
    void connectionRoutingActive(
        uint16_t const /* sourceAddress */,
        ::doip::DoIpTcpConnection::ConnectionType const /* type */) override
    {}

    void connectionClosed(uint16_t const sourceAddress) override
    {
        transportSystem->getRouter().releaseTester(sourceAddress);
    }
};

TesterConnectionMonitor testerConnectionMonitor;

class LifecycleMonitor : private ::lifecycle::ILifecycleListener
{
public:
    explicit LifecycleMonitor(LifecycleManager& manager) { manager.addLifecycleListener(*this); }

    bool isReadyForReset() const { return _isReadyForReset; }

private:
    void lifecycleLevelReached(
        uint8_t const level,
        ::lifecycle::ILifecycleComponent::Transition::Type const /* transition */) override
    {
        if (0 == level)
        {
            _isReadyForReset = true;
        }
    }

    bool _isReadyForReset = false;
};

LifecycleMonitor lifecycleMonitor(lifecycleManager);

class IdleHandler : private ::async::RunnableType
{
public:
    void init()
    {
        ::logger::init();
        ::console::init();
        ::console::enable();
    }

    void start() { ::async::execute(AsyncAdapter::TASK_IDLE, *this); }

private:
    void execute() override
    {
        ::logger::run();
        ::console::run();
        if (lifecycleMonitor.isReadyForReset())
        {
            shutdown();
        }
        else
        {
            ::async::execute(AsyncAdapter::TASK_IDLE, *this);
        }
    }

    void shutdown()
    {
        Logger::info(LIFECYCLE, "Lifecycle shutdown complete");
        ::logger::flush();
        softwareSystemReset();
    }
};

IdleHandler idleHandler;

void startApp();

void staticInit()
{
    Uart::getInstance(Uart::Id::TERMINAL).init();
    Uart::getInstance(Uart::Id::TERMINAL).waitForTxReady();
}

void run()
{
    staticInit();
    etl::print("openbsw-zonal-gw\r\n");
    idleHandler.init();
    AsyncAdapter::run(AsyncAdapter::StartAppFunctionType::create<&startApp>());
}

void startApp()
{
    /* runlevel 1 */
    ::platform::platformLifecycleAdd(lifecycleManager, 1U);
    lifecycleManager.addComponent(
        "runtime", runtimeSystem.create(TASK_BACKGROUND, runtimeMonitor), 1U);
    lifecycleManager.addComponent("safety", safetySystem.create(TASK_SAFETY, lifecycleManager), 1U);

    /* runlevel 2: CAN and Ethernet drivers */
    ::platform::platformLifecycleAdd(lifecycleManager, 2U);

    /* runlevel 3 */
    ::platform::platformLifecycleAdd(lifecycleManager, 3U);

    /* runlevel 4: router */
    auto& transport = transportSystem.create(TASK_UDS);
    lifecycleManager.addComponent("transport", transport, 4U);

    /* runlevel 5: ISO-TP and IP stack */
    lifecycleManager.addComponent(
        "docan", doCanSystem.create(*transportSystem, ::systems::getCanSystem(), TASK_CAN), 5U);
    lifecycleManager.addComponent(
        "ethernet", ethernetSystem.create(TASK_ETHERNET, ::systems::getEthernetSystem()), 5U);

    /* runlevel 6: gateway UDS server, before DoIP announces the gateway (SWR-044) */
    auto& uds = udsSystem.create(lifecycleManager, transport, TASK_UDS, LOGICAL_ADDRESS);
    // node monitor -> fault memory (SWR-024, SWR-025); routing DIDs FD00/FD01 (SWR-022/023)
    auto& monitor = nodeMonitor.create(transport.getRoutingTable(), dtcSink.create(uds.getDtcManager()));
    monitor.init();
    transport.getRouter().setObserver(&monitor);
    uds.addJob(readRoutingTable.create(transport.getRoutingTable()));
    uds.addJob(readRoutingStatistics.create(transport.getRoutingTable(), transport.getStatistics()));
    lifecycleManager.addComponent("uds", uds, 6U);

    /* runlevel 7: DoIP server and vehicle announcement */
    auto& doip = doipServerSystem.create(
        transport,
        ::shed::get<::systems::NetifConfigRegistry>(ethernetSystem->netifs).value,
        TASK_ETHERNET,
        ::busid::ETH_0,
        LOGICAL_ADDRESS,
        ::ethX::MAC_ADDRESS,
        ::shed::get<::ip::NetworkInterfaceConfig>(ethernetSystem->netifs)[0]
            .broadcastAddress()); // ETH0
    doip.setConnectionStateCallback(testerConnectionMonitor);
    doip.setVinCallback(::doip::DoIpServerSystem::VinCallbackType::create<&provideVin>());
    lifecycleManager.addComponent("doipServer", doip, 7U);

    /* runlevel 8 */
    lifecycleManager.addComponent(
        "sysadmin", sysAdminSystem.create(TASK_SYSADMIN, lifecycleManager), 8U);

    /* runlevel 9 */
    ::platform::platformLifecycleAdd(lifecycleManager, 9U);

    lifecycleManager.transitionToLevel(MaxNumLevels);

    runtimeMonitor.start();
    idleHandler.start();
}

using TimerTask = AsyncAdapter::TimerTask<1024 * 1>;
TimerTask timerTask{"timer"};

using IdleTask = AsyncAdapter::IdleTask<1024 * 2>;
IdleTask idleTask{"idle"};

using UdsTask = AsyncAdapter::Task<TASK_UDS, 1024 * 2>;
UdsTask udsTask{"uds"};

using SysadminTask = AsyncAdapter::Task<TASK_SYSADMIN, 1024 * 2>;
SysadminTask sysadminTask{"sysadmin"};

using CanTask = AsyncAdapter::Task<TASK_CAN, 1024 * 2>;
CanTask canTask{"can"};

using EthernetTask = AsyncAdapter::Task<TASK_ETHERNET, 1024 * 2>;
EthernetTask ethernetTask{"ethernet"};

using BspTask = AsyncAdapter::Task<TASK_BSP, 1024 * 2>;
BspTask bspTask{"bsp"};

// Unused by the gateway; kept so the async task table matches asyncCoreConfiguration.
using DemoTask = AsyncAdapter::Task<TASK_DEMO, 1024 * 2>;
DemoTask demoTask{"demo"};

using BackgroundTask = AsyncAdapter::Task<TASK_BACKGROUND, 1024 * 2>;
BackgroundTask backgroundTask{"background"};

using SafetyTask = AsyncAdapter::TaskStack<TASK_SAFETY>;
SafetyTask safetyTask{"safety", safetyStack};

AsyncContextHook contextHook{runtimeMonitor};

} // namespace app
