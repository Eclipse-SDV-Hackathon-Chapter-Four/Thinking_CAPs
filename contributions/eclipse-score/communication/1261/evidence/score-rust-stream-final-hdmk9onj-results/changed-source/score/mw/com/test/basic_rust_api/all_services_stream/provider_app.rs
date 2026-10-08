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
//! It offers two different interfaces (a pre-existing offer and a delayed offer), then withdraws and re-offers the
//! first interface, so the consumer's stream must report: two interfaces, a provider instance id that is absent from
//! the consumer's configuration, and a second availability item for the withdrawn-and-re-offered identity.
//!
//! The provider uses its own manifest (`etc/producer_config.json`) in which the `BigDataInterface` instance id is 2,
//! while the consumer manifest (`etc/config.json`) only contains instance id 1 for that type.

use std::path::Path;
use std::thread;
use std::time::Duration;

use bigdata_com_api_gen::{BigDataInterface, MixedPrimitivesInterface};
use score_com::{
    Builder, InstanceSpecifier, LolaRuntimeBuilderImpl, Producer, Runtime, RuntimeBuilder,
};

const CONFIG_PATH: &str = "etc/producer_config.json";

const PRE_EXISTING_OFFER_HOLD: Duration = Duration::from_secs(2);
const DELAYED_OFFER_HOLD: Duration = Duration::from_secs(2);
const WITHDRAWAL_HOLD: Duration = Duration::from_secs(1);
const FINAL_HOLD: Duration = Duration::from_secs(6);

fn main() {
    let mut runtime_builder = LolaRuntimeBuilderImpl::new();
    runtime_builder.load_config(Path::new(CONFIG_PATH));
    let runtime = runtime_builder.build().expect("Failed to build Lola runtime");

    // Pre-existing offer: the consumer is expected to observe this service immediately.
    let bigdata_specifier =
        InstanceSpecifier::new("/score/cp60/MapApiLanesStamped").expect("Invalid instance specifier");
    let bigdata_producer = runtime
        .producer_builder::<BigDataInterface>(bigdata_specifier)
        .build()
        .expect("Failed to build BigData producer");
    let bigdata_offered = bigdata_producer.offer().expect("Failed to offer BigData service");
    println!("[all-services-provider] offered BigDataInterface");

    thread::sleep(PRE_EXISTING_OFFER_HOLD);

    // Delayed offer: a second, different interface that becomes available later.
    let mixed_specifier =
        InstanceSpecifier::new("/IntegrationTest/MixedPrimitives").expect("Invalid instance specifier");
    let mixed_producer = runtime
        .producer_builder::<MixedPrimitivesInterface>(mixed_specifier)
        .build()
        .expect("Failed to build MixedPrimitives producer");
    let mixed_offered = mixed_producer.offer().expect("Failed to offer MixedPrimitives service");
    println!("[all-services-provider] offered MixedPrimitivesInterface");

    thread::sleep(DELAYED_OFFER_HOLD);

    // Withdraw the first interface: the stream must not report a removal, but must clear membership.
    let bigdata_producer = bigdata_offered.unoffer().expect("Failed to unoffer BigData service");
    println!("[all-services-provider] withdrew BigDataInterface");

    thread::sleep(WITHDRAWAL_HOLD);

    // Re-offer the same identity: it must be reported again.
    let bigdata_offered = bigdata_producer.offer().expect("Failed to re-offer BigData service");
    println!("[all-services-provider] re-offered BigDataInterface");

    thread::sleep(FINAL_HOLD);

    drop(bigdata_offered);
    drop(mixed_offered);
    println!("[all-services-provider] exiting");
}
