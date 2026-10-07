# SPDX-License-Identifier: Apache-2.0
"""Qualification with the ThreadX rear lighting ECU (QTC-14, OP-2).

The actual ThreadX controller (ThreadX/ on branch feature/threadx-uds-server, image given by
ZGW_THREADX_IMAGE) runs in Docker on the host's vcan0 with its UDS-on-CAN server
(0x7E1/0x7E9) and its lighting function (0x1F1 -> 0x1F4). The gateway routes to it as
route 0x1020. The module is skipped without ZGW_THREADX_IMAGE.

  ZGW_THREADX_IMAGE=threadx-zonal-lights:1.1.0-uds OpenBSW/scripts/gateway-it.sh test_threadx_ecu.py
"""

from __future__ import annotations

import os
import subprocess
import time

import can
import pytest

from conftest import CAN_CHANNEL, RESULTS
from doip_tester import FUNCTIONAL, GATEWAY, REAR

IMAGE = os.environ.get("ZGW_THREADX_IMAGE", "")
pytestmark = pytest.mark.skipif(not IMAGE, reason="set ZGW_THREADX_IMAGE to a ThreadX image with the UDS server")
U0293 = 0xC29300
INPUT_TIMEOUT_MS = 1000


@pytest.fixture(scope="module")
def threadx(gateway):
    """The ThreadX controller in Docker on the host CAN interface, with the input timeout on."""
    name = f"zgw-qtc14-{os.getpid()}"
    log = (RESULTS / "threadx-ecu.log").open("wb")
    proc = subprocess.Popen(
        ["docker", "run", "--rm", "--init", "--name", name, "--network", "host", "--cap-add", "SYS_NICE",
         "--ulimit", "rtprio=3:3", IMAGE, "threadx-zonal-lights", "--interface", CAN_CHANNEL,
         "--timeout-ms", str(INPUT_TIMEOUT_MS)],
        stdout=log, stderr=subprocess.STDOUT)
    bus = can.Bus(channel=CAN_CHANNEL, interface="socketcan")
    deadline = time.time() + 20
    while time.time() < deadline:  # the startup lights-off frame shows that it runs
        msg = bus.recv(timeout=0.2)
        if msg is not None and msg.arbitration_id == 0x1F4:
            break
    else:
        proc.kill()
        pytest.fail("ThreadX controller did not start (no 0x1F4 frame)")
    yield bus
    subprocess.run(["docker", "stop", "-t", "5", name], capture_output=True, timeout=30)
    proc.wait(timeout=30)
    log.close()
    bus.shutdown()
    (RESULTS / "threadx-image.txt").write_text(
        subprocess.run(["docker", "image", "inspect", "--format", "{{.Id}}", IMAGE],
                       capture_output=True, text=True).stdout)


def send_status(bus: can.BusABC, brake: bool, reverse: bool) -> can.Message:
    """VCU status on 0x1F1; returns the controller's 0x1F4 light command."""
    while bus.recv(timeout=0) is not None:
        pass
    status = (0x04 if brake else 0) | (0x02 if reverse else 0)
    bus.send(can.Message(arbitration_id=0x1F1, data=bytes([status]) + bytes(7), is_extended_id=False))
    deadline = time.time() + 2
    while time.time() < deadline:
        msg = bus.recv(timeout=0.1)
        if msg is not None and msg.arbitration_id == 0x1F4:
            return msg
    raise TimeoutError("no light command on 0x1F4")


def read_dtcs(tester, mask: int = 0xFF) -> dict[int, int]:
    payload = tester.request(REAR, bytes([0x19, 0x02, mask])).responses[-1][1]
    records = payload[3:]
    return {int.from_bytes(records[i:i + 3], "big"): records[i + 3] for i in range(0, len(records), 4)}


def test_threadx_identification(threadx, tester):
    """SWR-012, SWR-014: the gateway routes to the ThreadX ECU; segmented response forwarded."""
    version = tester.read_did(REAR, 0xF195)[3:].decode()
    assert version.startswith("THREADX-LIGHTS "), version
    assert tester.read_did(REAR, 0xF18C)[3:] == b"TXZL-SIM-0001"
    assert tester.request(REAR, b"\x10\x03").responses == [(REAR, b"\x50\x03\x00\x32\x01\xF4")]
    assert tester.request(REAR, b"\x2E\xF1\x90\x00").responses == [(REAR, b"\x7F\x2E\x11")]


def test_threadx_lighting_unaffected_and_state_readable(threadx, tester):
    """SWR-030, SWR-033: lighting keeps working while it is diagnosed; DID 4C01 shows it."""
    assert send_status(threadx, brake=True, reverse=False).data[0] == 0x02
    assert tester.read_did(REAR, 0x4C01)[3:] == b"\x02\x00"
    assert send_status(threadx, brake=True, reverse=True).data[0] == 0x03
    assert tester.read_did(REAR, 0x4C01)[3:] == b"\x03\x00"
    assert send_status(threadx, brake=False, reverse=False).data[0] == 0x00


def test_threadx_functional_tester_present(threadx, tester):
    """SWR-013: functional TesterPresent answered by the gateway and the ThreadX ECU."""
    result = tester.request(FUNCTIONAL, b"\x3E\x00", wait=0.5, until_final=False)
    assert (GATEWAY, b"\x7E\x00") in result.responses and (REAR, b"\x7E\x00") in result.responses


def test_threadx_dtc_through_the_gateway(threadx, tester):
    """SWR-024, SWR-025 end to end: the ECU's own DTC U0293 (VCU status lost) is read and
    cleared through the gateway; recovery passes the test."""
    send_status(threadx, brake=False, reverse=False)
    assert tester.request(REAR, b"\x14\xFF\xFF\xFF").responses == [(REAR, b"\x54")]
    time.sleep(INPUT_TIMEOUT_MS / 1000 + 0.5)  # no status: the controller's input timeout
    assert read_dtcs(tester, 0x09).get(U0293) == 0x2F
    send_status(threadx, brake=False, reverse=False)  # recovery: test passed
    assert read_dtcs(tester).get(U0293) == 0x2E
    assert tester.request(REAR, b"\x14\xFF\xFF\xFF").responses == [(REAR, b"\x54")]
    assert read_dtcs(tester, 0x09).get(U0293) is None


def test_threadx_reachability_routine(threadx, tester):
    """SWR-026: routine F000 reports the ThreadX ECU (0x1020) as reached."""
    assert tester.request(GATEWAY, b"\x31\x01\xF0\x00").responses == [(GATEWAY, b"\x71\x01\xF0\x00")]
    time.sleep(2.2)
    payload = tester.request(GATEWAY, b"\x31\x03\xF0\x00").responses[-1][1]
    assert payload[:6] == b"\x71\x03\xF0\x00\x00\x03" and payload[6] == 0x01, payload.hex()
