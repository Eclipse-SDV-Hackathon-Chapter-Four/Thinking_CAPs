"""Operational negative tests; these do not verify or accept native bug fixes."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('queue_collector', P / 'collector.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)

class Controls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=collector.R, prefix='control-test-')
        self.root = Path(self.temp.name)
        self.records, self.scratch = self.root / 'records', self.root / 'scratch'
        self.records.mkdir(); self.scratch.mkdir()
        self.d = self.records / '1236'; self.d.mkdir()
        self.tree = self.scratch / 'issue-1236'; self.tree.mkdir()
        (self.records / 'native-run-id').write_text('test-fixture-not-a-native-run')
        (self.records / 'node-ids.json').write_text(json.dumps({'1236_draft': 'draft'}))
        self.item = {'allowed_files': ['BUILD'], 'allowed_prefixes': []}
        self.patches = [patch.object(collector, 'P', self.records), patch.object(collector, 'R', self.scratch),
                        patch.object(collector, 'state_update')]
        for p in self.patches: p.start()
    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        self.temp.cleanup()
    def apply_response(self, files, rationale='fixture'):
        raw = json.dumps({'files': files, 'rationale': rationale})
        with patch.object(collector, 'api', return_value={'stages': {'draft@1': {'response': raw}}}):
            collector.apply(1236, self.d, self.item)
    def test_path_escape_refused_before_any_write(self):
        with self.assertRaises(ValueError): self.apply_response([{'path':'../escape','content':'bad'}])
        self.assertFalse((self.scratch / 'escape').exists())
    def test_whitelist_refused_before_any_write(self):
        with self.assertRaises(ValueError): self.apply_response([{'path':'MODULE.bazel','content':'bad'}])
        self.assertFalse((self.tree / 'MODULE.bazel').exists())
    def test_all_entries_validated_before_write(self):
        with self.assertRaises(ValueError): self.apply_response([{'path':'BUILD','content':'first'}, {'path':'BUILD','content':'second'}])
        self.assertFalse((self.tree / 'BUILD').exists())
    def test_empty_draft_preserved_and_refused(self):
        with self.assertRaises(ValueError): self.apply_response([])
        self.assertTrue((self.d / 'draft-output.txt').exists())
    def test_symlink_refused(self):
        other = self.root / 'protected'; other.write_text('keep')
        (self.tree / 'BUILD').symlink_to(other)
        with self.assertRaises(ValueError): self.apply_response([{'path':'BUILD','content':'bad'}])
        self.assertEqual(other.read_text(), 'keep')
    def test_valid_patch_bound_to_source(self):
        self.apply_response([{'path':'BUILD','content':'fixture-content'}])
        self.assertEqual(json.loads((self.d / 'candidate-hashes.json').read_text()), {'BUILD': collector.sha(self.tree / 'BUILD')})
    def test_budget_exhaustion_and_duplicate_are_not_reset(self):
        baseline = self.scratch / 'baseline'; baseline.mkdir()
        (self.records / 'baseline-hashes.json').write_text('{}')
        ledger = self.records / 'budget-ledger.json'
        original = {'cap_usd_micros':10000000, 'reservations':{'other':9500000}, 'actual_provider_cost_usd_micros':None}
        ledger.write_text(json.dumps(original))
        with self.assertRaises(ValueError): collector.admit(1236,self.d,self.item)
        self.assertEqual(json.loads(ledger.read_text()), original)
        original['reservations'] = {'1236':2359296}
        ledger.write_text(json.dumps(original))
        with self.assertRaises(ValueError): collector.admit(1236,self.d,self.item)
        self.assertEqual(json.loads(ledger.read_text()), original)

if __name__ == '__main__':
    unittest.main()
