/********************************************************************************
 * Copyright (c) 2026 Jefferson Nascimento
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

#include "doip/client/DoIpClientTransportLayer.h"

#include <async/AsyncMock.h>
#include <async/TestContext.h>
#include <tcp/IDataListener.h>
#include <tcp/IDataSendNotificationListener.h>
#include <tcp/socket/AbstractSocket.h>
#include <transport/ITransportMessageProcessedListener.h>
#include <transport/ITransportMessageProvidingListener.h>

#include <etl/vector.h>
#include <gtest/gtest.h>

#include <deque>
#include <vector>

namespace
{
using namespace ::doip;
using ::testing::NiceMock;
using ::transport::AbstractTransportLayer;
using ::transport::ITransportMessageProcessedListener;
using ::transport::ITransportMessageProvidingListener;
using ::transport::TransportMessage;
using Bytes            = std::vector<uint8_t>;
using ProcessingResult = ITransportMessageProcessedListener::ProcessingResult;
using ErrorCode        = AbstractTransportLayer::ErrorCode;

uint8_t const BUS          = 5U;
uint16_t const CLIENT      = 0x0E10U;
uint16_t const FUNCTIONAL  = 0xE400U;
uint16_t const NODE_A      = 0x1040U;
uint16_t const NODE_B      = 0x1050U;
uint32_t const TIMEOUT_MS  = 1500U;
uint16_t const MAX_PAYLOAD = 64U;

Bytes frame(uint16_t const type, Bytes const& payload, uint8_t const version = 0x02U)
{
    auto const length = static_cast<uint32_t>(payload.size());
    Bytes data{
        version,
        static_cast<uint8_t>(~version),
        static_cast<uint8_t>(type >> 8U),
        static_cast<uint8_t>(type),
        static_cast<uint8_t>(length >> 24U),
        static_cast<uint8_t>(length >> 16U),
        static_cast<uint8_t>(length >> 8U),
        static_cast<uint8_t>(length)};
    data.insert(data.end(), payload.begin(), payload.end());
    return data;
}

Bytes diagnostic(uint16_t const source, uint16_t const target, Bytes const& userData)
{
    Bytes payload{
        static_cast<uint8_t>(source >> 8U),
        static_cast<uint8_t>(source),
        static_cast<uint8_t>(target >> 8U),
        static_cast<uint8_t>(target)};
    payload.insert(payload.end(), userData.begin(), userData.end());
    return frame(0x8001U, payload);
}

Bytes ack(uint16_t const source, uint16_t const type = 0x8002U, uint8_t const code = 0x00U)
{
    return frame(
        type,
        {static_cast<uint8_t>(source >> 8U),
         static_cast<uint8_t>(source),
         static_cast<uint8_t>(CLIENT >> 8U),
         static_cast<uint8_t>(CLIENT),
         code});
}

Bytes activationResponse(uint16_t const entity, uint8_t const code = 0x10U)
{
    return frame(
        0x0006U,
        {static_cast<uint8_t>(CLIENT >> 8U),
         static_cast<uint8_t>(CLIENT),
         static_cast<uint8_t>(entity >> 8U),
         static_cast<uint8_t>(entity),
         code,
         0U,
         0U,
         0U,
         0U});
}

Bytes const ACTIVATION_REQUEST = frame(0x0005U, {0x0EU, 0x10U, 0x00U, 0U, 0U, 0U, 0U});

/** TCP socket in memory: records connects and sent bytes, delivers received bytes. */
class FakeSocket : public ::tcp::AbstractSocket
{
public:
    ErrorCode bind(::ip::IPAddress const&, uint16_t) override { return ErrorCode::SOCKET_ERR_OK; }

    ErrorCode connect(
        ::ip::IPAddress const& address, uint16_t const port, ConnectedDelegate delegate) override
    {
        ++connects;
        lastAddress = address;
        lastPort    = port;
        if (!acceptConnect)
        {
            return ErrorCode::SOCKET_ERR_NOT_OK;
        }
        _delegate = delegate;
        _open     = true;
        return ErrorCode::SOCKET_ERR_OK;
    }

