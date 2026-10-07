"""Exact-scope #1104 measurement: issue target //score/mw/com/impl/... minus the two
dev-only cc_build_error_test targets whose shebang-less helper fails under CodeQL tracing
(see offline-followup/DIAGNOSIS-20261007.md). No source change, zero model calls.
Fresh database directories avoid residue from earlier attempts. Failures are retained."""
from pathlib import Path
import json
import sys
from native_measure import P, R, guard, measure, sha, write

D = P / 'evidence4-results'
EXCLUDED = ['//score/mw/com/impl/util/test:arithmetic_utils_addition_build_error_test',
            '//score/mw/com/impl/util/test:arithmetic_utils_multiplication_build_error_test']
# One argv element: argparse keeps a space-containing value positional; codeql_lint joins
# it into its shell command, so Bazel receives "-- //score/mw/com/impl/... -<excluded>...".
TARGET = ' '.join(['--', '//score/mw/com/impl/...'] + ['-' + t for t in EXCLUDED])
SUBJECTS = {
    'baseline': (R / 'baseline-check', R / 'codeql-baseline-v2/impl-no-build-error'),
    'candidate-1104': (R / 'issue-1104', R / 'codeql-candidate/1104-impl-no-build-error'),
}


def run(label, tree, args, timeout):
    D.mkdir(exist_ok=True)
    result = measure(D, tree, label, args, timeout)
    print(json.dumps(result), flush=True)
    return result


def placeholder_summary(output):
    reports = []
    for path in sorted(output.rglob('*.sarif')):
        counts, samples, results, locations = {}, [], 0, 0

        def visit(value, pointer, rule=None):
            nonlocal locations
            if isinstance(value, dict):
                rule = value.get('ruleId', rule)
                if 'physicalLocation' in value:
                    locations += 1
                if value.get('uri') in {'file:/', 'file:///', ''}:
                    counts[value['uri']] = counts.get(value['uri'], 0) + 1
                    if len(samples) < 8:
                        samples.append({'pointer': pointer, 'rule_id': rule, 'artifact_location': value})
                for key, item in value.items():
                    visit(item, pointer + '/' + key, rule)
            elif isinstance(value, list):
                for index, item in enumerate(value):
                    visit(item, pointer + '/' + str(index), rule)

        data = json.loads(path.read_text())
        for run_ in data.get('runs', []):
            results += len(run_.get('results', []))
        visit(data, '')
        reports.append({'report': str(path), 'sha256': sha(path), 'results': results,
                        'physical_locations': locations, 'root_or_empty_uris': counts,
                        'bounded_samples': samples, 'paths_synthesized': False})
    return reports


def subject(name):
    tree, database = SUBJECTS[name]
    if database.exists():
        raise FileExistsError('Refusing to reuse database directory: ' + str(database))
    output = database.with_name(database.name + '-reports')
    summary = {'subject': name, 'tree': str(tree), 'database': str(database), 'target': TARGET,
               'excluded_targets': EXCLUDED, 'paid_calls': 0, 'source_changed': False,
               'engineering_acceptance': 'pending_offline_review'}
    created = run(name + '-codeql-create-impl', tree,
                  ['run', '//quality/static_analysis:codeql_lint', '--', '--phase', 'create-database',
                   '--database-path', str(database), '--target', TARGET], 3600)
    summary['create'] = created
    if created['exit_code'] == 0:
        analyzed = run(name + '-codeql-analyze-impl', tree,
                       ['run', '//quality/static_analysis:codeql_lint', '--', '--phase', 'analyze-database',
                        '--database-path', str(database), '--output-dir', str(output),
                        '--output-prefix', name + '-impl'], 3600)
        summary['analyze'] = analyzed
        if output.exists():
            summary['reports'] = placeholder_summary(output)
    write(D / (name + '-summary.json'), summary)
    return summary


if __name__ == '__main__':
    guard()
    for name in sys.argv[1:] or list(SUBJECTS):
        if subject(name).get('analyze', {}).get('exit_code') != 0:
            print('stopping after failed or missing analysis: ' + name, flush=True)
            break
