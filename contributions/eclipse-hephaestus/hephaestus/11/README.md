# Hephaestus s-core_sw_fabric contribution proposal

Draft [PR #14](https://github.com/eclipse-hephaestus/hephaestus/pull/14) proposes an engineering workflow pilot with architecture, evidence, a pinned public implementation and maintainer decisions. It relates to [issue #11](https://github.com/eclipse-hephaestus/hephaestus/issues/11), the website content review, without closing that broader issue.

Branch: `jnsagai/hephaestus:contrib/s-core-sw-fabric-proposal`.
Proposal commit: `2c5bdf5f3faa855a8be984ea8ff7603d85268252`.
Upstream base: `6933c816cc79db4e444bd09847280790fc5f43ce`.
Implementation: `jnsagai/s-core_sw_fabric@7e24a43c258f1dcaa2b27e02b501964847bc8714`.

## Scope and validation

The PR adds the proposal and links it from the tooling catalog and Sphinx documentation. Hugo Extended 0.163.0, navigation/inventory generation and Sphinx 8.2.3 with warnings treated as errors passed. Sixteen pinned implementation references and the rendered navigation were checked. Eclipse's PR ECA status reports success. No CI build check was attached at capture time; these are local build results.

Historical implementation acceptance reports retain their original scope; the implementation test suite was not rerun for this documentation PR. Adoption, metamodel compatibility, the first pilot adapter, dependency review and authorized engineering acceptance remain pending.

## Retained artifacts

- [Proposal](proposal.md), [submitted PR body](pr-body.md), and [patch](proposal.patch).
- [Binding](proposal-binding.json), [provenance](provenance.json), and frozen issue/PR/status snapshots.
- `evidence/validation/`: commands, tool identity, dependency freeze, raw logs and content checks, including the corrected earlier render reference.
- `evidence/implementation/`: all 16 linked records copied byte-for-byte from the pinned public implementation, including architecture, historic acceptance, license, notices and dependency lock.
- `evidence/upstream/`: contribution guide and applicable repository license/build inputs at the upstream base.
- [SHA-256 manifest](artifact-manifest.json): all packet files except the manifest itself.

This folder is a proposal record, excluded from completed or accepted implementation counts. It does not alter other contribution records.

Verify retained bytes from any directory:

```bash
python /home/jefferson/Thinking_CAPs/contributions/eclipse-hephaestus/hephaestus/11/verify_evidence.py
```

Hash verification establishes retained artifact integrity; it does not rerun builds or grant engineering acceptance.
