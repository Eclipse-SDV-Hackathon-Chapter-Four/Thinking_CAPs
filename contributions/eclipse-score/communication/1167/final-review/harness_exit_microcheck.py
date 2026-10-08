"""Isolated negative checks with the actual pinned wrapper and fake process exits."""
from pathlib import Path
import hashlib
import json
import runpy
import sys

ROOT = Path(__file__).resolve().parent
CONTRIBUTION = ROOT.parent
CONFIG = json.loads((ROOT / 'verification-run/configuration.json').read_text())
NATIVE_ITF = Path(CONFIG['scratch_root']) / 'bazel-output/87133c72bf7ae1cb42b36a2ab32613c6/external/score_itf+'
sys.path.insert(0, str(NATIVE_ITF))
from score.itf.core.process.wrapped_process import WrappedProcess

RELATIVE = 'score/mw/com/test/api_idempotency/integration_test/api_idempotency_test.py'
SUBJECTS = {
    'before': CONTRIBUTION / 'review-correction/verification-run/candidate' / RELATIVE,
    'after': ROOT / 'verification-run/candidate' / RELATIVE,
}


class FakeProcess:
    def __init__(self, exit_code):
        self.exit_code = exit_code

    def wait(self, timeout_s):
        assert timeout_s == 15
        return self.exit_code


class FakeTarget:
    def __init__(self, exit_code):
        self.exit_code = exit_code

    def execute_async(self, binary_path, args, cwd):
        assert binary_path == 'bin/main_api_idempotency'
        assert args == ['--service_instance_manifest', './etc/mw_com_config.json']
        assert cwd == '/opt/ApiIdempotencyApp'
        return FakeProcess(self.exit_code)

    def wrap_exec(self, *args, **kwargs):
        assert kwargs['wait_on_exit'] is True
        return WrappedProcess(self, *args, **kwargs)


def main():
    cases = []
    for subject, path in SUBJECTS.items():
        test = runpy.run_path(str(path))['test_api_idempotency']
        for exit_code in (0, 1, 137, 143):
            try:
                test(FakeTarget(exit_code))
                actual = 'pass'
            except (AssertionError, RuntimeError):
                actual = 'reject'
            expected = 'pass' if exit_code == 0 or (subject == 'before' and exit_code in (137, 143)) else 'reject'
            if actual != expected:
                raise AssertionError(f'{subject}: exit {exit_code}: {actual} != {expected}')
            cases.append({'subject': subject, 'exit_code': exit_code, 'outcome': actual, 'expected': expected})
    record = {
        'classification': 'isolated_fixture_microcheck_not_native_readiness_evidence',
        'actual_native_wrapper': str(NATIVE_ITF / 'score/itf/core/process/wrapped_process.py'),
        'source_hashes': {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in SUBJECTS.items()},
        'cases': cases,
        'checks_passed': len(cases),
        'native_required_checks': 'separate fresh Fabro run; none replaced by these fixtures',
    }
    (ROOT / 'harness-exit-microcheck.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({'checks_passed': len(cases), 'signals_137_and_143_rejected_after_correction': True}))


if __name__ == '__main__':
    main()
