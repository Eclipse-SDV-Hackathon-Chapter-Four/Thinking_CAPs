/********************************************************************************
 * Copyright (c) 2026 Jefferson Nascimento
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

#include "doip/client/DoIpClientConnection.h"

#include "doip/client/DoIpClientLogger.h"
#include "doip/client/DoIpClientTransportLayer.h"

#include <doip/common/DoIpHeader.h>

// NOLINTBEGIN(cppcoreguidelines-pro-type-vararg): Logger API is variadic by design.

namespace doip
{
using ::transport::ITransportMessageProcessedListener;
using ::transport::TransportMessage;
using ::util::logger::DOIPCLIENT;
using ::util::logger::Logger;

namespace
{
uint16_t read16(::etl::span<uint8_t const> const data, size_t const offset)
{
    return static_cast<uint16_t>(
        (static_cast<uint16_t>(data[offset]) << 8U) | static_cast<uint16_t>(data[offset + 1U]));
}

void write16(::etl::span<uint8_t> const data, size_t const offset, uint16_t const value)
{
    data[offset]      = static_cast<uint8_t>(value >> 8U);
    data[offset + 1U] = static_cast<uint8_t>(value & 0xFFU);
}

bool expired(uint32_t const now, uint32_t const deadline)
{
    return static_cast<int32_t>(now - deadline) >= 0;
}

char const* nameOf(DoIpClientNode const& node) { return (node.name != nullptr) ? node.name : ""; }
} // namespace

DoIpClientConnection::DoIpClientConnection(
    DoIpClientTransportLayer& layer,
    DoIpClientNode const& node,
    ::tcp::AbstractSocket& socket,
    ::async::ContextType const context)
: _layer(layer)
, _node(node)
, _socket(socket)
, _writeBuffer()
, _connection(context, socket, ::etl::span<uint8_t>(_writeBuffer))
, _activationJob(
      static_cast<uint8_t>(layer.parameters().protocolVersion),
      DoIpConstants::PayloadTypes::ROUTING_ACTIVATION_REQUEST,
      ACTIVATION_REQUEST_LENGTH,
      StaticJob::ReleaseCallbackType::
          create<DoIpClientConnection, &DoIpClientConnection::activationJobReleased>(*this))
, _aliveJob(
      static_cast<uint8_t>(layer.parameters().protocolVersion),
      DoIpConstants::PayloadTypes::ALIVE_CHECK_RESPONSE,
      2U,
      StaticJob::ReleaseCallbackType::
          create<DoIpClientConnection, &DoIpClientConnection::aliveJobReleased>(*this))
, _requestJob()
, _functionalJob()
, _pendingAcks()
, _request(nullptr)
, _requestListener(nullptr)
, _deadline(0U)
, _requestSent(false)
, _requestReleased(false)
, _ackReceived(false)
, _ackPositive(false)
, _activationJobBusy(false)
, _aliveJobBusy(false)
, _functionalJobBusy(false)
, _rxBuffer()
, _rxPayloadType(0U)
, _rxLength(0U)
, _rxSource(0U)
, _rxMessage(nullptr)
, _state(State::CLOSED)
{
    uint16_t const source                 = layer.parameters().sourceAddress;
    // routing activation request: source address, activation type 0x00 (default), reserved
    ::etl::span<uint8_t> const activation = _activationJob.accessPayloadBuffer();
    write16(activation, 0U, source);
    for (size_t i = 2U; i < ACTIVATION_REQUEST_LENGTH; ++i)
    {
        activation[i] = 0U;
    }
    write16(_aliveJob.accessPayloadBuffer(), 0U, source);
}

bool DoIpClientConnection::request(
    TransportMessage& message,
    ITransportMessageProcessedListener* const listener,
    uint32_t const deadline)
{
    if (_request != nullptr)
    {
        return false;
    }
    _request         = &message;
    _requestListener = listener;
    _deadline        = deadline;
    _requestSent     = false;
    _requestReleased = false;
    _ackReceived     = false;
    _ackPositive     = false;
    switch (_state)
    {
        case State::CLOSED:
        {
            connect();
            if (_state == State::CLOSED)
            {
                // not started: the caller reports the failure
                _request         = nullptr;
                _requestListener = nullptr;
                return false;
            }
            break;
        }
        case State::ACTIVE:
        {
            sendRequest();
            break;
        }
        default:
        {
            // sent once routing is active
            break;
        }
    }
    return true;
}

bool DoIpClientConnection::functional(TransportMessage& message)
{
    if ((_state != State::ACTIVE) || (_request != nullptr) || _functionalJobBusy
        || _pendingAcks.full())
    {
        return false;
    }
    DoIpClientParameters const& parameters = _layer.parameters();
    (void)_functionalJob.emplace(
        parameters.protocolVersion,
        message,
        nullptr,
        parameters.sourceAddress,
        parameters.functionalAddress,
        *this);
    if (!_connection.sendMessage(*_functionalJob))
    {
        return false;
    }
    _functionalJobBusy = true;
    _pendingAcks.push(Ack::FUNCTIONAL);
    return true;
}

void DoIpClientConnection::cyclic(uint32_t const now)
{
    if ((_request != nullptr) && expired(now, _deadline))
    {
        closeAndFail(
            (_state == State::ACTIVE) ? "no acknowledgement in time"
                                      : "no routing activation in time");
    }
}

void DoIpClientConnection::close()
{
    State const previous = _state;
    _state               = State::CLOSED;
    if (previous == State::CONNECTING)
    {
        _socket.abort();
    }
    else if (previous != State::CLOSED)
    {
        // releases the queued send jobs and calls connectionClosed()
        _connection.close();
    }
    else
    {
        // nothing open
    }
    _pendingAcks.clear();
    if (_request != nullptr)
    {
        finishRequest(false);
    }
}

void DoIpClientConnection::connect()
{
    if (!_socket.isClosed())
    {
        _socket.abort();
    }
    _state                                        = State::CONNECTING;
    DoIpClientParameters const& parameters        = _layer.parameters();
    ::tcp::AbstractSocket::ErrorCode const result = _socket.connect(
        _node.address,
        parameters.port,
        ::tcp::AbstractSocket::ConnectedDelegate::
            create<DoIpClientConnection, &DoIpClientConnection::connected>(*this));
    if (result != ::tcp::AbstractSocket::ErrorCode::SOCKET_ERR_OK)
    {
        Logger::warn(
            DOIPCLIENT, "0x%04x (%s): connect not started", _node.logicalAddress, nameOf(_node));
        _state = State::CLOSED;
    }
}

void DoIpClientConnection::connected(::tcp::AbstractSocket::ErrorCode const result)
{
    if (_state != State::CONNECTING)
    {
        return;
    }
    if (result != ::tcp::AbstractSocket::ErrorCode::SOCKET_ERR_OK)
    {
        closeAndFail("connection refused or unreachable");
        return;
    }
    _state = State::ACTIVATING;
    // diagnostic messages are small: send them without waiting for earlier data to be acknowledged
    _socket.disableNagleAlgorithm();
    // calls connectionClosed() if the socket is not established
    _connection.init(*this);
    if (_state == State::ACTIVATING)
    {
        sendActivation();
    }
}

void DoIpClientConnection::sendActivation()
{
    if (_activationJobBusy || (!_connection.sendMessage(_activationJob)))
    {
        closeAndFail("routing activation request not sent");
        return;
    }
    _activationJobBusy = true;
}

void DoIpClientConnection::sendRequest()
{
    if (_pendingAcks.full())
    {
        closeAndFail("too many unacknowledged messages");
        return;
    }
    DoIpClientParameters const& parameters = _layer.parameters();
    (void)_requestJob.emplace(
        parameters.protocolVersion,
        *_request,
        nullptr,
        parameters.sourceAddress,
        _node.logicalAddress,
        *this);
    if (!_connection.sendMessage(*_requestJob))
    {
        closeAndFail("diagnostic message not sent");
        return;
    }
    _requestSent = true;
    _pendingAcks.push(Ack::REQUEST);
}

void DoIpClientConnection::tryFinishRequest()
{
    // the send job references the message buffer until it is released
    if (_requestReleased && _ackReceived)
    {
        finishRequest(_ackPositive);
    }
}

void DoIpClientConnection::finishRequest(bool const success)
{
    TransportMessage* const message                    = _request;
    ITransportMessageProcessedListener* const listener = _requestListener;
    _request                                           = nullptr;
    _requestListener                                   = nullptr;
    _requestSent                                       = false;
    if ((listener != nullptr) && (message != nullptr))
    {
        listener->transportMessageProcessed(
            *message,
            success ? ITransportMessageProcessedListener::ProcessingResult::PROCESSED_NO_ERROR
                    : ITransportMessageProcessedListener::ProcessingResult::PROCESSED_ERROR);
    }
}

void DoIpClientConnection::closeAndFail(char const* const reason)
{
    Logger::warn(DOIPCLIENT, "0x%04x (%s): %s", _node.logicalAddress, nameOf(_node), reason);
    close();
}

void DoIpClientConnection::sendAliveCheckResponse()
{
    if ((!_aliveJobBusy) && ((_state == State::ACTIVATING) || (_state == State::ACTIVE)))
    {
        _aliveJobBusy = _connection.sendMessage(_aliveJob);
    }
}

void DoIpClientConnection::activationJobReleased(StaticJob& /* job */, bool const /* success */)
{
    _activationJobBusy = false;
}

