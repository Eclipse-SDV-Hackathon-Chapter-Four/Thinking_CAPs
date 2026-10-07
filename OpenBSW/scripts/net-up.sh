#!/usr/bin/env bash
# Create the SIL network interfaces the OpenBSW POSIX app expects (needs sudo):
#   vcan0  SocketCAN, shared with X-Verse (reused if it already exists)
#   tap0   Ethernet for lwIP/DoIP; host 192.168.0.10/24, ECU 192.168.0.201
#   192.168.0.30/32 on lo: the simulated Ethernet zonal ECU (DoIP route 0x1040). The host
#          answers ARP for it on tap0 and on the board link, so the PC gateway and the
#          S32K148EVB both reach it.
# Mirrors OpenBSW tools/can/bring-up-vcan0.sh and tools/enet/bring-up-ethernet.sh,
# without the VLAN sub-interface. Run: sudo OpenBSW/scripts/net-up.sh
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

if ip -4 address show dev lo | grep -q "192.168.0.30/32"; then
  echo "192.168.0.30 already on lo"
else
  ip address add 192.168.0.30/32 dev lo
  echo "192.168.0.30 added to lo (simulated DoIP zonal ECU)"
fi
