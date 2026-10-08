"""Export actual native Communication safety products, excluding runtime/tool caches."""
import json,shutil,sys
from native_measure import P,R,guard,sha,write

def export_products(destination):
    guard();root=R/'issue-1031/bazel-bin/score/mw/com/dependability/safety_analysis'
    if not root.exists():raise ValueError('Native safety products are missing')
    destination.mkdir(parents=True,exist_ok=True);files=[]
    for source in sorted(root.rglob('*')):
        name=source.relative_to(root)
        if any(p.endswith(('.runfiles','.venv')) for p in name.parts):continue
        if not source.is_file():continue
        if source.suffix not in {'.json','.html','.rst','.puml','.svg','.trlc','.csv','.lobster'} and source.name!='traceability_config':continue
        if not source.resolve().is_relative_to(R):raise ValueError('Native product points outside owned volume')
        before=sha(source);target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        if sha(source)!=before or sha(target)!=before:raise ValueError('Native product changed during export')
        files.append({'path':str(name),'source_path':str(source),'sha256':before,'bytes':source.stat().st_size})
        guard()
    if not files:raise ValueError('No native engineering products found')
    write(destination/'manifest.json',{'files':files,'source_commit':json.loads((P/'configuration.json').read_text())['source_commit'],'native_source_manifest_sha256':sha(P/'results/1031/candidate-hashes.json'),'complete_for_scope':'Native safety analysis products; runtime/tool launchers, runfiles and virtual environments are excluded','production_config_management_integration':'unmeasured','engineering_acceptance':'pending_offline_review','credentials_exported':False})
    return {'files':len(files),'bytes':sum(f['bytes'] for f in files),'path':str(destination)}
if __name__=='__main__':print(json.dumps(export_products(P/sys.argv[1])))