void DoIpClientConnection::aliveJobReleased(StaticJob& /* job */, bool const /* success */)
{
    _aliveJobBusy = false;
}

void DoIpClientConnection::connectionClosed(bool const closedByRemotePeer)
{
    bool const wasOpen = (_state != State::CLOSED);
    _state             = State::CLOSED;
    _pendingAcks.clear();
    if (_rxMessage != nullptr)
    {
        _layer.fProvidingListenerHelper.releaseTransportMessage(*_rxMessage);
        _rxMessage = nullptr;
    }
    if (wasOpen && closedByRemotePeer)
    {
        Logger::info(
            DOIPCLIENT,
            "0x%04x (%s): connection closed by the node",
            _node.logicalAddress,
            nameOf(_node));
    }
    if (_request != nullptr)
    {
        finishRequest(false);
    }
}

IDoIpConnectionHandler::HeaderReceivedContinuation
DoIpClientConnection::headerReceived(DoIpHeader const& header)
{
    uint16_t const payloadType   = header.payloadType;
    uint32_t const payloadLength = header.payloadLength;
    if (!checkProtocolVersion(header, static_cast<uint8_t>(_layer.parameters().protocolVersion)))
    {
        Logger::warn(
            DOIPCLIENT,
            "0x%04x (%s): protocol version 0x%02x ignored",
            _node.logicalAddress,
            nameOf(_node),
            header.protocolVersion);
        return skipPayload();
    }
    switch (payloadType)
    {
        case DoIpConstants::PayloadTypes::ROUTING_ACTIVATION_RESPONSE:
        {
            if (payloadLength >= ACTIVATION_RESPONSE_LENGTH)
            {
                (void)_connection.receivePayload(
                    ::etl::span<uint8_t>(_rxBuffer).subspan(0U, ACTIVATION_RESPONSE_LENGTH),
                    IDoIpConnection::PayloadReceivedCallbackType::create<
                        DoIpClientConnection,
                        &DoIpClientConnection::activationResponseReceived>(*this));
                return HandledByThisHandler{};
            }
            break;
        }
        case DoIpConstants::PayloadTypes::DIAGNOSTIC_MESSAGE_POSITIVE_ACK:
        case DoIpConstants::PayloadTypes::DIAGNOSTIC_MESSAGE_NEGATIVE_ACK:
        {
            if (payloadLength >= ACK_LENGTH)
            {
                _rxPayloadType = payloadType;
                (void)_connection.receivePayload(
                    ::etl::span<uint8_t>(_rxBuffer).subspan(0U, ACK_LENGTH),
                    IDoIpConnection::PayloadReceivedCallbackType::
                        create<DoIpClientConnection, &DoIpClientConnection::ackReceived>(*this));
                return HandledByThisHandler{};
            }
            break;
        }
        case DoIpConstants::PayloadTypes::DIAGNOSTIC_MESSAGE:
        {
            if ((payloadLength > ADDRESS_INFO_LENGTH)
                && ((payloadLength - ADDRESS_INFO_LENGTH) <= _layer.parameters().maxPayloadLength))
            {
                _rxLength = static_cast<uint16_t>(payloadLength - ADDRESS_INFO_LENGTH);
                (void)_connection.receivePayload(
                    ::etl::span<uint8_t>(_rxBuffer).subspan(0U, ADDRESS_INFO_LENGTH),
                    IDoIpConnection::PayloadReceivedCallbackType::
                        create<DoIpClientConnection, &DoIpClientConnection::addressInfoReceived>(
                            *this));
                return HandledByThisHandler{};
            }
            Logger::warn(
                DOIPCLIENT,
                "0x%04x (%s): diagnostic message of %d bytes discarded",
                _node.logicalAddress,
                nameOf(_node),
                static_cast<int>(payloadLength));
            break;
        }
        case DoIpConstants::PayloadTypes::ALIVE_CHECK_REQUEST:
        {
            sendAliveCheckResponse();
            break;
        }
        case DoIpConstants::PayloadTypes::NEGATIVE_ACK:
        {
            Logger::warn(
                DOIPCLIENT,
                "0x%04x (%s): generic header negative acknowledgement",
                _node.logicalAddress,
                nameOf(_node));
            break;
        }
        default:
        {
            break;
        }
    }
    return skipPayload();
}

