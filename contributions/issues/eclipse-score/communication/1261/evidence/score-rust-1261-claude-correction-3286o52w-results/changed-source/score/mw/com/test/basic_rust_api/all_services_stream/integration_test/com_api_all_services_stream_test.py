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
    """Provider advancing through the offer / later offer / withdrawal / re-offer phases."""
    return target.wrap_exec(
        "bin/all-services-provider",
        [],
        cwd="/opt/all-services-stream",
        wait_on_exit=True,
        **kwargs,
    )


def consumer(target, **kwargs):
    """Consumer asserting exact items per phase on one stream, with quiet windows against duplicates."""
    return target.wrap_exec(
        "bin/all-services-consumer",
        [],
        cwd="/opt/all-services-stream",
        wait_on_exit=True,
        **kwargs,
    )


def test_com_api_all_services_stream(target):
    """Heterogeneous service-availability stream.

    Provider and consumer advance through explicit phases synchronized by marker files. For each phase the consumer
    requires exactly one item with an exact full identity (type name, version, binding, service id, instance id),
    followed by a quiet window, on a single stream: the initial result (BigData provider instance 2, which is absent
    from the consumer manifest), a later offer of a different interface (MixedPrimitives), no item on withdrawal (with
    the withdrawal boundary confirmed by probe streams), and exactly one item when the withdrawn identity is
    re-offered. Both processes exit non-zero on any deviation or timeout.
    """
    with (
        provider(target),
        consumer(target, wait_timeout=60),
    ):
        pass
