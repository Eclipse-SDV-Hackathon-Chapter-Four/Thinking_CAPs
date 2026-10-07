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
            self._create_database_with_sources(
                tmpdir, ["score/mw/com/impl/plumbing/proxy_binding_factory_impl.cpp"]
            )
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


if __name__ == "__main__":
    unittest.main()
