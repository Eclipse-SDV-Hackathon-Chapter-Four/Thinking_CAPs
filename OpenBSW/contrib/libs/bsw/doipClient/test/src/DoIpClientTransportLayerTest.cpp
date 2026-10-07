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

#include "doip/client/DoIpClientTransportLayer.h"

#include <async/AsyncMock.h>
#include <async/TestContext.h>
#include <tcp/socket/AbstractSocketMock.h>
#include <transport/TransportMessageProcessedListenerMock.h>
#include <transport/TransportMessageProvidingListenerMock.h>

#include <etl/vector.h>
#include <gmock/gmock.h>

#include <array>
#include <vector>

namespace
{
using namespace ::doip;
using namespace ::testing;
using ::transport::AbstractTransportLayer;
using ::transport::ITransportMessageProcessedListener;
using ::transport::TransportMessage;
using Bytes            = std::vector<uint8_t>;
using ProcessingResult = ITransportMessageProcessedListener::ProcessingResult;
using ErrorCode        = AbstractTransportLayer::ErrorCode;
using SocketError      = ::tcp::AbstractSocket::ErrorCode;
using ProviderError    = ::transport::ITransportMessageProvider::ErrorCode;
using ReceiveResult    = ::transport::ITransportMessageListener::ReceiveResult;

uint8_t const BUS          = 5U;
uint16_t const CLIENT      = 0x0E10U;
uint16_t const FUNCTIONAL  = 0xE400U;
uint16_t const NODE_A      = 0x1040U;
uint16_t const NODE_B      = 0x1050U;
uint16_t const PORT        = 13400U;
uint32_t const TIMEOUT_MS  = 1500U;
uint16_t const MAX_PAYLOAD = 64U;

Bytes const ACTIVATION_REQUEST
    = {0x02, 0xFD, 0x00, 0x05, 0x00, 0x00, 0x00, 0x07, 0x0E, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00};
Bytes const ACTIVATION_OK
    = {0x02, 0xFD, 0x00, 0x06, 0x00, 0x00, 0x00, 0x09, 0x0E, 0x10, 0x10, 0x40, 0x10, 0, 0, 0, 0};
Bytes const ACTIVATION_REFUSED
    = {0x02, 0xFD, 0x00, 0x06, 0x00, 0x00, 0x00, 0x09, 0x0E, 0x10, 0x10, 0x40, 0x00, 0, 0, 0, 0};
Bytes const ACK_A  = {0x02, 0xFD, 0x80, 0x02, 0x00, 0x00, 0x00, 0x05, 0x10, 0x40, 0x0E, 0x10, 0x00};
Bytes const NACK_A = {0x02, 0xFD, 0x80, 0x03, 0x00, 0x00, 0x00, 0x05, 0x10, 0x40, 0x0E, 0x10, 0x06};
/// 3E 00 from the client to NODE_A, and to the functional address
Bytes const REQUEST_A
    = {0x02, 0xFD, 0x80, 0x01, 0x00, 0x00, 0x00, 0x06, 0x0E, 0x10, 0x10, 0x40, 0x3E, 0x00};
Bytes const REQUEST_FUNCTIONAL
    = {0x02, 0xFD, 0x80, 0x01, 0x00, 0x00, 0x00, 0x06, 0x0E, 0x10, 0xE4, 0x00, 0x3E, 0x00};
/// 7E 00 from NODE_A to the client
Bytes const RESPONSE_A
    = {0x02, 0xFD, 0x80, 0x01, 0x00, 0x00, 0x00, 0x06, 0x10, 0x40, 0x0E, 0x10, 0x7E, 0x00};
Bytes const RESPONSE_TO_OTHER_TESTER
    = {0x02, 0xFD, 0x80, 0x01, 0x00, 0x00, 0x00, 0x06, 0x10, 0x40, 0x0E, 0x80, 0x7E, 0x00};
Bytes const ALIVE_CHECK_REQUEST  = {0x02, 0xFD, 0x00, 0x07, 0x00, 0x00, 0x00, 0x00};
Bytes const ALIVE_CHECK_RESPONSE = {0x02, 0xFD, 0x00, 0x08, 0x00, 0x00, 0x00, 0x02, 0x0E, 0x10};

/** Collects what a socket mock sends, and how much of it the TCP peer has not acknowledged. */
struct SentData
{
    SocketError send(::etl::span<uint8_t const> const& data)
    {
        bytes.insert(bytes.end(), data.begin(), data.end());
        unacknowledged += data.size();
        return SocketError::SOCKET_ERR_OK;
    }

