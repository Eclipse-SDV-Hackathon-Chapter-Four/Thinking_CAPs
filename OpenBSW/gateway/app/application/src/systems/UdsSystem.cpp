/********************************************************************************
 * Copyright (c) 2024 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Derived from Eclipse OpenBSW executables/referenceApp/application/src/systems/UdsSystem.cpp.
// Modified for the zonal diagnostic gateway (ARC-05).

#include "systems/UdsSystem.h"

#include "gateway/GatewayIdentity.h"

#include <busid/BusId.h>
#include <lifecycle/LifecycleManager.h>
#include <transport/ITransportSystem.h>
#include <transport/TransportConfiguration.h>

namespace uds
{

UdsSystem::UdsSystem(
    lifecycle::LifecycleManager& lManager,
    transport::ITransportSystem& transportSystem,
    ::async::ContextType context,
    uint16_t udsAddress)
: AsyncLifecycleComponent()
, ::etl::singleton_base<UdsSystem>(*this)
, _udsLifecycleConnector(lManager)
, _transportSystem(transportSystem)
, _jobRoot()
, _diagnosticSessionControl(_udsLifecycleConnector, context, _dummySessionPersistence)
, _udsConfiguration{
      udsAddress,
      transport::TransportConfiguration::FUNCTIONAL_ALL_ISO14229,
      transport::TransportConfiguration::DIAG_PAYLOAD_SIZE,
      ::busid::SELFDIAG,
      true,  /* activate outgoing pending */
      false, /* accept all requests */
      true,  /* copy functional requests */
      context}
, _udsDispatcher(
      _connectionPool, _sendJobQueue, _udsConfiguration, _diagnosticSessionControl, _jobRoot)
, _asyncDiagHelper(context)
, _readDataByIdentifier()
, _routineControl()
, _startRoutine()
, _requestRoutineResults()
, _readF190(0xF190, ::gateway::identity::vin())
, _readF18C(0xF18C, ::gateway::identity::ecuSerial())
, _readF195(0xF195, ::gateway::identity::softwareVersion())
, _testerPresent()
, _dtcManager()
, _clearDtc(_dtcManager)
, _readDtcInfo(_dtcManager)
, _extraJobs()
, _context(context)
, _timeout()
{
    setTransitionContext(_context);
}

void UdsSystem::init()
{
    (void)_udsDispatcher.init();
    AbstractDiagJob::setDefaultDiagSessionManager(_diagnosticSessionControl);
    _diagnosticSessionControl.setDiagDispatcher(&_udsDispatcher);
    _transportSystem.addTransportLayer(_udsDispatcher);
    addDiagJobs();
    transitionDone();
}

void UdsSystem::run()
{
    ::async::scheduleAtFixedRate(_context, *this, _timeout, 10, ::async::TimeUnit::MILLISECONDS);
    transitionDone();
}

void UdsSystem::shutdown()
{
    removeDiagJobs();
    _diagnosticSessionControl.setDiagDispatcher(nullptr);
    _diagnosticSessionControl.shutdown();
    _transportSystem.removeTransportLayer(_udsDispatcher);
    (void)_udsDispatcher.shutdown(transport::AbstractTransportLayer::ShutdownDelegate::
                                      create<UdsSystem, &UdsSystem::shutdownComplete>(*this));
}

void UdsSystem::shutdownComplete(transport::AbstractTransportLayer&)
{
    _timeout.cancel();
    transitionDone();
}

DiagDispatcher& UdsSystem::getUdsDispatcher() { return _udsDispatcher; }

IAsyncDiagHelper& UdsSystem::getAsyncDiagHelper() { return _asyncDiagHelper; }

IDiagSessionManager& UdsSystem::getDiagSessionManager() { return _diagnosticSessionControl; }

DiagnosticSessionControl& UdsSystem::getDiagnosticSessionControl()
{
    return _diagnosticSessionControl;
}

ReadDataByIdentifier& UdsSystem::getReadDataByIdentifier() { return _readDataByIdentifier; }

DemoDtcManager& UdsSystem::getDtcManager() { return _dtcManager; }

void UdsSystem::addJob(AbstractDiagJob& job)
{
    if (!_extraJobs.full())
    {
        _extraJobs.push_back(&job);
    }
}

void UdsSystem::addDiagJobs()
{
    // 10 - DiagnosticSessionControl, 3E - TesterPresent
    (void)_jobRoot.addAbstractDiagJob(_diagnosticSessionControl);
    (void)_jobRoot.addAbstractDiagJob(_testerPresent);
    // 14 - ClearDiagnosticInformation, 19 - ReadDTCInformation (01, 02, 0A)
    (void)_jobRoot.addAbstractDiagJob(_clearDtc);
    (void)_jobRoot.addAbstractDiagJob(_readDtcInfo);
    // 22 - ReadDataByIdentifier
    (void)_jobRoot.addAbstractDiagJob(_readDataByIdentifier);
    (void)_jobRoot.addAbstractDiagJob(_readF190);
    (void)_jobRoot.addAbstractDiagJob(_readF18C);
    (void)_jobRoot.addAbstractDiagJob(_readF195);
    // 31 - RoutineControl (start routine)
    (void)_jobRoot.addAbstractDiagJob(_routineControl);
    (void)_jobRoot.addAbstractDiagJob(_startRoutine);
    (void)_jobRoot.addAbstractDiagJob(_requestRoutineResults);
    // gateway DIDs and routines
    for (AbstractDiagJob* const job : _extraJobs)
    {
        (void)_jobRoot.addAbstractDiagJob(*job);
    }
}

void UdsSystem::removeDiagJobs()
{
    for (AbstractDiagJob* const job : _extraJobs)
    {
        _jobRoot.removeAbstractDiagJob(*job);
    }
    _jobRoot.removeAbstractDiagJob(_requestRoutineResults);
    _jobRoot.removeAbstractDiagJob(_startRoutine);
    _jobRoot.removeAbstractDiagJob(_routineControl);
    _jobRoot.removeAbstractDiagJob(_readF195);
    _jobRoot.removeAbstractDiagJob(_readF18C);
    _jobRoot.removeAbstractDiagJob(_readF190);
    _jobRoot.removeAbstractDiagJob(_readDataByIdentifier);
    _jobRoot.removeAbstractDiagJob(_readDtcInfo);
    _jobRoot.removeAbstractDiagJob(_clearDtc);
    _jobRoot.removeAbstractDiagJob(_testerPresent);
    _jobRoot.removeAbstractDiagJob(_diagnosticSessionControl);
}

void UdsSystem::execute() {}

} // namespace uds
