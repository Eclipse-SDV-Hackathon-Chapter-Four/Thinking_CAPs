// SPDX-License-Identifier: Apache-2.0
#pragma once

#include "uds/DemoDtcManager.h"

#include <gateway/NodeMonitor.h>
#include <transport/routing/TransportRouterStatistics.h>
#include <gateway/RoutingTable.h>
#include <uds/jobs/DataIdentifierJob.h>

namespace uds
{
/**
 * DID FD00 (SWR-022): active routing table.
 * Response: route count (1), gateway address (2), functional address (2), then per route:
 * logical address (2), transport (1, 0 = DoCAN), request CAN ID (2), response CAN ID (2),
 * P2 ms (2), P2* ms (2). All values big-endian.
 */
class ReadRoutingTable : public DataIdentifierJob
{
public:
    static constexpr uint16_t DID = 0xFD00U;

    explicit ReadRoutingTable(::gateway::RoutingTable const& table);

private:
    DiagReturnCode::Type process(
        IncomingDiagConnection& connection,
        uint8_t const request[],
        uint16_t requestLength) override;

    uint8_t _implementedRequest[3];
    ::gateway::RoutingTable const& _table;
};

/**
 * DID FD01 (SWR-023): routing statistics.
 * Response: gateway counters (local, functional, unknown target, no buffer; 2 bytes each),
 * route count (1), then per route: logical address (2) and the counters requests, responses,
 * pending, timeouts, busy, too large, tx failures, discarded (2 bytes each). Big-endian,
 * saturating at 0xFFFF.
 */
class ReadRoutingStatistics : public DataIdentifierJob
{
public:
    static constexpr uint16_t DID = 0xFD01U;

    ReadRoutingStatistics(
        ::gateway::RoutingTable const& table,
        ::transport::TransportRouterStatistics const& statistics);

private:
    DiagReturnCode::Type process(
        IncomingDiagConnection& connection,
        uint8_t const request[],
        uint16_t requestLength) override;

    uint8_t _implementedRequest[3];
    ::gateway::RoutingTable const& _table;
    ::transport::TransportRouterStatistics const& _statistics;
};

/** Connects the node monitor (ARC-06) to the UDS fault memory (SWR-025). */
class DtcSink : public ::gateway::IDtcSink
{
public:
    explicit DtcSink(DemoDtcManager& manager) : _manager(manager) {}

    void registerDtc(uint32_t dtc) override;
    void setFailed(uint32_t dtc) override;
    void setPassed(uint32_t dtc) override;

private:
    DemoDtcManager& _manager;
};

} // namespace uds