    /// Completes the connection attempt (TCP handshake done or failed).
    void completeConnect(bool const success)
    {
        _established = success;
        _open        = success;
        _delegate(success ? ErrorCode::SOCKET_ERR_OK : ErrorCode::SOCKET_ERR_NOT_OK);
    }

    ErrorCode close() override
    {
        ++closes;
        _open = _established = false;
        rx.clear();
        return ErrorCode::SOCKET_ERR_OK;
    }

    void abort() override
    {
        ++aborts;
        _open = _established = false;
        rx.clear();
    }

    ErrorCode flush() override { return ErrorCode::SOCKET_ERR_OK; }

    void discardData() override { rx.clear(); }

    size_t available() override { return 2920U; }

    uint8_t read(uint8_t& byte) override { return static_cast<uint8_t>(read(&byte, 1U)); }

    size_t read(uint8_t* const buffer, size_t const n) override
    {
        size_t const count = (n < rx.size()) ? n : rx.size();
        for (size_t i = 0U; i < count; ++i)
        {
            if (buffer != nullptr)
            {
                buffer[i] = rx.front();
            }
            rx.pop_front();
        }
        return count;
    }

    ErrorCode send(::etl::span<uint8_t const> const& data) override
    {
        tx.insert(tx.end(), data.begin(), data.end());
        _unacknowledged += data.size();
        return ErrorCode::SOCKET_ERR_OK;
    }

    ::ip::IPAddress getRemoteIPAddress() const override { return lastAddress; }

    ::ip::IPAddress getLocalIPAddress() const override { return {}; }

    uint16_t getRemotePort() const override { return lastPort; }

    uint16_t getLocalPort() const override { return 50000U; }

    bool isClosed() const override { return !_open; }

    bool isEstablished() const override { return _established; }

    void disableNagleAlgorithm() override { nagleDisabled = true; }

    void enableKeepAlive(uint32_t, uint32_t, uint32_t) override {}

    void disableKeepAlive() override {}

    /// Delivers bytes from the node.
    void receive(Bytes const& data)
    {
        rx.insert(rx.end(), data.begin(), data.end());
        getDataListener()->dataReceived(static_cast<uint16_t>(data.size()));
    }

    /// The TCP peer acknowledged everything sent so far.
    void acknowledge()
    {
        if (_unacknowledged > 0U)
        {
            auto const length = static_cast<uint16_t>(_unacknowledged);
            _unacknowledged   = 0U;
            getSendNotificationListener()->dataSent(
                length, ::tcp::IDataSendNotificationListener::SendResult::DATA_SENT);
        }
    }

    /// The node closed the connection.
    void remoteClose()
    {
        _open = _established = false;
        getDataListener()->connectionClosed(::tcp::IDataListener::ErrorCode::ERR_CONNECTION_CLOSED);
    }

    Bytes takeSent()
    {
        Bytes data;
        data.swap(tx);
        return data;
    }

    bool acceptConnect = true;
    bool nagleDisabled = false;
    int connects       = 0;
    int closes         = 0;
    int aborts         = 0;
    ::ip::IPAddress lastAddress;
    uint16_t lastPort = 0U;
    std::deque<uint8_t> rx;
    Bytes tx;

private:
    ConnectedDelegate _delegate;
    size_t _unacknowledged = 0U;
    bool _open             = false;
    bool _established      = false;
};

/** Message provider and listener: hands out buffers and records the messages received. */
class Provider : public ITransportMessageProvidingListener
{
public:
    ErrorCode getTransportMessage(
        uint8_t const busId,
        uint16_t const source,
        uint16_t const target,
        uint16_t const size,
        ::etl::span<uint8_t const> const& /* peek */,
        TransportMessage*& message) override
    {
        requested.push_back({busId, source, target, size});
        if (!accept || allocated)
        {
            message = nullptr;
            return ErrorCode::TPMSG_NOT_RESPONSIBLE;
        }
        _message.init(_buffer, sizeof(_buffer));
        allocated = true;
        message   = &_message;
        return ErrorCode::TPMSG_OK;
    }

