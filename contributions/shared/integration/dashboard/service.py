"""Local observational dashboard. Vehicle verdicts remain owned by the native runner."""
import copy
import datetime
import fcntl
import hashlib
import http.server
import json
import os
from pathlib import Path
import re
import secrets
import signal
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import uuid

REPO = Path(__file__).resolve().parents[4]
WEB = Path(__file__).parent / 'web'
SCENARIOS = {'core': 'Fixture vehicle inputs; real receiver/openDuT/native faults',
             'cleanup-failure': 'Deliberate failure fixture; actual owned cleanup acceptance',
             'carla': 'Physical CARLA; existing X-Verse/VCU; harness operator commands'}
ALLOWED = {'results.json', 'manifest.json', 'junit.xml', 'summary.md', 'timeline.jsonl',
           'native/results.json', 'native/manifest.json', 'native/events.json',
           'native/requests.json', 'native/return-events.json', 'native/packets.json'}
ID = re.compile(r'^[a-zA-Z0-9_-]{1,80}$')


def utc():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path, fallback=None):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return fallback


def atomic(path, value):
    temporary = Path(path).with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.chmod(0o600)
    temporary.replace(path)


class Artifacts:
    def __init__(self, directory, hashes):
        self.directory = Path(directory).resolve()
        self.hashes = dict(hashes)

    def bytes(self, name):
        if name not in ALLOWED or name not in self.hashes:
            raise ValueError('artifact is not registered for download')
        path = self.directory / name
        if any(p.is_symlink() for p in (path, *path.parents) if p != self.directory.parent):
            raise ValueError('symlink artifact is not admitted')
        if not path.resolve().is_relative_to(self.directory):
            raise ValueError('artifact escapes registered run')
        return path.read_bytes()

    def read(self, name):
        data = self.bytes(name)
        if sha(data) != self.hashes[name]:
            raise ValueError('artifact integrity mismatch')
        return data

    def inventory(self):
        rows = {}
        for name, expected in self.hashes.items():
            if name not in ALLOWED:
                continue
            try:
                data = self.bytes(name)
                rows[name] = {'integrity': 'verified' if sha(data) == expected else 'mismatch',
                              'sha256': expected, 'size': len(data)}
            except FileNotFoundError:
                rows[name] = {'integrity': 'missing', 'sha256': expected}
            except (OSError, ValueError) as error:
                rows[name] = {'integrity': 'unavailable', 'reason': str(error), 'sha256': expected}
        return rows


def freeze(directory):
    directory = Path(directory)
    return {name: sha((directory / name).read_bytes()) for name in sorted(ALLOWED)
            if (directory / name).is_file() and not (directory / name).is_symlink()}


