Buildifier warnings currently escape the formatter check, the nightly extraction
can omit production implementation dependencies, and the type-alias MISRA query
can emit unusable `file:/` related links. This change makes warnings fail the lint
job, audits every configured production C++ compilation input after extraction,
and replaces the affected query with a location-preserving correction.

It also exposes the existing Communication AoU target through a public alias,
with a native forwarding fixture and one original TRLC source. The restricted
target and original AoU IDs are retained. A separate Config Management proposal
demonstrates real provider consumption; its full safety index remains blocked.

For #1031, this contribution covers public AoU visibility, the forwarding
regression fixture and measured provider consumption. Production safety decisions
are deferred to a separate Config Management follow-up: shared-memory adequacy,
the consuming requirement's QM classification against the ASIL B AoU, dispositions
for every received AoU, and correction of placeholder safety records with real
implementation/verification links. The passing API/provider checks establish
technical consumption only. Full consumer FMEA/LOBSTER/index validation,
including duplicate processing and complete forwarding, remains incomplete.
Use `Related` for #1031; keep the issue open until its remaining acceptance
criteria are met. The Config Management companion remains a draft proposal.

- Adds positive and negative buildifier fixtures and repairs observed warnings.
  Rust unit-test compatibility constraints are forwarded rather than discarded.
- Includes external implementation dependencies in the extraction closure;
  rejects missing compilation sources and nonempty failed database retries.
- Retains CodeQL 2.21.4, MISRA 2.62.0 and locked libraries. The corrected query
  keeps its original predicates, rule ID and primary locations. Located aliases
  link to their definitions; locationless instances link to the actual type-name
  use selected by the query.
- Adds Bash shebangs to all six rules_build_error 0.11.0 helpers so expected
  compiler failures remain testable under CodeQL tracing. The pin and CC0
  licensing remain unchanged; the imported query retains its MIT license.

Validation and exact source bindings are in the [verification report](https://github.com/jnsagai/communication/tree/d3c4da334600e1d90a9ff6ec779605e4676cfe2d/verification.md) and [required-check inventory](https://github.com/jnsagai/communication/tree/d3c4da334600e1d90a9ff6ec779605e4676cfe2d/required-checks.json). The retained exact-scope comparison has 501 findings
before/after, removes 281 empty URI occurrences, and preserves primary findings,
fingerprints, alias descriptions and previously located related links. Two
merged messages expand because restored locations distinguish link targets.
The final licensed-source database covers 516/516 configured C++ inputs,
with exact source-byte matches. All 218 queries and native reports pass;
2127 findings remain for native disposition, with zero empty file URIs.
Host tests report 508 passes and 7 explicit skips. Full build, formatting,
buildifier and complete-repository copyright checks pass. The code-file audit
also covers query suites, templates, fixtures and packet helpers outside the
native checker. Existing numeric years, MIT attribution and CC0 terms remain.
Generated action bundles retain their third-party notices and receive project
license banners during regeneration.


Related: eclipse-score/communication#1236, #751, #1104 and #1031.
Close individual issues only after their native acceptance criteria are met.

The lint job implements the existing Bazel formatting/linting obligation in
CI.md and provides a local reproduction command. Codeowner review must assess
the workflow change and its performance in native CI. Hosted
lint/sanitizer/platform results and native codeowner/dependency acceptance
remain pending. The deferred #1031 safety work is described above.

This PR is a draft for Jefferson Nascimento's review. Please keep it in draft
until the intended scope, native CI results and codeowner/dependency requirements
have been reviewed. Auto-merge is not enabled.

The native patch is based on `cef680454e8586daca9f953084dca33fb3759d0c`; the measured check results
are bound to the same source bytes committed as `fb634728809bae2cacf485c9edab891a1ab20321`.
Upstream main was `251ea495e25852d357e589cee95cc8c54d141633` at publication preparation.
A temporary merge with that main was clean; no test/analyzer result is claimed
for the merge tree or later upstream changes. Strict Eclipse ECA validation
passes for the actual PR commit, with zero errors.

The repository-wide license cleanup overlaps
[the existing header PR #1341](https://github.com/eclipse-score/communication/pull/1341).
Coordinate the shared notice changes before merging either contribution.

[Review evidence](https://github.com/jnsagai/communication/tree/d3c4da334600e1d90a9ff6ec779605e4676cfe2d/README.md) includes the native patches,
source bindings, final test/coverage/location summaries, selected complete
command logs, final SARIF, license audit and actual-commit ECA result. Its
142 exported files are hash-bound; larger database/source archives and historical
evidence remain in the retained local packet, described by the original manifest.
The Config Management companion remains a proposal in that evidence branch;
no Config Management PR or safety acceptance is claimed.

Reproduction in the native environment:

```bash
bazel build --config=ci //...
bazel test --config=ci //... --build_tests_only
bazel run //:format.check
bazel run //:copyright.check
bazel run //tools/lint/buildifier:buildifier_lint -- --recursive
bazel test //score/mw/com/dependability/safety_analysis/aou_forwarding_test:component_requirements_test
```

Use the [reproduction guide](https://github.com/jnsagai/communication/tree/d3c4da334600e1d90a9ff6ec779605e4676cfe2d/reproduce.md) for fresh CodeQL
extraction, full native reporting and companion provider checks. Local host
results use the recorded process-wrapper profile; hosted native Linux-sandbox,
sanitizer/aspect/platform checks remain pending.

AI assistance: OpenAI Codex prepared the implementation, license audit,
verification artifacts and this draft under Jefferson Nascimento's instructions.
Original ownership and licenses are retained; native engineering acceptance
remains with the project owners.

