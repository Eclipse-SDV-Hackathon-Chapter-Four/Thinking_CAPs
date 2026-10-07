// SPDX-License-Identifier: Apache-2.0
#include "uds/GatewayDiagJobs.h"

#include <async/Async.h>
#include <time/TimestampProvider.h>
#include <uds/connection/IncomingDiagConnection.h>

namespace uds
{
namespace
{
void setDid(uint8_t (&request)[3], uint16_t const did)
{
    request[0] = 0x22U;
    request[1] = static_cast<uint8_t>(did >> 8U);
    request[2] = static_cast<uint8_t>(did & 0xFFU);
}

void append16(PositiveResponse& response, uint16_t const value)
{
    (void)response.appendUint8(static_cast<uint8_t>(value >> 8U));
    (void)response.appendUint8(static_cast<uint8_t>(value & 0xFFU));
}
} // namespace

ReadRoutingTable::ReadRoutingTable(::gateway::RoutingTable const& table)
: DataIdentifierJob(_implementedRequest, DiagSession::ALL_SESSIONS()), _table(table)
{
    setDid(_implementedRequest, DID);
}

DiagReturnCode::Type ReadRoutingTable::process(
    IncomingDiagConnection& connection,
    uint8_t const* const /* request */,
    uint16_t const /* requestLength */)
{
    PositiveResponse& response = connection.releaseRequestGetResponse();
    (void)response.appendUint8(static_cast<uint8_t>(_table.size()));
    append16(response, _table.addresses().gateway);
    append16(response, _table.addresses().functional);
    for (::gateway::Route const& route : _table.routes())
    {
        append16(response, route.logicalAddress);
        if (route.transport == ::gateway::Transport::DOIP)
        {
            // DoIP: the 4 bytes of the CAN identifiers hold the node's IPv4 address
            (void)response.appendUint8(1U);
            append16(response, static_cast<uint16_t>(route.ipAddress >> 16U));
            append16(response, static_cast<uint16_t>(route.ipAddress & 0xFFFFU));
        }
        else
        {
            (void)response.appendUint8(0U); // DoCAN
            append16(response, static_cast<uint16_t>(route.requestCanId));
            append16(response, static_cast<uint16_t>(route.responseCanId));
        }
        append16(response, route.p2Ms);
        append16(response, route.p2StarMs);
    }
    (void)connection.sendPositiveResponseInternal(response.getLength(), *this);
    return DiagReturnCode::OK;
}

ReadRoutingStatistics::ReadRoutingStatistics(
    ::gateway::RoutingTable const& table, ::transport::TransportRouterStatistics const& statistics)
: DataIdentifierJob(_implementedRequest, DiagSession::ALL_SESSIONS())
, _table(table)
, _statistics(statistics)
{
    setDid(_implementedRequest, DID);
}

DiagReturnCode::Type ReadRoutingStatistics::process(
    IncomingDiagConnection& connection,
    uint8_t const* const /* request */,
    uint16_t const /* requestLength */)
{
    using RouterCounter = ::transport::TransportRouterStatistics::RouterCounter;
    using RouteCounter  = ::transport::TransportRouterStatistics::RouteCounter;

    PositiveResponse& response = connection.releaseRequestGetResponse();
    for (size_t c = 0U; c < ::transport::TransportRouterStatistics::ROUTER_COUNTERS; ++c)
    {
        append16(response, _statistics.get(static_cast<RouterCounter>(c)));
    }
    (void)response.appendUint8(static_cast<uint8_t>(_table.size()));
    for (size_t i = 0U; i < _table.size(); ++i)
    {
        append16(response, _table.at(i).logicalAddress);
        for (size_t c = 0U; c < ::transport::TransportRouterStatistics::ROUTE_COUNTERS; ++c)
        {
            append16(response, _statistics.get(i, static_cast<RouteCounter>(c)));
        }
    }
    (void)connection.sendPositiveResponseInternal(response.getLength(), *this);
    return DiagReturnCode::OK;
}

void DtcSink::registerDtc(uint32_t const dtc)
{
    ::async::LockType const lock;
    _manager.registerDtc(dtc);
}

void DtcSink::setFailed(uint32_t const dtc)
{
    ::async::LockType const lock;
    _manager.reportFault(dtc);
}

void DtcSink::setPassed(uint32_t const dtc)
{
    ::async::LockType const lock;
    _manager.reportPassed(dtc);
}

namespace
{
uint32_t probeNowMs() { return ::bsw::time::TimestampProvider::getTimestampUs32Bit() / 1000U; }
} // namespace

ReachabilityRoutine::ReachabilityRoutine(
    ::gateway::ReachabilityProbe& probe, ::async::ContextType const probeContext)
: RoutineControlJob(_implRequest, sizeof(_implRequest), nullptr, &_resultsNode)
, _probe(probe)
, _probeContext(probeContext)
, _startPending(false)
, _implRequest{0x31U, 0x01U, ROUTINE_ID >> 8U, ROUTINE_ID & 0xFFU}
, _resultsImplRequest{0x31U, 0x03U, ROUTINE_ID >> 8U, ROUTINE_ID & 0xFFU}
, _resultsNode(_resultsImplRequest, *this)
{}

DiagReturnCode::Type ReachabilityRoutine::start(
    IncomingDiagConnection& connection, uint8_t const* const, uint16_t const)
{
    _startPending = true;
    ::async::execute(_probeContext, *this);
    // the dispatcher has already put the sub-function and the routine ID into the response
    PositiveResponse& response = connection.releaseRequestGetResponse();
    (void)connection.sendPositiveResponseInternal(response.getLength(), *this);
    return DiagReturnCode::OK;
}

void ReachabilityRoutine::execute()
{
    _probe.start(probeNowMs());
    _startPending = false;
}

DiagReturnCode::Type ReachabilityRoutine::requestResults(
    IncomingDiagConnection& connection, uint8_t const* const, uint16_t const)
{
    uint32_t const now         = probeNowMs();
    bool const running         = _startPending || _probe.running(now);
    PositiveResponse& response = connection.releaseRequestGetResponse();
    (void)response.appendUint8(running ? 0x01U : 0x00U);
    (void)response.appendUint8(static_cast<uint8_t>(_probe.routeCount()));
    for (size_t i = 0U; i < _probe.routeCount(); ++i)
    {
        bool const reached
            = (!running) && (_probe.result(i, now) == ::gateway::ReachabilityProbe::Result::REACHED);
        (void)response.appendUint8(reached ? 0x01U : 0x00U);
    }
    (void)connection.sendPositiveResponseInternal(response.getLength(), *this);
    return DiagReturnCode::OK;
}

} // namespace uds
