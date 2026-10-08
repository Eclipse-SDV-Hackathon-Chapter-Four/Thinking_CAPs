"""Own a private rootless Docker runtime, without altering the global daemon."""
import hashlib
import json
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from storage import private_server_root, validate_run_root

ROOT = Path(__file__).parent
PRIVATE = private_server_root(ROOT, 'rust_api_queue_docker')
SHORT = Path.home() / '.local/state/s-core/dk' / hashlib.sha256(str(ROOT).encode()).hexdigest()[:12]
STATE = SHORT.parent / (SHORT.name + '_state')

def write(name, value):
    (ROOT / name).write_text(json.dumps(value, indent=2) + '\n')

def status():
    validate_run_root(ROOT)
    binding = json.loads((ROOT / 'docker-binding.json').read_text())
    result = subprocess.run(['/usr/bin/docker', '--host', binding['endpoint'], 'info', '--format', '{{json .}}'], capture_output=True, text=True, timeout=10, env={'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'DOCKER_CONFIG': str(PRIVATE / 'client')})
    if result.returncode:
        return {'exit_code': result.returncode, 'stderr': result.stderr}
    data = json.loads(result.stdout)
    assert data['DockerRootDir'] == str(ROOT / 'docker-data')
    assert any('rootless' in s for s in data['SecurityOptions'])
    return {'exit_code': 0, **{k: data.get(k) for k in ['ServerVersion', 'DockerRootDir', 'Driver', 'SecurityOptions', 'Name']}}

def start():
    validate_run_root(ROOT)
    assert not (ROOT / 'docker-binding.json').exists(), 'Single owned daemon start'
    SHORT.parent.mkdir(parents=True, exist_ok=True)
    if not SHORT.exists():
        SHORT.symlink_to(PRIVATE, target_is_directory=True)
    assert SHORT.resolve() == PRIVATE.resolve()
    STATE.mkdir(mode=0o700, exist_ok=True)
    if not (PRIVATE / 'short-state').exists():
        (PRIVATE / 'short-state').symlink_to(STATE, target_is_directory=True)
    assert (PRIVATE / 'short-state').resolve() == STATE.resolve()
    for name in ['runtime', 'client', 'config']:
        (PRIVATE / name).mkdir(mode=0o700, exist_ok=True)
    (STATE / 'runtime').mkdir(mode=0o700, exist_ok=True)
    configuration = PRIVATE / 'daemon.json'
    configuration.write_text('{}\n')
    configuration.chmod(0o600)
    socket = STATE / 'runtime/docker.sock'
    command = ['/usr/bin/dockerd-rootless.sh', '--config-file', str(configuration), '--data-root', str(ROOT / 'docker-data'), '--exec-root', str(STATE / 'e'), '--pidfile', str(PRIVATE / 'dockerd.pid'), '--host', 'unix://' + str(socket)]
    user_runtime = Path('/run/user') / str(os.getuid())
    assert (user_runtime / 'bus').is_socket(), 'Existing user DBus session required'
    env = {'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'HOME': str(Path.home()), 'USER': 'jefferson', 'XDG_RUNTIME_DIR': str(user_runtime), 'DBUS_SESSION_BUS_ADDRESS': 'unix:path=' + str(user_runtime / 'bus'), 'XDG_CONFIG_HOME': str(PRIVATE / 'config'), 'DOCKER_CONFIG': str(PRIVATE / 'client'), 'DOCKERD_ROOTLESS_ROOTLESSKIT_STATE_DIR': str(STATE / 'rootlesskit-c3'), 'CONTAINERD_ROOTLESS_ROOTLESSKIT_STATE_DIR': str(STATE / 'containerd-rootless-c3')}
    (ROOT / 'logs').mkdir(exist_ok=True)
    log_path = ROOT / 'logs/docker-daemon-start.log'
    with log_path.open('wb') as log:
        daemon = subprocess.Popen(command, env=env, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    binding = {'pid': daemon.pid, 'endpoint': 'unix://' + str(socket), 'socket': str(socket), 'private_state': str(PRIVATE), 'data_root': str(ROOT / 'docker-data'), 'command': command, 'environment': env, 'config_sha256': hashlib.sha256(configuration.read_bytes()).hexdigest(), 'rootless_script_sha256': hashlib.sha256(Path(command[0]).read_bytes()).hexdigest(), 'global_daemon_reconfigured': False}
    write('docker-binding.json', binding)
    deadline = time.monotonic() + 30
    while time.monotonic() < deadline:
        validate_run_root(ROOT)
        if daemon.poll() is not None:
            write('docker-runtime-preflight.json', {'exit_code': daemon.returncode, 'status': 'failed', 'reason': 'Owned rootless daemon exited before readiness', 'log': str(log_path.relative_to(ROOT))})
            return 1
        if socket.exists():
            result = status()
            if result['exit_code'] == 0:
                write('docker-runtime-preflight.json', {'status': 'passed', **result})
                print(json.dumps(result))
                return 0
        time.sleep(.5)
    write('docker-runtime-preflight.json', {'exit_code': 1, 'status': 'failed', 'reason': 'Owned daemon readiness timed out'})
    stop()
    return 1

def stop():
    if not (ROOT / 'docker-binding.json').exists():
        return 0
    binding = json.loads((ROOT / 'docker-binding.json').read_text())
    pid = binding['pid']
    try:
        raw = Path(f'/proc/{pid}/cmdline').read_bytes()
        assert b'rootless' in raw and str(ROOT).encode() in raw, 'Do not signal an unrelated PID'
        os.killpg(pid, signal.SIGTERM)
        for _ in range(30):
            if not Path(f'/proc/{pid}').exists():
                break
            time.sleep(.2)
        if Path(f'/proc/{pid}').exists():
            # A zombie group leader has no running descendants; kill is still group-scoped.
            os.killpg(pid, signal.SIGKILL)
    except (FileNotFoundError, ProcessLookupError):
        pass
    check = subprocess.run(['/usr/bin/docker', '--host', binding['endpoint'], 'info', '--format', '{{json .}}'], capture_output=True, text=True, timeout=10, env={'PATH': '/usr/sbin:/usr/bin:/sbin:/bin', 'DOCKER_CONFIG': str(PRIVATE / 'client')})
    members = []
    for process in Path('/proc').iterdir():
        if not process.name.isdigit():
            continue
        try:
            if os.getpgid(int(process.name)) == pid:
                state = (process / 'stat').read_text().split(') ', 1)[1].split()[0]
                if state != 'Z':
                    members.append(int(process.name))
        except (FileNotFoundError, ProcessLookupError, PermissionError):
            pass
    stopped = check.returncode != 0 and not members
    write('docker-shutdown.json', {'pid': pid, 'owned_runtime_stopped': stopped, 'owned_group_running_members': members, 'private_API_exit_code': check.returncode, 'private_API_stderr': check.stderr, 'socket': binding['socket'], 'global_daemon_stopped': False})
    return 0 if stopped else 1

if __name__ == '__main__':
    action = sys.argv[1]
    if action == 'status':
        print(json.dumps(status()))
    else:
        sys.exit({'start': start, 'stop': stop}[action]())
