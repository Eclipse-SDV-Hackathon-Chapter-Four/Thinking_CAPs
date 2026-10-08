use sdv_receiver_diagnostics::{Budgets, Cache, Observation};
use serde_json::json;

fn observation(now: u64, speed_time: Option<u64>, session: &str) -> Observation {
    serde_json::from_value(json!({
        "schema_version":1, "source_instance":"cruise-control", "source_session":session,
        "boot_id":"boot", "clock_domain":"linux-clock-monotonic",
        "observed_at_monotonic_ns":now, "received_at_monotonic_ns":speed_time,
        "last_accepted_at_monotonic_ns":speed_time, "vehicle_speed":speed_time.map(|_| 42.0),
        "target_speed":42.0, "cc_state":"engaged", "software_identity":"test-build",
        "sample_id":null, "integrity_result":"not_available", "acceptance_kind":"decoded_by_consumer"
    })).unwrap()
}

fn cache() -> Cache {
    Cache::new(
        "boot".into(),
        Budgets {
            speed_ns: 100,
            heartbeat_ns: 200,
        },
    )
}

#[test]
fn no_collector_is_unknown() {
    let view = cache().view(1000);
    assert_eq!(view.receiver_state, "unknown");
    assert_eq!(view.freshness_state, "unknown");
    assert!(view.observation.is_none());
}

#[test]
fn other_events_do_not_refresh_speed() {
    let mut cache = cache();
    cache
        .accept(observation(1000, Some(1000), "one"), 1000)
        .unwrap();
    assert_eq!(cache.view(1100).freshness_state, "fresh");
    cache
        .accept(observation(1101, Some(1000), "one"), 1101)
        .unwrap();
    assert_eq!(cache.view(1101).receiver_state, "available");
    assert_eq!(cache.view(1101).freshness_state, "stale");
    assert_eq!(cache.view(1302).receiver_state, "stale");
    assert_eq!(cache.view(1302).freshness_state, "unknown");
}

#[test]
fn receipt_does_not_refresh_acceptance() {
    let mut cache = cache();
    let mut obs = observation(1200, Some(1000), "one");
    obs.received_at_monotonic_ns = Some(1200);
    cache.accept(obs, 1200).unwrap();
    let view = cache.view(1200);
    assert_eq!(view.received_age_ns, Some(0));
    assert_eq!(view.accepted_age_ns, Some(200));
    assert_eq!(view.freshness_state, "stale");
}

#[test]
fn future_wrong_boot_and_clock_are_rejected() {
    let mut cache = cache();
    assert!(cache.accept(observation(1001, None, "one"), 1000).is_err());
    let mut obs = observation(1000, None, "one");
    obs.boot_id = "other".into();
    assert!(cache.accept(obs, 1000).is_err());
    let mut obs = observation(1000, None, "one");
    obs.clock_domain = "simulation".into();
    assert!(cache.accept(obs, 1000).is_err());
    assert!(cache.view(1000).observation.is_none());
}

#[test]
fn restart_does_not_resurrect_old_session() {
    let mut cache = cache();
    cache
        .accept(observation(1000, Some(1000), "one"), 1000)
        .unwrap();
    cache.accept(observation(1100, None, "two"), 1100).unwrap();
    assert_eq!(cache.view(1100).freshness_state, "unknown");
    assert!(
        cache
            .accept(observation(1200, Some(1200), "one"), 1200)
            .is_err()
    );
}

#[test]
fn backwards_and_impossible_acceptance_are_rejected() {
    let mut cache = cache();
    cache
        .accept(observation(1000, Some(1000), "one"), 1000)
        .unwrap();
    assert!(
        cache
            .accept(observation(999, Some(999), "one"), 1001)
            .is_err()
    );
    let mut obs = observation(1100, Some(1100), "one");
    obs.received_at_monotonic_ns = None;
    assert!(cache.accept(obs, 1100).is_err());
    let mut obs = observation(1200, Some(1200), "one");
    obs.vehicle_speed = None;
    assert!(cache.accept(obs, 1200).is_err());
}
