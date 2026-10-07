/********************************************************************************
 * Copyright (c) 2024 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Derived from Eclipse OpenBSW executables/referenceApp/application/include/systems/
// DoCanSystem.h. Modified for the zonal diagnostic gateway (ARC-02): one ISO-TP layer with
// normal 11-bit addressing whose entries come from the routing table. The gateway is the
// client: it transmits on each route's request ID and the functional ID and receives
// only the routes' response IDs (SWR-018, SWR-030).

#pragma once

#include "can/PacedCanTransceiver.h"
#include <async/Async.h>
#include <async/IRunnable.h>
#include <busid/BusId.h>
#include <docan/addressing/DoCanNormalAddressing.h>
#include <docan/addressing/DoCanNormalAddressingFilter.h>
#include <docan/can/DoCanPhysicalCanTransceiver.h>
#include <docan/datalink/DoCanFdFrameSizeMapper.h>
#include <docan/datalink/DoCanFrameCodec.h>
#include <docan/transmitter/IDoCanTickGenerator.h>
#include <docan/transport/DoCanTransportLayerContainer.h>
#include <etl/array.h>
#include <etl/optional.h>
#include <gateway/RoutingConfig.h>
#include <lifecycle/AsyncLifecycleComponent.h>

namespace can
{
class ICanSystem;
} // namespace can

namespace transport
{
class ITransportSystem;
} // namespace transport

namespace docan
{
class DoCanSystem final
: public ::lifecycle::AsyncLifecycleComponent
, private ::async::IRunnable
{
public:
    static size_t const NUM_CAN_TRANSPORT_LAYERS = 1UL;

    using NormalAddressingType = ::docan::DoCanNormalAddressing<>;
    using DataLinkLayerType    = NormalAddressingType::DataLinkLayerType;

    DoCanSystem(
        ::transport::ITransportSystem& transportSystem,
        ::can::ICanSystem& canSystem,
        ::async::ContextType asyncContext);
    DoCanSystem(DoCanSystem const&)            = delete;
    DoCanSystem& operator=(DoCanSystem const&) = delete;

    void init() final;
    void run() final;
    void shutdown() final;

private:
    using TransportLayers = ::docan::declare::
        DoCanTransportLayerContainer<DataLinkLayerType, NUM_CAN_TRANSPORT_LAYERS>;
    using FrameCodecType             = ::docan::DoCanFrameCodec<DataLinkLayerType>;
    using NormalAddressingFilterType = ::docan::DoCanNormalAddressingFilter<DataLinkLayerType>;
    using AddressEntryType           = NormalAddressingFilterType::AddressEntryType;
    using AddressEntries
        = ::etl::array<AddressEntryType, ::gateway::config::DOCAN_ROUTE_COUNT + 1U>;

    class TickGeneratorRunnableAdapter final
    : public ::docan::IDoCanTickGenerator
    , private ::async::RunnableType
    {
    public:
        TickGeneratorRunnableAdapter(::async::ContextType context, TransportLayers& layers);
        void cancelTimeout();

    private:
        void execute() final;
        void tickNeeded() final;
        void scheduleTick();

        TransportLayers& _layers;
        ::async::TimeoutType _tickTimeout;
        ::async::ContextType _context;
    };

    void execute() final;
    static AddressEntries buildAddressEntries();

    ::async::ContextType const _context;
    ::async::TimeoutType _cyclicTimeout;
    ::can::ICanSystem& _canSystem;
    ::transport::ITransportSystem& _transportSystem;
    ::docan::DoCanFdFrameSizeMapper<DataLinkLayerType::FrameSizeType> _frameSizeMapper;
    FrameCodecType _classicCodec;
    NormalAddressingType _normalAddressing;
    AddressEntries _addressEntries;
    NormalAddressingFilterType _normalAddressingFilter;
    ::docan::DoCanParameters _parameters;
    ::docan::declare::DoCanTransportLayerConfig<DataLinkLayerType, 80U, 15U, 64U>
        _transportLayerConfig;
    ::etl::optional<::can::PacedCanTransceiver> _pacedTransceiver;
    ::etl::optional<::docan::DoCanPhysicalCanTransceiver<NormalAddressingType>> _transceiver;
    TransportLayers _transportLayers;
    TickGeneratorRunnableAdapter _tickGenerator;
    ::etl::array<FrameCodecType const*, 1U> _codecs;
    ::docan::DoCanTransportLayer<DataLinkLayerType>* _layer;
};

} // namespace docan
