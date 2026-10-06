#!/usr/bin/env python3
"""Start the Serial2CAN bridge, preparing vcan0 first when the config uses SocketCAN.

Usage: python3 launch/bridge_launch.py [config.json] [bridge options...]
Default config: config/az3166-vcan0.json. Mirrors the Zenoh2CAN bridge launcher:
vcan setup needs sudo and is skipped on WSL2 or when the interface already exists.
"""
import json
import os
import platform
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
bridge_path = os.path.join(HERE, "..", "src", "serial2can_bridge.py")
args = sys.argv[1:]
default_config = os.path.join(HERE, "..", "config", "az3166-vcan0.json")
config_path = args.pop(0) if args and not args[0].startswith("-") else default_config

with open(config_path) as handle:
    can_config = json.load(handle)["can"]
if can_config["interface"] in ("socketcan", "socketcan_native"):
    channel = can_config["channel"]
    exists = subprocess.run(["ip", "link", "show", channel], capture_output=True, check=False).returncode == 0
    if "microsoft" in platform.uname().release.lower():
        print("Skipping vcan setup: not supported in WSL2.")
    elif not exists and channel.startswith("vcan"):
        subprocess.run("sudo modprobe vcan", shell=True, check=True)
        subprocess.run(["sudo", "ip", "link", "add", "dev", channel, "type", "vcan"], check=True)
        subprocess.run(["sudo", "ip", "link", "set", "up", channel], check=True)

command = [sys.executable, os.path.abspath(bridge_path), os.path.abspath(config_path), *args]
sys.exit(subprocess.run(command, check=False).returncode)
