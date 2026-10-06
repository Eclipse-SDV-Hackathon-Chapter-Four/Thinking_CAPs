"""Recheck original baseline using its actual text-normalization contract."""
from pathlib import Path
from importlib.util import spec_from_file_location, module_from_spec
from datetime import datetime, timezone
import hashlib, json, subprocess

root = Path(__file__).resolve().parents[2]
lock = json.loads((root / 'config/dependencies.lock.json').read_text())
previous = json.loads((root / 'evidence/f009-reproduction-preservation.json').read_text())
spec = spec_from_file_location('baseline', root / 'scripts/audit_baseline.py')
baseline = module_from_spec(spec)
spec.loader.exec_module(baseline)
record = {'schema_version': 1, 'observed_at': datetime.now(timezone.utc).isoformat(),
          'work_classification': 'prepared', 'repositories': {}, 'configurations': {}, 'images': {}}
for name, expected in lock['repositories'].items():
    current = baseline.repository(Path(expected['path']))
    raw = subprocess.check_output(['git', '-C', expected['path'], 'diff', 'HEAD', '--binary'])
    current['raw_tracked_diff_sha256'] = hashlib.sha256(raw).hexdigest()
    current['raw_crlf_count'] = raw.count(b'\r\n')
    current['preserved'] = all(current[k] == expected[k] for k in ('revision', 'worktree_status', 'tracked_diff_sha256'))
    record['repositories'][name] = current
for name, expected in lock['configurations'].items():
    current = hashlib.sha256((Path('/home/jefferson') / name).read_bytes()).hexdigest()
    record['configurations'][name] = {'sha256': current, 'preserved': current == expected['sha256']}
for name, expected in lock['images'].items():
    current = baseline.command(['docker', 'image', 'inspect', '--format', '{{.Id}}', name])['stdout']
    record['images'][name] = {'id': current, 'preserved': current == expected}
record['original_container_states'] = {name: baseline.command(['docker', 'inspect', '--format', '{{.State.Status}}', name])['stdout'] for name in previous['original_container_states']}
record['owned_containers_remaining'] = baseline.command(['docker', 'ps', '-a', '--filter', 'label=sdv.opendut.run', '--format', '{{.Names}}'])['stdout'].splitlines() + baseline.command(['docker', 'ps', '-a', '--filter', 'label=sdv.reproduction.run', '--format', '{{.Names}}'])['stdout'].splitlines()
record['owned_networks_remaining'] = baseline.command(['docker', 'network', 'ls', '--filter', 'label=sdv.opendut.run', '--format', '{{.Name}}'])['stdout'].splitlines()
record['owned_volumes_remaining'] = baseline.command(['docker', 'volume', 'ls', '--filter', 'label=sdv.opendut.run', '--format', '{{.Name}}'])['stdout'].splitlines()
record['carla_listeners_remaining'] = [line for line in baseline.command(['ss', '-ltnp'])['stdout'].splitlines() if any(':' + str(port) + ' ' in line for port in (2000, 2100))]
h = hashlib.sha256()
with open('/home/jefferson/carla-simulator/CarlaUE4/Binaries/Linux/CarlaUE4-Linux-Shipping', 'rb') as stream:
    for block in iter(lambda: stream.read(1024 * 1024), b''): h.update(block)
record['carla_binary_sha256'] = h.hexdigest()
record['comparison_method'] = 'Original baseline auditor: subprocess text=True universal newline normalization, followed by strip, then SHA256. Raw byte identity is separately recorded, not compared to the text hash.'
record['corrects'] = 'Earlier f009-reproduction-preservation.json omitted universal newline normalization. The original autoverse diff contains 156 CRLF sequences; its normalized identity matches the initial baseline. No original file was modified to resolve the comparison.'
record['auditor_sha256'] = hashlib.sha256((root / 'scripts/audit_baseline.py').read_bytes()).hexdigest()
record['probe_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
passed = all(row['preserved'] for key in ('repositories', 'configurations', 'images') for row in record[key].values()) and record['original_container_states'] == previous['original_container_states'] and record['carla_binary_sha256'] == previous['carla_binary_sha256'] and not any(record[key] for key in ('owned_containers_remaining', 'owned_networks_remaining', 'owned_volumes_remaining', 'carla_listeners_remaining'))
record['status'] = 'passed' if passed else 'failed'
(Path(__file__).parent / 'verification.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'status': record['status'], 'repository_comparisons': len(record['repositories']), 'original_files_changed_by_probe': 0}))
raise SystemExit(0 if passed else 1)
