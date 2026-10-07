/********************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

//! bigdata-consumer-any -n <num_cycles> [-m <mode>]
//!
//! Dedicated regression consumer for the typed `FindServiceSpecifier::Any` path.
//!
//! Modes:
//! * `positive` (default): against a real two-provider setup it asserts
//!   - exact error reasons for unmapped, concrete-selector and malformed-selector registrations,
//!   - a genuine readiness barrier: the offered `ComplexStructInterface` instance is positively
//!     observed (via `Specific` discovery) *before* the wildcard exclusion is asserted, so the
//!     exclusion cannot be vacuous under scheduling,
//!   - the **sync** one-shot wildcard returns exactly two offered `BigDataInterface` instances
//!     (one of which is absent from this consumer's configuration),
//!   - BOTH returned builders are built, subscribed and actually receive samples; the producer
//!     encodes a distinct per-provider marker in `x`, and the unordered marker sets prove two
//!     distinct providers delivered (not the same instance twice and not an order artifact),
//!   - `Specific` discovery compatibility,
//!   - identity honesty (no fabricated producer specifier for `Any` results),
//!   - proxy construction and use after the sync discovery handle is dropped, and
//!   - the **async** typed wildcard snapshot returns exactly two results, remains usable after the
//!     future/discovery are dropped, and both async builders likewise deliver both markers.
//! * `empty`: asserts the documented no-offer native outcome for a service type that is never
//!   offered (exact `Ok(empty)`, not an error).
//!
//! All discovery and receive waits are bounded by an explicit deadline; the surrounding integration
//! test additionally supervises both processes with `wait_timeout`.

use clap::Parser;
use futures::executor::block_on;
use score_com::{
    Builder, ConsumerDescriptor, Error, FindServiceSpecifier, InstanceSpecifier, LolaRuntimeBuilderImpl, LolaRuntimeImpl,
    Result, Runtime, RuntimeBuilder, SampleContainer, ServiceDiscovery, ServiceFailedReason, Subscriber, Subscription,
};
use std::collections::BTreeSet;
use std::path::Path;
use std::thread;
use std::time::{Duration, Instant};

use bigdata_com_api_gen::{
    BigDataInterface, ComplexStructInterface, ConcreteSelectorInterface, EmptySelectorInterface, MalformedSelectorInterface,
};

const CONFIG_PATH: &str = "etc/config.json";
const MAX_SAMPLES_PER_CALL: usize = 5;
const DISCOVERY_RETRY_MS: Duration = Duration::from_millis(500);
const RECEIVE_RETRY_MS: Duration = Duration::from_millis(100);
/// Bound on every discovery wait so a missing provider fails fast instead of hanging.
const DISCOVERY_TIMEOUT: Duration = Duration::from_secs(60);
/// Bound on the sample-receive loop, independent of the outer process supervision timeout.
const RECEIVE_TIMEOUT: Duration = Duration::from_secs(60);
/// Upper bound on the number of samples required from each wildcard-discovered instance.
const MAX_SAMPLES_PER_PROVIDER: usize = 5;

/// Distinct marker bases encoded by the find-any producer into `MapApiLanesStamped::x`
/// (`x = marker * MARKER_STEP + index`); `x / MARKER_STEP` recovers the marker.
const MARKER_FIRST: u32 = 1;
const MARKER_SECOND: u32 = 2;
const MARKER_STEP: u32 = 1000;

#[derive(Clone, clap::ValueEnum)]
enum Mode {
    Positive,
    Empty,
}

#[derive(Parser)]
struct Args {
    /// Number of samples to receive before exiting
    #[arg(short = 'n', required = true)]
    num_cycles: usize,
    /// Consumer phase
    #[arg(short = 'm', long, default_value = "positive")]
    mode: Mode,
}

/// Asserts that discovery failed with the exact propagated reason, not merely any error.
fn assert_not_found<T>(result: Result<T>, context: &str) {
    assert!(
        matches!(result, Err(Error::ServiceError(ServiceFailedReason::ServiceNotFound))),
        "{context} must return ServiceError(ServiceNotFound)"
    );
    println!("[find-any-consumer] {context} returned ServiceNotFound as expected");
}

/// Drains up to `target` samples from each of two subscriptions in a bounded, interleaved loop and
/// returns `(first_markers, second_markers)`, the set of per-provider marker buckets observed on
/// each subscription.
///
/// Implemented as a macro because the LoLa runtime's concrete subscription type is not nameable
/// through the public `score_com` facade; the macro keeps the per-subscription buffers and counters
/// hygienic and lets type inference derive `SampleContainer`'s element type from `try_receive`.
macro_rules! drain_two_subscriptions {
    ($first_sub:ident, $second_sub:ident, $target:expr, $label:expr) => {{
        let mut first_buf = SampleContainer::new(MAX_SAMPLES_PER_CALL);
        let mut second_buf = SampleContainer::new(MAX_SAMPLES_PER_CALL);
        let mut first_seen = 0usize;
        let mut second_seen = 0usize;
        let mut first_markers: BTreeSet<u32> = BTreeSet::new();
        let mut second_markers: BTreeSet<u32> = BTreeSet::new();
        let deadline = Instant::now() + RECEIVE_TIMEOUT;
        while (first_seen < $target || second_seen < $target) && Instant::now() < deadline {
            let mut progressed = false;
            match $first_sub.try_receive(&mut first_buf, MAX_SAMPLES_PER_CALL) {
                Ok(0) => {},
                Ok(n) => {
                    progressed = true;
                    first_seen += n;
                    while let Some(sample) = first_buf.pop_front() {
                        first_markers.insert(sample.x / MARKER_STEP);
                    }
                },
                Err(error) => panic!("{} first subscription receive failed: {:?}", $label, error),
            }
            match $second_sub.try_receive(&mut second_buf, MAX_SAMPLES_PER_CALL) {
                Ok(0) => {},
                Ok(n) => {
                    progressed = true;
                    second_seen += n;
                    while let Some(sample) = second_buf.pop_front() {
                        second_markers.insert(sample.x / MARKER_STEP);
                    }
                },
                Err(error) => panic!("{} second subscription receive failed: {:?}", $label, error),
            }
            if !progressed {
                thread::sleep(RECEIVE_RETRY_MS);
            }
        }
        assert!(
            first_seen >= $target && second_seen >= $target,
            "{}: both wildcard-discovered instances must deliver real samples (first={}, second={})",
            $label,
            first_seen,
            second_seen
        );
        (first_markers, second_markers)
    }};
}

/// Asserts the unordered marker sets from the two wildcard-discovered builders: each builder must
/// map to exactly one provider, the two must differ, and together they must cover both markers.
/// This proves both distinct providers (including the one absent from the consumer configuration)
/// were exercised, independently of the order in which handles were returned.
fn assert_marker_sets(first: &BTreeSet<u32>, second: &BTreeSet<u32>, label: &str) {
    let union: BTreeSet<u32> = first.union(second).copied().collect();
    assert_eq!(
        union,
        BTreeSet::from([MARKER_FIRST, MARKER_SECOND]),
        "{label}: the two wildcard-discovered builders must map to the two distinct providers"
    );
    assert_eq!(
        first.len(),
        1,
        "{label}: the first builder must map to exactly one provider"
    );
    assert_eq!(
        second.len(),
        1,
        "{label}: the second builder must map to exactly one provider"
    );
    assert_ne!(first, second, "{label}: the two builders must map to distinct providers");
    println!("[find-any-consumer] {label}: observed distinct provider markers {union:?} from both instances");
}

/// No-offer phase: the selector resolves to a valid LoLa wildcard for a service type that is never
/// offered, so the documented sync outcome is `Ok(empty)` (never an error, never a Specific result).
fn run_empty_phase(runtime: &LolaRuntimeImpl) {
    let discovery = runtime.find_service::<EmptySelectorInterface>(FindServiceSpecifier::Any);
    let count = discovery
        .get_available_instances()
        .expect("no-offer Any discovery must return the documented Ok(empty), not an error")
        .into_iter()
        .count();
    assert_eq!(count, 0, "no-offer Any discovery must return zero instances");
    println!("[find-any-consumer] No-offer Any returned Ok(empty) with 0 instances as documented");
}

fn run_positive_phase(runtime: &LolaRuntimeImpl, num_cycles: usize) {
    // Per-provider sample target, derived from the CLI to keep `-n` meaningful but capped so the
    // second (async) round can still be satisfied from the same producer run.
    let sample_target = num_cycles.clamp(1, MAX_SAMPLES_PER_PROVIDER);

    // 1) Exact error propagation and selector rejection. Each case must be ServiceNotFound. These do
    //    not depend on any offer, so they run first.
    assert_not_found(
        runtime
            .find_service::<ComplexStructInterface>(FindServiceSpecifier::Any)
            .get_available_instances(),
        "unmapped-interface Any",
    );
    assert_not_found(
        runtime
            .find_service::<ConcreteSelectorInterface>(FindServiceSpecifier::Any)
            .get_available_instances(),
        "concrete-selector Any",
    );
    assert_not_found(
        runtime
            .find_service::<MalformedSelectorInterface>(FindServiceSpecifier::Any)
            .get_available_instances(),
        "malformed-selector Any",
    );

    // 2) Genuine readiness barrier for the *other* interface. Positively observe that the offered
    //    ComplexStructInterface instance exists (via a real Specific discovery, not a sleep) before
    //    asserting that the BigData wildcard excludes it, so the exclusion is not vacuous.
    let complex_specifier =
        InstanceSpecifier::new("/UserDefinedTest/ComplexStruct").expect("Invalid instance specifier");
    let complex_discovery =
        runtime.find_service::<ComplexStructInterface>(FindServiceSpecifier::Specific(complex_specifier));
    let barrier_deadline = Instant::now() + DISCOVERY_TIMEOUT;
    loop {
        match complex_discovery.get_available_instances() {
            Ok(instances) if !instances.is_empty() => {
                println!(
                    "[find-any-consumer] Readiness barrier: offered ComplexStructInterface observed ({} instance(s))",
                    instances.len()
                );
                break;
            },
            Ok(_) => {
                assert!(
                    Instant::now() < barrier_deadline,
                    "timed out waiting for the offered ComplexStructInterface readiness barrier"
                );
                thread::sleep(DISCOVERY_RETRY_MS);
            },
            Err(error) => {
                assert!(
                    Instant::now() < barrier_deadline,
                    "ComplexStructInterface readiness barrier did not succeed: {error:?}"
                );
                thread::sleep(DISCOVERY_RETRY_MS);
            },
        }
    }

    // 3) Sync typed wildcard: wait until both offered BigData instances are discovered. Only the
    //    first instance exists in this consumer's configuration; the second is offered solely from
    //    the provider manifest, so returning both is only possible via a genuine native wildcard.
    let sync_discovery = runtime.find_service::<BigDataInterface>(FindServiceSpecifier::Any);
    let sync_deadline = Instant::now() + DISCOVERY_TIMEOUT;
    let sync_builders = loop {
        match sync_discovery.get_available_instances() {
            Ok(instances) if instances.len() == 2 => break instances,
            Ok(instances) => {
                assert!(
                    Instant::now() < sync_deadline,
                    "timed out waiting for the two offered BigData instances, saw {}",
                    instances.len()
                );
                println!(
                    "[find-any-consumer] Waiting for 2 BigData instances, currently {}",
                    instances.len()
                );
                thread::sleep(DISCOVERY_RETRY_MS);
            },
            Err(error) => {
                assert!(
                    Instant::now() < sync_deadline,
                    "sync Any discovery did not become ready: {error:?}"
                );
                println!("[find-any-consumer] Sync Any discovery not ready yet: {error:?}");
                thread::sleep(DISCOVERY_RETRY_MS);
            },
        }
    };
    assert_eq!(
        sync_builders.len(),
        2,
        "sync typed Any must return exactly the two offered BigData instances"
    );
    println!("[find-any-consumer] Sync Any discovered exactly 2 BigData instances");
    for builder in &sync_builders {
        assert!(
            builder.try_get_instance_specifier().is_err(),
            "a sync Any result must not expose a producer instance specifier"
        );
    }

    // 4) Specific compatibility: the concrete configured instance still resolves with its real
    //    producer specifier.
    let specific_instance =
        InstanceSpecifier::new("/score/cp60/MapApiLanesStamped").expect("Invalid instance specifier");
    let specific_builder = runtime
        .find_service::<BigDataInterface>(FindServiceSpecifier::Specific(specific_instance.clone()))
        .get_available_instances()
        .expect("Specific BigData discovery failed")
        .into_iter()
        .next()
        .expect("Specific BigData instance missing");
    assert_eq!(
        specific_builder
            .try_get_instance_specifier()
            .expect("Specific instance must expose a producer specifier")
            .as_ref(),
        specific_instance.as_ref()
    );
    println!("[find-any-consumer] Specific discovery remains compatible");

    // 5) Lifetime after sync discovery drop + use BOTH wildcard-discovered builders. The
    //    deployment owner is runtime-owned and outlives discovery, so proxies can still be built and
    //    used after the discovery handle is dropped.
    drop(sync_discovery);
    let mut sync_iter = sync_builders.into_iter();
    let sync_first_builder = sync_iter.next().expect("first sync BigData builder");
    let sync_second_builder = sync_iter.next().expect("second sync BigData builder");
    assert!(
        sync_iter.next().is_none(),
        "wildcard must not return more than the two offered instances"
    );
    let sync_first_consumer = sync_first_builder
        .build()
        .expect("Failed to build consumer from first sync Any builder");
    let sync_second_consumer = sync_second_builder
        .build()
        .expect("Failed to build consumer from second sync Any builder");
    let sync_first_sub = sync_first_consumer
        .map_api_lanes_stamped_
        .subscribe(MAX_SAMPLES_PER_CALL)
        .expect("Failed to subscribe on first sync Any consumer");
    let sync_second_sub = sync_second_consumer
        .map_api_lanes_stamped_
        .subscribe(MAX_SAMPLES_PER_CALL)
        .expect("Failed to subscribe on second sync Any consumer");
    let (sync_first_markers, sync_second_markers) =
        drain_two_subscriptions!(sync_first_sub, sync_second_sub, sample_target, "sync Any");
    assert_marker_sets(&sync_first_markers, &sync_second_markers, "sync Any");
    // Release the sync subscriptions before the async phase so the per-instance sample-slot pool is
    // not held by two subscriptions per instance at the same time.
    drop(sync_first_sub);
    drop(sync_second_sub);
    drop(specific_builder);

    // 6) Async typed wildcard snapshot: await the one-shot query, assert two typed results, then
    //    drop the future/discovery and build/use BOTH async-discovered builders.
    let async_discovery = runtime.find_service::<BigDataInterface>(FindServiceSpecifier::Any);
    let async_builders = block_on(async_discovery.get_available_instances_async())
        .expect("async Any discovery must complete with the offered instances");
    assert_eq!(
        async_builders.len(),
        2,
        "async typed Any snapshot must return exactly the two offered BigData instances"
    );
    println!("[find-any-consumer] Async Any snapshot returned exactly 2 BigData instances");
    drop(async_discovery);
    for builder in &async_builders {
        assert!(
            builder.try_get_instance_specifier().is_err(),
            "an async Any result must not expose a producer instance specifier"
        );
    }
    let mut async_iter = async_builders.into_iter();
    let async_first_builder = async_iter.next().expect("first async BigData builder");
    let async_second_builder = async_iter.next().expect("second async BigData builder");
    assert!(
        async_iter.next().is_none(),
        "wildcard must not return more than the two offered instances"
    );
    let async_first_consumer = async_first_builder
        .build()
        .expect("Failed to build consumer from first async Any builder");
    let async_second_consumer = async_second_builder
        .build()
        .expect("Failed to build consumer from second async Any builder");
    let async_first_sub = async_first_consumer
        .map_api_lanes_stamped_
        .subscribe(MAX_SAMPLES_PER_CALL)
        .expect("Failed to subscribe on first async Any consumer");
    let async_second_sub = async_second_consumer
        .map_api_lanes_stamped_
        .subscribe(MAX_SAMPLES_PER_CALL)
        .expect("Failed to subscribe on second async Any consumer");
    let (async_first_markers, async_second_markers) =
        drain_two_subscriptions!(async_first_sub, async_second_sub, sample_target, "async Any");
    assert_marker_sets(&async_first_markers, &async_second_markers, "async Any");
}

fn main() {
    let args = Args::parse();

    // Initialise the Lola runtime with the consumer configuration.
    let mut runtime_builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();
    runtime_builder.load_config(Path::new(CONFIG_PATH));
    let runtime = runtime_builder.build().expect("Failed to build Lola runtime");

    match args.mode {
        Mode::Empty => run_empty_phase(&runtime),
        Mode::Positive => run_positive_phase(&runtime, args.num_cycles),
    }
}
