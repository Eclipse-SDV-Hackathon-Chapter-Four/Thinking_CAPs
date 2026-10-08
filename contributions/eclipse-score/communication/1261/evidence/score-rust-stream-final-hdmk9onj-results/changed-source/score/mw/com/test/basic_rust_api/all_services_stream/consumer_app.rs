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
//! Opens `Runtime::find_all_services()` and verifies that a single stream reports:
//!  * services belonging to two different configured interfaces,
//!  * a pre-existing offer and a later (delayed) offer,
//!  * a concrete provider instance id that is absent from the consumer's own configured instance entries,
//!  * a second availability item for an identity that was withdrawn and re-offered (dedup of unchanged snapshots).
//!
//! Exits 0 only when all of the above were observed; otherwise it exits 1 after a bounded deadline.

use std::collections::HashMap;
use std::path::Path;
use std::sync::mpsc;
use std::thread;
use std::time::{Duration, Instant};

use futures::channel::oneshot;
use futures::{FutureExt, StreamExt};
use score_com::{LolaRuntimeBuilderImpl, Runtime, RuntimeBuilder, ServiceDescriptor};

const CONFIG_PATH: &str = "etc/config.json";

const BIGDATA_TYPE: &str = "/score/adp/MapApiLanesStamped";
const MIXED_TYPE: &str = "/score/test/MixedPrimitivesInterface";

/// Instance id offered by the provider for `BigDataInterface`; deliberately not present in the consumer manifest.
const BIGDATA_PROVIDER_INSTANCE_ID: u32 = 2;

const POLL_TIMEOUT: Duration = Duration::from_secs(2);
const OVERALL_DEADLINE: Duration = Duration::from_secs(25);

#[derive(Default)]
struct Observed {
    /// Number of availability items observed per service type name.
    interfaces: HashMap<String, u32>,
    /// Instance ids observed for the BigData interface.
    bigdata_instance_ids: Vec<u32>,
}

impl Observed {
    fn record(&mut self, descriptor: &ServiceDescriptor) {
        println!(
            "[all-services-consumer] observed type={} version={} binding={} service_id={} instance_id={}",
            descriptor.service_type_name(),
            descriptor.version(),
            descriptor.binding(),
            descriptor.service_id(),
            descriptor.instance_id(),
        );
        *self
            .interfaces
            .entry(descriptor.service_type_name().to_string())
            .or_insert(0) += 1;
        if descriptor.service_type_name() == BIGDATA_TYPE {
            self.bigdata_instance_ids.push(descriptor.instance_id());
        }
    }

    fn satisfied(&self) -> bool {
        let big = self.interfaces.get(BIGDATA_TYPE).copied().unwrap_or(0);
        let mixed = self.interfaces.get(MIXED_TYPE).copied().unwrap_or(0);
        let provider_instance_count = self
            .bigdata_instance_ids
            .iter()
            .filter(|instance_id| **instance_id == BIGDATA_PROVIDER_INSTANCE_ID)
            .count();
        big >= 2 && mixed >= 1 && provider_instance_count >= 2
    }
}

fn main() {
    let mut runtime_builder = LolaRuntimeBuilderImpl::new();
    runtime_builder.load_config(Path::new(CONFIG_PATH));
    let runtime = runtime_builder.build().expect("Failed to build Lola runtime");

    let mut stream = runtime
        .find_all_services()
        .expect("Lola backend must support the heterogeneous service stream");
    println!("[all-services-consumer] opened heterogeneous service stream");

    // A bounded timeout mechanism implemented with a helper thread and oneshot channels.
    let (timer_tx, timer_rx) = mpsc::channel::<oneshot::Sender<()>>();
    thread::spawn(move || {
        while let Ok(reply_tx) = timer_rx.recv() {
            thread::sleep(POLL_TIMEOUT);
            let _ = reply_tx.send(());
        }
    });

    let mut observed = Observed::default();
    let deadline = Instant::now() + OVERALL_DEADLINE;

    while Instant::now() < deadline && !observed.satisfied() {
        let (tx, rx) = oneshot::channel();
        if timer_tx.send(tx).is_err() {
            break;
        }
        let timeout = rx.map(|_| ());

        match futures::executor::block_on(async { futures::future::select(stream.next(), timeout).await }) {
            futures::future::Either::Left((Some(Ok(descriptor)), _)) => observed.record(&descriptor),
            futures::future::Either::Left((Some(Err(error)), _)) => {
                // Inline errors must not terminate the stream.
                eprintln!("[all-services-consumer] stream yielded an inline error: {error:?}");
            },
            futures::future::Either::Left((None, _)) => {
                eprintln!("[all-services-consumer] stream terminated unexpectedly");
                std::process::exit(1);
            },
            futures::future::Either::Right(_) => {
                // Poll timeout: the stream stays pending, keep waiting.
            },
        }
    }

    println!("[all-services-consumer] observed summary: {:?}", observed.interfaces);
    if observed.satisfied() {
        println!(
            "[all-services-consumer] OK: two interfaces, delayed offer, withdrawal/re-offer and a provider instance \
             absent from the consumer entries were observed"
        );
        std::process::exit(0);
    }
    eprintln!("[all-services-consumer] FAILED: required stream updates were not observed before the deadline");
    std::process::exit(1);
}
