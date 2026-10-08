# SPDX-License-Identifier: Apache-2.0
"""Fixtures for the gateway integration tests (SWE.5).

Environment:
  ZGW_ELF        gateway executable (required)
  ZGW_RESULTS    directory for logs and CAN captures (default: ./results)
  ZGW_CAN        CAN interface (default: vcan0)
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import threading
import time
from pathlib import Path

import can
import pytest

from doip_tester import FRONT, GATEWAY_IP, REAR, Tester
from sim_ecu import SimEcu

CAN_CHANNEL = os.environ.get("ZGW_CAN", "vcan0")
RESULTS = Path(os.environ.get("ZGW_RESULTS", "results"))


class GatewayProcess:
    def __init__(self, elf: Path, log: Path):
        self.elf, self.log = elf, log
        self.proc: subprocess.Popen | None = None
        self.started_at = 0.0

    def start(self) -> "GatewayProcess":
        self.log.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, ZGW_CAN_INTERFACE=CAN_CHANNEL)
        self._logfile = self.log.open("wb")
        self.started_at = time.time()
        self.proc = subprocess.Popen(
            [str(self.elf)], stdin=subprocess.PIPE, stdout=self._logfile, stderr=subprocess.STDOUT,
            cwd=self.log.parent, env=env, start_new_session=True)
        self.wait_ready()
        return self

    def wait_ready(self, timeout: float = 10.0) -> None:
        deadline = time.time() + timeout
        while time.time() < deadline:
            assert self.proc and self.proc.poll() is None, f"gateway exited: {self.text()[-2000:]}"
            try:
                with socket.create_connection((GATEWAY_IP, 13400), timeout=0.3):
                    return
            except OSError:
                time.sleep(0.1)
        raise TimeoutError("gateway DoIP port not reachable")

    def text(self) -> str:
        return self.log.read_text(errors="replace") if self.log.exists() else ""

    def stop(self, sig: int = signal.SIGINT, timeout: float = 3.0) -> int | None:
        if not self.proc:
            return None
        if self.proc.poll() is None:
            self.proc.send_signal(sig)
            try:
                self.proc.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait()
        self._logfile.close()
        return self.proc.returncode


class CanRecorder:
    """Records every frame on the CAN bus with its timestamp."""

    def __init__(self, channel: str):
        self.frames: list[can.Message] = []
        self._bus = can.Bus(channel=channel, interface="socketcan", receive_own_messages=True)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        while not self._stop.is_set():
            msg = self._bus.recv(timeout=0.05)
            if msg is not None:
                self.frames.append(msg)

    def mark(self) -> int:
        return len(self.frames)

    def since(self, mark: int) -> list[can.Message]:
        return self.frames[mark:]

    def stop(self, dump: Path | None = None) -> None:
        self._stop.set()
        self._thread.join(timeout=2)
        self._bus.shutdown()
        if dump:
            dump.parent.mkdir(parents=True, exist_ok=True)
            with dump.open("w") as f:
                for m in self.frames:
                    f.write(f"({m.timestamp:.6f}) {CAN_CHANNEL} {m.arbitration_id:03X}#{m.data.hex().upper()}\n")


def gateway_elf() -> Path:
    elf = Path(os.environ.get("ZGW_ELF", ""))
    if not elf.is_file():
        pytest.exit("set ZGW_ELF to the built openbsw-zonal-gw.elf", returncode=4)
    return elf


@pytest.fixture(scope="module")
def can_log(request):
    recorder = CanRecorder(CAN_CHANNEL)
    yield recorder
    recorder.stop(RESULTS / f"{request.module.__name__}.candump")


@pytest.fixture(scope="module")
def gateway(request, can_log):
    proc = GatewayProcess(gateway_elf(), RESULTS / f"{request.module.__name__}-gateway.log").start()
    yield proc
    proc.stop()


@pytest.fixture(scope="module")
def rear_ecu(gateway):
    ecu = SimEcu(CAN_CHANNEL, 0x7E1, 0x7E9, "rear").start()
    yield ecu
    ecu.stop()


@pytest.fixture(autouse=True)
def _reset_rear(request):
    if "rear_ecu" in request.fixturenames:
        ecu = request.getfixturevalue("rear_ecu")
        ecu.mode = "normal"
        ecu.requests.clear()
        ecu.functional_requests.clear()
    yield


@pytest.fixture
def front_ecu(gateway):
    ecu = SimEcu(CAN_CHANNEL, 0x7E2, 0x7EA, "front").start()
    yield ecu
    ecu.stop()


@pytest.fixture
def tester(gateway):
    t = Tester()
    yield t
    t.close()
    time.sleep(0.05)


def wait_route_idle(seconds: float = 0.25) -> None:
    """Let a pending request on a route time out (P2 = 150 ms)."""
    time.sleep(seconds)


__all__ = ["REAR", "FRONT", "wait_route_idle"]