    Bytes take()
    {
        Bytes result;
        result.swap(bytes);
        return result;
    }

    Bytes bytes;
    size_t unacknowledged = 0U;
};

class DoIpClientTransportLayerTest : public Test
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
              PORT,
              TIMEOUT_MS,
              MAX_PAYLOAD},
          connections,
          DoIpClientTransportLayer::NowMsType::
              create<DoIpClientTransportLayerTest, &DoIpClientTransportLayerTest::nowMs>(*this))
    {
        for (size_t i = 0U; i < nodes.size(); ++i)
        {
            connections.emplace_back(layer, nodes[i], sockets[i], asyncContext);
            // AbstractSocketMock starts with an empty read window without data pointer, which
            // inject() would extend; an empty read resets both windows to the injection buffer
            (void)sockets[i].readImplementation(nullptr, 0U);
            EXPECT_CALL(sockets[i], read(_, _))
                .Times(AnyNumber())
                .WillRepeatedly(
                    Invoke(&sockets[i], &::tcp::AbstractSocketMock::readImplementation));
            EXPECT_CALL(sockets[i], send(_))
                .Times(AnyNumber())
                .WillRepeatedly(Invoke(&sent[i], &SentData::send));
            EXPECT_CALL(sockets[i], flush())
                .Times(AnyNumber())
                .WillRepeatedly(Return(SocketError::SOCKET_ERR_OK));
        }
        layer.fProvidingListenerHelper.fpMessageProvider = &provider;
        layer.fProvidingListenerHelper.fpMessageListener = &provider;
        responseMessage.init(responseBuffer, sizeof(responseBuffer));
    }

    void SetUp() override { testContext.handleAll(); }

    uint32_t nowMs() { return now; }

    /// Runs the send jobs queued on the connections.
    void run() { testContext.expireAndExecute(); }

    TransportMessage& message(uint16_t const target)
    {
        uint8_t const payload[] = {0x3E, 0x00};
        requestMessage.init(requestBuffer, sizeof(requestBuffer));
        requestMessage.setSourceAddress(CLIENT);
        requestMessage.setTargetAddress(target);
        requestMessage.setPayloadLength(sizeof(payload));
        (void)requestMessage.append(payload, sizeof(payload));
        return requestMessage;
    }

    void expectConnect(size_t const index)
    {
        EXPECT_CALL(sockets[index], isClosed()).WillOnce(Return(true));
        EXPECT_CALL(sockets[index], connect(nodes[index].address, PORT, _))
            .WillOnce(DoAll(SaveArg<2>(&connected[index]), Return(SocketError::SOCKET_ERR_OK)));
    }

    void completeConnect(size_t const index)
    {
        EXPECT_CALL(sockets[index], disableNagleAlgorithm());
        EXPECT_CALL(sockets[index], isEstablished()).WillOnce(Return(true));
        connected[index](SocketError::SOCKET_ERR_OK);
    }

    void receive(size_t const index, Bytes const& data)
    {
        (void)sockets[index].inject(::etl::span<uint8_t const>(data.data(), data.size()));
    }

    /// The TCP peer acknowledges everything sent so far.
    void acknowledgeTcp(size_t const index)
    {
        size_t const length        = sent[index].unacknowledged;
        sent[index].unacknowledged = 0U;
        sockets[index].signalDataSent(length);
    }

    /// Opens the connection to NODE_A with a request for it, up to the diagnostic message on
    /// the wire (neither released by TCP nor acknowledged by the node).
    void openWithRequest()
    {
        expectConnect(0U);
        ASSERT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
        completeConnect(0U);
        run();
        ASSERT_EQ(ACTIVATION_REQUEST, sent[0].take());
        acknowledgeTcp(0U);
        receive(0U, ACTIVATION_OK);
        run();
        ASSERT_EQ(REQUEST_A, sent[0].take());
    }

    /// openWithRequest(), completed by the TCP release and the node's acknowledgement.
    void openAndComplete()
    {
        openWithRequest();
        EXPECT_CALL(
            processed,
            transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_NO_ERROR));
        acknowledgeTcp(0U);
        receive(0U, ACK_A);
        Mock::VerifyAndClearExpectations(&processed);
    }

    StrictMock<::async::AsyncMock> asyncMock;
    ::async::ContextType asyncContext;
    ::async::TestContext testContext;
    uint32_t now = 1000U;
    std::array<DoIpClientNode, 2U> nodes;
    StrictMock<::tcp::AbstractSocketMock> sockets[2];
    SentData sent[2];
    ::tcp::AbstractSocket::ConnectedDelegate connected[2];
    ::etl::vector<DoIpClientConnection, 2U> connections;
    DoIpClientTransportLayer layer;
    StrictMock<::transport::TransportMessageProvidingListenerMock> provider{false};
    StrictMock<::transport::TransportMessageProcessedListenerMock> processed;
    TransportMessage requestMessage;
    uint8_t requestBuffer[MAX_PAYLOAD];
    TransportMessage responseMessage;
    uint8_t responseBuffer[MAX_PAYLOAD];
};

