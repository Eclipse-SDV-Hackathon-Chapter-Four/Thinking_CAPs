//! Deterministic accepted-speed assessment. Independent of controller engagement policy.
use crate::DiagnosticView;
use schemars::JsonSchema;
use serde::Serialize;

#[derive(Clone, Copy, Debug, Serialize, JsonSchema)]
pub struct Policy {
    pub timeout_ns: u64,
    pub startup_grace_ns: u64,
    pub failure_debounce_ns: u64,
    pub recovery_hold_ns: u64,
    pub poll_ns: u64,
    pub query_ns: u64,
}

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, JsonSchema)]
#[serde(rename_all = "snake_case")]
pub enum Stage {
    Failed,
    Passed,
}

#[derive(Clone, Debug, Serialize, JsonSchema)]
pub struct Assessment {
    pub assessed_at_monotonic_ns: u64,
    pub state: String,
    pub desired_stage: Option<Stage>,
    pub condition_since_monotonic_ns: Option<u64>,
    pub detected_at_monotonic_ns: Option<u64>,
    pub clock_domain: String,
    pub policy: Policy,
}

pub struct Monitor {
    policy: Policy,
    session: Option<String>,
    started: u64,
    seen_accepted: bool,
    last_now: u64,
    state: &'static str,
    since: Option<u64>,
    detected: Option<u64>,
}

impl Monitor {
    pub fn new(policy: Policy) -> Result<Self, &'static str> {
        if policy.timeout_ns == 0 || policy.poll_ns == 0 || policy.query_ns == 0 {
            return Err("timeout, monitor and query periods must be positive");
        }
        Ok(Self {
            policy,
            session: None,
            started: 0,
            seen_accepted: false,
            last_now: 0,
            state: "unknown",
            since: None,
            detected: None,
        })
    }

    fn enter(&mut self, state: &'static str, now: u64) {
        if self.state != state {
            self.state = state;
            self.since = Some(now);
            self.detected = None;
        }
    }

    pub fn step(&mut self, view: &DiagnosticView, now: u64) -> Assessment {
        let mut desired = None;
        if now < self.last_now || view.receiver_state != "available" || view.observation.is_none() {
            self.enter("unknown", now);
            self.since = None;
        } else if let Some(observation) = &view.observation {
            if self.session.as_ref() != Some(&observation.source_session) {
                self.session = Some(observation.source_session.clone());
                self.started = now;
                self.seen_accepted = false;
                self.enter("startup", now);
            }
            if observation.vehicle_speed.is_some() && view.accepted_age_ns.is_some() {
                self.seen_accepted = true;
            }
            let fresh = observation.vehicle_speed.is_some()
                && view
                    .accepted_age_ns
                    .is_some_and(|age| age <= self.policy.timeout_ns);
            if fresh {
                if self.state != "healthy" {
                    self.enter("pending_recovery", now);
                    if self.since.is_some_and(|since| {
                        now.saturating_sub(since) >= self.policy.recovery_hold_ns
                    }) {
                        self.enter("healthy", now);
                        self.detected = Some(now);
                    }
                }
                if self.state == "healthy" {
                    desired = Some(Stage::Passed);
                }
            } else if !self.seen_accepted
                && now.saturating_sub(self.started) < self.policy.startup_grace_ns
            {
                self.enter("startup", now);
            } else {
                if self.state != "failed" {
                    self.enter("pending_failure", now);
                    if self.since.is_some_and(|since| {
                        now.saturating_sub(since) >= self.policy.failure_debounce_ns
                    }) {
                        self.enter("failed", now);
                        self.detected = Some(now);
                    }
                }
                if self.state == "failed" {
                    desired = Some(Stage::Failed);
                }
            }
        }
        self.last_now = self.last_now.max(now);
        Assessment {
            assessed_at_monotonic_ns: now,
            state: self.state.into(),
            desired_stage: desired,
            condition_since_monotonic_ns: self.since,
            detected_at_monotonic_ns: self.detected,
            clock_domain: "linux-clock-monotonic".into(),
            policy: self.policy,
        }
    }
}
