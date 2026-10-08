# Bug Fix

## Description

SOCom separates canonical service ID + major identity, full offered instance
identity and optional local discovery filters. Bounded snapshots report actual
enabled offer minors, and single-server registration ignores minor versions.
Full contracts retain compatibility versions and all in-repository callers are
migrated. The native design guide documents migration, storage and locking.

Eight proposed SOCom requirements now link the native design, implementation and
177 targeted passing test cases. They are explicitly unaccepted (`invalid` /
`proposal`) under the pinned metamodel. Native requirement/API classification and
acceptance must precede final review as required by the committers' disposition.
A standard inline Apache header is added to the existing licensed config schema.

## Related ticket

Related to https://github.com/eclipse-score/inc_someip_gateway/issues/84.
The actual codeowner_review tracking issue and PR links must be supplied at
submission; no tracking issue or PR has been published for this local packet.

## Validation

Full native build, 722 SOCom cases, formatting, pre-commit copyright/REUSE,
docs and trace checks pass for the current revision. SOCom Clang-Tidy passes for the exact current revision. All eight new component requirements have source
and partial-test links, with no broken test references. Unrelated TC8 requirements
remain outside this verification. Exact commands/raw evidence are in native-results.json.

Original selected sanitizer/full host/quality/QEMU runs belong to the prior
implementation revision and are retained as history. QEMU has two passing targets
and four host tcpdump credential-change EPERM failures; integration and remaining
applicable CI are pending. Trace presence does not establish complete verification.

## AI assistance

OpenAI Codex assisted code, documentation, mapping and verification helpers
(model revision unavailable). AI-generated portions are disclosed and offered
under CC0-1.0; existing Apache notices remain. Exact-revision human AI review is
pending. Both local commits include Jefferson Nascimento's authorized DCO sign-off.

## Review and IP

Committer requirement/API acceptance, human review, required IP disposition and
remaining CI are pending. Prepare as draft under CONTRIBUTION.md until these
gates are met. External users must migrate the source API and Runtime method.

