# Contribution reorganisation — 2026-10-08

All contributions, and the material they depend on, are grouped by Eclipse project under
`contributions/`. The repository root keeps only `contributions/`, `demo/` and the repository
files. `demo/` was not changed.

| Folder | Contents |
| --- | --- |
| `eclipse-score/` | communication, lifecycle, inc_diagnostics, inc_someip_gateway and score issue records; S-CORE app integration (`s-core-app/`, was `score/`) |
| `eclipse-opensovd/` | `OpenSOVD/` component, CDA #543, fault-storage write-through |
| `eclipse-threadx/` | threadx #744 (the ThreadX controller itself is in `demo/X-Verse/external_hackathon_ecus/ThreadX/`) |
| `eclipse-openbsw/` | `OpenBSW/` component, transportRouter |
| `eclipse-opendut/` | `OpenDut/` component |
| `eclipse-autosd/` | `AutoSD/` component |
| `eclipse-hephaestus/` | hephaestus #11, S-CORE docs assistant proposal |
| `shared/` | compliance, audits, submission, DCO, docs, evidence, specs, tests, scripts, dashboard and other cross-project material |

Files moved with `git mv`, so history follows them. References were then updated in
documentation, records, code and symlinks. References to ThreadX and the consoles now point
at their location in `demo/X-Verse/external_hackathon_ecus/`. Manifests and hash pins
covering edited files were re-sealed.
[relocation-2026-10-08.json](relocation-2026-10-08.json) lists every move, every edited
file with its SHA-256 before and after, and every retargeted symlink.

Unchanged by design: captured upstream sources, branch snapshots, native logs, test outputs
and API responses; scripts inside contribution packets (the record of how evidence was
produced); the dashboard code, which resolves everything relative to `shared/`; dated
audits; `.specify/` and `.agents/`; and `demo/`.

Checks against the base commit (4e69da65): `verify_contributions.py` passes for 24 issues and 128
compliance files. Every manifest that passed still passes, and the shared and verifier tests
pass. No document gained broken links.
