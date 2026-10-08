# Measured verification after license cleanup

The current patches include the repository-wide license cleanup requested on
2026-10-07. Every current code file is covered by the independent audit; native
copyright checks scan the complete repository. Existing numeric copyright years
and imported MIT/CC0 terms are retained. Before-state sources, patches, failures
and measurements remain in `license-header-history` and the original evidence.

| Check | Result | Evidence |
| --- | --- | --- |
| All current code headers | 2858 repository files and 13 packet helpers; zero missing notices | `license-header-audit.json` |
| Communication native copyright | Passed; all original 198 errors addressed | `license-headers-communication-copyright-verified` |
| Config Management native copyright | Passed over complete repository | `license-headers-config-management-copyright-final-lock` |
| Host tests | 508 passed, 7 skipped | `license-headers-host-tests`, `license-final-host-summary.json` |
| Formatting / buildifier / full build | Passed on final licensed source | `license-headers-format`, `license-headers-buildifier`, `license-headers-all-build` |
| Fresh production extraction | 516/516 configured C++ inputs present and byte-matched | `license-headers-production-extraction`, `license-final-compile-source-coverage.json` |
| Full analyzer and native reports | 218 queries; 2127 findings; zero empty file URI occurrences | `license-headers-native-analyzer-reporting-verified`, `license-final-suite-summary.json` |
| Patch applicability | Both patches apply to their pinned upstream revisions | `license-final-patch-applicability.json` |
| Exact-scope #1104 regression | Final licensed query retains all 501 baseline findings and removes 281 empty URI occurrences | `license-final-location-comparison.json` |

Program bodies remain unchanged by notice normalization. The audit records the
separate checker scope/configuration changes, generated-bundle license banner,
and buildifier keyword ordering. Config Management retains its previous formatter
macro and wrapper locally because the proposed tooling upgrade removes them.
JSON lockfiles cannot contain inline comments; they remain covered by the native
project LICENSE and NOTICE. The header-template file contains literal examples
and is excluded through the checker's supported mechanism, matching upstream
S-CORE tooling; its own license notice is retained.

The earlier database and reports bind the source before headers moved line numbers.
The fresh database, source archive and SARIF bind the final licensed source.
Findings are not resolved, accepted or qualified by successful execution.

The full host run and build precede the final query header arrangement. The query
license notice and metadata now share the first comment block so CodeQL reads
the original metadata correctly. The
initial separate-block attempt and its stale cached BQRS metadata are retained
as failed reporting records. The affected result was explicitly reevaluated;
parsed metadata, affected regressions and the complete corrected reporting run pass.
The query's original metadata and predicates are unchanged by this arrangement.
The fresh full database reports 2127 findings versus 2,065 in the prior
database. Every finding remains in the artifacts; rule-count differences are
recorded in `license-finding-count-comparison.json`. The same-database regression
retains the original 501 primary findings, fingerprints and located related links.

Merge readiness remains false: #1031's complete consumer safety integration,
published API dependency pin, required hosted CI/platform checks and native
engineering/author acceptance remain outstanding. No PR or approval is published.
