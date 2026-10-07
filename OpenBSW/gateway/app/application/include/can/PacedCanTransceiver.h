// SPDX-License-Identifier: Apache-2.0
//
// CAN transceiver decorator that keeps a minimum gap between the frames the gateway sends
// (SWR-032, DD-21). DoCAN writes one data frame at a time and waits for canFrameSent(), so at
// most one frame is held back. Reception, state and listeners pass through unchanged.

#pragma once

#include <async/Async.h>
#include <can/canframes/CANFrame.h>
#include <can/canframes/ICANFrameSentListener.h>
#include <can/transceiver/ICanTransceiver.h>
#include <gateway/TransmitPacer.h>

namespace can
{
class PacedCanTransceiver
: public ICanTransceiver
, private ICANFrameSentListener
, private ::async::RunnableType
{
public:
    PacedCanTransceiver(ICanTransceiver& transceiver, ::async::ContextType context, uint32_t minGapUs);

    ErrorCode init() override { return _transceiver.init(); }

    void shutdown() override;

    ErrorCode open(CANFrame const& frame) override { return _transceiver.open(frame); }

    ErrorCode open() override { return _transceiver.open(); }

    ErrorCode close() override { return _transceiver.close(); }

    ErrorCode mute() override { return _transceiver.mute(); }

    ErrorCode unmute() override { return _transceiver.unmute(); }

    State getState() const override { return _transceiver.getState(); }

    uint32_t getBaudrate() const override { return _transceiver.getBaudrate(); }

    uint16_t getHwQueueTimeout() const override { return _transceiver.getHwQueueTimeout(); }

    /// Without listener (flow control frames): sent at once, counted for the gap.
    ErrorCode write(CANFrame const& frame) override;

    /// Sent at once if the gap has passed, otherwise held back until it has.
    ErrorCode write(CANFrame const& frame, ICANFrameSentListener& listener) override;

    void addCANFrameListener(ICANFrameListener& listener) override
    {
        _transceiver.addCANFrameListener(listener);
    }

    void addVIPCANFrameListener(ICANFrameListener& listener) override
    {
        _transceiver.addVIPCANFrameListener(listener);
    }

    void removeCANFrameListener(ICANFrameListener& listener) override
    {
        _transceiver.removeCANFrameListener(listener);
    }

    uint8_t getBusId() const override { return _transceiver.getBusId(); }

    void addCANFrameSentListener(IFilteredCANFrameSentListener& listener) override
    {
        _transceiver.addCANFrameSentListener(listener);
    }

    void removeCANFrameSentListener(IFilteredCANFrameSentListener& listener) override
    {
        _transceiver.removeCANFrameSentListener(listener);
    }

    ICANTransceiverStateListener::CANTransceiverState getCANTransceiverState() const override
    {
        return _transceiver.getCANTransceiverState();
    }

    void setStateListener(ICANTransceiverStateListener& listener) override
    {
        _transceiver.setStateListener(listener);
    }

    void removeStateListener() override { _transceiver.removeStateListener(); }

private:
    void canFrameSent(CANFrame const& frame) override;
    void execute() override;
    ErrorCode sendNow(CANFrame const& frame, ICANFrameSentListener& listener);

    ICanTransceiver& _transceiver;
    ::async::ContextType _context;
    ::async::TimeoutType _timeout;
    ::gateway::TransmitPacer _pacer;
    CANFrame _pending;
    ICANFrameSentListener* _pendingListener;
    ICANFrameSentListener* _sentListener;
};

} // namespace can
