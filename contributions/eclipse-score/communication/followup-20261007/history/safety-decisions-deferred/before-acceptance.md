# Acceptance and engineering trace

This is a new follow-up to the preserved 2026-10-06 packet. The old patches,
logs and manifests remain historical evidence. The user authorized completing
the contribution and preparing the artifacts for project review. No upstream
PR, comment, merge or release has been published by this follow-up.

Communication submission source: `cef680454e8586daca9f953084dca33fb3759d0c`.
Earlier verification baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Current source is 61 commits ahead; current-main results are recorded separately.
Production consumer discovered from the issue: `eclipse-score/config_management`,
source `e82ec2750d7e9a9dd18edbfe6f5a78be57c22d80`. Its default profile uses LLVM
19.1.0; its CI also defines `host_gcc`. This consumer is a real repository,
distinct from the Communication forwarding regression fixture.

| Issue criterion | Native artifact / obligation | Change | Verification and acceptance limit |
| --- | --- | --- | --- |
| #1236: existing Bazel warnings must fail CI | `CI.md`: Bazel formatting and linting; `_linter.yml` | A pinned buildifier lint wrapper and CI job; repair all 27 observed warnings without disabling checks | Native clean/warning fixture and full repository buildifier checks; native build and affected rule analysis remain part of the expected inventory |
| #1031: public AoU consumption and forwarding without duplicate FMEA / LOBSTER processing | Original `Communication` AoU IDs and versions; native `assumptions_of_use`, `component_requirements`, `dependable_element` providers | Public alias of the existing restricted target, one original AoU source; native CompReq regression fixture; separate real-consumer proposal | A fixture alone cannot establish production acceptance. Real-consumer source binding, toolchain compatibility and generated trace reports must be checked |
| #751: `proxy_binding_factory_impl.cpp` included in nightly analysis | `_codeql.yml`, CodeQL configuration, configured production compilation actions | Select production library/binary closure, including external implementation dependencies; audit every configured CppCompile input and named reported file; reject contaminated database retries | Fresh database source archive and action-derived coverage manifest are required. Source archive presence is separate from successful full-suite analysis and tool qualification |
| #1104: replace empty `file:/` related locations | Native MISRA `cpp/misra/type-aliases-declaration`, pinned 2.62.0 query semantics | Preserve located alias definitions; use actual type-name use location for locationless template alias instances; replace only this query in the default 218-query suite | Retained exact-scope database comparison: 501 findings before/after, 281 empty URI occurrences before and zero after. Primary finding locations and fingerprints, alias descriptions and all original located related links preserved. Two merged messages expand; raw text is not byte-identical |

The consumer proposal retains `ConfigManagement.AdditionalProxyNeedsRegistration`,
changes its version from 1 to 2 because its derivation changes, and adds
`Communication.MonotonicSemiDynamicMemoryAllocation@1` to its original feature
derivation. Its description and QM classification remain unchanged. This is a
proposed trace, requiring review of whether the native requirement actually
discharges the received AoU and whether its classification is adequate.
No unreviewed claim that the requirement satisfies the AoU is made.

The proposed consumer dependency on `mw_com` introduces received-AoU obligations
for the complete imported set. Applicability, satisfaction and forwarding of
those obligations require native engineering decisions. Blanket forwarding,
invented mitigations and acceptance of placeholder safety content are not used
to make tooling checks appear complete.

The default query replacement retains the upstream MIT license and the original
query ID, predicates and primary finding selection. CodeQL 2.21.4, MISRA pack
2.62.0 and its locked dependencies are retained. A restored use-site link does
not purport to identify a definition unavailable in the database. The helper is
inline and bound to the already selected alias/use pair to avoid an unbounded
cross-product during query evaluation.

Native contribution policy requires all tests to pass and an Eclipse Contributor
Agreement. Native CI also requires host build/tests, lint checks and sanitizer
jobs. QNX nightly analysis is conditional on the project's licensed environment.
Historical copyright failures, unrun checks, platform exclusions and unavailable
human acceptance remain explicit in the review packet; none is waived here.

The issue labels and checked template fields do not establish safety relevance
or acceptance. #751 is marked safety related upstream. No independent tool
qualification or safety-release claim is established by these local executions.
