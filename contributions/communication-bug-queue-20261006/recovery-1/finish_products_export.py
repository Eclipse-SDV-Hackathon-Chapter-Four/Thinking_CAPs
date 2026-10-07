"""Finish the preserved product archive; retain the completed disposable cache."""
import hashlib,json,tarfile,time
from pathlib import Path
from native_measure import P,R,guard,hashes,sha,write

def digest_stream(f):
    h=hashlib.sha256()
    for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
    return h.hexdigest()

def main():
    guard();control=P/'phases/repair-3/cache-reclamation';folder=P/'results/1236'
    if not (control/'cancellation.json').exists():raise ValueError('Original verifier termination is not recorded')
    subject=R/'issue-1236';expected=json.loads((folder/'candidate-hashes.json').read_text())
    if hashes(subject)!=expected:raise ValueError('Source drift')
    cache=R/'bazel-output/ae3faa9c0dd5776ee8fa52806c33e0fc'
    if (cache/'execroot/_main/MODULE.bazel').resolve()!=subject/'MODULE.bazel':raise ValueError('Cache ownership differs')
    native=cache/'execroot/_main/bazel-out/k8-fastbuild/bin'
    archive=folder/'native-generated-products.tar.gz';tmp=archive.with_suffix('.gz.tmp')
    if archive.exists() or not tmp.exists():raise ValueError('Archive state differs; inspect rather than overwrite')
    requested=set(n.decode() for n in (control/'files.list').read_bytes().split(b'\0') if n)
    members={};last_guard=time.monotonic()
    with tarfile.open(tmp,'r|gz') as tar:
        for member in tar:
            if time.monotonic()-last_guard>=1:guard();last_guard=time.monotonic()
            if not member.isfile() or member.name not in requested or member.name in members:raise ValueError('Unexpected archive member')
            source=native/member.name
            if source.is_symlink() or not source.resolve().is_relative_to(cache):raise ValueError('Source escaped owned cache')
            with source.open('rb') as f:expected_sha=digest_stream(f)
            with tar.extractfile(member) as f:actual=digest_stream(f)
            if actual!=expected_sha or member.size!=source.stat().st_size:raise ValueError('Native product differs from archive')
            members[member.name]={'sha256':actual,'bytes':member.size}
    if set(members)!=requested:raise ValueError('Archive lacks native products')
    guard()
    if hashes(subject)!=expected:raise ValueError('Source changed during export')
    tmp.replace(archive)
    with archive.open('rb') as f:archive_sha=digest_stream(f)
    write(folder/'native-generated-products-manifest.json',{'files':members,'archive':archive.name,'archive_sha256':archive_sha,'source_manifest_sha256':sha(folder/'candidate-hashes.json'),'native_run_id':'01M497MN3CXK842EEAAP765SFQ','all_members_verified':True,'scope':'Actual generated engineering/source/documentation products under native score/docs/quality; compiler objects, tool runtimes, runfiles and OCI build caches excluded','engineering_acceptance':'pending_offline_review'})
    write(control/'completion.json',{'cache_removed':False,'cache_retained':True,'reason':'Capacity recovered while tests finished; cache reclamation is unnecessary','engineering_products':len(members),'archive_sha256':archive_sha,'archive_bytes':archive.stat().st_size,'source_unchanged':True,'control_sha256':sha(Path(__file__)),'native_run_id':'01M497MN3CXK842EEAAP765SFQ','source_fixes_added':0,'paid_calls':0,'engineering_acceptance':'pending_offline_review'})
    print(json.dumps({'verified_products':len(members),'archive_bytes':archive.stat().st_size,'cache_retained':True}))

if __name__=='__main__':main()
