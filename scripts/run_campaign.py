#!/usr/bin/env python3
"""Run named native receiver campaigns with honest evidence and exit codes."""
import argparse
import datetime
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

REPO = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def exit_for(rows):
    statuses = {row['status'] for row in rows}
    return 1 if 'failed' in statuses else 2 if 'blocked' in statuses else 0


def assess(selection, code, child, definitions):
    checks = child.get('checks', [])
    by_id = {check['id']: check for check in checks}
    if selection == 'carla' and code == 2 and child.get('status') == 'blocked':
        failed = [c for c in checks if c['status'] == 'failed']
        return [{'id': 'CARLA-prerequisite', 'status': 'blocked', 'reason': by_id.get('execution', {}).get('reason', 'CARLA unavailable')},
                {'id': 'runner-and-cleanup', 'status': 'failed' if failed else 'passed', 'failed_checks': failed}]
    if selection == 'cleanup-failure':
        failed = [check for check in checks if check['status'] != 'passed']
        expected = (len(failed) == 1 and failed[0]['id'] == 'execution' and
                    'deliberate failure after tunnel disturbance' in failed[0].get('reason', ''))
        required = ('restore-tunnel', 'restore-private-directory-owner')
        cleanup = all(by_id.get(key, {}).get('status') == 'passed' for key in required)
        for prefix, count in (('cleanup-', 3), ('stop-capture-', 4), ('read-capture-', 4)):
            cleanup = cleanup and sum(c['id'].startswith(prefix) and c['status'] == 'passed' for c in checks) >= count
        passed = code == 1 and child.get('status') == 'failed' and expected and cleanup
        return [{'id': 'T07', 'status': 'passed' if passed else 'failed',
                 'reason': 'Only the deliberately injected failure is expected; all owned cleanup must pass.'}]
    rows = []
    for definition in definitions:
        missing = [key for key in definition['checks'] if by_id.get(key, {}).get('status') != 'passed']
        rows.append({'id': definition['id'], 'name': definition['name'],
                     'status': 'failed' if missing else 'passed', 'missing_or_failed_checks': missing})
    if selection == 'carla':
        keys = ('real-carla-moving-actor', 'real-carla-return-actuation', 'real-carla-native-actuation-correlation', 'cleanup-owned-carla')
        missing = [key for key in keys if by_id.get(key, {}).get('status') != 'passed']
        rows.append({'id': 'CARLA', 'status': 'failed' if missing else 'passed', 'missing_or_failed_checks': missing})
    honest = code == 0 and child.get('status') == 'passed' and bool(checks) and all(c['status'] == 'passed' for c in checks)
    rows.append({'id': 'runner-and-cleanup', 'status': 'passed' if honest else 'failed', 'child_exit': code})
    return rows


def junit(rows):
    suite = ET.Element('testsuite', name='sdv-receiver', tests=str(len(rows)),
                       failures=str(sum(r['status'] == 'failed' for r in rows)),
                       skipped=str(sum(r['status'] in ('blocked', 'skipped') for r in rows)))
    for row in rows:
        case = ET.SubElement(suite, 'testcase', name=row['id'], classname='integration.campaign')
        if row['status'] == 'failed':
            ET.SubElement(case, 'failure', message=row.get('reason', 'selected acceptance failed')).text = json.dumps(row)
        elif row['status'] in ('blocked', 'skipped'):
            ET.SubElement(case, 'skipped', message=row.get('reason', row['status']))
    return suite


def command(args, timeout=20):
    return subprocess.check_output([str(a) for a in args], stderr=subprocess.STDOUT, timeout=timeout).decode().strip()


def snapshot(path):
    path = Path(path).resolve()
    root = Path(command(['git', '-C', path, 'rev-parse', '--show-toplevel']))
    diff = subprocess.check_output(['git', '-C', root, 'diff', '--binary', 'HEAD'], timeout=20)
    return {'path': str(root), 'revision': command(['git', '-C', root, 'rev-parse', 'HEAD']),
            'status': command(['git', '-C', root, 'status', '--porcelain']).splitlines(),
            'tracked_diff_sha256': hashlib.sha256(diff).hexdigest()}


