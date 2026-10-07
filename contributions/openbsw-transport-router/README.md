# Prepared OpenBSW contribution: transportRouter (diagnostic gateway router)

Prepared on 6 October 2026 and brought up to the OpenBSW and Eclipse Foundation rules on
7 October 2026. The feature issue is open as
[eclipse-openbsw/openbsw#664](https://github.com/eclipse-openbsw/openbsw/issues/664), and the pull
request as [#665](https://github.com/eclipse-openbsw/openbsw/pull/665) (opened on 7 October 2026 at the author's request, before a
committer replied on #664). No maintainer approval or merge is claimed.

- **Upstream:** [eclipse-openbsw/openbsw](https://github.com/eclipse-openbsw/openbsw),
  base `main` at `b0550871b7a44ae47bb9b7c68af84fb9115bfa77`.
- **Change:** a new module `libs/bsw/transportRouter` and two registration lines.
  `TransportRouterSimple` is unchanged.

OpenBSW has no router that forwards UDS by logical address: `TransportRouterSimple`
only serves the local diagnostic server. This module adds that, so an OpenBSW node
can act as a diagnostic gateway from DoIP to DoCAN (and, with the
[doipClient](../openbsw-doip-client/README.md), to DoIP). It came out of the
[OpenBSW zonal diagnostic gateway](../../OpenBSW/README.md), which builds from the
same source in [`OpenBSW/contrib/`](../../OpenBSW/contrib/libs/bsw/transportRouter).

## Review artifacts

| Artifact | Content |
| --- | --- |
| [compliance.md](compliance.md) | Every OpenBSW, Eclipse Foundation and repository rule checked, with status and evidence |
| [ISSUE-draft.md](ISSUE-draft.md) | Feature request in the OpenBSW issue template; filed as #664 |
| [upstream-snapshot.json](upstream-snapshot.json) | State of #664 when recorded |
| [0001-transport-router.patch](0001-transport-router.patch) | `git format-patch` of the signed-off commit, with `Assisted-by` trailer |
| [commit-message.txt](commit-message.txt) | Commit message (gitlint-checked) with `Resolves: #664` |
| [PR-description.md](PR-description.md) | Pull request title and body in the OpenBSW template |
| [validation.md](validation.md) | Checks performed, tools, results and limitations |
| [evidence/](evidence/) | Unit test, coverage, format, copyright, clang-tidy, Bazel, docs and gitlint outputs |
| [artifact-manifest.json](artifact-manifest.json) | SHA-256 of every file in this folder |

## Results at a glance

| Check | Result |
| --- | --- |
| Unit tests | 46/46 passed (42 new with Doxygen descriptions and `StrictMock`s, 4 existing) |
| Coverage | 100 % lines, 99.1 % branches, 100 % functions |
| Format · copyright · clang-tidy | clean · ok · 0 findings |
| Bazel | 2/2 passed |
| Documentation build | no warnings |
| gitlint | ok |
| Patch | applies to `main` with an identical tree |
| Gateway integration | 44/44 on POSIX, 16/16 on the S32K148EVB |

## Before submitting (author)

1. Review: approved by the author on 7 October 2026. ECA (`jnascimento6p0`,
   `jnsagai@gmail.com`), copyright owner and AI-use policy are confirmed.
2. Issue opened: #664 (7 October 2026).
3. PR opened: [#665](https://github.com/eclipse-openbsw/openbsw/pull/665) from `jnsagai/openbsw:feature/transport-router`, commit
   `2fb03107` (the patch in this folder) on `main` `b0550871`. The ECA check passed. The
   CI workflows wait for a maintainer's approval (first contribution). The
   `tested_on_hw` label cannot be set by the author, so the PR asks a committer to set it.
4. Follow the review. If `main` moves or changes are requested, regenerate and force-push
   the branch:

   ```bash
   OBSW_BASE=<main sha> OpenBSW/scripts/openbsw-pr.sh all
   ```

To verify the integrity of this folder:

```bash
python3 -c "import sys; sys.path.insert(0, 'scripts'); import verify_contributions as v; from pathlib import Path; print(v.check_manifest(Path('contributions/openbsw-transport-router/artifact-manifest.json')), 'files ok')"
```
