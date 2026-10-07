# Lifecycle #704 — actual Fabro/DeepSeek Flash attempt

**Qualification failed; the Flash implementation is incomplete.** Four real provider
requests ran through the pinned native Fabro server. The model produced a draft macro,
but Bazel rejects its duplicate profile key and its output has the wrong native JSON
schema. The BUILD reply failed strict JSON validation. No valid Flash patch or passing
native test suite is claimed. The [earlier Codex patch](../lifecycle-704/README.md) remains
unchanged and separately tested; it was excluded from implementation prompts.

The latest owner `go` authorized this qualification-only experiment. Source commit:
`7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`. Native Fabro source:
`1b4fb15281ebb724426f9e480dce48d0100ff79b`. Requests remained within four calls,
24,000 original serialized bytes, 2,000 completion tokens per call and $0.10 conservative
reservations. Source, Skill, role, stage, native cwd and transport bindings are retained.
Global disabled policy, reviewed T032 bytes, prior experiments and upstream remain unchanged.

| Request | Actual result |
|---|---|
| Macro, thinking enabled | 2,000 reasoning tokens, no answer; automatic continuation refused before transmission. |
| Macro, thinking disabled | Structured draft applied by a native Fabro command; subsequently fails native Bazel. |
| BUILD edits and proposed schema correction | DSML shell-call text instead of JSON; command rejects it, no shell tool or BUILD edit executes. |
| S3 advisory critique, JSON mode | Structured review retained; native human gate reached without an answer. |

[summary.json](summary.json) reports **$0.007867 observed cost upper bound**, with actual
billed cost null, and **$0.022398 maximum reservations**. All four native/provider token
counts and original/transmitted request hashes reconcile in
[measurement-reconciliation.json](measurement-reconciliation.json). No token-savings
comparison is measured. Provider reasoning detail absent from a reply remains null.
Bounds use freshly checked [official peak prices](https://api-docs.deepseek.com/quick_start/pricing/).
The native catalog's cost values are stale estimates, not provider bills.

The initial transport ledger stays stopped at `CONTEXT_LIMIT`. A separate remainder
instruction subtracts its used request and full reservation from the same four-call/$0.10
ceiling. It does not reset that ledger. One native nonthinking retry used the documented
[thinking toggle](https://api-docs.deepseek.com/guides/thinking_mode/), supplied through
source-checked native catalog `default_options`; the final advisory stage additionally uses
documented [JSON mode](https://api-docs.deepseek.com/guides/json_mode/). The provider transport
preserves those native fields and every message; only unselected tool declarations are removed.
The remaining ledger closes at `QUALIFICATION_FAILED_HUMAN_REVIEW_REQUEST_CAP`.

Native Git checkpoint preparation twice failed on shallow worker clones before any provider
request. An exact source-file archive without upstream `.git` allowed Fabro to own its local
checkpoints. Fetching history alone did not solve the pinned runtime behavior. No native binary,
global Git policy, source bytes or reference repository was changed for that workaround.
Failed run/event/stage records remain separate. The first macro run's overall native status
reported success despite failed agent/application stages; stage and collector results are
required to determine the qualification result.

[Native probe log](logs/generated-probe.log) confirms the duplicate-key load failure at
`config/mw_com_config.bzl:137`. The temporary three-profile probe BUILD is retained as
[qualification-probe-BUILD.txt](qualification-probe-BUILD.txt), then removed from the source
copy. Generated configuration equivalence, packaging, buildifier and the five affected
native test targets could not be established for an admissible Flash implementation.
[flash-draft.patch](flash-draft.patch) is the rejected draft, preserved without a hand fix
or mechanical formatting. All three original JSON files and BUILD files remain unchanged.

[Flash review](critique-model-output.json) is advisory model output. Speculative findings,
generic finding paths and the proposed repair require human triage; they are not native
evidence or engineering decisions. The independently measured parser/Bazel failures stand.
T033, native impact/export applicability, QNX execution and human acceptance remain open.
No interview answer or authenticated acceptance receipt was fabricated.

Scratch/tools/source copies use the shared, measured external Linux build volume. Credentials
and native private state stay internal. Native co-located worker scratch retains the same
documented private-server limitation as prior qualification. No running queue or global storage
was changed. Only this experiment's native, transport and Bazel servers are stopped.
Operator script snapshots embed disposable paths and are not safe replay instructions;
native activation requires fresh exact bindings. [manifest.json](manifest.json) pins evidence.

Next proposal: use native nonthinking JSON mode from the first implementation request,
present the original native schema explicitly, and stop on any invalid stage result. A new
paid attempt needs a fresh bounded instruction; this experiment cannot be resumed for calls.
