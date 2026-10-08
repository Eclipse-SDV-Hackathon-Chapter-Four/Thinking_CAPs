#!/usr/bin/env python3
"""Create an offline historical replay of a verified real CARLA campaign."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from urllib.parse import quote

REPO = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render(campaign, output):
    campaign, output = campaign.resolve(), output.resolve()
    native = campaign / 'native'
    results = json.loads((campaign / 'results.json').read_text())
    checks = json.loads((native / 'results.json').read_text())
    manifest = json.loads((native / 'manifest.json').read_text())
    required = {'real-carla-moving-actor', 'real-carla-native-actuation-correlation', 'cleanup-owned-carla'}
    passed = {row['id'] for row in checks['checks'] if row['status'] == 'passed'}
    if results['status'] != 'passed' or checks['status'] != 'passed' or not required <= passed or manifest.get('CARLA', {}).get('status') != 'real' or any(c['status'] != 'passed' for c in checks['checks']) or any(c['status'] in ('failed', 'blocked') for c in results['scenarios']):
        raise ValueError('Historical physical replay requires a passed real CARLA campaign with native actuation and cleanup evidence')
    expected = json.loads((campaign / 'manifest.json').read_text())['native_evidence_sha256']
    for name in ('results.json', 'manifest.json', 'carla-samples.json', 'events.json', 'requests.json', 'carla-control-return.json'):
        if expected.get(name) != sha(native / name):
            raise ValueError('Recorded source hash mismatch: ' + name)
    samples = json.loads((native / 'carla-samples.json').read_text())
    events = json.loads((native / 'events.json').read_text())
    requests = json.loads((native / 'requests.json').read_text())
    observations, faults = [], []
    for row in requests:
        target = observations if row['uri'].endswith('/cc.observation') else faults if row['uri'].endswith('/cc.fault-history') else None
        if target is None:
            continue
        value = row['response'].get('data', {}).get('value')
        if not value:
            continue
        target.append({'time_ns': row['observed_at_monotonic_ns'], 'value': value})
    if not samples or not observations or not faults:
        raise ValueError('Missing actual physical, receiver or fault observations')
    origin = min([s['observed_at_monotonic_ns'] for s in samples] + [e['monotonic_ns'] for e in events] +
                 [r['time_ns'] for r in observations + faults])
    sources = [campaign / 'results.json', native / 'results.json', native / 'manifest.json',
               native / 'carla-samples.json', native / 'events.json', native / 'requests.json', native / 'carla-control-return.json']
    provenance = [{'name': str(path.relative_to(campaign)), 'sha256': sha(path),
                   'href': quote(os.path.relpath(path, output), safe='/')} for path in sources]
    data = {'classification': 'Historical preparation recording; not live diagnostics',
            'run_id': results['run_id'], 'origin_ns': origin, 'results': results, 'identity': manifest['CARLA'],
            'samples': samples, 'events': events, 'observations': observations, 'faults': faults,
            'correlation': json.loads((native / 'carla-control-return.json').read_text()), 'sources': provenance}
    template = REPO / 'templates/campaign_replay.html'
    serialized = json.dumps(data, separators=(',', ':'), allow_nan=False).replace('<', '\\u003c')
    html = template.read_text().replace('__RECORDED_DATA__', serialized)
    output.mkdir(parents=True, exist_ok=False)
    (output / 'index.html').write_text(html)
    record = {'schema_version': 1, 'work_classification': 'prepared', 'mode': data['classification'],
              'source_run_id': results['run_id'], 'source_campaign_status': results['status'],
              'inputs': provenance, 'producer_sha256': sha(Path(__file__)), 'template_sha256': sha(template),
              'html_sha256': sha(output / 'index.html'), 'limits': ['Saved samples only; no current-health or runtime-verdict inference',
              'No AAOS/FOTA or independent-person reproduction', 'HTTP gaps preserved; no native E2E sample identifier']}
    (output / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--campaign', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    render(args.campaign, args.output)
    print(json.dumps({'output': str(args.output), 'classification': 'historical; not live'}))


if __name__ == '__main__':
    main()
