# Contribution rules check — doipClient

Checked on 7 October 2026 against OpenBSW `main` at `b0550871` (CONTRIBUTING.md,
`doc/dev/guidelines/*`, `.gitlint`, PR and issue templates, CI workflows), the Eclipse
Foundation Project Handbook (current as of 2026-09-25: ECA, copyright headers,
generative AI guidelines) and this repository's
[contribution conventions](../README.md).

Status: **met** (checked here, evidence linked), **author** (only the author can do or
confirm it), **open** (to do at submission).

## Eclipse Foundation

| Rule | Source | Status | Evidence / action |
| --- | --- | --- | --- |
| Author covered by the Eclipse Contributor Agreement, with the same email as the commits | CONTRIBUTING.md; handbook "Eclipse Contributor Agreement" | **author** (partly confirmed) | The author stated on 7 October 2026 that the ECA is signed under the Eclipse account `jnascimento6p0`. Still to confirm: the commit email `jnsagai@gmail.com` is an address of that account (the ECA check matches the email). |
| Contributor (or employer) holds the copyright; header `Copyright (c) {year} {owner}` with a legal entity | Handbook "Copyright Headers" | **author** | Headers name `Jefferson Nascimento`, 2026. Confirm that no employer owns this work; otherwise name the employer. |
| Disclose generative AI use | Handbook "Using Artificial Intelligence" → "Disclosure"; genai guidelines "Be transparent" | met | Every new file has an AI disclosure comment below the header; the commit has `Assisted-by: Anthropic Claude Opus 5.5`. No `Co-authored-by` for the tool, which has no ECA. |
| Human review and verification of AI-generated content | Genai guidelines "Verify accuracy and vet output" | met | The author stated on 7 October 2026 that they reviewed the code; tests and gates pass (below). |
| Use of the AI platform consistent with the employer's policy and the platform's terms | Genai guidelines "Responsibilities" | **author** | Confirm. |
| AI-generated portions: optional `CC0-1.0` dedication (`Apache-2.0 AND CC0-1.0`) | Handbook disclosure template ("could use") | open | Not applied: OpenBSW's `cr_checker` expects `SPDX-License-Identifier: Apache-2.0`. Asked in the [issue](ISSUE-draft.md); follow the committers' answer. |
| No third-party content without IP review | Handbook "Third Party Content" | met | Only new code; dependencies are OpenBSW modules and ETL already in the repository. |

## OpenBSW

| Rule | Source | Status | Evidence / action |
| --- | --- | --- | --- |
| Discuss a new feature in an issue before the PR | CONTRIBUTING.md; `pull_request.rst` ("adding a completely new feature" must be discussed) | open | Open [ISSUE-draft.md](ISSUE-draft.md) first; open the PR after the committers agree. |
| Fork, branch, commit, push, open PR | CONTRIBUTING.md | open | Steps in [README.md](README.md). |
| Commit message: subject ≤ 72, capital, imperative, no period; body ≤ 72; what and why | `commit_message.rst`, `.gitlint` | met | [evidence/gitlint.txt](evidence/gitlint.txt) |
| Reference the ticket in the commit body | `commit_message.rst` "Reference Tickets" | open | Add `Resolves:` with the issue number once it exists, then rerun the `all` step. |
| PR description follows the template; one commit → may equal the commit message | `pull_request.rst`, PR template | met | [PR-description.md](PR-description.md) |
| `tested_on_hw` or `no_hw_test_required` tag | `pull_request.rst` "Tags" | met (to set) | Tested on the S32K148EVB through the gateway; tag `tested_on_hw`. |
| Module structure: `include/`, `src/` by namespace, `doc/index.rst`, `test/`, `module.spec`, `CMakeLists.txt` | `module.rst` | met | Patch file list; `module.spec` `oss: true` like `doip` |
| `BUILD.bazel` with standard rules | `module.rst` "BUILD.bazel" | met | [evidence/bazel-test.txt](evidence/bazel-test.txt): `doip_client_test` and `doip_test` pass |
| Module documentation with introduction, features, integration, configuration, API, example | `documentation/*.rst` | met | `doc/index.rst`; Sphinx build without warnings ([evidence/docs-build.log](evidence/docs-build.log)) |
| GoogleTest; suite `<Class>Test`; CamelCase test names; Doxygen brief per test; no logic in tests; anonymous namespace | `unittests.rst` | met | 20 tests in `DoIpClientTransportLayerTest`, each with a Doxygen block |
| Mocks with gmock, `StrictMock`, existing mocks of the defining module | `unittests.rst` "Mocks" | met | `AbstractSocketMock`, `TransportMessageProvidingListenerMock`, `TransportMessageProcessedListenerMock`, `AsyncMock`, all `StrictMock` |
| Mocks for the module's own interfaces | `unittests.rst` | met | The module defines no new interface |
| Format: treefmt (clang-format 17, cmake-format, buildifier) | `format.yml` | met | [evidence/treefmt.txt](evidence/treefmt.txt), second pass clean |
| Copyright header check | `copyright.yml` (`tools/cr_checker`) | met | [evidence/copyright.txt](evidence/copyright.txt) |
| Unit tests build without warnings (`-Wall -Werror`) | `practices.rst` | met | [evidence/build-warnings.txt](evidence/build-warnings.txt): 0 |
| clang-tidy with the repository `.clang-tidy` | `clang-tidy.yml`, `practices.rst` | met | [evidence/clang-tidy.txt](evidence/clang-tidy.txt): 0 findings |
| Unit tests and coverage | `build.yml`, `code-coverage.yml` | met | [evidence/ctest.txt](evidence/ctest.txt) 20/20; [evidence/coverage.txt](evidence/coverage.txt) 94.6 % lines |
| Release notes | `CHANGELOG.md` → `doc/release_notes` | not needed | Upstream PRs do not edit release notes (last 15 merged PRs checked). |
| Do not mix cleanup and features | `commit_message.rst` | met | One commit: the new module and two registration lines |
| Patch applies to current `main` | — | met | Applied with `git am` to `b0550871`; identical tree to the tested one |

## This repository

| Convention | Source | Status |
| --- | --- | --- |
| Packet with README, issue draft, signed-off patch, commit message, PR description, validation, evidence | [openbsw-transport-router](../openbsw-transport-router/README.md) layout | met |
| SHA-256 artifact manifest checked by `scripts/verify_contributions.py` | [contributions/README.md](../README.md) | met ([artifact-manifest.json](artifact-manifest.json)) |
| Registry entry once an upstream issue exists | [contributions/README.md](../README.md) step 4 | open (after the issue is opened) |
| No claim of submission, approval or merge | packet convention | met |

## Related packet: transportRouter

The earlier [transportRouter packet](../openbsw-transport-router/README.md) does not yet
meet the same rules: its 42 tests have no Doxygen descriptions, two mocks are `NiceMock`,
the `IRouteObserver` mock lives in the test instead of a module `mock/` folder, test helpers
contain `if` logic, its files and commit carry no AI disclosure, and it is based on
`432b9be6`. Bring it to the same state before submitting it.
