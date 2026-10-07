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

//! Consumer binary for the heterogeneous service-availability stream integration test.
//!
//! Phases are synchronized with the provider through marker files (see `provider_app.rs`). In each phase the consumer
//! requires exactly one item with an exact, full identity, followed by a quiet window without further items, so
//! duplicate notifications or an unexpected service fail the test. It verifies:
//!
//! 1. initial result: a stream opened after `BigDataInterface` was offered reports it first, with the provider's
//!    instance id 2 that is absent from the consumer's own configured instance entries;
//! 2. later offer: a different interface (`MixedPrimitivesInterface`) offered after the stream was opened;
//! 3. withdrawal: produces no item; the withdrawal boundary is then confirmed through native discovery by opening
//!    probe streams until one reports exactly the remaining `MixedPrimitivesInterface`;
//! 4. re-offer: the withdrawn identity is reported again, exactly once.
//!
//! On success `run()` returns normally, so the streams and the runtime are dropped and native discovery is stopped
//! through `Drop`.

use std::path::Path;
use std::thread;
use std::time::{Duration, Instant};

use futures::channel::oneshot;
use futures::future::{select, Either};
use futures::{Stream, StreamExt};
use score_com::{
    Builder, LolaRuntimeBuilderImpl, Result as ComResult, Runtime, RuntimeBuilder, ServiceDescriptor, ServiceVersion,
};

const CONFIG_PATH: &str = "etc/config.json";
const SYNC_DIR: &str = "/tmp/all-services-stream-sync";

const PHASE_TIMEOUT: Duration = Duration::from_secs(20);
const ITEM_TIMEOUT: Duration = Duration::from_secs(5);
const QUIET_WINDOW: Duration = Duration::from_millis(1500);
const WITHDRAWAL_PROBES: u32 = 10;

#[derive(Debug)]
struct Expected {
    name: &'static str,
    version: (u32, u32),
    binding: &'static str,
    service_id: u32,
    instance_id: u32,
}

/// Provider instance of `BigDataInterface`; instance id 2 is deliberately absent from the consumer manifest.
const BIGDATA: Expected = Expected {
    name: "/score/adp/MapApiLanesStamped",
    version: (1, 0),
    binding: "lola",
    service_id: 6432,
    instance_id: 2,
};

const MIXED: Expected = Expected {
    name: "/score/test/MixedPrimitivesInterface",
    version: (1, 0),
    binding: "lola",
    service_id: 7001,
    instance_id: 1,
};

fn describe(descriptor: &ServiceDescriptor) -> String {
    format!(
        "type={} version={} binding={} service_id={} instance_id={}",
        descriptor.service_type_name(),
        descriptor.version(),
        descriptor.binding(),
        descriptor.service_id(),
        descriptor.instance_id(),
    )
}

fn matches(descriptor: &ServiceDescriptor, expected: &Expected) -> bool {
    descriptor.service_type_name() == expected.name
        && descriptor.version() == ServiceVersion::new(expected.version.0, expected.version.1)
        && descriptor.binding() == expected.binding
        && descriptor.service_id() == expected.service_id
        && descriptor.instance_id() == expected.instance_id
}

enum Next {
    Item(ServiceDescriptor),
    Timeout,
}

/// Wait for the next stream item, at most `timeout`. Errors and stream termination fail the test.
fn next_within<S>(stream: &mut S, timeout: Duration) -> Result<Next, String>
where
    S: Stream<Item = ComResult<ServiceDescriptor>> + Unpin,
{
    let (timer_tx, timer_rx) = oneshot::channel::<()>();
    thread::spawn(move || {
        thread::sleep(timeout);
        let _ = timer_tx.send(());
    });
    match futures::executor::block_on(select(stream.next(), timer_rx)) {
        Either::Left((Some(Ok(descriptor)), _)) => Ok(Next::Item(descriptor)),
        Either::Left((Some(Err(error)), _)) => Err(format!("stream yielded an error item: {error:?}")),
        Either::Left((None, _)) => Err("stream terminated while it was still owned".to_string()),
        Either::Right(_) => Ok(Next::Timeout),
    }
}

