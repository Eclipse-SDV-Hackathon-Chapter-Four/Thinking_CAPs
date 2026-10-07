# Bugfix

Prepared locally. Publish as a draft only after publication is authorized.
The user-authorized DCO sign-off is prepared on local native commit `28b0d84c`.
No native PR exists.

## Description

Constructing two SOCom servers with the same instance, service ID and major version
but different minor versions previously occupied separate registration slots while
resolving to the same `Service_database` record. Enabling both could reach the
duplicate-server assertion. Comparing registration keys by `(instance, service id,
major)` makes the second construction return `Construction_error::duplicate_service`
while the first connector exists.

Regression tests cover enabled/disabled connectors, version and identifier boundaries,
distinct identities, slot reuse, ordering and existing compatibility rules. The
seven-file patch includes the original six source/build/test files and CC0 terms.

## Related ticket

Related to https://github.com/eclipse-score/inc_someip_gateway/issues/84.
The broader public identifier/discovery design remains under #84. Use the prepared
separate bugfix tracking issue when initiating native content review; insert its
actual number here once created. This draft does not close #84.

## Validation

Fresh checks on the current patch: GCC 12 and Clang 19 focused regressions, 91 passed
each; native SOCom unit suite, 689 passed with cached test results disabled; all four
native formatting targets passed; all native pre-commit hooks passed. The original
comparator fails the duplicate-minor-version regression as expected. Patch, source
and unchanged policy hashes are captured in the companion review packet.

Initial harness failures and third-party deprecation warnings remain recorded.
Clang's third-party GoogleTest build uses the original recorded profile; project
sources retain `-Werror`. Native warning policy and dependency pins are unchanged.

Historical integration evidence records six Linux QEMU targets with 13 applicable
cases and two profiling targets with 12 datasets/flamegraphs on the original patch.
Those checks have not been rerun on the amended revision. Full host/sanitizer,
integration, benchmark, coverage, documentation, quality, analyzer and applicable
cross/QNX CI still require current results or maintainer disposition. No full CI,
tool qualification or MISRA acceptance is claimed.

## AI and IP disclosure

Historical implementation was assisted by OpenAI Codex; the exact historical
model revision was not retained. Native Fabro verification/repair evidence is
preserved. This compliance preparation also used OpenAI Codex. The largely
generated new regression file has a scoped disclosure: AI portions use CC0-1.0,
copyrightable human modifications/curation retain Apache-2.0. Existing notices
are preserved; complete CC0 terms are included. Human review of the amended
revision and confirmation of generation/provenance extent remain required.

The diff has 3,325 additions and 6 removals. A project committer must determine
net new IP and obtain applicable Eclipse IP Team review before official inclusion.
A request draft is prepared; no approval is claimed. Jefferson's ECA lookup passes;
the eventual native author/committer eligibility checks remain required. Local
native commit `28b0d84c990a539bd61ec107b2f9e66f9ab741a2` carries the DCO sign-off
`Signed-off-by: Jefferson Nascimento <jnsagai@gmail.com>`, prepared following the
user's instruction after explanation of the DCO. This supplies no technical or IP approval.

The current prepared revision has recorded local contributor approval. Broader
issue #84 work remains outside the patch; upstream committer review and project
acceptance are still required.

Assisted-by: OpenAI Codex (historical model revision not retained)
Assisted-by: OpenAI Codex (compliance preparation; model revision unavailable)
