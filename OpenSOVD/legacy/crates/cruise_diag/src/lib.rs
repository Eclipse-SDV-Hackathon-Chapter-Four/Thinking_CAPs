use std::{
    collections::BTreeMap,
    time::{Duration, Instant},
};

use async_trait::async_trait;
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use serde_json::Value;
use thiserror::Error;
use tokio::sync::Mutex;

pub const TEST_FAILED: u8 = 0x01;
pub const TEST_FAILED_THIS_OPERATION_CYCLE: u8 = 0x02;
pub const PENDING_DTC: u8 = 0x04;
pub const CONFIRMED_DTC: u8 = 0x08;
pub const TEST_NOT_COMPLETED_SINCE_LAST_CLEAR: u8 = 0x10;
pub const TEST_FAILED_SINCE_LAST_CLEAR: u8 = 0x20;
pub const TEST_NOT_COMPLETED_THIS_OPERATION_CYCLE: u8 = 0x40;
pub const WARNING_INDICATOR_REQUESTED: u8 = 0x80;

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Severity {
    Info,
    Low,
    Medium,
    High,
    Critical,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct EnvironmentData {
    pub captured_at: DateTime<Utc>,
    #[serde(default)]
    pub signals: BTreeMap<String, Value>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Fault {
    pub code: String,
    pub display: String,
    pub status: u8,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub severity: Option<Severity>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub environment_data: Option<EnvironmentData>,
    pub first_seen: DateTime<Utc>,
    pub last_seen: DateTime<Utc>,
    pub occurrence_count: u64,
}

#[derive(Debug, Clone, Default, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FaultFilter {
    pub status_mask: Option<u8>,
    pub status_value: Option<u8>,
}

#[derive(Debug, Error)]
pub enum FaultError {
    #[error("unknown DTC: {0}")]
    NotFound(String),
    #[error("invalid fault definition: {0}")]
    InvalidDefinition(String),
    #[error("invalid status filter: statusValue must be a subset of statusMask")]
    InvalidFilter,
    #[error("fault source is stale")]
    SourceStale,
}

#[async_trait]
pub trait FaultProvider: Send + Sync + 'static {
    async fn list(&self, filter: FaultFilter) -> Result<Vec<Fault>, FaultError>;
    async fn read(&self, code: &str) -> Result<Fault, FaultError>;
    async fn clear(&self, code: Option<&str>) -> Result<usize, FaultError>;
}

#[derive(Debug, Clone)]
pub struct FaultDefinition {
    pub code: String,
    pub display: String,
    pub severity: Option<Severity>,
}

#[derive(Debug, Clone, Deserialize, Serialize)]
pub struct FaultObservation {
    pub code: String,
    pub status: u8,
    pub timestamp: DateTime<Utc>,
    pub severity: Option<Severity>,
    pub environment_data: Option<EnvironmentData>,
}

#[derive(Debug, Clone)]
struct StoredFault {
    fault: Fault,
}

#[derive(Default)]
struct ProviderState {
    faults: BTreeMap<String, StoredFault>,
    last_source_activity: Option<Instant>,
}

pub struct CruiseFaultProvider {
    definitions: BTreeMap<String, FaultDefinition>,
    max_age: Duration,
    state: Mutex<ProviderState>,
}

impl CruiseFaultProvider {
    pub fn builder() -> FaultProviderBuilder {
        FaultProviderBuilder::default()
    }

    pub async fn observe(&self, observation: FaultObservation) -> Result<(), FaultError> {
        let definition = self
            .definitions
            .get(&observation.code)
            .cloned()
            .ok_or_else(|| FaultError::NotFound(observation.code.clone()))?;
        let mut state = self.state.lock().await;
        let received_at = Instant::now();
        state.last_source_activity = Some(received_at);
        let stored = state
            .faults
            .entry(observation.code.clone())
            .or_insert_with(|| StoredFault {
                fault: Fault {
                    code: definition.code.clone(),
                    display: definition.display.clone(),
                    status: 0,
                    severity: observation.severity.or(definition.severity),
                    environment_data: observation.environment_data.clone(),
                    first_seen: observation.timestamp,
                    last_seen: observation.timestamp,
                    occurrence_count: 0,
                },
            });
        if stored.fault.status & TEST_FAILED == 0 && observation.status & TEST_FAILED != 0 {
            stored.fault.occurrence_count = stored.fault.occurrence_count.saturating_add(1);
        }
        stored.fault.status = observation.status;
        stored.fault.last_seen = observation.timestamp;
        stored.fault.severity = observation.severity.or(definition.severity);
        if observation.environment_data.is_some() {
            stored.fault.environment_data = observation.environment_data;
        }
        Ok(())
    }

    pub async fn mark_source_alive(&self) {
        self.state.lock().await.last_source_activity = Some(Instant::now());
    }