void DoIpClientConnection::activationResponseReceived(::etl::span<uint8_t const> const payload)
{
    _connection.endReceiveMessage(discard());
    if (_state != State::ACTIVATING)
    {
        return;
    }
    uint16_t const tester = read16(payload, 0U);
    uint16_t const entity = read16(payload, 2U);
    uint8_t const code    = payload[4U];
    if ((code != DoIpConstants::RoutingResponseCodes::ROUTING_SUCCESS)
        || (tester != _layer.parameters().sourceAddress))
    {
        Logger::warn(
            DOIPCLIENT,
            "0x%04x (%s): routing activation rejected, code 0x%02x",
            _node.logicalAddress,
            nameOf(_node),
            code);
        close();
        return;
    }
    _state = State::ACTIVE;
    Logger::info(
        DOIPCLIENT,
        "0x%04x (%s): routing active, DoIP entity 0x%04x",
        _node.logicalAddress,
        nameOf(_node),
        entity);
    if ((_request != nullptr) && (!_requestSent))
    {
        sendRequest();
    }
}

void DoIpClientConnection::ackReceived(::etl::span<uint8_t const> const payload)
{
    _connection.endReceiveMessage(discard());
    if (_pendingAcks.empty())
    {
        return;
    }
    Ack const kind = _pendingAcks.front();
    _pendingAcks.pop();
    if ((kind != Ack::REQUEST) || (_request == nullptr))
    {
        return;
    }
    _ackReceived = true;
    _ackPositive = (_rxPayloadType == DoIpConstants::PayloadTypes::DIAGNOSTIC_MESSAGE_POSITIVE_ACK);
    if (!_ackPositive)
    {
        Logger::warn(
            DOIPCLIENT,
            "0x%04x (%s): diagnostic message rejected, code 0x%02x",
            _node.logicalAddress,
            nameOf(_node),
            payload[4U]);
    }
    tryFinishRequest();
}

