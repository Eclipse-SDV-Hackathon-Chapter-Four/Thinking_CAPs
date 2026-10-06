// SPDX-License-Identifier: Apache-2.0
//! Cruise control diagnostics exposed as `diag_api` data resources.
//!
//! The cruise control app belongs to another team. This crate never calls it
//! directly: it only sees a [`CruiseLink`], which caches the app's latest status
//! events and publishes our `inject_fault` event. In process that link is the
//! stand-in `cruise_sim`; on the target it is mw::com through the S-CORE SOME/IP
//! gateway (links ④ ⑤ ⑥ in `docs/architecture/sdv-hackathon-final.drawio`).
//!
//! | resource                    | category    | access     |
//! |-----------------------------|-------------|------------|
//! | `vehicle_speed`             | currentData | read       |
//! | `cruise_state`              | currentData | read       |
//! | `speed_sensor_fault_status` | currentData | read       |
//! | `speed_sensor_stuck`        | storedData  | read/write |

use diag_api::sovd::data_resource::{
    DataCategory, DataResourceMetadata, ReadValueArgs, ReadValueHandle, ReadValueReply, WriteValueArgs,
    WriteValueHandle,
};
use diag_api::sovd::{DataError, DataResource, ErrorCode, GenericError};
use diag_api::{ReplyMessagePayload, RequestMessagePayload};
use diag_json::json;
use sovd_adapter::{DataResourceRegistry, RegistrationError};
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};

/// State reported by the cruise control app.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum CruiseState {
    /// Switched on, not holding a speed.
    Standby,
    /// Holding the set speed.
    Active,
    /// Refuses to engage, e.g. because the speed signal is implausible.
    Unavailable,
}

impl CruiseState {
    #[must_use]
    pub fn as_str(self) -> &'static str {
        match self {
            Self::Standby => "standby",
            Self::Active => "active",
            Self::Unavailable => "unavailable",
        }
    }
}

/// One status event from the cruise control app (`vehicle_speed` + `cruise_state`).
#[derive(Clone, Copy, Debug, PartialEq)]
pub struct CruiseStatus {
    pub speed_kmh: f64,
    pub state: CruiseState,
    pub set_speed_kmh: Option<f64>,
}

/// The only way cruise diag talks to the cruise control app.
pub trait CruiseLink: Send + Sync {
    /// Latest status event and when it arrived; `None` before the first event.
    fn latest(&self) -> Option<(CruiseStatus, Instant)>;
    /// Publishes our `inject_fault` event to the app.
    fn publish_inject_fault(&self, stuck: bool);
}

/// `score::mw::diag::dtc::Debounce::TimeBased`: a monitor result must hold
/// continuously for the given duration before the status changes.
#[derive(Clone, Copy, Debug)]
pub struct TimeBased {
    pub failed_duration: Duration,
    pub passed_duration: Duration,
}

/// Debounced status of the monitored condition.
#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Stage {
    Passed,
    PreFailed,
    Failed,
    PrePassed,
}

impl Stage {
    fn as_str(self) -> &'static str {
        match self {
            Self::Passed => "passed",
            Self::PreFailed => "prefailed",
            Self::Failed => "failed",
            Self::PrePassed => "prepassed",
        }
    }
}

/// Same debounce as the HVAC example in the reference gateway.
#[derive(Debug)]
struct Monitor {
    debounce: TimeBased,
    qualified_failed: bool,
    raw_failed: bool,
    raw_since: Instant,
}

impl Monitor {
    fn new(debounce: TimeBased, now: Instant) -> Self {
        Self {
            debounce,
            qualified_failed: false,
            raw_failed: false,
            raw_since: now,
        }
    }

    fn report(&mut self, failed: bool, now: Instant) {
        self.settle(now);
        if failed != self.raw_failed {
            self.raw_failed = failed;
            self.raw_since = now;
        }
    }

    fn settle(&mut self, now: Instant) {
        if self.raw_failed == self.qualified_failed {
            return;
        }
        let needed = if self.raw_failed {
            self.debounce.failed_duration
        } else {
            self.debounce.passed_duration
        };
        if now.duration_since(self.raw_since) >= needed {
            self.qualified_failed = self.raw_failed;
        }
    }

    fn stage(&mut self, now: Instant) -> Stage {
        self.settle(now);
        match (self.qualified_failed, self.raw_failed) {
            (false, false) => Stage::Passed,
            (false, true) => Stage::PreFailed,
            (true, true) => Stage::Failed,
            (true, false) => Stage::PrePassed,
        }
    }
}

struct State {
    stuck: bool,
    monitor: Monitor,
}

/// Shared state of cruise diag; each resource holds a handle to it.
#[derive(Clone)]
pub struct CruiseDiag {
    state: Arc<Mutex<State>>,
    link: Arc<dyn CruiseLink>,
}

