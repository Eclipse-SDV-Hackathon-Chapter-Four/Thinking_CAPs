# <Project> #<issue> — <specific contribution>

| Field | Record |
| --- | --- |
| Upstream issue | <canonical URL> |
| Local status | evidence_missing / implemented_locally / scoped_fix_verified |
| Upstream status and observation date | <state, YYYY-MM-DD> |
| Baseline commit | <full SHA> |
| Implementation source | <repository, revision, local changes, tool/workflow> |
| Upstream PR / merge | <actual URL and commit, or pending> |

## Problem and fix

Describe the observed failure, reproduction and resulting behavior. State the
exact solved scope and any remaining obligations under the upstream issue.

## Evidence and artifacts

Link the patch, candidate hashes, original command records, raw logs, test results,
screenshots/datasets where relevant, baseline identity, licenses and notices.
Record the checks actually performed, failed attempts, exclusions and limitations.
Keep implementation, test success, human approval and upstream merge distinct.

## Provenance and reproducibility

Record where the bytes originated and when they were captured. Add
`artifact-manifest.json` with an SHA-256 `files` mapping of relative paths.
Explain how to reproduce relevant checks in an isolated checkout and what tools
or platforms are required. Add a `registry.json` entry with paths relative to
`contributions/`, then run `python3 scripts/verify_contributions.py`.

## Later upstream PR

Provide a title/body draft, target project and review/CI actions. Once submitted,
record actual PR, review, merge and issue-closure evidence.
