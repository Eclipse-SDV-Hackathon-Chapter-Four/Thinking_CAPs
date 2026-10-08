# SOME/IP #84 — native CI applicability

Mapped from workflows at `f8a196c3b16d5172d898394ab99b0ed81346d63d`.
Copies and hashes are captured under `native-policy/`. This matrix is a record of
what was measured and what still requires execution or actual maintainer disposition.
It supplies no waiver and does not replace GitHub branch protection checks.

| Native gate | Current amended revision | Remaining action |
| --- | --- | --- |
| Common PR checks / ECA / DCO | Account lookup passes; user-authorized DCO sign-off on local native commit `28b0d84c`; no PR yet | Actual commit author/committer eligibility and common PR checks must pass |
| Formatting | Four native `//:format.check` targets passed | Eventual upstream check still required |
| pre-commit | All hooks passed; policy/lockfile unchanged | Preserve on submitted revision |
| Host build and tests, default | SOCom unit target passed, 689 cases | Run applicable full `bazel build //...` / `bazel test //... --build_tests_only` workflow |
| Host ASAN/LSAN/UBSAN and TSAN | Not rerun on this revision | Execute native sanitizer matrix |
| Linux QEMU integration, default and sanitizers | Original six-target/13-case measurement retained as history | Execute current native integration matrix; historical QNX exclusion is not a new waiver |
| Performance and flamegraphs | Original two-target/12-dataset measurement retained as history | Current native workflow result or maintainer disposition |
| Coverage / docs / quality pack | Not rerun on this revision | Execute corresponding native workflows |
| `clang-tidy.check` / `ruff.check` | Not rerun on this revision; formatting's ruff check covers formatting only | Execute native analyzer checks |
| Cross compilation | Conditional on `test-cross` label or non-PR/merge-queue event | Apply the actual workflow condition and collect required results |
| QNX | Conditional on `test-qnx` label or non-PR-target/merge-queue event | Authorized QNX runner/toolchain and required results; no local full-platform claim |
| License / Dash / IP | Native copyright and REUSE hooks pass; IP request draft prepared | Actual license check plus project committer/IP Team determination; hook success is not IP approval |
| `ci/can_merge` and `ci_pull_request_target/can_merge` | No native PR; not evaluated | All applicable needed jobs must succeed under actual workflow conditions |

The native CI permits jobs skipped by its event/label conditions; it rejects needed
jobs that fail or are cancelled. Any broader platform, qualification or analyzer
acceptance decision belongs to the actual project reviewers.

Assisted-by: OpenAI Codex (model revision unavailable)
