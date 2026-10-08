/********************************************************************************
 * Copyright (c) 2024 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Modified for the zonal diagnostic gateway: CAN interface from ZGW_CAN_INTERFACE.

#include "systems/CanSystem.h"

#include <cstdlib>

namespace systems
{
static uint32_t const TIMEOUT_CAN_SYSTEM_IN_MS = 1U;
static int const MAX_SENT_PER_RUN              = 3;
static int const MAX_RECEIVED_PER_RUN          = 3;

namespace
{
// gateway: interface selectable with ZGW_CAN_INTERFACE, default vcan0 (SWR-050)
char const* canInterfaceName()
{
    char const* const name = ::std::getenv("ZGW_CAN_INTERFACE");
    return ((name != nullptr) && (name[0] != '\0')) ? name : "vcan0";
}

// clang-format off
::can::SocketCanTransceiver::DeviceConfig canConfig
{
    canInterfaceName(), ::busid::CAN_0,
#if defined(PLATFORM_CAN0_USE_FD)
        true, /*enableCanFd*/
        true  /*enableBitRateSwitch*/
#else
        false, /*enableCanFd*/
        false  /*enableBitRateSwitch*/
#endif
};
// clang-format on
} // namespace

CanSystem::CanSystem(::async::ContextType context)
: _timeout(), _context(context), _canTransceiver(canConfig)
{
    setTransitionContext(context);
}

void CanSystem::init() { transitionDone(); }

void CanSystem::run()
{
    _canTransceiver.init();
    _canTransceiver.open();
    ::async::scheduleAtFixedRate(
        _context, *this, _timeout, TIMEOUT_CAN_SYSTEM_IN_MS, ::async::TimeUnit::MILLISECONDS);
    transitionDone();
}

void CanSystem::shutdown()
{
    _timeout.cancel();
    _canTransceiver.close();
    _canTransceiver.shutdown();
    transitionDone();
}

::can::ICanTransceiver* CanSystem::getCanTransceiver(uint8_t busId)
{
    if (busId == ::busid::CAN_0)
    {
        return &_canTransceiver;
    }
    return nullptr;
}

void CanSystem::execute() { _canTransceiver.run(MAX_SENT_PER_RUN, MAX_RECEIVED_PER_RUN); }

} // namespace systems
