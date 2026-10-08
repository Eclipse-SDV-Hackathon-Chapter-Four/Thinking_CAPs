// SPDX-License-Identifier: Apache-2.0
// Host unit tests of the gateway units: RoutingTable (DD-04), NodeMonitor (DD-06),
// GatewayIdentity (DD-08) and the extended DTC store (DD-07).

#include "gateway/GatewayIdentity.h"
#include "gateway/GatewayLogger.h"
#include "gateway/NodeMonitor.h"
#include "gateway/RoutingConfig.h"
#include "gateway/RoutingTable.h"
#include "uds/DemoDtcManager.h"

#include <gtest/gtest.h>

#include <string>
#include <vector>

DEFINE_LOGGER_COMPONENT(GATEWAY)

namespace
{
using ::gateway::Route;
using ::gateway::RoutingTable;
using ::gateway::Transport;
using Error = RoutingTable::Error;

RoutingTable::Addresses const ADDRESSES{0x1010U, 0xE400U, 0x7DFU, 0x0E00U, 0x0EFFU};

Route route(uint16_t address, uint32_t request, uint32_t response)
{
    return Route{address, "r", Transport::DOCAN, request, response, 150U, 5100U, 4095U, 0xC14000U};
}

Error validate(std::vector<Route> const& routes, size_t& bad)
{
    RoutingTable const table(ADDRESSES, ::etl::span<Route const>(routes.data(), routes.size()));
    return table.validate(bad);
}

// --- RoutingTable ------------------------------------------------------------------------

TEST(RoutingTable, generatedConfigurationIsValid)
{
    RoutingTable const table(ADDRESSES, ::etl::span<Route const>(::gateway::config::ROUTES));
    size_t bad = 0U;
    EXPECT_EQ(Error::NONE, table.validate(bad));
    EXPECT_EQ(RoutingTable::INVALID_INDEX, bad);
    EXPECT_EQ(0U, table.indexOf(0x1020U));
    EXPECT_EQ(1U, table.indexOf(0x1030U));
    EXPECT_EQ(RoutingTable::INVALID_INDEX, table.indexOf(0x1099U));
    EXPECT_EQ(nullptr, table.find(0x1099U));
    EXPECT_EQ(0x7E1U, table.find(0x1020U)->requestCanId);
    EXPECT_TRUE(table.isTesterAddress(0x0E80U));
    EXPECT_FALSE(table.isTesterAddress(0x1010U));
}

TEST(RoutingTable, invalidTablesNameTheOffendingRoute)
{
    struct Case
    {
        std::vector<Route> routes;
        Error error;
        size_t bad;
    };
    Route timing = route(0x1030U, 0x7E2U, 0x7EAU);
    timing.p2Ms  = 0U;
    Route late   = route(0x1030U, 0x7E2U, 0x7EAU);
    late.p2Ms    = 6000U;
    Route length = route(0x1030U, 0x7E2U, 0x7EAU);
    length.maxLength = 4096U;
    Route empty = route(0x1030U, 0x7E2U, 0x7EAU);
    empty.maxLength = 0U;
    std::vector<Case> const cases = {
        {{}, Error::EMPTY, RoutingTable::INVALID_INDEX},
        {{route(0x1020U, 0x7E1U, 0x7E9U), route(0x1010U, 0x7E2U, 0x7EAU)}, Error::ADDRESS_CONFLICT, 1U},
        {{route(0xE400U, 0x7E1U, 0x7E9U)}, Error::ADDRESS_CONFLICT, 0U},
        {{route(0x0E44U, 0x7E1U, 0x7E9U)}, Error::ADDRESS_CONFLICT, 0U},
        {{route(0x1020U, 0x1F1U, 0x7E9U)}, Error::CAN_ID_OUT_OF_RANGE, 0U},
        {{route(0x1020U, 0x7E1U, 0x7F0U)}, Error::CAN_ID_OUT_OF_RANGE, 0U},
        {{route(0x1020U, 0x7E1U, 0x7E1U)}, Error::DUPLICATE_CAN_ID, 0U},
        {{route(0x1020U, 0x7DFU, 0x7E9U)}, Error::DUPLICATE_CAN_ID, 0U},
        {{route(0x1020U, 0x7E1U, 0x7DFU)}, Error::DUPLICATE_CAN_ID, 0U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), timing}, Error::INVALID_TIMING, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), late}, Error::INVALID_TIMING, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), length}, Error::INVALID_LENGTH, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), empty}, Error::INVALID_LENGTH, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), route(0x1020U, 0x7E2U, 0x7EAU)}, Error::DUPLICATE_ADDRESS, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), route(0x1030U, 0x7E1U, 0x7EAU)}, Error::DUPLICATE_CAN_ID, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), route(0x1030U, 0x7E9U, 0x7EAU)}, Error::DUPLICATE_CAN_ID, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), route(0x1030U, 0x7E2U, 0x7E1U)}, Error::DUPLICATE_CAN_ID, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), route(0x1030U, 0x7E2U, 0x7E9U)}, Error::DUPLICATE_CAN_ID, 1U},
    };
    for (Case const& c : cases)
    {
        size_t bad = 0U;
        EXPECT_EQ(c.error, validate(c.routes, bad));
        EXPECT_EQ(c.bad, bad);
        EXPECT_STRNE("unknown", RoutingTable::errorText(c.error));
    }
    RoutingTable::Addresses badFunctional = ADDRESSES;
    badFunctional.functionalCanId         = 0x700U;
    std::vector<Route> const one          = {route(0x1020U, 0x7E1U, 0x7E9U)};
    RoutingTable const table(badFunctional, ::etl::span<Route const>(one.data(), one.size()));
    size_t bad = 0U;
    EXPECT_EQ(Error::CAN_ID_OUT_OF_RANGE, table.validate(bad));
    EXPECT_STREQ("ok", RoutingTable::errorText(Error::NONE));
    EXPECT_STREQ("unknown", RoutingTable::errorText(static_cast<Error>(0xFFU)));
}

