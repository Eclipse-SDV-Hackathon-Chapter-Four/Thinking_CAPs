"""Preserve verified engineering products before reclaiming one owned inactive cache."""
import hashlib,json,os,signal,subprocess,tarfile,time
from pathlib import Path
from native_measure import P,R,guard,hashes,sha,write

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    guard();folder=P/'results/1236';subject=R/'issue-1236'
    cache=R/'bazel-output/ae3faa9c0dd5776ee8fa52806c33e0fc'
    control=P/'phases/repair-3/cache-reclamation';control.mkdir(exist_ok=True)
    if (control/'admission.json').exists():raise ValueError('Cache reclamation already attempted; inspect receipts')
    state=json.loads((P.parent/'state.json').read_text())
    item=next(i for i in state['items'] if i['issue_number']==1236)
    if item['run_id']!='01M497MN3CXK842EEAAP765SFQ' or item['stage']!='verification_exported':raise ValueError('Native stage is not complete')
    if hashes(subject)!=json.loads((folder/'candidate-hashes.json').read_text()):raise ValueError('Source drift')
    for name in ['build-all','test-all','format']:
        record=json.loads((folder/'evidence'/ (name+'.json')).read_text())
        if record['exit_code']!=0 or record['started_at_epoch']<1791311300:raise ValueError('Fresh successful check missing: '+name)
    if cache.is_symlink() or not cache.is_relative_to(R) or (cache/'execroot/_main/MODULE.bazel').resolve()!=subject/'MODULE.bazel':raise ValueError('Cache ownership differs')
    for process in Path('/proc').glob('[0-9]*'):
        try:command=(process/'cmdline').read_bytes()
        except OSError:continue
        if str(cache).encode() in command or str(subject).encode() in command:raise ValueError('Cache/subject still referenced by process '+process.name)
    native=cache/'execroot/_main/bazel-out/k8-fastbuild/bin'
    suffixes={'.json','.html','.rst','.puml','.svg','.trlc','.rsl','.csv','.lobster','.sarif','.dot','.txt','.xml','.css','.js','.png','.jpg','.gif','.woff','.woff2','.ttf','.pdf','.h','.hpp','.cpp','.cc','.rs'}
    files={}
    for scope in ['score','docs','quality']:
        for base,dirs,names in os.walk(native/scope,followlinks=False):
            dirs[:]=[d for d in dirs if not d.endswith(('.runfiles','.venv')) and d!='__pycache__']
            for name in names:
                path=Path(base)/name
                if not path.is_symlink() and path.is_file() and (path.suffix in suffixes or name=='traceability_config'):
                    if not path.resolve().is_relative_to(cache):raise ValueError('Product outside cache')
                    files[str(path.relative_to(native))]={'sha256':digest(path),'bytes':path.stat().st_size}
    write(control/'admission.json',{'cache':str(cache),'native_run_id':item['run_id'],'source_manifest_sha256':sha(folder/'candidate-hashes.json'),'control_sha256':sha(Path(__file__)),'phase':'preserving_products','cache_scope':'This task-owned completed issue1236 Bazel output only; sources/control/global caches retained','engineering_acceptance':'pending_offline_review'})
    listing=control/'files.list';listing.write_bytes(b''.join(n.encode()+b'\0' for n in sorted(files)))
    archive=folder/'native-generated-products.tar.gz';tmp=archive.with_suffix('.gz.tmp')
    command=['tar','--hard-dereference','--use-compress-program=gzip -1','-cf',str(tmp),'-C',str(native),'--null','-T',str(listing)]
    with (control/'archive.stderr').open('wb') as error:
        child=subprocess.Popen(command,stderr=error,start_new_session=True)
        try:
            while child.poll() is None:guard();time.sleep(1)
            if child.returncode:raise ValueError('Archive creation failed')
        except BaseException:
            if child.poll() is None:os.killpg(child.pid,signal.SIGKILL);child.wait()
            raise
    verified=set()
    with tarfile.open(tmp,'r|gz') as tar:
        for member in tar:
            guard()
            if not member.isfile() or member.name not in files:raise ValueError('Unexpected archive entry')
            h=hashlib.sha256();f=tar.extractfile(member)
            for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
            if h.hexdigest()!=files[member.name]['sha256']:raise ValueError('Archive product digest differs')
            verified.add(member.name)
    if verified!=set(files):raise ValueError('Incomplete engineering product archive')
    guard();tmp.replace(archive)
    write(folder/'native-generated-products-manifest.json',{'files':files,'archive':archive.name,'archive_sha256':digest(archive),'source_manifest_sha256':sha(folder/'candidate-hashes.json'),'native_run_id':item['run_id'],'scope':'Actual generated engineering/source/documentation products under native score/docs/quality; compiler objects, tool runtimes, runfiles and OCI build caches are disposable','all_members_verified':True,'engineering_acceptance':'pending_offline_review'})
    write(control/'preserved-evidence.json',{'files':{str(f.relative_to(folder)):digest(f) for f in folder.rglob('*') if f.is_file() and f.name!='artifact-manifest.json'},'source_hashes':hashes(subject)})
    guard();before=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
    child=subprocess.Popen(['/usr/bin/rm','-rf','--one-file-system','--',str(cache)],start_new_session=True)
    try:
        while child.poll() is None:guard();time.sleep(1)
        if child.returncode:raise ValueError('Cache reclamation failed')
    except BaseException:
        if child.poll() is None:os.killpg(child.pid,signal.SIGKILL);child.wait()
        raise
    guard()
    if hashes(subject)!=json.loads((folder/'candidate-hashes.json').read_text()):raise ValueError('Source changed during reclamation')
    after=os.statvfs(R).f_bavail*os.statvfs(R).f_frsize
    write(control/'completion.json',{'cache_removed':not cache.exists(),'free_bytes_before':before,'free_bytes_after':after,'engineering_products':len(files),'archive_sha256':digest(archive),'source_unchanged':True,'native_run_id':item['run_id'],'engineering_acceptance':'pending_offline_review'})
    print(json.dumps({'reclaimed_GiB':round((after-before)/2**30,2),'engineering_products':len(files),'archive_bytes':archive.stat().st_size}))

if __name__=='__main__':main()
