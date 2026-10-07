/********************************************************************************
 * Copyright (c) 2026 Jefferson Nascimento
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// AI disclosure: this file was largely generated with an AI assistant and was reviewed and
// tested by the contributor. Assisted-by: Anthropic Claude Opus 5.5

#pragma once

#include "doip/client/DoIpClientConnection.h"

#include <transport/AbstractTransportLayer.h>
#include <transport/ITransportMessageProcessedListener.h>
#include <transport/TransportMessage.h>

#include <etl/delegate.h>
#include <etl/span.h>
#include <etl/uncopyable.h>
#include <etl/vector.h>

#include <cstdint>

namespace doip
{
/**
 * DoIP client transport layer (ISO 13400-2, external test equipment role).
 *
 * Sends diagnostic messages to DoIP nodes over TCP and passes their diagnostic messages to
 * the transport message provider, so a router (for example transport::TransportRouter) can
 * reach Ethernet ECUs in the same way as CAN ECUs through DoCAN:
 *
 * - send() with a node's logical address as target: the connection to that node is opened on
 *   demand (TCP, then routing activation with type 0x00), the message is sent as a diagnostic
 *   message, and the message is reported as processed once the node acknowledges it (0x8002:
 *   success, 0x8003: error). One request per node at a time.
 * - send() with the functional address as target: the message is sent to every node whose
 *   routing is active and which has no request in progress; it is reported as processed when
 *   every copy has been handed to TCP.
 * - Diagnostic messages from a node to the client address are passed to the provider with
 *   the node as source; alive check requests are answered.
 *
 * Every send() is reported as processed within DoIpClientParameters::deliveryTimeoutMs; a
 * node that does not connect, activate or acknowledge in time is disconnected. Choose a
 * timeout shorter than the receiver's own supervision (for example the TransportRouter
 * transfer budget).
 *
 * All calls, including send(), must be made in the context of the TCP stack (for lwIP, the
 * Ethernet task). Call cyclic() periodically (for example every 10 ms) in that context.
 */
class DoIpClientTransportLayer
: public ::transport::AbstractTransportLayer
, public ::etl::uncopyable
{
public:
    using NowMsType = ::etl::delegate<uint32_t()>;

    DoIpClientTransportLayer(
        uint8_t busId,
        DoIpClientParameters const& parameters,
        ::etl::ivector<DoIpClientConnection>& connections,
        NowMsType nowMs);

    ErrorCode init() override;
    bool shutdown(ShutdownDelegate delegate) override;
    ErrorCode send(
        ::transport::TransportMessage& transportMessage,
        ::transport::ITransportMessageProcessedListener* pNotificationListener) override;

    /// Supervision of connection set-up and acknowledgements.
    void cyclic();

    DoIpClientParameters const& parameters() const { return _parameters; }

    ::etl::span<DoIpClientConnection const> connections() const
    {
        return ::etl::span<DoIpClientConnection const>(_connections.data(), _connections.size());
    }

    DoIpClientConnection* findConnection(uint16_t logicalAddress);

    uint32_t nowMs() const { return _nowMs(); }

    /// Called by a connection when its copy of the functional message has been released.
    void functionalCopyReleased();

private:
    DoIpClientParameters _parameters;
    ::etl::ivector<DoIpClientConnection>& _connections;
    NowMsType _nowMs;
    ::transport::TransportMessage* _functionalMessage;
    ::transport::ITransportMessageProcessedListener* _functionalListener;
    size_t _functionalCopies;
};

namespace declare
{
/**
 * DoIP client transport layer with storage for NodeCount connections, each with its own
 * socket of type SocketType (for example tcp::LwipSocket).
 */
template<size_t NodeCount, class SocketType>
class DoIpClientTransportLayer : public ::doip::DoIpClientTransportLayer
{
public:
    DoIpClientTransportLayer(
        uint8_t busId,
        DoIpClientParameters const& parameters,
        ::etl::span<DoIpClientNode const> nodes,
        ::async::ContextType context,
        NowMsType nowMs)
    : ::doip::DoIpClientTransportLayer(busId, parameters, _connectionStorage, nowMs)
    , _sockets()
    , _connectionStorage()
    {
        size_t const count = (nodes.size() < NodeCount) ? nodes.size() : NodeCount;
        for (size_t i = 0U; i < count; ++i)
        {
            _connectionStorage.emplace_back(*this, nodes[i], _sockets[i], context);
        }
    }

private:
    SocketType _sockets[NodeCount];
    ::etl::vector<DoIpClientConnection, NodeCount> _connectionStorage;
};
} // namespace declare

} // namespace doip
