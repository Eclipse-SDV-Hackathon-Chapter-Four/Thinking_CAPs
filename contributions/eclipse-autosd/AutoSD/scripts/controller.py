#!/usr/bin/env python3
"""Run ThreadX and retain its actual JSON observations for native OpenSOVD."""
import json
import os
from pathlib import Path
import signal
import subprocess
import time

STATE = Path('/state/lighting.json')


def main():
    previous = json.loads(STATE.read_text()) if STATE.exists() else {}
    history = previous.get('fault_history', [])
    active = previous.get('active_faults', [])
    view = {'schema_version': 1, 'source': 'actual-threadx-linux-port',
            'boot_id': Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
            'controller_state': 'starting', 'lights': None, 'identity': None,
            'active_faults': active, 'fault_history': history}

    def fault(code, enabled):
        if enabled == (code in active):
            return
        if enabled:
            active.append(code)
        else:
            active.remove(code)
        history.append({'code': code, 'active': enabled, 'time_unix_ns': time.time_ns(),
                        'source': 'integration-owned-observation-journal'})
        del history[:-128]

    def save():
        view['observed_at_monotonic_ns'] = time.monotonic_ns()
        temp = STATE.with_suffix('.tmp')
        temp.write_text(json.dumps(view) + '\n')
        temp.replace(STATE)

    args = ['threadx-zonal-lights', '--interface', os.environ['CAN_INTERFACE'],
            '--timeout-ms', os.environ.get('INPUT_TIMEOUT_MS', '0')]
    child = subprocess.Popen(args, stdout=subprocess.PIPE, text=True, bufsize=1)
    def stop(_signum, _frame):
        if child.poll() is None:
            child.terminate()
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    save()
    for line in child.stdout:
        print(line.rstrip(), flush=True)
        try:
            row = json.loads(line)
        except ValueError:
            continue
        event = row.get('event')
        if event == 'started':
            view['identity'] = row
            view['controller_state'] = 'running'
            # ThreadX emits started only after its startup OFF frame succeeds.
            view['lights'] = {'reverse': False, 'brake': False, 'stale': False}
            fault('controller_unavailable', False)
        elif event in ('lights', 'input_timeout'):
            view['lights'] = {k: row[k] for k in ('reverse', 'brake', 'stale')}
            fault('can_input_timeout', row['stale'])
        elif event == 'heartbeat':
            view['heartbeat'] = row
            fault('can_input_timeout', row.get('stale', False))
        elif event == 'stopped':
            view['controller_state'] = 'stopped'
            # Shutdown sends actual OFF over CAN before the kernel returns.
            view['lights'] = {'reverse': False, 'brake': False, 'stale': False}
        save()
    status = child.wait()
    view['controller_state'] = 'stopped' if status == 0 else 'failed'
    view['exit_code'] = status
    fault('controller_unavailable', True)
    save()
    return status


if __name__ == '__main__':
    raise SystemExit(main())
