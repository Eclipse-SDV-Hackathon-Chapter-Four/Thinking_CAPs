# Bug Fix

## Description

SOCom previously mixed service identity with minor compatibility. Its database
ignored minor version while the server-registration key included it, and the
public identifier did not distinguish service identity, full instance identity
and discovery filters.

This change introduces canonical service ID + major identity, a public offered
instance identity carrying minor version and instance ID, and a find-service
request with optional minimum minor and instance filters. A bounded local
snapshot API reports enabled server offers without allocating. Database and
registration indexing use canonical identity; duplicate servers remain rejected
across minor versions. Full-version connector contracts become `Service_interface`;
in-repository gateway, IPC, benchmark, test and mock callers are migrated.

The native SOCom documentation describes discovery semantics, buffer and locking
contracts, source migration and verification. Serialized IPC fields are unchanged.
External callers must migrate the renamed type and Runtime implementations.

## Related ticket

Related to https://github.com/eclipse-score/inc_someip_gateway/issues/84.

The full issue use cases are mapped in the offline review packet. Link the actual
bugfix content-review tracking issue (label `codeowner_review`) and its PR before
requesting final committer review. Contribution classification and any requirement
acceptance prerequisite remain subject to committer assessment.

## Validation

- `final-clang-tidy`: exit 0 (190.1 seconds).
- `final-precommit`: exit 0 (21.7 seconds).
- `final-format`: exit 0 (9.5 seconds).
- `final-build`: exit 0 (214.9 seconds).
- `final-host`: exit 0 (112.1 seconds).
- `final-asan`: exit 0 (143.6 seconds).
- `final-tsan`: exit 0 (145.2 seconds).
- `final-quality-tests`: exit 0 (122.2 seconds).
- `final-docs`: exit 0 (30.6 seconds).
- `final-traceability`: exit 0 (15.8 seconds).
- `final-qemu`: exit 3 (929.3 seconds).

SOCom: 722 cases passed in each final default, ASAN/LSAN/UBSAN and TSAN run.
Selected sanitizer checks do not represent the complete CI matrix. The native trace gate passes baseline zero thresholds with 0/8 linked component
requirements and 0/996 linked tests; this is not formal acceptance of the new
behavior. Earlier 689-test scoped results remain historical. See native-results.json for source
bindings, raw logs, failures and remaining CI obligations.

QEMU default integration: two targets passed, four failed starting unchanged
host capture code because tcpdump could not change root UID/GID (EPERM). The
guest application suite passed SOCom unit/stress, IPC and serializer binaries,
with one baseline multi-process skip. This is an incomplete integration result;
appropriate-host/upstream rerun is required. Raw logs and the disposition are
preserved in the review packet.

## AI assistance

OpenAI Codex assisted the historical scoped regression patch and the full issue
implementation, verification helpers and documentation. Exact model revisions
were not retained/are unavailable. Changed/new C++ files and the new native design guide carry scoped
AI notices and Apache-2.0 AND CC0-1.0 licensing; complete CC0 terms are included.
Human review of this exact full revision is pending. Signed-off-by is a contributor
DCO certification and does not establish that the required AI review occurred.

## Review and IP

Public API migration, the complete issue acceptance map, raw evidence and IP
review request are available in the offline packet. Project committer assessment
and any required IP Team disposition remain pending. Submit as draft until ready
for committer review, following native CONTRIBUTION.md.
