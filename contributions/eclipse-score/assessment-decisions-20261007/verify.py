#!/usr/bin/env python3
"""Verify the frozen decision packet offline; confer no engineering acceptance."""

import argparse
import hashlib
import json
from pathlib import Path
import re


PACKET = Path(__file__).resolve().parent
ROOT = PACKET.parents[1]


def read(name):
    return json.loads((PACKET / name).read_text())


def check_files(base, files):
    for relative, expected in files.items():
        path = (base / relative).resolve()
        if not path.is_relative_to(base.resolve()):
            raise ValueError(f"Path escapes binding root: {relative}")
        data = path.read_bytes()
        if len(data) != expected['size_bytes']:
            raise ValueError(f"Size mismatch: {relative}")
        if hashlib.sha256(data).hexdigest() != expected['sha256']:
            raise ValueError(f"SHA-256 mismatch: {relative}")


def verify(content_only=False):
    inputs = read('input-bindings.json')['files']
    check_files(ROOT, inputs)
    packet = read('decisions.json')
    decisions = packet['decisions']
    selection = {item['id']: item for item in read('registry-selection.json')['issues']}
    ids = [item['issue'] for item in decisions]
    if len(ids) != len(set(ids)) or set(ids) != set(selection):
        raise ValueError('Decision coverage does not match frozen registry selection')
    if packet['completed_fix_count_delta'] != 0 or packet['native_status_changes'] or packet['native_tests_rerun']:
        raise ValueError('Packet claims work or status changes outside assessment scope')
    for item in decisions:
        selected = selection[item['issue']]
        if item['baseline_commit'] != selected['baseline_commit'] or item['local_status'] != selected['local_status']:
            raise ValueError(f"Selected evidence baseline/status mismatch: {item['issue']}")
        human = item['human_decision']
        if human['status'] != 'pending' or any(value is not None for key, value in human.items() if key != 'status'):
            raise ValueError(f"Unexpected human decision in frozen proposal: {item['issue']}")
        if item['completed_fix_claim'] or item['submission_candidate'] or selected['submission_candidate']:
            raise ValueError(f"Unexpected completed-fix/submission claim: {item['issue']}")
        if not item['required_inputs'] or not item['proposed_reviewer_roles'] or not item['alternatives']:
            raise ValueError(f"Incomplete decision proposal: {item['issue']}")
        if not all(path in inputs for path in item['evidence_paths']):
            raise ValueError(f"Unbound decision evidence: {item['issue']}")
        upstream = read(item['upstream_observation']['capture'])
        if upstream['html_url'] != selected['issue_url'] or upstream['state'] != item['upstream_observation']['state']:
            raise ValueError(f"Upstream identity/state mismatch: {item['issue']}")
    template = read('acceptance-record-template.json')
    if not template['template_only'] or template['completed_fix_claim']:
        raise ValueError('Acceptance template supplies an actual decision or fix claim')
    for key, value in template.items():
        if key not in ['schema', 'template_only', 'completed_fix_claim'] and value not in [None, []]:
            raise ValueError(f"Unexpected prefilled acceptance field: {key}")
    links = 0
    for match in re.finditer(r'\[[^\]]+\]\(([^)]+)\)', (PACKET / 'README.md').read_text()):
        target = match.group(1)
        if target.startswith(('https://', 'http://', '#')):
            continue
        if content_only and target == 'artifact-manifest.json':
            # The final manifest is created after the content receipt is written.
            continue
        path = (PACKET / target.split('#')[0]).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file():
            raise ValueError(f"Missing or external local document link: {target}")
        links += 1
    retrievals = read('upstream/retrievals.json')
    recovered = {row['url'] for row in retrievals if row.get('http_status') == 200}
    for row in retrievals:
        if 'error' in row and row['url'] not in recovered:
            raise ValueError(f"Unrecovered upstream retrieval: {row['url']}")
    files = read('artifact-manifest.json')['files'] if not content_only else {}
    check_files(PACKET, files)
    return {
        'status': 'verified',
        'scope': 'packet coverage, links, selected input integrity and pending decisions; native tests not rerun; engineering acceptance not granted',
        'decisions': len(decisions),
        'input_bindings': len(inputs),
        'local_document_links': links,
        'retained_retrieval_failures': sum('error' in row for row in retrievals),
        'unrecovered_retrievals': 0,
        'packet_manifest_files': len(files) if not content_only else None,
        'manifest_checked': not content_only,
        'completed_fix_count_delta': 0,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content-only', action='store_true', help='Check content before sealing the final manifest')
    args = parser.parse_args()
    try:
        result = verify(args.content_only)
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(json.dumps({'status': 'failed', 'error': str(error)}, indent=2))
        raise SystemExit(1)
    print(json.dumps(result, indent=2))
