import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


SPEC = importlib.util.spec_from_file_location(
    "run_autoverse", Path(__file__).resolve().parents[1] / "run_autoverse.py"
)
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


class LauncherTests(unittest.TestCase):
    def test_component_overrides_do_not_mix_android_and_bridge(self):
        with mock.patch.dict(runner.os.environ, {
                'AUTOVERSE_BRIDGE_CONTAINER': 'audit-bridge', 'AUTOVERSE_BRIDGE_IMAGE': 'audit-bridge-img',
                'AUTOVERSE_ANDROID_CONTAINER': 'audit-android', 'AUTOVERSE_ANDROID_IMAGE': 'audit-android-img',
                'COMPOSE_PROJECT_NAME': 'audit-score', 'SCORE_FOR': 'X-Verse'}):
            steps = runner.build_steps(vcu_zenoh=True)
        bridge = next(s for s in steps if 'SOME-IP bridge' in s['name'])
        android = next(s for s in steps if 'ANDROID' in s['name'])
        score = next(s for s in steps if 'Module S-CORE' in s['name'])
        self.assertEqual(bridge['containers'], ['audit-bridge'])
        self.assertEqual(android['containers'], ['audit-android'])
        self.assertIn('CONTAINER=audit-bridge', bridge['cmd'])
        self.assertIn('CONTAINER=audit-android', android['stp'])
        self.assertEqual(score['containers'], ['audit-score-adas_score-1'])

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        logs = self.root / "logs"
        logs.mkdir()
        patch = mock.patch.object(runner, "LOG_DIR", logs)
        patch.start()
        self.addCleanup(patch.stop)

    def register_temporary_cleanup(self, callback):
        if getattr(callback, "__name__", "") == "cleanup":
            self.addCleanup(callback)

    def test_stop_waits_for_shutdown_to_finish(self):
        marker = self.root / "stopped"
        command = [sys.executable, "-c",
                   "import pathlib, sys, time; time.sleep(0.2); "
                   "pathlib.Path(sys.argv[1]).write_text('stopped')", str(marker)]
        with contextlib.redirect_stdout(io.StringIO()):
            process, _, _ = runner.stop_process("delayed stop", str(self.root), command)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(marker.read_text(), "stopped")

    def test_failed_stop_is_reported(self):
        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "Failed to stop.*exit 7"):
                runner.stop_process("failed stop", str(self.root),
                                    [sys.executable, "-c", "raise SystemExit(7)"])

    def test_stop_timeout_terminates_command(self):
        with mock.patch.object(runner, "CONTROL_STOP_TIMEOUT", 0.05), \
                contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, "Timed out stopping"):
                runner.stop_process("hung stop", str(self.root),
                                    [sys.executable, "-c", "import time; time.sleep(30)"])

    def test_containers_must_actually_be_running(self):
        for status, running, paused, restarting in (
                ("exited", False, False, False),
                ("paused", True, True, False),
                ("restarting", True, False, True)):
            with self.subTest(status=status):
                state = {"Status": status, "Running": running, "Paused": paused,
                         "Restarting": restarting, "ExitCode": 137, "OOMKilled": False}
                result = subprocess.CompletedProcess([], 0, json.dumps(state), "")
                with mock.patch.object(runner.subprocess, "run", return_value=result):
                    with self.assertRaisesRegex(RuntimeError, "bridge-e2e is " + status):
                        runner.check_containers(["bridge-e2e"])

    def test_missing_container_is_reported(self):
        result = subprocess.CompletedProcess([], 1, "", "No such container: bridge-e2e")
        with mock.patch.object(runner.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(RuntimeError, "No such container"):
                runner.check_containers(["bridge-e2e"])

    def test_running_containers_are_accepted(self):
        state = {"Status": "running", "Running": True, "Paused": False,
                 "Restarting": False, "ExitCode": 0, "OOMKilled": False}
        result = subprocess.CompletedProcess([], 0, json.dumps(state), "")
        with mock.patch.object(runner.subprocess, "run", return_value=result):
            runner.check_containers(["bridge-e2e"])

    def test_duplicate_launcher_exits_before_cleanup(self):
        with runner.acquire_runner_lock(), \
                mock.patch.object(sys, "argv", ["run_autoverse.py"]), \
                mock.patch.object(runner, "select_python", create=True) as select_python, \
                mock.patch.object(runner, "kill_carla_processes") as cleanup, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(runner.main(), 1)
            select_python.assert_not_called()
            cleanup.assert_not_called()
        with runner.acquire_runner_lock():
            pass

    def test_main_waits_before_start_and_supervises_detached_container(self):
        marker = self.root / "stopped"
        stop = [sys.executable, "-c",
                "import pathlib, sys, time; time.sleep(0.2); "
                "pathlib.Path(sys.argv[1]).touch()", str(marker)]
        start = [sys.executable, "-c",
                 "import pathlib, sys; raise SystemExit(0 if "
                 "pathlib.Path(sys.argv[1]).exists() else 7)", str(marker)]
        step = {"name": "test container", "cwd": str(self.root), "stp": stop,
                "cmd": start, "kill_patterns": [], "containers": ["test-container"]}
        lock = runner.acquire_runner_lock()
        self.addCleanup(lock.close)
        patches = (
            mock.patch.object(sys, "argv", ["run_autoverse.py"]),
            mock.patch.object(runner, "acquire_runner_lock", return_value=lock),
            mock.patch.object(runner, "select_python", return_value=sys.executable, create=True),
            mock.patch.object(runner, "build_steps", return_value=[step]),
            mock.patch.object(runner, "kill_carla_processes"),
            mock.patch.object(runner, "detect_second_monitor", return_value=None),
            mock.patch.object(runner.signal, "signal"),
            mock.patch.object(runner.atexit, "register",
                              side_effect=self.register_temporary_cleanup),
            mock.patch.object(runner, "shutdown_all"),
            mock.patch.object(runner, "children", []),
            mock.patch.object(runner, "CONTROL_STEPS", []),
            mock.patch.object(runner, "check_containers",
                              side_effect=[None, RuntimeError("test-container stopped")]),
            contextlib.redirect_stdout(io.StringIO()),
        )
        with contextlib.ExitStack() as stack:
            for patch in patches:
                stack.enter_context(patch)
            self.assertEqual(runner.main(), 1)
            self.assertTrue(marker.exists())
            self.assertEqual(runner.check_containers.call_count, 2)
            self.assertEqual(runner.children, [])
            runner.shutdown_all.assert_called_once()

    def test_failed_stop_prevents_start(self):
        step = {"name": "test container", "cwd": str(self.root),
                "stp": [sys.executable, "-c", "raise SystemExit(7)"],
                "cmd": [sys.executable, "-c", "pass"], "kill_patterns": [],
                "containers": ["test-container"]}
        lock = runner.acquire_runner_lock()
        self.addCleanup(lock.close)
        with contextlib.ExitStack() as stack:
            for patch in (
                    mock.patch.object(sys, "argv", ["run_autoverse.py"]),
                    mock.patch.object(runner, "acquire_runner_lock", return_value=lock),
                    mock.patch.object(runner, "select_python", return_value=sys.executable, create=True),
                    mock.patch.object(runner, "build_steps", return_value=[step]),
                    mock.patch.object(runner, "kill_carla_processes"),
                    mock.patch.object(runner.signal, "signal"),
                    mock.patch.object(runner.atexit, "register",
                              side_effect=self.register_temporary_cleanup),
                    mock.patch.object(runner, "CONTROL_STEPS", []),
                    mock.patch.object(runner, "start_process"),
                    contextlib.redirect_stdout(io.StringIO())):
                stack.enter_context(patch)
            self.assertEqual(runner.main(), 1)
            runner.start_process.assert_not_called()


if __name__ == "__main__":
    unittest.main()
