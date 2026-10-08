#!/usr/bin/env python3
"""Exercise the deployed controller through the opposite vxcan endpoint."""
import argparse
import json
from pathlib import Path
import time
import can


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--interface', default='avcan1')
    p.add_argument('--timeout', action='store_true', help='Controller must currently use --timeout-ms 200')
    a = p.parse_args()
    checks = []
    bus = can.Bus(interface='socketcan', channel=a.interface,
                  can_filters=[{'can_id': 0x1F4, 'can_mask': 0x7FF, 'extended': False}])
    def request(status):
        bus.send(can.Message(arbitration_id=0x1F1, is_extended_id=False, data=bytes([status]) + bytes([255]) * 7))
    def response(state):
        m = bus.recv(3)
        assert m is not None and m.dlc == 8 and bytes(m.data) == bytes([state]) + bytes(7), str(m)
    def check(name, value=True):
        checks.append({'id': name, 'status': 'passed' if value else 'failed'})
        assert value, name
    def observed(predicate):
        end = time.monotonic() + 2
        while time.monotonic() < end:
            value = json.loads(Path('/state/lighting.json').read_text())
            if predicate(value): return value
            time.sleep(.01)
        raise AssertionError('Controller observation did not arrive')
    try:
        if a.timeout:
            request(6)
            response(3)
            start = time.monotonic()
            response(0)
            elapsed = time.monotonic() - start
            check('guest-optional-200ms-input-timeout', .12 <= elapsed < 1)
            view = observed(lambda v: 'can_input_timeout' in v['active_faults'])
            check('native-journal-actual-can-timeout-activation', view['lights']['stale'])
            request(2)
            response(1)
            view = observed(lambda v: 'can_input_timeout' not in v['active_faults'])
            check('native-journal-can-timeout-recovery-retains-history',
                  any(x['code'] == 'can_input_timeout' and x['active'] for x in view['fault_history']))
        else:
            for status in range(256):
                request(status)
                response((status >> 1) & 3)
            check('autosd-socketcan-all-256-status-values')
            for m in [can.Message(arbitration_id=0x1F1, data=[6], is_extended_id=False),
                      can.Message(arbitration_id=0x1F1, data=bytes(8), is_extended_id=True),
                      can.Message(arbitration_id=0x1F1, dlc=8, is_remote_frame=True, is_extended_id=False),
                      can.Message(arbitration_id=0x1F2, data=bytes(8), is_extended_id=False)]:
                bus.send(m)
            check('autosd-malformed-frames-ignored', bus.recv(.3) is None)
            start = observed(lambda v: 'heartbeat' in v)
            time.sleep(2.1)
            end = json.loads(Path('/state/lighting.json').read_text())
            check('autosd-default-held-state', end['lights'] == {'reverse': True, 'brake': True, 'stale': False})
            check('autosd-threadx-timer-wall-clock', 100 <= end['heartbeat']['tick'] - start['heartbeat']['tick'] <= 300)
        print(json.dumps({'status': 'passed', 'checks': checks}))
    finally:
        request(0)
        bus.shutdown()


if __name__ == '__main__':
    main()