// --- connection set-up and requests --------------------------------------------------------

/**
 * Test that the first request to a node opens the connection and activates routing.
 *
 * The client connects to the node's address on the configured port, disables Nagle's
 * algorithm, requests routing activation with its own address and type 0x00, and sends the
 * request as a diagnostic message once the node accepts the activation (code 0x10). The
 * request is processed successfully when TCP has released it and the node acknowledged it.
 */
TEST_F(DoIpClientTransportLayerTest, FirstRequestConnectsActivatesAndSends)
{
    EXPECT_EQ(ErrorCode::TP_OK, layer.init());
    expectConnect(0U);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
    EXPECT_EQ(DoIpClientConnection::State::CONNECTING, connections[0].state());

    completeConnect(0U);
    EXPECT_EQ(DoIpClientConnection::State::ACTIVATING, connections[0].state());
    run();
    EXPECT_EQ(ACTIVATION_REQUEST, sent[0].take());

    acknowledgeTcp(0U);
    receive(0U, ACTIVATION_OK);
    EXPECT_EQ(DoIpClientConnection::State::ACTIVE, connections[0].state());
    run();
    EXPECT_EQ(REQUEST_A, sent[0].take());

    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_NO_ERROR));
    acknowledgeTcp(0U);
    receive(0U, ACK_A);
    EXPECT_FALSE(connections[0].hasRequest());
}

/**
 * Test that later requests reuse the open connection without a new routing activation.
 */
TEST_F(DoIpClientTransportLayerTest, ConnectionIsReusedForLaterRequests)
{
    openAndComplete();
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
    run();
    EXPECT_EQ(REQUEST_A, sent[0].take());
}

/**
 * Test that a request is processed only after both the TCP release and the node's ACK.
 *
 * The send job references the request buffer until TCP releases it, so an acknowledgement
 * that arrives first must not complete the request.
 */
TEST_F(DoIpClientTransportLayerTest, AcknowledgementBeforeTcpReleaseWaitsForTheRelease)
{
    openWithRequest();
    receive(0U, ACK_A);
    EXPECT_TRUE(connections[0].hasRequest());
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_NO_ERROR));
    acknowledgeTcp(0U);
}

/**
 * Test that a negative acknowledgement of the node fails the request and keeps the
 * connection open.
 */
TEST_F(DoIpClientTransportLayerTest, NegativeAcknowledgementFailsTheRequest)
{
    openWithRequest();
    acknowledgeTcp(0U);
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_ERROR));
    receive(0U, NACK_A);
    EXPECT_EQ(DoIpClientConnection::State::ACTIVE, connections[0].state());
}

/**
 * Test that a node takes one request at a time and that unknown targets are rejected.
 */
