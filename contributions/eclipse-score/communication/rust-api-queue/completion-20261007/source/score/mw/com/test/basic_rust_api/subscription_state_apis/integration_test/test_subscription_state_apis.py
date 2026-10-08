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

"""Production-path Linux integration cases for the Rust subscription-state change API (#560).

Each case launches a fresh controller process. The controller spawns its own provider child
(handling OFFER/WITHDRAW/SEND/FINISH over a prefixed stdin/stdout protocol), so a single
``target.wrap_exec`` drives the whole scenario for that case.
"""

APP = "bin/subscription-state-apis"
APP_CWD = "/opt/subscription-state-apis"


def scenario(target, name, **kwargs):
    return target.wrap_exec(
        APP,
        ["--scenario", name],
        cwd=APP_CWD,
        wait_on_exit=True,
        **kwargs,
    )


def test_subscription_state_notifications(target):
    """Real pending-after-withdrawal and subscribed-after-reoffer callbacks on one subscription."""
    with scenario(target, "notifications", wait_timeout=180):
        pass


def test_subscription_state_handler_replacement(target):
    """A second handler replaces the first; each is disposed exactly once and only B observes."""
    with scenario(target, "replacement", wait_timeout=180):
        pass


def test_subscription_state_handler_unset(target):
    """A returning unset fences the old handler; a positive control confirms later transitions."""
    with scenario(target, "unset", wait_timeout=180):
        pass


def test_subscription_state_handler_false_then_drop(target):
    """A false-returning handler is disposed once and is not invoked again across re-offer/drop."""
    with scenario(target, "false-then-drop", wait_timeout=180):
        pass


def test_subscription_state_handler_drop_active(target):
    """Dropping a subscription with an active handler disposes it once; fresh control verifies."""
    with scenario(target, "drop-active", wait_timeout=180):
        pass
