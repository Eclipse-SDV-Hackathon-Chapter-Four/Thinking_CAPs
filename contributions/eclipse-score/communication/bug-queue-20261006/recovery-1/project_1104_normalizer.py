"""Projection (not a candidate measurement): apply the #1104 candidate's own SARIF
placeholder normalizer, loaded by AST from the exact candidate source, to a copy of the
baseline exact-scope SARIF. Reports counts before/after and finding preservation."""
from pathlib import Path
import ast
import hashlib
import json
import os
import shutil
import sys

R = Path('/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-communication-bug-recovery-fw8j963z')
P = Path(__file__).resolve().parent
SOURCE = R / 'issue-1104/quality/static_analysis/codeql_lint.py'
NAMES = {'PLACEHOLDER_URIS', '_normalize_placeholder_artifact_locations', 'normalize_sarif_placeholder_locations'}
PLACEHOLDERS = {'file:/', 'file:', 'file:///', ''}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_normalizer():
    tree = ast.parse(SOURCE.read_text())
    nodes = [n for n in tree.body
             if (isinstance(n, ast.FunctionDef) and n.name in NAMES)
             or (isinstance(n, ast.Assign) and any(getattr(t, 'id', None) in NAMES for t in n.targets))]
    found = {n.name if isinstance(n, ast.FunctionDef) else n.targets[0].id for n in nodes}
    if found != NAMES:
        raise ValueError('Candidate normalizer definitions missing: ' + str(NAMES - found))
    namespace = {'json': json, 'os': os, 'shutil': shutil}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), namespace)
    return namespace['normalize_sarif_placeholder_locations']


def count(sarif):
    placeholders, results, rules, unavailable = 0, 0, {}, 0

    def visit(value, rule=None):
        nonlocal placeholders, unavailable
        if isinstance(value, dict):
            rule = value.get('ruleId', rule)
            if value.get('uri') in PLACEHOLDERS and not (value.get('uri') == '' and value.get('uriBaseId')):
                placeholders += 1
                rules[str(rule)] = rules.get(str(rule), 0) + 1
            if value.get('properties', {}).get('score.artifactLocationUnavailable'):
                unavailable += 1
            for item in value.values():
                visit(item, rule)
        elif isinstance(value, list):
            for item in value:
                visit(item, rule)

    for run in sarif.get('runs', []):
        results += len(run.get('results', []))
    visit(sarif)
    return {'results': results, 'placeholder_uris': placeholders, 'placeholder_by_rule': rules,
            'marked_location_unavailable': unavailable}


def main(baseline_sarif, out_dir):
    baseline_sarif, out_dir = Path(baseline_sarif), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=False)
    projected = out_dir / 'projected-candidate-1104.sarif'
    shutil.copyfile(baseline_sarif, projected)
    before = json.loads(projected.read_text())
    load_normalizer()(str(projected))
    after = json.loads(projected.read_text())
    ids = lambda s: [(r.get('ruleId'), r.get('message', {}).get('text')) for run in s['runs'] for r in run.get('results', [])]
    record = {
        'kind': 'projection_not_candidate_measurement',
        'limits': 'Candidate patch changes no extraction or query selection; in the candidate the normalizer '
                  'runs before recategorization, here it runs on the already recategorized baseline report. '
                  'Recategorization does not touch locations. No candidate database or analysis was run.',
        'candidate_source': str(SOURCE), 'candidate_source_sha256': sha(SOURCE),
        'baseline_sarif': str(baseline_sarif), 'baseline_sarif_sha256': sha(baseline_sarif),
        'projected_sarif_sha256': sha(projected),
        'before': count(before), 'after': count(after),
        'results_preserved_in_order': ids(before) == ids(after),
        'paths_synthesized': False, 'paid_calls': 0, 'source_changed': False,
        'engineering_acceptance': 'pending_offline_review',
    }
    (out_dir / 'projection-summary.json').write_text(json.dumps(record, indent=1, sort_keys=True) + '\n')
    print(json.dumps({k: record[k] for k in ('before', 'after', 'results_preserved_in_order')}, indent=1))


if __name__ == '__main__':
    main(*sys.argv[1:3])
