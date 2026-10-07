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
//!   - the **sync** one-shot wildcard returns exactly two offered `BigDataInterface` instances
//!     (one of which is absent from this consumer's configuration) and excludes the actually
//!     offered `ComplexStructInterface` instance,
//!   - `Specific` discovery compatibility,
//!   - identity honesty (no fabricated producer specifier for `Any` results),
//!   - proxy construction after the sync discovery handle is dropped, and
//!   - the **async** typed wildcard snapshot returns exactly two results, remains usable after the
//!     future/discovery are dropped, and can receive real samples.
//! * `empty`: asserts the documented no-offer native outcome for a service type that is never
//!   offered (exact `Ok(empty)`, not an error).

use clap::Parser;
use futures::executor::block_on;
use score_com::{
    Builder, ConsumerDescriptor, Error, FindServiceSpecifier, InstanceSpecifier, LolaRuntimeBuilderImpl, LolaRuntimeImpl,
    Result, Runtime, RuntimeBuilder, SampleContainer, ServiceDiscovery, ServiceFailedReason, Subscriber, Subscription,
};
use std::path::Path;
use std::thread;
use std::time::Duration;

use bigdata_com_api_gen::{
    BigDataInterface, ComplexStructInterface, ConcreteSelectorInterface, EmptySelectorInterface, MalformedSelectorInterface,
};

const CONFIG_PATH: &str = "etc/config.json";
const MAX_SAMPLES_PER_CALL: usize = 5;
const DISCOVERY_RETRY_MS: Duration = Duration::from_millis(500);
const RECEIVE_RETRY_MS: Duration = Duration::from_millis(100);

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
    // 1) Exact error propagation and selector rejection. Each case must be ServiceNotFound.
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

    // 2) Sync typed wildcard: wait until both offered BigData instances are discovered. Only the
    //    first instance exists in this consumer's configuration, so returning both is only possible
    //    via a genuine native wildcard, and the offered ComplexStructInterface instance is excluded.
    let sync_discovery = runtime.find_service::<BigDataInterface>(FindServiceSpecifier::Any);
    let sync_builders = loop {
        match sync_discovery.get_available_instances() {
            Ok(instances) if instances.len() == 2 => break instances,
            Ok(instances) => {
                println!(
                    "[find-any-consumer] Waiting for 2 BigData instances, currently {}",
                    instances.len()
                );
                thread::sleep(DISCOVERY_RETRY_MS);
            },
            Err(error) => {
                println!("[find-any-consumer] Sync Any discovery not ready yet: {:?}", error);
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

    // 3) Specific compatibility: the concrete configured instance still resolves with its real
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

    // 4) Lifetime after sync discovery drop: drop the handle, then still build a proxy from a
    //    wildcard-discovered builder. The deployment owner is runtime-owned and outlives discovery.
    drop(sync_discovery);
    for builder in &sync_builders {
        assert!(
            builder.try_get_instance_specifier().is_err(),
            "a sync Any result must not expose a producer instance specifier"
        );
    }
    let sync_consumer = sync_builders
        .into_iter()
        .next()
        .expect("At least one sync BigData instance discovered")
        .build()
        .expect("Failed to build consumer from sync Any discovery");
    drop(sync_consumer);
    println!("[find-any-consumer] Built a sync Any-discovered consumer after dropping discovery");

    // 5) Async typed wildcard snapshot: await the one-shot query, assert two typed results, then
    //    drop the future/discovery and use an async-discovered builder.
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

    // 6) Lifetime after async completion/drop: build a consumer from an async-discovered builder
    //    and receive real samples.
    let consumer = async_builders
        .into_iter()
        .next()
        .expect("At least one async BigData instance discovered")
        .build()
        .expect("Failed to build consumer from async Any discovery");
    let subscription = consumer
        .map_api_lanes_stamped_
        .subscribe(MAX_SAMPLES_PER_CALL)
        .expect("Failed to subscribe to map_api_lanes_stamped_");
    println!("[find-any-consumer] Subscribed, waiting for {} samples", num_cycles);

    let mut sample_buf = SampleContainer::new(MAX_SAMPLES_PER_CALL);
    let mut received_total = 0usize;
    let mut last_x = 0u32;
    while received_total < num_cycles {
        let want = (num_cycles - received_total).min(MAX_SAMPLES_PER_CALL);
        match subscription.try_receive(&mut sample_buf, want) {
            Ok(0) => thread::sleep(RECEIVE_RETRY_MS),
            Ok(n) => {
                received_total += n;
                while let Some(sample) = sample_buf.pop_front() {
                    assert!(sample.x >= last_x, "samples must be delivered in order");
                    last_x = sample.x;
                }
                println!("[find-any-consumer] Progress: {}/{}", received_total, num_cycles);
            },
            Err(error) => panic!("Receive failed: {:?}", error),
        }
    }

    println!(
        "[find-any-consumer] Received {} samples from an async Any-discovered instance",
        received_total
    );
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
