/********************************************************************************
 * Copyright (c) 2024 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Derived from Eclipse OpenBSW executables/referenceApp/application/src/systems/
// TransportSystem.cpp. Modified for the zonal diagnostic gateway (see TransportSystem.h).

#include "systems/TransportSystem.h"

#include <busid/BusId.h>
#include <etl/span.h>
#include <gateway/GatewayLogger.h>
#include <gateway/RoutingConfig.h>
#include <logger/logger.h>
#include <time/TimestampProvider.h>

#include <cstdint>
#include <cstdlib>

namespace transport
{
namespace
{
using RouteCounter  = ::transport::TransportRouterStatistics::RouteCounter;
using RouterCounter = ::transport::TransportRouterStatistics::RouterCounter;

uint32_t nowMs() { return ::bsw::time::TimestampProvider::getTimestampUs32Bit() / 1000U; }

::gateway::RoutingTable::Addresses const ADDRESSES{
    ::gateway::config::GATEWAY_ADDRESS,
    ::gateway::config::FUNCTIONAL_ADDRESS,
    ::gateway::config::FUNCTIONAL_CAN_ID,
    ::gateway::config::TESTER_ADDRESS_MIN,
    ::gateway::config::TESTER_ADDRESS_MAX};

/// Every route of this gateway is a DoCAN node on CAN_0 (SWR-012).
::etl::array<::transport::DiagnosticRoute, ::gateway::config::ROUTE_COUNT> diagnosticRoutes()
{
    ::etl::array<::transport::DiagnosticRoute, ::gateway::config::ROUTE_COUNT> routes{};
    for (size_t i = 0U; i < ::gateway::config::ROUTE_COUNT; ++i)
    {
        ::gateway::Route const& route = ::gateway::config::ROUTES[i];
        routes[i]                     = ::transport::DiagnosticRoute{
            route.logicalAddress,
            ::busid::CAN_0,
            route.p2Ms,
            route.p2StarMs,
            route.maxLength,
            route.name};
    }
    return routes;
}

uint16_t const MAX_FUNCTIONAL_LENGTH = 7U; // one classic CAN single frame (SWR-013)
} // namespace

using ::util::logger::GATEWAY;
using ::util::logger::Logger;

TransportSystem::TransportSystem(::async::ContextType transitionContext)
: ::etl::singleton_base<TransportSystem>(*this)
, _context(transitionContext)
, _timeout()
, _table(ADDRESSES, ::etl::span<::gateway::Route const>(::gateway::config::ROUTES))
, _routes(diagnosticRoutes())
, _statistics()
, _router(
      ::transport::TransportRouterConfiguration{
          ::gateway::config::GATEWAY_ADDRESS,
          ::busid::SELFDIAG,
          ::gateway::config::FUNCTIONAL_ADDRESS,
          ::gateway::config::CAN_TESTER_ADDRESS,
          ::gateway::config::TESTER_ADDRESS_MIN,
          ::gateway::config::TESTER_ADDRESS_MAX,
          ::gateway::config::FUNCTIONAL_WINDOW_MS,
          MAX_FUNCTIONAL_LENGTH,
          ::etl::span<::transport::DiagnosticRoute const>(_routes)},
      _statistics,
      ::transport::TransportRouter::NowMsType::create<&nowMs>())
, _ticks(0U)
{
    // Tell the lifecycle manager in which context to execute init/run/shutdown
    setTransitionContext(transitionContext);
}

char const* TransportSystem::getName() const { return "Transport"; }

void TransportSystem::init()
{
    size_t badIndex = ::gateway::RoutingTable::INVALID_INDEX;
    auto const error = _table.validate(badIndex);
    if (error != ::gateway::RoutingTable::Error::NONE)
    {
        // SWR-010: an invalid routing table stops start-up
        Logger::critical(
            GATEWAY,
            "routing table invalid at route %d: %s",
            static_cast<int>(badIndex),
            ::gateway::RoutingTable::errorText(error));
        ::logger::flush();
        ::std::exit(2);
    }
    auto const routerError = _router.validate(badIndex);
    if (routerError != ::transport::TransportRouter::ValidationError::NONE)
    {
        Logger::critical(
            GATEWAY,
            "router configuration invalid at route %d: %s",
            static_cast<int>(badIndex),
            ::transport::TransportRouter::toString(routerError));
        ::logger::flush();
        ::std::exit(2);
    }
    Logger::info(
        GATEWAY,
        "routing table %s: gateway 0x%04x, functional 0x%04x, %d routes",
        ::gateway::config::ROUTING_TABLE_HASH,
        ::gateway::config::GATEWAY_ADDRESS,
        ::gateway::config::FUNCTIONAL_ADDRESS,
        static_cast<int>(_table.size()));
    for (::gateway::Route const& route : _table.routes())
    {
        Logger::info(
            GATEWAY,
            "route 0x%04x %s: CAN 0x%03x/0x%03x, P2 %d ms, P2* %d ms",
            route.logicalAddress,
            route.name,
            static_cast<unsigned>(route.requestCanId),
            static_cast<unsigned>(route.responseCanId),
            route.p2Ms,
            route.p2StarMs);
    }
    _router.init();
    transitionDone();
}

void TransportSystem::run()
{
    ::async::scheduleAtFixedRate(
        _context, *this, _timeout, SUPERVISION_PERIOD_MS, ::async::TimeUnit::MILLISECONDS);
    transitionDone();
}

void TransportSystem::shutdown()
{
    _timeout.cancel();
    logStatistics();
    _router.shutdown();
    transitionDone();
}

void TransportSystem::execute()
{
    _router.cyclic();
    ++_ticks;
    if ((_ticks * SUPERVISION_PERIOD_MS) >= STATISTICS_LOG_MS)
    {
        _ticks = 0U;
        logStatistics();
    }
}

void TransportSystem::logStatistics() const
{
    Logger::info(
        GATEWAY,
        "stats local=%d functional=%d unknown_target=%d no_buffer=%d",
        _statistics.get(RouterCounter::LOCAL_REQUESTS),
        _statistics.get(RouterCounter::FUNCTIONAL_REQUESTS),
        _statistics.get(RouterCounter::UNKNOWN_TARGET),
        _statistics.get(RouterCounter::NO_BUFFER));
    for (size_t i = 0U; i < _table.size(); ++i)
    {
        Logger::info(
            GATEWAY,
            "stats 0x%04x req=%d rsp=%d pending=%d timeout=%d busy=%d too_large=%d tx_fail=%d "
            "discarded=%d",
            _table.at(i).logicalAddress,
            _statistics.get(i, RouteCounter::REQUESTS),
            _statistics.get(i, RouteCounter::RESPONSES),
            _statistics.get(i, RouteCounter::PENDING),
            _statistics.get(i, RouteCounter::TIMEOUTS),
            _statistics.get(i, RouteCounter::NACK_BUSY),
            _statistics.get(i, RouteCounter::NACK_TOO_LARGE),
            _statistics.get(i, RouteCounter::TX_FAILURES),
            _statistics.get(i, RouteCounter::DISCARDED));
    }
}

void TransportSystem::dump() const {}

void TransportSystem::addTransportLayer(AbstractTransportLayer& layer)
{
    _router.addTransportLayer(layer);
}

void TransportSystem::removeTransportLayer(AbstractTransportLayer& layer)
{
    _router.removeTransportLayer(layer);
}

ITransportMessageProvider& TransportSystem::getTransportMessageProvider() { return _router; }

} // namespace transport
