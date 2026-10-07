"""Check real fresh SARIF and replay only its bound source normalizer; no model call."""
import ast,collections,copy,hashlib,importlib.metadata,json,sys
from native_measure import P,R,guard,sha,write
import jsonschema

def main():
    guard();phase=sys.argv[1];folder=P/'results/1104/native-codeql/reports'
    record=json.loads((P/'results/1104/evidence/codeql-analyze.json').read_text())
    if record['exit_code']!=0:raise ValueError('Candidate native analysis failed; no successful report claim')
    code=R/'issue-1104/quality/static_analysis/codeql_lint.py';source=ast.parse(code.read_text())
    nodes=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='_normalize_placeholder_artifact_locations' or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PLACEHOLDER_URIS' for t in n.targets)]
    scope={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(code),'exec'),scope)
    schema_file=P/'native-sarif-schema-2.1.0.json';schema=json.loads(schema_file.read_text());validator=jsonschema.validators.validator_for(schema)(schema)
    def uris(value,placeholders=False):
        result=[]
        def visit(v):
            if isinstance(v,dict):
                if 'uri' in v and ((v['uri'] in scope['PLACEHOLDER_URIS'])==placeholders):result.append(json.dumps(v,sort_keys=True))
                for x in v.values():visit(x)
            elif isinstance(v,list):
                for x in v:visit(x)
        visit(value);return collections.Counter(result)
    reports=[]
    for report in sorted(folder.rglob('*.sarif')):
        raw=report.with_name(report.name+'.before-placeholder-normalization')
        if not raw.exists():raise ValueError('Raw report missing')
        before=json.loads(raw.read_text());replayed=copy.deepcopy(before);scope['_normalize_placeholder_artifact_locations'](replayed)
        final=json.loads(report.read_text());replay_errors=list(validator.iter_errors(replayed));final_errors=list(validator.iter_errors(final))
        counts=lambda v:[len(r.get('results',[])) for r in v.get('runs',[])]
        preserved=uris(before)==uris(replayed)
        if replay_errors or final_errors or not preserved or counts(before)!=counts(replayed):raise ValueError('Fresh native SARIF/schema or preservation check failed')
        reports.append({'report':str(report.relative_to(P)),'raw_sha256':sha(raw),'final_sha256':sha(report),'raw_finding_count':sum(counts(before)),'final_finding_count':sum(counts(final)),'native_final_schema_errors':len(final_errors),'bound_normalizer_schema_errors':len(replay_errors),'all_valid_uri_objects_preserved_in_normalization':preserved,'finding_counts_preserved_in_normalization':True,'remaining_placeholders_after_normalization':sum(uris(replayed,True).values()),'remaining_placeholders_in_final_report':sum(uris(final,True).values()),'scope':'Fresh supplemental nightly projection; exact impl/... extraction failed and remains retained','paths_synthesized':False})
    if not reports:raise ValueError('No fresh native SARIF report')
    output={'phase':phase,'native_run_id':(P/'phases'/phase/'native-run-id').read_text().strip(),'python':sys.version.split()[0],'jsonschema_version':importlib.metadata.version('jsonschema'),'schema_sha256':sha(schema_file),'source_normalizer_sha256':sha(code),'native_analysis_record_sha256':sha(P/'results/1104/evidence/codeql-analyze.json'),'reports':reports,'engineering_acceptance':'pending_offline_review','paid_calls':0}
    write(P/'results/1104/fresh-sarif-check.json',output);print(json.dumps(output))
if __name__=='__main__':main()
