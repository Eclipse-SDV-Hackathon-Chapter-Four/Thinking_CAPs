/********************************************************************************
 * Copyright (c) 2024 Accenture
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Derived from Eclipse OpenBSW executables/referenceApp/application/include/systems/UdsSystem.h.
// Modified for the zonal diagnostic gateway: the gateway's own UDS server (ARC-05) with
// sessions, TesterPresent, identification DIDs and fault memory (SWR-020, SWR-021, SWR-025).

#pragma once

#include <async/Async.h>
#include <async/IRunnable.h>
#include <etl/singleton_base.h>
#include <lifecycle/AsyncLifecycleComponent.h>
#include <uds/DemoClearDtc.h>
#include <uds/DemoDtcManager.h>
#include <uds/DemoReadDtcInfo.h>
#include <uds/DiagDispatcher.h>
#include <uds/DummySessionPersistence.h>
#include <uds/UdsLifecycleConnector.h>
#include <uds/async/AsyncDiagHelper.h>
#include <uds/jobs/ReadIdentifierFromMemory.h>
#include <uds/services/readdata/ReadDataByIdentifier.h>
#include <uds/services/routinecontrol/RoutineControl.h>
#include <uds/services/routinecontrol/StartRoutine.h>
#include <uds/services/sessioncontrol/DiagnosticSessionControl.h>
#include <uds/services/testerpresent/TesterPresent.h>

namespace lifecycle
{
class LifecycleManager;
}

namespace transport
{
class ITransportSystem;
}

namespace uds
{
class UdsSystem
: public lifecycle::AsyncLifecycleComponent
, public ::etl::singleton_base<UdsSystem>
, private ::async::IRunnable
{
public:
    UdsSystem(
        lifecycle::LifecycleManager& lManager,
        transport::ITransportSystem& transportSystem,
        ::async::ContextType context,
        uint16_t udsAddress);

    void init() override;
    void run() override;
    void shutdown() override;

    DiagDispatcher& getUdsDispatcher();
    IAsyncDiagHelper& getAsyncDiagHelper();
    IDiagSessionManager& getDiagSessionManager();
    DiagnosticSessionControl& getDiagnosticSessionControl();
    ReadDataByIdentifier& getReadDataByIdentifier();
    DemoDtcManager& getDtcManager();

    /** Registers an additional job (DIDs, routines) before init(). */
    void addJob(AbstractDiagJob& job);

private:
    static constexpr size_t MAX_EXTRA_JOBS = 8U;

    void addDiagJobs();
    void removeDiagJobs();
    void shutdownComplete(transport::AbstractTransportLayer&);
    void execute() override;

    UdsLifecycleConnector _udsLifecycleConnector;
    transport::ITransportSystem& _transportSystem;
    DummySessionPersistence _dummySessionPersistence;
    DiagJobRoot _jobRoot;
    DiagnosticSessionControl _diagnosticSessionControl;
    DiagnosisConfiguration _udsConfiguration;
    ::etl::pool<IncomingDiagConnection, 5> _connectionPool;
    ::etl::queue<TransportJob, 16> _sendJobQueue;
    DiagDispatcher _udsDispatcher;
    uds::declare::AsyncDiagHelper<5> _asyncDiagHelper;
    ReadDataByIdentifier _readDataByIdentifier;
    RoutineControl _routineControl;
    StartRoutine _startRoutine;
    ReadIdentifierFromMemory _readF190;
    ReadIdentifierFromMemory _readF18C;
    ReadIdentifierFromMemory _readF195;
    TesterPresent _testerPresent;
    DemoDtcManager _dtcManager;
    DemoClearDtc _clearDtc;
    DemoReadDtcInfo _readDtcInfo;
    ::etl::vector<AbstractDiagJob*, MAX_EXTRA_JOBS> _extraJobs;
    ::async::ContextType _context;
    ::async::TimeoutType _timeout;
};

} // namespace uds
