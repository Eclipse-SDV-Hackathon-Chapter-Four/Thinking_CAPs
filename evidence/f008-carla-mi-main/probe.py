import hashlib,json,os,re,selectors,signal,socket,subprocess,tempfile,time
from pathlib import Path
import carla
root=Path.cwd(); out=root/'evidence/f008-carla-mi-main'; out.mkdir(exist_ok=False)
for port in [2100,2101,2102]:
 with socket.socket() as sock: sock.bind(('127.0.0.1',port))
log=(out/'gdb-mi.txt').open('wb'); observed=[]; lines=[]; native_pid=None; debugger=None; interrupted=False
with tempfile.TemporaryDirectory(prefix='sdv-carla-mi-') as runtime:
 environment=os.environ.copy(); environment['XDG_CONFIG_HOME']=runtime+'/config'; environment['VK_ICD_FILENAMES']='/usr/share/vulkan/icd.d/nvidia_icd.json'
 binary='/home/jefferson/carla-simulator/CarlaUE4/Binaries/Linux/CarlaUE4-Linux-Shipping'
 args=['gdb','--quiet','--interpreter=mi2','--args',binary,'CarlaUE4','-nullrhi','-nosound','-carla-rpc-port=2100','-UserDir='+runtime+'/user']
 record={'schema_version':1,'mode':'owned CARLA debugger command-interface main-thread probe','work_classification':'prepared','commands':args,'observations':observed}
 try:
  debugger=subprocess.Popen(args,cwd='/home/jefferson/carla-simulator',env=environment,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True,bufsize=0)
  poller=selectors.DefaultSelector(); poller.register(debugger.stdout,selectors.EVENT_READ); buffer=b''
  def pump(seconds):
   global buffer,native_pid
   deadline=time.monotonic()+seconds
   while time.monotonic()<deadline:
    for key,_ in poller.select(min(.2,max(0,deadline-time.monotonic()))):
     data=os.read(key.fd,65536)
     if not data: poller.unregister(key.fileobj); return
     log.write(data); log.flush(); buffer+=data
     while b'\n' in buffer:
      line,buffer=buffer.split(b'\n',1); line=line.decode(errors='replace'); lines.append(line)
      found=re.search(r'thread-group-started.*pid="(\d+)"',line)
      if found: native_pid=int(found.group(1))
  def send(command,seconds=1):
   debugger.stdin.write((command+'\n').encode()); debugger.stdin.flush(); pump(seconds)
  pump(.5); send('1-gdb-set pagination off'); send('2-gdb-set confirm off'); send('3-gdb-set mi-async on'); send('4-interpreter-exec console "handle SIGINT stop nopass"'); send('5-exec-run',2)
  client=carla.Client('127.0.0.1',2100,2); client.set_timeout(1)
  deadline=time.monotonic()+25
  while time.monotonic()<deadline and debugger.poll() is None:
   try: observed.append({'server_version':client.get_server_version(),'world_id':client.get_world().id,'status':'ready'})
   except RuntimeError as error: observed.append({'status':'unavailable','error':str(error)})
   pump(.2)
  send('6-exec-interrupt --all',5)
  interrupted=any(line.startswith('*stopped') for line in lines)
  if interrupted:
   send('7-thread-select 1',1); send('8-stack-list-frames 0 30',2); send('9-interpreter-exec console "bt 30"',2)
  send('10-gdb-exit',1)
  try: debugger.wait(timeout=5)
  except subprocess.TimeoutExpired: pass
  record['main_thread_frames']=[line for line in lines if line.startswith('8^')]
  record['interrupt_stopped']=interrupted
  record['status']='ready' if any(o['status']=='ready' for o in observed) else 'blocked'
 except Exception as error: record['status']='failed'; record['error']=str(error)
 finally:
  if debugger:
   try: os.killpg(debugger.pid,signal.SIGTERM)
   except ProcessLookupError: pass
   try: debugger.wait(timeout=3)
   except subprocess.TimeoutExpired:
    os.killpg(debugger.pid,signal.SIGKILL); debugger.wait(timeout=3)
  # GDB may create an inferior process group; verify this exact child identity before removal.
  if native_pid:
   try:
    cmd=Path('/proc/'+str(native_pid)+'/cmdline').read_bytes()
    if binary.encode() in cmd and runtime.encode() in cmd:
     os.kill(native_pid,signal.SIGKILL)
   except (FileNotFoundError,ProcessLookupError): pass
  log.close()
 record['debugger_exit']=debugger.returncode if debugger else None
 record['native_pid']=native_pid
 record['native_binary_sha256']=hashlib.sha256(Path(binary).read_bytes()).hexdigest()
(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
(out/'probe.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':record['status'],'interrupt_stopped':interrupted,'frames':record.get('main_thread_frames',[])}))
