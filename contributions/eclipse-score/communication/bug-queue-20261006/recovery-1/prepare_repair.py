"""Reanchor complete Flash hunks and correct source-backed integration defects."""
from pathlib import Path
import ast
import difflib
import json
import re
from native_measure import P, R, hashes, sha, write
import correction


def reconstruct(patch,tree):
    sections=[];current=None;hunk=None
    for line in patch.splitlines(keepends=True):
        if line.startswith('diff --git '):
            current={'path':None,'old_path':None,'hunks':[]};sections.append(current);hunk=None
        elif line.startswith('--- '):current['old_path']=line[4:].strip()
        elif line.startswith('+++ '):current['path']=line[4:].strip().removeprefix('b/')
        elif line.startswith('@@ '):hunk={'old':[],'new':[]};current['hunks'].append(hunk)
        elif hunk is not None:
            if line.startswith((' ','-')):hunk['old'].append(line[1:])
            if line.startswith((' ','+')):hunk['new'].append(line[1:])
            if line=='\n':hunk['old'].append(line);hunk['new'].append(line)
            if line.startswith('\\'):raise ValueError('Unsupported no-newline marker')
    desired={};anchors=[]
    for section in sections:
        name=section['path'];source=tree/name
        if section['old_path']=='/dev/null':
            if source.exists() or source.is_symlink():raise ValueError('New path exists: '+name)
            if len(section['hunks'])!=1 or section['hunks'][0]['old']:raise ValueError('Malformed new-file hunk')
            desired[name]=''.join(section['hunks'][0]['new']);continue
        before=source.read_text().splitlines(keepends=True);changes=[]
        for h in section['hunks']:
            old=h['old'];new=h['new']
            if not old:raise ValueError('No old-context anchor')
            matches=[i for i in range(len(before)-len(old)+1) if before[i:i+len(old)]==old]
            if len(matches)!=1:raise ValueError('Old hunk has no unique exact match: '+name)
            start=matches[0];changes.append((start,start+len(old),new));anchors.append({'path':name,'exact_line':start+1,'old_lines':len(old)})
        ordered=sorted(changes,key=lambda x:x[0]);last=-1
        for start,end,new in ordered:
            if start<last:raise ValueError('Overlapping model hunks')
            last=end
        for start,end,new in reversed(ordered):before[start:end]=new
        desired[name]=''.join(before)
    return desired,anchors


def substitute(text,old,new):
    if text.count(old)!=1:raise ValueError('Expected exactly one integration repair subject')
    return text.replace(old,new)


def fix_751(desired):
    name='quality/static_analysis/codeql_lint.py';text=desired[name]
    text=substitute(text,'def create_database(code_ql_path, config_path, target, source_root, database_path, build_configs=None):',
                    'def create_database(code_ql_path, config_path, target, source_root, database_path, build_configs=None, production_targets=False):')
    text=substitute(text,'query_expr = f\'kind("cc_library|cc_binary", {" + ".join(patterns)})\'',
                    'query_expr = f\'attr("testonly", "0", kind("cc_library|cc_binary", {" + ".join(patterns)}))\'')
    text=substitute(text,'labels = [line.strip() for line in cquery_stdout.splitlines() if line.strip()]',
                    'labels = [line.split()[0] for line in cquery_stdout.splitlines() if line.strip()]')
    desired[name]=text


def fix_1236(desired):
    name='tools/lint/buildifier/buildifier_lint.py';text=desired[name]
    text=substitute(text,'"buildifier_prebuilt/buildifier"','"buildifier_prebuilt/buildifier/buildifier.bash"')
    text=substitute(text,'if proc.returncode != 0 or "warning:" in output:', 'if proc.returncode != 0 or output.strip():')
    desired[name]=text
    name='tools/lint/buildifier/buildifier_lint_test.py';text=desired[name]
    for variable in ['CLEAN_FIXTURE','WARNING_FIXTURE']:
        text=substitute(text,'fixture = os.environ["'+variable+'"]','fixture = buildifier_lint.Runfiles.Create().Rlocation(os.environ["'+variable+'"])')
    text=substitute(text,'self.assertIn("warning:", output)','self.assertIn("unused-variable", output)')
    desired[name]=text


