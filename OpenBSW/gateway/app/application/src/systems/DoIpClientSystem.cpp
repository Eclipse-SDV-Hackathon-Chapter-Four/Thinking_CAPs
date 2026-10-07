// SPDX-License-Identifier: Apache-2.0

#include "systems/DoIpClientSystem.h"

#include <busid/BusId.h>
#include <doip/client/DoIpClientLogger.h>
#include <doip/common/DoIpConstants.h>
#include <ip/IPAddress.h>
#include <logger/logger.h>
#include <time/TimestampProvider.h>

namespace doip
{
namespace
{
uint32_t nowMs() { return ::bsw::time::TimestampProvider::getTimestampUs32Bit() / 1000U; }

DoIpClientParameters const PARAMETERS{
    ::gateway::config::NODE_TESTER_ADDRESS,
    ::gateway::config::FUNCTIONAL_ADDRESS,
    DoIpConstants::ProtocolVersion::version02Iso2012,
    DoIpConstants::Ports::TCP_DATA,
    DoIpClientSystem::DELIVERY_TIMEOUT_MS,
    4095U};
} // namespace

using ::util::logger::DOIPCLIENT;
using ::util::logger::Logger;

DoIpClientSystem::Nodes DoIpClientSystem::buildNodes()
{
    Nodes nodes{};
    size_t i = 0U;
    for (::gateway::Route const& route : ::gateway::config::ROUTES)
    {
        if ((route.transport == ::gateway::Transport::DOIP) && (i < NODE_CAPACITY))
        {
            nodes[i] = DoIpClientNode{
                route.logicalAddress, ::ip::make_ip4(route.ipAddress), route.name};
            ++i;
        }
    }
    return nodes;
}

DoIpClientSystem::DoIpClientSystem(
    ::transport::ITransportSystem& transportSystem, ::async::ContextType const context)
: _transportSystem(transportSystem)
, _context(context)
, _timeout()
, _nodes(buildNodes())
, _layer(
      ::busid::DOIP_NODES,
      PARAMETERS,
      ::etl::span<DoIpClientNode const>(_nodes.data(), ::gateway::config::DOIP_ROUTE_COUNT),
      context,
      DoIpClientTransportLayer::NowMsType::create<&nowMs>())
{
    setTransitionContext(context);
}

void DoIpClientSystem::init() { transitionDone(); }

void DoIpClientSystem::run()
{
    _transportSystem.addTransportLayer(_layer);
    (void)_layer.init();
    ::async::scheduleAtFixedRate(
        _context, *this, _timeout, SUPERVISION_PERIOD_MS, ::async::TimeUnit::MILLISECONDS);
    Logger::info(
        DOIPCLIENT,
        "DoIP client: %d node(s), source 0x%04x",
        static_cast<int>(::gateway::config::DOIP_ROUTE_COUNT),
        ::gateway::config::NODE_TESTER_ADDRESS);
    transitionDone();
}

void DoIpClientSystem::shutdown()
{
    _timeout.cancel();
    _transportSystem.removeTransportLayer(_layer);
    (void)_layer.shutdown(::transport::AbstractTransportLayer::ShutdownDelegate::
                              create<DoIpClientSystem, &DoIpClientSystem::shutdownDone>(*this));
    transitionDone();
}

void DoIpClientSystem::shutdownDone(::transport::AbstractTransportLayer& /* layer */) {}

void DoIpClientSystem::execute() { _layer.cyclic(); }

} // namespace doip
