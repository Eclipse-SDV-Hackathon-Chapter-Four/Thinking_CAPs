// SPDX-License-Identifier: Apache-2.0
#include "gateway/NodeMonitor.h"

#include "gateway/GatewayLogger.h"

namespace gateway
{
using ::util::logger::GATEWAY;
using ::util::logger::Logger;

NodeMonitor::NodeMonitor(RoutingTable const& table, IDtcSink& sink) : _table(table), _sink(sink)
{}

void NodeMonitor::init()
{
    _consecutiveTimeouts.fill(0U);
    for (Route const& route : _table.routes())
    {
        _sink.registerDtc(route.lostCommDtc);
    }
}

void NodeMonitor::routeResponded(size_t const routeIndex)
{
    if (routeIndex >= _table.size())
    {
        return;
    }
    _consecutiveTimeouts[routeIndex] = 0U;
    _sink.setPassed(_table.at(routeIndex).lostCommDtc);
}

void NodeMonitor::routeTimedOut(size_t const routeIndex)
{
    if (routeIndex >= _table.size())
    {
        return;
    }
    uint8_t& count = _consecutiveTimeouts[routeIndex];
    if (count >= THRESHOLD)
    {
        return; // already reported; the next response makes the test pass again
    }
    ++count;
    if (count == THRESHOLD)
    {
        Route const& route = _table.at(routeIndex);
        Logger::warn(
            GATEWAY,
            "route 0x%04x (%s) not responding, DTC 0x%06x",
            route.logicalAddress,
            route.name,
            route.lostCommDtc);
        _sink.setFailed(route.lostCommDtc);
    }
}

bool NodeMonitor::isNotResponding(size_t const routeIndex) const
{
    return (routeIndex < _table.size()) && (_consecutiveTimeouts[routeIndex] >= THRESHOLD);
}

} // namespace gateway
