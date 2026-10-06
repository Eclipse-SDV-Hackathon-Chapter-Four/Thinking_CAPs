#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# The other team's ECU: the stand-in cruise control app, a plain SOME/IP (vsomeip) application.
set -u
mkdir -p /run/sdv
# vsomeip starts SOME/IP-SD only once a route to the SD multicast group exists.
ip route add 224.244.224.245/32 dev eth0 2>/dev/null || true
cd /run/sdv
export VSOMEIP_CONFIGURATION=/opt/sdv/etc/vsomeip_cruise_ecu.json
export CRUISE_ECU_STATS=/run/sdv/cruise_ecu.json
exec /opt/sdv/bin/cruise_ecu > /run/sdv/cruise_ecu.log 2>&1
