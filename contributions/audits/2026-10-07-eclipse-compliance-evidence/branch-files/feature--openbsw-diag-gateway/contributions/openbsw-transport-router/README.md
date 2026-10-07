# Prepared OpenBSW contribution: transportRouter (diagnostic gateway router)

Prepared on 6 October 2026. Nothing has been submitted publicly, and no
maintainer approval or merge is claimed.

- **Upstream:** [eclipse-openbsw/openbsw](https://github.com/eclipse-openbsw/openbsw),
  base `432b9be6098d99570ab8ebc32a7cbb895ca7bb63`.
- **Change:** a new module `libs/bsw/transportRouter` and two registration lines.
  `TransportRouterSimple` is unchanged.

OpenBSW has no router that forwards UDS by logical address: `TransportRouterSimple`
only serves the local diagnostic server. This module adds that, so an OpenBSW node
can act as a DoIP-to-DoCAN diagnostic gateway. It came out of the
[OpenBSW zonal diagnostic gateway](../../OpenBSW/README.md), which builds from the
same source in [`OpenBSW/contrib/`](../../OpenBSW/contrib/libs/bsw/transportRouter).

## Review artifacts

| Artifact | Content |
| --- | --- |
| [ISSUE-draft.md](ISSUE-draft.md) | Feature request in the OpenBSW issue template, to open first (CONTRIBUTING.md) |
| [0001-transport-router.patch](0001-transport-router.patch) | `git format-patch` of the signed-off commit |
| [commit-message.txt](commit-message.txt) | Commit message (gitlint-checked) |
| [PR-description.md](PR-description.md) | Pull request title and body |
| [validation.md](validation.md) | Checks performed, tool versions, results and limitations |
| [evidence/](evidence/) | Unit test, coverage, format, copyright, clang-tidy, Bazel and gitlint outputs |
| [artifact-manifest.json](artifact-manifest.json) | SHA-256 of every file in this folder |

## Results at a glance

| Check | Result |
| --- | --- |
| Unit tests | 46/46 passed |
| Coverage | 100% lines, 99.1% branches |
| Format | clean |
| Copyright | ok |
| clang-tidy | 0 findings |
| Bazel | 2/2 passed |
| gitlint | ok |
| Patch | applies to the base with an identical tree |
| Gateway integration | 28/28 passed |

## Submitting

1. Sign the Eclipse Contributor Agreement with `jnsagai@gmail.com`.
2. Open the issue from [ISSUE-draft.md](ISSUE-draft.md) and agree on the approach.
3. Fork the repository and apply the patch:

   ```bash
   git am 0001-transport-router.patch
   ```

4. Push and open the PR with [PR-description.md](PR-description.md), filling in the issue number.
5. Record the issue and PR URLs here and add an entry to [registry.json](../registry.json).

To verify the integrity of this folder:

```bash
python3 -c "import sys; sys.path.insert(0, 'scripts'); import verify_contributions as v; from pathlib import Path; print(v.check_manifest(Path('contributions/openbsw-transport-router/artifact-manifest.json')), 'files ok')"
```