    fn ensure_source_fresh(&self, state: &ProviderState) -> Result<(), FaultError> {
        if state
            .last_source_activity
            .is_none_or(|last_seen| Instant::now().duration_since(last_seen) > self.max_age)
        {
            return Err(FaultError::SourceStale);
        }
        Ok(())
    }
}

pub struct FaultProviderBuilder {
    max_age: Duration,
    definitions: Vec<FaultDefinition>,
}

impl Default for FaultProviderBuilder {
    fn default() -> Self {
        Self {
            max_age: Duration::from_secs(5),
            definitions: Vec::new(),
        }
    }
}

impl FaultProviderBuilder {
    pub fn max_age(mut self, duration: Duration) -> Self {
        self.max_age = duration;
        self
    }

    pub fn register(
        mut self,
        code: impl Into<String>,
        display: impl Into<String>,
        severity: Option<Severity>,
    ) -> Self {
        self.definitions.push(FaultDefinition {
            code: code.into(),
            display: display.into(),
            severity,
        });
        self
    }

    pub fn build(self) -> Result<CruiseFaultProvider, FaultError> {
        let mut definitions = BTreeMap::new();
        for definition in self.definitions {
            if definition.code.len() != 6
                || !definition.code.bytes().all(|byte| byte.is_ascii_hexdigit())
            {
                return Err(FaultError::InvalidDefinition(definition.code));
            }
            if definitions
                .insert(definition.code.clone(), definition.clone())
                .is_some()
            {
                return Err(FaultError::InvalidDefinition(format!(
                    "duplicate DTC {}",
                    definition.code
                )));
            }
        }
        Ok(CruiseFaultProvider {
            definitions,
            max_age: self.max_age,
            state: Mutex::new(ProviderState::default()),
        })
    }
}

#[async_trait]
impl FaultProvider for CruiseFaultProvider {
    async fn list(&self, filter: FaultFilter) -> Result<Vec<Fault>, FaultError> {
        let mask = filter.status_mask.unwrap_or(0);
        let value = filter.status_value.unwrap_or(0);
        if value & !mask != 0 {
            return Err(FaultError::InvalidFilter);
        }
        let state = self.state.lock().await;
        self.ensure_source_fresh(&state)?;
        Ok(state
            .faults
            .values()
            .map(|stored| &stored.fault)
            .filter(|fault| fault.status & mask == value)
            .cloned()
            .collect())
    }

    async fn read(&self, code: &str) -> Result<Fault, FaultError> {
        let state = self.state.lock().await;
        let stored = state
            .faults
            .get(code)
            .ok_or_else(|| FaultError::NotFound(code.to_string()))?;
        self.ensure_source_fresh(&state)?;
        Ok(stored.fault.clone())
    }