    void releaseTransportMessage(TransportMessage& /* message */) override
    {
        allocated = false;
        ++releases;
    }

    ReceiveResult messageReceived(
        uint8_t const busId,
        TransportMessage& message,
        ITransportMessageProcessedListener* const listener) override
    {
        received.push_back(
            {busId,
             message.getSourceId(),
             message.getTargetId(),
             Bytes(message.getPayload(), message.getPayload() + message.getPayloadLength())});
        listener->transportMessageProcessed(message, ProcessingResult::PROCESSED_NO_ERROR);
        return ReceiveResult::RECEIVED_NO_ERROR;
    }

    void dump() override {}

    struct Request
    {
        uint8_t busId;
        uint16_t source;
        uint16_t target;
        uint16_t size;
    };

    struct Received
    {
        uint8_t busId;
        uint16_t source;
        uint16_t target;
        Bytes payload;
    };

    bool accept    = true;
    bool allocated = false;
    int releases   = 0;
    std::vector<Request> requested;
    std::vector<Received> received;

private:
    TransportMessage _message;
    uint8_t _buffer[MAX_PAYLOAD];
};

class ProcessedRecorder : public ITransportMessageProcessedListener
{
public:
    void
    transportMessageProcessed(TransportMessage& message, ProcessingResult const result) override
    {
        results.push_back(result);
        messages.push_back(&message);
    }

    std::vector<ProcessingResult> results;
    std::vector<TransportMessage*> messages;
};

class DoIpClientTransportLayerTest : public ::testing::Test
{
public:
    DoIpClientTransportLayerTest()
    : asyncContext(1U)
    , testContext(asyncContext)
    , nodes{{
          DoIpClientNode{NODE_A, ::ip::make_ip4(0xC0A8001EU), "a"},
          DoIpClientNode{NODE_B, ::ip::make_ip4(0xC0A8001FU), nullptr},
      }}
    , connections()
    , layer(
          BUS,
          DoIpClientParameters{
              CLIENT,
              FUNCTIONAL,
              DoIpConstants::ProtocolVersion::version02Iso2012,
              13400U,
              TIMEOUT_MS,
              MAX_PAYLOAD},
          connections,
          DoIpClientTransportLayer::NowMsType::
              create<DoIpClientTransportLayerTest, &DoIpClientTransportLayerTest::nowMs>(*this))
    {
        for (size_t i = 0U; i < nodes.size(); ++i)
        {
            connections.emplace_back(layer, nodes[i], sockets[i], asyncContext);
        }
        layer.fProvidingListenerHelper.fpMessageProvider = &provider;
        layer.fProvidingListenerHelper.fpMessageListener = &provider;
    }

    void SetUp() override { testContext.handleAll(); }

    uint32_t nowMs() { return now; }

    /// Runs the queued send jobs of the connections.
    void run() { testContext.expireAndExecute(); }

    TransportMessage& message(uint16_t const target, Bytes const& payload)
    {
        requestMessage.init(requestBuffer, sizeof(requestBuffer));
        requestMessage.setSourceAddress(CLIENT);
        requestMessage.setTargetAddress(target);
        requestMessage.setPayloadLength(static_cast<uint16_t>(payload.size()));
        (void)requestMessage.append(payload.data(), static_cast<uint16_t>(payload.size()));
        return requestMessage;
    }

    /// Opens the connection to node index 0 (NODE_A) with a first request, up to the
    /// diagnostic message on the wire (not yet acknowledged).
    void openWithRequest(Bytes const& payload)
    {
        ASSERT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, payload), &processed));
        sockets[0].completeConnect(true);
        run();
        ASSERT_EQ(ACTIVATION_REQUEST, sockets[0].takeSent());
        sockets[0].acknowledge();
        sockets[0].receive(activationResponse(NODE_A));
        run();
        ASSERT_EQ(diagnostic(CLIENT, NODE_A, payload), sockets[0].takeSent());
    }

    NiceMock<::async::AsyncMock> asyncMock;
    ::async::ContextType asyncContext;
    ::async::TestContext testContext;
    uint32_t now = 1000U;
    std::array<DoIpClientNode, 2U> nodes;
    FakeSocket sockets[2];
    ::etl::vector<DoIpClientConnection, 2U> connections;
    DoIpClientTransportLayer layer;
    Provider provider;
    ProcessedRecorder processed;
    TransportMessage requestMessage;
    uint8_t requestBuffer[MAX_PAYLOAD];
};

