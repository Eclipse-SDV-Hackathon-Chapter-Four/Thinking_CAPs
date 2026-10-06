"""Prepare one issue-scoped run with the frozen, pre-011 fabric compiler."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import urllib.request

import yaml
from score_sw_fabric.compiler.package import compile_request
from score_sw_fabric.compiler.reader import semantic_digest
from score_sw_fabric.storage import validate_run_root

HERE = Path(__file__).resolve().parent
SCRATCH = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha')
FABRIC = SCRATCH / 'fabric'
BINARY = Path('/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro')
PIN = '1b4fb15281ebb724426f9e480dce48d0100ff79b'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def write(p, value):
    p.write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')

def seal(value):
    value = {k: v for k, v in value.items() if k != 'digest'}
    return {**value, 'digest': semantic_digest(value)}

def main():
    validate_run_root(SCRATCH)
    if subprocess.check_output(['findmnt', '-n', '-o', 'SOURCE', '-T', str(SCRATCH)], text=True).strip() != '/dev/loop27':
        raise ValueError('Owner-selected loop27 is not the scratch filesystem')
    stable_sha = subprocess.check_output(['git', '-C', str(FABRIC), 'rev-parse', 'HEAD'], text=True).strip()
    if not stable_sha.startswith('b2aa9a7') or (FABRIC / 'src/score_sw_fabric/optimization').exists():
        raise ValueError('Expected the unmodified pre-optimization compiler')
    candidate = HERE / 'candidate'
    if not candidate.exists():
        shutil.copytree(SCRATCH / 'communication', candidate, symlinks=True)
    native_sha = subprocess.check_output(['git', '-C', str(candidate), 'rev-parse', 'HEAD'], text=True).strip()
    for name in ['LICENSE', 'NOTICE', 'CONTRIBUTING.md', '.bazelversion', '.bazelrc', 'CI.md']:
        dest = HERE / 'upstream' / name
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(candidate / name, dest)
    request = urllib.request.Request('https://api.github.com/repos/eclipse-score/communication/issues/1167', headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'score-fabric-1167'})
    issue = json.load(urllib.request.urlopen(request, timeout=20))
    write(HERE / 'upstream/issue.json', issue)
    shutil.copyfile(SCRATCH / 'storage-selection.json', HERE / 'storage-selection.json')
    write(HERE / 'authority.json', {
        'scope': 'Create an isolated draft fix run for eclipse-score/communication#1167 using the non-optimized fabric',
        'user_authorization': 'Use the existing configured model, maximum $10',
        'artifact_destination': str(HERE), 'scratch_root': str(SCRATCH),
        'selected_loop_device': '/dev/loop27', 'fabric_commit': stable_sha,
        'target_commit': native_sha, 'provider': 'deepseek', 'model': 'deepseek-v4-flash',
        'fallbacks': [], 'max_total_cost_usd': 10, 'engineering_acceptance': 'pending_offline_review',
        'publication_authorized': False, 'native_requirement_ids': [],
        'native_id_status': 'No native requirement IDs supplied by the issue; applicability unaccepted',
    })
    # A single prompt stage has no tool loop, no workflow retries, no output repairs,
    # no fallback and at most three transport attempts in the pinned client.
    # Reserve the full published model context and full output, even though output
    # is explicitly limited to 32,000 tokens. Peak rates are the conservative rates.
    write(HERE / 'budget.json', {
        'authorization_usd': 10, 'prompt_stages': 1, 'workflow_attempts': 1,
        'output_retries': 0, 'transport_max_attempts': 3,
        'context_ceiling': 1048576, 'output_limit': 32000,
        'conservative_output_ceiling': 384000,
        'peak_input_usd_per_million': 0.3, 'peak_output_usd_per_million': 1.2,
        'reserved_upper_cost_usd': 3 * (1048576 * .3 + 384000 * 1.2) / 1000000,
        'pricing_source': 'https://api-docs.deepseek.com/quick_start/pricing/',
        'actual_usage': None, 'actual_cost': None,
        'usage_note': 'Native catalogue prices are stale; retain native usage and independently price it using the provider rates',
    })
    origin = {
        'kind': 'authorized_human_decision',
        'source_ref': {'path': 'authority.json', 'sha256': sha(HERE / 'authority.json')},
        'pointer': '/scope', 'decision_ref': 'user-communication1167-run-20261005',
        'rationale': 'Task execution authorized; engineering review remains outside Fabro',
    }
    selected = ['CONTRIBUTING.md', 'score/mw/com/test/pkg_application.bzl',
                'score/mw/com/test/common_test_resources/test_interface.h',
                'score/mw/com/test/common_test_resources/proxy_observer.h',
                'score/mw/com/test/common_test_resources/fail_test.h',
                'score/mw/com/test/common_test_resources/sctf_test_runner.h',
                'score/mw/com/impl/proxy_base.h', 'score/mw/com/impl/skeleton_base.h',
                'score/mw/com/impl/proxy_event.h', 'score/mw/com/types.h']
    for tree in ['score/mw/com/test/service_discovery_offer_and_search',
                 'score/mw/com/test/all_service_elements']:
        selected += [str(p.relative_to(candidate)) for p in (candidate / tree).rglob('*')
                     if p.is_file() and p.suffix in {'.cpp', '.h', '.json', '.py'} or p.is_file() and p.name == 'BUILD']
    selected = sorted(set(p for p in selected if (candidate / p).is_file()))
    contexts = [{'path': p, 'sha256': sha(candidate / p)} for p in selected]
    write(HERE / 'context-manifest.json', {'fabric_commit': stable_sha, 'target_commit': native_sha, 'files': contexts})
    prefix = '''Implement eclipse-score/communication issue #1167 as a draft C++17 contribution.
Return ONLY JSON with keys files (array of {path, content}), rationale (string), assumptions (array of strings).
Write one dedicated integration test under score/mw/com/test/api_idempotency/ with an application, configuration,
BUILD targets and the native Python integration harness. Never modify production code or existing tests.
Cover OfferService, StopOfferService, StartFindService, Subscribe, Unsubscribe.
Each API must be called repeatedly and checked for the native documented behavior, errors and functional state.
Use real LoLa objects and integration macros, not mocked APIs. Include bounded waits and explicit failing exits.
Verify service remains discoverable and usable after duplicate offers; discovery absent after repeated stops;
repeat StartFindService registrations and verify discovery results without incorrectly asserting equal registration handles;
clean up every registration with StopFindService. Duplicate Subscribe uses the same sample limit, preserve the subscribed
state and prove real sample reception; repeated Unsubscribe preserves unsubscribed state and re-subscription works.
Respect asynchronous subscription and discovery; use synchronization with finite deadlines rather than arbitrary sleeps.
Use the supplied source examples and their actual public API signatures. Keep configuration self-contained and valid.
Preserve upstream license headers and follow CONTRIBUTING.md. Do not claim tests passed, acceptance or issue closure.
The only permitted new paths are below score/mw/com/test/api_idempotency/. No shell scripts, CI changes, fake IDs or approvals.
Issue text follows:\n'''
    prompt = prefix + issue['body'] + '\n\nPinned native source context:\n'
    for p in selected:
        prompt += '\nFILE ' + p + '\n' + (candidate / p).read_text() + '\n'
    if len(prompt.encode()) > 400000:
        raise ValueError('Prompt exceeds bounded source envelope')
    (HERE / 'implementation-prompt.txt').write_text(prompt)
    refs = ['admit', 'draft', 'apply', 'verify', 'export']
    ids = ['local-communication1167-' + ref for ref in refs]
    plan = seal({'schema_version': 1, 'plan_kind': 'draft', 'planning_status': 'complete',
        'closure_complete': True, 'engineering_readiness': 'not_evaluated',
        'target_namespace': 'local-operational-communication1167', 'change': {'id': 'communication1167'},
        'semantic_inputs': {'task_authority': sha(HERE / 'authority.json')}, 'scopes': [], 'coverage': [], 'findings': [],
        'instances': [{'instance_id': name, 'applicability': 'required', 'effective_disposition': 'create',
                       'dependency_ids': ids[i-1:i]} for i, name in enumerate(ids)]})
    profile = yaml.safe_load((FABRIC / 'profiles/deterministic-compiler-v1.yaml').read_text())
    validator = yaml.safe_load((FABRIC / 'profiles/fabro-conformance-1b4fb152-v1.yaml').read_text())
    (HERE / 'fabro-pin').mkdir(exist_ok=True)
    for name, expected in validator['source_hashes'].items():
        raw = subprocess.check_output(['git', '-C', '/home/jefferson/fabro', 'show', PIN + ':' + name])
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError('Pinned native validator source differs: ' + name)
        dest = HERE / 'fabro-pin' / name
        dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(raw)
    validator['executable_sha256'] = sha(BINARY); validator = seal(validator)
    actions, support = [], []
    for i, ref in enumerate(refs):
        draft = ref == 'draft'
        action = {'ref': ref, 'purpose': prompt if draft else 'Run frozen host collector: ' + ref,
            'type': 'prompt' if draft else 'deterministic_check', 'label': ref,
            'instance_ids': [ids[i]], 'role': 'implementation_drafter' if draft else 'measurement_runner',
            'allowed_inputs': ['authority.json', 'context-manifest.json', 'budget.json'],
            'allowed_paths': [str(candidate), str(SCRATCH)],
            'expected_outputs': [ref + '-result.json'], 'data_destinations': ['provider.deepseek'] if draft else ['local:contribution-artifacts'],
            'write_scope': [] if draft else [str(HERE), str(SCRATCH)],
            'tool_profile': 'none' if draft else 'frozen-host-collector',
            'model_capability': 'bounded-agent-v1' if draft else 'none',
            'budget': {'wall_time_seconds': 1200 if draft else 14400, 'attempts': 1,
                'tool_calls': 0 if draft else 20, 'input_tokens': len(prompt.encode()) if draft else 0,
                'output_tokens': 32000 if draft else 0, 'cost_microunits': 10000000 if draft else 0},
            'completion_predicate': 'Draft output retained' if draft else 'Original measured results retained; acceptance pending',
            'evidence_expectation': 'Native model output and measured logs, hashes and failures',
            'fallible_outcomes': ['failure', 'success'],
            'prohibited_authority': ['approval', 'trusted_evidence_collection', 'automatic_approval', 'replayed_approval'],
            'support_files': [], 'origin': origin}
        if not draft:
            path = 'commands/' + ref + '.sh'
            action.update(command_file=path, support_files=[path])
            support.append({'path': path, 'content': 'true\n', 'origin': origin})
        actions.append(action)
    def edge(source, target, outcome):
        return {'source': source, 'target': target, 'type': 'failure' if outcome == 'failure' else 'success',
                'outcome': outcome, 'condition': None, 'loop_id': None, 'origin': origin}
    edges = [edge('start', 'admit', None)]
    for a, b in zip(refs, refs[1:]):
        edges.append(edge(a, b, 'success'))
    for ref in refs[:-1]:
        edges.append(edge(ref, 'export', 'failure'))
    edges.append(edge('export', 'exit', 'success'))
    edges.append(edge('export', 'exit', 'failure'))
    mapping = seal({'schema_version': 1, 'id': 'communication1167-operational', 'version': 1, 'plan_version': 1,
        'compiler_profile': profile['id'], 'review': {'state': 'reviewed', 'reference': {**origin['source_ref'],
        'scope': 'User-authorized operational task; engineering applicability/review pending'}},
        'rules': [{'id': 'authorized-operational-execution', 'instance_ids': ids, 'actions': actions}],
        'edges': edges, 'loop_policies': [], 'fan_groups': [], 'support_files': support})
    selections = {'plan': plan, 'execution_mapping': mapping, 'compiler_profile': profile, 'validator_profile': validator}
    request = {'schema_version': 1, 'inputs': {}, 'local_paths': {'output_root': 'out', 'protected_roots': ['candidate']}}
    for name, value in selections.items():
        path = 'plan.json' if name == 'plan' else name + '.yaml'
        (HERE / path).write_text(json.dumps(value, indent=2) + '\n' if name == 'plan' else yaml.safe_dump(value))
        request['inputs'][name] = {'path': path, 'sha256': sha(HERE / path), 'semantic_digest': value['digest']}
    (HERE / 'out').mkdir(exist_ok=True)
    (HERE / 'compile.yaml').write_text(yaml.safe_dump(request))
    package = compile_request(HERE / 'compile.yaml', HERE / 'out/package.json')
    for name, content in package['files'].items():
        path = HERE / 'workflow' / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text(content)
    node_ids = {node['label']: node['id'] for node in package['manifest']['ir']['nodes'] if node['label'] in refs}
    write(HERE / 'node-ids.json', node_ids)
    workflow = HERE / 'workflow/workflow.fabro'
    native = workflow.read_text()
    draft_id = node_ids['draft']
    native = '\n'.join(line.replace(' [', ' [output_retries=0, ') if line.strip().startswith(draft_id + ' [') else line for line in native.splitlines()) + '\n'
    workflow.write_text(native)
    entry = HERE / 'workflow/workflow.toml'
    text = entry.read_text() + '''
[run.model]
provider = "deepseek"
name = "deepseek-v4-flash"
[run.model.fallbacks]
deepseek-v4-flash = []
[run.clone]
enabled = false
[run.run_branch]
enabled = false
push = false
[run.agent]
fabro_tools = false
'''
    python = str(FABRIC / '.venv/bin/python')
    for label in ['admit', 'apply', 'verify', 'export']:
        text += '\n[[run.hooks]]\nid = ' + json.dumps('communication1167-' + label) + '\nevent = "stage_start"\n'
        text += 'matcher = ' + json.dumps('^' + node_ids[label] + '$') + '\nblocking = true\nsandbox = false\ntimeout = "14400s"\n'
        text += 'command = ' + json.dumps([python, str(HERE / 'collector.py'), label]) + '\n'
    entry.write_text(text)
    write(HERE / 'operational-overlay.json', {'compiled_package_sha256': sha(HERE / 'out/package.json'),
        'native_workflow_sha256': sha(workflow), 'native_entrypoint_sha256': sha(entry),
        'reason': 'Host collectors and one output-repair-free prompt; no interview or approval nodes'})
    print(json.dumps({'contribution': str(HERE), 'fabric_commit': stable_sha, 'target_commit': native_sha,
                      'prompt_bytes': len(prompt.encode()), 'nodes': node_ids}))

if __name__ == '__main__':
    main()
