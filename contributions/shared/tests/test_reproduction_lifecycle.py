"""Process-boundary regressions; no Docker, native compiler or vehicle is simulated as passing."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import tempfile
import time
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/reproduce_core.py'
spec = importlib.util.spec_from_file_location('reproduction_lifecycle', SCRIPT)
reproduction = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reproduction)


def process_terminated(pid):
    state = Path('/proc') / str(pid) / 'stat'
    return not state.exists() or state.read_text().split()[2] in ('Z', 'X')


class ReproductionLifecycleTests(unittest.TestCase):
    def test_timeout_stops_child_and_preserves_partial_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'command.txt'
            program = ('import subprocess,time;'
                       'print(subprocess.Popen(["/usr/bin/python3","-c","import time;time.sleep(40)"]).pid,flush=True);'
                       'time.sleep(40)')
            with self.assertRaises(subprocess.TimeoutExpired):
                reproduction.run_owned_command(['/usr/bin/python3', '-c', program], .3, output)
            self.assertTrue(process_terminated(int(output.read_text().strip())))

    def test_invalid_config_leaves_failure_manifest_without_build(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'config.json'
            config.write_text('[]')
            result = subprocess.run(['/usr/bin/python3', str(SCRIPT), '--config', str(config),
                                     '--state', str(root / 'state'), '--output', str(root / 'evidence')],
                                    capture_output=True, timeout=10)
            manifest = json.loads((root / 'evidence/manifest.json').read_text())
            self.assertEqual(result.returncode, 1)
            self.assertEqual(manifest['status'], 'failed')
            self.assertEqual(manifest['reason'], 'reproduction config must be a JSON object')
            self.assertEqual(manifest['build_container_cleanup']['status'], 'skipped')
            self.assertEqual(manifest['commands'], [])

    def test_signals_record_failure_and_stop_owned_waiting_command(self):
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signal=signal.Signals(signum).name), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                marker = root / 'compiler.pid'
                tools = root / 'bin'
                tools.mkdir()
                compiler = tools / 'rustc'
                compiler.write_text('#!/usr/bin/python3\nfrom pathlib import Path\nimport os,time\n'
                                    'Path(' + repr(str(marker)) + ').write_text(str(os.getpid()))\n'
                                    'print("controlled wait fixture",flush=True)\ntime.sleep(40)\n')
                compiler.chmod(0o700)
                config = root / 'config.json'
                config.write_text('{}')
                environment = dict(os.environ)
                environment['PATH'] = str(tools) + os.pathsep + environment['PATH']
                process = subprocess.Popen(['/usr/bin/python3', str(SCRIPT), '--config', str(config),
                                            '--state', str(root / 'state'), '--output', str(root / 'evidence')],
                                           env=environment, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           start_new_session=True)
                try:
                    deadline = time.monotonic() + 10
                    while not marker.exists():
                        if process.poll() is not None or time.monotonic() > deadline:
                            self.fail('helper failed to reach the controlled command boundary')
                        time.sleep(.02)
                    os.kill(process.pid, signum)
                    process.communicate(timeout=10)
                    manifest = json.loads((root / 'evidence/manifest.json').read_text())
                    self.assertEqual(process.returncode, 128 + signum)
                    self.assertEqual(manifest['status'], 'failed')
                    self.assertEqual(manifest['interrupted_signal'], signal.Signals(signum).name)
                    self.assertFalse(manifest['independent_person_reproduced'])
                    self.assertTrue(process_terminated(int(marker.read_text())))
                    self.assertIn('controlled wait fixture', (root / 'evidence/command-02.txt').read_text())
                finally:
                    if process.poll() is None:
                        os.killpg(process.pid, signal.SIGKILL)
                        process.communicate(timeout=5)
                    if marker.exists():
                        try:
                            os.killpg(int(marker.read_text()), signal.SIGKILL)
                        except ProcessLookupError:
                            pass


if __name__ == '__main__':
    unittest.main()
