Title: Enforce Bazel lint and restore complete CodeQL coverage and finding links

Buildifier warnings currently escape the formatter check, the nightly extraction
can omit production implementation dependencies, and the type-alias MISRA query
can emit unusable `file:/` related links. This change makes warnings fail the lint
job, audits every configured production C++ compilation input after extraction,
and replaces the affected query with a location-preserving correction.

It also exposes the existing Communication AoU target through a public alias,
with a native forwarding fixture and one original TRLC source. The restricted
target and original AoU IDs are retained. A separate Config Management proposal
demonstrates real provider consumption; its full safety index remains blocked.

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

Validation and exact source bindings are in `verification.md` and
`required-checks.json`. The retained exact-scope comparison has 501 findings
before/after, removes 281 empty URI occurrences, and preserves primary findings,
fingerprints, alias descriptions and previously located related links. Two
merged messages expand because restored locations distinguish link targets.
The fresh submission-source database covers 516/516 configured C++ inputs, with
matching source hashes. The execution survived a collector restart; native exit
status, full logs and complete byte audits are retained as recovered evidence.
The complete 218-query suite and native reporting succeed, producing 2,065
findings with no empty file URI occurrences. These findings still require
native disposition; this execution supplies no tool qualification.
Current-source host tests pass 508 tests with seven explicit platform skips;
final complete build, affected regressions, module integration, formatting,
buildifier and changed Python Ruff checks pass. See the source-bound check
inventory for remaining hosted sanitizer/aspect/platform checks.


Related: eclipse-score/communication#1236, #751, #1104 and #1031.
Close individual issues only after their native acceptance criteria are met.

The lint job implements the existing Bazel formatting/linting obligation in
CI.md and provides a local reproduction command. Codeowner review must assess
the workflow change and its performance in native CI. Copyright debt, hosted
lint/sanitizer/platform results, ECA and native safety/dependency approval remain
explicit gates; this draft does not waive them.