TEST_F(DoIpClientTransportLayerTest, OneRequestPerNodeAndUnknownTargetsAreRejected)
{
    openWithRequest();
    EXPECT_EQ(ErrorCode::TP_MESSAGE_ALREADY_IN_PROGRESS, layer.send(message(NODE_A), &processed));
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(0x1099U), &processed));
    EXPECT_EQ(nullptr, layer.findConnection(0x1099U));
    EXPECT_EQ(&connections[1], layer.findConnection(NODE_B));
    EXPECT_EQ(2U, layer.connections().size());
}

// --- connection failures --------------------------------------------------------------------

/**
 * Test that a connect that cannot be started is reported to the caller of send().
 */
TEST_F(DoIpClientTransportLayerTest, ConnectNotStartedIsReportedToTheCaller)
{
    EXPECT_CALL(sockets[0], isClosed()).WillOnce(Return(true));
    EXPECT_CALL(sockets[0], connect(_, PORT, _)).WillOnce(Return(SocketError::SOCKET_ERR_NOT_OK));
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(NODE_A), &processed));
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
    EXPECT_FALSE(connections[0].hasRequest());
}

/**
 * Test that a refused connection fails the request and that the next request connects again.
 *
 * A late connect callback after the failure is ignored.
 */
TEST_F(DoIpClientTransportLayerTest, RefusedConnectionFailsTheRequestAndAllowsARetry)
{
    expectConnect(0U);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_ERROR));
    EXPECT_CALL(sockets[0], abort());
    connected[0](SocketError::SOCKET_ERR_NOT_OK);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
    connected[0](SocketError::SOCKET_ERR_NOT_OK);

    expectConnect(0U);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
}

/**
 * Test that a refused routing activation fails the request and closes the connection.
 */
TEST_F(DoIpClientTransportLayerTest, RejectedRoutingActivationFailsTheRequestAndCloses)
{
    expectConnect(0U);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
    completeConnect(0U);
    run();
    acknowledgeTcp(0U);
    EXPECT_CALL(sockets[0], close()).WillOnce(Return(SocketError::SOCKET_ERR_OK));
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_ERROR));
    receive(0U, ACTIVATION_REFUSED);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
}

/**
 * Test that a request without acknowledgement fails at its deadline and closes the
 * connection.
 */
TEST_F(DoIpClientTransportLayerTest, DeadlineFailsTheRequestAndClosesTheConnection)
{
    openWithRequest();
    acknowledgeTcp(0U);
    now += TIMEOUT_MS - 1U;
    layer.cyclic();
    EXPECT_TRUE(connections[0].hasRequest());

    EXPECT_CALL(sockets[0], close()).WillOnce(Return(SocketError::SOCKET_ERR_OK));
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_ERROR));
    now += 1U;
    layer.cyclic();
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
}

/**
 * Test that the deadline also covers the connection set-up.
 */
TEST_F(DoIpClientTransportLayerTest, DeadlineCoversConnectionSetUp)
{
    expectConnect(0U);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
    EXPECT_CALL(sockets[0], abort());
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_ERROR));
    now += TIMEOUT_MS;
    layer.cyclic();
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
}

/**
 * Test that a connection closed by the node fails the pending request and that the next
 * request connects again.
 */
TEST_F(DoIpClientTransportLayerTest, RemoteCloseFailsThePendingRequestAndTheNextRequestReconnects)
{
    openWithRequest();
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_ERROR));
    sockets[0].signalClosed(::tcp::IDataListener::ErrorCode::ERR_CONNECTION_CLOSED);
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());

    expectConnect(0U);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
}

/**
 * Test that shutdown closes every connection and fails a request in progress.
 */
TEST_F(DoIpClientTransportLayerTest, ShutdownClosesEveryConnection)
{
    openWithRequest();
    EXPECT_CALL(sockets[0], close()).WillOnce(Return(SocketError::SOCKET_ERR_OK));
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_ERROR));
    EXPECT_TRUE(layer.shutdown(AbstractTransportLayer::ShutdownDelegate()));
    EXPECT_EQ(DoIpClientConnection::State::CLOSED, connections[0].state());
}

// --- messages from the node ----------------------------------------------------------------

