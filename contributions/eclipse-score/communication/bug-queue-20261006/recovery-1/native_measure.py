"""Protected native measurement functions derived from the preserved stable collector."""
from pathlib import Path
import hashlib,json,os,signal,subprocess,time,urllib.request
from score_sw_fabric.storage import build_environment,validate_run_root
P=Path(__file__).resolve().parent
C=json.loads((P/'configuration.json').read_text())
R=Path(C['scratch_root'])
SERVER='http://127.0.0.1:43916'
AUTH=Path('/home/jefferson/.local/state/s-core/fabro/someip84-server/cli-auth.json')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    temporary = p.with_name(p.name + '.tmp')
    temporary.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
    temporary.replace(p)

def api(route, raw=False):
    token = json.loads(AUTH.read_text())['servers'][SERVER]['token']
    req = urllib.request.Request(SERVER + route, headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=20) as response:
        body = response.read(20_000_001)
    if len(body) > 20_000_000:
        raise ValueError('Native response exceeds bound')
    return body if raw else json.loads(body)

def hashes(tree):
    return {str(p.relative_to(tree)): sha(p) for p in tree.rglob('*')
            if p.is_file() and not p.is_symlink() and '.git' not in p.relative_to(tree).parts
            and not any(part.startswith('bazel-') for part in p.relative_to(tree).parts)
            and '.ruff_cache' not in p.relative_to(tree).parts}

def guard():
    validate_run_root(R)
    mount = json.loads(subprocess.check_output(['findmnt', '-J', '-T', str(R), '-o', 'SOURCE,UUID'], text=True))['filesystems'][0]
    if mount['source'] != C['required_device'] or mount['uuid'] != C['volume_uuid']:
        raise ValueError('Storage identity changed; stop without relocating')
    for name, expected in json.loads((P / 'frozen-inputs.json').read_text()).items():
        if sha(P / name) != expected:
            raise ValueError('Frozen input changed: ' + name)
    for name, expected in C['tools'].items():
        if sha(R / 'tools' / name) != expected:
            raise ValueError('Pinned native tool changed: ' + name)

def measure(d, tree, label, args, timeout=1200):
    guard()
    storage = build_environment(R)
    storage.pop('TEST_TMPDIR', None)
    env = {**os.environ, **storage, 'PYTHONDONTWRITEBYTECODE': '1'}
    image = C['image_id']
    if subprocess.check_output(['/usr/bin/docker', 'image', 'inspect', image, '--format', '{{.Id}}'], text=True).strip() != image:
        raise ValueError('Pinned build image missing or changed')
    name = 'score-bug-' + d.name + '-' + label
    command = ['/usr/bin/docker', 'run', '--rm', '--name', name, '--read-only', '--network', 'host',
               '--user', '1000:1000', '--group-add', '999', '--cpus', '8', '--memory', '16g', '--cap-add', 'SYS_ADMIN',
               '--security-opt', 'seccomp=unconfined', '--security-opt', 'apparmor=unconfined',
               '--mount', f'type=bind,source={R},target={R}',
               '--mount', f'type=bind,source={R / "container-tmp"},target=/tmp',
               '--mount', f'type=bind,source={R / "container-var-tmp"},target=/var/tmp',
               '--mount', f'type=bind,source={R / "tools/docker-client"},target=/usr/bin/docker,readonly',
               '--mount', 'type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock',
               '--workdir', str(tree), '--env', 'HOME=' + str(R / 'container-home'),
               '--env', 'PATH=' + str(R / 'tools') + ':/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
               '--env', 'PYTHONDONTWRITEBYTECODE=1']
    for key, value in storage.items():
        command += ['--env', key + '=' + value]
    bazel_args = list(args)
    if args[0] == 'test':
        bazel_args += ['--test_env=' + k + '=' + v for k, v in sorted({**storage, 'HOME': str(R / 'container-home')}.items())]
    # Bazel options must precede the native binary's -- argument separator.
    insert = bazel_args.index('--') if '--' in bazel_args else len(bazel_args)
    if args[0] in {'run', 'build', 'test'}:
        bazel_args[insert:insert] = ['--jobs=8']
    command += ['--entrypoint', str(R / 'tools/bazel-8.7.0'), image,
                '--output_user_root=' + str(R / 'bazel-output'), '--batch', *bazel_args]
    evidence = d / 'evidence'
    evidence.mkdir(exist_ok=True)
    out, err = evidence / (label + '.stdout'), evidence / (label + '.stderr')
    record = {'command': command, 'cwd': str(tree), 'subject_hashes': hashes(tree),
              'started_at_epoch': time.time(), 'timeout_seconds': timeout, 'carried_evidence': False}
    with out.open('wb') as stdout, err.open('wb') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, env=env, start_new_session=True)
        try:
            while process.poll() is None:
                guard()
                if time.time() - record['started_at_epoch'] > timeout:
                    raise TimeoutError('Native command exceeded time bound')
                time.sleep(1)
            record['exit_code'] = process.returncode
        except BaseException as error:
            subprocess.run(['/usr/bin/docker', 'rm', '--force', name], capture_output=True, timeout=15)
            if process.poll() is None:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
            record.update(exit_code=process.returncode, stop_reason=str(error))
    record.update(finished_at_epoch=time.time(), stdout_sha256=sha(out), stderr_sha256=sha(err))
    write(evidence / (label + '.json'), record)
    guard()
    return {'check': label, 'exit_code': record['exit_code'], 'record': str((evidence / (label + '.json')).relative_to(P))}
