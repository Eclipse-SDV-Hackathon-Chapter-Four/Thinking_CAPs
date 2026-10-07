// SPDX-License-Identifier: Apache-2.0
#include "gateway/ReachabilityProbe.h"

namespace gateway
{
using ::transport::ITransportMessageProcessedListener;
using ::transport::TransportMessage;

namespace
{
uint8_t const TESTER_PRESENT[] = {0x3EU, 0x00U};
}

ReachabilityProbe::ReachabilityProbe(
    uint8_t const busId,
    uint16_t const testerAddress,
    RoutingTable const& table,
    uint32_t const windowMs)
: AbstractTransportLayer(busId)
, _table(table)
, _tester(testerAddress)
, _windowMs(windowMs)
, _deadline(0U)
, _results()
{
    _results.fill(Result::NOT_STARTED);
}

void ReachabilityProbe::start(uint32_t const nowMs)
{
    _deadline = nowMs + _windowMs;
    for (size_t i = 0U; (i < _table.size()) && (i < MAX_ROUTES); ++i)
    {
        _results[i] = Result::PENDING;
    }
    for (size_t i = 0U; (i < _table.size()) && (i < MAX_ROUTES); ++i)
    {
        uint16_t const target   = _table.at(i).logicalAddress;
        TransportMessage* request = nullptr;
        if ((fProvidingListenerHelper.getTransportMessage(
                 getBusId(), _tester, target, sizeof(TESTER_PRESENT), {}, request)
             != ::transport::ITransportMessageProvider::ErrorCode::TPMSG_OK)
            || (request == nullptr))
        {
            // busy route or no buffer: not confirmed
            _results[i] = Result::NOT_REACHED;
            continue;
        }
        request->setSourceAddress(_tester);
        request->setTargetAddress(target);
        request->setPayloadLength(sizeof(TESTER_PRESENT));
        (void)request->append(TESTER_PRESENT, sizeof(TESTER_PRESENT));
        if (fProvidingListenerHelper.messageReceived(getBusId(), *request, this)
            != ::transport::ITransportMessageListener::ReceiveResult::RECEIVED_NO_ERROR)
        {
            fProvidingListenerHelper.releaseTransportMessage(*request);
            _results[i] = Result::NOT_REACHED;
        }
    }
}

bool ReachabilityProbe::running(uint32_t const nowMs) const
{
    if (expired(nowMs))
    {
        return false;
    }
    for (size_t i = 0U; (i < _table.size()) && (i < MAX_ROUTES); ++i)
    {
        if (_results[i] == Result::PENDING)
        {
            return true;
        }
    }
    return false;
}

ReachabilityProbe::Result ReachabilityProbe::result(size_t const routeIndex, uint32_t const nowMs) const
{
    if (routeIndex >= MAX_ROUTES)
    {
        return Result::NOT_STARTED;
    }
    Result const result = _results[routeIndex];
    return ((result == Result::PENDING) && expired(nowMs)) ? Result::NOT_REACHED : result;
}

ReachabilityProbe::ErrorCode ReachabilityProbe::send(
    TransportMessage& transportMessage, ITransportMessageProcessedListener* const pNotificationListener)
{
    size_t const index = _table.indexOf(transportMessage.getSourceId());
    if ((index < MAX_ROUTES) && (_results[index] == Result::PENDING))
    {
        // any answer, positive or negative, shows that the node is reachable
        _results[index] = Result::REACHED;
    }
    if (pNotificationListener != nullptr)
    {
        pNotificationListener->transportMessageProcessed(
            transportMessage, ProcessingResult::PROCESSED_NO_ERROR);
    }
    return ErrorCode::TP_OK;
}

void ReachabilityProbe::transportMessageProcessed(
    TransportMessage& transportMessage, ProcessingResult const result)
{
    // the TesterPresent request has been delivered (or not); the probe owns its buffer
    size_t const index = _table.indexOf(transportMessage.getTargetId());
    if ((result != ProcessingResult::PROCESSED_NO_ERROR) && (index < MAX_ROUTES)
        && (_results[index] == Result::PENDING))
    {
        _results[index] = Result::NOT_REACHED;
    }
    fProvidingListenerHelper.releaseTransportMessage(transportMessage);
}

} // namespace gateway
