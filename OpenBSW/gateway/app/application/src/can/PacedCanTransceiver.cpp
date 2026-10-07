// SPDX-License-Identifier: Apache-2.0

#include "can/PacedCanTransceiver.h"

#include <time/TimestampProvider.h>

namespace can
{
namespace
{
uint32_t nowUs() { return ::bsw::time::TimestampProvider::getTimestampUs32Bit(); }
} // namespace

PacedCanTransceiver::PacedCanTransceiver(
    ICanTransceiver& transceiver, ::async::ContextType const context, uint32_t const minGapUs)
: _transceiver(transceiver)
, _context(context)
, _timeout()
, _pacer(minGapUs)
, _pending()
, _pendingListener(nullptr)
, _sentListener(nullptr)
{}

void PacedCanTransceiver::shutdown()
{
    _timeout.cancel();
    _pendingListener = nullptr;
    _transceiver.shutdown();
}

ICanTransceiver::ErrorCode PacedCanTransceiver::write(CANFrame const& frame)
{
    _pacer.sent(nowUs());
    return _transceiver.write(frame);
}

ICanTransceiver::ErrorCode
PacedCanTransceiver::write(CANFrame const& frame, ICANFrameSentListener& listener)
{
    if (_pendingListener != nullptr)
    {
        return ErrorCode::CAN_ERR_TX_HW_QUEUE_FULL;
    }
    uint32_t const delay = _pacer.delayUs(nowUs());
    if (delay == 0U)
    {
        return sendNow(frame, listener);
    }
    _pending         = frame;
    _pendingListener = &listener;
    ::async::schedule(_context, *this, _timeout, delay, ::async::TimeUnit::MICROSECONDS);
    return ErrorCode::CAN_ERR_OK;
}

ICanTransceiver::ErrorCode
PacedCanTransceiver::sendNow(CANFrame const& frame, ICANFrameSentListener& listener)
{
    _pacer.sent(nowUs());
    _sentListener = &listener;
    return _transceiver.write(frame, *this);
}

void PacedCanTransceiver::execute()
{
    ICANFrameSentListener* const listener = _pendingListener;
    _pendingListener                      = nullptr;
    if (listener != nullptr)
    {
        // a failure is noticed by the sender through its transmit callback timeout
        (void)sendNow(_pending, *listener);
    }
}

void PacedCanTransceiver::canFrameSent(CANFrame const& frame)
{
    ICANFrameSentListener* const listener = _sentListener;
    _sentListener                         = nullptr;
    if (listener != nullptr)
    {
        listener->canFrameSent(frame);
    }
}

} // namespace can
