#!/bin/sh
set -eu
endpoint=$1
interface=$2
timeout_ms=$3
bridge_interface=$4
cd /var/lib/sdv-lighting
python3 - <<'PY'
import hashlib,json
from pathlib import Path
for name, expected in json.load(open('build.json'))['files'].items():
    actual=hashlib.sha256(Path(name).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit('Workload bundle file digest mismatch: '+name)
PY
. /etc/os-release
[ "$ID" = autosd ]
command -v podman
modprobe vxcan
# Own only this deployment's avcan0; do not reuse somebody else's interface.
if ip link show "$interface" >/dev/null 2>&1 && [ ! -e can-interface-owned ]; then
    echo 'CAN interface exists without ownership receipt' >&2
    exit 1
fi
if ! ip link show "$interface" >/dev/null 2>&1; then
    if ip link show "$bridge_interface" >/dev/null 2>&1; then
        echo 'Bridge CAN endpoint exists without a controller endpoint' >&2
        exit 1
    fi
    ip link add dev "$interface" type vxcan peer name "$bridge_interface"
    touch can-interface-owned
fi
ip link set dev "$interface" up
ip link set dev "$bridge_interface" up
podman load -i workload-image.tar
mkdir -p state
chmod 755 state
podman run --rm --network none -v /var/lib/sdv-lighting:/config:z sdv-autosd-lighting:1.0 \
    python3 scripts/configure_bridge.py --interface "$bridge_interface" --endpoint "$endpoint" \
    --output /config/bridge.json
cat > /etc/sdv-lighting.env <<EOF
CAN_INTERFACE=$interface
BRIDGE_CAN_INTERFACE=$bridge_interface
INPUT_TIMEOUT_MS=$timeout_ms
EOF
install -m 755 sdv-lighting-diagnostics /usr/local/bin/sdv-lighting-diagnostics
restorecon /usr/local/bin/sdv-lighting-diagnostics
install -m 644 sdv-*.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable sdv-can sdv-image sdv-lighting-diagnostics sdv-zenoh-can sdv-threadx
systemctl start sdv-can sdv-image sdv-lighting-diagnostics sdv-zenoh-can
# Give the bridge a subscriber before ThreadX sends its initial OFF frame.
sleep 2
systemctl start sdv-threadx
rm -f /var/tmp/sdv-workload.tar
systemctl --no-pager status sdv-threadx sdv-zenoh-can sdv-lighting-diagnostics
