// SPDX-License-Identifier: Apache-2.0
//
// DoIP client of the zonal gateway (ARC-11, SWR-006, SWR-019): reaches the routes with
// transport doip through the contributed doip::DoIpClientTransportLayer on bus DOIP_NODES.
// Runs in the Ethernet (lwIP) context.

#pragma once

#include <async/Async.h>
#include <async/IRunnable.h>
#include <doip/client/DoIpClientTransportLayer.h>
#include <etl/array.h>
#include <gateway/RoutingConfig.h>
#include <lifecycle/AsyncLifecycleComponent.h>
#include <lwipSocket/tcp/LwipSocket.h>
#include <transport/ITransportSystem.h>

namespace doip
{
class DoIpClientSystem
: public ::lifecycle::AsyncLifecycleComponent
, private ::async::IRunnable
{
public:
    static constexpr uint32_t SUPERVISION_PERIOD_MS = 10U;
    /// Connect, routing activation and acknowledgement; below the router's transfer budget.
    static constexpr uint32_t DELIVERY_TIMEOUT_MS   = 1500U;
    static_assert(
        DELIVERY_TIMEOUT_MS < ::gateway::config::TRANSFER_TIMEOUT_MS,
        "the router must not give up a request the DoIP client still sends (AD-11)");
    static constexpr size_t NODE_CAPACITY
        = (::gateway::config::DOIP_ROUTE_COUNT > 0U) ? ::gateway::config::DOIP_ROUTE_COUNT : 1U;

    DoIpClientSystem(::transport::ITransportSystem& transportSystem, ::async::ContextType context);

    void init() override;
    void run() override;
    void shutdown() override;

    DoIpClientTransportLayer& transportLayer() { return _layer; }

private:
    using Nodes     = ::etl::array<DoIpClientNode, NODE_CAPACITY>;
    using LayerType = declare::DoIpClientTransportLayer<NODE_CAPACITY, ::tcp::LwipSocket>;

    static Nodes buildNodes();
    void execute() override;
    void shutdownDone(::transport::AbstractTransportLayer& layer);

    ::transport::ITransportSystem& _transportSystem;
    ::async::ContextType _context;
    ::async::TimeoutType _timeout;
    Nodes _nodes;
    LayerType _layer;
};

} // namespace doip