/**
 * Test that a diagnostic message of the node is passed to the provider.
 *
 * The message gets the node as source and the client as target; when the provider reports
 * it as processed, it is released.
 */
TEST_F(DoIpClientTransportLayerTest, DiagnosticMessageFromTheNodeIsPassedToTheProvider)
{
    openAndComplete();
    ITransportMessageProcessedListener* listener = nullptr;
    EXPECT_CALL(provider, getTransportMessage(BUS, NODE_A, CLIENT, 2U, _, _))
        .WillOnce(DoAll(SetArgReferee<5>(&responseMessage), Return(ProviderError::TPMSG_OK)));
    EXPECT_CALL(provider, messageReceived(BUS, Ref(responseMessage), _))
        .WillOnce(DoAll(SaveArg<2>(&listener), Return(ReceiveResult::RECEIVED_NO_ERROR)));
    receive(0U, RESPONSE_A);
    EXPECT_EQ(NODE_A, responseMessage.getSourceId());
    EXPECT_EQ(CLIENT, responseMessage.getTargetId());
    EXPECT_EQ(
        (Bytes{0x7E, 0x00}), Bytes(responseMessage.getPayload(), responseMessage.getPayload() + 2));

    EXPECT_CALL(provider, releaseTransportMessage(Ref(responseMessage)));
    listener->transportMessageProcessed(responseMessage, ProcessingResult::PROCESSED_NO_ERROR);
}

/**
 * Test that a message the provider does not take is released when its listener refuses it.
 */
TEST_F(DoIpClientTransportLayerTest, MessageRefusedByTheListenerIsReleased)
{
    openAndComplete();
    EXPECT_CALL(provider, getTransportMessage(BUS, NODE_A, CLIENT, 2U, _, _))
        .WillOnce(DoAll(SetArgReferee<5>(&responseMessage), Return(ProviderError::TPMSG_OK)));
    EXPECT_CALL(provider, messageReceived(BUS, Ref(responseMessage), _))
        .WillOnce(Return(ReceiveResult::RECEIVED_ERROR));
    EXPECT_CALL(provider, releaseTransportMessage(Ref(responseMessage)));
    receive(0U, RESPONSE_A);
}

/**
 * Test that messages the client does not process are skipped and the stream stays in sync.
 *
 * Skipped: a diagnostic message to another tester, one the provider does not want, one larger
 * than the maximum payload, one without user data, an unknown payload type, a generic header
 * NACK, a too short activation response or acknowledgement, and a wrong protocol version. The
 * acknowledgement that follows them still completes the request.
 */
TEST_F(DoIpClientTransportLayerTest, MessagesNotForTheClientOrNotWantedAreSkipped)
{
    openWithRequest();
    acknowledgeTcp(0U);
    receive(0U, RESPONSE_TO_OTHER_TESTER);
    EXPECT_CALL(provider, getTransportMessage(BUS, NODE_A, CLIENT, 2U, _, _))
        .WillOnce(Return(ProviderError::TPMSG_NOT_RESPONSIBLE));
    receive(0U, RESPONSE_A);
    Bytes tooLarge
        = {0x02, 0xFD, 0x80, 0x01, 0x00, 0x00, 0x00, MAX_PAYLOAD + 5U, 0x10, 0x40, 0x0E, 0x10};
    tooLarge.resize(tooLarge.size() + MAX_PAYLOAD + 1U, 0x11U);
    receive(0U, tooLarge);
    receive(0U, {0x02, 0xFD, 0x80, 0x01, 0x00, 0x00, 0x00, 0x04, 0x10, 0x40, 0x0E, 0x10});
    receive(0U, {0x02, 0xFD, 0x40, 0x02, 0x00, 0x00, 0x00, 0x03, 0x01, 0x02, 0x03});
    receive(0U, {0x02, 0xFD, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x02});
    receive(0U, {0x02, 0xFD, 0x00, 0x06, 0x00, 0x00, 0x00, 0x02, 0x01, 0x02});
    receive(0U, {0x02, 0xFD, 0x80, 0x02, 0x00, 0x00, 0x00, 0x01, 0x01});
    receive(0U, {0x03, 0xFC, 0x80, 0x02, 0x00, 0x00, 0x00, 0x05, 0x10, 0x40, 0x0E, 0x10, 0x00});
    EXPECT_TRUE(connections[0].hasRequest());

    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_NO_ERROR));
    receive(0U, ACK_A);
}

