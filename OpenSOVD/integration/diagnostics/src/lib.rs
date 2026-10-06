//! Integration-owned receiver contract, not an upstream SOVD observation schema.
use schemars::JsonSchema;
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
#[cfg(feature = "fault-lifecycle")]
pub mod faults;
pub mod monitor;

#[derive(Clone, Debug, Deserialize, Serialize, JsonSchema)]
#[serde(deny_unknown_fields)]
pub struct Observation {
    pub schema_version: u32,
    pub source_instance: String,
    pub source_session: String,
    pub boot_id: String,
    pub clock_domain: String,
    pub observed_at_monotonic_ns: u64,
    pub received_at_monotonic_ns: Option<u64>,
    pub last_accepted_at_monotonic_ns: Option<u64>,
    pub vehicle_speed: Option<f64>,
    pub target_speed: Option<f64>,
    pub cc_state: String,
    pub software_identity: String,
    pub sample_id: Option<String>,
    pub integrity_result: String,
    pub acceptance_kind: String,
}

#[derive(Clone, Copy, Debug, Serialize, JsonSchema)]
pub struct Budgets {
    pub speed_ns: u64,
    pub heartbeat_ns: u64,
}

#[derive(Clone, Debug, Serialize, JsonSchema)]
pub struct DiagnosticView {
    pub observation: Option<Observation>,
    pub receiver_state: String,
    pub freshness_state: String,
    pub received_age_ns: Option<u64>,
    pub accepted_age_ns: Option<u64>,
    pub heartbeat_age_ns: Option<u64>,
    pub speed_unit: String,
    pub target_speed_unit: String,
    pub assessment_source: String,
    pub budgets: Budgets,
    pub rejected_observations: u64,
}

pub struct Cache {
    boot_id: String,
    budgets: Budgets,
    latest: Option<Observation>,
    retired_sessions: HashSet<String>,
    rejected: u64,
}

impl Cache {
    pub fn new(boot_id: String, budgets: Budgets) -> Self {
        assert!(budgets.speed_ns > 0 && budgets.heartbeat_ns > 0);
        Self {
            boot_id,
            budgets,
            latest: None,
            retired_sessions: HashSet::new(),
            rejected: 0,
        }
    }

    pub fn accept(&mut self, obs: Observation, now: u64) -> Result<(), &'static str> {
        let valid = self.validate(&obs, now);
        if let Err(reason) = valid {
            self.rejected = self.rejected.saturating_add(1);
            return Err(reason);
        }
        if let Some(old) = &self.latest
            && old.source_session != obs.source_session
        {
            self.retired_sessions.insert(old.source_session.clone());
        }
        self.latest = Some(obs);
        Ok(())
    }

    fn validate(&self, obs: &Observation, now: u64) -> Result<(), &'static str> {
        if obs.schema_version != 1
            || obs.source_instance != "cruise-control"
            || obs.clock_domain != "linux-clock-monotonic"
            || obs.boot_id != self.boot_id
            || obs.source_session.is_empty()
            || obs.source_session.len() > 128
            || obs.software_identity.is_empty()
            || obs.software_identity.len() > 1024
            || !matches!(obs.cc_state.as_str(), "engaged" | "disengaged")
            || obs.integrity_result != "not_available"
            || obs.sample_id.is_some()
            || obs.acceptance_kind != "decoded_by_consumer"
        {
            return Err("unsupported contract or provenance");
        }
        if obs.observed_at_monotonic_ns > now || obs.observed_at_monotonic_ns == 0 {
            return Err("invalid heartbeat timestamp");
        }
        if obs
            .received_at_monotonic_ns
            .is_some_and(|time| time == 0 || time > obs.observed_at_monotonic_ns)
        {
            return Err("invalid receipt timestamp");
        }
        if let Some(accepted) = obs.last_accepted_at_monotonic_ns {
            if accepted == 0
                || obs.vehicle_speed.is_none()
                || obs
                    .received_at_monotonic_ns
                    .is_none_or(|received| accepted > received)
            {
                return Err("invalid acceptance timestamp");
            }
        } else if obs.vehicle_speed.is_some() {
            return Err("speed lacks acceptance provenance");
        }
        if obs.vehicle_speed.is_some_and(|speed| !speed.is_finite())
            || obs.target_speed.is_some_and(|speed| !speed.is_finite())
        {
            return Err("nonfinite JSON value");
        }
        if self.retired_sessions.contains(&obs.source_session) {
            return Err("retired source session");
        }
        if let Some(old) = &self.latest {
            if obs.observed_at_monotonic_ns <= old.observed_at_monotonic_ns {
                return Err("out-of-order observation");
            }
            if old.source_session == obs.source_session
                && (obs.received_at_monotonic_ns < old.received_at_monotonic_ns
                    || obs.last_accepted_at_monotonic_ns < old.last_accepted_at_monotonic_ns)
            {
                return Err("event timestamp regressed");
            }
            if old.source_session != obs.source_session && self.retired_sessions.len() >= 128 {
                return Err("source restart limit reached; restart collector explicitly");
            }
        }
        Ok(())
    }

    pub fn reject_datagram(&mut self) {
        self.rejected = self.rejected.saturating_add(1);
    }

    pub fn view(&self, now: u64) -> DiagnosticView {
        let age = |stamp: u64| now.checked_sub(stamp);
        let heartbeat = self
            .latest
            .as_ref()
            .and_then(|obs| age(obs.observed_at_monotonic_ns));
        let received = self
            .latest
            .as_ref()
            .and_then(|obs| obs.received_at_monotonic_ns)
            .and_then(age);
        let accepted = self
            .latest
            .as_ref()
            .and_then(|obs| obs.last_accepted_at_monotonic_ns)
            .and_then(age);
        let receiver = match heartbeat {
            Some(value) if value <= self.budgets.heartbeat_ns => "available",
            Some(_) => "stale",
            None => "unknown",
        };
        let freshness = if receiver != "available" {
            "unknown"
        } else {
            match accepted {
                Some(value) if value <= self.budgets.speed_ns => "fresh",
                Some(_) => "stale",
                None => "unknown",
            }
        };
        DiagnosticView {
            observation: self.latest.clone(),
            receiver_state: receiver.into(),
            freshness_state: freshness.into(),
            received_age_ns: received,
            accepted_age_ns: accepted,
            heartbeat_age_ns: heartbeat,
            speed_unit: "km/h".into(),
            target_speed_unit: "km/h".into(),
            assessment_source: "local observer; freshness is separate from controller policy"
                .into(),
            budgets: self.budgets,
            rejected_observations: self.rejected,
        }
    }
}

pub fn monotonic_ns() -> u64 {
    let mut stamp = libc::timespec {
        tv_sec: 0,
        tv_nsec: 0,
    };
    // CLOCK_MONOTONIC is shared by co-located Linux processes; boot ID is separately checked.
    let result = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut stamp) };
    assert_eq!(result, 0, "Linux monotonic clock unavailable");
    stamp.tv_sec as u64 * 1_000_000_000 + stamp.tv_nsec as u64
}
