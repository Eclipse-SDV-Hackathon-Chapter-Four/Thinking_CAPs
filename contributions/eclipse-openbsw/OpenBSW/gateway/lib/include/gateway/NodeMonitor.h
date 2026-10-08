// SPDX-License-Identifier: Apache-2.0
#pragma once

#include "gateway/RoutingTable.h"

#include <transport/routing/IRouteObserver.h>
#include <transport/routing/TransportRouterStatistics.h>

#include <etl/array.h>

#include <cstdint>

namespace gateway
{
/** Fault memory interface the monitor reports into (implemented by the UDS DTC store). */
class IDtcSink
{
public:
    virtual void registerDtc(uint32_t dtc) = 0;
    virtual void setFailed(uint32_t dtc)   = 0;
    virtual void setPassed(uint32_t dtc)   = 0;

protected:
    ~IDtcSink() = default;
};

/**
 * Passive node communication monitor (ARC-06, SWR-024): a route is "not responding"
 * after THRESHOLD consecutive timeouts of routed requests, which sets its lost-
 * communication DTC; the next valid response makes the test pass again. It never
 * sends CAN traffic of its own (AD-05).
 */
class NodeMonitor : public ::transport::IRouteObserver
{
public:
    static constexpr uint8_t THRESHOLD = 3U;

    NodeMonitor(RoutingTable const& table, IDtcSink& sink);

    /** Registers every route's DTC as supported. */
    void init();

    void routeResponded(size_t routeIndex) override;
    void routeTimedOut(size_t routeIndex) override;

    bool isNotResponding(size_t routeIndex) const;

private:
    RoutingTable const& _table;
    IDtcSink& _sink;
    ::etl::array<uint8_t, ::transport::TransportRouterStatistics::MAX_ROUTES> _consecutiveTimeouts{};
};

} // namespace gateway
