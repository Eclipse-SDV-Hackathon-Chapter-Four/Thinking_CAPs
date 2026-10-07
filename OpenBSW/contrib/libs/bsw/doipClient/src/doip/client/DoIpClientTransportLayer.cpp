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

namespace doip
{
using ::transport::ITransportMessageProcessedListener;
using ::transport::TransportMessage;

DoIpClientTransportLayer::DoIpClientTransportLayer(
    uint8_t const busId,
    DoIpClientParameters const& parameters,
    ::etl::ivector<DoIpClientConnection>& connections,
    NowMsType const nowMs)
: AbstractTransportLayer(busId)
, _parameters(parameters)
, _connections(connections)
, _nowMs(nowMs)
, _functionalMessage(nullptr)
, _functionalListener(nullptr)
, _functionalCopies(0U)
{}

DoIpClientTransportLayer::ErrorCode DoIpClientTransportLayer::init() { return ErrorCode::TP_OK; }

bool DoIpClientTransportLayer::shutdown(ShutdownDelegate /* delegate */)
{
    for (DoIpClientConnection& connection : _connections)
    {
        connection.close();
    }
    return SYNC_SHUTDOWN_COMPLETE;
}

DoIpClientTransportLayer::ErrorCode DoIpClientTransportLayer::send(
    TransportMessage& transportMessage,
    ITransportMessageProcessedListener* const pNotificationListener)
{
    uint16_t const target = transportMessage.getTargetId();
    if (target == _parameters.functionalAddress)
    {
        if (_functionalMessage != nullptr)
        {
            return ErrorCode::TP_MESSAGE_ALREADY_IN_PROGRESS;
        }
        _functionalMessage  = &transportMessage;
        _functionalListener = pNotificationListener;
        // the extra count keeps a copy released early from completing the message
        _functionalCopies   = 1U;
        size_t sent         = 0U;
        for (DoIpClientConnection& connection : _connections)
        {
            if (connection.functional(transportMessage))
            {
                ++_functionalCopies;
                ++sent;
            }
        }
        if (sent == 0U)
        {
            // no node with active routing: the caller keeps the message
            _functionalMessage  = nullptr;
            _functionalListener = nullptr;
            _functionalCopies   = 0U;
            return ErrorCode::TP_SEND_FAIL;
        }
        functionalCopyReleased();
        return ErrorCode::TP_OK;
    }

    DoIpClientConnection* const connection = findConnection(target);
    if (connection == nullptr)
    {
        return ErrorCode::TP_SEND_FAIL;
    }
    if (connection->hasRequest())
    {
        return ErrorCode::TP_MESSAGE_ALREADY_IN_PROGRESS;
    }
    if (!connection->request(
            transportMessage, pNotificationListener, _nowMs() + _parameters.deliveryTimeoutMs))
    {
        return ErrorCode::TP_SEND_FAIL;
    }
    return ErrorCode::TP_OK;
}

void DoIpClientTransportLayer::cyclic()
{
    uint32_t const now = _nowMs();
    for (DoIpClientConnection& connection : _connections)
    {
        connection.cyclic(now);
    }
}

DoIpClientConnection* DoIpClientTransportLayer::findConnection(uint16_t const logicalAddress)
{
    for (DoIpClientConnection& connection : _connections)
    {
        if (connection.node().logicalAddress == logicalAddress)
        {
            return &connection;
        }
    }
    return nullptr;
}

void DoIpClientTransportLayer::functionalCopyReleased()
{
    if (_functionalCopies == 0U)
    {
        return;
    }
    --_functionalCopies;
    if (_functionalCopies == 0U)
    {
        TransportMessage* const message                    = _functionalMessage;
        ITransportMessageProcessedListener* const listener = _functionalListener;
        _functionalMessage                                 = nullptr;
        _functionalListener                                = nullptr;
        if ((message != nullptr) && (listener != nullptr))
        {
            listener->transportMessageProcessed(
                *message, ITransportMessageProcessedListener::ProcessingResult::PROCESSED_NO_ERROR);
        }
    }
}

} // namespace doip