def fix_1104(desired):
    name='quality/static_analysis/codeql_lint.py';text=desired[name];tree=ast.parse(text)
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_normalize_placeholder_artifact_locations')
    old=ast.get_source_segment(text,node)
    new='''def _normalize_placeholder_artifact_locations(value):
    def placeholder(location):
        uri = location.get("uri")
        return uri in PLACEHOLDER_URIS and not (uri == "" and location.get("uriBaseId"))

    if isinstance(value, dict):
        physical = value.get("physicalLocation")
        artifact = physical.get("artifactLocation") if isinstance(physical, dict) else None
        if isinstance(artifact, dict) and placeholder(artifact):
            previous_uri = artifact.get("uri")
            remaining = {key: child for key, child in physical.items() if key != "artifactLocation"}
            if "address" in remaining:
                value["physicalLocation"] = remaining
            else:
                del value["physicalLocation"]
                if remaining:
                    value.setdefault("properties", {})["score.unlocatedPhysicalDetails"] = remaining
            value.setdefault("properties", {})["score.artifactLocationUnavailable"] = True
            value["properties"]["score.previousArtifactUri"] = previous_uri
            if "index" in artifact:
                value["properties"]["score.previousArtifactIndex"] = artifact["index"]
        location = value.get("location")
        if isinstance(location, dict) and placeholder(location):
            del value["location"]
            value.setdefault("properties", {})["score.artifactLocationUnavailable"] = True
            value["properties"]["score.previousArtifactUri"] = location.get("uri")
            if "index" in location:
                value["properties"]["score.previousArtifactIndex"] = location["index"]
        for child in value.values():
            _normalize_placeholder_artifact_locations(child)
    elif isinstance(value, list):
        for child in value:
            _normalize_placeholder_artifact_locations(child)'''
    text=substitute(text,old,new)
    text=substitute(text,'    recategorize_sarif(\n','    normalize_sarif_placeholder_locations(sarif_path)\n    recategorize_sarif(\n')
    text=substitute(text,'    normalize_sarif_rule_order(sarif_path)\n    normalize_sarif_placeholder_locations(sarif_path)\n','    normalize_sarif_rule_order(sarif_path)\n')
    text=substitute(text,'def normalize_sarif_placeholder_locations(sarif_path):\n',
                    'def normalize_sarif_placeholder_locations(sarif_path):\n    shutil.copyfile(sarif_path, sarif_path + ".before-placeholder-normalization")\n')
    desired[name]=text
    name='quality/static_analysis/codeql_lint_test.py';text=desired[name]
    text=substitute(text,'artifact_location = sarif["runs"][0]["artifacts"][0]["location"]\n        self.assertNotIn("uri", artifact_location)\n        self.assertEqual(artifact_location["index"], 101)\n        related_physical = sarif["runs"][0]["results"][0]["relatedLocations"][0]["physicalLocation"]\n        self.assertNotIn("artifactLocation", related_physical)',
                    'artifact = sarif["runs"][0]["artifacts"][0]\n        self.assertNotIn("location", artifact)\n        self.assertEqual(artifact["properties"]["score.previousArtifactIndex"], 101)\n        related = sarif["runs"][0]["results"][0]["relatedLocations"][0]\n        self.assertNotIn("physicalLocation", related)\n        self.assertEqual(related["message"]["text"], "Result")')
    text=substitute(text,'physical = normalized["runs"][0]["results"][0]["physicalLocation"]\n            self.assertNotIn("artifactLocation", physical)',
                    'result = normalized["runs"][0]["results"][0]\n            self.assertNotIn("physicalLocation", result)\n            self.assertTrue(result["properties"]["score.artifactLocationUnavailable"])')
    desired[name]=text


def main():
    original=json.loads((P/'correction-response.txt').read_text());all_patches=[]
    for value in original['issues']:
        number=value['number'];tree=R/('issue-'+str(number));desired,anchors=reconstruct(value['patch'],tree)
        globals()['fix_'+str(number)](desired)
        patch=''
        for name,after in desired.items():
            before=(tree/name).read_text() if (tree/name).exists() else ''
            if name.endswith('.py'):ast.parse(after)
            patch+='diff --git a/'+name+' b/'+name+'\n'
            if not (tree/name).exists():patch+='new file mode 100644\n'
            patch+=''.join(difflib.unified_diff(before.splitlines(keepends=True),after.splitlines(keepends=True),fromfile='a/'+name if (tree/name).exists() else '/dev/null',tofile='b/'+name,n=3))
        paths=correction.check_patch(number,patch,tree)
        folder=P/'repair-1'/str(number);folder.mkdir(parents=True,exist_ok=True);(folder/'canonical.patch').write_text(patch)
        write(folder/'preparation.json',{'original_model_patch_sha256':__import__('hashlib').sha256(value['patch'].encode()).hexdigest(),'canonical_patch_sha256':sha(folder/'canonical.patch'),'exact_old_hunk_anchors':anchors,'paths':paths,'source_hashes_before':hashes(tree),'paid_calls':0,'source_repair':'Exact hunk reanchoring plus documented integration corrections; original response retained.'})
        all_patches.append({'number':number,'patch':patch,'rationale':value['rationale']+' Integration repairs are separately documented; native evidence and offline review are required.'})
    write(P/'repair-1/canonical-correction.json',{'issues':all_patches,'rationale':'One deterministic repair pass; no new model call.'})
    print(json.dumps({'prepared':[v['number'] for v in all_patches],'paid_calls':0}))

if __name__=='__main__':main()
