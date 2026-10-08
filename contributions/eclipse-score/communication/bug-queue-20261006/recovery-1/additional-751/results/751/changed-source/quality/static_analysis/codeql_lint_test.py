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
import os
import tempfile
import unittest
import zipfile

import codeql_lint


class AuditDatabaseSourceCoverageTest(unittest.TestCase):
    def _create_database_with_sources(self, database_path, sources):
        src_zip = os.path.join(database_path, "src.zip")
        with zipfile.ZipFile(src_zip, "w") as archive:
            for source in sources:
                archive.writestr(source, "// dummy source\n")

    def test_audit_passes_when_expected_source_is_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_database_with_sources(tmpdir, ["score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"])
            missing = codeql_lint.audit_database_source_coverage(
                tmpdir,
                tmpdir,
                ["score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"],
            )
            self.assertEqual(missing, [])

    def test_audit_reports_missing_expected_source(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            self._create_database_with_sources(tmpdir, ["score/mw/com/impl/other.cpp"])
            missing = codeql_lint.audit_database_source_coverage(
                tmpdir,
                tmpdir,
                ["score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"],
            )
            self.assertEqual(
                missing,
                ["score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"],
            )

    def test_audit_accepts_absolute_source_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            relative = "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"
            self._create_database_with_sources(tmpdir, [relative])
            absolute = os.path.join(tmpdir, relative)
            missing = codeql_lint.audit_database_source_coverage(
                tmpdir,
                tmpdir,
                [absolute],
            )
            self.assertEqual(missing, [])

    def test_audit_raises_when_src_zip_is_missing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(RuntimeError):
                codeql_lint.audit_database_source_coverage(
                    tmpdir,
                    tmpdir,
                    ["score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"],
                )

    def test_audit_accepts_absolute_archive_root_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            relative = "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"
            source_root = "/workspace"
            archive_entry = "workspace/" + relative
            self._create_database_with_sources(tmpdir, [archive_entry])
            missing = codeql_lint.audit_database_source_coverage(
                tmpdir,
                source_root,
                [relative],
            )
            self.assertEqual(missing, [])

    def test_audit_rejects_unrelated_absolute_archive_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            relative = "score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"
            source_root = "/workspace"
            archive_entry = "other/workspace/" + relative
            self._create_database_with_sources(tmpdir, [archive_entry])
            missing = codeql_lint.audit_database_source_coverage(
                tmpdir,
                source_root,
                [relative],
            )
            self.assertEqual(missing, [relative])


class ProductionTargetTest(unittest.TestCase):
    def test_production_target_patterns_preserve_requested_roots(self):
        patterns = codeql_lint._production_target_patterns("//score/message_passing //score/mw/com")
        self.assertEqual(
            patterns,
            [
                "//score/message_passing",
                "//score/mw/com",
            ],
        )

    def test_production_target_patterns_preserve_explicit_selectors(self):
        self.assertEqual(
            codeql_lint._production_target_patterns("//score/mw/com:com //score/message_passing/... //:api"),
            ["//score/mw/com:com", "//score/message_passing/...", "//:api"],
        )

    def test_parse_production_targets_deduplicates_configured_labels(self):
        self.assertEqual(
            codeql_lint._parse_production_targets("//score/mw/com:com (aaa)\n//score/mw/com:com (bbb)\n"),
            ["//score/mw/com:com"],
        )

    def test_production_target_patterns_reject_empty(self):
        with self.assertRaises(RuntimeError):
            codeql_lint._production_target_patterns("")

    def test_parse_production_targets_filters_external(self):
        labels = codeql_lint._parse_production_targets(
            "//score/mw/com/impl:foo\n@external//bar:baz\n//score/message_passing:msg\n"
        )
        self.assertEqual(
            labels,
            [
                "//score/message_passing:msg",
                "//score/mw/com/impl:foo",
            ],
        )


if __name__ == "__main__":
    unittest.main()
