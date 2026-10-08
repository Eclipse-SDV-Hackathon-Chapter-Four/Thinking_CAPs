from pathlib import Path
import ast,json,copy,hashlib,collections,sys,importlib.metadata
p=Path(__file__).resolve().parent.parent;sys.path.insert(0,str(p));import prepare_repair as prepare
values=json.loads((p/'correction-response.txt').read_text())['issues'];v=next(x for x in values if x['number']==1104);desired,_=prepare.reconstruct(v['patch'],prepare.R/'issue-1104');prepare.fix_1104(desired)
def load(source,label):
    tree=ast.parse(source);nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_normalize_placeholder_artifact_locations' or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PLACEHOLDER_URIS' for t in n.targets)];scope={};exec(compile(ast.Module(body=nodes,type_ignores=[]),label,'exec'),scope);return scope
scope=load(desired['quality/static_analysis/codeql_lint.py'],'repaired-normalizer');raw=p/'evidence3-results/codeql-reports/baseline-nightly.sarif';before=json.loads(raw.read_text());after=copy.deepcopy(before);scope['_normalize_placeholder_artifact_locations'](after)
import jsonschema
schema_path=p/'native-sarif-schema-2.1.0.json';schema=json.loads(schema_path.read_text());cls=jsonschema.validators.validator_for(schema);validator=cls(schema);errors=list(validator.iter_errors(after))
def valid_uris(data):
    result=[]
    def visit(v):
        if isinstance(v,dict):
            if 'uri' in v and v['uri'] not in scope['PLACEHOLDER_URIS']:result.append(json.dumps(v,sort_keys=True))
            for x in v.values():visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
    visit(data);return collections.Counter(result)
assert not errors,[str(x)[:400] for x in errors[:3]]
assert valid_uris(before)==valid_uris(after)
assert [len(r.get('results',[])) for r in before['runs']]==[len(r.get('results',[])) for r in after['runs']]
original,_=prepare.reconstruct(v['patch'],prepare.R/'issue-1104');ns=load(original['quality/static_analysis/codeql_lint.py'],'original-model-normalizer');bad=copy.deepcopy(before);ns['_normalize_placeholder_artifact_locations'](bad);bad_errors=list(validator.iter_errors(bad));assert bad_errors
report={'source':'Actual native nightly SARIF, hash-bound replay; not a new candidate extraction or analyzer run','python':sys.version.split()[0],'input_sha256':hashlib.sha256(raw.read_bytes()).hexdigest(),'native_schema_sha256':hashlib.sha256(schema_path.read_bytes()).hexdigest(),'schema_validator_version':importlib.metadata.version('jsonschema'),'original_model_schema_errors':len(bad_errors),'repaired_schema_errors':len(errors),'all_valid_uri_objects_preserved':True,'finding_counts_preserved':True,'finding_count':sum(len(r.get('results',[])) for r in before['runs']),'human_acceptance':'pending_offline_review'}
(p/'repair-1/sarif-replay-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
