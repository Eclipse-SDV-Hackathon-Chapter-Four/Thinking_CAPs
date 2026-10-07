#!/usr/bin/env python3
# Copyright 2026 Eclipse SDV Hackathon Team
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: This test file was generated with OpenAI Codex. AI-generated
# portions are offered under CC0-1.0; copyrightable curation retains Apache-2.0.
# Human review pending. Assisted-by: OpenAI Codex (model version not retained)
"""Regression checks for omitted series validation and unsafe readiness claims."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from verify_contributions import check_compliance, check_patches, local_path, source_diffs


class PatchIntegrityRegression(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.record = {"id": "example#16", "patches": ["one.patch", "two.patch"], "patch_sha256s": {}}
        for name, value in [("one.patch", b"first patch"), ("two.patch", b"second patch")]:
            (self.root / name).write_bytes(value)
            self.record["patch_sha256s"][name] = hashlib.sha256(value).hexdigest()

    def test_checks_every_series_member(self):
        self.assertEqual(check_patches(self.root, self.record), 2)
        (self.root / "two.patch").write_bytes(b"corrupted second member")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            check_patches(self.root, self.record)

    def test_rejects_missing_series_member(self):
        (self.root / "two.patch").unlink()
        with self.assertRaises(FileNotFoundError):
            check_patches(self.root, self.record)

    def test_each_mail_diff_is_bound_independently_of_metadata(self):
        first = b"From " + b"a" * 40 + b" Mon Sep 17 00:00:00 2001\nFrom: human\ndiff --git a/one b/one\n+first\n"
        second = b"From " + b"b" * 40 + b" Mon Sep 17 00:00:00 2001\nFrom: human\ndiff --git a/two b/two\n+second\n"
        original = first + second
        self.assertEqual(len(source_diffs(original)), 2)
        self.assertEqual(source_diffs(original), source_diffs(original.replace(b"From: human", b"From: legal human\nAssisted-by: example")))
        self.assertNotEqual(source_diffs(original), source_diffs(original.replace(b"+second", b"+changed")))

    def test_rejects_missing_hash(self):
        self.record["patch_sha256s"].pop("two.patch")
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            check_patches(self.root, self.record)

    def test_rejects_series_path_escape(self):
        self.record["patches"] = ["../outside.patch"]
        self.record["patch_sha256s"] = {"../outside.patch": "a" * 64}
        with self.assertRaisesRegex(ValueError, "Unsafe artifact path"):
            check_patches(self.root, self.record)

    def test_rejects_symlink_escape(self):
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "leaves its record"):
            local_path(self.root, "escape/outside.patch")

    def test_blocks_ready_claim_with_open_gates(self):
        status = {"id": self.record["id"], "ready_for_official_merge": True, "remaining_gates": ["ECA failure"], "artifacts": {}}
        (self.root / "status.json").write_text(json.dumps(status))
        self.record.update(compliance_status="status.json", submission_candidate=True)
        with self.assertRaisesRegex(ValueError, "unresolved compliance gates"):
            check_compliance(self.root, self.record)

    def test_rejects_changed_source_disguised_as_metadata_correction(self):
        original = b"From: human\ndiff --git a/file b/file\n+original code\n"
        prepared = b"From: legal human\ndiff --git a/file b/file\n+changed code\n"
        (self.root / "original.patch").write_bytes(original)
        (self.root / "prepared.patch").write_bytes(prepared)
        status = {"id": self.record["id"], "ready_for_official_merge": False, "remaining_gates": [], "artifacts": {"patch": "prepared.patch"}, "patch_provenance": {"original_path": "original.patch", "original_sha256": hashlib.sha256(original).hexdigest(), "prepared_sha256": hashlib.sha256(prepared).hexdigest(), "source_diff_unchanged": True}}
        (self.root / "status.json").write_text(json.dumps(status))
        self.record.update(compliance_status="status.json", submission_candidate=False)
        with self.assertRaisesRegex(ValueError, "source diff changed"):
            check_compliance(self.root, self.record)


if __name__ == "__main__":
    unittest.main()
