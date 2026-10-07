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


def provider(target, **kwargs):
    """Provider offering two different interfaces, then withdrawing and re-offering one of them."""
    return target.wrap_exec(
        "bin/all-services-provider",
        [],
        cwd="/opt/all-services-stream",
        wait_on_exit=True,
        **kwargs,
    )


def consumer(target, **kwargs):
    """Consumer asserting a single stream reports two interfaces and withdrawal/re-offer."""
    return target.wrap_exec(
        "bin/all-services-consumer",
        [],
        cwd="/opt/all-services-stream",
        wait_on_exit=True,
        **kwargs,
    )


def test_com_api_all_services_stream(target):
    """Heterogeneous service-availability stream.

    The provider offers the BigData interface immediately (with provider instance id 2, absent from the consumer
    manifest which only contains instance id 1) and a second, different interface after a delay. It then withdraws and
    re-offers the first interface. The consumer opens one system-wide stream and exits 0 only after it has observed:
    two interfaces, the delayed offer, the withdrawal/re-offer (a second availability item for the same identity) and
    the provider instance id that is absent from its own configured entries.
    """
    with (
        provider(target),
        consumer(target, wait_timeout=60),
    ):
        pass
