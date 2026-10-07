# Correction 1 — eclipse-score/communication #173

Issue: *Improvement: Usage and Integration of External Crates in COM-API (e.g., paste crate)*
Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`
Mode: `assessment`. Platform: Linux only. Engine: DeepSeek Flash.
Correction budget: `max_source_corrections: 3` (`task.json`); this is correction **1**.

## 1. Bounded native result supplied by the operator

The latest measured native result is the `check 173 0` collector run, which failed
deterministically while validating the Linux collector check-plan schema:

```
Traceback (most recent call last):
  File ".../driver_linux.py", line 132, in <module>
    raise SystemExit(checks(number, sys.argv[3]))
  File ".../driver_linux.py", line 87, in checks
    assert all(isinstance(t, str) and t.startswith('//') and not any(c in t for c in '\n\r;`$') for t in item.get('targets', []))
AssertionError
```

This is a **measured schema defect**, not `infrastructure_unavailable` and not a missing
design/backend prerequisite. It was corrected rather than converted into a blocker.

## 2. Root cause (measured)

`.rust-queue/reports/check-plan.json` used four `query` entries whose targets were
external-repo crate-index labels:

- `@score_communication_crate_index//:pastey`
- `@score_communication_crate_index//:thiserror`
- `@score_communication_crate_index//:futures`
- `@score_communication_crate_index//:paste`

The collector schema requires every `targets` entry to be a native
`//actual/native/package:target` label (the assertion rejects any target not starting
with `//`). External-repo labels (`@repo//…`) are outside the accepted form, so the
whole check plan failed to validate even though all other labels already conformed.

## 3. Correction applied

Only `.rust-queue/reports/check-plan.json` (an agent-produced check-inventory artifact)
was corrected. No repository source, test, dependency, lockfile, BUILD file, lint policy
or pin was changed.

The four `query` checks were re-targeted to the **actual BUILD-derived native labels**
that consume (or, for the unused crate, would reveal) the named external crates. The
dependency-inventory obligation is preserved for each entry — the checks were not
dropped or weakened.

| Crate | Old (rejected) target | New native target(s) | BUILD anchor |
| --- | --- | --- | --- |
| `pastey 0.2.3` | `@score_communication_crate_index//:pastey` | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/rust:score_com` | `score_com_concept/BUILD:22`; `score_com.rs:144-146` |
| `thiserror 2.0.21` | `@score_communication_crate_index//:thiserror` | `//score/mw/com/rust/score_com_concept:score_com_concept` | `score_com_concept/BUILD:31` |
| `futures 0.3.34` | `@score_communication_crate_index//:futures` | `//score/mw/com/rust/score_com_concept:score_com_concept`, `//score/mw/com/test/basic_rust_api/consumer_async_apis:bigdata-consumer-async`, `//score/mw/com/example/com-api-example:com-api-example-lib` | `score_com_concept/BUILD:30`; `consumer_async_apis/BUILD:39`; `com-api-example/BUILD:26` |
| `paste 1.0.15` (unused) | `@score_communication_crate_index//:paste` | `//score/mw/com/rust/score_com_concept:score_com_concept` | query the consumer's dependency graph to show no `paste` reference |

Each entry's `reason` and `native_obligation` retain the original dependency-inventory
intent and now cite the concrete BUILD locations. All targets in the resulting
`check-plan.json` start with `//` and contain none of the forbidden characters.

The matching row in `.rust-queue/reports/review-packet.md` was updated to the same
native labels so the packet does not document the rejected label form.

## 4. Evidence basis (bounded, native)

Targets were derived from inspected BUILD files (bounded reads):

- `score/mw/com/rust/score_com_concept/BUILD` — `proc_macro_deps: pastey`; `deps: thiserror, futures`.
- `score/mw/com/rust/BUILD` — target `score_com`.
- `score/mw/com/test/basic_rust_api/consumer_async_apis/BUILD` — `deps: futures`.
- `score/mw/com/example/com-api-example/BUILD` — `deps: futures`.
- `score/mw/com/rust/score_com_macros/BUILD` — unchanged (quote/syn, already valid labels).
- `score/mw/com/test/basic_rust_api/consumer_sync_apis/integration_test/BUILD` and
  `.../consumer_async_apis/integration_test/BUILD` — unchanged targets confirmed.
- `quality/dependency_compatibility_checker/tests/BUILD` — unchanged targets confirmed.

No label was invented; each new label corresponds to a target declared in the baseline
BUILD files.

## 5. Preserved failed / missing evidence (not reset, not fabricated)

- The failed `check 173 0` result above is retained verbatim. It is **not** counted as a
  pass; the corrected check-plan still requires a fresh deterministic collector run.
- `.rust-queue/reports/native-check-summary.json` remains **missing** in this workspace;
  no native check has been executed by this agent (shell/measurement are outside agent
  authority). All `check-plan.json` entries remain **planned, not run**.
- Previous reports (`scope.md`, `dependency-assessment.md`, `implementation.md`,
  `review-packet.md`) are retained; only the check-plan and the one review-packet row
  changed. No passing evidence is asserted.
- Correction counters were not reset; this is correction 1 of at most 3.

## 6. Remaining unknowns and acceptance status

- Provenance/license/advisory status of `pastey`, `thiserror` and `futures` remains
  unverified (network blocked, nothing vendored).
- The integrate-vs-manual external-crate policy decision remains open and tracked to
  `score-crates#42`, which is unreachable locally.
- `wp__tlm_plan` / `wp__tool_verification_report` have no project instances; tool
  applicability/qualification is unknown.
- No Rust API-surface lock exists; QNX and sanitizer variants are excluded by policy.

Status: the measured schema defect is corrected; re-validation of `check-plan.json` by
the deterministic collector is **pending** and outside agent authority. Native
engineering acceptance remains a **pending offline human decision**; no qualification,
certification or release status is asserted.
