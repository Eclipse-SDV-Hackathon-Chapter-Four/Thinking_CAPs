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

//! Provider binary for the heterogeneous service-availability stream integration test.
//!
//! The provider and the consumer advance through explicit phases, synchronized by marker files in
//! [`SYNC_DIR`], so every availability transition happens at a point the consumer can attribute:
//!
//! 1. offer `BigDataInterface` (instance id 2, absent from the consumer manifest), then wait for the consumer to
//!    report it as an initial result of a freshly opened stream;
//! 2. offer `MixedPrimitivesInterface` (a different interface) and wait until the consumer reported it as a later
//!    offer;
//! 3. withdraw `BigDataInterface` and wait until the consumer has confirmed the withdrawal through native discovery;
//! 4. re-offer the same `BigDataInterface` identity and wait until the consumer is done.
//!
//! Every wait is bounded; the provider exits with an error if the consumer does not progress.

use std::path::Path;
use std::thread;
use std::time::{Duration, Instant};

use bigdata_com_api_gen::{BigDataInterface, MixedPrimitivesInterface};
use score_com::{
    Builder, InstanceSpecifier, LolaRuntimeBuilderImpl, OfferedProducer, Producer, Runtime, RuntimeBuilder,
};

const CONFIG_PATH: &str = "etc/producer_config.json";
const SYNC_DIR: &str = "/tmp/all-services-stream-sync";
const PHASE_TIMEOUT: Duration = Duration::from_secs(20);

fn write_marker(name: &str) -> Result<(), String> {
    std::fs::write(Path::new(SYNC_DIR).join(name), b"").map_err(|error| format!("cannot write marker {name}: {error}"))
}

fn wait_for_marker(name: &str) -> Result<(), String> {
    let marker = Path::new(SYNC_DIR).join(name);
    let deadline = Instant::now() + PHASE_TIMEOUT;
    while Instant::now() < deadline {
        if marker.exists() {
            return Ok(());
        }
        thread::sleep(Duration::from_millis(20));
    }
    Err(format!("consumer did not reach phase marker {name} in time"))
}

fn run() -> Result<(), String> {
    std::fs::create_dir_all(SYNC_DIR).map_err(|error| format!("cannot create {SYNC_DIR}: {error}"))?;

    let mut runtime_builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();
    runtime_builder.load_config(Path::new(CONFIG_PATH));
    let runtime = runtime_builder.build().map_err(|error| format!("cannot build Lola runtime: {error:?}"))?;

    // Phase 1: pre-existing offer, observed as an initial result.
    let bigdata_specifier = InstanceSpecifier::new("/score/cp60/MapApiLanesStamped")
        .map_err(|error| format!("invalid BigData specifier: {error:?}"))?;
    let bigdata_producer = runtime
        .producer_builder::<BigDataInterface>(bigdata_specifier)
        .build()
        .map_err(|error| format!("cannot build BigData producer: {error:?}"))?;
    let bigdata_offered = bigdata_producer
        .offer()
        .map_err(|error| format!("cannot offer BigData: {error:?}"))?;
    println!("[all-services-provider] offered BigDataInterface");
    write_marker("bigdata-offered")?;
    wait_for_marker("consumer-saw-initial")?;

    // Phase 2: a different interface offered after the stream was opened.
    let mixed_specifier = InstanceSpecifier::new("/IntegrationTest/MixedPrimitives")
        .map_err(|error| format!("invalid MixedPrimitives specifier: {error:?}"))?;
    let mixed_producer = runtime
        .producer_builder::<MixedPrimitivesInterface>(mixed_specifier)
        .build()
        .map_err(|error| format!("cannot build MixedPrimitives producer: {error:?}"))?;
    let mixed_offered = mixed_producer
        .offer()
        .map_err(|error| format!("cannot offer MixedPrimitives: {error:?}"))?;
    println!("[all-services-provider] offered MixedPrimitivesInterface");
    write_marker("mixed-offered")?;
    wait_for_marker("consumer-saw-mixed")?;

    // Phase 3: withdrawal. The consumer confirms it through native discovery before the re-offer happens.
    let bigdata_producer = bigdata_offered
        .unoffer()
        .map_err(|error| format!("cannot withdraw BigData: {error:?}"))?;
    println!("[all-services-provider] withdrew BigDataInterface");
    write_marker("bigdata-withdrawn")?;
    wait_for_marker("consumer-confirmed-withdrawal")?;

    // Phase 4: re-offer of the same identity.
    let bigdata_offered = bigdata_producer
        .offer()
        .map_err(|error| format!("cannot re-offer BigData: {error:?}"))?;
    println!("[all-services-provider] re-offered BigDataInterface");
    write_marker("bigdata-reoffered")?;
    wait_for_marker("consumer-done")?;

    drop(bigdata_offered);
    drop(mixed_offered);
    Ok(())
}

fn main() {
    match run() {
        Ok(()) => println!("[all-services-provider] OK: all phases completed"),
        Err(error) => {
            eprintln!("[all-services-provider] FAILED: {error}");
            std::process::exit(1);
        },
    }
}
