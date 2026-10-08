//! Native upstream reporter/IPC/DFM integration, exposed through labelled data fallback.
use crate::{
    Cache, DiagnosticView,
    monitor::{Assessment, Monitor, Policy, Stage},
    monotonic_ns,
};
use dfm_lib::{
    diagnostic_fault_manager::DiagnosticFaultManager,
    fault_catalog_registry::FaultCatalogRegistry,
    query_api::DfmQueryApi,
    sovd_fault_manager::{Error as QueryError, SovdEnvData, SovdFault},
    sovd_fault_storage::{
        KvsSovdFaultStateStorage, SovdFaultState, SovdFaultStateStorage, StorageError,
    },
};
use fault_lib::{
    FaultApi,
    catalog::FaultCatalogBuilder,
    reporter::{Reporter, ReporterApi, ReporterConfig},
};
use schemars::JsonSchema;
use score_fault_common::{
    SourceId,
    fault::{FaultId, LifecyclePhase, LifecycleStage},
    types::{MetadataVec, to_static_short_string},
};
use serde::Serialize;
use sha2::{Digest, Sha256};
use std::{
    collections::HashMap,
    path::PathBuf,
    sync::{
        Arc, RwLock,
        atomic::{AtomicBool, Ordering},
    },
    thread::{self, JoinHandle},
    time::Duration,
};

pub const FAULT_CODE: &str = "CC.LostCommunication";
const CATALOG: &str = include_str!("../../../config/faults/cruise-control.json");

#[derive(Clone, Debug, Default, Serialize, JsonSchema)]
pub struct StorageEvidence {
    pub acknowledged_mutations: u64,
    pub last_mutation_monotonic_ns: Option<u64>,
    pub last_error: Option<String>,
}

/// Delegates fault storage to native KVS and records actual mutation outcomes.
/// Native DFM logs write errors but query can see an unflushed in-memory mutation;
/// therefore query visibility alone is never a durability acknowledgment.
struct AuditedStorage {
    native: KvsSovdFaultStateStorage,
    evidence: Arc<RwLock<StorageEvidence>>,
}
impl AuditedStorage {
    fn acknowledge(&self, result: Result<(), StorageError>) -> Result<(), StorageError> {
        let mut evidence = self.evidence.write().unwrap_or_else(|p| p.into_inner());
        match &result {
            Ok(()) => {
                evidence.acknowledged_mutations = evidence.acknowledged_mutations.saturating_add(1);
                evidence.last_mutation_monotonic_ns = Some(monotonic_ns());
                evidence.last_error = None;
            }
            Err(error) => evidence.last_error = Some(error.to_string()),
        }
        result
    }
}
impl SovdFaultStateStorage for AuditedStorage {
    fn put(&self, path: &str, id: &FaultId, state: SovdFaultState) -> Result<(), StorageError> {
        self.acknowledge(self.native.put(path, id, state))
    }
    fn get_all(&self, path: &str) -> Result<Vec<(FaultId, SovdFaultState)>, StorageError> {
        self.native.get_all(path)
    }
    fn get(&self, path: &str, id: &FaultId) -> Result<Option<SovdFaultState>, StorageError> {
        self.native.get(path, id)
    }
    fn delete_all(&self, path: &str) -> Result<(), StorageError> {
        self.acknowledge(self.native.delete_all(path))
    }
    fn delete(&self, path: &str, id: &FaultId) -> Result<(), StorageError> {
        self.acknowledge(self.native.delete(path, id))
    }
}

