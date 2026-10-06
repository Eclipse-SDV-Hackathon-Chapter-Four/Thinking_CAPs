#!/usr/bin/env python3
"""Generate a lighting-only profile for the existing ZenohCANBridge."""
import argparse
import json
from pathlib import Path


def profile(interface="vcan0", endpoint="tcp/127.0.0.1:7447"):
    def signal(name, topic, bit):
        return {"name": name, "zenoh_key": topic, "start_bit": bit, "length": 1,
                "byte_order": "little_endian", "factor": 1, "offset": 0,
                "min": 0, "max": 1, "type": "bool"}
    return {
        "zenoh": {"mode": "client", "connect": [endpoint]},
        "publish_aggregate": True,
        "can_buses": [{"name": "zonal", "interface": interface, "bus_type": "socketcan"}],
        "can_forwarding": {"enabled": False},
        "mappings": [
            {"name": "VCU status to zonal controller", "zenoh_key": "vcu/control/status",
             "direction": "zenoh_to_can", "tx_buses": ["zonal"],
             "can_message": {"id": "0x1F1", "dlc": 8},
             "signals": [signal("vcu_cc_engage_sts", "vcu/control/cc_engage_sts", 0),
                         signal("vcu_reverse_sts", "vcu/control/reverse_sts", 1),
                         signal("vcu_brake_sts", "vcu/control/brake_sts", 2)]},
            {"name": "ThreadX lights to vehicle", "zenoh_key": "vehicle/lights/frame",
             "direction": "can_to_zenoh", "rx_buses": ["zonal"],
             "can_message": {"id": "0x1F4", "dlc": 8},
             "signals": [signal("bcm_reverse_lights_cmd", "vehicle/lights/reverse_lights_cmd", 0),
                         signal("bcm_brake_lights_cmd", "vehicle/lights/brake_lights_cmd", 1)]},
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interface", default="vcan0")
    parser.add_argument("--endpoint", default="tcp/127.0.0.1:7447")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(profile(args.interface, args.endpoint), indent=2) + "\n")
    print(args.output)
