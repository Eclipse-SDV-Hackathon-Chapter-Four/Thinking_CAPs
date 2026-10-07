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
import json
import os
import tempfile
import unittest

import codeql_lint


class NormalizePlaceholderLocationsTest(unittest.TestCase):
    def test_removes_placeholder_uri_with_index(self):
        sarif = {
            "runs": [
                {
                    "artifacts": [
                        {"location": {"uri": "file:/", "index": 101}},
                    ],
                    "results": [
                        {
                            "relatedLocations": [
                                {
                                    "physicalLocation": {"artifactLocation": {"uri": "file:/"}},
                                    "message": {"text": "Result"},
                                }
                            ]
                        }
                    ],
                }
            ]
        }
        codeql_lint._normalize_placeholder_artifact_locations(sarif)
        artifact = sarif["runs"][0]["artifacts"][0]
        self.assertNotIn("location", artifact)
        self.assertEqual(artifact["properties"]["score.previousArtifactIndex"], 101)
        related = sarif["runs"][0]["results"][0]["relatedLocations"][0]
        self.assertNotIn("physicalLocation", related)
        self.assertEqual(related["message"]["text"], "Result")

    def test_preserves_valid_uri(self):
        sarif = {
            "runs": [
                {
                    "results": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {
                                    "uri": "score/mw/com/impl/foo.cpp",
                                }
                            }
                        }
                    ]
                }
            ]
        }
        codeql_lint._normalize_placeholder_artifact_locations(sarif)
        artifact_location = sarif["runs"][0]["results"][0]["physicalLocation"]["artifactLocation"]
        self.assertEqual(artifact_location["uri"], "score/mw/com/impl/foo.cpp")

    def test_normalize_sarif_placeholder_locations_writes_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            sarif_path = os.path.join(tmpdir, "out.sarif")
            sarif = {"runs": [{"results": [{"physicalLocation": {"artifactLocation": {"uri": "file:/"}}}]}]}
            with open(sarif_path, "w") as f:
                json.dump(sarif, f)
            codeql_lint.normalize_sarif_placeholder_locations(sarif_path)
            with open(sarif_path, "r") as f:
                normalized = json.load(f)
            result = normalized["runs"][0]["results"][0]
            self.assertNotIn("physicalLocation", result)
            self.assertTrue(result["properties"]["score.artifactLocationUnavailable"])


if __name__ == "__main__":
    unittest.main()
