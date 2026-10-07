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


def producer(target, num_cycles, **kwargs):
    # The provider manifest offers two BigDataInterface instances (only one of which is present in
    # the consumer manifest) plus one ComplexStructInterface instance, so the consumer's typed Any
    # query is discriminating.
    args = ["-n", str(num_cycles), "-t", "find-any", "--config", "etc/provider_config.json"]
    return target.wrap_exec("bin/bigdata-producer", args, cwd="/opt/bigdata-com-api-any", **kwargs)


def consumer(target, num_cycles, mode="positive", **kwargs):
    args = ["-n", str(num_cycles), "-m", mode]
    return target.wrap_exec(
        "bin/bigdata-consumer-any",
        args,
        cwd="/opt/bigdata-com-api-any",
        wait_on_exit=True,
        **kwargs,
    )


def test_com_api_any(target):
    """Typed find-any discovery regression.

    The client asserts exact unmapped/concrete/malformed selector rejection, two same-interface
    instances via both the sync and the async one-shot wildcard (one instance absent from its own
    configuration), an actually-offered other interface excluded, Specific compatibility, no
    fabricated Any specifier, and real sample reception after discovery is dropped.
    """
    with (
        producer(target, num_cycles=40),
        consumer(target, num_cycles=25, mode="positive", wait_timeout=180),
    ):
        pass


def test_com_api_any_no_offer(target):
    """Bounded no-offer phase: no provider is started.

    The consumer queries a valid find-any selector for a service type that is never offered and
    asserts the documented native outcome (`Ok(empty)` with zero instances, not an error).
    """
    with consumer(target, num_cycles=1, mode="empty", wait_timeout=60):
        pass
