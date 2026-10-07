#!/usr/bin/env python3

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

"""Verify retained native evidence offline; do not execute archived source."""
from __future__ import annotations

import hashlib
import json
import tarfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def local(relative: str) -> Path:
    name = PurePosixPath(relative)
    if name.is_absolute() or ".." in name.parts:
        raise ValueError(f"Unsafe packet path: {relative}")
    path = ROOT / relative
    if path.is_symlink() or not path.resolve().is_relative_to(ROOT):
        raise ValueError(f"Path escaped packet: {relative}")
    return path


def main() -> None:
    manifest = json.loads((ROOT / "manifest.json").read_text())
    actual = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*")
              if p.is_file() and p != ROOT / "manifest.json"}
    if actual != set(manifest["files"]):
        raise ValueError("Missing or unmanifested native packet files")
    for path, item in manifest["files"].items():
        file = local(path)
        if digest(file) != item["sha256"] or file.stat().st_size != item["size"]:
            raise ValueError(f"Packet mismatch: {path}")
    source = json.loads(local("evidence/source/binding.json").read_text())
    archive = local("evidence/source/docs-as-code-4bc0fbfc.tar.gz")
    if digest(archive) != source["archive_sha256"]:
        raise ValueError("Baseline archive mismatch")
    regular = {}
    with tarfile.open(archive) as bundle:
        seen = set()
        for entry in bundle:
            path = PurePosixPath(entry.name)
            if path.is_absolute() or ".." in path.parts or entry.name in seen:
                raise ValueError("Unsafe or duplicate archive entry")
            seen.add(entry.name)
            if entry.isfile():
                stream = bundle.extractfile(entry)
                if stream is None:
                    raise ValueError("Archive file unavailable")
                with stream:
                    regular[entry.name] = hashlib.file_digest(stream, "sha256").hexdigest()
            elif not entry.isdir():
                raise ValueError("Unexpected archive entry type")
    if regular != source["archive_files"]:
        raise ValueError("Baseline contents mismatch")
    patch = local("patches/0001-score-2850-assurance-harness.patch")
    if digest(patch) != source["patch_sha256"]:
        raise ValueError("Patch mismatch")
    for path, expected in source["changed_files"].items():
        if digest(local("candidate/" + path)) != expected:
            raise ValueError(f"Candidate mismatch: {path}")
    proof = json.loads(local("evidence/patch-application.json").read_text())
    if proof["patch_sha256"] != source["patch_sha256"] or not all(
        proof[key] for key in ("changed_files_match", "unchanged_contracts_match")
    ):
        raise ValueError("Patch application proof mismatch")
    counts = {split: len(list((ROOT / "candidate/score_harness/corpus" / split).glob("*/task.json")))
              for split in ("search", "heldout")}
    if counts != {"search": 30, "heldout": 10}:
        raise ValueError("Corpus count mismatch")
    rows = [json.loads(line) for line in local("evidence/runs/evolution_summary.jsonl").read_text().splitlines()]
    if len(rows) != 4:
        raise ValueError("Missing final candidate/split evaluations")
    for row in rows:
        count = counts[row["split"]]
        if row["tasks_total"] != count or row["tasks_correct"] != count:
            raise ValueError("Incorrect recorded scenario result")
        run = ROOT / "evidence/runs" / f'iteration_{row["iteration"]:03d}' / row["candidate"]
        traces = list((run / "traces").iterdir())
        if len(traces) != count or not (run / "meta.json").is_file():
            raise ValueError("Incomplete trace store")
        for trace in traces:
            for name in ("gate_output.json", "impacted_elements.json", "score.json", "agent_diff.patch"):
                if not (trace / name).is_file():
                    raise ValueError("Missing required trace artifact")
            score = json.loads((trace / "score.json").read_text())
            if not all(score[key] for key in ("verdict_correct", "gate_verdict_correct", "impacts_correct")):
                raise ValueError("Incorrect task outcome")
    junit = json.loads(local("evidence/junit-summary.json").read_text())
    if junit["total_cases"] != 274 or len(junit["targets"]) != 11 or any(
        row[key] for row in junit["targets"] for key in ("errors", "failures", "skipped")
    ):
        raise ValueError("Unexpected native test result")
    print(f"Verified {len(actual)} native packet files, {len(source['changed_files'])} candidate files, "
          "30 search / 10 held-out scenarios and recorded native evidence.")
    print("Integrity only; tests not rerun; inherited typing findings and human acceptance remain pending.")


if __name__ == "__main__":
    main()