#[derive(Clone, Debug, Serialize, JsonSchema)]
pub struct FaultRecordView {
    pub code: String,
    pub name: String,
    pub severity: u32,
    pub status: HashMap<String, String>,
    pub test_failed: Option<bool>,
    pub confirmed: Option<bool>,
    pub failed_since_clear: Option<bool>,
    pub occurrence_counter: Option<u32>,
    pub healing_counter: Option<u32>,
    pub first_occurrence: Option<String>,
    pub last_occurrence: Option<String>,
    pub environment: SovdEnvData,
}
impl FaultRecordView {
    fn from_native(fault: SovdFault, environment: SovdEnvData) -> Self {
        Self {
            code: fault.code,
            name: fault.fault_name,
            severity: fault.severity,
            status: fault.status,
            test_failed: fault.typed_status.as_ref().and_then(|s| s.test_failed),
            confirmed: fault.typed_status.as_ref().and_then(|s| s.confirmed_dtc),
            failed_since_clear: fault
                .typed_status
                .as_ref()
                .and_then(|s| s.test_failed_since_last_clear),
            occurrence_counter: fault.occurrence_counter,
            healing_counter: fault.healing_counter,
            first_occurrence: fault.first_occurrence,
            last_occurrence: fault.last_occurrence,
            environment,
        }
    }
}

#[derive(Clone, Debug, Serialize, JsonSchema)]
pub struct FaultView {
    pub native_faults_resource: bool,
    pub exposure: String,
    pub storage_policy: String,
    pub storage: StorageEvidence,
    pub assessment: Assessment,
    pub report_stage: Option<Stage>,
    pub report_error: Option<String>,
    pub report_enqueued_at_monotonic_ns: Option<u64>,
    pub query_state: String,
    pub query_error: Option<String>,
    pub queried_at_monotonic_ns: Option<u64>,
    pub query_age_ns: Option<u64>,
    pub fault: Option<FaultRecordView>,
}
impl FaultView {
    pub fn view(&self, now: u64) -> Self {
        let mut view = self.clone();
        view.query_age_ns = self
            .queried_at_monotonic_ns
            .and_then(|stamp| now.checked_sub(stamp));
        let query_budget = self.assessment.policy.query_ns.saturating_mul(4);
        if view.query_state == "available" && view.query_age_ns.is_none_or(|age| age > query_budget)
        {
            view.query_state = "stale".into();
        }
        if now.saturating_sub(self.assessment.assessed_at_monotonic_ns)
            > self.assessment.policy.poll_ns.saturating_mul(4)
        {
            view.assessment.state = "unavailable".into();
            view.assessment.desired_stage = None;
        }
        view
    }
    fn update_query(&mut self, result: Result<(SovdFault, SovdEnvData), QueryError>, now: u64) {
        match result {
            Ok((fault, environment)) => {
                self.fault = Some(FaultRecordView::from_native(fault, environment));
                self.query_state = "available".into();
                self.query_error = None;
                self.queried_at_monotonic_ns = Some(now);
            }
            Err(error) => {
                self.query_state = "unavailable".into();
                self.query_error = Some(error.to_string());
                // Retain last real query and timestamp. Error never clears history.
            }
        }
    }
}

pub struct FaultRuntime {
    pub cache: Arc<RwLock<FaultView>>,
    shutdown: Arc<AtomicBool>,
    thread: Option<JoinHandle<()>>,
}
impl FaultRuntime {
    pub fn start(
        storage: PathBuf,
        receiver: Arc<RwLock<Cache>>,
        policy: Policy,
    ) -> Result<Self, Box<dyn std::error::Error>> {
        let mut monitor = Monitor::new(policy)?;
        let initial = monitor.step(
            &receiver
                .read()
                .unwrap_or_else(|p| p.into_inner())
                .view(monotonic_ns()),
            monotonic_ns(),
        );
        let cache = Arc::new(RwLock::new(FaultView { native_faults_resource: false,
            exposure: "native OpenSOVD App data fallback; not native /faults".into(),
            storage_policy: "opt-in write-through native KVS; process-restart contract; no hardware/power-loss guarantee".into(),
            storage: StorageEvidence::default(), assessment: initial, report_stage: None, report_error: None,
            report_enqueued_at_monotonic_ns: None, query_state: "initializing".into(), query_error: None,
            queried_at_monotonic_ns: None, query_age_ns: None, fault: None }));
        let shutdown = Arc::new(AtomicBool::new(false));
        let worker_shutdown = Arc::clone(&shutdown);
        let worker_cache = Arc::clone(&cache);
        let handle = thread::Builder::new()
            .name("receiver-fault-monitor".into())
            .spawn(move || {
                if let Err(error) = worker(
                    storage,
                    receiver,
                    Arc::clone(&worker_cache),
                    worker_shutdown,
                    monitor,
                    policy,
                ) {
                    let mut view = worker_cache.write().unwrap_or_else(|p| p.into_inner());
                    view.query_state = "unavailable".into();
                    view.query_error = Some(format!("fault worker unavailable: {error}"));
                    view.report_error = Some(format!("fault worker unavailable: {error}"));
                }
            })?;
        Ok(Self {
            cache,
            shutdown,
            thread: Some(handle),
        })
    }
}
impl Drop for FaultRuntime {
    fn drop(&mut self) {
        self.shutdown.store(true, Ordering::Release);
        if let Some(handle) = self.thread.take() {
            let _ = handle.join();
        }
    }
}