class Snapshot:
    def __init__(self, max_age=3):
        self.lock = threading.Lock()
        self.value = None
        self.acquired = None
        self.acquired_utc = None
        self.error = 'No observation acquired'
        self.uri = None
        self.max_age = max_age

    def success(self, value, uri):
        with self.lock:
            self.value = value
            self.uri = uri
            self.acquired = time.monotonic()
            self.acquired_utc = utc()
            self.error = None

    def failure(self, error):
        with self.lock:
            self.error = str(error)

    def view(self):
        with self.lock:
            age = None if self.acquired is None else time.monotonic() - self.acquired
            available = self.error is None and age is not None and age <= self.max_age
            return {'availability': 'available' if available else 'unavailable',
                    'value': copy.deepcopy(self.value), 'acquired_utc': self.acquired_utc,
                    'acquired_age_seconds': age, 'last_observed_only': not available,
                    'uri': self.uri, 'error': self.error if self.error else ('Snapshot expired' if not available else None)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('diagnostic redirects are not admitted')


class Diagnosis:
    def __init__(self, base):
        self.base = base.rstrip('/')
        self.parsed = urllib.parse.urlsplit(self.base)
        if self.parsed.scheme not in ('http', 'https') or not self.parsed.hostname or self.parsed.username:
            raise ValueError('diagnostic base must be a configured HTTP origin without credentials')
        self.observation = Snapshot()
        self.history = Snapshot()
        self.links = None
        self.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())

    def fetch(self, uri):
        parsed = urllib.parse.urlsplit(uri)
        if ((parsed.scheme, parsed.netloc) != (self.parsed.scheme, self.parsed.netloc)
                or not parsed.path.startswith(self.parsed.path.rstrip('/') + '/')
                or '..' in urllib.parse.unquote(parsed.path).split('/') or parsed.username):
            raise ValueError('diagnostic resource escapes configured origin/path')
        with self.opener.open(uri, timeout=.65) as response:
            raw = response.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError('diagnostic response exceeds bound')
        result = json.loads(raw)
        if not isinstance(result, dict):
            raise ValueError('diagnostic response must be an object')
        return result

    def poll(self):
        try:
            if self.links is None:
                root = self.fetch(self.base + '/v1')
                apps = self.fetch(root['apps'])
                target = next(item for item in apps['items'] if item['id'] == 'cruise-control')
                app = self.fetch(target['href'])
                collection = app['data']
                resources = self.fetch(collection)['items']
                self.links = {item['id']: collection + '/' + urllib.parse.quote(item['id'], safe='') for item in resources}
            value = self.fetch(self.links['cc.observation'])['data']['value']
            if not isinstance(value, dict) or value.get('freshness_state') not in ('fresh', 'stale', 'unknown'):
                raise ValueError('unsupported diagnostic observation')
            self.observation.success(value, self.links['cc.observation'])
        except (OSError, ValueError, KeyError, TypeError, StopIteration) as error:
            self.observation.failure(error)
            self.links = None
        try:
            if not self.links or 'cc.fault-history' not in self.links:
                raise ValueError('fault-history resource unavailable')
            self.history.success(self.fetch(self.links['cc.fault-history'])['data']['value'], self.links['cc.fault-history'])
        except (OSError, ValueError, KeyError, TypeError) as error:
            self.history.failure(error)

    def snapshot(self):
        return {'target': {'id': 'cruise-control', 'name': 'Cruise Control', 'base': self.base},
                'observation': self.observation.view(), 'history': self.history.view()}


def cleanup_verdict(native, scenario='core', blocked=False):
    if blocked and native is None:
        return {'status': 'not_required', 'reason': 'Runner blocked before native execution'}
    if not isinstance(native, dict):
        return {'status': 'unknown', 'reason': 'Native cleanup evidence is missing'}
    checks = native.get('checks', [])
    selected = [c for c in checks if c.get('id', '').startswith(('restore-', 'cleanup-', 'stop-capture-', 'read-capture-'))]
    failed = [c for c in selected if c.get('status') != 'passed']
    if failed:
        return {'status': 'failed', 'checks': selected, 'reason': 'Native cleanup/restoration did not pass'}
    by_id = {c.get('id'): c.get('status') for c in selected}
    missing = [key for key in ('restore-tunnel', 'restore-private-directory-owner') if by_id.get(key) != 'passed']
    contract = native.get('cleanup_contract')
    if contract is not None:
        expected = contract.get('application_checks') if isinstance(contract, dict) else None
        if (not isinstance(contract, dict) or contract.get('schema_version') != 1
                or not isinstance(expected, list)
                or not all(isinstance(key, str) and key.startswith('cleanup-sdv-net-') for key in expected)
                or len(expected) != len(set(expected))):
            missing.append('valid application cleanup contract')
        else:
            missing.extend(key for key in expected if by_id.get(key) != 'passed')
            actual = {key for key in by_id if key.startswith('cleanup-sdv-net-')}
            if actual != set(expected):
                missing.append('application cleanup inventory mismatch')
    elif sum(c.get('id', '').startswith('cleanup-') for c in selected) < 3:
        # Preserve the stricter contract for older evidence without an inventory.
        missing.append('cleanup- contract count 3')
    for prefix, count in (('stop-capture-', 4), ('read-capture-', 4)):
        if sum(c.get('id', '').startswith(prefix) for c in selected) < count:
            missing.append(prefix + ' contract count ' + str(count))
    if scenario == 'carla' and by_id.get('cleanup-owned-carla') != 'passed':
        missing.append('cleanup-owned-carla')
    return {'status': 'unknown' if missing else 'passed', 'checks': selected,
            'reason': 'Missing required cleanup evidence: ' + ', '.join(missing) if missing else 'Native owned cleanup acknowledged'}


