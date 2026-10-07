"""Analyze-phase rerun for the baseline exact-scope database after the first attempt hit
evidence4.py's own 3600 s bound at query 215/218 (exit 137, record retained). Same command,
fresh output directory, longer bound. No source change, zero model calls."""
import json
from evidence4 import D, R, SUBJECTS, placeholder_summary, run, write
from native_measure import guard

if __name__ == '__main__':
    guard()
    tree, database = SUBJECTS['baseline']
    output = database.with_name(database.name + '-reports-rerun')
    if output.exists():
        raise FileExistsError('Refusing to reuse output directory: ' + str(output))
    previous = json.loads((D / 'baseline-summary.json').read_text())
    analyzed = run('baseline-codeql-analyze-impl-rerun', tree,
                   ['run', '//quality/static_analysis:codeql_lint', '--', '--phase', 'analyze-database',
                    '--database-path', str(database), '--output-dir', str(output),
                    '--output-prefix', 'baseline-impl'], 7200)
    summary = {**previous, 'previous_analyze_attempt': previous.get('analyze'), 'analyze': analyzed,
               'rerun_reason': 'first analyze attempt exceeded the measurement script own 3600 s bound at 215/218'}
    if output.exists():
        summary['reports'] = placeholder_summary(output)
    write(D / 'baseline-summary-rerun.json', summary)
