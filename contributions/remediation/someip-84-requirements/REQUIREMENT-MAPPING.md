# Issue #84 requirement mapping

This is a native proposal, not an accepted requirement baseline. The hierarchy
is `stkh_req__someip_gw__local_version_selection` →
`feat_req__socom__version_selection` → the eight requirements
below → existing `comp__socom` (belongs to `feat__someip_gateway`). New requirement
status is `invalid`, tagged `proposal`, as required by the pinned metamodel's
valid/invalid vocabulary. Existing TC8 requirements and valid architecture IDs
retain their status and meaning.

| Proposed requirement | Implementation | Passing partial cases |
|---|---|---|
| `comp_req__socom__available_offers` | `score/socom/impl/runtime_impl.cpp:325` | 5 |
| `comp_req__socom__bounded_discovery` | `score/socom/impl/runtime_impl.cpp:325` | 3 |
| `comp_req__socom__canonical_identity` | `score/socom/service_interface_identifier.hpp:81` | 3 |
| `comp_req__socom__connector_compatibility` | `score/socom/impl/runtime_impl.cpp:136`, `score/socom/service_interface_identifier.hpp:115` | 29 |
| `comp_req__socom__discovery_filters` | `score/socom/service_interface_identifier.hpp:230` | 21 |
| `comp_req__socom__discovery_synchronization` | `score/socom/impl/runtime_impl.cpp:588` | 1 |
| `comp_req__socom__instance_identity` | `score/socom/service_interface_identifier.hpp:208` | 2 |
| `comp_req__socom__registration_identity` | `score/socom/impl/service_identifier.hpp:32` | 117 |

All eight requirements have native source and test links. The 177 distinct
linked SOCom cases pass within the 722-case suite; counts overlap when a case
covers several requirements. [Machine-readable matrix](requirement-mapping.json)
provides exact paths, line numbers, hashes and case names. Native [metrics](evidence/mapping-verified-metrics.json)
and [needs graph](evidence/mapping-verified-needs.json) preserve the resolved links.

Optional minor as a minimum, enabled-only local synchronous snapshots, bounded
storage and the new virtual API are explicit design interpretations for
committer review. Individual cases use `PartiallyVerifies`, not a claim of
complete requirement verification. Synchronization/heap allocation/callback
absence and caller/snapshot lifetime obligations need implementation inspection
and human adequacy review as well as concurrency test evidence. Source API
migration is validated by the full native build; IPC layout and network sentinel
translation remain separate unchanged design constraints, not TC8 acceptance.

The proposed stakeholder requirement's `valid_from: v0.1` is a proposed
applicability window required by the metamodel, not approval of a release.
Classification QM/security NO follows the existing component and is still
subject to committer disposition. Committers must decide whether the expanded
scope requires requirements acceptance before a code PR under CONTRIBUTION.md.

Native revision: `3a3a0d9ee0e502df99dc52279cdd2e536d361c0a`.

