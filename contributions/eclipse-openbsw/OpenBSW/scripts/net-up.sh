#!/usr/bin/env bash
# Create the SIL network interfaces the OpenBSW POSIX app expects (needs sudo):
#   vcan0  SocketCAN, shared with X-Verse (reused if it already exists)
#   tap0   Ethernet for lwIP/DoIP; host 192.168.0.10/24, ECU 192.168.0.201
# Mirrors OpenBSW tools/can/bring-up-vcan0.sh and tools/enet/bring-up-ethernet.sh,
# without the VLAN sub-interface. Run: sudo contributions/eclipse-openbsw/OpenBSW/scripts/net-up.sh
set -euo pipefail
owner="${SUDO_USER:-$USER}"

if ip link show vcan0 >/dev/null 2>&1; then
  echo "vcan0 exists; reusing it"
else
  modprobe vcan
  ip link add dev vcan0 type vcan
  ip link set up vcan0
  echo "vcan0 created"
fi

if ip link show tap0 >/dev/null 2>&1; then
  echo "tap0 exists; reusing it"
else
  ip tuntap add dev tap0 mode tap user "$owner"
  ip address add 192.168.0.10/24 dev tap0
  ip link set tap0 up
  echo "tap0 created for user $owner"
fi
