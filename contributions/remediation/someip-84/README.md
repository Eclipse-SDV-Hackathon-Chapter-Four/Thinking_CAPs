# SOME/IP #84 — current contribution preparation

First item in the ordered compliance remediation. The [DCO submission patch](submission-with-dco.patch)
fixes only duplicate SOCom server registration across minor versions. The broader
[identifier/discovery issue #84](https://github.com/eclipse-score/inc_someip_gateway/issues/84)
remains open. No native PR or bugfix review issue has been created.

Baseline: `f8a196c3b16d5172d898394ab99b0ed81346d63d`. The exact patch SHA-256,
seven changed file hashes and native policy hashes are in [preparation.json](preparation.json).
The earlier owner approval and original sealed evidence remain preserved. That
approval covered the earlier patch and restricted preparation to local work.

The current amendment adds an AI disclosure and Apache-2.0 / CC0-1.0 notice to
the largely generated new regression file, plus complete CC0 terms. Its executable
body and the other five original source/build files remain unchanged. Historical
OpenAI Codex assistance is disclosed; its exact model revision was not retained.
This preparation also used OpenAI Codex. No legal certification or human approval
has been supplied by an agent. The user's subsequent instruction authorized
preparing their DCO sign-off; see [DCO.md](DCO.md). Native commit
`28b0d84c990a539bd61ec107b2f9e66f9ab741a2` and its exported mail patch carry
`Signed-off-by: Jefferson Nascimento <jnsagai@gmail.com>`. The earlier plain patch
and its verified source hashes are unchanged.

## Fresh verification

All results are bound to the current candidate hashes in [native-results.json](native-results.json)
and the retained command records and raw logs:

| Check | Result |
| --- | --- |
| Focused GCC 12 regressions | 91 passed |
| Focused Clang 19 regressions | 91 passed |
| Original comparator with the duplicate-minor-version regression | 1 expected failure; demonstrates the bug |
| Native `//score/socom/test/unit:socom_test`, without cached test results | 689 passed; zero failures/errors/disabled cases |
| Native `//:format.check` | All four targets passed |
| Native `pre-commit run --all-files` | All hooks passed, including copyright, REUSE, module tidy/lockfile, shellcheck and yamlfmt |

The initial focused Clang harness rejected a third-party libstdc++ deprecation.
The corrected attempt uses the original packet's GoogleTest compilation flags;
project sources keep `-Werror`. The initial negative-control compile lacked the
include path after moving the baseline source into scratch. Both failed attempts
remain captured. Native policies, toolchain pins, module lockfile and warning
configuration are unchanged after verification. Native stderr retains Java and
third-party deprecation warnings.

The original Linux integration and profiling results remain historical measurements
of the original patch. They are not described as fresh executions of this amended
revision. [CI applicability](CI-applicability.md) maps the remaining workflow jobs.

## Human and project decisions

Review the [PR draft](PR-body.md), [bugfix tracking issue draft](bugfix-issue-draft.md),
[IP review request](IP-review-request.md) and [review dispositions](HUMAN-DISPOSITION.md).
Current contributor approval is transcribed in [user-approval.json](user-approval.json).
The user-authorized DCO sign-off is prepared; upstream committers must review this exact revision; project
committers must resolve IP and required CI/platform decisions. Jefferson's current
ECA lookup passes; eventual native author/committer checks still have to pass.
See [status.json](status.json). This contribution is not marked ready for official merge.

## Reproduce and verify

Use a disposable checkout of `eclipse-score/inc_someip_gateway` at the baseline,
read its `AGENTS.md` and `CONTRIBUTION.md`, and apply `submission.patch` with
`git apply --check --whitespace=error-all` followed by `git apply --whitespace=error-all`.
Use native Bazel 8.6.0 and the unchanged dependency/toolchain configuration. Keep
scratch in `.llm_tmp/` and caches/output under the managed run root.

```bash
bazel test //:format.check
bazel test //score/socom/test/unit:socom_test --nocache_test_results
pre-commit run --all-files
```

The captured harness scripts and command records document the separate focused
and negative-control executions; their absolute workstation paths are provenance.
From the Thinking_CAPs root, `python3 scripts/verify_contributions.py --json` checks
the prepared packet manifest, original artifacts and patch hashes offline. It
does not rerun native tests or grant acceptance. `artifact-manifest.json` excludes
itself; the registry supplies the current packet location.

Next item after this contribution's disposition: Lifecycle #704.

Policy: [Eclipse Project Handbook](https://www.eclipse.org/projects/handbook/#genai)
and the copied native baseline contribution guide. Captured policy bytes and tool
identities are retained in this packet.

Assisted-by: OpenAI Codex (model revision unavailable)