/**
 * Test that an alive check request is answered and that the following message is read.
 *
 * The alive check request has an empty payload; skipping it must not stop the reception.
 */
TEST_F(DoIpClientTransportLayerTest, AliveCheckIsAnsweredAndTheStreamStaysInSync)
{
    openWithRequest();
    acknowledgeTcp(0U);
    receive(0U, ALIVE_CHECK_REQUEST);
    run();
    EXPECT_EQ(ALIVE_CHECK_RESPONSE, sent[0].take());
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_NO_ERROR));
    receive(0U, ACK_A);
}

/**
 * Test that acknowledgements and activation responses that nothing waits for are ignored.
 */
TEST_F(DoIpClientTransportLayerTest, UnexpectedAcknowledgementsAreIgnored)
{
    openAndComplete();
    receive(0U, ACK_A);
    receive(0U, ACTIVATION_REFUSED);
    EXPECT_EQ(DoIpClientConnection::State::ACTIVE, connections[0].state());
}

// --- functional requests -------------------------------------------------------------------

/**
 * Test that a functional request goes to every node with active routing.
 *
 * Node B is not connected and gets no copy. The message is processed when every copy is
 * released by TCP, and a second functional request is rejected until then. The node's
 * acknowledgement of the functional copy comes before the one of the next physical request
 * and does not complete it.
 */
TEST_F(DoIpClientTransportLayerTest, FunctionalRequestGoesToNodesWithActiveRouting)
{
    openAndComplete();
    StrictMock<::transport::TransportMessageProcessedListenerMock> functionalProcessed;
    TransportMessage& functional = message(FUNCTIONAL);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(functional, &functionalProcessed));
    EXPECT_EQ(
        ErrorCode::TP_MESSAGE_ALREADY_IN_PROGRESS, layer.send(functional, &functionalProcessed));
    run();
    EXPECT_EQ(REQUEST_FUNCTIONAL, sent[0].take());

    EXPECT_CALL(
        functionalProcessed,
        transportMessageProcessed(Ref(functional), ProcessingResult::PROCESSED_NO_ERROR));
    acknowledgeTcp(0U);

    EXPECT_EQ(ErrorCode::TP_OK, layer.send(message(NODE_A), &processed));
    run();
    acknowledgeTcp(0U);
    receive(0U, ACK_A);
    EXPECT_TRUE(connections[0].hasRequest());
    EXPECT_CALL(
        processed,
        transportMessageProcessed(Ref(requestMessage), ProcessingResult::PROCESSED_NO_ERROR));
    receive(0U, ACK_A);
}

/**
 * Test that a functional request is not sent without a node with active routing and no
 * request in progress.
 */
TEST_F(DoIpClientTransportLayerTest, FunctionalRequestWithoutActiveRoutingIsNotSent)
{
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(FUNCTIONAL), &processed));
    openWithRequest();
    EXPECT_EQ(ErrorCode::TP_SEND_FAIL, layer.send(message(FUNCTIONAL), &processed));
}

/**
 * Test that a functional copy released by a closed connection completes the message once.
 */
TEST_F(DoIpClientTransportLayerTest, FunctionalCopyReleasedByACloseCompletesTheMessage)
{
    openAndComplete();
    StrictMock<::transport::TransportMessageProcessedListenerMock> functionalProcessed;
    TransportMessage& functional = message(FUNCTIONAL);
    EXPECT_EQ(ErrorCode::TP_OK, layer.send(functional, &functionalProcessed));
    EXPECT_CALL(sockets[0], close()).WillOnce(Return(SocketError::SOCKET_ERR_OK));
    EXPECT_CALL(
        functionalProcessed,
        transportMessageProcessed(Ref(functional), ProcessingResult::PROCESSED_NO_ERROR));
    connections[0].close();
    layer.functionalCopyReleased();
}

} // namespace