void DoIpClientConnection::addressInfoReceived(::etl::span<uint8_t const> const payload)
{
    _rxSource                 = read16(payload, 0U);
    uint16_t const target     = read16(payload, 2U);
    TransportMessage* message = nullptr;
    if ((_state == State::ACTIVE) && (target == _layer.parameters().sourceAddress))
    {
        (void)_layer.fProvidingListenerHelper.getTransportMessage(
            _layer.getBusId(), _rxSource, target, _rxLength, {}, message);
    }
    if (message == nullptr)
    {
        // not addressed to the client or not wanted by the provider (e.g. unsolicited)
        _connection.endReceiveMessage(discard());
        return;
    }
    message->resetValidBytes();
    message->setSourceAddress(_rxSource);
    message->setTargetAddress(target);
    message->setPayloadLength(_rxLength);
    _rxMessage = message;
    (void)_connection.receivePayload(
        ::etl::span<uint8_t>(message->getBuffer(), _rxLength),
        IDoIpConnection::PayloadReceivedCallbackType::
            create<DoIpClientConnection, &DoIpClientConnection::diagnosticPayloadReceived>(*this));
}

void DoIpClientConnection::diagnosticPayloadReceived(::etl::span<uint8_t const> const /* payload */)
{
    TransportMessage* const message = _rxMessage;
    _rxMessage                      = nullptr;
    _connection.endReceiveMessage(discard());
    if (message == nullptr)
    {
        return;
    }
    (void)message->increaseValidBytes(_rxLength);
    if (_layer.fProvidingListenerHelper.messageReceived(_layer.getBusId(), *message, this)
        != ::transport::ITransportMessageListener::ReceiveResult::RECEIVED_NO_ERROR)
    {
        _layer.fProvidingListenerHelper.releaseTransportMessage(*message);
    }
}

void DoIpClientConnection::releaseSendJob(DoIpTransportMessageSendJob& sendJob, bool const success)
{
    if (_requestJob.has_value() && (&sendJob == &(*_requestJob)))
    {
        if (_request == nullptr)
        {
            return;
        }
        _requestReleased = true;
        if (!success)
        {
            finishRequest(false);
            return;
        }
        tryFinishRequest();
    }
    else if (_functionalJob.has_value() && (&sendJob == &(*_functionalJob)))
    {
        _functionalJobBusy = false;
        _layer.functionalCopyReleased();
    }
    else
    {
        // not a job of this connection
    }
}

void DoIpClientConnection::transportMessageProcessed(
    TransportMessage& transportMessage, ProcessingResult const /* result */)
{
    _layer.fProvidingListenerHelper.releaseTransportMessage(transportMessage);
}

IDoIpConnection::PayloadDiscardedCallbackType DoIpClientConnection::discard()
{
    return IDoIpConnection::PayloadDiscardedCallbackType{};
}

IDoIpConnectionHandler::HeaderReceivedContinuation DoIpClientConnection::skipPayload()
{
    // endReceiveMessage() also handles an empty payload (e.g. an alive check request); the
    // discard continuation of headerReceived() does not leave the discard state in that case
    _connection.endReceiveMessage(discard());
    return HandledByThisHandler{};
}

} // namespace doip

// NOLINTEND(cppcoreguidelines-pro-type-vararg)
