"""Failure and ownership boundaries for the local dashboard; no vehicle mocks as E2E."""
import concurrent.futures
import hashlib
import fcntl
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import time
import subprocess
import unittest
import threading
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from integration.dashboard.service import Artifacts, Coordinator, cleanup_verdict, Diagnosis, Dashboard, server


def wait_for(predicate, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(.02)
    raise AssertionError('bounded wait exceeded')


class DashboardBoundaries(unittest.TestCase):
    def test_artifact_tamper_missing_symlink_and_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            content = b'{"status":"passed"}\n'
            (root / 'results.json').write_bytes(content)
            hashes = {'results.json': hashlib.sha256(content).hexdigest(), 'manifest.json': '0' * 64}
            store = Artifacts(root, hashes)
            self.assertEqual(store.read('results.json'), content)
            self.assertEqual(store.inventory()['manifest.json']['integrity'], 'missing')
            (root / 'results.json').write_bytes(b'tampered')
            self.assertEqual(store.inventory()['results.json']['integrity'], 'mismatch')
            with self.assertRaises(ValueError): store.read('results.json')
            with self.assertRaises(ValueError): store.read('../passwd')
            (root / 'results.json').unlink()
            (root / 'results.json').symlink_to('/etc/passwd')
            with self.assertRaises(ValueError): store.read('results.json')
            (root / 'private.key').write_text('never served')
            with self.assertRaises(ValueError): store.read('private.key')

    def test_cleanup_requires_complete_native_contract(self):
        checks = [{'id': key, 'status': 'passed'} for key in (
            'restore-tunnel', 'restore-private-directory-owner',
            'cleanup-sdv-test-score', 'cleanup-sdv-test-bridge', 'cleanup-sdv-test-diag',
            'stop-capture-a-1', 'stop-capture-a-2', 'stop-capture-b-1', 'stop-capture-b-2',
            'read-capture-a-dut', 'read-capture-a-gre', 'read-capture-b-dut', 'read-capture-b-gre')]
        self.assertEqual(cleanup_verdict({'checks': checks})['status'], 'passed')
        self.assertEqual(cleanup_verdict({'checks': checks[:-1]})['status'], 'unknown')
        checks[0]['status'] = 'failed'
        self.assertEqual(cleanup_verdict({'checks': checks})['status'], 'failed')
        self.assertEqual(cleanup_verdict(None)['status'], 'unknown')

    def test_early_cancellation_checks_actual_application_inventory(self):
        apps = ['cleanup-sdv-net-test-bridge', 'cleanup-sdv-net-test-diag']
        identifiers = ['restore-tunnel', 'restore-private-directory-owner', *apps,
                       'stop-capture-a-1', 'stop-capture-a-2', 'stop-capture-b-1', 'stop-capture-b-2',
                       'read-capture-a-dut', 'read-capture-a-gre', 'read-capture-b-dut', 'read-capture-b-gre']
        native = {'checks': [{'id': key, 'status': 'passed'} for key in identifiers],
                  'cleanup_contract': {'schema_version': 1, 'application_checks': apps}}
        self.assertEqual(cleanup_verdict(native)['status'], 'passed')
        native['checks'] = [check for check in native['checks'] if check['id'] != apps[0]]
        self.assertEqual(cleanup_verdict(native)['status'], 'unknown')

    def test_cleanup_inventory_cannot_hide_missing_or_unlisted_applications(self):
        apps = ['cleanup-sdv-net-test-bridge', 'cleanup-sdv-net-test-diag']
        identifiers = ['restore-tunnel', 'restore-private-directory-owner', *apps,
                       'stop-capture-a-1', 'stop-capture-a-2', 'stop-capture-b-1', 'stop-capture-b-2',
                       'read-capture-a-dut', 'read-capture-a-gre', 'read-capture-b-dut', 'read-capture-b-gre']
        for inventory in ([], apps[:1], apps + ['cleanup-sdv-net-test-score'], apps + apps,
                          [['unhashable']], ['arbitrary-check']):
            with self.subTest(inventory=inventory):
                native = {'checks': [{'id': key, 'status': 'passed'} for key in identifiers],
                          'cleanup_contract': {'schema_version': 1, 'application_checks': inventory}}
                self.assertEqual(cleanup_verdict(native)['status'], 'unknown')

    def test_concurrent_starts_cancel_and_unproven_cleanup_inhibits(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / 'inputs.json'; config.write_text('{}')
            fixture = root / 'fixture.py'
            fixture.write_text('import signal,time,sys\nsignal.signal(signal.SIGTERM,lambda s,f:sys.exit(1))\nprint("owned test fixture",flush=True)\ntime.sleep(30)\n')
            manager = Coordinator(root / 'state', config, sys.executable,
                                  command_factory=lambda r: [sys.executable, str(fixture)])
            try:
                def start():
                    try: return manager.start('core')['id']
                    except RuntimeError: return None
                with concurrent.futures.ThreadPoolExecutor(2) as pool:
                    answers = list(pool.map(lambda _: start(), range(2)))
                self.assertEqual(sum(a is not None for a in answers), 1)
                identity = next(a for a in answers if a)
                wait_for(lambda: manager.snapshot()['runs'][identity].get('pid'))
                time.sleep(.15)
                manager.cancel(identity)
                final = wait_for(lambda: manager.snapshot()['runs'][identity]
                                 if manager.snapshot()['runs'][identity]['state'] == 'cancelled' else None)
                self.assertEqual(final['cleanup']['status'], 'unknown')
                self.assertNotEqual((final.get('results') or {}).get('status'), 'passed')
                with self.assertRaises(RuntimeError): manager.start('core')
            finally: manager.close()
            resumed = Coordinator(root / 'state', config, sys.executable)
            try:
                self.assertEqual(resumed.snapshot()['runs'][identity]['state'], 'cancelled')
                with self.assertRaises(RuntimeError): resumed.start('carla')
            finally: resumed.close()

    def test_restart_unfinished_run_is_unknown_and_does_not_signal_pid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); state = root / 'state'; state.mkdir()
            identity = 'a' * 32
            (state / 'ledger.json').write_text(json.dumps({'active': identity, 'runs': {
                identity: {'id': identity, 'state': 'running', 'pid': 1, 'pid_identity': 'wrong',
                           'scenario': 'core', 'output': str(state / 'runs' / identity)}}}))
            manager = Coordinator(state, root / 'none.json', sys.executable)
            try:
                self.assertEqual(manager.snapshot()['runs'][identity]['state'], 'unknown')
                with self.assertRaises(RuntimeError): manager.start('core')
            finally: manager.close()

    def test_invalid_ledger_never_discards_possible_active_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); (root/'ledger.json').write_text('{broken')
            with self.assertRaises(RuntimeError): Coordinator(root, root/'none.json', sys.executable)
            self.assertEqual((root/'ledger.json').read_text(), '{broken')

    def test_cli_campaign_cannot_bypass_bench_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'bench';state.mkdir()
            inputs=root/'inputs.json';inputs.write_text(json.dumps({'state':str(state),'schema_version':1}))
            with (state/'campaign.lock').open('a') as lease:
                fcntl.flock(lease,fcntl.LOCK_EX|fcntl.LOCK_NB)
                identity='b'*32
                process=subprocess.run([sys.executable,str(ROOT/'scripts/run_campaign.py'),
                    '--config',str(inputs),'--output',str(root/'blocked'),'--run-id',identity],capture_output=True,timeout=5)
            self.assertEqual(process.returncode,2)
            result=json.loads((root/'blocked/results.json').read_text())
            self.assertEqual(result['run_id'],identity)
            self.assertEqual(result['status'],'blocked')
            self.assertIn('another campaign owns',result['scenarios'][0]['reason'])

    def test_unavailable_interpreter_blocks_without_claiming_runner_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);manager=Coordinator(root/'state',root/'inputs.json','/nonexistent/sdv-python')
            try:
                identity=manager.start('core')['id']
                final=wait_for(lambda:manager.snapshot()['runs'][identity] if manager.snapshot()['runs'][identity]['state']=='blocked' else None)
                self.assertIsNone(final['results'])
                self.assertEqual(final['cleanup']['status'],'not_required')
                self.assertIsNone(manager.snapshot()['active'])
            finally:manager.close()

    def test_queued_cancellation_never_launches_runner(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);entered=threading.Event();release=threading.Event()
            def factory(record):
                entered.set();release.wait(timeout=3)
                return [sys.executable,'-c','raise RuntimeError("must never launch")']
            manager=Coordinator(root/'state',root/'inputs.json',sys.executable,command_factory=factory)
            try:
                identity=manager.start('core')['id'];self.assertTrue(entered.wait(timeout=2))
                manager.cancel(identity);release.set()
                final=wait_for(lambda:manager.snapshot()['runs'][identity] if manager.snapshot()['runs'][identity]['state']=='cancelled' else None)
                self.assertNotIn('pid',final)
                self.assertEqual(final['cleanup']['status'],'not_required')
                self.assertIsNone(manager.snapshot()['active'])
            finally:release.set();manager.close()

    def test_diagnostic_outage_retains_only_last_observed_truth(self):
        diagnostic = Diagnosis('http://127.0.0.1:1/sovd')
        diagnostic.observation.success({'freshness_state': 'fresh', 'receiver_state': 'available',
                                       'observation': {'source_session': 'fixture-A'}}, 'fixture-uri')
        diagnostic.observation.failure('deliberate outage')
        view = diagnostic.snapshot()['observation']
        self.assertEqual(view['availability'], 'unavailable')
        self.assertEqual(view['value']['freshness_state'], 'fresh')
        self.assertTrue(view['last_observed_only'])
        self.assertIsNotNone(view['acquired_utc'])

    def test_discovery_cannot_redirect_to_other_origin(self):
        diagnostic = Diagnosis('http://127.0.0.1:1/sovd')
        with self.assertRaises(ValueError): diagnostic.fetch('http://example.com/secret')
        with self.assertRaises(ValueError): diagnostic.fetch('http://127.0.0.1:1/private')

    def test_http_boundaries_and_actual_runner_blocked_result(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); inputs = root / 'inputs.json'; inputs.write_text('{}')
            app = Dashboard({'state_dir': str(root / 'private'), 'campaign_config': str(inputs),
                             'diagnostic_base': 'http://127.0.0.1:1/sovd'})
            httpd = server(app, 0)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True); thread.start()
            base = 'http://127.0.0.1:' + str(httpd.server_port)
            try:
                state = json.load(urllib.request.urlopen(base + '/api/state', timeout=2))
                for headers in ({}, {'Origin': 'http://example.com', 'X-SDV-Token': state['token']},
                                {'Origin': base, 'X-SDV-Token': 'wrong'}, {'Host': 'example.com'}):
                    req = urllib.request.Request(base + '/api/runs', data=b'{"scenario":"core"}', headers=headers)
                    with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(req, timeout=2)
                    self.assertEqual(error.exception.code, 403)
                headers = {'Origin': base, 'X-SDV-Token': state['token'], 'Content-Type': 'application/json'}
                req = urllib.request.Request(base + '/api/runs', data=b'{"scenario":"arbitrary-command"}', headers=headers)
                with self.assertRaises(urllib.error.HTTPError) as error: urllib.request.urlopen(req, timeout=2)
                self.assertEqual(error.exception.code, 400)
                req = urllib.request.Request(base + '/api/runs', data=b'{"scenario":"core"}', headers=headers)
                record = json.load(urllib.request.urlopen(req, timeout=2))
                result = wait_for(lambda: app.manager.snapshot()['runs'][record['id']]
                                  if app.manager.snapshot()['runs'][record['id']]['state'] == 'blocked' else None)
                self.assertEqual(result['results']['run_id'], record['id'])
                self.assertEqual(result['cleanup']['status'], 'not_required')
                self.assertIsNone(app.manager.snapshot()['active'])
                detail = json.load(urllib.request.urlopen(base + '/api/runs/' + record['id'], timeout=2))
                self.assertEqual(detail['results']['status'], 'blocked')
                original = urllib.request.urlopen(base + '/api/runs/' + record['id'] + '/artifacts/results.json').read()
                self.assertEqual(original, (Path(result['output']) / 'results.json').read_bytes())
                (Path(result['output']) / 'results.json').write_text('{"status":"passed"}')
                changed = json.load(urllib.request.urlopen(base + '/api/runs/' + record['id'], timeout=2))
                self.assertEqual(changed['results']['status'], 'blocked')
                self.assertEqual(changed['artifacts']['results.json']['integrity'], 'mismatch')
                with self.assertRaises(urllib.error.HTTPError) as error:
                    urllib.request.urlopen(base + '/api/runs/' + record['id'] + '/artifacts/results.json', timeout=2)
                self.assertEqual(error.exception.code, 409)
            finally:
                httpd.shutdown(); httpd.server_close(); thread.join(timeout=2); app.close()


if __name__ == '__main__': unittest.main()
