# Local contribution registry support

The verifier now accepts historical and native manifest formats and captured GitHub API/CLI issue wrappers, checks size and SHA-256 identities, rejects escaping and duplicate artifact paths, and verifies optional readiness packet bindings. Eight regression tests pass. Exact issue selection rejects unknown IDs and lets Communication records be checked independently of concurrent work in other repositories.

The #781/#490 registry repair is derived from their retained, hash-validated native evidence. The preceding scoped verification report covers Communication #1261/#250/#560/#781/#490 before linking this new packet. The final linked report is retained in contributions/audits after sealing.

A whole-registry check at recovery reported an unrelated inc_someip_gateway #84 observation mismatch (registry date 2026-10-07 versus retained snapshot date 2026-10-04). Its records were preserved; no global verification success is claimed from the scoped report.