// --- connection set-up and requests --------------------------------------------------------

TEST_F(DoIpClientTransportLayerTest, firstRequestConnectsActivatesAndSends)
{
    EXPECT_EQ(ErrorCode::TP_OK, layer.init());
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x22U, 0xF1U, 0x95U}), &processed));
    EXPECT_EQ(1, sockets[0].connects);
    EXPECT_EQ(::ip::make_ip4(0xC0A8001EU), sockets[0].lastAddress);
    EXPECT_EQ(13400U, sockets[0].lastPort);
    EXPECT_EQ(DoIpClientConnection::State::CONNECTING, connections[0].state());

    sockets[0].completeConnect(true);
    EXPECT_TRUE(sockets[0].nagleDisabled);
    EXPECT_EQ(DoIpClientConnection::State::ACTIVATING, connections[0].state());
    run();
    EXPECT_EQ(ACTIVATION_REQUEST, sockets[0].takeSent());

    sockets[0].receive(activationResponse(NODE_A));
    EXPECT_EQ(DoIpClientConnection::State::ACTIVE, connections[0].state());
    run();
    EXPECT_EQ(diagnostic(CLIENT, NODE_A, {0x22U, 0xF1U, 0x95U}), sockets[0].takeSent());
    EXPECT_TRUE(processed.results.empty());

    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_NO_ERROR, processed.results[0]);
    EXPECT_EQ(&requestMessage, processed.messages[0]);
    EXPECT_FALSE(connections[0].hasRequest());
}

TEST_F(DoIpClientTransportLayerTest, connectionIsReusedForLaterRequests)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));

    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x10U, 0x03U}), &processed));
    run();
    EXPECT_EQ(diagnostic(CLIENT, NODE_A, {0x10U, 0x03U}), sockets[0].takeSent());
    EXPECT_EQ(1, sockets[0].connects);
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));
    EXPECT_EQ(2U, processed.results.size());
}

TEST_F(DoIpClientTransportLayerTest, acknowledgementBeforeTcpReleaseWaitsForTheRelease)
{
    openWithRequest({0x3EU, 0x00U});
    // the node's ACK arrives before the send job is released: the message buffer is in use
    sockets[0].receive(ack(NODE_A));
    EXPECT_TRUE(processed.results.empty());
    sockets[0].acknowledge();
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_NO_ERROR, processed.results[0]);
}

TEST_F(DoIpClientTransportLayerTest, negativeAcknowledgementFailsTheRequest)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A, 0x8003U, 0x06U));
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_ERROR, processed.results[0]);
    // the connection stays open
    EXPECT_EQ(DoIpClientConnection::State::ACTIVE, connections[0].state());
}

TEST_F(DoIpClientTransportLayerTest, oneRequestPerNodeAndUnknownTargetsAreRejected)
{
    openWithRequest({0x3EU, 0x00U});
    EXPECT_EQ(
        ErrorCode::TP_MESSAGE_ALREADY_IN_PROGRESS,
        layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(0x1099U, {0x3EU, 0x00U}), &processed));
    EXPECT_EQ(nullptr, layer.findConnection(0x1099U));
    EXPECT_EQ(&connections[1], layer.findConnection(NODE_B));
    EXPECT_EQ(2U, layer.connections().size());
}

TEST_F(DoIpClientTransportLayerTest, connectNotStartedIsReportedToTheCaller)
{
    sockets[0].acceptConnect = false;
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    EXPECT_TRUE(processed.results.empty());
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
    EXPECT_FALSE(connections[0].hasRequest());
}

