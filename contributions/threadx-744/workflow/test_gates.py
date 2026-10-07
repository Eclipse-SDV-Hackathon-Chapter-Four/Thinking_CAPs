"""Checks for false-positive review acceptance and external readiness claims."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import driver


class ReviewGateTests(unittest.TestCase):
    def records(self, digest="current", technical="pass", process="pass"):
        return {
            "freeze.json": {"patch_sha256": "current"},
            "verification.json": {"patch_sha256": "current", "status": "pass"},
            "technical-review.json": {"patch_sha256": digest, "verdict": technical, "findings": []},
            "process-review.json": {"patch_sha256": "current", "verdict": process, "findings": []},
        }

    def check(self, records):
        with patch.object(driver, "read", side_effect=records.__getitem__), \
             patch.object(driver, "patch_hash", return_value="current"), \
             patch.object(driver, "write"):
            driver.review_gate()

    def test_stale_approval_cannot_accept_a_new_patch(self):
        with self.assertRaises(RuntimeError):
            self.check(self.records(digest="old-reviewed-patch"))

    def test_failed_independent_review_blocks_publication(self):
        with self.assertRaises(RuntimeError):
            self.check(self.records(process="fail"))

    def test_failed_measured_verification_overrides_agent_passes(self):
        records = self.records()
        records["verification.json"]["status"] = "fail"
        with self.assertRaises(RuntimeError):
            self.check(records)

    def test_blocking_finding_overrides_a_pass_verdict(self):
        records = self.records()
        records["technical-review.json"]["findings"] = [{"severity": "high", "message": "Stack pointer still truncates"}]
        with self.assertRaises(RuntimeError):
            self.check(records)


class ReadinessTests(unittest.TestCase):
    def test_pending_applicable_check_blocks_readiness(self):
        pr = {"headRefOid": "head", "statusCheckRollup": [
            {"name": name, "status": "COMPLETED", "conclusion": "SUCCESS"} for name in driver.REQUIRED] +
            [{"name": "Arm compiler", "status": "IN_PROGRESS", "conclusion": None}],
            "isDraft": False, "reviewDecision": "APPROVED", "baseRefName": "dev",
            "mergeable": "MERGEABLE", "mergeStateStatus": "CLEAN", "url": "https://github.com/example/pr/1"}
        records = {"publication.json": {"url": pr["url"], "head_sha": "head"},
                   "admission.json": {"required_checks": driver.REQUIRED}}
        writes = {}
        with patch.object(driver, "read", side_effect=records.__getitem__), \
             patch.object(driver, "gh_json", return_value=pr), patch.object(driver.time, "sleep"), \
             patch.object(driver, "write", side_effect=lambda name, value: writes.__setitem__(name, value)):
            driver.monitor()
        self.assertEqual(writes["readiness.json"]["status"], "blocked")
        self.assertTrue(any("still pending" in b for b in writes["readiness.json"]["blockers"]))

    def test_protected_branch_block_cannot_be_reported_ready(self):
        pr = {"headRefOid": "head", "statusCheckRollup": [
            {"name": name, "status": "COMPLETED", "conclusion": "SUCCESS"} for name in driver.REQUIRED],
            "isDraft": False, "reviewDecision": "APPROVED", "baseRefName": "dev",
            "mergeable": "MERGEABLE", "mergeStateStatus": "BLOCKED", "url": "https://github.com/example/pr/1"}
        records = {"publication.json": {"url": pr["url"], "head_sha": "head"},
                   "admission.json": {"required_checks": driver.REQUIRED}}
        writes = {}
        with patch.object(driver, "read", side_effect=records.__getitem__), \
             patch.object(driver, "gh_json", return_value=pr), \
             patch.object(driver, "write", side_effect=lambda name, value: writes.__setitem__(name, value)):
            driver.monitor()
        self.assertEqual(writes["readiness.json"]["status"], "blocked")
        self.assertTrue(any("protected-branch" in b for b in writes["readiness.json"]["blockers"]))

    def test_green_ci_does_not_replace_human_approval(self):
        pr = {"headRefOid": "head", "statusCheckRollup": [
            {"name": name, "status": "COMPLETED", "conclusion": "SUCCESS"} for name in driver.REQUIRED],
            "isDraft": True, "reviewDecision": "REVIEW_REQUIRED", "baseRefName": "dev",
            "mergeable": "MERGEABLE", "url": "https://github.com/example/pr/1"}
        records = {"publication.json": {"url": pr["url"], "head_sha": "head"},
                   "admission.json": {"required_checks": driver.REQUIRED}}
        writes = {}
        with patch.object(driver, "read", side_effect=records.__getitem__), \
             patch.object(driver, "gh_json", return_value=pr), \
             patch.object(driver, "write", side_effect=lambda name, value: writes.__setitem__(name, value)):
            driver.monitor()
        self.assertEqual(writes["readiness.json"]["status"], "blocked")
        self.assertGreaterEqual(len(writes["readiness.json"]["blockers"]), 2)

    def test_export_preserves_blocked_status(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "evidence"
            artifacts = Path(temp) / "artifacts"
            evidence.mkdir()
            (evidence / "readiness.json").write_text(json.dumps({"status": "blocked", "blockers": ["ECA pending"]}))
            with patch.object(driver, "EVIDENCE", evidence), patch.object(driver, "REPO_ARTIFACTS", artifacts):
                with self.assertRaises(RuntimeError):
                    driver.export()
            self.assertEqual(json.loads((artifacts / "readiness.json").read_text())["status"], "blocked")
            self.assertTrue((artifacts / "manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
