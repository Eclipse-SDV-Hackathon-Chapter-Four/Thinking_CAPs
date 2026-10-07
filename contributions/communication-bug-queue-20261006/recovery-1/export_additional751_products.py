"""Preserve actual native engineering products; retain every build cache."""
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import time
from pathlib import Path

import native_measure as n
import additional751 as task


def digest(stream):
    value=hashlib.sha256()
    for block in iter(lambda:stream.read(8*1024*1024),b''):
        value.update(block)
    return value.hexdigest()


def main():
    task.guard();folder=task.OUT/'results/751'
    expected=json.loads((folder/'candidate-hashes.json').read_text())
    if n.hashes(task.TREE)!=expected:
        raise ValueError('Additional source drift')
    summary=n.api('/api/v1/runs/'+task.identifier())
    if summary['lifecycle']['status']['kind'] not in {'succeeded','failed'}:
        raise ValueError('Native execution is not finished')
    native=(task.TREE/'bazel-bin').resolve();cache=native.parents[4]
    if cache.parent!=n.R/'bazel-output' or (cache/'execroot/_main/MODULE.bazel').resolve()!=task.TREE/'MODULE.bazel':
        raise ValueError('Generated product cache ownership differs')
    suffixes={'.json','.html','.rst','.puml','.svg','.trlc','.rsl','.csv','.lobster','.sarif','.dot','.txt','.xml','.css','.js','.png','.jpg','.gif','.woff','.woff2','.ttf','.pdf','.h','.hpp','.cpp','.cc','.rs'}
    files={};last_guard=time.monotonic()
    for scope in ['score','docs','quality']:
        for base,dirs,names in os.walk(native/scope,followlinks=False):
            dirs[:]=[d for d in dirs if not d.endswith(('.runfiles','.venv')) and d!='__pycache__']
            for name in names:
                path=Path(base)/name
                if path.is_symlink() or not path.is_file() or not (path.suffix in suffixes or name=='traceability_config'):
                    continue
                if time.monotonic()-last_guard>=1:
                    task.guard();last_guard=time.monotonic()
                if not path.resolve().is_relative_to(cache):
                    raise ValueError('Generated product escaped owned cache')
                with path.open('rb') as stream:
                    files[str(path.relative_to(native))]={'sha256':digest(stream),'bytes':path.stat().st_size}
    if not files:
        raise ValueError('No actual generated products')
    listing=task.OUT/'engineering-products.list'
    listing.write_bytes(b''.join(name.encode()+b'\0' for name in sorted(files)))
    target=folder/'native-generated-products.tar.gz';temporary=target.with_suffix('.gz.tmp')
    if target.exists() or temporary.exists():
        raise ValueError('Engineering archive already exists; inspect before replay')
    command=['tar','--hard-dereference','--use-compress-program=gzip -1','-cf',str(temporary),'-C',str(native),'--null','-T',str(listing)]
    with (task.OUT/'engineering-products.stderr').open('wb') as stderr:
        process=subprocess.Popen(command,stderr=stderr,start_new_session=True)
        try:
            while process.poll() is None:
                task.guard()
                if shutil.disk_usage(folder).free<64*1024*1024:
                    raise OSError('Explicit artifact destination below64MiB free')
                time.sleep(1)
            if process.returncode:
                raise ValueError('Native engineering product tar failed')
        except BaseException:
            if process.poll() is None:
                process.terminate();process.wait(timeout=10)
            raise
    verified=set();last_guard=time.monotonic()
    with tarfile.open(temporary,'r|gz') as archive:
        for member in archive:
            if time.monotonic()-last_guard>=1:
                task.guard();last_guard=time.monotonic()
            if not member.isfile() or member.name not in files or member.name in verified:
                raise ValueError('Unexpected generated archive member')
            with archive.extractfile(member) as stream:
                if digest(stream)!=files[member.name]['sha256'] or member.size!=files[member.name]['bytes']:
                    raise ValueError('Generated product archive mismatch')
            with (native/member.name).open('rb') as stream:
                if digest(stream)!=files[member.name]['sha256']:
                    raise ValueError('Generated product changed while packaging')
            verified.add(member.name)
    if verified!=set(files) or n.hashes(task.TREE)!=expected:
        raise ValueError('Incomplete products or source drift')
    task.guard();temporary.replace(target)
    with target.open('rb') as stream:
        archive_sha=digest(stream)
    n.write(folder/'native-generated-products-manifest.json',{'files':files,'archive':target.name,
        'archive_sha256':archive_sha,'source_manifest_sha256':n.sha(folder/'candidate-hashes.json'),
        'native_run_id':task.identifier(),'scope':'Actual generated engineering/source/documentation products under native score/docs/quality; compiler objects, runtimes, runfiles and OCI caches excluded',
        'all_members_verified':True,'cache_retained':True,'source_fixes_added':0,'paid_calls':0,
        'engineering_acceptance':'pending_offline_review'})
    print(json.dumps({'verified_products':len(files),'archive_bytes':target.stat().st_size,'cache_retained':True}))


if __name__=='__main__':
    main()
