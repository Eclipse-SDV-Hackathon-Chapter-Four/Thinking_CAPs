import base64,json,os,secrets,signal,socket,struct,subprocess,tempfile,time,urllib.request
from pathlib import Path
root=Path.cwd(); out=root/'evidence/f009-replay-browser'; out.mkdir(exist_ok=False)
chrome='/home/jefferson/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'; page=(root/'evidence/f009-recorded-replay-final/index.html').as_uri(); proc=None; channel=None; checks=[]; failures=[]; number=0
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with tempfile.TemporaryDirectory(prefix='sdv-replay-browser-') as profile, (out/'browser.txt').open('wb') as log:
 try:
  proc=subprocess.Popen([chrome,'--headless','--no-sandbox','--disable-gpu','--no-first-run','--no-default-browser-check','--remote-debugging-port=0','--remote-allow-origins=http://localhost','--user-data-dir='+profile,page],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  deadline=time.monotonic()+15; portfile=Path(profile)/'DevToolsActivePort'
  while not portfile.exists():
   if time.monotonic()>deadline: raise RuntimeError('browser readiness timeout')
   time.sleep(.1)
  port=int(portfile.read_text().splitlines()[0]); targets=json.load(opener.open('http://127.0.0.1:'+str(port)+'/json/list'))
  url=next(t['webSocketDebuggerUrl'] for t in targets if t['type']=='page'); path=url.split(str(port),1)[1]
  channel=socket.create_connection(('127.0.0.1',port),timeout=5); channel.settimeout(10); key=base64.b64encode(secrets.token_bytes(16)).decode(); channel.sendall(('GET '+path+' HTTP/1.1\r\nHost: localhost\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: '+key+'\r\nSec-WebSocket-Version: 13\r\nOrigin: http://localhost\r\n\r\n').encode())
  header=b''
  while not header.endswith(b'\r\n\r\n'): header+=channel.recv(1)
  if not header.startswith(b'HTTP/1.1 101'): raise RuntimeError('debugger handshake rejected')
  def exact(size):
   data=b''
   while len(data)<size:
    part=channel.recv(size-len(data))
    if not part: raise RuntimeError('debugger closed')
    data+=part
   return data
  def call(method,params=None):
   global number
   number+=1; payload=json.dumps({'id':number,'method':method,'params':params or {}}).encode(); mask=secrets.token_bytes(4); length=len(payload)
   header=bytes([0x81,0x80|length]) if length<126 else bytes([0x81,0xfe])+struct.pack('!H',length) if length<65536 else bytes([0x81,0xff])+struct.pack('!Q',length)
   channel.sendall(header+mask+bytes(v^mask[i%4] for i,v in enumerate(payload)))
   while True:
    first,second=exact(2); size=second&127
    if size==126: size=struct.unpack('!H',exact(2))[0]
    elif size==127: size=struct.unpack('!Q',exact(8))[0]
    value=json.loads(exact(size))
    if value.get('method')=='Runtime.exceptionThrown': failures.append(value)
    if value.get('id')==number:
     if 'error' in value: raise RuntimeError(str(value['error']))
     return value['result']
  def evaluate(expression):
   value=call('Runtime.evaluate',{'expression':expression,'returnByValue':True,'awaitPromise':True})
   if 'exceptionDetails' in value: raise RuntimeError(str(value['exceptionDetails']))
   return value['result'].get('value')
  call('Runtime.enable'); call('Page.enable'); call('Emulation.setDeviceMetricsOverride',{'width':1180,'height':1100,'deviceScaleFactor':1,'mobile':False}); time.sleep(.5)
  checks.append({'id':'initial-render','passed':evaluate('document.getElementById("summary").textContent.includes("9 selected") && document.getElementById("sources").children.length===7')})
  checks.append({'id':'failed-fault-seek','passed':evaluate('(()=>{const f=faults.find(s=>s.value.assessment.state==="failed");element("seek").value=(f.t+.05)/duration*1000;element("seek").dispatchEvent(new Event("input"));return element("fault").textContent.includes("failed")&&element("event-log").textContent.includes("tunnel-down-complete");})()')})
  image=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True})['data']; (out/'failed-fault-replay.png').write_bytes(base64.b64decode(image))
  checks.append({'id':'end-retains-unknown','passed':evaluate('element("seek").value=1000;element("seek").dispatchEvent(new Event("input"));element("fault").textContent.includes("unknown")')})
  checks.append({'id':'play-and-pause','passed':evaluate('element("restart").click();element("play").click();new Promise(resolve=>setTimeout(()=>{element("play").click();resolve(cursor>0&&!playing);},200))')})
  checks.append({'id':'restart','passed':evaluate('element("restart").click();cursor===0&&!playing')})
  checks.append({'id':'no-runtime-or-external-requests','passed':evaluate('performance.getEntriesByType("resource").every(r=>r.name.startsWith("file:"))')})
  checks.append({'id':'javascript-errors','passed':not failures})
  record={'status':'passed' if all(c['passed'] for c in checks) else 'failed','scope':'actual local headless browser rendering/seeking/play/pause/restart; historical offline data only','browser_version':subprocess.check_output([chrome,'--version']).decode().strip(),'checks':checks,'javascript_errors':failures}
 except Exception as error: record={'status':'failed','error':str(error),'checks':checks,'javascript_errors':failures}
 finally:
  if channel: channel.close()
  if proc:
   try: os.killpg(proc.pid,signal.SIGTERM)
   except ProcessLookupError: pass
   try: proc.wait(timeout=5)
   except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL); proc.wait(timeout=3)
(out/'verification.json').write_text(json.dumps(record,indent=2)+'\n'); (out/'probe.py').write_bytes(Path(__file__).read_bytes()); print(json.dumps(record)); raise SystemExit(0 if record['status']=='passed' else 1)
