import base64,json,os,secrets,signal,socket,struct,subprocess,tempfile,time,urllib.request
from pathlib import Path
root=Path.cwd(); out=root/'evidence/f008-presentation-browser'; out.mkdir(exist_ok=False)
chrome='/home/jefferson/.cache/ms-playwright/chromium-1243/chrome-linux64/chrome'; page=(root/'docs/hackathon/pitch.html').as_uri(); proc=None; channel=None; checks=[]; failures=[]; number=0
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
with tempfile.TemporaryDirectory(prefix='sdv-pitch-browser-') as profile, (out/'browser.txt').open('wb') as log:
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
  call('Runtime.enable'); call('Page.enable'); call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':850,'deviceScaleFactor':1,'mobile':False}); time.sleep(.5)
  checks.append({'id':'initial-slide-and-target-duration','passed':evaluate('slides.length===7 && slides.reduce((sum,s)=>sum+Number(s.dataset.seconds),0)===570 && slides.filter(s=>!s.hidden).length===1 && index===0')})
  checks.append({'id':'next-button-and-slide-context','passed':evaluate('document.getElementById("next").click();index===1 && document.getElementById("position").textContent==="2 / 7" && location.hash==="#slide-2" && slides.filter(s=>!s.hidden).length===1')})
  shot=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True})['data']; (out/'desktop-architecture.png').write_bytes(base64.b64decode(shot))
  checks.append({'id':'keyboard-last-and-first','passed':evaluate('(()=>{document.body.dispatchEvent(new KeyboardEvent("keydown",{key:"End",bubbles:true}));const last=index===6&&document.getElementById("next").disabled;document.body.dispatchEvent(new KeyboardEvent("keydown",{key:"Home",bubbles:true}));return last&&index===0&&document.getElementById("previous").disabled;})()')})
  checks.append({'id':'keyboard-slide-navigation','passed':evaluate('document.body.dispatchEvent(new KeyboardEvent("keydown",{key:"ArrowRight",bubbles:true}));index===1')})
  checks.append({'id':'rehearsal-clock','passed':evaluate('document.getElementById("timer").click();new Promise(resolve=>setTimeout(()=>resolve(document.getElementById("elapsed").textContent!=="0:00"),1100))')})
  call('Emulation.setDeviceMetricsOverride',{'width':360,'height':900,'deviceScaleFactor':1,'mobile':True}); evaluate('show(4)'); time.sleep(.2)
  checks.append({'id':'mobile-width-and-evidence-limit','passed':evaluate('document.documentElement.scrollWidth<=360 && slides[index].textContent.includes("Human reproduction remains pending")')})
  shot=call('Page.captureScreenshot',{'format':'png','captureBeyondViewport':True})['data']; (out/'mobile-evidence.png').write_bytes(base64.b64decode(shot))
  call('Emulation.setDeviceMetricsOverride',{'width':1280,'height':850,'deviceScaleFactor':1,'mobile':False})
  pdf=call('Page.printToPDF',{'printBackground':True,'preferCSSPageSize':True})['data']; (out/'pitch.pdf').write_bytes(base64.b64decode(pdf))
  checks.append({'id':'no-external-runtime-requests','passed':evaluate('performance.getEntriesByType("resource").every(r=>r.name.startsWith("file:"))')})
  checks.append({'id':'javascript-errors','passed':not failures})
  record={'status':'passed' if all(c['passed'] for c in checks) else 'failed','scope':'actual local headless browser navigation, clock, responsive layout and print rendering; not human rehearsal','browser_version':subprocess.check_output([chrome,'--version']).decode().strip(),'checks':checks,'javascript_errors':failures}
 except Exception as error: record={'status':'failed','error':str(error),'checks':checks,'javascript_errors':failures}
 finally:
  if channel: channel.close()
  if proc:
   try: os.killpg(proc.pid,signal.SIGTERM)
   except ProcessLookupError: pass
   try: proc.wait(timeout=5)
   except subprocess.TimeoutExpired: os.killpg(proc.pid,signal.SIGKILL); proc.wait(timeout=3)
(out/'verification.json').write_text(json.dumps(record,indent=2)+'\n'); (out/'probe.py').write_bytes(Path(__file__).read_bytes()); print(json.dumps(record)); raise SystemExit(0 if record['status']=='passed' else 1)
