# Lifecycle #704 — guarded Fabro / DeepSeek Flash retry

Flash produced the configuration macro and three BUILD edits through native Fabro.
All **113 native test cases** in five affected targets passed, with no failures/skips.
All three generated configurations exactly match the original parsed JSON, and the
integration tar retains its original `etc/mw_com_config.json` payload/path.

The fresh final graph ran a deterministic evidence command, then Flash advisory review,
then stopped at an unanswered native human gate. Its original/projected requests, full
provider reply, native usage and hashes reconcile under the corrected transport. All
paid ledgers, private run bindings, loopback servers and the disposable Bazel server are
now stopped. No upstream issue action, PR, publishing or engineering acceptance occurred.

## Review artifacts

- [Portable Flash-produced patch](lifecycle-704-flash.patch), SHA-256
  `c8a33936900b24c13b46298e929d4ef483d0e128d44f9a2cce97909f55702f01`.
- [Summary](summary.json), [configuration equality](configuration-equivalence.json),
  [package equality](packaged-configuration-equivalence.json),
  [test results](native-test-results.json), [unit runfiles](unit-runfiles-equivalence.json),
  [clean patch application](portable-patch-check.json), and [final formatting](buildifier-final.json).
- [Final guarded proof](fresh-proof-reconciliation.json), [native stages](critique-stages.json),
  [unanswered gate](human-gate-before-shutdown.json), and [verified shutdown](shutdown-verification.json).
- [Unchanged Flash advisory](critique-model-output.json) and
  [draft evidence responses](review-evidence-responses.md). Its high consumer-inventory
  concern has a new source sweep supplied for human assessment, not automatic acceptance.
- [Actual usage](usage-reconciliation.json), [retention gap](transport-retention-gap.json),
  [operator inputs](operator-inputs/), [operator scripts](operator-scripts/),
  [original sources](original-source/), [final sources](final-source/) and [license notices](source-license/).

## Scope and measured limitations

Baseline: eclipse-score/lifecycle `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`.
Native source ID `feat_arc_sta__lifecycle__cfg_params_static`, version 1, status valid.
Pinned Fabro source `1b4fb15281ebb724426f9e480dce48d0100ff79b`; native catalogue alias
`deepseek-v4-flash` is served as DeepSeek Flash. Thinking was disabled and JSON mode enabled.
The earlier Codex solution was excluded from implementation prompts. Buildifier formatting
is retained separately from the actual structured model output and native command application.

The owner waived this issue qualification's limited DeepSeek budget and requested autonomous
continuation followed by inactivity. [Authorization](../../deepseek-budget-exception.md)
leaves the default policy and all 20 T032 reviewed hashes unchanged. Five new paid requests
have a conservative peak-price observed upper bound of **$0.014952**; actual billed cost
is unavailable. Native catalogue costs are not invoices. These are generation/review calls,
not B1–B5 token-savings measurements.

Two initial legacy transport envelopes were overwritten when separate ledgers reused
ticket-zero filenames. Their prompts, structured outputs, exact native agent usage and
ledger hashes remain, but the missing envelopes were not reconstructed or presented as
original bytes. The transport now uses full instruction-SHA namespaces and exclusive file
creation; tests show two independent ticket-zero ledgers coexist and a duplicate refuses
before forwarding. The fresh final proof has complete raw records. The old failed four-call
experiment and the earlier valid Codex patch/evidence remain unchanged.

Other retained failures include a nonunique/no-op model edit rejected before source writes,
a stopped run binding caught before paid forwarding, the native Starlark indent type error
repaired by Flash, and an empty native non-Git worker caught before review. The final native
command initializes only checksum-verified selected files into that worker, validates source
and measurement freshness, and then permits advisory review. Native server process-title
rewriting required PID/executable/private-storage-FD checks for the final verified shutdown.

The framework's initial full suite had 2,089 passes, 22 skips and four failures caused by a
missing `SCORE_FABRO_BIN` environment setting. All four passed when rerun with the pinned
binary. After the transport fix, all 102 affected optimization tests passed. Ruff, mypy,
foundation consistency, frozen dependency sync and package build pass; retained logs preserve
these distinctions. QNX execution, full native impact/export closure, T033 engineering
acceptance and real-task B1–B5 savings remain unmeasured. Human T032/T033 markers stay open.

The experiment is idle. Resume requires fresh protected bindings; stopped ledgers cannot
silently authorize another paid call.
