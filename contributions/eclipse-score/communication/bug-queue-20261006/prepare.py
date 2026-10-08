"""Compile the user-authorized queue with the frozen pre-optimization fabric."""
from pathlib import Path
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import yaml
from score_sw_fabric.compiler.reader import semantic_digest
from score_sw_fabric.compiler.package import compile_request
from score_sw_fabric.compiler.validator import validate_native
from score_sw_fabric.storage import validate_run_root

P = Path(__file__).resolve().parent
R = Path((P / 'scratch-root').read_text().strip())
F = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha/fabric')
N = R / 'baseline'
B = Path('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro')
PIN = '1b4fb15281ebb724426f9e480dce48d0100ff79b'
OLD = R.parent / 'score-communication1167-review-wzlezbhr'
os.environ['SCORE_FABRO_BIN'] = str(B)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')
def seal(v):
    v = {k: value for k, value in v.items() if k != 'digest'}
    return {**v, 'digest': semantic_digest(v)}

def main():
    validate_run_root(R)
    fabric_commit = subprocess.check_output(['git', '-C', str(F), 'rev-parse', 'HEAD'], text=True).strip()
    if fabric_commit != 'b2aa9a7a49a054621f38e59f3aef6d6e5daf3cce' or (F / 'src/score_sw_fabric/optimization').exists():
        raise ValueError('Stable pre-optimization baseline changed')
    if (P / 'native-run-id').exists():
        raise ValueError('Do not rebuild or reset an existing paid queue')
    tools = {'bazel-8.7.0': 'd7606e679b78067c811096fb3d6cf135225b528835ca396e3a4dddf957859544',
             'docker-client': '361ff5e29dad49f4e757bcd6ca16d64fce82a6a97313c60190ad0ff66d624720'}
    for name, expected in tools.items():
        source = OLD / 'tools' / name
        if sha(source) != expected:
            raise ValueError('Native tool provenance differs')
        dest = R / 'tools' / name
        dest.parent.mkdir(exist_ok=True)
        shutil.copyfile(source, dest)
        dest.chmod(0o755)
    shim = R / 'tools/bazel'
    shim.write_text('#!/bin/sh\nexec ' + shlex.join([str(R / 'tools/bazel-8.7.0'), '--output_user_root=' + str(R / 'bazel-output'), '--batch']) + ' "$@"\n')
    shim.chmod(0o755)
    tools['bazel'] = sha(shim)
    for name in ['container-tmp', 'container-var-tmp', 'container-home', 'bazel-output', 'runtime-target']:
        (R / name).mkdir(exist_ok=True)
    (R / 'runtime-target/README.txt').write_text('Fabro control workspace. Native issue workspaces are independently pinned and checked by the collector.\n')
    native_commit = subprocess.check_output(['git', '-C', str(N), 'rev-parse', 'HEAD'], text=True).strip()
    base_hashes = {str(p.relative_to(N)): sha(p) for p in N.rglob('*') if p.is_file() and not p.is_symlink() and '.git' not in p.relative_to(N).parts}
    write(P / 'baseline-hashes.json', base_hashes)
    specs = {
      1236: {'reason': 'Native formatter/CI configuration can be measured against an unused-load regression.',
        'allowed_files': ['BUILD', '.github/workflows/build_and_test_host.yml', '.github/workflows/_linter.yml', 'CONTRIBUTING.md'],
        'allowed_prefixes': ['tools/lint/buildifier/', 'quality/buildifier/'],
        'context': ['BUILD', 'MODULE.bazel', '.bazelrc', '.github/workflows/build_and_test_host.yml', '.github/workflows/_linter.yml', 'score/mw/com/impl/BUILD', 'score/mw/com/impl/bindings/lola/BUILD'],
        'query': '//tools/lint/... union //quality/...',
        'native_checks': [('quality-tests', ['test', '//quality/...', '--nocache_test_results'])],
        'instruction': 'Reproduce the unused cc_test load from PR1234 with a meaningful negative regression. Distinguish buildifier formatting from lint warnings: formatting-only CI is insufficient. Use the pinned buildifier_prebuilt dependency and native Bazel/CI patterns. Add an enforcing lint target and CI invocation and regression test; do not silently suppress unused-load warnings across the repository. Buildifier cannot verify arbitrary dependency closure, so do not claim it can. Preserve unrelated C++ targets and dependencies.'},
      1031: {'reason': 'Native AoU visibility and tooling forwarding are directly relevant to portable traceability artifacts.',
        'allowed_files': ['score/mw/com/dependability/safety_analysis/BUILD', 'score/mw/com/dependability/safety_analysis/README.md', 'quality/visibility_guard/public_targets.golden'],
        'allowed_prefixes': ['score/mw/com/dependability/safety_analysis/aou_forwarding_test/'],
        'context': ['score/mw/com/dependability/BUILD', 'score/mw/com/dependability/safety_analysis/BUILD', 'score/mw/com/dependability/safety_analysis/aou.trlc', 'quality/visibility_guard/BUILD', 'quality/visibility_guard/parser.py', 'quality/visibility_guard/visibility_guard_test.py', 'quality/visibility_guard/public_targets.golden', 'MODULE.bazel'],
        'query': '//score/mw/com/dependability/safety_analysis/...',
        'native_checks': [('aou-artifacts', ['build', '//score/mw/com/dependability/safety_analysis:aous']), ('visibility', ['test', '//quality/visibility_guard:visibility_guard_test', '--nocache_test_results'])],
        'instruction': 'Expose only the required aous target for external Config Management consumption. Preserve the safety_analysis dependency so existing AoU root_causes resolve correctly; never duplicate safety analysis processing or invent native AoU IDs. Keep other targets restricted unless supplied native evidence requires otherwise. Document exact score_tooling2.3.1 forwarding semantics using the supplied pinned tooling implementation and guide. If public exposure changes the visibility golden, change only the exact intended target and explicitly describe that API addition as a draft requiring offline review. Add a realistic consumer regression if implementable from supplied actual tooling rules; if cross-repository semantics cannot be proven, explicitly state the unresolved obligation rather than manufacture acceptance.'},
      751: {'reason': 'Production-source completeness is central to fabric analyzer evidence; the owned native CodeQL pipeline is available.',
        'allowed_files': ['quality/static_analysis/BUILD', 'quality/static_analysis/codeql_lint.py', 'quality/static_analysis/codeql_lint_test.py', '.github/workflows/_codeql.yml', 'quality/static_analysis/README.md'],
        'allowed_prefixes': [], 'context': ['quality/static_analysis/BUILD', 'quality/static_analysis/codeql_lint.py', 'quality/static_analysis/config.yaml', 'quality/static_analysis/static_analysis.bazelrc', '.github/workflows/_codeql.yml', 'score/mw/com/impl/plumbing/BUILD', 'score/mw/com/impl/BUILD', 'quality/visibility_guard/BUILD'],
        'query': '//quality/static_analysis/...', 'native_checks': [('analysis-tests', ['test', '//quality/static_analysis/...', '--nocache_test_results'])],
        'instruction': 'Investigate why production proxy_binding_factory_impl.cpp is absent. A source file having no findings does not prove it was omitted. Make a scoped production-target selection/completeness audit improvement supported by the native tracing implementation; distinguish extraction/database source coverage from SARIF result presence. Preserve compiler tracing environment and forced-recompile seed. If adjusting nightly --target selection, use exact native package patterns and do not silently include tests or drop production targets. Add negative and positive regressions around target expansion or audit behavior using real helper interfaces, and document any missing native compiler-database proof. Do not fabricate a CodeQL command, query, file location or analysis success.'},
      1104: {'reason': 'The native SARIF generation/postprocessing pipeline permits bounded location-preservation regressions.',
        'allowed_files': ['quality/static_analysis/BUILD', 'quality/static_analysis/codeql_lint.py', 'quality/static_analysis/codeql_lint_test.py', 'quality/static_analysis/README.md'],
        'allowed_prefixes': [], 'context': ['quality/static_analysis/BUILD', 'quality/static_analysis/codeql_lint.py', 'quality/static_analysis/config.yaml', 'quality/static_analysis/static_analysis.bazelrc', '.github/workflows/_codeql.yml', 'quality/visibility_guard/BUILD'],
        'query': '//quality/static_analysis/...', 'native_checks': [('analysis-tests', ['test', '//quality/static_analysis/...', '--nocache_test_results'])],
        'instruction': 'Trace source-root, working-directory and postprocessing behavior that could produce file:/ rather than a source location. Preserve legitimate relative URIs, uriBaseId and artifact indexes, percent encoding and existing native SARIF fields. Never synthesize a file path, assign the first artifact, remove findings with missing locations or rewrite file:/ without source-backed mapping. Add meaningful negative/positive regression tests around any corrected native helper. If the error originates in upstream queries or cannot be reconstructed from these sources, return no files with the precise unresolved reason rather than emit a speculative fix.'}
    }
    issues = {i['number']: i for i in json.loads((P / 'open-bugs.json').read_text())['issues']}
    excluded = {1116:'Gateway implementation and a supplied restart reproducer are not available in this owned baseline.', 1064:'Atomic close-on-exec depends on baselibs filesystem APIs and a security/lifecycle decision across repositories.', 848:'Requires licensed QNX runtime and dispatch behavior unavailable on this Linux build host.', 805:'Requires Reference Integration documentation ownership and acceptance scope absent from the issue.', 767:'No supplied IPC callback reproducer; broad method/concurrency semantics exceed this bounded tooling queue.', 722:'Recovery policy and multi-subscription reproducer are unspecified; requires safety decisions before implementation.', 695:'Fails inside score_tooling/rules_python integration; dependency upgrade qualification belongs to a separate scoped task.', 694:'Bazel9 dependency/toolchain qualification conflicts with this native Bazel8.7 baseline.', 646:'The cited feature-requirement document is absent from this communication repository baseline.'}
    order = [1236, 1031, 751, 1104]
    write(P / 'authority.json', {'scope': 'Create and execute a sequential queue of suitable open communication bugs using the stable fabric.',
       'user_instruction': 'Use deepseek flash only; $10 total', 'provider': 'deepseek', 'model': 'deepseek-flash', 'fallbacks': [],
       'max_total_cost_usd': 10, 'artifact_destination': str(P), 'fabric_commit': fabric_commit,
       'native_commit': native_commit, 'scratch_root': str(R), 'device': '/dev/loop1',
       'engineering_acceptance': 'pending_offline_review', 'publish_or_push_authorized': False,
       'execution_authority_is_not_engineering_acceptance': True})
    write(P / 'selection.json', {'query': 'repo:eclipse-score/communication is:issue state:open type:Bug',
          'native_commit': native_commit, 'selected': [{'number': n, 'reason': specs[n]['reason']} for n in order],
          'excluded': [{'number': n, 'title': issues[n]['title'], 'reason': reason} for n, reason in excluded.items()]})
    budget = {'authorization_usd': 10, 'prompt_stages_max': 4, 'workflow_retries': 0, 'output_retries': 0,
       'transport_attempts_per_stage_max': 3, 'context_ceiling': 1048576, 'output_ceiling': 384000,
       'input_peak_usd_per_million': .3, 'output_peak_usd_per_million': 1.2, 'reserved_per_stage_usd_micros': 2359296,
       'reserved_queue_upper_usd_micros': 9437184, 'actual_provider_cost_usd': None,
       'pricing_source': 'https://api-docs.deepseek.com/quick_start/pricing/', 'pricing_snapshot_sha256': sha(P / 'deepseek-pricing.html'),
       'basis': 'Reserve full model context and output at peak pricing for all three transport attempts, including reasoning output; no output-token enforcement is assumed.',
       'implicit_title_generation': 'Suppressed by an explicit title in native RunIntent; no LLM title call authorized.',
       'native_catalogue_prices': 'Retained as native source; stale prices are not used for admission.',
       'model_resolution': 'Native configured deepseek-flash alias; provider documents it as DeepSeek-V4.1-Flash.'}
    write(P / 'budget.json', budget)
    write(P / 'budget-ledger.json', {'cap_usd_micros': 10000000, 'reservations': {}, 'actual_provider_cost_usd_micros': None})
    write(P / 'configuration.json', {'scratch_root': str(R), 'native_commit': native_commit, 'fabric_commit': fabric_commit,
       'volume_uuid': '11c42dee-73a3-4c2b-ab42-a0440011d9e0', 'order': order, 'tools': tools,
       'image_id': 'sha256:8332c7a66af3f1cfdb04ce803ce4b7711a976fb2bcbdda3cdae598c96c11fa88'})
    items, prompts = [], {}
    for n in order:
        spec = specs[n]
        tree = R / ('issue-' + str(n))
        if not tree.exists():
            subprocess.run(['git', 'clone', '--no-hardlinks', str(N), str(tree)], check=True, capture_output=True)
            subprocess.run(['git', '-C', str(tree), 'config', 'core.hooksPath', '/dev/null'], check=True)
            subprocess.run(['git', '-C', str(tree), 'switch', '-c', 'fix/communication-' + str(n)], check=True, capture_output=True)
        d = P / 'items' / str(n)
        d.mkdir(parents=True, exist_ok=True)
        write(d / 'issue.json', issues[n])
        paths = sorted(set(['CONTRIBUTING.md', 'LICENSE', 'NOTICE', '.bazelversion'] + spec['context']))
        manifests = []
        prompt = f'''Draft a scoped contribution for eclipse-score/communication#{n}, on native commit {native_commit}.
Return ONLY JSON {{"files":[{{"path":"relative/path","content":"complete replacement content"}}],"rationale":"brief source-grounded reason and unresolved obligations"}}.
No Markdown fences, tools, shell execution, model calls, workflow creation, approval, invented native identifiers or assertions that checks passed.
Put complete source files first; at most 16 files. No deletions. If supplied evidence cannot support a correct fix, return an empty files array and explain the unresolved cause.
Follow CONTRIBUTING.md, preserve licenses and native semantics. Required full native build/tests and lint checks will be measured separately; human engineering acceptance remains offline.
Allowed exact files: {json.dumps(spec['allowed_files'])}. Allowed new directory prefixes: {json.dumps(spec['allowed_prefixes'])}.
This item uses a fresh independent copy of the baseline. Other queue items' patches are not applied; do not assume their changes exist.
{spec['instruction']}
Issue text:\n{issues[n]['body']}\nPinned source context:\n'''
        for path in paths:
            source = N / path
            if not source.is_file():
                continue
            content = source.read_text()
            prompt += '\nFILE ' + path + '\n' + content + '\n'
            dest = d / 'upstream' / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, dest)
            manifests.append({'path': path, 'sha256': sha(source)})
        if n == 1236:
            prompt += '\nReference PR1234 changes (historical context only):\n' + (P / 'buildifier-1234-files.json').read_text()
        if n == 1031:
            for path in sorted((P / 'tooling-context').rglob('*')):
                if path.is_file():
                    prompt += '\nTOOLING FILE @score_tooling2.3.1/' + str(path.relative_to(P / 'tooling-context')) + '\n' + path.read_text() + '\n'
        if len(prompt.encode()) > 180000:
            raise ValueError('Context bound exceeded for ' + str(n))
        (d / 'implementation-prompt.txt').write_text(prompt)
        write(d / 'context-manifest.json', {'native_commit': native_commit, 'files': manifests,
              'tooling_commit_if_applicable': '37043e82df0fdc374caf499cb340abc0d4732302' if n == 1031 else None})
        prompts[n] = prompt
        items.append({'id': 'communication-' + str(n), 'issue_number': n, 'title': issues[n]['title'], 'url': issues[n]['html_url'],
                      'status': 'pending', **{k:v for k,v in spec.items() if k not in {'context','instruction'}},
                      'depends_on': [], 'model': 'deepseek-flash', 'workspace': str(tree)})
    write(P / 'queue-record.json', {'schema_version': 1, 'queue_id': 'communication-bug-queue-20261006',
          'owner': 'Fabro', 'status': 'prepared', 'execution': 'Single sequential Fabro workflow; each item independent at same source pin.',
          'max_total_cost_usd': 10, 'provider': 'deepseek', 'model': 'deepseek-flash', 'items': items,
          'engineering_acceptance': 'pending_offline_review'})
    write(P / 'state.json', {'queue_id': 'communication-bug-queue-20261006', 'status': 'prepared',
          'items': [{'id': i['id'], 'issue_number': i['issue_number'], 'title': i['title'], 'status': 'pending'} for i in items],
          'provider_reported_cost_usd': None, 'notes': 'No paid calls yet; total cap $10. Provider cost remains unknown until reported.'})
    profile = yaml.safe_load((F / 'profiles/deterministic-compiler-v1.yaml').read_text())
    validator = yaml.safe_load((F / 'profiles/fabro-conformance-1b4fb152-v1.yaml').read_text())
    for path, expected in validator['source_hashes'].items():
        raw = subprocess.check_output(['git', '-C', '/home/jefferson/fabro', 'show', PIN + ':' + path])
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Native validator source pin differs')
        dest = P / 'fabro-pin' / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(raw)
    validator['executable_sha256'] = sha(B)
    validator = seal(validator)
    origin = {'kind': 'authorized_human_decision', 'decision_ref': 'user-bug-queue-flash-10-total-20261006',
          'pointer': '/scope', 'rationale': 'User-authorized queue execution only; native applicability and engineering acceptance remain pending.',
          'source_ref': {'path': 'authority.json', 'sha256': sha(P / 'authority.json')}}
    refs = [f'{n}_{stage}' for n in order for stage in ['admit','draft','apply','verify','export']]
    ids = ['local-bugqueue-' + ref for ref in refs]
    plan = seal({'schema_version':1, 'plan_kind':'draft', 'planning_status':'complete','closure_complete':True,
          'engineering_readiness':'not_evaluated', 'target_namespace':'local-operational-bugqueue', 'change':{'id':'communication-bug-queue'},
          'semantic_inputs':{'task_authority':sha(P / 'authority.json')}, 'scopes':[], 'coverage':[], 'findings':[],
          'instances':[{'instance_id':ident,'applicability':'required','effective_disposition':'create','dependency_ids':ids[i-1:i]} for i,ident in enumerate(ids)]})
    actions, support = [], []
    for ref, ident in zip(refs, ids):
        number, stage = ref.split('_')
        draft = stage == 'draft'
        prompt_path = 'prompts/' + number + '.j2'
        action = {'ref':ref, 'purpose':"{% include '" + prompt_path + "' %}" if draft else 'Execute bound host collector '+ref,
           'type':'prompt' if draft else 'deterministic_check','label':ref,'instance_ids':[ident],
           'role':'implementation_drafter' if draft else 'measurement_runner', 'allowed_inputs':['authority.json','budget.json','context-manifest.json'],
           'allowed_paths':[str(R / ('issue-'+number))], 'expected_outputs':[stage+'-result.json'],
           'data_destinations':['provider.deepseek'] if draft else ['local:contribution-artifacts'], 'write_scope':[] if draft else [str(P),str(R)],
           'tool_profile':'none' if draft else 'frozen-host-collector','model_capability':'bounded-agent-v1' if draft else 'none',
           'budget':{'wall_time_seconds':1200 if draft else 14400,'attempts':1,'tool_calls':0 if draft else 20,
                'input_tokens':len(prompts[int(number)].encode()) if draft else 0,'output_tokens':32000 if draft else 0,'cost_microunits':2359296 if draft else 0},
           'completion_predicate':'Output retained; native verification and engineering acceptance remain separate.',
           'evidence_expectation':'Full source-bound native logs, failures, patch and offline review obligations.',
           'fallible_outcomes':['failure','success'],'prohibited_authority':['approval','trusted_evidence_collection','automatic_approval','replayed_approval'],
           'support_files':[], 'origin':origin}
        if draft:
            # Included inside the DOT quoted prompt: retain JSON escaping and
            # prevent GitHub workflow expressions from becoming Jinja code.
            content = '{% raw %}' + json.dumps(prompts[int(number)], ensure_ascii=False)[1:-1] + '{% endraw %}'
            if '{% endraw %}' in prompts[int(number)]:
                raise ValueError('Source contains a template raw-block terminator')
            action['support_files'] = [prompt_path]
            support.append({'path':prompt_path,'content':content,'origin':origin})
        else:
            path='commands/'+ref+'.sh'
            action.update(command_file=path,support_files=[path])
            support.append({'path':path,'content':shlex.join(['env','PYTHONDONTWRITEBYTECODE=1',str(F / '.venv/bin/python'),str(P / 'collector.py'),number,stage])+'\n','origin':origin})
        actions.append(action)
    def edge(a,b,outcome):
        return {'source':a,'target':b,'type':'failure' if outcome=='failure' else 'success','outcome':outcome,
                'condition':None,'loop_id':None,'origin':origin}
    edges = [edge('start', refs[0], None)]
    for i,n in enumerate(order):
        for a,b in zip(['admit','draft','apply','verify'],['draft','apply','verify','export']):
            edges.append(edge(f'{n}_{a}',f'{n}_{b}','success'))
            edges.append(edge(f'{n}_{a}', 'exit' if a=='admit' else f'{n}_export','failure'))
        edges += [edge(f'{n}_export',f'{order[i+1]}_admit' if i+1<len(order) else 'exit','success'), edge(f'{n}_export','exit','failure')]
    mapping = seal({'schema_version':1,'id':'communication-bugqueue-operational','version':1,'plan_version':1,'compiler_profile':profile['id'],
           'review':{'state':'reviewed','reference':{**origin['source_ref'],'scope':'User execution authority; engineering acceptance pending offline review'}},
           'rules':[{'id':'authorized-sequential-bugqueue','instance_ids':ids,'actions':actions}],
           'edges':edges,'loop_policies':[],'fan_groups':[],'support_files':support})
    request={'schema_version':1,'inputs':{},'local_paths':{'output_root':'out','protected_roots':[]}}
    for name,value in {'plan':plan,'execution_mapping':mapping,'compiler_profile':profile,'validator_profile':validator}.items():
        path='plan.json' if name=='plan' else name+'.yaml'
        (P / path).write_text(json.dumps(value,indent=2)+'\n' if name=='plan' else yaml.safe_dump(value))
        request['inputs'][name]={'path':path,'sha256':sha(P / path),'semantic_digest':value['digest']}
    (P / 'compile.yaml').write_text(yaml.safe_dump(request))
    (P / 'out').mkdir(exist_ok=True)
    def measured_validator(files, entrypoint, validator_profile):
        write(P / 'compiler-native-files.json', {'sizes': {k: len(v.encode()) for k,v in files.items()}})
        def runner(command, **kwargs):
            result = subprocess.run(command, **kwargs)
            label = 'version' if 'version' in command else 'validate'
            (P / ('compiler-' + label + '.stdout')).write_text(result.stdout)
            (P / ('compiler-' + label + '.stderr')).write_text(result.stderr)
            return result
        return validate_native(files, entrypoint, validator_profile, runner=runner)
    package=compile_request(P / 'compile.yaml',P / 'out/package.json', native_validator=measured_validator)
    for path,content in package['files'].items():
        dest=P / 'workflow' / path
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(content)
    nodeids={n['label']:n['id'] for n in package['manifest']['ir']['nodes'] if n['label'] in refs}
    write(P / 'node-ids.json',nodeids)
    graph=P / 'workflow/workflow.fabro'
    text=graph.read_text()
    draftids={nodeids[f'{n}_draft'] for n in order}
    text='\n'.join(line.replace(' [',' [output_retries=0, fidelity="summary:high", model="deepseek-flash", provider="deepseek", reasoning_effort="high", ',1)
                   if any(line.strip().startswith(node+' [') for node in draftids) else line for line in text.splitlines())+'\n'
    graph.write_text(text)
    config=P / 'workflow/workflow.toml'
    config.write_text(config.read_text()+'''\n[run.model]\nprovider = "deepseek"\nname = "deepseek-flash"\n[run.model.controls]\nreasoning_effort = "high"\n[run.model.fallbacks]\ndeepseek-flash = []\n[run.clone]\nenabled = false\n[run.run_branch]\nenabled = false\npush = false\n[run.agent]\nfabro_tools = false\n''')
    write(P / 'operational-overlay.json',{'compiled_package_sha256':sha(P / 'out/package.json'),
          'graph_sha256':sha(graph),'config_sha256':sha(config),'prompt_stages_max':4,'output_retries':0,
          'reason':'Explicit Flash-only model controls and no workflow retries, tools, fallback or human approval nodes.'})
    frozen=['collector.py','prepare.py','configuration.json','authority.json','budget.json','queue-record.json','baseline-hashes.json','node-ids.json',
            'workflow/workflow.fabro','workflow/workflow.toml','deepseek-pricing.html']
    frozen += [str(p.relative_to(P)) for p in (P / 'items').rglob('*') if p.is_file()]
    frozen += [str(p.relative_to(P)) for p in (P / 'workflow/commands').rglob('*') if p.is_file()]
    frozen += [str(p.relative_to(P)) for p in (P / 'workflow/prompts').rglob('*') if p.is_file()]
    write(P / 'frozen-inputs.json',{path:sha(P / path) for path in frozen})
    print(json.dumps({'queue':str(P),'source_commit':native_commit,'items':order,'max_cost_usd':10,'reserved_upper_usd':9.437184,
                      'prompt_bytes':{n:len(v.encode()) for n,v in prompts.items()}}))

if __name__ == '__main__':
    main()
