// SPDX-License-Identifier: Apache-2.0
#pragma once

#include "gateway/RoutingTable.h"

#include <transport/AbstractTransportLayer.h>
#include <transport/ITransportMessageProcessedListener.h>
#include <transport/TransportMessage.h>

#include <etl/array.h>

#include <cstddef>
#include <cstdint>

namespace gateway
{
/**
 * Node reachability probe (SWR-026, DD-22).
 *
 * A transport layer on its own bus that acts as an internal tester: start() sends
 * TesterPresent (3E 00) through the router to every route of the routing table; any
 * diagnostic message a node sends back marks it as reached. A route that is busy, whose
 * delivery fails or that does not answer within the window counts as not reached.
 *
 * start() must run in the context in which the route transport layers may be called (the
 * Ethernet context of the gateway, because of the DoIP client).
 */
class ReachabilityProbe
: public ::transport::AbstractTransportLayer
, private ::transport::ITransportMessageProcessedListener
{
public:
    static constexpr size_t MAX_ROUTES = 16U;

    enum class Result : uint8_t
    {
        NOT_STARTED,
        PENDING,
        REACHED,
        NOT_REACHED
    };

    ReachabilityProbe(
        uint8_t busId, uint16_t testerAddress, RoutingTable const& table, uint32_t windowMs);

    /// Probes every route; earlier results are discarded.
    void start(uint32_t nowMs);

    /// True while a route is pending within the window.
    bool running(uint32_t nowMs) const;

    /// Result of a route; a route still pending after the window is NOT_REACHED.
    Result result(size_t routeIndex, uint32_t nowMs) const;

    size_t routeCount() const { return _table.size(); }

    uint16_t testerAddress() const { return _tester; }

    /// Responses of the nodes, forwarded by the router to the probe's bus.
    ErrorCode send(
        ::transport::TransportMessage& transportMessage,
        ::transport::ITransportMessageProcessedListener* pNotificationListener) override;

private:
    void transportMessageProcessed(
        ::transport::TransportMessage& transportMessage, ProcessingResult result) override;

    bool expired(uint32_t nowMs) const { return static_cast<int32_t>(nowMs - _deadline) >= 0; }

    RoutingTable const& _table;
    uint16_t _tester;
    uint32_t _windowMs;
    uint32_t _deadline;
    ::etl::array<Result, MAX_ROUTES> _results;
};

} // namespace gateway