// --- NodeMonitor ---------------------------------------------------------------------------

class SinkSpy : public ::gateway::IDtcSink
{
public:
    void registerDtc(uint32_t dtc) override { events.push_back("register " + std::to_string(dtc)); }
    void setFailed(uint32_t dtc) override { events.push_back("failed " + std::to_string(dtc)); }
    void setPassed(uint32_t dtc) override { events.push_back("passed " + std::to_string(dtc)); }

    std::vector<std::string> events;
};

TEST(NodeMonitor, registersEveryRouteDtc)
{
    RoutingTable const table(ADDRESSES, ::etl::span<Route const>(::gateway::config::ROUTES));
    SinkSpy sink;
    ::gateway::NodeMonitor monitor(table, sink);
    monitor.init();
    EXPECT_EQ((std::vector<std::string>{"register 12664832", "register 12665088"}), sink.events);
}

TEST(NodeMonitor, threeConsecutiveTimeoutsSetTheDtcOnceAndAResponsePassesIt)
{
    RoutingTable const table(ADDRESSES, ::etl::span<Route const>(::gateway::config::ROUTES));
    SinkSpy sink;
    ::gateway::NodeMonitor monitor(table, sink);
    monitor.routeTimedOut(1U);
    monitor.routeTimedOut(1U);
    EXPECT_FALSE(monitor.isNotResponding(1U));
    EXPECT_TRUE(sink.events.empty());
    monitor.routeTimedOut(1U);
    EXPECT_TRUE(monitor.isNotResponding(1U));
    monitor.routeTimedOut(1U); // already failed: reported once
    EXPECT_EQ((std::vector<std::string>{"failed 12665088"}), sink.events);
    monitor.routeResponded(1U);
    EXPECT_FALSE(monitor.isNotResponding(1U));
    EXPECT_EQ("passed 12665088", sink.events.back());
}

