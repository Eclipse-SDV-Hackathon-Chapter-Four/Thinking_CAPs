# Measured verification

Submission: Communication `cef680454e8586daca9f953084dca33fb3759d0c` plus the retained
patch; companion Config Management `e82ec2750d7e9a9dd18edbfe6f5a78be57c22d80`.
Technical changes and portable artifacts are prepared. **Merge readiness is not
established**: #1031's complete production integration still needs native owners.

| Check | Result | Evidence |
| --- | --- | --- |
| Current host suite | 508 passed; 7 skipped; no flaky result | `current-native-host-tests` |
| Final affected tests | 4 passed, including real lint/analyzer regressions, visibility and native AoU fixture | `final-source-affected-tests` |
| Final full build | Passed | `final-source-all-build` |
| Formatting, buildifier warnings and changed Python Ruff | Passed with native pins | `final-source-format`, `final-source-buildifier-wrapper`, `current-final-ruff` |
| Coverage rule / module integration and lock | Passed | `final-source-coverage-rule`, `current-module-integration`, `current-module-integration-lock` |
| Current production extraction | 516/516 configured C++ inputs present and hash-matched; 1,698 extant archive files hash-match | `extraction-recovery.json`, `current-compile-source-coverage.json`, `current-source-archive-binding.json` |
| Complete current analyzer and native reports | All 218 queries; 2065 reported findings; zero empty file URI occurrences | `current-full-suite-summary.json`, `evidence/current-native-reporting` |
| Exact-scope #1104 comparison | 501 findings retained; 281 empty URI occurrences removed; primary findings/fingerprints and valid related links retained | `1104-location-comparison.json`, `compare_locations.py` |
| Real production provider | Build and TRLC validation passed on bound baseline candidate | `1031-provider-native-cc-toolchain`, `1031-production-provider-validation` |
| Complete production consumer index | Failed on legacy/placeholder safety data | `1031-production-traceability-index`, `1031-production-integration-disposition.json` |
| Native copyright | Failed; final touched-file notices corrected; 198 remaining native failures | `final-source-copyright`, `copyright-current-disposition.json` |

The restart interrupted the extraction collector after launch. The native
container finished with exit 0, its full log streams survived, and the recovered
database was audited against the configured compilation manifest and final
physical source hashes. The configured-graph and recovery observer input hashes
match exactly. Two temporary generated XML source paths no longer exist; their
archive bytes remain. This is explicitly recovered evidence, not a reconstructed
normal collector record. Subsequent query, report and final source checks have
ordinary source-bound execution records.

The full host suite precedes an unused import removal, CI documentation and two
comment-only copyright corrections. Macro bodies are byte-identical across the
notice additions. Final affected tests, complete build, formatting and lint bind
the final source. Earlier source overlap and invalid consumer repository overrides
are retained and reconciled, not represented as final passes.

`test-dispositions.json` accounts for all 1,158 discovered rules, including 643
manual rules: 265 selected manual actuals execute through passing native
forwarders; 264 QNX and 114 other manual rules have no direct pass claimed.
The seven skips are enumerated in the full test stdout. The local default
process-wrapper sandbox does not establish the project's Linux-sandbox CI
environment. Required hosted sanitizer/aspect jobs and licensed/applicable
platform checks remain outstanding without a waiver.

Successful analyzer execution does not resolve the 2065 MISRA findings
or establish qualified/safety accepted tool use. Native requirements, safety,
dependency and codeowner acceptance remain human decisions. The companion root
still needs a published Communication dependency containing the public API,
correction/disposition of placeholder safety records, and assessed received-AoU
handling before #1031 can be considered complete.

Full commands, raw logs, exit codes, timings, tool/image/source bindings, failed
attempts and generated artifacts are retained. Baseline results remain historical;
see `evidence-reconciliation.json` and `required-checks.json` for their limits.
The immutable prior archive verifies 11,236 retained files without mismatches.
Run `python verify_packet.py` and `python compare_locations.py` for portable checks.