    async fn clear(&self, code: Option<&str>) -> Result<usize, FaultError> {
        if let Some(code) = code
            && !self.definitions.contains_key(code)
        {
            return Err(FaultError::NotFound(code.to_string()));
        }
        let mut state = self.state.lock().await;
        let removed = if let Some(code) = code {
            usize::from(state.faults.remove(code).is_some())
        } else {
            let count = state.faults.len();
            state.faults.clear();
            count
        };
        Ok(removed)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn provider(max_age: Duration) -> CruiseFaultProvider {
        CruiseFaultProvider::builder()
            .max_age(max_age)
            .register(
                "CC0001",
                "Cruise input signal invalid",
                Some(Severity::High),
            )
            .register(
                "CC0002",
                "Cruise controller output unavailable",
                Some(Severity::Medium),
            )
            .build()
            .unwrap()
    }

    fn observation(code: &str, status: u8) -> FaultObservation {
        FaultObservation {
            code: code.into(),
            status,
            timestamp: Utc::now(),
            severity: None,
            environment_data: None,
        }
    }

    #[tokio::test]
    async fn producer_confirmed_fault_is_immediately_visible() {
        let provider = provider(Duration::from_secs(30));
        let status = TEST_FAILED | CONFIRMED_DTC;
        provider
            .observe(observation("CC0001", status))
            .await
            .unwrap();
        assert_eq!(provider.read("CC0001").await.unwrap().status, status);
    }

    #[tokio::test]
    async fn provider_preserves_source_status_timestamp_and_snapshot() {
        let provider = provider(Duration::from_secs(30));
        let mut signals = BTreeMap::new();
        signals.insert("ego_velocity_kmh".into(), Value::from(80));
        let timestamp = Utc::now();
        let snapshot = EnvironmentData {
            captured_at: timestamp,
            signals,
        };
        provider
            .observe(FaultObservation {
                code: "CC0001".into(),
                status: TEST_FAILED
                    | TEST_FAILED_THIS_OPERATION_CYCLE
                    | CONFIRMED_DTC
                    | TEST_FAILED_SINCE_LAST_CLEAR,
                timestamp,
                severity: Some(Severity::High),
                environment_data: Some(snapshot.clone()),
            })
            .await
            .unwrap();
        let fault = provider.read("CC0001").await.unwrap();
        assert_eq!(fault.status & TEST_FAILED, TEST_FAILED);
        assert_eq!(fault.status & CONFIRMED_DTC, CONFIRMED_DTC);
        assert_eq!(
            fault.status & TEST_FAILED_SINCE_LAST_CLEAR,
            TEST_FAILED_SINCE_LAST_CLEAR
        );
        assert_eq!(fault.environment_data, Some(snapshot));
        assert_eq!(fault.occurrence_count, 1);
        assert_eq!(fault.first_seen, timestamp);
        assert_eq!(fault.last_seen, timestamp);
    }

    #[tokio::test]
    async fn producer_status_transition_is_preserved_without_local_debounce() {
        let provider = provider(Duration::from_secs(30));
        provider
            .observe(observation(
                "CC0001",
                TEST_FAILED | CONFIRMED_DTC | TEST_FAILED_SINCE_LAST_CLEAR,
            ))
            .await
            .unwrap();
        provider
            .observe(observation(
                "CC0001",
                CONFIRMED_DTC | TEST_FAILED_SINCE_LAST_CLEAR,
            ))
            .await
            .unwrap();
        let fault = provider.read("CC0001").await.unwrap();
        assert_eq!(fault.status & TEST_FAILED, 0);
        assert_eq!(fault.status & CONFIRMED_DTC, CONFIRMED_DTC);
        assert_eq!(
            fault.status & TEST_FAILED_SINCE_LAST_CLEAR,
            TEST_FAILED_SINCE_LAST_CLEAR
        );
    }

    #[tokio::test]
    async fn status_filter_and_clear_are_scoped() {
        let provider = provider(Duration::from_secs(30));
        let status = TEST_FAILED
            | TEST_FAILED_THIS_OPERATION_CYCLE
            | CONFIRMED_DTC
            | TEST_FAILED_SINCE_LAST_CLEAR;
        for code in ["CC0001", "CC0002"] {
            provider.observe(observation(code, status)).await.unwrap();
        }
        let filtered = provider
            .list(FaultFilter {
                status_mask: Some(TEST_FAILED),
                status_value: Some(TEST_FAILED),
            })
            .await
            .unwrap();
        assert_eq!(filtered.len(), 2);
        assert_eq!(provider.clear(Some("CC0001")).await.unwrap(), 1);
        assert_eq!(
            provider.list(FaultFilter::default()).await.unwrap().len(),
            1
        );
        assert_eq!(provider.clear(None).await.unwrap(), 1);
        assert!(
            provider
                .list(FaultFilter::default())
                .await
                .unwrap()
                .is_empty()
        );
    }

    #[tokio::test]
    async fn stale_fault_is_not_served_as_fresh() {
        let provider = provider(Duration::from_millis(10));
        provider
            .observe(observation("CC0001", TEST_FAILED | CONFIRMED_DTC))
            .await
            .unwrap();
        tokio::time::sleep(Duration::from_millis(20)).await;
        assert!(matches!(
            provider.list(FaultFilter::default()).await,
            Err(FaultError::SourceStale)
        ));
        assert!(matches!(
            provider.read("CC0001").await,
            Err(FaultError::SourceStale)
        ));
    }

    #[tokio::test]
    async fn source_sample_heartbeat_keeps_unchanged_fault_fresh() {
        let provider = provider(Duration::from_millis(10));
        provider
            .observe(observation("CC0001", TEST_FAILED | CONFIRMED_DTC))
            .await
            .unwrap();
        let event_time = provider.read("CC0001").await.unwrap().last_seen;
        tokio::time::sleep(Duration::from_millis(20)).await;
        provider.mark_source_alive().await;
        let fault = provider.read("CC0001").await.unwrap();
        assert_eq!(fault.last_seen, event_time);
    }

    #[tokio::test]
    async fn unknown_dtc_and_invalid_status_filter_are_errors() {
        let provider = provider(Duration::from_secs(30));
        assert!(matches!(
            provider.read("FFFFFF").await,
            Err(FaultError::NotFound(_))
        ));
        assert!(matches!(
            provider
                .list(FaultFilter {
                    status_mask: Some(0x01),
                    status_value: Some(0x02),
                })
                .await,
            Err(FaultError::InvalidFilter)
        ));
    }

    #[test]
    fn builder_rejects_non_24_bit_dtc_identifiers() {
        assert!(matches!(
            CruiseFaultProvider::builder()
                .register("CC000", "invalid DTC", None)
                .build(),
            Err(FaultError::InvalidDefinition(_))
        ));
    }
}
