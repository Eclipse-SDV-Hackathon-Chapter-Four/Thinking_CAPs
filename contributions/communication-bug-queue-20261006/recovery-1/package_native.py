"""Export owned native databases as bounded portable archives."""
from pathlib import Path
import os
import shutil
import subprocess
import time
import yaml
from native_measure import P, R, guard, hashes, sha, write

def export_databases():
    folder=P/'native-databases';folder.mkdir(exist_ok=True)
    results=[]
    for relative in ['codeql-baseline-v2/nightly','codeql-baseline-v2/impl','codeql-candidate/751','codeql-candidate/1104','codeql-candidate/1104-nightly']:
        source=R/relative
        if not source.is_dir():
            results.append({'source':relative,'status':'not_created'});continue
        guard();before=hashes(source);metadata=source/'codeql-database.yml'
        state=yaml.safe_load(metadata.read_text()) if metadata.is_file() else {}
        target=folder/(relative.replace('/','-')+'.tar.gz');tmp=target.with_suffix(target.suffix+'.tmp')
        command=['tar','--use-compress-program=gzip -1','-cf',str(tmp),'-C',str(source.parent),source.name]
        result={'source':relative,'native_finalized':bool(metadata.exists() and not state.get('inProgress')),'command':command,'source_hashes':before,'started_at_epoch':time.time()}
        error=None
        with (target.with_suffix('.stderr')).open('wb') as stderr:
            child=subprocess.Popen(command,stdout=subprocess.DEVNULL,stderr=stderr,start_new_session=True)
            try:
                while child.poll() is None:
                    guard()
                    if shutil.disk_usage(P).free<64*1024*1024:raise OSError('Artifact destination has less than 64MiB free; preserve external subjects and stop packaging')
                    if time.time()-result['started_at_epoch']>1800:raise TimeoutError('Archive packaging timeout')
                    time.sleep(1)
                if child.returncode:raise RuntimeError('Native tar exit '+str(child.returncode))
                if hashes(source)!=before:raise RuntimeError('Native database changed during export')
                guard();tmp.replace(target);result.update(status='exported',archive=str(target.relative_to(P)),archive_sha256=sha(target),archive_bytes=target.stat().st_size)
            except BaseException as exc:
                error=exc
                if child.poll() is None:
                    os.killpg(child.pid,15)
                    try:child.wait(timeout=5)
                    except subprocess.TimeoutExpired:os.killpg(child.pid,9);child.wait()
                if tmp.exists():tmp.unlink()
                result.update(status='failed',reason=str(exc))
        result['finished_at_epoch']=time.time();results.append(result)
        write(folder/'manifest.json',{'databases':results,'artifact_destination':str(P),'credentials_exported':False})
        if error:raise error
    write(folder/'manifest.json',{'databases':results,'artifact_destination':str(P),'credentials_exported':False})
    return results