TEST_F(DoIpClientTransportLayerTest, refusedConnectionFailsTheRequestAndAllowsARetry)
{
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    sockets[0].completeConnect(false);
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_ERROR, processed.results[0]);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
    // a late connect callback is ignored
    sockets[0].completeConnect(false);
    EXPECT_EQ(1U, processed.results.size());

    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    EXPECT_EQ(2, sockets[0].connects);
}

TEST_F(DoIpClientTransportLayerTest, rejectedRoutingActivationFailsTheRequestAndCloses)
{
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    sockets[0].completeConnect(true);
    run();
    sockets[0].acknowledge();
    sockets[0].receive(activationResponse(NODE_A, 0x00U));
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_ERROR, processed.results[0]);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
    EXPECT_EQ(1, sockets[0].closes);
}

TEST_F(DoIpClientTransportLayerTest, deadlineFailsTheRequestAndClosesTheConnection)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    now += TIMEOUT_MS - 1U;
    layer.cyclic();
    EXPECT_TRUE(processed.results.empty());
    now += 1U;
    layer.cyclic();
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_ERROR, processed.results[0]);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
    EXPECT_EQ(1, sockets[0].closes);
}

TEST_F(DoIpClientTransportLayerTest, deadlineCoversConnectionSetUp)
{
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    now += TIMEOUT_MS;
    layer.cyclic();
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_ERROR, processed.results[0]);
    EXPECT_EQ(1, sockets[0].aborts);
}

TEST_F(DoIpClientTransportLayerTest, remoteCloseFailsThePendingRequestAndTheNextRequestReconnects)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].remoteClose();
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_ERROR, processed.results[0]);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());

    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    EXPECT_EQ(2, sockets[0].connects);
}

TEST_F(DoIpClientTransportLayerTest, shutdownClosesEveryConnection)
{
    openWithRequest({0x3EU, 0x00U});
    EXPECT_TRUE(layer.shutdown(AbstractTransportLayer::ShutdownDelegate()));
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_ERROR, processed.results[0]);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
}

// --- messages from the node ----------------------------------------------------------------

TEST_F(DoIpClientTransportLayerTest, diagnosticMessageFromTheNodeIsPassedToTheProvider)
{
    openWithRequest({0x22U, 0xF1U, 0x95U});
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));
    sockets[0].receive(diagnostic(NODE_A, CLIENT, {0x62U, 0xF1U, 0x95U, 0x01U}));
    ASSERT_EQ(1U, provider.received.size());
    EXPECT_EQ(BUS, provider.received[0].busId);
    EXPECT_EQ(NODE_A, provider.received[0].source);
    EXPECT_EQ(CLIENT, provider.received[0].target);
    EXPECT_EQ((Bytes{0x62U, 0xF1U, 0x95U, 0x01U}), provider.received[0].payload);
    EXPECT_EQ(4U, provider.requested[0].size);
    EXPECT_EQ(1, provider.releases);
}

TEST_F(DoIpClientTransportLayerTest, messagesNotForTheClientOrNotWantedAreDiscarded)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    // another target address
    sockets[0].receive(diagnostic(NODE_A, 0x0E80U, {0x7EU, 0x00U}));
    EXPECT_TRUE(provider.requested.empty());
    // the provider has no buffer for it (e.g. unsolicited)
    provider.accept = false;
    sockets[0].receive(diagnostic(NODE_A, CLIENT, {0x7EU, 0x00U}));
    EXPECT_EQ(1U, provider.requested.size());
    EXPECT_TRUE(provider.received.empty());
    // too large, unknown payload type, generic NACK and wrong protocol version are skipped
    sockets[0].receive(diagnostic(NODE_A, CLIENT, Bytes(MAX_PAYLOAD + 1U, 0x11U)));
    sockets[0].receive(frame(0x4002U, {0x01U, 0x02U, 0x03U}));
    sockets[0].receive(frame(0x0000U, {0x02U}));
    sockets[0].receive(frame(0x0006U, {0x01U, 0x02U}));
    sockets[0].receive(frame(0x8002U, {0x01U}));
    sockets[0].receive(diagnostic(NODE_A, CLIENT, {}));
    sockets[0].receive(frame(0x8002U, {0x10U, 0x40U, 0x0EU, 0x10U, 0x00U}, 0x03U));
    EXPECT_EQ(1U, provider.requested.size());
    EXPECT_TRUE(processed.results.empty());
    // the stream is still in sync: the request's ACK is processed
    sockets[0].receive(ack(NODE_A));
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_NO_ERROR, processed.results[0]);
    // responses are taken again
    provider.accept = true;
    sockets[0].receive(diagnostic(NODE_A, CLIENT, {0x7EU, 0x00U}));
    EXPECT_EQ(1U, provider.received.size());
}

