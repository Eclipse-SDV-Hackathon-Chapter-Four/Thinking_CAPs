# Verification — 2026-10-07

Subject: clean chatbot commit `72c1fb2cab280e6835513b046013e5abea066c3a`;
[source archive and per-file binding](evidence/source/source-manifest.json).
Fresh checks ran against a disposable extraction on Linux x86-64. Python 3.12.14,
pytest 9.1.1, ruff 0.16.9, mypy 2.3.1, Node 20.20.2 and npm 10.8.2 were measured.
Existing virtualenv/frontend dependencies were reused without installing or updating.

| Check | Recorded result | Evidence |
| --- | --- | --- |
| Backend deterministic suite, initial full run | 1230 passed, 4 failed, 10 skipped; 257.72 s | [Raw log](evidence/checks/pytest.log), [JUnit](evidence/checks/pytest.xml) |
| Timer module after environment correction | 9 passed; 0.35 s; covers all 4 failed cases and 5 already-passing cases | [Rerun log](evidence/checks/pytest-timer-rerun.log), [command and setup](evidence/checks/pytest-timer-rerun.json) |
| Frontend tests | 76 passed; no failures/errors | [JUnit](evidence/checks/vitest.xml), [log](evidence/checks/frontend-tests.log) |
| Ruff format and lint | Pass; 502 files formatted | [format](evidence/checks/ruff-format.log), [lint](evidence/checks/ruff-lint.log) |
| Mypy | Pass; 147 source files | [log](evidence/checks/mypy.log) |
| Dependency license allowlist | Pass; 470 packages | [log](evidence/checks/licenses.log) |
| Product traceability | Pass; every local requirement mapped, public requirements deferred | [log](evidence/checks/traceability.log) |
| Frontend lint, types, build | Pass | [lint](evidence/checks/frontend-lint.log), [types](evidence/checks/frontend-typecheck.log), [build](evidence/checks/frontend-build.log) |
| External assets and telemetry checks | Pass | [assets](evidence/checks/frontend-assets.log), [telemetry](evidence/checks/frontend-telemetry.log) |
| Original and disposable source inputs after checks | Clean original source; all 655 tracked input hashes unchanged | [initial after-check](evidence/checks/source-after.json), [after-rerun](evidence/checks/source-after-rerun.json) |
| Original historical release manifest | All 17 artifacts copied with matching original sizes/hashes | [original manifest](evidence/historical/local-release-1.0.0/release-manifest.json) |
| Scoped packet/source/original-release verifier | Pass; 266 packet files, 655 archived source files, 17 historical artifacts | `python3 contributions/eclipse-score/score/2850/verify_packet.py` |
| Entire contribution registry verifier | Fail: inherited upstream observation mismatch for diagnostics #16; stops before new entry | [raw result](evidence/checks/repository-verifier.log), [command record](evidence/checks/repository-verifier.json) |

The four initial failures all came from the timer installer requiring the copied
project's `.venv/bin/score-assistant`. The first full run supplied dependencies through
PATH/PYTHONPATH but lacked that project-local path. A symlink to the existing prepared
environment corrected the setup. Only the affected nine-test module was rerun; there
was no source change or full-suite rerun. Across those runs all 1234 non-skipped backend
cases have a passing observation, but the initial full-run exit status remains failure.
The 10 skips are one GitHub-network test and nine real-Ollama tests.

The source archive is bound to the clean commit; isolated copies kept the original code.
Mock systemctl commands and temporary unit directories were used by timer tests; these
tests did not enable a timer on the owner's machine.

## Historical and unavailable checks

The [historical reports](evidence/historical/reports/) include held-out model runs,
retrieval/citation metrics, adversarial tests, blocked-egress checks, browser/deployment
results, human review records and performance reports. They were copied and hashed,
not rerun on the current chatbot commit. The retained local release report JSON records
43 pass gates and one optional public-profile gate not run; the prose release notes
claim 44 passing gates. Preserve that discrepancy.

Original human support/coverage metrics were based on blanket owner acceptance.
Citation validity and heuristic adversarial checks do not establish factual accuracy,
safety certification or maintainer approval. Older verification records retain the
earlier injection failure, unexplained transient test failures, failed performance
targets and superseded blocked release decisions.

Native #2850 interface conformance, CR-001–CR-005, gate scenario corpus, trace schemas,
outer loop, traceability_coverage.py, traceability_gate.py and target CI: **not run;
adapter and native integration not implemented**. Current GitHub CI success was not
established by the bounded connector query. No fresh real-model, GPU, browser,
container, screen-reader, blocked-egress or public-hosting checks were performed.

The capture itself initially stopped twice before executing checks (a null historical
evidence reference, then a read-only retained file on retry). Both collection errors
and their fixes are recorded in [collection-attempts.json](evidence/checks/collection-attempts.json).
They are separate from product test failures.

