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

"""Retain every final native copyright error and identify contribution overlap."""
import json
import re
import subprocess

from measure import PACKET, ROOT


def update(record="license-headers-communication-copyright-verified"):
    measurement = json.loads((PACKET / "evidence" / (record + ".json")).read_text())
    text = (PACKET / "evidence" / (record + ".stderr")).read_text()
    text = re.sub(r"\x1b\[[0-9;]*m", "", text)
    prefix = re.escape(str(ROOT / "candidate")) + "/"
    errors = []
    for line in text.splitlines():
        match = re.search(r"ERROR: (.*?) in: " + prefix + r"([^,\n]+)", line)
        if match:
            path = match[2].split(" (similarity")[0].split(" (repeated")[0]
            errors.append({"kind": match[1], "path": path})
        else:
            match = re.search(r"ERROR: Copyright header in " + prefix + r"(.*?) is preceded", line)
            if match:
                errors.append({"kind": "Wrong copyright format preceded by content", "path": match[1]})
    source = ROOT / "candidate"
    changed = set(subprocess.check_output(["git", "diff", "HEAD", "--name-only"], cwd=source, text=True).splitlines())
    changed.update(subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=source, text=True).splitlines())
    overlap = [e for e in errors if e["path"] in changed]
    assert not overlap, overlap
    assert measurement["exit_code"] == 0 and not errors, errors
    assert not measurement["changed_during_execution"]
    result = {"record": "evidence/" + record + ".json", "source_revision": "cef680454e8586daca9f953084dca33fb3759d0c",
              "counts": {"missing": 0, "wrong_format": 0, "duplicate": 0, "license_mismatch": 0},
              "errors": errors, "errors_in_changed_files": overlap,
              "corrections": "Repository-wide notice cleanup and extended code-file audit; existing numeric years and imported MIT/CC0 licenses retained. See license-header-audit.json.",
              "disposition": "Native full-repository copyright check passes. The literal template resource is excluded using the supported exclusion mechanism, as in upstream S-CORE tooling. Before-state failures are retained in license-header-history/copyright-current-disposition.json."}
    (PACKET / "copyright-current-disposition.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Final copyright: zero native failures")


if __name__ == "__main__":
    update()