impl CruiseDiag {
    pub fn new(link: Arc<dyn CruiseLink>, debounce: TimeBased) -> Self {
        Self {
            state: Arc::new(Mutex::new(State {
                stuck: false,
                monitor: Monitor::new(debounce, Instant::now()),
            })),
            link,
        }
    }

    fn with<T>(&self, f: impl FnOnce(&mut State, Instant) -> T) -> diag_api::Result<T> {
        let mut state = self.state.lock().map_err(|_| diag_api::Error::mutex_poisoned())?;
        Ok(f(&mut state, Instant::now()))
    }

    fn latest(&self) -> diag_api::Result<(CruiseStatus, Instant)> {
        self.link.latest().ok_or_else(|| {
            diag_api::Error::from_error(GenericError::from_code(
                ErrorCode::NotResponding,
                "no status event from the cruise control app yet".to_string(),
            ))
        })
    }

    /// Registers the four cruise resources in `registry`.
    ///
    /// # Errors
    /// [`RegistrationError`] if one of the ids is already taken.
    pub fn register(&self, registry: &mut DataResourceRegistry) -> Result<(), RegistrationError> {
        let meta = |id: &str, name: &str, category, read_only| DataResourceMetadata {
            id: id.to_string(),
            name: name.to_string(),
            translation_id: None,
            read_only,
            category,
            groups: Some(vec!["cruise".to_string()]),
        };
        registry.register(
            meta("vehicle_speed", "Vehicle speed", DataCategory::CurrentData, true),
            VehicleSpeed(self.clone()),
        )?;
        registry.register(
            meta("cruise_state", "Cruise control state", DataCategory::CurrentData, true),
            StateResource(self.clone()),
        )?;
        registry.register(
            meta(
                "speed_sensor_fault_status",
                "Vehicle speed sensor fault status",
                DataCategory::CurrentData,
                true,
            ),
            FaultStatus(self.clone()),
        )?;
        registry.register(
            meta(
                "speed_sensor_stuck",
                "Fault injection: vehicle speed sensor stuck",
                DataCategory::StoredData,
                false,
            ),
            StuckInjection(self.clone()),
        )
    }
}

fn as_handle(result: diag_api::Result<diag_json::Value>) -> ReadValueHandle {
    match result {
        Ok(value) => ReadValueHandle::ready(ReadValueReply {
            data: ReplyMessagePayload::from_json(value, None),
            errors: None,
        }),
        Err(err) => ReadValueHandle::from_error(err),
    }
}

fn age_ms(at: Instant) -> u64 {
    u64::try_from(at.elapsed().as_millis()).unwrap_or(u64::MAX)
}

struct VehicleSpeed(CruiseDiag);

impl DataResource for VehicleSpeed {
    fn read(&self, _input: ReadValueArgs) -> ReadValueHandle {
        as_handle(
            self.0
                .latest()
                .map(|(s, at)| json!({ "value": s.speed_kmh, "unit": "km/h", "age_ms": age_ms(at) })),
        )
    }
}

struct StateResource(CruiseDiag);

impl DataResource for StateResource {
    fn read(&self, _input: ReadValueArgs) -> ReadValueHandle {
        as_handle(self.0.latest().map(|(s, at)| {
            json!({ "state": s.state.as_str(), "set_speed": s.set_speed_kmh, "age_ms": age_ms(at) })
        }))
    }
}

struct FaultStatus(CruiseDiag);

impl DataResource for FaultStatus {
    fn read(&self, _input: ReadValueArgs) -> ReadValueHandle {
        as_handle(self.0.with(|s, now| {
            s.monitor.report(s.stuck, now);
            let stage = s.monitor.stage(now);
            json!({
                "fault": "VehicleSpeedSensorStuck",
                "status": stage.as_str(),
                "test_failed": s.monitor.raw_failed,
                "confirmed": stage == Stage::Failed,
            })
        }))
    }
}

struct StuckInjection(CruiseDiag);

impl DataResource for StuckInjection {
    fn read(&self, _input: ReadValueArgs) -> ReadValueHandle {
        as_handle(self.0.with(|s, _| json!({ "stuck": s.stuck })))
    }

