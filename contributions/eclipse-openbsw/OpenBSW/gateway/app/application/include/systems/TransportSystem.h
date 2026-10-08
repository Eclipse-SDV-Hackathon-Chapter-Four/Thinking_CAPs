/********************************************************************************
 * Copyright (c) 2024 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Derived from Eclipse OpenBSW executables/referenceApp/application/include/systems/
// TransportSystem.h. Modified for the zonal diagnostic gateway: hosts the gateway routing
// table and the contributed transport::TransportRouter instead of TransportRouterSimple
// (ARC-03, ARC-04, ARC-07).

#pragma once

#include <async/Async.h>
#include <async/IRunnable.h>
#include <etl/array.h>
#include <etl/singleton_base.h>
#include <gateway/RoutingConfig.h>
#include <gateway/RoutingTable.h>
#include <lifecycle/AsyncLifecycleComponent.h>
#include <transport/ITransportMessageProvider.h>
#include <transport/ITransportSystem.h>
#include <transport/routing/TransportRouter.h>

namespace transport
{
class AbstractTransportLayer;

class TransportSystem
: public ::etl::singleton_base<TransportSystem>
, public ::transport::ITransportSystem
, public ::lifecycle::AsyncLifecycleComponent
, private ::async::IRunnable
{
public:
    static constexpr uint32_t SUPERVISION_PERIOD_MS = 10U;
    static constexpr uint32_t STATISTICS_LOG_MS     = 30000U;

    explicit TransportSystem(::async::ContextType transitionContext);

    virtual char const* getName() const;
    void init() override;
    void run() override;
    void shutdown() override;
    virtual void dump() const;

    ::transport::TransportRouter& getRouter() { return _router; }
    ::gateway::RoutingTable const& getRoutingTable() const { return _table; }
    ::transport::TransportRouterStatistics& getStatistics() { return _statistics; }

    /** \see ITransportSystem::addTransportLayer() */
    void addTransportLayer(AbstractTransportLayer& layer) override;
    /** \see ITransportSystem::removeTransportLayer() */
    void removeTransportLayer(AbstractTransportLayer& layer) override;
    /** \see ITransportSystem::getTransportMessageProvider() */
    ITransportMessageProvider& getTransportMessageProvider() override;

private:
    void execute() override;
    void logStatistics() const;

    ::async::ContextType _context;
    ::async::TimeoutType _timeout;
    ::gateway::RoutingTable _table;
    ::etl::array<::transport::DiagnosticRoute, ::gateway::config::ROUTE_COUNT> _routes;
    ::transport::TransportRouterStatistics _statistics;
    ::transport::TransportRouter _router;
    uint32_t _ticks;
};

} // namespace transport
