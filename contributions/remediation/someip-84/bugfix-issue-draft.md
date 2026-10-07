# Bugfix: reject duplicate SOCom servers across minor versions

Use the upstream Bugfix issue template and `codeowner_review` label when publication
is authorized. This document is a local draft and has not been posted.

Constructing a second SOCom server with the same instance, service ID and major
version, but another minor version, can occupy another registration slot for the
same service-database record. Enabling both can reach a duplicate-server assertion.

The prepared patch aligns the internal registration key with the database identity
and returns `Construction_error::duplicate_service` for the second construction.
Regression coverage includes enabled/disabled connectors, version boundaries,
distinct identities, ordering, compatibility and reuse after destruction.

Related to https://github.com/eclipse-score/inc_someip_gateway/issues/84. The wider
public identifier/discovery design remains under #84. Link this tracking issue to
the eventual draft PR; do not automatically close #84 for the scoped fix.

Historical implementation and this preparation were assisted by OpenAI Codex.
The user-authorized DCO sign-off is prepared on local native commit `28b0d84c`.
Human review, project IP disposition and native CI remain required.
