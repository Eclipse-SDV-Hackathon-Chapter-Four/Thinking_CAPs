"""Analyze-phase rerun for the baseline exact-scope database after the first attempt hit
evidence4.py's own 3600 s bound at query 215/218 (exit 137, record retained). Same command,
fresh output directory, longer bound. No source change, zero model calls."""
import json
import sys
from evidence4 import D, R, SUBJECTS, placeholder_summary, run, write
from native_measure import guard

if __name__ == '__main__':
    attempt = sys.argv[1] if len(sys.argv) > 1 else '1'
    bound = int(sys.argv[2]) if len(sys.argv) > 2 else 7200
    suffix = '' if attempt == '1' else '-' + attempt
    guard()
    tree, database = SUBJECTS['baseline']
    output = database.with_name(database.name + '-reports-rerun' + suffix)
    if output.exists():
        raise FileExistsError('Refusing to reuse output directory: ' + str(output))
    previous = json.loads((D / 'baseline-summary.json').read_text())
    if suffix:
        previous['rerun_attempt_1'] = json.loads((D / 'evidence/baseline-codeql-analyze-impl-rerun.json').read_text()).get('stop_reason')
    analyzed = run('baseline-codeql-analyze-impl-rerun' + suffix, tree,
                   ['run', '//quality/static_analysis:codeql_lint', '--', '--phase', 'analyze-database',
                    '--database-path', str(database), '--output-dir', str(output),
                    '--output-prefix', 'baseline-impl'], bound)
    summary = {**previous, 'previous_analyze_attempt': previous.get('analyze'), 'analyze': analyzed,
               'rerun_reason': 'first analyze attempt exceeded the measurement script own 3600 s bound at 215/218'}
    if output.exists():
        summary['reports'] = placeholder_summary(output)
    write(D / ('baseline-summary-rerun' + suffix + '.json'), summary)
