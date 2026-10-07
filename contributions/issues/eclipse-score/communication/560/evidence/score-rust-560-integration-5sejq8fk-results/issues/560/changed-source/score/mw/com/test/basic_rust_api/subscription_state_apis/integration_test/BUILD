# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
load("//quality/integration_testing:integration_testing.bzl", "integration_test")

# Linux-only production callback coverage for the Rust subscription-state API. The QNX/ARM
# variants are intentionally not exercised here (QNX #1278 remains excluded).
integration_test(
    name = "test_subscription_state_apis",
    timeout = "moderate",
    srcs = [
        "test_subscription_state_apis.py",
    ],
    filesystem = "//score/mw/com/test/basic_rust_api/subscription_state_apis:subscription-state-apis-pkg",
    target_compatible_with = [
        "@platforms//os:linux",
        "@platforms//cpu:x86_64",
    ],
)
