#!/usr/bin/env python3
"""Exercise dashboard acquisition against actual native OpenSOVD, with fixture input."""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import socket
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from integration.dashboard.service import Diagnosis


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=False)
    checks=[];snapshots=[];process=None;paused=False
    def check(name,condition):
        checks.append({'id':name,'passed':bool(condition)})
        if not condition:raise AssertionError(name)
    def observed():
        diagnostic.poll();value=diagnostic.snapshot();snapshots.append(value);return value
    try:
        with tempfile.TemporaryDirectory(prefix='sdv-dashboard-native-') as directory:
            unix=Path(directory)/'receiver.sock'
            with socket.socket() as reservation:
                reservation.bind(('127.0.0.1',0));port=reservation.getsockname()[1]
            base=f'http://127.0.0.1:{port}/sovd';diagnostic=Diagnosis(base)
            with (args.output/'native-server.log').open('wb') as log:
                process=subprocess.Popen([str(args.binary.resolve()),'--socket',str(unix),'--listen',f'127.0.0.1:{port}','--base-uri',base,'--speed-timeout-ms','500','--heartbeat-timeout-ms','2000'],stdout=log,stderr=subprocess.STDOUT)
                deadline=time.monotonic()+10
                while observed()['observation']['availability']!='available':
                    if process.poll() is not None or time.monotonic()>deadline:raise RuntimeError('Native OpenSOVD startup timeout')
                    time.sleep(.02)
                value=observed();check('native-startup-unknown',value['observation']['value']['freshness_state']=='unknown')
                check('absent-history-independent-of-observations',value['history']['availability']=='unavailable' and value['observation']['availability']=='available')
                boot=Path('/proc/sys/kernel/random/boot_id').read_text().strip();stamp=time.monotonic_ns()
                observation={'schema_version':1,'source_instance':'cruise-control','source_session':'dashboard-fixture-A','boot_id':boot,'clock_domain':'linux-clock-monotonic','observed_at_monotonic_ns':stamp,'received_at_monotonic_ns':stamp,'last_accepted_at_monotonic_ns':stamp,'vehicle_speed':42.5,'target_speed':45.,'cc_state':'engaged','software_identity':'explicit-dashboard-fixture','sample_id':None,'integrity_result':'not_available','acceptance_kind':'decoded_by_consumer'}
                with socket.socket(socket.AF_UNIX,socket.SOCK_DGRAM) as sender:
                    def publish():sender.sendto(json.dumps(observation).encode(),str(unix));time.sleep(.03)
                    publish();value=observed()['observation']['value']
                    check('native-fresh-provenance-and-units',value['freshness_state']=='fresh' and value['speed_unit']=='km/h' and value['observation']['source_session']=='dashboard-fixture-A')
                    time.sleep(.55);observation['observed_at_monotonic_ns']=time.monotonic_ns();publish();value=observed()['observation']['value']
                    check('native-stale-speed-receiver-available',value['freshness_state']=='stale' and value['receiver_state']=='available' and value['observation']['cc_state']=='engaged')
                    stamp=time.monotonic_ns();observation.update(source_session='dashboard-fixture-B',observed_at_monotonic_ns=stamp,received_at_monotonic_ns=stamp,last_accepted_at_monotonic_ns=stamp,vehicle_speed=21.5);publish();value=observed()['observation']['value']
                    check('new-native-session-replaces-old-snapshot',value['observation']['source_session']=='dashboard-fixture-B' and value['observation']['vehicle_speed']==21.5 and value['freshness_state']=='fresh')
                    process.send_signal(signal.SIGSTOP);paused=True;started=time.monotonic();value=observed()['observation']
                    check('native-service-outage-current-truth-invalidated',value['availability']=='unavailable' and value['last_observed_only'] and value['value']['observation']['source_session']=='dashboard-fixture-B' and time.monotonic()-started<5)
                    process.send_signal(signal.SIGCONT);paused=False
                    stamp=time.monotonic_ns();observation.update(observed_at_monotonic_ns=stamp,received_at_monotonic_ns=stamp,last_accepted_at_monotonic_ns=stamp);publish();value=observed()['observation']
                    check('native-outage-recovery',value['availability']=='available' and not value['last_observed_only'])
            process.send_signal(signal.SIGTERM);process.wait(timeout=5);check('owned-native-socket-cleaned',not unix.exists())
        result={'status':'passed','scope':'Actual native OpenSOVD HTTP and dashboard adapter; explicit fixture observations, not S-CORE/CARLA or native fault acceptance','checks':checks}
    except Exception as error:result={'status':'failed','error':str(error),'checks':checks}
    finally:
        if process and process.poll() is None:
            if paused:process.send_signal(signal.SIGCONT)
            process.terminate()
            try:process.wait(timeout=5)
            except subprocess.TimeoutExpired:process.kill();process.wait(timeout=3)
    result['binary_sha256']=hashlib.sha256(args.binary.read_bytes()).hexdigest();result['source_sha256']=hashlib.sha256((ROOT/'integration/dashboard/service.py').read_bytes()).hexdigest()
    (args.output/'verification.json').write_text(json.dumps(result,indent=2)+'\n');(args.output/'snapshots.json').write_text(json.dumps(snapshots,indent=2)+'\n')
    print(json.dumps(result));return 0 if result['status']=='passed' else 1


if __name__=='__main__':raise SystemExit(main())
