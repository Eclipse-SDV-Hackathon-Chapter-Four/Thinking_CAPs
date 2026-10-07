# Tooling evaluation outcome

Scope: qualitative selection for S-CORE integration and evaluation, proposed for maintainer acceptance. The native authority is `DR-010-infra.rst`, `dec_rec__infra__ai_sdlc_tooling`, version 3. This supporting table is not a second native requirements database.

Criteria: native artifact/metamodel fit; reproducible provenance and destinations; change loopbacks; deterministic checks and portable evidence; client/dependency constraints; maintenance and integration effort. Priority comes from the existing #3140 review and labelled fabric experience. No numeric score or measured head-to-head advantage is assigned to unexecuted tools.

| Option | Recommendation | Source-supported reason | Limit / reconsideration |
| --- | --- | --- | --- |
| APM | Primary packaging recommendation | Documents content/source locks, installation policy, drift and SBOM inventory; aligns with the issue assignee's packaging direction | CLI distribution/governance behavior remains untested here; rollout requires allowed-destination and install/upgrade/rollback cases |
| Lola | Packaging fallback | Documents cross-client skills, MCP and project/user distribution | Demonstrate required clients and identical provenance/destination cases before replacing APM; documentation silence is not a proven missing capability |
| OKIT | Isolated personal prototype | Documents source commit tracking, stdlib implementation and installation into enabled providers | Auto-enables detected providers; establish bounded destinations before shared use; do not repeat an unsupported no-versioning claim |
| Spec Kit | Primary integration-development workflow | Retained implementation experience at pinned v1.0.12 in the fabric | Does not replace native S-CORE engineering work products; historical passing checks are not fresh qualification |
| Syspilot | Preferred next native-context prototype; defer default rollout | Direct Sphinx-Needs trace/impact focus matches native artifact context | README labels early research/breaking changes and requires VS Code, Copilot and jarvis-core; silent handoff loss needs capability checks |
| BMAD | Alternative; defer baseline choice | Documents adaptive planning, native workflow integration and skill/plugin distribution | Native S-CORE metamodel/loopback adaptation unmeasured; retained Spec Kit implementation supplies stronger project-specific experience |
| Pharaoh | Reuse reviewed concepts; no new dependency on the archived repository | Extensive Sphinx-Needs analysis concepts; archived repository states successor integrations | No maintained repository support is inferred; successor licensing/support needs separate evaluation |
| Harbor | Recommended comparative evaluation driver | Documents arbitrary agents and custom benchmark environments | No Harbor experiment executed; native verifiers and human review remain acceptance authority |

## Source and licensing bindings

All documentary claims use the original primary captures from 2026-10-07 in `../evidence/candidates/index.json` and their README/LICENSE bytes. Every requested/resolved repository, commit, redirect and archive state is recorded there. These current survey versions do not replace older execution/tool locks in the fabric. BMAD's captured LICENSE is MIT plus a trademark notice even though GitHub's automatic license metadata says NOASSERTION; retain both observations.

The selections are recommendations, not a licensing clearance, a safety tool classification or a rollout approval. No candidate implementation, dependency lock or global agent configuration is installed into S-CORE by this PR. Impact analysis/safety qualification for operational tooling depends on the subsequently authorized use case and cannot be supplied by this documentation-only change.
