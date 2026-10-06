# F003 research decisions
Decision: matched release 0.10.2 with two isolated Docker EDGAR namespaces and TLS CARL.
Rationale: release binaries/images available and supported VPN-disabled Ethernet mode keeps
real CARL rollout/GRE behavior with feasible storage/capability budget. Source and artifact
inspection by research agents: [release spike](../../docs/opendut-release-spike.md),
[deployment research](../../docs/opendut-deployment-research.md).
Alternatives: full NetBird/OIDC profile requires additional backend provisioning and provides
no required benefit for the explicitly local claim; latest main cannot mix release artifacts.
Remaining implementation gates (not unanswered design): GRE capability, release startup,
actual enrollment and application network overlays. Record their outcomes, not assumptions.
