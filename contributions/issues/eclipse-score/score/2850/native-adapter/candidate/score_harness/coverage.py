# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************
"""Extract schema-v1 metrics with the native docs-build metric implementation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from score_harness.consistency import needs
from src.extensions.score_metamodel.traceability_metrics import (
    compute_traceability_summary,
)


def extract_metrics(snapshot: dict[str, Any], types: list[str]) -> dict[str, Any]:
    items = list(needs(snapshot).values())
    by_type = {}
    for need_type in sorted(set(types)):
        summary = compute_traceability_summary(items, {need_type}, False, set())
        by_type[need_type] = {
            "include_not_implemented": False,
            "requirements": summary["requirements"],
            "tests": summary["tests"],
        }
    return {
        "schema_version": "1",
        "generated_by": "score_harness.coverage/native_metrics",
        "metrics_by_type": by_type,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("needs_json", type=Path)
    parser.add_argument("--json-output", required=True, type=Path)
    parser.add_argument("--need-type", action="append", default=[])
    args = parser.parse_args()
    result = extract_metrics(
        json.loads(args.needs_json.read_text()), args.need_type or ["tool_req"]
    )
    args.json_output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
