"""Keyboard run/cancel controls with owned wait-process fixture; no native acceptance."""
import json
from pathlib import Path
import sys
import tempfile
import threading
import time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tests'))
from integration.dashboard.service import Dashboard,server
from dashboard_browser_smoke import Browser
OUT=Path(__file__).parent;CHROME='/home/jefferson/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome';checks=[]
try:
 for width in (360,1280):
  with tempfile.TemporaryDirectory(prefix='sdv-dashboard-keyboard-') as directory:
   root=Path(directory);inputs=root/'inputs.json';inputs.write_text('{}')
   app=Dashboard({'state_dir':str(root/'state'),'campaign_config':str(inputs),'diagnostic_base':'http://127.0.0.1:1/sovd'})
   app.manager.command_factory=lambda record:[sys.executable,'-c','import signal,time,sys;signal.signal(signal.SIGTERM,lambda s,f:sys.exit(1));print("explicit keyboard wait fixture",flush=True);time.sleep(30)']
   httpd=server(app,0);thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start();browser=None
   def check(name,condition):
    checks.append({'id':str(width)+'-'+name,'passed':bool(condition)})
    if not condition:raise AssertionError(name)
   try:
    browser=Browser(CHROME,'http://127.0.0.1:'+str(httpd.server_port),OUT/(str(width)+'-browser.log'))
    check('loaded',browser.wait('typeof snapshot!=="undefined"&&snapshot!==null'))
    browser.call('Emulation.setDeviceMetricsOverride',{'width':width,'height':900,'deviceScaleFactor':1,'mobile':width<720})
    browser.evaluate('$("nav-tests").focus()');browser.key('Enter',13)
    check('keyboard-navigation',browser.wait('!$("tests-view").hidden'))
    browser.evaluate('$("start").focus()');browser.key('Enter',13)
    check('keyboard-start',browser.wait('snapshot.active_run?.state==="running"'))
    identity=browser.evaluate('snapshot.active_run.id');browser.call('Page.reload')
    check('reload-same-run',browser.wait('typeof snapshot!=="undefined"&&snapshot?.active_run?.id==='+json.dumps(identity)+'&&$("cancel").disabled===false'))
    time.sleep(.15);browser.evaluate('$("cancel").focus()');browser.key('Enter',13)
    check('keyboard-cancel-and-unknown-cleanup',browser.wait('snapshot.active_run?.state==="cancelled"&&snapshot.active_run.cleanup.status==="unknown"&&$("start").disabled'))
    check('cleanup-visible',browser.evaluate('$("run-info").textContent.includes("unknown")&&$("evidence-info").textContent.includes("unknown")'))
    check('no-javascript-errors',not browser.errors)
    browser.screenshot(OUT/(str(width)+'-cancelled.png'),width,900)
   finally:
    if browser:browser.close()
    httpd.shutdown();httpd.server_close();thread.join(timeout=2);app.close()
 record={'status':'passed','scope':'Actual Chromium keyboard start/reload/cancel at360/1280 using owned wait-process fixture; no vehicle/native fault/cleanup success claim','checks':checks}
except Exception as error:record={'status':'failed','error':str(error),'checks':checks}
(OUT/'verification.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record));raise SystemExit(0 if record['status']=='passed' else 1)
