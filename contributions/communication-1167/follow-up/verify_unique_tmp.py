"""No-model Fabro verification with explicitly inherited build-storage paths."""
from pathlib import Path
import importlib.util
import json
import sys

P = Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167')
V = P / 'follow-up/final-verification-run'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


closed = load('closed_supervisor', P / 'supervisor/run_stage.py')
base = load('verification_collectors', P / 'supervisor/collector.py')
base.HERE = V


def guard():
    closed.guard()
    for relative, expected in json.loads((V / 'frozen-inputs.json').read_text()).items():
        if base.sha(P / relative) != expected:
            raise ValueError('Follow-up input changed: ' + relative)


base.guard = guard
original_measure = base.measure


def measure(command, label, cwd, env, timeout):
    if label in {'focused', 'test-all'}:
        inherited = base.build_environment(base.SCRATCH)
        inherited['HOME'] = str(base.SCRATCH / 'container-home')
        # Bazel must retain its unique per-test directory; it is already on bound storage.
        inherited.pop('TEST_TMPDIR', None)
        command = command + ['--test_env=' + key + '=' + value for key, value in sorted(inherited.items())]
    return original_measure(command, label, cwd, env, timeout)


base.measure = measure


def main():
    stage = sys.argv[1]
    guard()
    identifier = (V / 'current-native-run-id').read_text().strip()
    try:
        if stage == 'verify':
            base.verify({'run_id': identifier})
        elif stage == 'export':
            base.export({'run_id': identifier})
        else:
            raise ValueError('Unsupported deterministic stage')
    except Exception as error:
        base.write(stage + '-failure.json', {'reason': str(error), 'run_id': identifier})
        print(json.dumps({'status': 'failed', 'reason': str(error)}))
        return 1
    print(json.dumps({'status': 'completed', 'run_id': identifier}))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
