#!/usr/bin/env python3
"""Rebuild frozen sources in new local state and repeat the actual native core.

The original host, immutable images, LLVM repository and deployed openDuT state
are reused explicitly. This is clean-source self-reproduction, not human signoff.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import signal
import subprocess
import sys
import uuid

REPO = Path(__file__).resolve().parents[1]
SCORE_PIN = '93f8ea1e6f76714496c092902e00c9b91c58cdc8'
BRIDGE_PIN = '0d53a2af8b37121e54d742c6cefd0297dd9e4b92'


class ReproductionInterrupted(Exception):
    def __init__(self, signum):
        self.signum = signum
        super().__init__('interrupted by ' + signal.Signals(signum).name)


def run_owned_command(command, timeout, output):
    """Bound the entire owned command group, including compiler/helper children."""
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               start_new_session=True)
    captured = b''
    try:
        captured, _ = process.communicate(timeout=timeout)
    except BaseException as error:
        captured = getattr(error, 'output', None) or b''
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            captured, _ = process.communicate(timeout=30)
        except subprocess.TimeoutExpired as timeout_error:
            captured = timeout_error.output or captured
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            captured, _ = process.communicate(timeout=5)
        raise
    finally:
        output.write_bytes(captured)
    return subprocess.CompletedProcess(command, process.returncode, captured)


def cleanup_build_container(name, identity):
    """Remove only the immutable container ID proven to belong to this run."""
    def docker(*parts):
        return subprocess.run(['docker', *parts], text=True, capture_output=True, timeout=30)

    found = docker('ps', '-a', '--no-trunc', '--filter', 'name=^/' + name + '$', '--format', '{{.ID}}')
    if found.returncode:
        return {'status': 'failed', 'reason': 'cannot enumerate build container', 'exit_code': found.returncode}
    identifiers = found.stdout.strip().splitlines()
    if not identifiers:
        return {'status': 'passed', 'reason': 'build container already absent'}
    if len(identifiers) != 1:
        return {'status': 'failed', 'reason': 'ambiguous build container identity'}
    identifier = identifiers[0]
    inspected = docker('inspect', '--format', '{{json .Config.Labels}}', identifier)
    if inspected.returncode:
        # --rm can complete between enumeration and inspection. Reconcile once.
        current = docker('ps', '-a', '--no-trunc', '--filter', 'name=^/' + name + '$', '--format', '{{.ID}}')
        if current.returncode == 0 and not current.stdout.strip():
            return {'status': 'passed', 'reason': 'build container removed during inspection'}
        return {'status': 'failed', 'reason': 'cannot verify build container ownership'}
    labels = json.loads(inspected.stdout) or {}
    if labels.get('sdv.reproduction.run') != identity:
        return {'status': 'failed', 'reason': 'refuse removing unowned build container', 'container_id': identifier}
    removed = docker('rm', '-f', identifier)
    remaining = docker('ps', '-a', '--no-trunc', '--filter', 'id=' + identifier, '--format', '{{.ID}}')
    if remaining.returncode or remaining.stdout.strip():
        return {'status': 'failed', 'reason': 'build container removal not verified', 'container_id': identifier,
                'remove_exit_code': removed.returncode}
    return {'status': 'passed', 'reason': 'owned build container removed', 'container_id': identifier}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--state', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--integration-revision', help='Freeze this revision; defaults to the current committed integration HEAD')
    parser.add_argument('--operator', help='Caller-declared operator identity; omission records unknown, not an invented human or agent')
    parser.add_argument('--shared-host', action=argparse.BooleanOptionalAction, default=None,
                        help='Declare whether the original reference host is shared; omission records unknown')
    args = parser.parse_args()
    args.state = args.state.resolve()
    args.output = args.output.resolve()
    args.state.mkdir(parents=True, exist_ok=False, mode=0o700)
    args.output.mkdir(parents=True, exist_ok=False)
    identity = uuid.uuid4().hex
    manifest = {'schema_version': 1, 'work_classification': 'prepared', 'operator': args.operator,
                'operator_identity_basis': 'caller declaration' if args.operator else 'not declared',
                'independent_person_reproduced': False, 'shared_host': args.shared_host,
                'shared_host_basis': 'caller declaration' if args.shared_host is not None else 'not declared',
                'observed_environment': {'hostname': platform.node(), 'platform': platform.platform(),
                                         'python_executable': sys.executable, 'python_version': platform.python_version()},
                'shared_assets': ['immutable Docker images', 'deployed openDuT', 'LLVM repository in Bazel volume'],
                'rust_target': 'fresh', 'bazel_output_base': 'fresh', 'sources': {}, 'commands': []}
    config = {}
    build_name = 'sdv-repro-' + identity[:10]
    ownership_name = build_name + '-ownership'
    build_attempted = False
    original_handlers = {signum: signal.getsignal(signum) for signum in (signal.SIGINT, signal.SIGTERM)}
    def interrupted(signum, _frame):
        # Further graceful signals cannot interrupt ownership-checked finalization.
        for current in original_handlers:
            signal.signal(current, signal.SIG_IGN)
        raise ReproductionInterrupted(signum)
    for signum in original_handlers:
        signal.signal(signum, interrupted)
    count = 0
    def run(command, timeout=1200):
        nonlocal count
        count += 1
        command = [str(part) for part in command]
        manifest['commands'].append(command)
        completed = run_owned_command(command, timeout, args.output / ('command-' + str(count).zfill(2) + '.txt'))
        if completed.returncode:
            raise RuntimeError('command failed: ' + str(count) + '; exit=' + str(completed.returncode))
        return completed.stdout.decode().strip()
    try:
        config = json.loads(args.config.read_text())
        if not isinstance(config, dict):
            config = {}
            raise ValueError('reproduction config must be a JSON object')
        integration_pin = run(['git', '-C', REPO, 'rev-parse', '--verify', (args.integration_revision or 'HEAD') + '^{commit}'])
        manifest['reproducer_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        manifest['rustc'] = run(['rustc', '+stable', '--version'])
        if config.get('expected_rustc') and manifest['rustc'] != config['expected_rustc']:
            raise RuntimeError('stable compiler identity differs from the selected build')
        # --no-hardlinks prevents this new checkout sharing mutable Git objects.
        for name, origin, pin in (('integration', str(REPO), integration_pin),
                                 ('score', config['baseline_source'], SCORE_PIN),
                                 ('bridge', config['bridge_source'], config.get('bridge_revision', BRIDGE_PIN))):
            requested = Path(origin).resolve()
            origin = run(['git', '-C', origin, 'rev-parse', '--show-toplevel'])
            relative = str(requested.relative_to(Path(origin)))
            destination = args.state / name
            run(['git', 'clone', '--no-hardlinks', '--no-checkout', origin, destination])
            run(['git', '-C', destination, 'checkout', '--detach', pin])
            clean = run(['git', '-C', destination, 'status', '--porcelain'])
            if clean:
                raise RuntimeError('clone was not initially clean: ' + name)
            manifest['sources'][name] = {'origin': origin, 'revision': run(['git', '-C', destination, 'rev-parse', 'HEAD']),
                                         'clean_before_patch': True, 'source_subdirectory': relative}
        integration = args.state / 'integration'
        score = args.state / 'score'
        patch = integration / 'OpenSOVD/patches/receiver-diagnostics/s-core-observation.patch'
        # Frozen revisions from before the component layout retain the original paths.
        if not patch.exists():
            patch = integration / 'patches/receiver-diagnostics/s-core-observation.patch'
        run(['git', '-C', score, 'apply', '--index', patch])
        diff = subprocess.check_output(['git', '-C', score, 'diff', '--binary', 'HEAD'])
        if diff != patch.read_bytes():
            raise RuntimeError('clean source does not match exported receiver patch')
        manifest['sources']['score']['patch_sha256'] = hashlib.sha256(diff).hexdigest()
        image = config['score_build_image']
        if run(['docker', 'image', 'inspect', '--format', '{{.Id}}', image]) != image:
            raise RuntimeError('score_build_image must be an immutable image ID')
        output_base = '/var/cache/bazel/sdv-reproduction-' + identity[:10]
        bazel = ['bazel', '--output_base=' + output_base]
        flags = ['--jobs=2']
        if config.get('llvm_repository'):
            flags.append('--override_repository=toolchains_llvm++llvm+llvm_toolchain_llvm=' + config['llvm_repository'])
        else:
            manifest['shared_assets'].remove('LLVM repository in Bazel volume')
        docker = ['docker', 'run', '--rm', '--name', build_name, '--label', 'sdv.reproduction.run=' + identity,
                  '--user', '0', '-v', str(score) + ':/home/source', '-v', config['bazel_volume'] + ':/var/cache/bazel',
                  '-w', '/home/source/cc_s-core', '--entrypoint', 'bash', image, '-c']
        # Structured subprocess arguments are converted with shell quoting only
        # for the command inside the owned build container.
        import shlex
        def build_command(parts):
            nonlocal build_attempted
            build_attempted = True
            return run(docker + [shlex.join(parts)], timeout=1800)
        build_command(bazel + ['build', *flags, '//score/cruise_control:cruise_control_main',
            '//tests/integration/gatewayd:gatewayd', '//tests/integration/someipd:someipd',
            '//tests/integration:cruise_control_someip_config', '@flatbuffers//:flatc'])
        build_command(bazel + ['test', *flags, '//score/cruise_control:cruise_control_unit_tests'])
        flatc = build_command(bazel + ['cquery', *flags, '@flatbuffers//:flatc', '--output=files']).splitlines()
        candidates = [line for line in flatc if line.startswith('bazel-out/') and line.endswith('/flatc')]
        if len(candidates) != 1:
            raise RuntimeError('could not resolve a unique built flatc from cquery')
        execution_root = build_command(bazel + ['info', 'execution_root']).splitlines()[-1]
        config['flatc'] = execution_root + '/' + candidates[0]
        config['gateway_schema'] = output_base + '/external/score_someip_gateway+/score/config/mw_someip_config.fbs'
        target = args.state / 'rust-target'
        fault_builder = integration / 'OpenSOVD/scripts/build_fault_diagnostics.py'
        if not fault_builder.exists():
            fault_builder = integration / 'scripts/build_fault_diagnostics.py'
        run([sys.executable, fault_builder, '--state', args.state / 'fault-build',
             '--target-dir', target, '--output', args.output / 'fault-build', '--check'], timeout=1800)
        config['binary'] = str(target / 'debug/sdv-receiver-diagnostics')
        config['score_source'] = config['baseline_source'] = str(score / 'cc_s-core')
        config['bridge_source'] = str(args.state / 'bridge' / manifest['sources']['bridge']['source_subdirectory'])
        local = args.output / 'reproduction-inputs.json'
        local.write_text(json.dumps(config, indent=2) + '\n')
        manifest['native_binary_sha256'] = hashlib.sha256(Path(config['binary']).read_bytes()).hexdigest()
        manifest['bazel_output_base_path'] = output_base
        run([sys.executable, integration / 'scripts/run_campaign.py', '--config', local,
             '--scenario', 'core', '--output', args.output / 'campaign'], timeout=240)
        manifest['status'] = 'passed'
        code = 0
    except ReproductionInterrupted as error:
        manifest['status'] = 'failed'
        manifest['reason'] = str(error)
        manifest['interrupted_signal'] = signal.Signals(error.signum).name
        code = 128 + error.signum
    except (OSError, RuntimeError, KeyError, ValueError, subprocess.SubprocessError) as error:
        manifest['status'] = 'failed'
        manifest['reason'] = str(error)
        code = 1
    finally:
        for signum in original_handlers:
            signal.signal(signum, signal.SIG_IGN)
        if build_attempted:
            try:
                manifest['build_container_cleanup'] = cleanup_build_container(build_name, identity)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                manifest['build_container_cleanup'] = {'status': 'failed', 'reason': str(error)}
            if manifest['build_container_cleanup']['status'] != 'passed':
                manifest['status'] = 'failed'
                code = 1
        else:
            manifest['build_container_cleanup'] = {'status': 'skipped', 'reason': 'native build never attempted'}
        # Only this new owned state can contain root-owned Bazel symlinks/files.
        if config.get('score_build_image'):
            try:
                run(['docker', 'run', '--rm', '--network', 'none', '--entrypoint', 'chown',
                     '--name', ownership_name, '--label', 'sdv.reproduction.run=' + identity,
                     '-v', str(args.state) + ':/owned', config['score_build_image'],
                     '-R', str(os.getuid()) + ':' + str(os.getgid()), '/owned'], timeout=60)
            except (OSError, RuntimeError, subprocess.SubprocessError) as error:
                manifest['status'] = 'failed'
                manifest['cleanup_error'] = str(error)
                code = 1
            try:
                manifest['ownership_container_cleanup'] = cleanup_build_container(ownership_name, identity)
            except (OSError, ValueError, subprocess.SubprocessError) as error:
                manifest['ownership_container_cleanup'] = {'status': 'failed', 'reason': str(error)}
            if manifest['ownership_container_cleanup']['status'] != 'passed':
                manifest['status'] = 'failed'
                code = 1
        try:
            (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
        finally:
            for signum, handler in original_handlers.items():
                signal.signal(signum, handler)
    print(json.dumps({'status': manifest['status'], 'output': str(args.output), 'independent_person_reproduced': False}))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