fn metadata(
    view: &DiagnosticView,
    assessment: &Assessment,
    stage: Stage,
) -> Result<MetadataVec, Box<dyn std::error::Error>> {
    let obs = view
        .observation
        .as_ref()
        .ok_or("no actual receiver observation")?;
    let pairs = [
        ("receiver", obs.source_instance.clone()),
        (
            "session_hash",
            format!("{:x}", Sha256::digest(obs.source_session.as_bytes())),
        ),
        (
            "build_hash",
            format!("{:x}", Sha256::digest(obs.software_identity.as_bytes())),
        ),
        (
            "accepted_age_ns",
            view.accepted_age_ns
                .map_or("unknown".into(), |v| v.to_string()),
        ),
        (
            "received_age_ns",
            view.received_age_ns
                .map_or("unknown".into(), |v| v.to_string()),
        ),
        (
            "detected_ns",
            assessment
                .detected_at_monotonic_ns
                .map_or("unknown".into(), |v| v.to_string()),
        ),
        (
            "stage",
            if stage == Stage::Failed {
                "failed"
            } else {
                "passed"
            }
            .into(),
        ),
        (
            "assessment",
            if stage == Stage::Failed {
                "accepted_speed_timeout"
            } else {
                "held_fresh_accepted_speed"
            }
            .into(),
        ),
    ];
    let mut result = Vec::new();
    for (key, value) in pairs {
        result.push((
            to_static_short_string(key).map_err(|e| format!("{e:?}"))?,
            to_static_short_string(value).map_err(|e| format!("{e:?}"))?,
        ));
    }
    MetadataVec::try_from(result.as_slice()).map_err(|e| format!("{e:?}").into())
}

