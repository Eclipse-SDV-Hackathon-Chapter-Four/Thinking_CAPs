"""Prepare the second bounded, zero-model native repair; preserve the first attempt."""
import difflib,json,shutil,subprocess
from native_measure import P,R,guard,hashes,sha,write,api
import repair

def main():
    guard()
    first='01M490DRQA2P6NDYHMJ4M3TJB5'
    state=api('/api/v1/runs/'+first+'/state')
    if state['status']['kind'] not in {'failed','succeeded'}:raise ValueError('Previous run not terminal')
    write(P/'phases/repair-1/terminal-native-state.json',state)
    archive=P/'phases/repair-1/exported-results'
    if archive.exists():raise ValueError('Previous results already archived; do not repeat preparation')
    shutil.copytree(P/'results',archive)
    values=[]
    for n in [1236,751,1104]:
        tree=R/('issue-'+str(n));name='tools/lint/buildifier/BUILD' if n==1236 else 'quality/static_analysis/BUILD'
        before=(tree/name).read_text();marker='py_test(\n'
        if before.count(marker)!=1:raise ValueError('Expected single new regression test')
        after=before.replace(marker,'py_test(\n    imports = ["."],\n',1)
        patch='diff --git a/'+name+' b/'+name+'\n'+''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='a/'+name,tofile='b/'+name,n=3))
        repair.check_patch(n,patch,tree)
        folder=P/'repair-2'/str(n);folder.mkdir(parents=True,exist_ok=True);(folder/'canonical.patch').write_text(patch)
        write(folder/'preparation.json',{'source_hashes_before':hashes(tree),'paths':[name],'canonical_patch_sha256':sha(folder/'canonical.patch'),'reason':'Native hermetic Python bootstrap failed with ModuleNotFoundError; explicitly expose the package directory to its new test.'})
        values.append({'number':n,'patch':patch,'rationale':'Repair the measured native regression import error; format only bound changed files before remeasurement.'})
    write(P/'repair-2/canonical-correction.json',{'issues':values,'rationale':'Second deterministic repair attempt; no model call.'})
    text=(P/'repair.py').read_text().replace('phases/repair-1','phases/repair-2').replace("P/'repair-1/", "P/'repair-2/").replace("P/'repair-1'", "P/'repair-2'")
    old="if ledger.exists():raise ValueError('This repair attempt already admitted; never reset')\n    write(ledger,{'maximum_fixes_retries':3,'attempts':[{'attempt':1,'phase':'repair-1','native_run_id':(P/'phases/repair-2/native-run-id').read_text().strip(),'paid_model_calls':0}],'further_paid_model_calls':0,'engineering_acceptance':'pending_offline_review'})"
    new="history=json.loads(ledger.read_text())\n    if len(history['attempts'])!=1 or history['maximum_fixes_retries']!=3 or history['further_paid_model_calls']!=0:raise ValueError('Repair admission history differs')\n    history['attempts'].append({'attempt':2,'phase':'repair-2','native_run_id':(P/'phases/repair-2/native-run-id').read_text().strip(),'paid_model_calls':0})\n    write(ledger,history)"
    if text.count(old)!=1:raise ValueError('Supervisor anchor differs')
    text=text.replace(old,new)
    # Formatting is a source mutation: constrain it to previously scoped contribution paths.
    injection='''    format_records=[]
    for number in NUMBERS:
        tree=R/('issue-'+str(number));folder=P/'results'/str(number)
        previous=hashes(tree)
        allowed=ALLOWED[number]
        changed=subprocess.check_output(['git','-C',str(tree),'ls-files','--modified','--others','--exclude-standard'],text=True).splitlines()
        scoped=[name for name in changed if name=='BUILD' or name in allowed['allowed_files'] or any(name.startswith(prefix) for prefix in allowed['allowed_prefixes'])]
        star=[name for name in scoped if name.endswith(('.bzl','.bazel')) or name.rsplit('/',1)[-1]=='BUILD']
        py=[name for name in scoped if name.endswith('.py')]
        for language,paths in [('Starlark_with_buildifier',star),('Python_with_ruff',py)]:
            if paths:
                record=measure(folder,tree,'scoped-format-'+language,['run','//:format_'+language,'--',*paths],600)
                format_records.append(record)
                if record['exit_code']!=0:raise ValueError('Scoped native formatter failed')
        current=hashes(tree)
        differences={name for name in set(previous)|set(current) if previous.get(name)!=current.get(name)}
        if not differences<=set(scoped):raise ValueError('Formatter changed an unscoped path: '+repr(differences-set(scoped)))
        write(folder/'format-repair.json',{'changed_paths':sorted(differences),'before':previous,'after':current,'paid_calls':0})
        write(folder/'candidate-hashes.json',current)
    write(P/'repair-2/format-results.json',format_records)
'''
    anchor="    write(P/'results/1031/candidate-hashes.json',hashes(R/'issue-1031'))\n"
    if text.count(anchor)!=1:raise ValueError('Apply anchor differs')
    text=text.replace(anchor,anchor+injection)
    (P/'repair2.py').write_text(text)
    compile_text=(P/'compile_repair.py').read_text().replace("elif phase=='repair-1':", "elif phase=='repair-2':").replace("script=D/'repair.py'","script=D/'repair2.py'")
    (P/'compile_repair2.py').write_text(compile_text)
    frozen=json.loads((P/'frozen-inputs.json').read_text())
    write(P/'phases/repair-2/prior-frozen-inputs.json',frozen)
    for f in [P/'prepare_repair2.py',P/'repair2.py',P/'compile_repair2.py',*(P/'repair-2').rglob('*')]:
        if f.is_file():frozen[str(f.relative_to(P))]=sha(f)
    write(P/'frozen-inputs.json',frozen)
    print(json.dumps({'prepared':[v['number'] for v in values],'attempt':2,'paid_calls':0}))
if __name__=='__main__':main()
