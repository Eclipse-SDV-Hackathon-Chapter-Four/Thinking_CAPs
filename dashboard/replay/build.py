#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Build the replay page for one demo run.

Embeds the run's timeline, assertions and raw responses into template.html,
so the page shows only what the run actually observed.

    demo/replay/build.py                 # latest run in evidence/runs/
    demo/replay/build.py 20260922T134533Z
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE.parents[1] / "evidence" / "runs"


def main() -> None:
    run_id = sys.argv[1] if len(sys.argv) > 1 else sorted(p.name for p in RUNS.iterdir())[-1]
    run_dir = RUNS / run_id

    run = json.loads((run_dir / "run.json").read_text())
    timeline = []
    for line in (run_dir / "timeline.log").read_text().splitlines():
        m = re.match(r"\[T\+([\d.]+)s\] (.*)", line)
        if m:
            timeline.append({"t": float(m.group(1)), "msg": m.group(2)})
    raw = {p.stem: json.loads(p.read_text()) for p in sorted((run_dir / "raw").glob("*.json"))}

    data = {
        "run": run["run"],
        "debounce_s": run.get("debounce_s"),
        "assertions": run["assertions"],
        "timeline": timeline,
        "raw": raw,
    }
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = (HERE / "template.html").read_text().replace("__RUN_DATA__", payload)
    out = HERE / "index.html"
    out.write_text(page)
    print(f"{out} <- {run_dir.relative_to(HERE.parents[1])}")


if __name__ == "__main__":
    main()
