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

#include <async/Types.h>
#include <doip/common/DoIpConstants.h>
#include <doip/common/DoIpStaticPayloadSendJob.h>
#include <doip/common/DoIpTcpConnection.h>
#include <doip/common/DoIpTransportMessageSendJob.h>
#include <doip/common/IDoIpConnectionHandler.h>
#include <doip/common/IDoIpSendJobCallback.h>
#include <ip/IPAddress.h>
#include <tcp/socket/AbstractSocket.h>
#include <transport/ITransportMessageProcessedListener.h>
#include <transport/TransportMessage.h>

#include <etl/optional.h>
#include <etl/queue.h>
#include <etl/span.h>
#include <etl/uncopyable.h>

#include <cstdint>

namespace doip
{
class DoIpClientTransportLayer;

/** A DoIP node reached by the client. */
struct DoIpClientNode
{
    /// Logical address of the node: target of requests, source of its responses.
    uint16_t logicalAddress;
    /// IP address of the DoIP entity that hosts the node.
    ::ip::IPAddress address;
    /// Name used in log output; may be nullptr.
    char const* name;
};

/** Parameters shared by all connections of a DoIpClientTransportLayer. */
struct DoIpClientParameters
{
    /// Logical address of the client (external test equipment), source of all requests.
    uint16_t sourceAddress;
    /// Target address of functional requests.
    uint16_t functionalAddress;
    DoIpConstants::ProtocolVersion protocolVersion;
    /// TCP port of the nodes (DoIpConstants::Ports::TCP_DATA).
    uint16_t port;
    /// Time from send() to the node's acknowledgement, including connection set-up.
    uint32_t deliveryTimeoutMs;
    /// Largest diagnostic message payload accepted from a node.
    uint16_t maxPayloadLength;
};

/**
 * Client connection to one DoIP node. Created and driven by DoIpClientTransportLayer.
 */
class DoIpClientConnection
: public IDoIpConnectionHandler
, public IDoIpSendJobCallback<DoIpTransportMessageSendJob>
, public ::transport::ITransportMessageProcessedListener
, public ::etl::uncopyable
{
public:
    enum class State : uint8_t
    {
        CLOSED,
        CONNECTING,
        ACTIVATING,
        ACTIVE
    };

    DoIpClientConnection(
        DoIpClientTransportLayer& layer,
        DoIpClientNode const& node,
        ::tcp::AbstractSocket& socket,
        ::async::ContextType context);

    DoIpClientNode const& node() const { return _node; }

    State state() const { return _state; }

    bool hasRequest() const { return _request != nullptr; }

    /**
     * Takes a physical request; it is reported as processed to listener on acknowledgement,
     * error or deadline. Returns false if a request is already in progress.
     */
    bool request(
        ::transport::TransportMessage& message,
        ::transport::ITransportMessageProcessedListener* listener,
        uint32_t deadline);

    /**
     * Sends a copy of a functional request if routing is active and no request is in
     * progress. Returns true if the copy was queued; its release is reported to the layer.
     */
    bool functional(::transport::TransportMessage& message);

    /// Deadline supervision.
    void cyclic(uint32_t now);

    /// Closes the connection; a request in progress fails.
    void close();

    // IDoIpConnectionHandler
    void connectionClosed(bool closedByRemotePeer) override;
    HeaderReceivedContinuation headerReceived(DoIpHeader const& header) override;

    // IDoIpSendJobCallback
    void releaseSendJob(DoIpTransportMessageSendJob& sendJob, bool success) override;

    // ITransportMessageProcessedListener: a node response was handled by the provider
    void transportMessageProcessed(
        ::transport::TransportMessage& transportMessage, ProcessingResult result) override;

private:
    enum class Ack : uint8_t
    {
        REQUEST,
        FUNCTIONAL
    };

    static constexpr size_t ACTIVATION_REQUEST_LENGTH  = 7U;
    static constexpr size_t ACTIVATION_RESPONSE_LENGTH = 9U;
    static constexpr size_t ACK_LENGTH                 = 5U;
    static constexpr size_t ADDRESS_INFO_LENGTH        = 4U;
    static constexpr size_t MAX_PENDING_ACKS           = 4U;

    using StaticJob = DoIpStaticPayloadSendJob;

    void connect();
    void connected(::tcp::AbstractSocket::ErrorCode result);
    void sendActivation();
    void sendRequest();
    void tryFinishRequest();
    void finishRequest(bool success);
    void closeAndFail(char const* reason);
    void sendAliveCheckResponse();

    void activationJobReleased(StaticJob& job, bool success);
    void aliveJobReleased(StaticJob& job, bool success);

    void activationResponseReceived(::etl::span<uint8_t const> payload);
    void ackReceived(::etl::span<uint8_t const> payload);
    void addressInfoReceived(::etl::span<uint8_t const> payload);
    void diagnosticPayloadReceived(::etl::span<uint8_t const> payload);

    static IDoIpConnection::PayloadDiscardedCallbackType discard();
    HeaderReceivedContinuation skipPayload();

    DoIpClientTransportLayer& _layer;
    DoIpClientNode const& _node;
    ::tcp::AbstractSocket& _socket;
    uint8_t _writeBuffer[DoIpConstants::DOIP_HEADER_LENGTH];
    DoIpTcpConnection _connection;
    declare::DoIpStaticPayloadSendJob<ACTIVATION_REQUEST_LENGTH> _activationJob;
    declare::DoIpStaticPayloadSendJob<2U> _aliveJob;
    ::etl::optional<DoIpTransportMessageSendJob> _requestJob;
    ::etl::optional<DoIpTransportMessageSendJob> _functionalJob;
    ::etl::queue<Ack, MAX_PENDING_ACKS> _pendingAcks;

    ::transport::TransportMessage* _request;
    ::transport::ITransportMessageProcessedListener* _requestListener;
    uint32_t _deadline;
    bool _requestSent;
    bool _requestReleased;
    bool _ackReceived;
    bool _ackPositive;

    bool _activationJobBusy;
    bool _aliveJobBusy;
    bool _functionalJobBusy;

    uint8_t _rxBuffer[ACTIVATION_RESPONSE_LENGTH];
    uint16_t _rxPayloadType;
    uint16_t _rxLength;
    uint16_t _rxSource;
    ::transport::TransportMessage* _rxMessage;

    State _state;
};

} // namespace doip
