from pathlib import Path
import hashlib,json,runpy,sys
sys.path.insert(0,'/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root
r=Path(__file__).parent;validate_run_root(r)
module=runpy.run_path(str(r/'collector.py'))
prior=r.parent/'score-fabric-upcaieyc';validate_run_root(prior)
compilers=list((prior/'bazel-output').glob('*/external/*ferrocene*/bin/rustc'));assert len(compilers)==1
compiler=compilers[0]
def h(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
identity={'rustc':{'path':str(compiler),'sha256':h(compiler)},'driver_libraries':[{'path':str(p),'sha256':h(p)} for p in (compiler.parent.parent/'lib').glob('librustc_driver*.so')],'source':'readonly prior native materialized compiler; pins preserved, fresh compilation will select compiler anew'}
results=[]
for name,args in [('compatibility-glibc',['/usr/bin/getconf','GNU_LIBC_VERSION']),('compatibility-ferrocene',[str(compiler),'--version','--verbose']),('compatibility-bazel',[str(r/'tools/bazel'),'--version'])]:
 result=module['execute'](name,args,30);results.append(result)
 (r/'compatibility-preflight.json').write_text(json.dumps({'kind':'fresh_direct_native_namespace_diagnostic','compiler_input_identity':identity,'checks':results,'engineering_qualification':'not_established'},indent=2)+'\n')
 assert result['exit_code']==0,name
 assert h(compiler)==identity['rustc']['sha256']
log=(r/'logs/compatibility-ferrocene.log').read_text();assert '779fbed05ae9e9fe2a04137929d99cc9b3d516fd' in log
assert 'glibc 2.39' in (r/'logs/compatibility-glibc.log').read_text()
print(json.dumps({'glibc':'2.39','Ferrocene_commit':'779fbed05ae9e9fe2a04137929d99cc9b3d516fd','Bazel':'8.7.0','checks_passed':len(results),'corrections_used':0,'scope':'fresh namespace diagnostics; no tests or engineering qualification'}))
