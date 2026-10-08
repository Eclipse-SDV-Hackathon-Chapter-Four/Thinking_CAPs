#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Record a gateway integration run (scripts/gateway-it.sh) as SWE.5 evidence.

  record_it_evidence.py <run dir> <evidence dir>

Writes <evidence dir>/results.json (one entry per test, the executable hash, latency and
the measured CAN load) and copies the JUnit file, pytest log, gateway logs (ANSI codes
stripped) and CAN captures.
"""

from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

BITRATE = 500_000
ANSI = re.compile(r"\x1b\[[0-9;]*m")
FRAME = re.compile(r"^\((\d+\.\d+)\) \S+ ([0-9A-F]+)#([0-9A-F]*)$")


def frame_bits(dlc: int) -> int:
    """Classic CAN base frame with worst-case bit stuffing (ISO 11898-1)."""
    payload = 8 * dlc
    return 47 + payload + (34 + payload - 1) // 4


def can_load(captures: list[Path], ids: set[int]) -> dict:
    """Peak load of frames with the given IDs over any 1 s window."""
    events = []
    for capture in captures:
        for line in capture.read_text().splitlines():
            match = FRAME.match(line.strip())
            if match and int(match.group(2), 16) in ids:
                events.append((float(match.group(1)), frame_bits(len(match.group(3)) // 2)))
    events.sort()
    peak, start, window = 0, 0, 0
    for end, (timestamp, bits) in enumerate(events):
        window += bits
        while timestamp - events[start][0] > 1.0:
            window -= events[start][1]
            start += 1
        peak = max(peak, window)
    return {"frames": len(events), "peak_bits_per_s": peak, "peak_percent": round(100 * peak / BITRATE, 2),
            "ids": sorted(hex(i) for i in ids)}


def main(run: Path, out: Path) -> int:
    out.mkdir(parents=True, exist_ok=True)
    tests = []
    for junit in sorted(run.glob("junit*.xml")):
        for case in ET.parse(junit).getroot().iter("testcase"):
            failure = case.find("failure") or case.find("error")
            skipped = case.find("skipped")
            tests.append({
                "name": case.get("name"),
                "module": (case.get("classname") or "").split(".")[-1],
                "status": "failed" if failure is not None else "skipped" if skipped is not None else "passed",
                "duration_s": float(case.get("time", 0)),
                "message": (failure.get("message", "")[:300] if failure is not None else ""),
            })
    latency = {}
    if (run / "latency.txt").exists():
        for line in (run / "latency.txt").read_text().splitlines():
            key, _, value = line.partition("=")
            latency[key] = float(value) if "." in value else int(value)
    captures = sorted(run.glob("*.candump"))
    gateway_tx = {0x7DF, 0x7E1, 0x7E2}
    results = {
        "schema_version": 1,
        "run_id": run.name,
        "recorded": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "status": "passed" if tests and all(t["status"] == "passed" for t in tests) else "failed",
        "executable_sha256": (run / "elf.sha256").read_text().strip(),
        "host": {"os": platform.platform(), "python": platform.python_version(),
                 "gcc": subprocess.run(["gcc", "-dumpfullversion"], capture_output=True, text=True).stdout.strip()},
        "tests": tests,
        "latency_ms": latency,
        "can_load": {"gateway_tx": can_load(captures, gateway_tx),
                     "diagnostic_total": can_load(captures, gateway_tx | {0x7E9, 0x7EA})},
    }
    (out / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    for name in ["pytest.txt", "latency.txt", *[p.name for p in run.glob("junit*.xml")], *[p.name for p in captures]]:
        if (run / name).exists():
            shutil.copy2(run / name, out / name)
    for log in run.glob("*-gateway.log"):
        (out / log.name).write_text(ANSI.sub("", log.read_text(errors="replace")))
    passed = sum(t["status"] == "passed" for t in tests)
    print(f"recorded {passed}/{len(tests)} passed -> {out / 'results.json'}")
    return 0 if results["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main(Path(sys.argv[1]), Path(sys.argv[2])))
