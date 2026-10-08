import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "audit", Path(__file__).parents[1] / "scripts/audit_baseline.py"
)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class AuditTests(unittest.TestCase):
    def test_incomplete_checks_never_pass(self):
        for status, code in (("blocked", 2), ("failed", 1), ("skipped", 2)):
            self.assertEqual(audit.exit_code([{"status": "passed"}, {"status": status}]), code)

    def test_failed_dominates_blocked(self):
        self.assertEqual(audit.exit_code([{"status": "blocked"}, {"status": "failed"}]), 1)

    def test_missing_checkout_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            record = audit.repository(Path(directory) / "missing")
        self.assertEqual(record["status"], "blocked")
        self.assertNotIn("revision", record)

    def test_empty_checks_do_not_pass(self):
        self.assertEqual(audit.exit_code([]), 2)
