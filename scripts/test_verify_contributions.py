#!/usr/bin/env python3
# Copyright 2026 Eclipse SDV Hackathon Team
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: This test file was generated with OpenAI Codex. AI-generated
# portions are offered under CC0-1.0; copyrightable curation retains Apache-2.0.
# Human review pending. Assisted-by: OpenAI Codex (model version not retained)
"""Regression checks for patch series, readiness claims, contribution formats and integrity failures."""

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

try:
    from .verify_contributions import (check_compliance, check_manifest, check_patches, local_path,
                                       snapshot_observation, source_diffs, verify)
except ImportError:
    from verify_contributions import (check_compliance, check_manifest, check_patches, local_path,
                                      snapshot_observation, source_diffs, verify)


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

    def test_rejects_tampered_prepared_native_evidence(self):
        evidence = b"91 tests passed\n"
        (self.root / "native-results.json").write_bytes(evidence)
        (self.root / "manifest.json").write_text(json.dumps({"files": {
            "native-results.json": hashlib.sha256(evidence).hexdigest()
        }}))
        status = {"id": self.record["id"], "ready_for_official_merge": False,
                  "remaining_gates": ["Human review"],
                  "artifacts": {"evidence_manifest": "manifest.json"}}
        (self.root / "status.json").write_text(json.dumps(status))
        self.record.update(compliance_status="status.json", submission_candidate=False)
        self.assertFalse(check_compliance(self.root, self.record))
        (self.root / "native-results.json").write_bytes(b"invented passing results\n")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            check_compliance(self.root, self.record)



class ContributionVerificationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.artifact = self.root / "artifact.txt"
        self.artifact.write_bytes(b"preserved native evidence\n")
        self.sha = hashlib.sha256(self.artifact.read_bytes()).hexdigest()
        self.manifest = self.root / "artifact-manifest.json"

    def write_manifest(self, files):
        self.manifest.write_text(json.dumps({"files": files}))

    def test_duplicate_symlink_alias_is_rejected(self):
        (self.root / "alias.txt").symlink_to(self.artifact.name)
        self.write_manifest({"artifact.txt": self.sha, "alias.txt": self.sha})
        with self.assertRaisesRegex(ValueError, "Duplicate manifest path"):
            check_manifest(self.manifest)

    def test_unknown_issue_selection_cannot_pass_an_empty_inventory(self):
        (self.root / "registry.json").write_text(json.dumps({"schema_version": 1, "issues": []}))
        with self.assertRaisesRegex(ValueError, "Unknown requested issues"):
            verify(self.root, ["eclipse-score/communication#1261"])

    def test_existing_and_native_manifest_formats_verify_the_same_bytes(self):
        for files in [
            {"artifact.txt": self.sha},
            {"artifact.txt": {"sha256": self.sha, "size_bytes": self.artifact.stat().st_size}},
            [{"path": "artifact.txt", "sha256": self.sha, "size": self.artifact.stat().st_size}],
        ]:
            with self.subTest(files=files):
                self.write_manifest(files)
                self.assertEqual(check_manifest(self.manifest), 1)
                self.artifact.write_bytes(b"X" + self.artifact.read_bytes()[1:])
                with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                    check_manifest(self.manifest)
                self.artifact.write_bytes(b"preserved native evidence\n")

    def test_native_manifest_size_is_checked_even_with_a_valid_digest(self):
        self.write_manifest([{"path": "artifact.txt", "sha256": self.sha, "size": 0}])
        with self.assertRaisesRegex(ValueError, "size mismatch"):
            check_manifest(self.manifest)

    def test_duplicate_native_paths_are_rejected_instead_of_overwritten(self):
        self.write_manifest([
            {"path": "artifact.txt", "sha256": self.sha},
            {"path": "./artifact.txt", "sha256": self.sha},
        ])
        with self.assertRaisesRegex(ValueError, "Duplicate manifest path"):
            check_manifest(self.manifest)

    def test_native_inventory_cannot_escape_the_record(self):
        self.write_manifest([{"path": "../artifact.txt", "sha256": self.sha}])
        with self.assertRaisesRegex(ValueError, "Unsafe artifact path"):
            check_manifest(self.manifest)

    def test_github_api_and_cli_wrappers_preserve_captured_observation(self):
        expected = {"url": "https://github.com/eclipse-score/communication/issues/781",
                    "issue_number": 781, "state": "open", "captured_on": "2026-10-07"}
        for issue in [
            {"html_url": expected["url"], "url": "https://api.github.com/repos/eclipse-score/communication/issues/781", "number": 781, "state": "open"},
            {"url": expected["url"], "number": 781, "state": "OPEN"},
        ]:
            self.assertEqual(snapshot_observation({"issue": issue, "retrieved_at": "2026-10-07T14:05:21+00:00"}), expected)
        self.assertEqual(snapshot_observation(expected), expected)

    def test_wrapped_snapshot_identity_is_still_checked_against_registry(self):
        snapshot = self.root / "snapshot.json"
        snapshot.write_text(json.dumps({"issue": {"html_url": "https://github.com/eclipse-score/communication/issues/490", "number": 490, "state": "open"}, "retrieved_at": "2026-10-07T14:05:21+00:00"}))
        (self.root / "registry.json").write_text(json.dumps({"schema_version": 1, "issues": [{
            "id": "eclipse-score/communication#781", "upstream_snapshot": "snapshot.json",
            "issue_url": "https://github.com/eclipse-score/communication/issues/781", "issue_number": 781,
        }]}))
        with self.assertRaisesRegex(ValueError, "Upstream issue identity mismatch"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
