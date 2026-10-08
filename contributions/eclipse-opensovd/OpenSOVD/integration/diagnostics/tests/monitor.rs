use sdv_receiver_diagnostics::{
    Budgets, Cache, Observation,
    monitor::{Monitor, Policy, Stage},
};
use serde_json::json;

fn view(
    now: u64,
    accepted: Option<u64>,
    session: &str,
) -> sdv_receiver_diagnostics::DiagnosticView {
    let mut cache = Cache::new(
        "boot".into(),
        Budgets {
            speed_ns: 100,
            heartbeat_ns: 1000,
        },
    );
    let observation: Observation = serde_json::from_value(json!({
        "schema_version":1,"source_instance":"cruise-control","source_session":session,
        "boot_id":"boot","clock_domain":"linux-clock-monotonic","observed_at_monotonic_ns":now,
        "received_at_monotonic_ns":accepted,"last_accepted_at_monotonic_ns":accepted,
        "vehicle_speed":accepted.map(|_|42.0),"target_speed":42.0,"cc_state":"engaged",
        "software_identity":"test","sample_id":null,"integrity_result":"not_available",
        "acceptance_kind":"decoded_by_consumer"
    }))
    .unwrap();
    cache.accept(observation, now).unwrap();
    cache.view(now)
}
fn monitor() -> Monitor {
    Monitor::new(Policy {
        timeout_ns: 100,
        startup_grace_ns: 200,
        failure_debounce_ns: 20,
        recovery_hold_ns: 30,
        poll_ns: 10,
        query_ns: 10,
    })
    .unwrap()
}

#[test]
fn startup_never_infers_a_healthy_source() {
    let mut monitor = monitor();
    let unknown = Cache::new(
        "boot".into(),
        Budgets {
            speed_ns: 100,
            heartbeat_ns: 1000,
        },
    )
    .view(1000);
    assert_eq!(monitor.step(&unknown, 1000).state, "unknown");
    assert_eq!(
        monitor.step(&view(1010, None, "one"), 1010).state,
        "startup"
    );
    assert_eq!(
        monitor.step(&view(1209, None, "one"), 1209).desired_stage,
        None
    );
    assert_eq!(
        monitor.step(&view(1210, None, "one"), 1210).state,
        "pending_failure"
    );
    assert_eq!(
        monitor.step(&view(1229, None, "one"), 1229).desired_stage,
        None
    );
    assert_eq!(
        monitor.step(&view(1230, None, "one"), 1230).desired_stage,
        Some(Stage::Failed)
    );
}

#[test]
fn accepted_age_boundary_debounce_and_recovery_hold() {
    let mut monitor = monitor();
    assert_eq!(
        monitor.step(&view(1000, Some(1000), "one"), 1000).state,
        "pending_recovery"
    );
    assert_eq!(
        monitor
            .step(&view(1029, Some(1029), "one"), 1029)
            .desired_stage,
        None
    );
    assert_eq!(
        monitor
            .step(&view(1030, Some(1030), "one"), 1030)
            .desired_stage,
        Some(Stage::Passed)
    );
    assert_eq!(
        monitor
            .step(&view(1300, Some(1200), "one"), 1300)
            .desired_stage,
        Some(Stage::Passed)
    );
    assert_eq!(
        monitor.step(&view(1301, Some(1200), "one"), 1301).state,
        "pending_failure"
    );
    assert_eq!(
        monitor
            .step(&view(1320, Some(1200), "one"), 1320)
            .desired_stage,
        None
    );
    assert_eq!(
        monitor
            .step(&view(1321, Some(1200), "one"), 1321)
            .desired_stage,
        Some(Stage::Failed)
    );
    assert_eq!(
        monitor.step(&view(1400, Some(1400), "one"), 1400).state,
        "pending_recovery"
    );
    assert_eq!(
        monitor
            .step(&view(1429, Some(1429), "one"), 1429)
            .desired_stage,
        None
    );
    assert_eq!(
        monitor
            .step(&view(1430, Some(1430), "one"), 1430)
            .desired_stage,
        Some(Stage::Passed)
    );
}

#[test]
fn oscillation_resets_holds_and_restart_requires_new_evidence() {
    let mut monitor = monitor();
    monitor.step(&view(1000, Some(1000), "one"), 1000);
    monitor.step(&view(1030, Some(1030), "one"), 1030);
    monitor.step(&view(1301, Some(1200), "one"), 1301);
    assert_eq!(
        monitor.step(&view(1310, Some(1310), "one"), 1310).state,
        "pending_recovery"
    );
    assert_eq!(
        monitor.step(&view(1311, Some(1200), "one"), 1311).state,
        "pending_failure"
    );
    assert_eq!(
        monitor
            .step(&view(1330, Some(1200), "one"), 1330)
            .desired_stage,
        None
    );
    assert_eq!(
        monitor
            .step(&view(1331, Some(1200), "one"), 1331)
            .desired_stage,
        Some(Stage::Failed)
    );
    assert_eq!(
        monitor.step(&view(1400, None, "two"), 1400).state,
        "startup"
    );
    assert_eq!(
        monitor.step(&view(1599, None, "two"), 1599).desired_stage,
        None
    );
}

#[test]
fn collector_loss_and_clock_regression_do_not_clear_a_fault() {
    let mut monitor = monitor();
    monitor.step(&view(1000, None, "one"), 1000);
    monitor.step(&view(1200, None, "one"), 1200);
    assert_eq!(
        monitor.step(&view(1220, None, "one"), 1220).desired_stage,
        Some(Stage::Failed)
    );
    let mut absent = view(1300, Some(1300), "one");
    absent.receiver_state = "stale".into();
    absent.freshness_state = "unknown".into();
    assert_eq!(monitor.step(&absent, 1300).desired_stage, None);
    assert_eq!(monitor.step(&absent, 1300).state, "unknown");
    assert_eq!(
        monitor
            .step(&view(1200, Some(1200), "one"), 1200)
            .desired_stage,
        None
    );
}

#[test]
fn invalid_policy_is_rejected() {
    let mut policy = Policy {
        timeout_ns: 100,
        startup_grace_ns: 200,
        failure_debounce_ns: 20,
        recovery_hold_ns: 30,
        poll_ns: 10,
        query_ns: 10,
    };
    policy.timeout_ns = 0;
    assert!(Monitor::new(policy).is_err());
}
