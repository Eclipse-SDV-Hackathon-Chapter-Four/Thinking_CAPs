#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Vehicle computer: gatewayd (ASIL side) first, then someipd (QM side), then our mw::com bridge.
set -u
E=/opt/sdv/etc
mkdir -p /run/sdv
# Start from a clean LoLa state. A stale service-discovery flag file from a previous run makes
# gatewayd's find-service handler run with an empty handle list, which asserts (upstream bug,
# see evidence/cruise-stage2/FINDINGS.md). Container-local paths only.
rm -rf /tmp/mw_com_lola /dev/shm/lola-* /dev/shm/*sdv* 2>/dev/null || true
# vsomeip starts SOME/IP-SD only once a route to the SD multicast group exists.
ip route add 224.244.224.245/32 dev eth0 2>/dev/null || true
cd /run/sdv
/opt/sdv/bin/gatewayd --configuration $E/vehicle_someip_config.bin \
    --service_instance_manifest $E/gatewayd_mw_com_config.json > /run/sdv/gatewayd.log 2>&1 &
sleep 1
VSOMEIP_CONFIGURATION=$E/vsomeip_vehicle.json /opt/sdv/bin/someipd \
    --configuration $E/vehicle_someip_config.bin > /run/sdv/someipd.log 2>&1 &
sleep 1
/opt/sdv/bin/cruise_bridge --config $E/bridge_mw_com_config.json --listen 0.0.0.0:7700 \
    --stats /run/sdv/bridge.json > /run/sdv/cruise_bridge.log 2>&1 &
wait -n
echo "a vehicle process exited; stopping the node" >&2
exit 1