TEST_F(DoIpClientTransportLayerTest, aliveCheckIsAnsweredAndTheStreamStaysInSync)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    // empty payload: the next header must still be read
    sockets[0].receive(frame(0x0007U, {}));
    run();
    EXPECT_EQ(frame(0x0008U, {0x0EU, 0x10U}), sockets[0].takeSent());
    sockets[0].receive(ack(NODE_A));
    ASSERT_EQ(1U, processed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_NO_ERROR, processed.results[0]);
}

TEST_F(DoIpClientTransportLayerTest, unexpectedAcknowledgementsAreIgnored)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));
    // no message waits for an acknowledgement
    sockets[0].receive(ack(NODE_A));
    EXPECT_EQ(1U, processed.results.size());
    // an activation response outside the activation is ignored
    sockets[0].receive(activationResponse(NODE_A, 0x00U));
    EXPECT_EQ(DoIpClientConnection::State::ACTIVE, connections[0].state());
}

// --- functional requests -------------------------------------------------------------------

TEST_F(DoIpClientTransportLayerTest, functionalRequestGoesToNodesWithActiveRouting)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));

    ProcessedRecorder functionalProcessed;
    EXPECT_EQ(
        ErrorCode::TP_OK, layer.send(message(FUNCTIONAL, {0x3EU, 0x00U}), &functionalProcessed));
    EXPECT_EQ(0, sockets[1].connects); // node B is not connected: not part of it
    EXPECT_EQ(
        ErrorCode::TP_MESSAGE_ALREADY_IN_PROGRESS,
        layer.send(message(FUNCTIONAL, {0x3EU, 0x00U}), &functionalProcessed));
    run();
    EXPECT_EQ(diagnostic(CLIENT, FUNCTIONAL, {0x3EU, 0x00U}), sockets[0].takeSent());
    EXPECT_TRUE(functionalProcessed.results.empty());
    sockets[0].acknowledge();
    ASSERT_EQ(1U, functionalProcessed.results.size());
    EXPECT_EQ(ProcessingResult::PROCESSED_NO_ERROR, functionalProcessed.results[0]);

    // the functional ACK comes first; it does not complete the next physical request
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A, {0x3EU, 0x00U}), &processed));
    run();
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));
    EXPECT_EQ(1U, processed.results.size());
    sockets[0].receive(ack(NODE_A));
    EXPECT_EQ(2U, processed.results.size());
}

TEST_F(DoIpClientTransportLayerTest, functionalRequestWithoutActiveRoutingIsNotSent)
{
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(FUNCTIONAL, {0x3EU, 0x00U}), &processed));
    // a node with a request in progress is skipped as well
    openWithRequest({0x3EU, 0x00U});
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(FUNCTIONAL, {0x3EU, 0x00U}), &processed));
    EXPECT_TRUE(processed.results.empty());
}

TEST_F(DoIpClientTransportLayerTest, functionalCopyReleasedByACloseCompletesTheMessage)
{
    openWithRequest({0x3EU, 0x00U});
    sockets[0].acknowledge();
    sockets[0].receive(ack(NODE_A));
    ProcessedRecorder functionalProcessed;
    EXPECT_EQ(
        ErrorCode::TP_OK, layer.send(message(FUNCTIONAL, {0x3EU, 0x00U}), &functionalProcessed));
    connections[0].close();
    ASSERT_EQ(1U, functionalProcessed.results.size());
    // released copies count once only
    layer.functionalCopyReleased();
    EXPECT_EQ(1U, functionalProcessed.results.size());
}

} // namespace
