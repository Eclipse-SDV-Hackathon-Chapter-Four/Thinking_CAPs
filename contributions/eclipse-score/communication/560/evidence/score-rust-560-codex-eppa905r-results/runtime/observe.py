"""Read-only bounded native state/log observation; no dispatch or source writes."""
from pathlib import Path
import json
import urllib.request
from storage import validate_run_root
ROOT = Path(__file__).parent
validate_run_root(ROOT)
binding = json.loads((ROOT / 'server-binding.json').read_bytes())
token = json.loads((Path(binding['private_state']) / 'operator-secret.json').read_bytes())['token']
queue = json.loads((ROOT / 'queue.json').read_bytes())
rid = queue['jobs'][0]['run_id']
req = urllib.request.Request(binding['url'] + '/api/v1/runs/' + rid,
                             headers={'Authorization': 'Bearer ' + token})
with urllib.request.urlopen(req, timeout=15) as stream:
    projection = json.load(stream)
print(json.dumps({'run_id': rid, 'status': projection['lifecycle']['status']}))
n = json.loads((ROOT / 'correction-ledger.json').read_bytes())['codex_used']
native = ROOT / f'attempt-{n}/native'
result = native / 'native-result.json'
if result.exists():
    data = json.loads(result.read_bytes())
    print(json.dumps({'passed': data['passed'], 'completed': [
        {'kind': c['kind'], 'exit_code': c['exit_code'], 'elapsed_seconds': c['elapsed_seconds']}
        for c in data['checks']], 'infrastructure_error': data.get('infrastructure_error')}))
logs = sorted(native.glob('check-*.log'))
if logs:
    log = logs[-1]
    with log.open('rb') as stream:
        stream.seek(max(0, log.stat().st_size - 1200))
        tail = stream.read().decode(errors='replace')
    print(log.name + '\n' + tail)
