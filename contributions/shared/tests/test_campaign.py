"""Meaningful verdict regressions: no false success from child exit/status or cleanup."""
import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'scripts/run_campaign.py'
spec = importlib.util.spec_from_file_location('campaign', MODULE)
campaign = importlib.util.module_from_spec(spec)
spec.loader.exec_module(campaign)


class VerdictTests(unittest.TestCase):
    definitions = [{'id': 'T01', 'name': 'Nominal', 'checks': ['actual-state']}]

    def test_exit_zero_does_not_hide_failed_check(self):
        child = {'status': 'passed', 'checks': [{'id': 'actual-state', 'status': 'failed'}]}
        rows = campaign.assess('core', 0, child, self.definitions)
        self.assertEqual(campaign.exit_for(rows), 1)

    def test_missing_assertion_is_failed_not_skipped(self):
        rows = campaign.assess('core', 0, {'status': 'passed', 'checks': []}, self.definitions)
        self.assertEqual(campaign.exit_for(rows), 1)

    def test_nonzero_child_cannot_pass_with_passed_checks(self):
        child = {'status': 'passed', 'checks': [{'id': 'actual-state', 'status': 'passed'}]}
        self.assertEqual(campaign.exit_for(campaign.assess('core', 1, child, self.definitions)), 1)

    def test_cleanup_failure_cannot_be_expected_injection_success(self):
        checks = [{'id': 'execution', 'status': 'failed', 'reason': 'deliberate failure after tunnel disturbance'},
                  {'id': 'restore-tunnel', 'status': 'failed'},
                  {'id': 'restore-private-directory-owner', 'status': 'passed'}]
        checks += [{'id': 'cleanup-app-' + str(i), 'status': 'passed'} for i in range(3)]
        checks += [{'id': 'stop-capture-' + str(i), 'status': 'passed'} for i in range(4)]
        checks += [{'id': 'read-capture-' + str(i), 'status': 'passed'} for i in range(4)]
        self.assertEqual(campaign.exit_for(campaign.assess('cleanup-failure', 1, {'status':'failed','checks':checks}, [])), 1)
        checks[1]['status'] = 'passed'
        self.assertEqual(campaign.exit_for(campaign.assess('cleanup-failure', 1, {'status':'failed','checks':checks}, [])), 0)

    def test_blocked_and_skipped_do_not_count_as_pass(self):
        rows = [{'id':'T01','status':'blocked','reason':'missing environment'}, {'id':'T09','status':'skipped'}]
        self.assertEqual(campaign.exit_for(rows), 2)
        xml = campaign.junit(rows)
        self.assertEqual(xml.get('failures'), '0')
        self.assertEqual(xml.get('skipped'), '2')
        self.assertEqual(len(xml.findall('testcase/skipped')), 2)

    def test_failed_precedence_over_blocked(self):
        self.assertEqual(campaign.exit_for([{'status':'blocked'}, {'status':'failed'}]), 1)

    def test_carla_readiness_blocked_does_not_pass_selected_campaign(self):
        checks = [{'id':'execution', 'status':'blocked', 'reason':'CARLA prerequisite unavailable: readiness timeout'},
                  {'id':'cleanup-owned-carla', 'status':'passed'}]
        rows = campaign.assess('carla', 2, {'status':'blocked', 'checks':checks}, self.definitions)
        self.assertEqual(campaign.exit_for(rows), 2)
        self.assertFalse(any(row['id'] == 'T01' and row['status'] == 'passed' for row in rows))
        checks.append({'id':'restore-tunnel', 'status':'failed'})
        self.assertEqual(campaign.exit_for(campaign.assess('carla', 2, {'status':'blocked', 'checks':checks}, [])), 1)

    def test_carla_requires_native_actuation_correlation(self):
        checks = [{'id': key, 'status': 'passed'} for key in
                  ('real-carla-moving-actor', 'real-carla-return-actuation', 'cleanup-owned-carla')]
        rows = campaign.assess('carla', 0, {'status': 'passed', 'checks': checks}, [])
        self.assertEqual(campaign.exit_for(rows), 1)
        carla = next(row for row in rows if row['id'] == 'CARLA')
        self.assertIn('real-carla-native-actuation-correlation', carla['missing_or_failed_checks'])


if __name__ == '__main__':
    unittest.main()