/// Require exactly one item with the expected full identity, followed by a quiet window without further items.
fn expect_exactly<S>(stream: &mut S, expected: &Expected, phase: &str) -> Result<(), String>
where
    S: Stream<Item = ComResult<ServiceDescriptor>> + Unpin,
{
    match next_within(stream, ITEM_TIMEOUT)? {
        Next::Item(descriptor) if matches(&descriptor, expected) => {
            println!("[all-services-consumer] {phase}: observed {}", describe(&descriptor));
        },
        Next::Item(descriptor) => {
            return Err(format!("{phase}: expected {expected:?}, observed {}", describe(&descriptor)));
        },
        Next::Timeout => return Err(format!("{phase}: no item for {expected:?} within {ITEM_TIMEOUT:?}")),
    }
    expect_quiet(stream, phase)
}

/// Require that no item arrives during the quiet window (no duplicates, no unexpected services).
fn expect_quiet<S>(stream: &mut S, phase: &str) -> Result<(), String>
where
    S: Stream<Item = ComResult<ServiceDescriptor>> + Unpin,
{
    match next_within(stream, QUIET_WINDOW)? {
        Next::Timeout => Ok(()),
        Next::Item(descriptor) => Err(format!("{phase}: unexpected extra item {}", describe(&descriptor))),
    }
}

/// Collect every item a stream reports within the quiet window.
fn collect_quiet<S>(stream: &mut S) -> Result<Vec<ServiceDescriptor>, String>
where
    S: Stream<Item = ComResult<ServiceDescriptor>> + Unpin,
{
    let mut items = Vec::new();
    while let Next::Item(descriptor) = next_within(stream, QUIET_WINDOW)? {
        items.push(descriptor);
    }
    Ok(items)
}

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
    Err(format!("provider did not reach phase marker {name} in time"))
}

fn run() -> Result<(), String> {
    std::fs::create_dir_all(SYNC_DIR).map_err(|error| format!("cannot create {SYNC_DIR}: {error}"))?;

    let mut runtime_builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();
    runtime_builder.load_config(Path::new(CONFIG_PATH));
    let runtime = runtime_builder.build().map_err(|error| format!("cannot build Lola runtime: {error:?}"))?;

    // Phase 1: initial result of a stream opened after the offer.
    wait_for_marker("bigdata-offered")?;
    let mut stream = runtime
        .find_all_services()
        .map_err(|error| format!("cannot open the service stream: {error:?}"))?;
    expect_exactly(&mut stream, &BIGDATA, "initial result")?;
    write_marker("consumer-saw-initial")?;

    // Phase 2: a different interface offered later.
    wait_for_marker("mixed-offered")?;
    expect_exactly(&mut stream, &MIXED, "later offer")?;
    write_marker("consumer-saw-mixed")?;

    // Phase 3: withdrawal yields no item; confirm the boundary through native discovery with probe streams.
    wait_for_marker("bigdata-withdrawn")?;
    expect_quiet(&mut stream, "withdrawal")?;
    let mut confirmed = false;
    for probe in 1..=WITHDRAWAL_PROBES {
        let mut probe_stream = runtime
            .find_all_services()
            .map_err(|error| format!("cannot open probe stream: {error:?}"))?;
        let items = collect_quiet(&mut probe_stream)?;
        drop(probe_stream);
        if items.len() == 1 && matches(&items[0], &MIXED) {
            println!("[all-services-consumer] withdrawal confirmed by probe stream {probe}");
            confirmed = true;
            break;
        }
        let seen: Vec<String> = items.iter().map(describe).collect();
        println!("[all-services-consumer] probe stream {probe} still reports {seen:?}");
    }
    if !confirmed {
        return Err("withdrawal of BigDataInterface was never visible to native discovery".to_string());
    }
    // The long-lived stream must still be quiet: the probes must not disturb it.
    expect_quiet(&mut stream, "after withdrawal probes")?;
    write_marker("consumer-confirmed-withdrawal")?;

    // Phase 4: re-offer of the withdrawn identity is reported again, exactly once.
    wait_for_marker("bigdata-reoffered")?;
    expect_exactly(&mut stream, &BIGDATA, "re-offer after withdrawal")?;
    write_marker("consumer-done")?;

    // Normal drop: stops every native watch of the stream before the runtime goes away.
    drop(stream);
    Ok(())
}

fn main() {
    match run() {
        Ok(()) => println!("[all-services-consumer] OK: initial, later, withdrawal and re-offer phases verified"),
        Err(error) => {
            eprintln!("[all-services-consumer] FAILED: {error}");
            std::process::exit(1);
        },
    }
}
