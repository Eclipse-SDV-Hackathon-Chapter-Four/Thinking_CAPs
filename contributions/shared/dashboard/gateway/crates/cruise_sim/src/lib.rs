// SPDX-License-Identifier: Apache-2.0
//! Stand-in for the other team's cruise control app, for testing before the event.
//!
//! [`App`] is the app's behaviour as we assume it, to confirm with the other team:
//! it holds 100 km/h, freezes its speed signal while our `inject_fault` event is
//! true, and becomes `unavailable` once the frozen signal has lasted
//! `fault_detect`. After the fault is released it waits in `standby` for the
//! driver to re-engage, as a real cruise control does; `resume_after` plays the
//! driver pressing "resume" so demo runs can repeat (`None` = never).
//!
//! [`InProcessLink`] plays the part of links ④ ⑤ ⑥: the app thread publishes a
//! status event every period into a cache, and cruise diag reads that cache.

use cruise_diag::{CruiseLink, CruiseState, CruiseStatus};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

pub const SET_SPEED_KMH: f64 = 100.0;

/// The stand-in app's state machine.
#[derive(Debug)]
pub struct App {
    started: Instant,
    fault_detect: Duration,
    resume_after: Option<Duration>,
    state: CruiseState,
    frozen_at: Option<f64>,
    inject_since: Option<Instant>,
    standby_since: Option<Instant>,
}

impl App {
    #[must_use]
    pub fn new(fault_detect: Duration, resume_after: Option<Duration>, now: Instant) -> Self {
        Self {
            started: now,
            fault_detect,
            resume_after,
            state: CruiseState::Active,
            frozen_at: None,
            inject_since: None,
            standby_since: None,
        }
    }

    /// Healthy speed wobbles a little around the set speed; a stuck sensor repeats one value.
    fn live_speed(&self, now: Instant) -> f64 {
        let t = now.duration_since(self.started).as_secs_f64();
        ((SET_SPEED_KMH + 0.4 * (t * 0.7).sin()) * 10.0).round() / 10.0
    }

    /// Advances the app to `now` with the current `inject_fault` value and returns its status event.
    pub fn step(&mut self, inject_fault: bool, now: Instant) -> CruiseStatus {
        match (inject_fault, self.inject_since) {
            (true, None) => {
                self.frozen_at = Some(self.live_speed(now));
                self.inject_since = Some(now);
            }
            (false, Some(_)) => {
                self.frozen_at = None;
                self.inject_since = None;
                if self.state == CruiseState::Unavailable {
                    self.state = CruiseState::Standby;
                    self.standby_since = Some(now);
                }
            }
            _ => {}
        }
        if let Some(since) = self.inject_since {
            if now.duration_since(since) >= self.fault_detect {
                self.state = CruiseState::Unavailable;
            }
        }
        if let (Some(since), Some(after)) = (self.standby_since, self.resume_after) {
            if now.duration_since(since) >= after {
                self.state = CruiseState::Active;
                self.standby_since = None;
            }
        }
        CruiseStatus {
            speed_kmh: self.frozen_at.unwrap_or_else(|| self.live_speed(now)),
            state: self.state,
            set_speed_kmh: (self.state == CruiseState::Active).then_some(SET_SPEED_KMH),
        }
    }
}

/// In-process stand-in for mw::com: a cache of the latest status event and the
/// value of our `inject_fault` event.
#[derive(Default)]
pub struct InProcessLink {
    latest: Mutex<Option<(CruiseStatus, Instant)>>,
    inject_fault: AtomicBool,
}

impl InProcessLink {
    fn deliver(&self, status: CruiseStatus) {
        if let Ok(mut latest) = self.latest.lock() {
            *latest = Some((status, Instant::now()));
        }
    }
}

impl CruiseLink for InProcessLink {
    fn latest(&self) -> Option<(CruiseStatus, Instant)> {
        self.latest.lock().ok().and_then(|l| *l)
    }

