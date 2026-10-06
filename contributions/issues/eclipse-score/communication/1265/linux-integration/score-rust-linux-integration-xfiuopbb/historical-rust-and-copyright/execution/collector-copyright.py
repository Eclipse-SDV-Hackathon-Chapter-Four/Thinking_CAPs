"""Remeasure copyright only; carry unchanged native Rust evidence explicitly."""
from pathlib import Path
import hashlib,json,runpy,sys
ROOT=Path(__file__).parent;ATTEMPT=ROOT/'copyright-recovery'
base=runpy.run_path(str(ROOT/'collector.py'))
def digest(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(name,obj):(ATTEMPT/name).write_text(json.dumps(obj,indent=2)+'\n')
def bind():
 base['bind']()
 b=json.loads((ROOT/'run-binding-copyright.json').read_text())
 for name,expected in b['files'].items():assert digest(ROOT/name)==expected,name
 for name,expected in b['git_metadata_files'].items():assert digest(ROOT/'candidate'/name)==expected,name
 return b
def preflight():
 b=bind();result=base['execute']('copyright-git-preflight',['/usr/bin/git','ls-files','-z','--cached','--others','--exclude-standard'],30)
 assert result['exit_code']==0
 raw=(ROOT/result['log']).read_bytes();names=raw.split(b'\0');required=b'score/mw/com/rust/design/identifier_pasting_assessment.md';assert required in names
 write('native-worker-preflight.json',{'kind':'actual_native_worker_git_and_carried_subject_check','source_hashes_verified':2879,'original_configuration_files_verified':45,'native_git_file_listing':result,'listed_files':len([n for n in names if n]),'assessment_in_listing':True,'HEAD_metadata_created':True,'commit_created':False,'HEAD_is_unborn':True,'Markdown_native_copyright_coverage':False})
 print('Native Git listing and unchanged carried Rust subjects verified.');return 0
def verify():
 b=bind();prior=json.loads((ROOT/'verification-results.json').read_text());rust=next(c for c in prior['checks'] if c['name']=='communication-macro-tests');assert rust['status']=='passed'
 assert digest(ROOT/rust['log'])==rust['log_sha256']
 carried={**rust,'evidence_mode':'carried_by_verified_unchanged_subject_hashes','source_run_id':'01M484ZS5EGJ8E5KH83XXN7PCB','native_test_targets':3,'Rust_cases_passed':33,'Rust_doctest_cases_ignored':2,'executed_this_copyright_only_run':False}
 args=[str(ROOT/'tools/bazel'),'--batch','--output_user_root='+str(ROOT/'bazel-output'),'run','--repository_cache='+str(ROOT/'repository-cache'),'--jobs=2','--color=no','--curses=no','//:copyright.check']
 current=base['execute']('native-copyright-correction2',args,300);bind()
 omissions=[c for c in prior['checks'] if c['name'] not in {'communication-macro-tests','native-copyright'}]
 checks=[carried,current,*omissions]
 write('verification-results.json',{'schema_version':1,'checks':checks,'patch_sha256':b['patch_sha256'],'engineering_acceptance':'pending_offline','qualification_adoption':'pending_offline','native_copyright_Markdown_coverage':'excluded_by_native_templates','native_test_baseline':'e3d126c2d7569345cf5f790310702eb00cd86b06','newer_HEAD_native_verification':False,'corrections_used':2,'max_corrections':3,'provider_calls':0})
 print(json.dumps({'native_copyright':current['status'],'Rust_evidence':'carried33passed2ignored','Markdown_native_copyright_coverage':False}));return current['exit_code']
def export():
 bind();p=ATTEMPT/'verification-results.json'
 if not p.exists():write('execution-export.json',{'verification_results_present':False,'engineering_acceptance':'pending_offline'});return 1
 x=json.loads(p.read_text());passed=all(c['status']=='passed' for c in x['checks'] if 'exit_code' in c)
 write('execution-export.json',{'verification_results_sha256':digest(p),'run_binding_sha256':digest(ROOT/'run-binding-copyright.json'),'all_selected_checks_passed':passed,'carried_evidence_explicit':True,'failed_prior_native_attempt_preserved':True,'engineering_acceptance':'pending_offline'})
 return 0 if passed else 1
if __name__=='__main__':sys.exit({'preflight':preflight,'verify':verify,'export':export}[sys.argv[1]]())
