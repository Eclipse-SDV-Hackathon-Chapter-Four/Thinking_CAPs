# Prepared OpenBSW contribution: doipClient (DoIP client transport layer)

Prepared on 7 October 2026. The feature issue is open as
[eclipse-openbsw/openbsw#663](https://github.com/eclipse-openbsw/openbsw/issues/663); the pull
request is not opened yet, and no maintainer approval or merge is claimed.

- **Upstream:** [eclipse-openbsw/openbsw](https://github.com/eclipse-openbsw/openbsw),
  base `main` at `b0550871b7a44ae47bb9b7c68af84fb9115bfa77`.
- **Change:** a new module `libs/bsw/doipClient` and two registration lines. No existing
  module changes.

OpenBSW has only the DoIP server side. This module adds the client side, so an OpenBSW
node can send diagnostic messages to other DoIP entities, for example a gateway to the
Ethernet ECUs behind it. It came out of the [OpenBSW zonal diagnostic gateway](../../OpenBSW/README.md#doip-routes-ethernet-zonal-ecus),
which builds from the same source in [`OpenBSW/contrib/`](../../OpenBSW/contrib/libs/bsw/doipClient).

## Review artifacts

| Artifact | Content |
| --- | --- |
| [compliance.md](compliance.md) | Every OpenBSW, Eclipse Foundation and repository rule checked, with status and evidence |
| [ISSUE-draft.md](ISSUE-draft.md) | Feature request in the OpenBSW issue template; filed as #663 |
| [upstream-snapshot.json](upstream-snapshot.json) | State of #663 when recorded |
| [related-issues/](related-issues/) | Three bug reports for existing OpenBSW code, with reproduction tests on `main`; filed on 7 October 2026 as [#660](https://github.com/eclipse-openbsw/openbsw/issues/660), [#661](https://github.com/eclipse-openbsw/openbsw/issues/661), [#662](https://github.com/eclipse-openbsw/openbsw/issues/662) |
| [0001-doip-client.patch](0001-doip-client.patch) | `git format-patch` of the signed-off commit, with `Assisted-by` trailer |
| [commit-message.txt](commit-message.txt) | Commit message (gitlint-checked) |
| [PR-description.md](PR-description.md) | Pull request title and body in the OpenBSW template |
| [validation.md](validation.md) | Checks performed, tools, results and limitations |
| [evidence/](evidence/) | Unit test, coverage, format, copyright, clang-tidy, Bazel, docs and gitlint outputs |
| [artifact-manifest.json](artifact-manifest.json) | SHA-256 of every file in this folder |

## Results at a glance

| Check | Result |
| --- | --- |
| Unit tests | 20/20 passed (gmock `StrictMock`s) |
| Coverage | 94.6 % lines, 97.2 % functions |
| Format · copyright · clang-tidy | clean · ok · 0 findings |
| Bazel | 2/2 passed |
| Documentation build | no warnings |
| gitlint | ok |
| Patch | applies to `main` with an identical tree |
| Gateway integration | 14/14 DoIP tests on POSIX, 5/5 on the S32K148EVB |

## Before submitting (author)

1. Code review: done by the author (7 October 2026).
2. ECA (`jnascimento6p0`, `jnsagai@gmail.com`), copyright owner and AI-use policy:
   confirmed by the author ([compliance.md](compliance.md)).
3. Issue opened: #663 (7 October 2026). Wait for the committers to agree on the approach.
   The three [related issues](related-issues/) are filed as #660, #661, #662.
4. The commit references #663 (`Resolves:`). Before the PR, regenerate the patch on the
   then-current `main`:

   ```bash
   OBSW_BASE=<main sha> OpenBSW/scripts/doip-client-test.sh all
   ```

5. Fork, apply the patch (`git am 0001-doip-client.patch`), push, and open the PR with
   [PR-description.md](PR-description.md) and the tag `tested_on_hw`.
6. Record the issue and PR URLs here and add an entry to [registry.json](../registry.json).
