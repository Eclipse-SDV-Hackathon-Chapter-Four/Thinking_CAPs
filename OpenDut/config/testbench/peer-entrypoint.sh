#!/bin/sh
set -eu
ip link add dut0 type veth peer name dut0local
ip link set dut0 up
ip link set dut0local up
ip addr add "$DUT_ADDRESS/24" dev dut0local
ip route replace 224.0.0.0/4 dev dut0local
# Setup strings are private, never traced or printed here.
while [ ! -s /run/opendut/peer-setup ]; do sleep 1; done
OPENDUT_EDGAR_SETUP_STRING=$(cat /run/opendut/peer-setup)
export OPENDUT_EDGAR_SETUP_STRING
/opt/opendut-edgar/opendut-edgar setup managed --no-confirm --skip-service-run --skip-can --log-file=-
unset OPENDUT_EDGAR_SETUP_STRING
exec /opt/opendut/edgar/opendut-edgar service