    fn write(&mut self, input: WriteValueArgs) -> WriteValueHandle {
        let stuck = match input.user_data {
            Some(RequestMessagePayload::JSON(body)) => body.get("stuck").and_then(diag_json::Value::as_bool),
            _ => None,
        };
        let Some(stuck) = stuck else {
            return WriteValueHandle::from_error(DataError::from_error(GenericError::from_code(
                ErrorCode::IncompleteRequest,
                "expected a JSON body {\"stuck\": true|false}".to_string(),
            )));
        };
        match self.0.with(|s, now| {
            s.stuck = stuck;
            s.monitor.report(stuck, now);
        }) {
            Ok(()) => {
                // Outside the lock: the link may block briefly on IPC.
                self.0.link.publish_inject_fault(stuck);
                WriteValueHandle::ready()
            }
            Err(_) => WriteValueHandle::from_error(DataError::from_error(GenericError::from_code(
                ErrorCode::SovdServerFailure,
                "cruise diag state is poisoned".to_string(),
            ))),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use diag_api::{JsonSchemaRequired, ReplyMessageEncoding};

    const MS: Duration = Duration::from_millis(1);

    #[derive(Default)]
    struct FakeLink {
        status: Mutex<Option<(CruiseStatus, Instant)>>,
        published: Mutex<Vec<bool>>,
    }

    impl CruiseLink for FakeLink {
        fn latest(&self) -> Option<(CruiseStatus, Instant)> {
            *self.status.lock().unwrap()
        }
        fn publish_inject_fault(&self, stuck: bool) {
            self.published.lock().unwrap().push(stuck);
        }
    }

    fn diag() -> (CruiseDiag, Arc<FakeLink>) {
        let link = Arc::new(FakeLink::default());
        let diag = CruiseDiag::new(
            link.clone(),
            TimeBased {
                failed_duration: 100 * MS,
                passed_duration: 50 * MS,
            },
        );
        (diag, link)
    }

    fn read(resource: &dyn DataResource) -> diag_api::Result<diag_json::Value> {
        match resource.read(ReadValueArgs::new(ReplyMessageEncoding::JSON(JsonSchemaRequired::No))) {
            ReadValueHandle::Ready(Ok(reply)) => match reply.data {
                ReplyMessagePayload::JSON(v, _) => Ok(v),
                other => panic!("unexpected payload {other:?}"),
            },
            ReadValueHandle::Ready(Err(e)) => Err(e),
            ReadValueHandle::Pending(_) => panic!("cruise diag answers synchronously"),
        }
    }

    fn write(diag: &CruiseDiag, body: diag_json::Value) -> WriteValueHandle {
        StuckInjection(diag.clone()).write(WriteValueArgs {
            user_data: Some(RequestMessagePayload::JSON(body)),
            ..WriteValueArgs::default()
        })
    }

    #[test]
    fn debounce_failed_only_after_failed_duration() {
        let t0 = Instant::now();
        let mut m = Monitor::new(
            TimeBased {
                failed_duration: 100 * MS,
                passed_duration: 50 * MS,
            },
            t0,
        );
        m.report(true, t0);
        assert_eq!(m.stage(t0 + 99 * MS), Stage::PreFailed);
        assert_eq!(m.stage(t0 + 100 * MS), Stage::Failed);
        m.report(false, t0 + 200 * MS);
        assert_eq!(m.stage(t0 + 249 * MS), Stage::PrePassed);
        assert_eq!(m.stage(t0 + 250 * MS), Stage::Passed);
    }

    #[test]
    fn no_event_yet_is_not_responding() {
        let (diag, _) = diag();
        let err = read(&VehicleSpeed(diag)).unwrap_err();
        let text = format!("{err:?}");
        assert!(text.contains("no status event"), "{text}");
    }

    #[test]
    fn speed_and_state_come_from_the_latest_event() {
        let (diag, link) = diag();
        *link.status.lock().unwrap() = Some((
            CruiseStatus {
                speed_kmh: 99.8,
                state: CruiseState::Active,
                set_speed_kmh: Some(100.0),
            },
            Instant::now(),
        ));
        assert_eq!(read(&VehicleSpeed(diag.clone())).unwrap()["value"], json!(99.8));
        let state = read(&StateResource(diag)).unwrap();
        assert_eq!(state["state"], "active");
        assert_eq!(state["set_speed"], json!(100.0));
    }

    #[test]
    fn injection_publishes_the_event_and_starts_the_debounce() {
        let (diag, link) = diag();
        assert!(matches!(write(&diag, json!({"stuck": true})), WriteValueHandle::Ready(Ok(()))));
        assert_eq!(*link.published.lock().unwrap(), [true]);
        assert_eq!(read(&FaultStatus(diag.clone())).unwrap()["status"], "prefailed");
        std::thread::sleep(120 * MS);
        assert_eq!(read(&FaultStatus(diag.clone())).unwrap()["status"], "failed");
        assert!(matches!(write(&diag, json!({"stuck": false})), WriteValueHandle::Ready(Ok(()))));
        assert_eq!(*link.published.lock().unwrap(), [true, false]);
        assert_eq!(read(&StuckInjection(diag)).unwrap()["stuck"], false);
    }

    #[test]
    fn bad_body_is_rejected_and_nothing_is_published() {
        let (diag, link) = diag();
        assert!(matches!(write(&diag, json!({"stuck": "yes"})), WriteValueHandle::Ready(Err(_))));
        assert!(link.published.lock().unwrap().is_empty());
    }
}
