"""Unit tests of configuration handling and the per-port queueing decisions (no I/O)."""
import json
import sys
import threading
from pathlib import Path

import can
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from serial2can_bridge import IdFilter, Serial2CanBridge, SerialLink, load_config


class StubBridge:
    stopping = threading.Event()


def frame(ident=0x1F1, extended=False):
    return can.Message(arbitration_id=ident, data=bytes(8), is_extended_id=extended)


def link(**extra):
    return SerialLink(dict({"name": "ecu", "device": "/dev/null"}, **extra), StubBridge())


def test_enqueue_decisions():
    port = link(to_serial=[{"id": "0x1F1"}], tx_queue=1)
    port.enqueue(frame(0x300))
    assert port.stats["filtered_out"] == 1
    port.enqueue(frame())
    assert port.stats["dropped_offline"] == 1
    port.connected.set()
    port.enqueue(frame())
    port.enqueue(frame())
    assert port.queue.qsize() == 1 and port.stats["dropped_queue_full"] == 1


def test_link_defaults_and_validation():
    port = link()
    assert (port.baudrate, port.can_bitrate, port.reconnect_s, port.close_on_exit) == (115200, 500000, 2.0, True)
    with pytest.raises(ValueError, match="unsupported can_bitrate"):
        link(can_bitrate=33333)


def test_extended_filter_defaults_to_29_bit_mask():
    only_extended = IdFilter([{"id": 0x18DAF110, "extended": True}])
    assert only_extended.matches(frame(0x18DAF110, extended=True))
    assert not only_extended.matches(frame(0x18DAF111, extended=True))


def test_load_config_overrides_and_errors(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"can": {"interface": "virtual", "channel": "x"},
                                "serial_ports": [{"name": "zonal", "device": "/dev/ttyACM9"}]}))
    assert load_config(path, ["zonal=/dev/ttyACM1"])["serial_ports"][0]["device"] == "/dev/ttyACM1"
    for bad in (["other=/dev/ttyACM1"], ["zonal="], ["zonal"]):
        with pytest.raises(SystemExit):
            load_config(path, bad)
    path.write_text(json.dumps({"can": {"interface": "virtual", "channel": "x"}, "serial_ports": []}))
    with pytest.raises(SystemExit):
        load_config(path, [])


def test_bridge_rejects_duplicate_port_names():
    with pytest.raises(ValueError, match="unique"):
        Serial2CanBridge({"can": {"interface": "virtual", "channel": "dup"},
                          "serial_ports": [{"name": "a", "device": "/dev/null"}, {"name": "a", "device": "/dev/null"}]})


@pytest.mark.parametrize("config", sorted((Path(__file__).resolve().parents[1] / "config").glob("*.json")))
def test_shipped_configs_are_valid(config):
    loaded = load_config(config, [])
    assert {"interface", "channel"} <= set(loaded["can"])
    for port in loaded["serial_ports"]:
        SerialLink(port, StubBridge())  # validates bitrate and filters
