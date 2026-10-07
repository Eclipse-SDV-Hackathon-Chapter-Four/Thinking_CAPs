/********************************************************************************
 * Copyright (c) 2024 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Derived from Eclipse OpenBSW executables/referenceApp/application/src/systems/DoCanSystem.cpp.
// Modified for the zonal diagnostic gateway (see DoCanSystem.h).

#include "systems/DoCanSystem.h"

#include "systems/ICanSystem.h"
#include "transport/ITransportSystem.h"

#include <docan/common/DoCanLogger.h>
#include <docan/datalink/DoCanFrameCodecConfigPresets.h>
#include <etl/algorithm.h>
#include <etl/delegate.h>
#include <etl/span.h>
#include <time/TimestampProvider.h>

namespace
{
uint32_t const TIMEOUT_DOCAN_SYSTEM   = 10U;
size_t const TICK_DELTA_TICKS         = 2U; // Tick delta
// ISO-TP timing (SWR-018): N_As/N_Bs/N_Cr 1000 ms
uint16_t const ALLOCATE_TIMEOUT       = 1000U;
uint16_t const RX_TIMEOUT             = 1000U;
uint16_t const TX_CALLBACK_TIMEOUT    = 1000U;
uint16_t const FLOW_CONTROL_TIMEOUT   = 1000U;
uint8_t const ALLOCATE_RETRY_COUNT    = 15U;
uint8_t const FLOW_CONTROL_WAIT_COUNT = 15U;
// STmin requested from ECUs when the gateway receives (5 ms, suits SLCAN ECUs at 115200 baud)
uint16_t const MIN_SEPARATION_TIME    = 5000U;
// block size 0: the ECU may send all consecutive frames without further flow control
uint8_t const BLOCK_SIZE              = 0U;

uint32_t systemUs() { return ::bsw::time::TimestampProvider::getTimestampUs32Bit(); }
} // namespace

namespace docan
{
DoCanSystem::AddressEntries DoCanSystem::buildAddressEntries()
{
    // Normal addressing entry: {reception CAN ID, transmission CAN ID, transport source,
    // transport target}. A response on a route's response ID arrives as route -> gateway
    // CAN tester; a request from the gateway CAN tester to the route goes out on its
    // request ID. The functional entry only transmits (no reception ID) and must be last,
    // because the filter requires valid reception IDs first, in ascending order.
    AddressEntries entries{};
    size_t i = 0U;
    for (::gateway::Route const& route : ::gateway::config::ROUTES)
    {
        if (route.transport != ::gateway::Transport::DOCAN)
        {
            continue;
        }
        entries[i] = AddressEntryType{
            route.responseCanId,
            route.requestCanId,
            route.logicalAddress,
            ::gateway::config::NODE_TESTER_ADDRESS,
            0U,
            0U};
        ++i;
    }
    ::etl::sort(
        entries.begin(),
        entries.begin() + ::gateway::config::DOCAN_ROUTE_COUNT,
        [](AddressEntryType const& a, AddressEntryType const& b)
        { return a._canReceptionId < b._canReceptionId; });
    entries[i] = AddressEntryType{
        DataLinkLayerType::INVALID_ADDRESS,
        ::gateway::config::FUNCTIONAL_CAN_ID,
        ::gateway::config::FUNCTIONAL_ADDRESS,
        ::gateway::config::NODE_TESTER_ADDRESS,
        0U,
        0U};
    return entries;
}

DoCanSystem::DoCanSystem(
    ::transport::ITransportSystem& transportSystem,
    ::can::ICanSystem& canSystem,
    ::async::ContextType asyncContext)
: _context(asyncContext)
, _cyclicTimeout()
, _canSystem(canSystem)
, _transportSystem(transportSystem)
, _frameSizeMapper()
, _classicCodec(::docan::DoCanFrameCodecConfigPresets::PADDED_CLASSIC, _frameSizeMapper)
, _normalAddressing()
, _addressEntries(buildAddressEntries())
, _normalAddressingFilter()
, _parameters(
      ::etl::delegate<decltype(systemUs)>::create<&systemUs>(),
      ALLOCATE_TIMEOUT,
      RX_TIMEOUT,
      TX_CALLBACK_TIMEOUT,
      FLOW_CONTROL_TIMEOUT,
      ALLOCATE_RETRY_COUNT,
      FLOW_CONTROL_WAIT_COUNT,
      MIN_SEPARATION_TIME,
      BLOCK_SIZE)
, _transportLayerConfig(_parameters)
, _transceiver()
, _transportLayers()
, _tickGenerator(asyncContext, _transportLayers)
, _codecs{&_classicCodec}
, _layer(nullptr)
{
    setTransitionContext(asyncContext);
}

void DoCanSystem::init()
{
    _normalAddressingFilter.init(
        ::etl::span<AddressEntryType const>(_addressEntries), ::etl::make_span(_codecs));

    auto& transceiver = *_canSystem.getCanTransceiver(::busid::CAN_0);
    auto& docanTransceiver = _transceiver.emplace(
        ::etl::ref(transceiver),
        ::etl::ref(_normalAddressingFilter),
        ::etl::ref(_normalAddressingFilter),
        ::etl::ref(_normalAddressing));
    _layer = &_transportLayers.emplace_back(
        ::busid::CAN_0,
        ::etl::ref(_context),
        ::etl::ref(_normalAddressingFilter),
        ::etl::ref(docanTransceiver),
        ::etl::ref(_tickGenerator),
        ::etl::ref(_transportLayerConfig),
        ::util::logger::DOCAN);
    transitionDone();
}

void DoCanSystem::run()
{
    _transportSystem.addTransportLayer(*_layer);
    _transportLayers.init();
    ::async::scheduleAtFixedRate(
        _context, *this, _cyclicTimeout, TIMEOUT_DOCAN_SYSTEM, ::async::TimeUnit::MILLISECONDS);
    transitionDone();
}

void DoCanSystem::shutdown()
{
    _cyclicTimeout.cancel();
    _transportSystem.removeTransportLayer(*_layer);
    transitionDone();
}

void DoCanSystem::execute() { _transportLayers.cyclicTask(systemUs()); }

void DoCanSystem::TickGeneratorRunnableAdapter::scheduleTick()
{
    ::async::schedule(
        _context, *this, _tickTimeout, TICK_DELTA_TICKS * 100U, ::async::TimeUnit::MICROSECONDS);
}

DoCanSystem::TickGeneratorRunnableAdapter::TickGeneratorRunnableAdapter(
    ::async::ContextType const context, TransportLayers& layers)
: _layers(layers), _context(context)
{}

void DoCanSystem::TickGeneratorRunnableAdapter::cancelTimeout() { _tickTimeout.cancel(); }

void DoCanSystem::TickGeneratorRunnableAdapter::tickNeeded() { scheduleTick(); }

void DoCanSystem::TickGeneratorRunnableAdapter::execute()
{
    if (_layers.tick(systemUs()))
    {
        scheduleTick();
    }
}

} // namespace docan
