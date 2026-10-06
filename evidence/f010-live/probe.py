"""Real native, cancellation and physical runs via local dashboard; owned resources only."""
from pathlib import Path
import concurrent.futures
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests'))
sys.path.insert(0,str(ROOT))
from dashboard_browser_smoke import Browser
from integration.dashboard.service import pid_identity
OUT = Path(__file__).parent
BASE = 'http://127.0.0.1:8791'
CHROME = '/home/jefferson/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'
checks=[]; browsers=[]; identities=[]; paused=None; pause_identity=None

def check(name, condition, **detail):
    checks.append(dict(id=name,passed=bool(condition),**detail))
    if not condition: raise AssertionError(name)

def get(path='/api/state'):
    return json.load(urllib.request.urlopen(BASE+path,timeout=5))

def post(path,body):
    token=get()['token'];req=urllib.request.Request(BASE+path,data=json.dumps(body).encode(),headers={'Origin':BASE,'X-SDV-Token':token,'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(req,timeout=5) as response:return response.status,json.load(response)
    except urllib.error.HTTPError as error:return error.code,json.load(error)

def wait(predicate,timeout=300):
    deadline=time.monotonic()+timeout
    while time.monotonic()<deadline:
        value=predicate()
        if value:return value
        time.sleep(.1)
    raise AssertionError('bounded live wait exceeded')

def detail(identity):return get('/api/runs/'+identity)

def retain(identity,name):
    record=json.loads((ROOT/'.local/dashboard-f010/ledger.json').read_text())['runs'][identity]
    source=Path(record['output']);target=OUT/name
    shutil.copytree(source,target)
    for artifact, info in detail(identity)['artifacts'].items():
        fetched=urllib.request.urlopen(BASE+'/api/runs/'+identity+'/artifacts/'+urllib.parse.quote(artifact,safe=''),timeout=5).read()
        check(name+'-download-'+artifact,hashlib.sha256(fetched).hexdigest()==info['sha256'] and fetched==(source/artifact).read_bytes())
    return record

try:
    wait(lambda:get()['bench']['availability']=='available',30)
    b1=Browser(CHROME,BASE,OUT/'browser-one.log');browsers.append(b1)
    b2=Browser(CHROME,BASE,OUT/'browser-two.log');browsers.append(b2)
    for b in browsers:check('browser-connected',b.wait('typeof snapshot!=="undefined"&&snapshot!==null'))
    with concurrent.futures.ThreadPoolExecutor(2) as pool:
        attempts=list(pool.map(lambda _:post('/api/runs',{'scenario':'core'}),range(2)))
    check('two-clients-exactly-one-start',sorted(code for code,value in attempts)==[202,409],responses=attempts)
    identity=next(value['id'] for code,value in attempts if code==202);identities.append(identity)
    check('both-browser-active-identity',all(b.wait('snapshot.active_run?.id==='+json.dumps(identity)) for b in browsers))
    b2.call('Page.reload');check('browser-reload-reconnect-same-run',b2.wait('typeof snapshot!=="undefined"&&snapshot?.active_run?.id==='+json.dumps(identity)))
    wait(lambda:get()['diagnosis']['observation']['availability']=='available',60)
    check('actual-native-live-diagnosis',b1.wait('$("service-status").dataset.state==="available"'))
    b1.screenshot(OUT/'actual-native-diagnosis.png')
    samples=[]
    for _ in range(12):
        value=get()['diagnosis']['observation'];stamp=value['acquired_utc'];started=time.monotonic()
        visible=b1.wait('$("last-acquired").textContent.includes('+json.dumps(stamp)+')',2)
        # A newer acquired snapshot also proves old data did not hold rendering back.
        if not visible:visible=b1.evaluate('$("last-acquired").textContent.startsWith("Acquired ")&&$("last-acquired").textContent.slice(9)>='+json.dumps(stamp))
        samples.append({'visible_within_two_seconds':visible,'elapsed_seconds':time.monotonic()-started,'acquired_utc':stamp})
        time.sleep(.1)
    check('nominal-acquisition-visibility',sum(s['visible_within_two_seconds'] for s in samples)/len(samples)>=.95,samples=samples)
    core=wait(lambda:detail(identity) if detail(identity)['state'] in ('passed','failed','blocked') else None)
    check('actual-native-core-pass',core['state']=='passed' and core['results']['status']=='passed' and core['cleanup']['status']=='passed',run_id=identity)
    record=retain(identity,'core')
    check('native-core-42-assertions',len(json.loads((OUT/'core/native/results.json').read_text())['checks'])==42)
    code,value=post('/api/runs',{'scenario':'core'});check('cancel-run-start',code==202);identity=value['id'];identities.append(identity)
    wait(lambda:any(e.get('kind')=='tunnel-down-complete' for e in detail(identity)['progress']),120)
    code,value=post('/api/runs/'+identity+'/cancel',{});check('cancellation-request-acknowledged',code==202 and value['cancel_requested'])
    final=wait(lambda:detail(identity) if detail(identity)['state']=='cancelled' else None)
    check('actual-cancel-not-pass',final['results']['status']=='failed' and final['cleanup']['status']=='passed',cleanup=final['cleanup'])
    retain(identity,'cancelled')
    code,value=post('/api/runs',{'scenario':'carla'});check('physical-run-start-after-restoration',code==202);identity=value['id'];identities.append(identity)
    wait(lambda:get()['diagnosis']['observation']['availability']=='available' and get()['diagnosis']['observation']['value'].get('freshness_state')=='fresh',90)
    check('physical-diagnosis-browser-live',b1.wait('$("freshness").dataset.state==="fresh"'))
    b1.screenshot(OUT/'physical-live-diagnosis.png')
    listening=subprocess.check_output(['ss','-ltnp'],text=True)
    row=next(row for row in listening.splitlines() if ':8791 ' in row)
    paused=int(re.search(r'pid=(\d+)',row).group(1));pause_identity=pid_identity(paused)
    cmdline=Path('/proc/'+str(paused)+'/cmdline').read_bytes()
    check('dashboard-pause-ownership',b'scripts/run_dashboard.py' in cmdline and b'.local/dashboard-f010.json' in cmdline)
    os.kill(paused,signal.SIGSTOP)
    check('actual-dashboard-loss-labels-unknown',b1.wait('$("connection").textContent.includes("unavailable")&&$("freshness").dataset.state==="unknown"',5))
    time.sleep(1)
    if pid_identity(paused)==pause_identity:os.kill(paused,signal.SIGCONT)
    paused=None
    check('dashboard-resume-same-physical-run',b1.wait('$("connection").textContent.includes("connected")&&snapshot.active_run?.id==='+json.dumps(identity)))
    physical=wait(lambda:detail(identity) if detail(identity)['state'] in ('passed','failed','blocked') else None)
    check('physical-control-survives-dashboard-outage',physical['state']=='passed' and physical['results']['status']=='passed' and physical['cleanup']['status']=='passed')
    retain(identity,'physical')
    native=json.loads((OUT/'physical/native/results.json').read_text())
    check('physical-46-native-assertions',len(native['checks'])==46 and all(c['status']=='passed' for c in native['checks']))
    check('no-browser-javascript-errors',all(not b.errors for b in browsers))
    record={'status':'passed','classification':'prepared','scope':'Actual dashboard API/browser, native core, cancellation during managed tunnel disturbance, physical CARLA with dashboard SIGSTOP outage; no independent human run','checks':checks,'run_ids':identities}
except Exception as error:
    record={'status':'failed','error':str(error),'checks':checks,'run_ids':identities}
finally:
    if paused is not None and pid_identity(paused)==pause_identity:os.kill(paused,signal.SIGCONT)
    for b in browsers:b.close()
    active=get().get('active_run')
    if active and active['state'] in ('queued','running','cancelling'):
        post('/api/runs/'+active['id']+'/cancel',{})
        wait(lambda:detail(active['id'])['state'] not in ('queued','running','cancelling'))
    record['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'integration/dashboard/service.py',ROOT/'scripts/run_campaign.py',ROOT/'tests/opendut_receiver_smoke.py',ROOT/'integration/dashboard/web/app.js',Path(__file__)]}
    (OUT/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({'status':record['status'],'error':record.get('error'),'checks':len(checks),'run_ids':identities}));raise SystemExit(0 if record['status']=='passed' else 1)
