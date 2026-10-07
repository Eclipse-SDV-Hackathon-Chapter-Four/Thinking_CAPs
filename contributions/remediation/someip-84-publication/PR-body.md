# Bugfix

## Description

SOCom previously used conflicting notions of service identity: the runtime database ignored minor versions while duplicate-server registration included them. Its public type also combined service identity with a full versioned connector contract.

This proposal implements the version model discussed in #84:

- Canonical service identity: service ID + exact major version.
- Full offered-instance identity: service ID + major + actual offered minor + instance ID.
- Find requests: exact service identity, optional minimum compatible minor, and optional exact instance ID.
- Bounded, synchronous local discovery: enabled server offers only; total match count and caller-provided output storage; existing runtime mutex; no heap allocation or callbacks.
- Server registration ignores minor versions while full connector contracts retain both versions. Gateway, IPC, benchmark, test and mock callers are migrated to `Service_interface`.

This changes the public source API: external callers must migrate the renamed contract type, and external Runtime implementations must provide the new discovery method. Serialized IPC fields/layout and existing configuration/wire sentinel handling are unchanged. Discovery covers the queried local runtime; bridge/network discovery stays with bridges.

The [native design and migration guide](https://github.com/jnsagai/inc_someip_gateway/blob/3a3a0d9ee0e502df99dc52279cdd2e536d361c0a/score/socom/docs/version_handling.rst) describes the semantics and caller obligations. The [eight proposed component requirements](https://github.com/jnsagai/inc_someip_gateway/blob/3a3a0d9ee0e502df99dc52279cdd2e536d361c0a/docs/requirements/component/socom/index.rst) link to implementation and targeted GoogleTest metadata, with a proposed feature/stakeholder hierarchy. They carry `invalid` status and `proposal` tags until accepted; the pinned metamodel does not support draft requirement status. Minimum-minor interpretation, snapshot semantics, API migration, requirement classification and acceptance require committer disposition.

A standard inline Apache header is also added to the existing licensed FlatBuffers schema. Original copyright and license notices are preserved.

## Related ticket

Refs #84 — Revise version handling in socom.

**Kept as draft for the contributor's review.** Formal committer content review has not been requested. The corresponding `codeowner_review` tracking issue will be opened and linked when the contribution is ready, following CONTRIBUTION.md. Committers should determine whether the expanded scope requires a separate requirements/contribution request before accepting implementation.

## Validation

Measured locally against baseline `f8a196c3b16d5172d898394ab99b0ed81346d63d`, with prepared head `3a3a0d9ee0e502df99dc52279cdd2e536d361c0a`:

| Check | Result |
|---|---|
| `pre-commit run --all-files` | Pass, including native copyright and REUSE hooks |
| `bazel test //:format.check` | Pass |
| `bazel build //...` | Pass, 155 targets |
| `bazel test //score/socom/test/unit:socom_test --nocache_test_results` | 722 cases pass |
| `bazel test --config=clang-tidy //score/socom/... --nocache_test_results` | Pass under native lint policy |
| `bazel run //:docs` | Pass, no documentation/metamodel warnings |
| Native `traceability_gate`, `--need-type=comp_req` | Pass; all eight new requirements have source and test links; zero broken test references |
| Tracked native code/build header audit | 243 files checked; no missing inline copyright/Apache/SPDX headers |

177 passing SOCom cases have **partial** requirement-verification links. Repository-wide component requirement linkage is 8/16; the other eight are unrelated TC8 wire-level requirements. The trace gate retains its original zero thresholds. Link presence does not establish complete verification or requirement acceptance.

Earlier full host, selected ASAN/LSAN/UBSAN and TSAN, and quality-test results belong to the original implementation commit `f9d46949e40e18637f4c51fcc878339552aa7409`; they are retained as historical evidence, not relabelled current-revision checks. Runtime changes since that commit are trace comments; test changes add metadata; the schema body is unchanged.

Earlier native QEMU integration has two passing targets and four failures in unchanged host packet-capture code: tcpdump cannot change root UID/GID (`Operation not permitted`). Integration needs an appropriate-host/upstream rerun. Remaining applicable sanitizer, cross-platform/QNX, coverage, license and other upstream CI gates are pending. Current PR checks are separate from the local measurements above.

## AI assistance and provenance

OpenAI Codex assisted the implementation, migrations, tests, documentation, requirement mapping and verification helpers; exact model revision is unavailable. Applicable source headers disclose AI-generated portions under CC0-1.0 alongside existing Apache-2.0 terms; complete CC0 terms are included. Human review of this exact expanded revision is pending and must be completed before merge.

Both commits carry:

`Signed-off-by: Jefferson Nascimento <jnsagai@gmail.com>`

The contributor's Eclipse account is `jnascimento6p0`; GitHub author is `jnsagai`. Upstream ECA/DCO checks must confirm eligibility. DCO sign-off does not constitute human AI review or IP clearance.

## Review status

Author review, committer API/requirement acceptance, project IP assessment and required IP Team disposition, integration resolution and remaining applicable CI are pending. No new dependency or toolchain pin is introduced. Do not merge or mark ready until the relevant reviews and checks are complete.
