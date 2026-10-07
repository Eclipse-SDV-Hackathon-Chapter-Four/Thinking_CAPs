// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <cstdint>

namespace gateway
{
/**
 * Minimum gap between frames the gateway transmits on a bus (SWR-032, DD-20).
 *
 * With a gap of g microseconds at most 1e6 / g frames are sent per second, whatever the
 * separation time a node grants. The clock is a free-running 32-bit microsecond counter;
 * differences are wrap-safe.
 */
class TransmitPacer
{
public:
    explicit TransmitPacer(uint32_t minGapUs) : _minGapUs(minGapUs), _lastUs(0U), _sent(false) {}

    /// Microseconds until the next frame may be sent; 0 if it may be sent now.
    uint32_t delayUs(uint32_t nowUs) const
    {
        uint32_t const elapsed = nowUs - _lastUs;
        return ((!_sent) || (elapsed >= _minGapUs)) ? 0U : (_minGapUs - elapsed);
    }

    /// A frame was handed to the transceiver at nowUs.
    void sent(uint32_t nowUs)
    {
        _lastUs = nowUs;
        _sent   = true;
    }

    uint32_t minGapUs() const { return _minGapUs; }

private:
    uint32_t _minGapUs;
    uint32_t _lastUs;
    bool _sent;
};

} // namespace gateway