def preflight(config, selection):
    if config.get('schema_version') != 1:
        raise RuntimeError('local input schema_version must be 1')
    required = ('state', 'binary', 'score_source', 'baseline_source', 'bridge_source',
                'score_image', 'bridge_image', 'bazel_volume', 'flatc', 'gateway_schema')
    for key in required:
        if not isinstance(config.get(key), str) or not config[key]:
            raise RuntimeError('missing local input: ' + key)
    for key in ('binary', 'score_source', 'baseline_source', 'bridge_source'):
        if not Path(config[key]).exists():
            raise RuntimeError('missing ' + key + ': ' + config[key])
    if not os.access(config['binary'], os.X_OK):
        raise RuntimeError('native binary is not executable')
    if importlib.util.find_spec('zenoh') is None:
        raise RuntimeError('selected Python interpreter lacks Zenoh')
    deployment = Path(config['state']) / 'deployment.json'
    if not deployment.exists() or json.loads(deployment.read_text()).get('phase') != 'deployed':
        raise RuntimeError('deployed openDuT state required')
    command(['docker', 'info', '--format', '{{.ServerVersion}}'])
    for key in ('score_image', 'bridge_image'):
        actual = command(['docker', 'image', 'inspect', '--format', '{{.Id}}', config[key]])
        if actual != config[key]:
            raise RuntimeError(key + ' must be an immutable local image ID, actual: ' + actual)
    command(['docker', 'volume', 'inspect', config['bazel_volume']])
    tools = command(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'sha256sum',
                     '-v', config['bazel_volume'] + ':/var/cache/bazel:ro', config['score_image'],
                     config['flatc'], config['gateway_schema']])
    if selection == 'carla':
        for module in ('carla', 'pygame', 'numpy'):
            if importlib.util.find_spec(module) is None:
                raise RuntimeError('selected Python interpreter lacks ' + module)
        carla = config.get('carla', {})
        if not isinstance(carla, dict):
            raise RuntimeError('carla inputs must be an object')
        for key in ('vehicle_module', 'signals', 'vcu_module'):
            if not Path(carla.get(key, '')).is_file():
                raise RuntimeError('missing CARLA input: ' + key)
        if not (Path(carla.get('root', '')) / 'CarlaUE4/Binaries/Linux/CarlaUE4-Linux-Shipping').is_file():
            raise RuntimeError('missing CARLA executable')
    return tools


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--scenario', choices=('core', 'cleanup-failure', 'carla'), default='core')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run-id', type=lambda value: uuid.UUID(value).hex,
                        help='Coordinator UUID; default is a new runner UUID')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    started = time.monotonic_ns()
    run_id = args.run_id or uuid.uuid4().hex
    manifest = {'schema_version': 1, 'run_id': run_id, 'scenario': args.scenario, 'seed': 42,
                'work_classification': 'prepared', 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'clock_domain': 'linux-clock-monotonic; simulation clock separate',
                'independent_person_reproduced': False, 'python': sys.version, 'inputs': {}, 'repositories': {}}
    rows, events = [], [{'run_id': run_id, 'event_id': 'campaign-start', 'source': 'runner',
                        'clock_domain': 'linux-clock-monotonic', 'monotonic_ns': started}]
    child_process = None
    interrupted = False
    def forward(signum, frame):
        nonlocal interrupted
        interrupted = True
        if child_process is not None and child_process.poll() is None:
            child_process.send_signal(signum)
    handlers = {sig: signal.signal(sig, forward) for sig in (signal.SIGINT, signal.SIGTERM)}
    stage = 'preflight'
    bench_lock = None
    try:
        config = json.loads(args.config.read_text())
        state = Path(config['state'])
        if not state.is_dir():
            raise RuntimeError('configured openDuT state directory is missing')
        bench_lock = (state / 'campaign.lock').open('a')
        try:
            fcntl.flock(bench_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise RuntimeError('another campaign owns the configured openDuT bench') from error
        manifest['config_sha256'] = digest(args.config)
        manifest['native_tool_hashes'] = preflight(config, args.scenario)
        manifest['mode'] = 'fixture vehicle inputs; real receiver/openDuT/native faults' if args.scenario != 'carla' else 'real CARLA; existing X-Verse/VCU; harness operator commands'
        for path in (args.config, REPO / 'scripts/run_campaign.py', REPO / 'OpenDut/tests/opendut_receiver_smoke.py',
                     REPO / 'tests/campaigns/core.json', REPO / 'OpenSOVD/integration/diagnostics/Cargo.toml',
                     REPO / 'OpenSOVD/integration/diagnostics/fault-build.lock', REPO / 'OpenSOVD/patches/receiver-diagnostics/s-core-observation.patch',
                     REPO / 'OpenSOVD/patches/fault-storage/write-through.patch', REPO / 'OpenSOVD/scripts/receiver_container_entrypoint.sh',
                     REPO / 'scripts/owned_carla.py', REPO / 'OpenSOVD/config/faults/cruise-control.json',
                     *sorted((REPO / 'OpenSOVD/integration/diagnostics/src').glob('*.rs')), Path(config['binary'])):
            manifest['inputs'][str(path.resolve())] = digest(path)
        if args.scenario == 'carla':
            for key in ('vehicle_module', 'vcu_module', 'signals', 'vulkan_icd'):
                if config['carla'].get(key):
                    path = Path(config['carla'][key])
                    manifest['inputs'][str(path.resolve())] = digest(path)
            manifest['inputs'][str(Path(config['carla']['vcu_module']).parent / 'config.py')] = digest(Path(config['carla']['vcu_module']).parent / 'config.py')
            manifest['carla_executable_sha256'] = digest(Path(config['carla']['root']) / 'CarlaUE4/Binaries/Linux/CarlaUE4-Linux-Shipping')
        manifest['repositories'] = {key: snapshot(path) for key, path in [('integration', REPO)] +
                                    [(k, config[k]) for k in ('score_source', 'baseline_source', 'bridge_source')]}
        local = args.output / 'inputs.json'
        local.write_text(json.dumps(config, indent=2) + '\n')
        definitions = json.loads((REPO / 'tests/campaigns/core.json').read_text())
        child_dir = args.output / 'native'
        invocation = [sys.executable, str(REPO / 'OpenDut/tests/opendut_receiver_smoke.py'), '--fault-lifecycle',
                      '--inputs', str(local.resolve()), '--output', str(child_dir.resolve())]
        for key, flag in (('state', '--state'), ('binary', '--binary'), ('score_source', '--score-source'),
                          ('baseline_source', '--baseline-source'), ('bridge_source', '--bridge-source')):
            invocation += [flag, config[key]]
        if args.scenario == 'cleanup-failure':
            invocation.append('--fail-after-disturbance')
        if args.scenario == 'carla':
            carla_file = args.output / 'carla-inputs.json'
            carla_file.write_text(json.dumps(config['carla'], indent=2) + '\n')
            invocation += ['--carla-config', str(carla_file.resolve())]
        if interrupted:
            raise RuntimeError('interrupted before native campaign')
        stage = 'execution'
        with (args.output / 'runner.log').open('w') as log:
            child_process = subprocess.Popen(invocation, stdout=log, stderr=subprocess.STDOUT,
                                             pass_fds=(bench_lock.fileno(),))
            try:
                code = child_process.wait(timeout=240 if args.scenario == 'carla' else 180)
            except subprocess.TimeoutExpired:
                child_process.terminate()
                code = child_process.wait(timeout=45)
                raise RuntimeError('native campaign deadline exceeded; cleanup requested')
        child = json.loads((child_dir / 'results.json').read_text())
        rows = assess(args.scenario, code, child, definitions['scenarios'])
        manifest['child_exit'] = code
        manifest['native_manifest'] = json.loads((child_dir / 'manifest.json').read_text())
        for index, event in enumerate(json.loads((child_dir / 'events.json').read_text())):
            events.append(dict(event, run_id=run_id, event_id=event['kind'] + '-' + str(index),
                               source='external-injector', clock_domain='linux-clock-monotonic'))
        for index, record in enumerate(json.loads((child_dir / 'requests.json').read_text())):
            events.append({'run_id': run_id, 'event_id': 'diagnostic-observation-' + str(index),
                           'source': 'native-OpenSOVD', 'clock_domain': 'linux-clock-monotonic',
                           'monotonic_ns': record['observed_at_monotonic_ns'], 'uri': record['uri'],
                           'response_sha256': hashlib.sha256(json.dumps(record['response'], sort_keys=True).encode()).hexdigest()})
        manifest['native_evidence_sha256'] = {p.name: digest(p) for p in sorted(child_dir.iterdir()) if p.is_file()}
        if digest(config['binary']) != manifest['inputs'][str(Path(config['binary']).resolve())]:
            rows.append({'id': 'binary-stability', 'status': 'failed', 'reason': 'native binary changed during run'})
        for identifier, reason in definitions['conditional_skipped'].items():
            rows.append({'id': identifier, 'status': 'skipped', 'reason': reason})
        if args.scenario == 'cleanup-failure':
            rows += [{'id': d['id'], 'status': 'skipped', 'reason': 'not selected; only T07 cleanup acceptance'} for d in definitions['scenarios']]
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, subprocess.SubprocessError) as error:
        rows.append({'id': stage, 'status': 'blocked' if stage == 'preflight' else 'failed', 'reason': str(error)})
        if child_process is not None and child_process.poll() is None:
            child_process.terminate()
            try:
                child_process.wait(timeout=45)
            except subprocess.TimeoutExpired:
                child_process.kill()
                child_process.wait()
                rows.append({'id': 'cleanup-timeout', 'status': 'failed', 'reason': 'child killed; inspect owned resources before next run'})
    finally:
        for sig, handler in handlers.items():
            signal.signal(sig, handler)
    if interrupted:
        rows.append({'id': 'interruption', 'status': 'failed', 'reason': 'runner interrupted; owned cleanup requested'})
    code = exit_for(rows)
    status = 'passed' if code == 0 else 'failed' if code == 1 else 'blocked'
    manifest['finished_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    manifest['elapsed_ns'] = time.monotonic_ns() - started
    counts = {status: sum(row['status'] == status for row in rows) for status in ('passed', 'failed', 'blocked', 'skipped')}
    result = {'schema_version': 1, 'run_id': run_id, 'status': status, 'exit_code': code, 'counts': counts, 'scenarios': rows}
    events.append({'run_id': run_id, 'event_id': 'campaign-finish', 'source': 'runner', 'clock_domain': 'linux-clock-monotonic', 'monotonic_ns': time.monotonic_ns(), 'status': status})
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (args.output / 'results.json').write_text(json.dumps(result, indent=2) + '\n')
    (args.output / 'timeline.jsonl').write_text(''.join(json.dumps(e) + '\n' for e in events))
    ET.ElementTree(junit(rows)).write(args.output / 'junit.xml', encoding='unicode', xml_declaration=True)
    (args.output / 'summary.md').write_text('# Campaign ' + run_id + '\n\n' + status + ': ' + json.dumps(counts) + '\n\n' +
        'Prepared work. Mode: ' + manifest.get('mode', 'not executed; prerequisites blocked') + '.\n' +
        'Native /faults, AAOS/FOTA, E2E and VIPER are conditional/deferred. Independent-person reproduction remains pending.\n\n' +
        '\n'.join('- ' + r['id'] + ': ' + r['status'] + (' — ' + r['reason'] if 'reason' in r else '') for r in rows) + '\n')
    if bench_lock is not None:
        bench_lock.close()
    print(json.dumps({'status': status, 'exit_code': code, 'output': str(args.output), 'counts': counts}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