    fn publish_inject_fault(&self, stuck: bool) {
        self.inject_fault.store(stuck, Ordering::SeqCst);
    }
}

/// Starts the stand-in app on its own thread, publishing a status event every `period`.
pub fn spawn(fault_detect: Duration, resume_after: Option<Duration>, period: Duration) -> Arc<InProcessLink> {
    let link = Arc::new(InProcessLink::default());
    let app_link = link.clone();
    thread::Builder::new()
        .name("cruise-sim".into())
        .spawn(move || {
            let mut app = App::new(fault_detect, resume_after, Instant::now());
            loop {
                let status = app.step(app_link.inject_fault.load(Ordering::SeqCst), Instant::now());
                app_link.deliver(status);
                thread::sleep(period);
            }
        })
        .expect("spawn cruise-sim thread");
    link
}

#[cfg(test)]
mod tests {
    use super::*;

    const MS: Duration = Duration::from_millis(1);

    #[test]
    fn healthy_app_is_active_near_set_speed() {
        let t0 = Instant::now();
        let mut app = App::new(5000 * MS, None, t0);
        for i in 0..50 {
            let s = app.step(false, t0 + i * 200 * MS);
            assert_eq!(s.state, CruiseState::Active);
            assert_eq!(s.set_speed_kmh, Some(SET_SPEED_KMH));
            assert!((s.speed_kmh - SET_SPEED_KMH).abs() <= 0.4 + 1e-9);
        }
    }

    #[test]
    fn injected_fault_freezes_speed_then_makes_it_unavailable() {
        let t0 = Instant::now();
        let mut app = App::new(100 * MS, None, t0);
        let frozen = app.step(true, t0 + 1000 * MS).speed_kmh;
        let s = app.step(true, t0 + 1099 * MS);
        assert_eq!(s.state, CruiseState::Active);
        assert_eq!(s.speed_kmh, frozen);
        let s = app.step(true, t0 + 1100 * MS);
        assert_eq!(s.state, CruiseState::Unavailable);
        assert_eq!(s.set_speed_kmh, None);
        assert_eq!(s.speed_kmh, frozen);
    }

    #[test]
    fn release_goes_to_standby_not_back_to_active() {
        let t0 = Instant::now();
        let mut app = App::new(100 * MS, None, t0);
        app.step(true, t0);
        assert_eq!(app.step(true, t0 + 200 * MS).state, CruiseState::Unavailable);
        assert_eq!(app.step(false, t0 + 300 * MS).state, CruiseState::Standby);
        assert_eq!(app.step(false, t0 + 9000 * MS).state, CruiseState::Standby);
    }

    #[test]
    fn driver_resumes_after_resume_after() {
        let t0 = Instant::now();
        let mut app = App::new(100 * MS, Some(300 * MS), t0);
        app.step(true, t0);
        app.step(true, t0 + 200 * MS);
        assert_eq!(app.step(false, t0 + 300 * MS).state, CruiseState::Standby);
        assert_eq!(app.step(false, t0 + 599 * MS).state, CruiseState::Standby);
        let s = app.step(false, t0 + 600 * MS);
        assert_eq!(s.state, CruiseState::Active);
        assert_eq!(s.set_speed_kmh, Some(SET_SPEED_KMH));
    }

    #[test]
    fn short_injection_does_not_disable_cruise() {
        let t0 = Instant::now();
        let mut app = App::new(100 * MS, None, t0);
        app.step(true, t0);
        assert_eq!(app.step(false, t0 + 50 * MS).state, CruiseState::Active);
    }

    #[test]
    fn spawned_app_publishes_and_reacts_to_the_event() {
        let link = spawn(50 * MS, None, 10 * MS);
        thread::sleep(40 * MS);
        assert_eq!(link.latest().expect("first event").0.state, CruiseState::Active);
        link.publish_inject_fault(true);
        thread::sleep(120 * MS);
        assert_eq!(link.latest().unwrap().0.state, CruiseState::Unavailable);
    }
}
