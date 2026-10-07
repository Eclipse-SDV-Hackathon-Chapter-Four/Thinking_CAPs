# Contribution rules check — transportRouter

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
| Author covered by the Eclipse Contributor Agreement, with the same email as the commits | CONTRIBUTING.md; handbook "Eclipse Contributor Agreement" | met | ECA signed under the Eclipse account `jnascimento6p0`; the author confirmed on 7 October 2026 that the commit email `jnsagai@gmail.com` is that account's address. |
| Contributor (or employer) holds the copyright; header `Copyright (c) {year} {owner}` with a legal entity | Handbook "Copyright Headers" | met | The author confirmed on 7 October 2026 that they hold the copyright personally; headers name `Jefferson Nascimento`, 2026. |
| Disclose generative AI use | Handbook "Using Artificial Intelligence" → "Disclosure"; genai guidelines "Be transparent" | met | Every new file except the one-line `module.spec` has an AI disclosure comment below the header; the commit has `Assisted-by: Anthropic Claude Opus 5.5`. No `Co-authored-by` for the tool, which has no ECA. |
| Human review and verification of AI-generated content | Genai guidelines "Verify accuracy and vet output" | author | Tests and gates pass (below). The author's review statement of 7 October 2026 covered `doipClient`; confirm it for this module before filing the issue. |
| Use of the AI platform consistent with the employer's policy and the platform's terms | Genai guidelines "Responsibilities" | met | Confirmed by the author on 7 October 2026. |
| AI-generated portions: optional `CC0-1.0` dedication (`Apache-2.0 AND CC0-1.0`) | Handbook disclosure template ("could use") | open | Not applied: OpenBSW's `cr_checker` expects `SPDX-License-Identifier: Apache-2.0`. Asked in #663 and in the [issue draft](ISSUE-draft.md); follow the committers' answer. |
| No third-party content without IP review | Handbook "Third Party Content" | met | Only new code; dependencies are OpenBSW modules and ETL already in the repository. |

## OpenBSW

| Rule | Source | Status | Evidence / action |
| --- | --- | --- | --- |
| Discuss a new feature in an issue before the PR | CONTRIBUTING.md; `pull_request.rst` ("adding a completely new feature" must be discussed) | open | [ISSUE-draft.md](ISSUE-draft.md), ready for the author's review; not filed. Open the PR after the committers agree. |
| Fork, branch, commit, push, open PR | CONTRIBUTING.md | open | Steps in [README.md](README.md). |
| Commit message: subject ≤ 72, capital, imperative, no period; body ≤ 72; what and why | `commit_message.rst`, `.gitlint` | met | [evidence/gitlint.txt](evidence/gitlint.txt) |
| Reference the ticket in the commit body | `commit_message.rst` "Reference Tickets" | open | `Resolves:` with the placeholder `#TBD`; replace it with the issue number and regenerate the patch |
| PR description follows the template; one commit → may equal the commit message | `pull_request.rst`, PR template | met | [PR-description.md](PR-description.md) |
| `tested_on_hw` or `no_hw_test_required` tag | `pull_request.rst` "Tags" | met (to set) | Tested on the S32K148EVB through the gateway (16 board tests); tag `tested_on_hw`. |
| Module structure: `include/`, `src/` by namespace, `doc/index.rst`, `test/`, `mock/gmock/include`, `module.spec`, `CMakeLists.txt` | `module.rst` | met | Patch file list; `module.spec` as `transportRouterSimple` |
| `BUILD.bazel` with standard rules | `module.rst` "BUILD.bazel" | met | [evidence/bazel-test.txt](evidence/bazel-test.txt): `transport_router_test` and `transport_router_simple_test` pass |
| Module documentation with introduction, features, integration, configuration, API, example | `documentation/*.rst` | met | `doc/index.rst`; Sphinx build without warnings ([evidence/docs-build.log](evidence/docs-build.log)) |
| GoogleTest; suite `<Class>Test`; CamelCase test names; Doxygen brief per test; no logic in tests; anonymous namespace | `unittests.rst` | met | 42 tests in `TransportRouterTest`, each with a Doxygen block; no `if` in the tests (one null check in a fixture helper) |
| Mocks with gmock, `StrictMock`, existing mocks of the defining module | `unittests.rst` "Mocks" | met | `AbstractTransportLayerMock`, `TransportMessageProcessedListenerMock` (`transport`), `LockMock` (`async`), all `StrictMock` |
| Mocks for the module's own interfaces, each method called in the tests | `unittests.rst` | met | `RouteObserverMock` for `IRouteObserver` in `mock/gmock/include` (CMake `transportRouterMock`, Bazel `transport_router_mock`); both methods are expected in the tests |
| Format: treefmt (clang-format 17, cmake-format, buildifier) | `format.yml` | met | [evidence/treefmt.txt](evidence/treefmt.txt), second pass clean |
| Copyright header check | `copyright.yml` (`tools/cr_checker`) | met | [evidence/copyright.txt](evidence/copyright.txt) |
| Unit tests build without warnings (`-Wall -Werror`) | `practices.rst` | met | [evidence/build-warnings.txt](evidence/build-warnings.txt): 0 |
| clang-tidy with the repository `.clang-tidy` | `clang-tidy.yml`, `practices.rst` | met | [evidence/clang-tidy.txt](evidence/clang-tidy.txt): 0 findings |
| Unit tests and coverage | `build.yml`, `code-coverage.yml` | met | [evidence/ctest.txt](evidence/ctest.txt) 46/46; [evidence/coverage.txt](evidence/coverage.txt) 100 % lines, 99.1 % branches |
| Release notes | `CHANGELOG.md` → `doc/release_notes` | not needed | Upstream PRs do not edit release notes (last 15 merged PRs checked). |
| Do not mix cleanup and features | `commit_message.rst` | met | One commit: the new module and two registration lines |
| Patch applies to current `main` | — | met | Applied with `git am` to `b0550871`; identical tree to the tested one (`c2f3e2f6…`) |

## This repository

| Convention | Source | Status |
| --- | --- | --- |
| Packet with README, issue draft, signed-off patch, commit message, PR description, validation, evidence | packet layout as [openbsw-doip-client](../openbsw-doip-client/README.md) | met |
| SHA-256 artifact manifest checked by `scripts/verify_contributions.py` | [contributions/README.md](../README.md) | met ([artifact-manifest.json](artifact-manifest.json)) |
| Registry entry once an upstream issue exists | [contributions/README.md](../README.md) step 4 | open | Add it when the issue is filed |
| No claim of submission, approval or merge | packet convention | met |
