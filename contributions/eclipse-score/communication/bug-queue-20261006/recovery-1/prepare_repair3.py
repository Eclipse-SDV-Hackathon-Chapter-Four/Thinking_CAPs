"""Prepare the final bounded repair only after attempt 2 terminates."""
import ast,difflib,json,shutil
from native_measure import P,R,guard,hashes,sha,write,api
import repair

def main():
    guard();first=(P/'phases/repair-2/native-run-id').read_text().strip();state=api('/api/v1/runs/'+first+'/state')
    if state['status']['kind'] not in {'failed','succeeded'}:raise ValueError('Attempt 2 remains active; do not prepare or alter subjects')
    write(P/'phases/repair-2/terminal-native-state.json',state)
    archive=P/'phases/repair-2/exported-results'
    if archive.exists():raise ValueError('Preparation already attempted; preserve previous history')
    shutil.copytree(P/'results',archive)
    from export_safety_products import export_products
    export_products(P/'phases/repair-2/generated-safety-products')
    for name in ['correction-export.json','native-correction-summary.json','native-correction-state.json','native-correction-stages.json']:
        if (P/name).exists():shutil.copyfile(P/name,P/'phases/repair-2'/name)
    if (P/'native-databases').exists():shutil.copytree(P/'native-databases',P/'phases/repair-2/native-databases')
    values=[]
    for n in [1236,751,1104]:
        tree=R/('issue-'+str(n))
        name='tools/lint/buildifier/buildifier_lint_test.py' if n==1236 else 'quality/static_analysis/BUILD'
        before=(tree/name).read_text()
        old='self.assertIn("unused-variable", output)' if n==1236 else '    target_compatible_with = ["@platforms//os:linux"],\n)\n\nfilegroup('
        new='self.assertIn(\'Loaded symbol "cc_test" is unused.\', output)' if n==1236 else '    tags = ["local"],\n    target_compatible_with = ["@platforms//os:linux"],\n)\n\nfilegroup('
        if before.count(old)!=1:raise ValueError('Measured repair anchor differs for '+str(n))
        after=before.replace(old,new,1)
        desired={name:after}
        if n==751:
            source='quality/static_analysis/codeql_lint.py';text=(tree/source).read_text()
            old='''        if ":" in label:
            pkg = label[2:].split(":", 1)[0]
        else:
            pkg = label[2:]
        patterns.append(f"//{pkg}/...")'''
            new='''        patterns.append(label)'''
            if text.count(old)!=1:raise ValueError('Production-root anchor differs')
            text=text.replace(old,new)
            old='query_expr = f\'attr("testonly", "0", kind("cc_library|cc_binary", {" + ".join(patterns)}))\''
            new='query_expr = f\'attr("testonly", "0", kind("cc_library|cc_binary", deps(set({" ".join(patterns)}))))\''
            if text.count(old)!=1:raise ValueError('Production closure anchor differs')
            text=text.replace(old,new)
            old='return [label for label in labels if label.startswith("//")]'
            if text.count(old)!=1:raise ValueError('Configured-label parser differs')
            text=text.replace(old,'return sorted({label for label in labels if label.startswith("//")})')
            old='''help="When set, explicitly build all non-test C/C++ library and binary "
        "targets under the supplied native scopes, including implementation_deps "
        "that would otherwise be built lazily.",'''
            new='''help="Build main-repository C/C++ library and binary targets not marked "
        "test-only from the dependency closure of the supplied roots, including "
        "implementation_deps that would otherwise be built lazily.",'''
            if text.count(old)!=1:raise ValueError('Production-target CLI help anchor differs')
            text=text.replace(old,new)
            desired[source]=text
            source='quality/static_analysis/codeql_lint_test.py';text=(tree/source).read_text()
            text=text.replace('test_production_target_patterns_expand_package_roots','test_production_target_patterns_preserve_requested_roots')
            text=text.replace('"//score/message_passing/...",','"//score/message_passing",').replace('"//score/mw/com/...",','"//score/mw/com",')
            anchor='    def test_production_target_patterns_reject_empty(self):\n'
            regression='''    def test_production_target_patterns_preserve_explicit_selectors(self):
        self.assertEqual(
            codeql_lint._production_target_patterns("//score/mw/com:com //score/message_passing/... //:api"),
            ["//score/mw/com:com", "//score/message_passing/...", "//:api"],
        )

    def test_parse_production_targets_deduplicates_configured_labels(self):
        self.assertEqual(
            codeql_lint._parse_production_targets("//score/mw/com:com (aaa)\\n//score/mw/com:com (bbb)\\n"),
            ["//score/mw/com:com"],
        )

'''
            if text.count(anchor)!=1:raise ValueError('Production selector test anchor differs')
            desired[source]=text.replace(anchor,regression+anchor)
        patch=''
        for path,content in desired.items():
            if path.endswith('.py'):ast.parse(content)
            original=(tree/path).read_text()
            patch+='diff --git a/'+path+' b/'+path+'\n'+''.join(difflib.unified_diff(original.splitlines(keepends=True),content.splitlines(keepends=True),fromfile='a/'+path,tofile='b/'+path,n=3))
        repair.check_patch(n,patch,tree)
        folder=P/'repair-3'/str(n);folder.mkdir(parents=True,exist_ok=True);(folder/'canonical.patch').write_text(patch)
        write(folder/'preparation.json',{'source_hashes_before':hashes(tree),'paths':list(desired),'canonical_patch_sha256':sha(folder/'canonical.patch'),'reason':'Use the native observed unused-load diagnostic' if n==1236 else 'Align native bytecode execution tags; for751 preserve supplied roots and select their configured dependency closure rather than unrelated package-subtree benchmarks.'})
        values.append({'number':n,'patch':patch,'rationale':'Final measured deterministic integration repair; no paid call. Full candidate verification remains required.'})
    write(P/'repair-3/canonical-correction.json',{'issues':values,'rationale':'Third and final deterministic repair attempt; no model call.'})
    text=(P/'repair2.py').read_text().replace('phases/repair-2','phases/repair-3').replace("P/'repair-2/", "P/'repair-3/").replace("P/'repair-2'", "P/'repair-3'")
    text=text.replace("len(history['attempts'])!=1", "len(history['attempts'])!=2").replace("{'attempt':2,'phase':'repair-2'", "{'attempt':3,'phase':'repair-3'")
    anchor="        star=[name for name in scoped if name.endswith(('.bzl','.bazel')) or name.rsplit('/',1)[-1]=='BUILD']\n"
    injection="""        # The native copyright/formatter tools discover files through Git.
        # Include all new scoped sources before measurement; never commit here.
        if scoped:
            subprocess.run(['git','-C',str(tree),'-c','core.hooksPath=/dev/null','add','--intent-to-add','--',*scoped],check=True,capture_output=True)
        write(folder/'git-index-input.json',{'index_sha256':sha(tree/'.git/index'),'scoped_files':scoped,'intent_to_add':True,'committed':False})
"""
    if text.count(anchor)!=1:raise ValueError('Native formatter scope anchor differs')
    text=text.replace(anchor,injection+anchor)
    # Each measurement explicitly binds the relevant index after native file discovery.
    anchor="    return measure(d,R/('issue-'+str(number)),label,args,timeout)\n"
    replacement="""    tree=R/('issue-'+str(number));before_index=sha(tree/'.git/index')
    discovery_before=__import__('hashlib').sha256(subprocess.check_output(['git','-C',str(tree),'ls-files','--stage','-z'])).hexdigest()
    result=measure(d,tree,label,args,timeout)
    record_path=P/result['record'];record=json.loads(record_path.read_text())
    record['git_index_sha256_before']=before_index
    record['git_index_sha256_after']=sha(tree/'.git/index')
    discovery_after=__import__('hashlib').sha256(subprocess.check_output(['git','-C',str(tree),'ls-files','--stage','-z'])).hexdigest()
    record['git_file_discovery_sha256_before']=discovery_before
    record['git_file_discovery_sha256_after']=discovery_after
    if discovery_after!=discovery_before:raise ValueError('Git file-discovery input changed during native check')
    write(record_path,record)
    return result
"""
    if text.count(anchor)!=1:raise ValueError('Measurement anchor differs')
    text=text.replace(anchor,replacement)
    ast.parse(text)
    (P/'repair3.py').write_text(text)
    text=(P/'compile_repair2.py').read_text().replace("elif phase=='repair-2':", "elif phase=='repair-3':").replace("script=D/'repair2.py'", "script=D/'repair3.py'")
    (P/'compile_repair3.py').write_text(text)
    frozen=json.loads((P/'frozen-inputs.json').read_text());write(P/'phases/repair-3/prior-frozen-inputs.json',frozen)
    for f in [P/'prepare_repair3.py',P/'repair3.py',P/'compile_repair3.py',P/'export_safety_products.py',P/'check_fresh_sarif.py',P/'finalize_review.py',*(P/'repair-3').rglob('*')]:
        if f.is_file():frozen[str(f.relative_to(P))]=sha(f)
    write(P/'frozen-inputs.json',frozen)
    print(json.dumps({'prepared':[v['number'] for v in values],'attempt':3,'paid_calls':0}))
if __name__=='__main__':main()
