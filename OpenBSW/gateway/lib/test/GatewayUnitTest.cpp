// SPDX-License-Identifier: Apache-2.0
// Host unit tests of the gateway units: RoutingTable (DD-04), NodeMonitor (DD-06),
// GatewayIdentity (DD-08), the extended DTC store (DD-07), TransmitPacer (DD-20) and
// ReachabilityProbe (DD-22).

#include "gateway/GatewayIdentity.h"
#include "gateway/GatewayLogger.h"
#include "gateway/NodeMonitor.h"
#include "gateway/RoutingConfig.h"
#include "gateway/ReachabilityProbe.h"
#include "gateway/RoutingTable.h"
#include "gateway/TransmitPacer.h"
#include "uds/DemoDtcManager.h"

#include <gtest/gtest.h>
#include <transport/ITransportMessageProvidingListener.h>

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
    return Route{
        address, "r", Transport::DOCAN, request, response, 0U, 150U, 5100U, 4095U, 0xC14000U};
}

Route doipRoute(uint16_t address, uint32_t ip)
{
    return Route{address, "e", Transport::DOIP, 0U, 0U, ip, 150U, 5100U, 4095U, 0xC14200U};
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
    EXPECT_EQ(2U, table.indexOf(0x1040U));
    EXPECT_EQ(Transport::DOIP, table.find(0x1040U)->transport);
    EXPECT_EQ(0xC0A8001EU, table.find(0x1040U)->ipAddress); // 192.168.0.30
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
        // DoIP routes (SWR-010): a unicast IPv4 address, one route per DoIP entity
        {{doipRoute(0x1040U, 0U)}, Error::INVALID_IP_ADDRESS, 0U},
        {{doipRoute(0x1040U, 0xFFFFFFFFU)}, Error::INVALID_IP_ADDRESS, 0U},
        {{doipRoute(0x1040U, 0x7F000001U)}, Error::INVALID_IP_ADDRESS, 0U},
        {{doipRoute(0x1040U, 0xE0000001U)}, Error::INVALID_IP_ADDRESS, 0U},
        {{doipRoute(0x1040U, 0xC0A8001EU), doipRoute(0x1050U, 0xC0A8001EU)}, Error::DUPLICATE_IP_ADDRESS, 1U},
        {{doipRoute(0x1040U, 0xC0A8001EU), doipRoute(0x1040U, 0xC0A8001FU)}, Error::DUPLICATE_ADDRESS, 1U},
        {{route(0x1020U, 0x7E1U, 0x7E9U), doipRoute(0x1020U, 0xC0A8001EU)}, Error::DUPLICATE_ADDRESS, 1U},
        {{doipRoute(0x1010U, 0xC0A8001EU)}, Error::ADDRESS_CONFLICT, 0U},
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
    EXPECT_EQ(
        (std::vector<std::string>{"register 12664832", "register 12665088", "register 12665344"}),
        sink.events);
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

// --- TransmitPacer ------------------------------------------------------------------------

TEST(TransmitPacer, firstFrameIsSentAtOnce)
{
    ::gateway::TransmitPacer const pacer(3000U);
    EXPECT_EQ(0U, pacer.delayUs(123456U));
    EXPECT_EQ(3000U, pacer.minGapUs());
}

TEST(TransmitPacer, nextFrameWaitsForTheGap)
{
    ::gateway::TransmitPacer pacer(3000U);
    pacer.sent(1000U);
    EXPECT_EQ(3000U, pacer.delayUs(1000U));
    EXPECT_EQ(1000U, pacer.delayUs(3000U));
    EXPECT_EQ(1U, pacer.delayUs(3999U));
    EXPECT_EQ(0U, pacer.delayUs(4000U));
    EXPECT_EQ(0U, pacer.delayUs(90000U));
}

TEST(TransmitPacer, gapWorksAcrossClockWrapAround)
{
    ::gateway::TransmitPacer pacer(3000U);
    pacer.sent(0xFFFFFF00U);
    EXPECT_EQ(3000U - 0x200U, pacer.delayUs(0x00000100U));
    EXPECT_EQ(0U, pacer.delayUs(0x00000B00U));
}

TEST(TransmitPacer, frameRateStaysWithinTheBusLoadBudget)
{
    // SWR-032: in one second at most 334 frames (t = 0, 3 ms, ..., 999 ms) of 135 bits each,
    // 45090 bits = 9 % of 500 kbit/s; the stack asks again 100 us after each frame
    ::gateway::TransmitPacer pacer(3000U);
    uint32_t now   = 0U;
    uint32_t count = 0U;
    for (now += pacer.delayUs(now); now < 1000000U; now += pacer.delayUs(now))
    {
        pacer.sent(now);
        ++count;
        now += 100U;
    }
    EXPECT_EQ(334U, count);
    EXPECT_LE(count * 135U, 50000U);
}

// --- ReachabilityProbe ---------------------------------------------------------------------

using ::gateway::ReachabilityProbe;
using ::transport::ITransportMessageProcessedListener;
using ::transport::TransportMessage;
using ProbeResult = ReachabilityProbe::Result;

/** Router stand-in: hands out buffers and records the requests of the probe. */
class RouterFake : public ::transport::ITransportMessageProvidingListener
{
public:
    ErrorCode getTransportMessage(
        uint8_t, uint16_t source, uint16_t target, uint16_t, ::etl::span<uint8_t const> const&,
        TransportMessage*& message) override
    {
        message = nullptr;
        if (target == busyTarget)
        {
            return ErrorCode::TPMSG_NO_MSG_AVAILABLE;
        }
        sources.push_back(source);
        TransportMessage& slot = messages[used++];
        slot.init(buffers[used - 1U], sizeof(buffers[0]));
        message = &slot;
        return ErrorCode::TPMSG_OK;
    }

    void releaseTransportMessage(TransportMessage&) override { ++released; }

    ReceiveResult messageReceived(
        uint8_t, TransportMessage& message, ITransportMessageProcessedListener* listener) override
    {
        requests.push_back(message.getTargetId());
        payloads.push_back(std::vector<uint8_t>(
            message.getPayload(), message.getPayload() + message.getPayloadLength()));
        delivered.push_back(listener);
        return (message.getTargetId() == refusedTarget) ? ReceiveResult::RECEIVED_ERROR
                                                         : ReceiveResult::RECEIVED_NO_ERROR;
    }

    void dump() override {}

    uint16_t busyTarget    = 0U;
    uint16_t refusedTarget = 0U;
    size_t used            = 0U;
    int released           = 0;
    TransportMessage messages[4];
    uint8_t buffers[4][8];
    std::vector<uint16_t> sources;
    std::vector<uint16_t> requests;
    std::vector<std::vector<uint8_t>> payloads;
    std::vector<ITransportMessageProcessedListener*> delivered;
};

/** Node-side listener of a forwarded response. */
class ResponseReleased : public ITransportMessageProcessedListener
{
public:
    void transportMessageProcessed(TransportMessage&, ProcessingResult) override { ++count; }

    int count = 0;
};

class ReachabilityProbeTest : public ::testing::Test
{
public:
    ReachabilityProbeTest()
    : table(ADDRESSES, ::etl::span<Route const>(::gateway::config::ROUTES))
    , probe(6U, 0x0EFEU, table, 2000U)
    {
        probe.fProvidingListenerHelper.fpMessageProvider = &router;
        probe.fProvidingListenerHelper.fpMessageListener = &router;
    }

    void answer(uint16_t node, std::vector<uint8_t> const& payload)
    {
        TransportMessage response;
        uint8_t buffer[8] = {};
        response.init(buffer, sizeof(buffer));
        response.setSourceAddress(node);
        response.setTargetAddress(0x0EFEU);
        response.setPayloadLength(static_cast<uint16_t>(payload.size()));
        (void)response.append(payload.data(), static_cast<uint16_t>(payload.size()));
        EXPECT_EQ(
            ::transport::AbstractTransportLayer::ErrorCode::TP_OK, probe.send(response, &released));
    }

    RoutingTable table;
    ReachabilityProbe probe;
    RouterFake router;
    ResponseReleased released;
};

TEST_F(ReachabilityProbeTest, sendsTesterPresentToEveryRouteFromTheProbeAddress)
{
    EXPECT_EQ(ProbeResult::NOT_STARTED, probe.result(0U, 0U));
    probe.start(1000U);
    EXPECT_EQ((std::vector<uint16_t>{0x1020U, 0x1030U, 0x1040U}), router.requests);
    EXPECT_EQ((std::vector<uint16_t>{0x0EFEU, 0x0EFEU, 0x0EFEU}), router.sources);
    EXPECT_EQ((std::vector<uint8_t>{0x3EU, 0x00U}), router.payloads[0]);
    EXPECT_TRUE(probe.running(1000U));
    EXPECT_EQ(3U, probe.routeCount());
    EXPECT_EQ(0x0EFEU, probe.testerAddress());
}

TEST_F(ReachabilityProbeTest, answersMarkNodesReachedAndSilentNodesTimeOut)
{
    probe.start(1000U);
    answer(0x1020U, {0x7EU, 0x00U});
    answer(0x1040U, {0x7FU, 0x3EU, 0x11U}); // a negative response also shows the node is there
    EXPECT_EQ(2, released.count);
    EXPECT_EQ(ProbeResult::REACHED, probe.result(0U, 1500U));
    EXPECT_EQ(ProbeResult::PENDING, probe.result(1U, 1500U));
    EXPECT_EQ(ProbeResult::REACHED, probe.result(2U, 1500U));
    EXPECT_TRUE(probe.running(2999U));
    EXPECT_FALSE(probe.running(3000U));
    EXPECT_EQ(ProbeResult::NOT_REACHED, probe.result(1U, 3000U));
    EXPECT_EQ(ProbeResult::NOT_STARTED, probe.result(ReachabilityProbe::MAX_ROUTES, 3000U));
}

TEST_F(ReachabilityProbeTest, probeEndsWhenEveryRouteHasAResult)
{
    probe.start(1000U);
    answer(0x1020U, {0x7EU, 0x00U});
    answer(0x1030U, {0x7EU, 0x00U});
    answer(0x1040U, {0x7EU, 0x00U});
    answer(0x1099U, {0x7EU, 0x00U}); // not a route: ignored, but released
    EXPECT_FALSE(probe.running(1100U));
    EXPECT_EQ(4, released.count);
}

TEST_F(ReachabilityProbeTest, busyRefusedAndUndeliveredRoutesAreNotReached)
{
    router.busyTarget    = 0x1020U;
    router.refusedTarget = 0x1030U;
    probe.start(1000U);
    EXPECT_EQ(ProbeResult::NOT_REACHED, probe.result(0U, 1000U));
    EXPECT_EQ(ProbeResult::NOT_REACHED, probe.result(1U, 1000U));
    EXPECT_EQ(1, router.released); // the refused request
    // the request to 0x1040 is reported as not delivered
    ASSERT_EQ(2U, router.delivered.size());
    router.delivered[1]->transportMessageProcessed(
        router.messages[1], ITransportMessageProcessedListener::ProcessingResult::PROCESSED_ERROR);
    EXPECT_EQ(ProbeResult::NOT_REACHED, probe.result(2U, 1000U));
    EXPECT_EQ(2, router.released);
    EXPECT_FALSE(probe.running(1000U));
}

TEST_F(ReachabilityProbeTest, deliveredRequestIsReleasedAndALateAnswerAfterRestartCounts)
{
    probe.start(1000U);
    router.delivered[0]->transportMessageProcessed(
        router.messages[0], ITransportMessageProcessedListener::ProcessingResult::PROCESSED_NO_ERROR);
    EXPECT_EQ(1, router.released);
    EXPECT_EQ(ProbeResult::PENDING, probe.result(0U, 1000U));
    answer(0x1020U, {0x7EU, 0x00U});
    answer(0x1020U, {0x7EU, 0x00U}); // a second answer changes nothing
    EXPECT_EQ(ProbeResult::REACHED, probe.result(0U, 1000U));
}

} // namespace
