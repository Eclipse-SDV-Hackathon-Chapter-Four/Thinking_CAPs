#!/home/jefferson/s-core_sw_fabric/.venv/bin/python
"""Collect native Linux Bazel evidence from explicit plans, without credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import time
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))
from storage import build_environment, validate_run_root


def digest(path: Path) -> str:
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    validate_run_root(ROOT)
    workspace = args.workspace.resolve()
    assert workspace.is_relative_to(ROOT / 'workspaces') or workspace == ROOT / 'target'
    output = args.output.resolve()
    assert output.is_relative_to(ROOT) and not output.is_relative_to(workspace)
    output.mkdir(parents=True, exist_ok=True)
    result = {'platform': 'Linux x86_64', 'passed': False, 'checks': [],
              'source_baseline': '381d43dec900ab6a9076f3f30e7bfbdee019e26e',
              'plan_sha256': digest(args.plan), 'acceptance': 'pending_offline'}
    try:
        tools = json.loads((ROOT / 'linux-tools.json').read_text())
        assert digest(Path(tools['bazel']['path'])) == tools['bazel']['sha256']
        for path, expected in tools['external_tools'].items():
            assert digest(Path(path)) == expected
        assert digest(ROOT / 'runtime-overlays.json') == tools['runtime_overlays_sha256']
        overlays = json.loads((ROOT / 'runtime-overlays.json').read_text())['overlays']
        for row in overlays:
            assert digest(Path(row['source'])) == row['source_sha256']
            assert digest(Path(row['target'])) == row['host_original_sha256']
        docker = json.loads((ROOT / 'docker-binding.json').read_text())
        assert Path(docker['socket']).is_socket()
        env = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'LANG': 'C.UTF-8',
               'LC_ALL': 'C.UTF-8', 'HOME': '/tmp/build-home',
               'DOCKER_HOST': 'unix:///run/docker.sock', **build_environment(ROOT)}
        namespace = ['/usr/bin/bwrap', '--die-with-parent', '--ro-bind', '/', '/',
                     '--bind', str(ROOT), str(ROOT), '--tmpfs', '/home/jefferson',
                     '--tmpfs', '/tmp', '--tmpfs', '/var/tmp', '--dir', '/tmp/build-home',
                     '--proc', '/proc', '--dev-bind', '/dev', '/dev',
                     '--ro-bind', docker['socket'], '/run/docker.sock']
        for row in overlays:
            namespace += ['--ro-bind', row['source'], row['target']]
        namespace += ['--chdir', str(workspace)]
        plan = json.loads(args.plan.read_text())
        assert isinstance(plan.get('checks'), list) and plan['checks'], 'Explicit native checks required'
        begun = time.monotonic()
        for index, check in enumerate(plan['checks']):
            validate_run_root(ROOT)
            kind = check['kind']
            assert kind in ['query', 'test', 'build', 'docs', 'lint']
            targets = check['targets']
            assert targets and all(isinstance(t, str) and re.fullmatch(r'//[A-Za-z0-9_/.-]+(?::[A-Za-z0-9_.*+-]+)?', t) for t in targets)
            assert all('qnx' not in t.lower() for t in targets), 'QNX execution excluded'
            config = check.get('config', 'linux_x64')
            assert config in ['linux_x64', 'linux_x64_gcc_15', 'clippy'], 'Unsupported native Linux configuration'
            if kind == 'lint':
                config = 'clippy'
            command = [tools['bazel']['path'], '--batch',
                       '--output_user_root=' + str(ROOT / 'bazel-output'),
                       '--bazelrc=' + str(workspace / 'quality/static_analysis/static_analysis.bazelrc')]
            command += ['query' if kind == 'query' else 'test' if kind == 'test' else 'build',
                        '--repository_cache=' + str(ROOT / 'repository-cache'), '--color=no', '--curses=no']
            if kind == 'query':
                command += ['--output=label_kind', 'set(' + ' '.join(targets) + ')']
            else:
                command += ['--config=' + config, '--jobs=2']
                if kind == 'test':
                    command += ['--local_test_jobs=1', '--test_output=errors', '--cache_test_results=no',
                                '--build_event_json_file=' + str(output / f'check-{index}-events.jsonl')]
                command += targets
            log = output / f'check-{index}.log'
            exact = namespace + command
            limit = max(1, min(1800, 3300 - (time.monotonic() - begun)))
            started = time.monotonic()
            timed_out = False
            with log.open('wb') as stream:
                process = subprocess.Popen(exact, env=env, stdout=stream, stderr=subprocess.STDOUT,
                                           stdin=subprocess.DEVNULL, start_new_session=True)
                try:
                    while process.poll() is None:
                        validate_run_root(ROOT)
                        if time.monotonic() - started > limit:
                            timed_out = True
                            os.killpg(process.pid, signal.SIGKILL)
                            break
                        time.sleep(.5)
                except BaseException:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                    raise
                process.wait()
            with log.open('rb') as stream:
                stream.seek(max(0, log.stat().st_size - 4000))
                tail = stream.read().decode(errors='replace')
            row = {'kind': kind, 'targets': targets, 'config': config, 'command': exact,
                   'environment': env, 'exit_code': process.returncode, 'timed_out': timed_out,
                   'elapsed_seconds': round(time.monotonic() - started, 3),
                   'log': str(log), 'log_sha256': digest(log), 'bounded_tail': tail,
                   'reason': check.get('reason'), 'native_obligation': check.get('native_obligation'),
                   'test_records': []}
            if kind == 'test':
                for xml in (workspace / 'bazel-testlogs').rglob('test.xml'):
                    parsed = ET.parse(xml)
                    destination = output / 'native-testlogs' / xml.relative_to(workspace / 'bazel-testlogs')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(xml.read_bytes())
                    record = {'path': str(destination), 'sha256': digest(destination),
                              'suites': [dict(n.attrib) for n in parsed.getroot().iter('testsuite')]}
                    raw = xml.with_name('test.log')
                    if raw.is_file():
                        retained = destination.with_name('test.log')
                        retained.write_bytes(raw.read_bytes())
                        record['test_log_sha256'] = digest(retained)
                    row['test_records'].append(record)
            result['checks'].append(row)
            save(output / 'native-result.json', result)
            if process.returncode != 0:
                break
        result['passed'] = len(result['checks']) == len(plan['checks']) and all(c['exit_code'] == 0 for c in result['checks'])
    except Exception as error:
        result['infrastructure_error'] = str(error)
    validate_run_root(ROOT)
    save(output / 'native-result.json', result)
    print(json.dumps({'passed': result['passed'], 'checks': len(result['checks']),
                      'infrastructure_error': result.get('infrastructure_error')}))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
