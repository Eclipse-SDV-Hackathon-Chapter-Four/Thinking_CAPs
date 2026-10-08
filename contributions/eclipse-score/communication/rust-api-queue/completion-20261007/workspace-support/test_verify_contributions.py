# Copyright (c) 2026 Eclipse SDV Hackathon Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

"""Regression cases for contribution formats and rejected integrity failures."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

try:
    from .verify_contributions import check_manifest, snapshot_observation, verify
except ImportError:
    from verify_contributions import check_manifest, snapshot_observation, verify


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