fn worker(
    directory: PathBuf,
    receiver: Arc<RwLock<Cache>>,
    cached: Arc<RwLock<FaultView>>,
    shutdown: Arc<AtomicBool>,
    mut monitor: Monitor,
    policy: Policy,
) -> Result<(), Box<dyn std::error::Error>> {
    let catalog = FaultCatalogBuilder::new()
        .json_string(CATALOG)?
        .try_build()?;
    let storage_evidence = Arc::new(RwLock::new(StorageEvidence::default()));
    let storage = AuditedStorage {
        native: KvsSovdFaultStateStorage::new_write_through(&directory, 0)?,
        evidence: Arc::clone(&storage_evidence),
    };
    let manager_catalog = FaultCatalogBuilder::new()
        .json_string(CATALOG)?
        .try_build()?;
    let manager =
        DiagnosticFaultManager::new(storage, FaultCatalogRegistry::new(vec![manager_catalog]));
    let query = manager.query_api();
    let _api = FaultApi::try_new(catalog)?;
    let source = SourceId {
        entity: to_static_short_string("cruise_control").map_err(|e| format!("{e:?}"))?,
        ecu: Some(to_static_short_string("score-host").map_err(|e| format!("{e:?}"))?),
        domain: Some(to_static_short_string("adas").map_err(|e| format!("{e:?}"))?),
        sw_component: Some(to_static_short_string("cruise-control").map_err(|e| format!("{e:?}"))?),
        instance: None,
    };
    let mut reporter = Reporter::new(
        &FaultId::Text(to_static_short_string(FAULT_CODE).map_err(|e| format!("{e:?}"))?),
        ReporterConfig {
            source,
            lifecycle_phase: LifecyclePhase::Running,
            default_env_data: MetadataVec::new(),
        },
    )?;
    // Seed from actual stored activity so restarting the service does not report
    // the same still-active incident again and inflate occurrence counters.
    let initial_query = query.get_fault("cruise_control", FAULT_CODE);
    let mut query_available = initial_query.is_ok();
    let mut published = initial_query.as_ref().ok().and_then(|(fault, _)| {
        if fault.occurrence_counter.unwrap_or(0) == 0 {
            return None;
        }
        match fault
            .typed_status
            .as_ref()
            .and_then(|status| status.test_failed)
        {
            Some(true) => Some(Stage::Failed),
            Some(false) => Some(Stage::Passed),
            None => None,
        }
    });
    cached
        .write()
        .unwrap_or_else(|p| p.into_inner())
        .update_query(initial_query, monotonic_ns());
    let mut last_query = 0;
    while !shutdown.load(Ordering::Acquire) {
        let now = monotonic_ns();
        let observation = receiver.read().unwrap_or_else(|p| p.into_inner()).view(now);
        let assessment = monitor.step(&observation, now);
        let mut report_error = None;
        let mut enqueued = None;
        if query_available
            && let Some(stage) = assessment.desired_stage
            && published != Some(stage)
        {
            let mut record = reporter.create_record(if stage == Stage::Failed {
                LifecycleStage::Failed
            } else {
                LifecycleStage::Passed
            });
            record.env_data = metadata(&observation, &assessment, stage)?;
            match reporter.publish("cruise_control", record) {
                Ok(()) => {
                    published = Some(stage);
                    enqueued = Some(now);
                }
                Err(error) => report_error = Some(error.to_string()),
            }
        }
        let queried = if now.saturating_sub(last_query) >= policy.query_ns {
            last_query = now;
            let result = query.get_fault("cruise_control", FAULT_CODE);
            query_available = result.is_ok();
            Some(result)
        } else {
            None
        };
        {
            let mut view = cached.write().unwrap_or_else(|p| p.into_inner());
            view.assessment = assessment;
            view.report_stage = published;
            if report_error.is_some() {
                view.report_error = report_error;
            }
            if enqueued.is_some() {
                view.report_error = None;
                view.report_enqueued_at_monotonic_ns = enqueued;
            }
            if let Some(result) = queried {
                view.update_query(result, now);
            }
            view.storage = storage_evidence
                .read()
                .unwrap_or_else(|p| p.into_inner())
                .clone();
        }
        thread::sleep(Duration::from_nanos(policy.poll_ns));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::Budgets;
    #[test]
    fn failed_query_retains_actual_previous_history() {
        let receiver = Arc::new(RwLock::new(Cache::new(
            "boot".into(),
            Budgets {
                speed_ns: 100,
                heartbeat_ns: 100,
            },
        )));
        let policy = Policy {
            timeout_ns: 100,
            startup_grace_ns: 100,
            failure_debounce_ns: 10,
            recovery_hold_ns: 10,
            poll_ns: 10,
            query_ns: 10,
        };
        let assessment = Monitor::new(policy)
            .unwrap()
            .step(&receiver.read().unwrap().view(100), 100);
        let mut view = FaultView {
            native_faults_resource: false,
            exposure: "data-only".into(),
            storage_policy: "test".into(),
            storage: StorageEvidence::default(),
            assessment,
            report_stage: None,
            report_error: None,
            report_enqueued_at_monotonic_ns: None,
            query_state: "initializing".into(),
            query_error: None,
            queried_at_monotonic_ns: None,
            query_age_ns: None,
            fault: None,
        };
        view.update_query(
            Ok((
                SovdFault {
                    code: FAULT_CODE.into(),
                    occurrence_counter: Some(2),
                    ..Default::default()
                },
                SovdEnvData::new(),
            )),
            100,
        );
        view.update_query(Err(QueryError::Storage("read failed".into())), 200);
        assert_eq!(view.query_state, "unavailable");
        assert_eq!(view.queried_at_monotonic_ns, Some(100));
        assert_eq!(view.fault.unwrap().occurrence_counter, Some(2));
    }
}