def pid_identity(pid):
    try:
        stat = Path('/proc/' + str(pid) + '/stat').read_text().rsplit(')', 1)[1].split()
        return Path('/proc/sys/kernel/random/boot_id').read_text().strip() + ':' + str(pid) + ':' + stat[19]
    except OSError:
        return None


class Coordinator:
    def __init__(self, state, inputs, python, command_factory=None):
        self.state = Path(state).resolve()
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        if self.state.stat().st_uid != os.getuid():
            raise ValueError('Dashboard private state belongs to another user')
        self.state.chmod(0o700)
        self.file_lock = (self.state / 'server.lock').open('a')
        try:
            fcntl.flock(self.file_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            self.file_lock.close()
            raise RuntimeError('Another coordinator owns this dashboard state')
        self.inputs = Path(inputs).resolve()
        self.python = str(python)
        self.command_factory = command_factory
        self.lock = threading.RLock()
        ledger_path = self.state / 'ledger.json'
        self.ledger = load(ledger_path) if ledger_path.exists() else {'active': None, 'runs': {}}
        if (not isinstance(self.ledger, dict) or not isinstance(self.ledger.get('runs'), dict)
                or 'active' not in self.ledger or
                (self.ledger['active'] is not None and self.ledger['active'] not in self.ledger['runs'])):
            self.file_lock.close()
            raise RuntimeError('Invalid persisted ledger; admission requires ownership reconciliation')
        for identity, record in self.ledger['runs'].items():
            if (not isinstance(record, dict) or not ID.fullmatch(identity)
                    or record.get('id') != identity or 'state' not in record
                    or Path(record.get('output', '')).resolve() != self.state / 'runs' / identity):
                self.file_lock.close()
                raise RuntimeError('Invalid persisted run; admission requires ownership reconciliation')
        self.process = None
        self.worker = None
        self.closing = False
        for record in self.ledger['runs'].values():
            if record['state'] in ('queued', 'running', 'cancelling'):
                record['state'] = 'unknown'
                record['cleanup'] = {'status': 'unknown', 'reason': 'Previous coordinator did not acknowledge termination/cleanup'}
        self.save()

    def save(self):
        atomic(self.state / 'ledger.json', self.ledger)

    def snapshot(self):
        with self.lock:
            return copy.deepcopy(self.ledger)

    def start(self, scenario):
        if scenario not in SCENARIOS:
            raise ValueError('Unsupported campaign')
        with self.lock:
            if self.closing:
                raise RuntimeError('Coordinator is shutting down')
            if self.ledger['active']:
                raise RuntimeError('Bench has an active run or unresolved cleanup')
            identity = uuid.uuid4().hex
            record = {'id': identity, 'scenario': scenario, 'mode': SCENARIOS[scenario], 'state': 'queued',
                      'created_utc': utc(), 'cancel_requested': False, 'cleanup': {'status': 'pending'},
                      'output': str(self.state / 'runs' / identity), 'hashes': {}, 'results': None}
            self.ledger['runs'][identity] = record
            self.ledger['active'] = identity
            self.save()
            self.worker = threading.Thread(target=self.execute, args=(identity,), daemon=True)
            self.worker.start()
            return copy.deepcopy(record)

    def execute(self, identity):
        record = self.ledger['runs'][identity]
        output = Path(record['output'])
        output.parent.mkdir(exist_ok=True)
        code, error, spawned = None, None, False
        try:
            command = (self.command_factory(record) if self.command_factory else
                       [self.python, str(REPO / 'contributions/shared/scripts/run_campaign.py'), '--config', str(self.inputs),
                        '--scenario', record['scenario'], '--output', str(output), '--run-id', identity])
            with (self.state / (identity + '.log')).open('wb') as log:
                with self.lock:
                    if record['cancel_requested']:
                        return
                    self.process = subprocess.Popen(command, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
                    spawned = True
                    record.update(pid=self.process.pid, pid_identity=pid_identity(self.process.pid), state='running')
                    self.save()
                    if record['cancel_requested']:
                        self.process.send_signal(signal.SIGTERM)
                        record['state'] = 'cancelling'
                        self.save()
                code = self.process.wait(timeout=360)
        except (OSError, subprocess.SubprocessError) as exception:
            error = str(exception)
            with self.lock:
                if self.process and self.process.poll() is None:
                    self.process.send_signal(signal.SIGTERM)
            if self.process:
                try:
                    code = self.process.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    # Owned group only. A kill cannot establish native container cleanup.
                    os.killpg(self.process.pid, signal.SIGKILL)
                    code = self.process.wait(timeout=5)
                    error += '; forced termination; owned-resource reconciliation required'
        finally:
            with self.lock:
                results = load(output / 'results.json')
                native = load(output / 'native/results.json')
                blocked = bool(results and results.get('status') == 'blocked' and
                               all(c.get('id') == 'preflight' for c in results.get('scenarios', [])))
                cleanup = cleanup_verdict(native, record['scenario'], blocked)
                if not spawned:
                    cleanup = {'status': 'not_required', 'reason': 'No runner process was launched'}
                elif error:
                    cleanup = {'status': 'unknown', 'reason': error}
                if record.get('forced_termination'):
                    cleanup = {'status': 'unknown', 'reason': 'Owned runner group forcibly terminated; native resource reconciliation required'}
                state = 'cancelled' if record['cancel_requested'] else (results or {}).get('status', 'failed' if spawned else 'blocked')
                if state not in ('passed', 'failed', 'blocked', 'cancelled'):
                    state = 'failed'
                if results and results.get('run_id') != identity:
                    state = 'failed'
                    error = 'Runner identity does not match coordinator'
                    cleanup = {'status': 'unknown', 'reason': error}
                if state == 'passed' and (code != 0 or cleanup['status'] != 'passed'):
                    state = 'failed'
                    error = 'Process/cleanup cannot substantiate successful execution'
                record.update(state=state, finished_utc=utc(), exit_code=code, results=results,
                              manifest=load(output / 'manifest.json'), cleanup=cleanup, error=error,
                              hashes=freeze(output) if output.exists() else {})
                if cleanup['status'] in ('passed', 'not_required'):
                    self.ledger['active'] = None
                self.process = None
                self.save()

    def cancel(self, identity):
        with self.lock:
            record = self.ledger['runs'].get(identity)
            if record is None:
                raise KeyError(identity)
            if record['state'] not in ('queued', 'running', 'cancelling'):
                return copy.deepcopy(record)
            if not record['cancel_requested']:
                record['cancel_requested'] = True
                record['state'] = 'cancelling'
                self.save()
                if self.process and self.process.poll() is None and pid_identity(self.process.pid) == record.get('pid_identity'):
                    self.process.send_signal(signal.SIGTERM)
            return copy.deepcopy(record)

    def close(self):
        with self.lock:
            self.closing = True
            identity = self.ledger['active']
            if identity:
                self.cancel(identity)
        if self.worker:
            self.worker.join(timeout=70)
            if self.worker.is_alive():
                with self.lock:
                    if self.process and self.process.poll() is None:
                        record = self.ledger['runs'][identity]
                        record['forced_termination'] = True
                        self.save()
                        if pid_identity(self.process.pid) == record.get('pid_identity'):
                            os.killpg(self.process.pid, signal.SIGKILL)
                self.worker.join(timeout=6)
                if self.worker.is_alive():
                    raise RuntimeError('Owned runner finalization still pending; coordinator lock retained')
        self.file_lock.close()


def command(args, timeout=4):
    result = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError((result.stderr or result.stdout)[-600:])
    return result.stdout


def observe_bench(inputs):
    config = load(inputs)
    if not isinstance(config, dict) or not config.get('state'):
        raise ValueError('Campaign inputs unavailable')
    state = load(Path(config['state']) / 'deployment.json')
    if not state or state.get('phase') != 'deployed':
        raise ValueError('Configured bench is not deployed')
    label = 'sdv.opendut.run'
    project = state['project']
    result = {'run_id': state['run_id'], 'phase': state['phase'], 'profile': 'local TLS; VPN/OIDC disabled',
              'release': state['pins']['release'], 'interfaces': {}, 'peers': [], 'devices': [], 'clusters': []}
    for suffix in ('a', 'b', 'carl'):
        rows = json.loads(command(['docker', 'inspect', project + '-' + suffix]))
        if rows[0]['Config']['Labels'].get(label) != state['run_id'] or not rows[0]['State']['Running']:
            raise ValueError('Configured openDuT resource not owned/running: ' + suffix)
    for key, collection in (('peers', 'peers'), ('devices', 'devices'), ('clusters', 'cluster-deployments')):
        result[key] = json.loads(command(['docker', 'exec', project + '-a', 'timeout', '2',
                                '/cleo/opendut-cleo', 'list', '--output', 'json', collection], timeout=4))
    for suffix in ('a', 'b'):
        result['interfaces'][suffix] = json.loads(command(['docker', 'exec', project + '-' + suffix,
                                                          'ip', '-d', '-j', 'link', 'show']))
    return result


class Dashboard:
    def __init__(self, config):
        self.config = config
        self.inputs = Path(config['campaign_config']).resolve()
        self.manager = Coordinator(config['state_dir'], self.inputs, config.get('python', '/usr/bin/python3'))
        self.bench_lock = None
        try:
            inputs = load(self.inputs, {})
            bench_state = Path(inputs.get('state', '/nonexistent'))
            if bench_state.is_dir():
                self.bench_lock = (bench_state / 'dashboard.lock').open('a')
                fcntl.flock(self.bench_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            self.diagnosis = Diagnosis(config.get('diagnostic_base', 'http://172.30.77.12:7691/sovd'))
        except Exception:
            self.manager.close()
            if self.bench_lock: self.bench_lock.close()
            raise
        self.bench = Snapshot(max_age=25)
        self.stop = threading.Event()
        self.token = secrets.token_urlsafe(32)
        self.history = {}
        for item in config.get('historical', []):
            if not ID.fullmatch(item['id']) or item['id'] in self.history:
                raise ValueError('Historical IDs must be unique simple names')
            store = Artifacts(item['directory'], item['hashes'])
            initial = {}
            for name in ('results.json', 'manifest.json'):
                try: initial[name] = json.loads(store.read(name))
                except (OSError, ValueError): initial[name] = None
            self.history[item['id']] = dict(item, initial=initial)
        self.threads = [threading.Thread(target=self.loop, args=(self.diagnosis.poll, .5), daemon=True),
                        threading.Thread(target=self.loop, args=(self.poll_bench, 3), daemon=True)]
        for worker in self.threads: worker.start()

    def loop(self, function, interval):
        while not self.stop.is_set():
            function()
            self.stop.wait(interval)

    def poll_bench(self):
        try:
            self.bench.success(observe_bench(self.inputs), 'configured openDuT CLEO management')
        except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError) as error:
            self.bench.failure(error)

    def prerequisites(self, scenario):
        inputs = load(self.inputs)
        missing = []
        if not isinstance(inputs, dict):
            return ['Campaign input file unavailable or invalid']
        for key in ('binary', 'score_source', 'baseline_source', 'bridge_source'):
            if not inputs.get(key) or not Path(inputs[key]).exists():
                missing.append(key + ' unavailable')
        state = load(Path(inputs.get('state', '/nonexistent')) / 'deployment.json', {})
        if state.get('phase') != 'deployed': missing.append('openDuT bench is not deployed')
        if self.bench.view()['availability'] != 'available': missing.append('openDuT management not currently observed')
        if scenario == 'carla' and not inputs.get('carla'): missing.append('CARLA inputs unavailable')
        return missing

    def state(self):
        ledger = self.manager.snapshot()
        runs = [self.summary(record) for record in reversed(list(ledger['runs'].values()))]
        runs += [self.summary(self.historical_record(identity)) for identity in self.history]
        active = ledger['runs'].get(ledger['active']) if ledger['active'] else None
        return {'token': self.token, 'diagnosis': self.diagnosis.snapshot(), 'bench': self.bench.view(),
                'active_run': self.summary(active) if active else None, 'runs': runs[:100],
                'campaigns': [{'id': key, 'mode': mode, 'missing_prerequisites': self.prerequisites(key)} for key, mode in SCENARIOS.items()],
                'capabilities': {'executor': 'Project campaign runner on openDuT-managed bench',
                                 'native_faults': 'Unavailable; native fault history uses OpenSOVD App data',
                                 'control_output': 'Unavailable in current observation contract',
                                 'work_classification': 'Prepared work', 'reproduction': 'Second-contributor run deferred by user; unattested'}}

    def historical_record(self, identity):
        item = self.history[identity]
        return {'id': identity, 'label': item.get('label', identity), 'state': 'historical',
                'mode': (item['initial']['manifest.json'] or {}).get('mode', 'Unverified historical evidence'),
                'results': item['initial']['results.json'], 'manifest': item['initial']['manifest.json'],
                'hashes': item['hashes'], 'output': item['directory'], 'historical': True,
                'replay': item.get('replay'), 'cleanup': {'status': 'historical; inspect original assertions'}}

    def record(self, identity):
        ledger = self.manager.snapshot()
        if identity in ledger['runs']: return ledger['runs'][identity]
        if identity in self.history: return self.historical_record(identity)
        raise KeyError(identity)

    def summary(self, record):
        return {key: copy.deepcopy(record.get(key)) for key in ('id', 'label', 'state', 'mode', 'scenario',
                'created_utc', 'finished_utc', 'cancel_requested', 'cleanup', 'results', 'error', 'historical')}

    def detail(self, identity):
        record = self.record(identity)
        store = Artifacts(record['output'], record.get('hashes', {}))
        view = self.summary(record)
        view['manifest'] = record.get('manifest')
        view['artifacts'] = store.inventory()
        view['timeline'] = []
        view['observations'] = []
        view['progress'] = []
        if record['state'] in ('running', 'cancelling', 'queued'):
            path = Path(record['output']) / 'native/events-live.jsonl'
            try:
                for line in path.read_text()[-20000:].splitlines()[-100:]:
                    try: view['progress'].append(json.loads(line))
                    except ValueError: pass
            except OSError: pass
        for name, target in (('timeline.jsonl', 'timeline'), ('native/requests.json', 'observations')):
            if name not in store.hashes: continue
            try:
                raw = store.read(name)
                values = [json.loads(line) for line in raw.splitlines()] if name.endswith('.jsonl') else json.loads(raw)
                view[target] = values[-100:]
            except (OSError, ValueError): pass
        if record.get('replay'): view['replay'] = True
        return view

    def artifact(self, identity, name):
        record = self.record(identity)
        return Artifacts(record['output'], record.get('hashes', {})).read(name)

    def replay(self, identity):
        record = self.record(identity)
        replay = record.get('replay')
        if not replay: raise KeyError(identity)
        path = Path(replay['path'])
        if path.is_symlink(): raise ValueError('Replay symlink not admitted')
        content = path.read_bytes()
        if sha(content) != replay['sha256']: raise ValueError('Replay integrity mismatch')
        return content

    def close(self):
        self.stop.set()
        self.manager.close()
        for worker in self.threads: worker.join(timeout=1)
        if self.bench_lock: self.bench_lock.close()


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Query/body/token are never logged.
        pass

    def reply(self, status, body, mime='application/json', attachment=None, replay=False):
        if not isinstance(body, bytes): body = json.dumps(body).encode()
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "sandbox allow-scripts; default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:" if replay else "default-src 'self'; script-src 'self'; style-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        if attachment: self.send_header('Content-Disposition', 'attachment; filename="' + Path(attachment).name + '"')
        self.end_headers()
        try: self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError): pass

    def valid_host(self):
        return self.headers.get('Host') == '127.0.0.1:' + str(self.server.server_port)

    def do_GET(self):
        if not self.valid_host(): return self.reply(403, {'error': 'Host rejected'})
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        app = self.server.app
        try:
            if path == '/api/state': return self.reply(200, app.state())
            if path in ('/', '/app.js', '/style.css'):
                name, mime = {'/': ('index.html', 'text/html; charset=utf-8'), '/app.js': ('app.js', 'text/javascript'), '/style.css': ('style.css', 'text/css')}[path]
                return self.reply(200, (WEB / name).read_bytes(), mime)
            parts = path.split('/')
            if len(parts) >= 4 and parts[1:3] == ['api', 'runs'] and ID.fullmatch(parts[3]):
                identity = parts[3]
                if len(parts) == 4: return self.reply(200, app.detail(identity))
                if len(parts) > 5 and parts[4] == 'artifacts':
                    name = '/'.join(parts[5:])
                    return self.reply(200, app.artifact(identity, name), 'application/octet-stream', attachment=name)
                if len(parts) == 5 and parts[4] == 'replay': return self.reply(200, app.replay(identity), 'text/html', replay=True)
            return self.reply(404, {'error': 'Unknown resource'})
        except (KeyError, FileNotFoundError): return self.reply(404, {'error': 'Resource unavailable'})
        except (ValueError, OSError) as error: return self.reply(409, {'error': str(error)})

    def do_POST(self):
        app = self.server.app
        origin = 'http://127.0.0.1:' + str(self.server.server_port)
        if (not self.valid_host() or self.headers.get('Origin') != origin or
                not secrets.compare_digest(self.headers.get('X-SDV-Token', ''), app.token)):
            return self.reply(403, {'error': 'Mutation requires same-origin session token'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 <= length <= 2048: raise ValueError('Request body too large')
            body = json.loads(self.rfile.read(length) or '{}')
            if not isinstance(body, dict): raise ValueError('Expected JSON object')
            path = urllib.parse.urlsplit(self.path).path
            if path == '/api/runs':
                if set(body) != {'scenario'}: raise ValueError('Only a fixed scenario is accepted')
                return self.reply(202, app.manager.start(body['scenario']))
            parts = path.split('/')
            if len(parts) == 5 and parts[1:3] == ['api', 'runs'] and parts[4] == 'cancel' and ID.fullmatch(parts[3]):
                if body: raise ValueError('Cancellation has no command arguments')
                return self.reply(202, app.manager.cancel(parts[3]))
            return self.reply(404, {'error': 'Unknown action'})
        except KeyError: return self.reply(404, {'error': 'Unknown run'})
        except (ValueError, TypeError) as error: return self.reply(400, {'error': str(error)})
        except (OSError, RuntimeError) as error: return self.reply(409, {'error': str(error)})


def server(app, port):
    instance = http.server.ThreadingHTTPServer(('127.0.0.1', port), Handler)
    instance.app = app
    return instance