TEST(NodeMonitor, aResponseResetsTheCount)
{
    RoutingTable const table(ADDRESSES, ::etl::span<Route const>(::gateway::config::ROUTES));
    SinkSpy sink;
    ::gateway::NodeMonitor monitor(table, sink);
    monitor.routeTimedOut(0U);
    monitor.routeTimedOut(0U);
    monitor.routeResponded(0U);
    monitor.routeTimedOut(0U);
    monitor.routeTimedOut(0U);
    EXPECT_FALSE(monitor.isNotResponding(0U));
    EXPECT_EQ((std::vector<std::string>{"passed 12664832"}), sink.events);
}

TEST(NodeMonitor, unknownRoutesAreIgnored)
{
    RoutingTable const table(ADDRESSES, ::etl::span<Route const>(::gateway::config::ROUTES));
    SinkSpy sink;
    ::gateway::NodeMonitor monitor(table, sink);
    monitor.routeTimedOut(7U);
    monitor.routeResponded(7U);
    EXPECT_FALSE(monitor.isNotResponding(7U));
    EXPECT_TRUE(sink.events.empty());
}

// --- GatewayIdentity ------------------------------------------------------------------------

std::string text(::etl::span<uint8_t const> const bytes)
{
    return std::string(bytes.begin(), bytes.end());
}

TEST(GatewayIdentity, identificationDataComesFromTheConfiguration)
{
    EXPECT_EQ("TCAPSZONALGW00001", text(::gateway::identity::vin()));
    EXPECT_EQ("ZGW-POSIX-0001", text(::gateway::identity::ecuSerial()));
    std::string const version = text(::gateway::identity::softwareVersion());
    EXPECT_EQ(0U, version.find("zgw "));
    EXPECT_NE(std::string::npos, version.find(" obsw "));
    EXPECT_NE(std::string::npos, version.find(std::string(" rt ") + ::gateway::config::ROUTING_TABLE_HASH));
    EXPECT_EQ(version, text(::gateway::identity::softwareVersion())); // stable
}

// --- DTC store (extended DemoDtcManager) ------------------------------------------------------

TEST(DtcStore, registeredDtcsAreSupportedWithTestNotCompleted)
{
    ::uds::DemoDtcManager dtcs;
    dtcs.registerDtc(0xC14000U);
    dtcs.registerDtc(0xC14000U); // once
    uint8_t buffer[16] = {};
    EXPECT_EQ(1U, dtcs.getSupportedDtcs(buffer));
    EXPECT_EQ(0x10U, buffer[3]);
    EXPECT_EQ(0U, dtcs.getCountByStatusMask(0x09U));
}

TEST(DtcStore, failedPassedAndClearFollowIso14229StatusBits)
{
    ::uds::DemoDtcManager dtcs;
    dtcs.registerDtc(0xC14100U);
    dtcs.reportFault(0xC14100U);
    uint8_t buffer[16] = {};
    ASSERT_EQ(1U, dtcs.getDtcsByStatusMask(0xFFU, buffer));
    EXPECT_EQ(0x0FU, buffer[3]); // testFailed, thisCycle, pending, confirmed
    dtcs.reportPassed(0xC14100U);
    ASSERT_EQ(1U, dtcs.getDtcsByStatusMask(0xFFU, buffer));
    EXPECT_EQ(0x0EU, buffer[3]); // testFailed cleared, history kept
    dtcs.clearByGroup(0xFFFFFFU);
    EXPECT_EQ(0U, dtcs.getCountByStatusMask(0x0FU));
    EXPECT_EQ(1U, dtcs.getSupportedDtcs(buffer)); // still supported
    dtcs.reportFault(0xC14100U);
    dtcs.clearByGroup(0xC14100U);
    EXPECT_EQ(0U, dtcs.getCountByStatusMask(0x0FU));
}

TEST(DtcStore, dtcSettingOffIgnoresResults)
{
    ::uds::DemoDtcManager dtcs;
    dtcs.registerDtc(0xC14000U);
    dtcs.setDtcSettingEnabled(false);
    dtcs.reportFault(0xC14000U);
    dtcs.reportPassed(0xC14000U);
    EXPECT_EQ(0U, dtcs.getCountByStatusMask(0x0FU));
    EXPECT_FALSE(dtcs.isDtcSettingEnabled());
}

} // namespace
