"""Read-only native terminal/event collector; never creates, starts or repairs a run."""
from pathlib import Path
import json
import time
import urllib.request
from storage import validate_run_root

ROOT = Path(__file__).parent
validate_run_root(ROOT)
binding = json.loads((ROOT / 'server-binding.json').read_bytes())
token = json.loads((Path(binding['private_state']) / 'operator-secret.json').read_bytes())['token']
rid = json.loads((ROOT / 'queue.json').read_bytes())['jobs'][0]['run_id']
dest = ROOT / 'native-runtime' / rid
dest.mkdir(parents=True, exist_ok=False)
def api(path):
    validate_run_root(ROOT)
    req = urllib.request.Request(binding['url'] + '/api/v1' + path,
                                  headers={'Authorization': 'Bearer ' + token})
    with urllib.request.urlopen(req, timeout=30) as stream:
        return json.load(stream)
def save(name, value):
    (dest / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')
deadline = time.monotonic() + 4000
while True:
    projection = api('/runs/' + rid)
    status = projection['lifecycle']['status']['kind']
    if status in ['succeeded', 'failed', 'dead', 'cancelled']:
        break
    assert time.monotonic() < deadline, 'Observer deadline; inspect native state without retrying starts'
    time.sleep(20)
save('final-projection.json', projection)
state = api('/runs/' + rid + '/state')
save('final-state.json', state)
after = count = 0
terminal = False
with (dest / 'events.jsonl').open('x') as stream:
    while True:
        page = api('/runs/' + rid + f'/events?limit=1000&after={after}')
        for item in page['data']:
            assert item['stream_seq'] > after
            after = item['stream_seq']; count += 1
            rec = item.get('item', {}).get('record', {})
            terminal |= rec.get('kind') == 'run.lifecycle' and rec.get('transition') in ['succeeded', 'failed', 'dead']
            stream.write(json.dumps(item, sort_keys=True) + '\n')
        if not page['meta']['has_more']:
            break
save('event-collection.json', {'records': count, 'last_stream_seq': after,
                             'has_more': False, 'terminal_lifecycle_present': terminal})
assert terminal and state['conclusion'] is not None
print(json.dumps({'run_id': rid, 'terminal_status': status, 'events_retained': count,
                  'note': 'Workflow status does not establish native verification success'}))
