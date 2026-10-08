# Correction 3 — Issue #741 (Rust COM API example move)

Status: **BLOCKED — no source change applied; missing backend prerequisite recorded.**
Technical completion: **not attainable within the granted boundary.**
Engineering acceptance: **pending** (unchanged). Prior failed evidence retained.

This correction reads the operator-supplied latest bounded native result
(`.rust-queue/reports/native-check-summary.json`, `attempt: 2`) and independently
re-measures the workspace state and the tool boundary. It does **not** reset counters,
weaken checks, modify the operator-supplied summary, or fabricate any evidence or source
data.

## 1. Binding

| Field | Value |
| --- | --- |
| Issue / repository | `eclipse-score/communication` #741 (`open`, label `rust-api`, 0 comments) |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Mode / platform | `implementation`; Linux only (`linux_x64`); DeepSeek Flash only |
| Measured subject hash | `bed9d5e017cff81a6adca2dedeca73e106853858834f31ebfc2d5b24180c42ac` (unchanged across attempts 0–2) |
| Latest native result | `jobs/741/execution/check-2/native-result.json` (sha256 `078ca7b7e2106870656228080f03329a71b4033cc878d83eee4d98e5493b2b8b`); `passed:false`, exit 1 |
| Native infra status | `infrastructure_error: null` — the native run itself was healthy |
| Deliverable report | this file |

## 2. Latest measured native result (operator-supplied)

`kind: measured_native_command`, `attempt: 2`, `passed: false`, `exit_code: 1`,
`engineering_acceptance: pending`. One bounded check:

| kind | targets | exit | timed_out |
| --- | --- | --- | --- |
| query | `//score/mw/com/doc/tutorial/com-api-example:all`<br>`//score/mw/com/doc/tutorial/com-api-example/com-api-gen:all` | 7 | false |

```
ERROR: no such package 'score/mw/com/doc/tutorial/com-api-example/com-api-gen':
BUILD file not found in any of the following directories. Add a BUILD file to a
directory to mark it as a package.
 - score/mw/com/doc/tutorial/com-api-example/com-api-gen
```

**Compared with attempts 0 and 1 this failure is identical** (same bounded tail, same
`measured_subject_hashes_sha256`). No subject change was ever measured; the recorded
observable is a repeated, unchanged failure caused by the still-unapplied move — not a
newly introduced defect and not an infrastructure fault.

## 3. First-hand measurements this correction

Re-measured directly with the granted file tools (no shell, no source writes attempted;
no prior report relied on):

| Observation | Method | Result |
| --- | --- | --- |
| 13 source files still at old path | `glob score/mw/com/example/com-api-example/**` | `BUILD`, `USAGE.md`, `main.rs`, `tests_using_tokio_runtime.rs`, `src/{lib,consumer,producer}.rs`, `com-api-gen/{BUILD,com_api_gen.rs,vehicle_gen.cpp,vehicle_gen.h}`, `etc/{logging.json,mw_com_config.json}` — all present |
| Destination holds only a placeholder | `glob score/mw/com/doc/tutorial/com-api-example/**` | only `BUILD` (read: comment-only probe, defines **no targets**) |
| Destination subpackage absent | `glob .../com-api-example/com-api-gen/*` | **empty** — exactly the package the native error names |
| Readable source/test text | `read_file` on `BUILD`, `main.rs`, `tests_using_tokio_runtime.rs`, `vehicle_gen.h`, `USAGE.md` | succeed (bounded, first-hand) |
| Source configs unreadable | `read_file` on `etc/logging.json`, `etc/mw_com_config.json`, and unrelated `doc/tutorial/chapter_1/mw_com_config.json` (with and without offset/limit) | `Bound Rust workspace/file-tool boundary` |
| Shell unavailable | `shell: pwd` | `Bound Rust workspace/file-tool boundary` |
| Content search unavailable | `grep` on the example package and its `etc/` | `Bound Rust workspace/file-tool boundary` |
| Network unavailable | `web_fetch` of the raw upstream config at the baseline | `Bound Rust workspace/file-tool boundary` |
| Tutorial package BUILD | `read_file score/mw/com/doc/tutorial/BUILD` | lists only `chapter_*` packages; does not reference the example |

Tool inventory confirms there is **no delete/rename primitive** (only read/write/edit/glob;
`write_file` creates/overwrites and cannot remove a path). This matches the carried
observations in `implementation.md` §3 and `correction-1.md`/`correction-2.md`; it is
re-confirmed here rather than assumed.

## 4. Root cause (unchanged)

The requested change (issue #741) is a **filesystem relocation** of
`score/mw/com/example/com-api-example/` (13 files) to
`score/mw/com/doc/tutorial/com-api-example/`. The relocation was never applied. The
measured defect is therefore exactly "the destination package graph does not exist", and
its cause is the un-applied move — not a defect in a moved source or test. **No correctable
source/test defect is independent of the missing move capability.**

## 5. Why this correction applies no code change

The available branch of the correction protocol is the blocker branch: the evidence does
not report `infrastructure_unavailable`, but a **backend prerequisite is missing** in the
granted tool boundary, so code must not be changed and checks must not be weakened.

A faithful move requires both:

1. a filesystem **delete/rename** primitive (or an authorized `git mv`/move stage) to
   remove the 13 old paths and retire the old
   `//score/mw/com/example/com-api-example:*` package; and
2. **read access** to the two `etc/*.json` configs so they can be carried byte-for-byte
   (the moved `BUILD` lists them as `data` + `MW_LOG_CONFIG_FILE`; `main.rs` L72 and the
   Tokio test L44 name them as the default/config path, and the integration test loads
   `/Vehicle/Service1/Instance` and `/Vehicle/Service3/Instance` from `mw_com_config.json`).

Neither is possible here:

- Writing the 11 readable source/`BUILD`/`USAGE.md` files to the new path without the
  configs would leave a **broken** package (`data`/`env` reference missing files; the
  build/test would fail) while the old package stays alive — trading a *query* failure for
  a *build/test* failure, and producing a duplicate rather than a move.
- Reproducing the configs without readable bytes would require **inventing source data**,
  which is prohibited; no readable upstream copy or history is reachable (network, `.git`
  and `grep` are all blocked).
- Creating only the destination `com-api-gen` subpackage (the exact label the error names)
  would be hollow: the parent `.../com-api-example` package still defines no build targets
  and its config data would still be absent, so the build/test/docs/lint obligations behind
  the query would fail. It would only make one query target resolve without correcting the
  change — an action taken merely to make a check succeed, which the workflow forbids.

Therefore **no source or test file was modified and no check was weakened.** The two probe
artifacts from earlier stages (`score/mw/com/doc/tutorial/com-api-example/BUILD`,
`.rust-queue/reports/boundary-test.txt`) are left in place; the agent cannot delete them and
they must be removed by the stage in §6.

## 6. Missing prerequisite (disposition: blocker) and required next action

Disposition: **blocker** — the change is not contradicted by native infrastructure
(`infrastructure_error: null`) and is not a design disagreement; it cannot be executed with
the granted backend capabilities.

Required for an actor with filesystem authority:

1. Apply the fully specified change in `.rust-queue/reports/implementation.md` §4 exactly:
   the 13 byte-preserving renames, the 6 reference-edit groups (`BUILD` deps ×3 +
   `MW_LOG_CONFIG_FILE`; `main.rs` L72; `tests_using_tokio_runtime.rs` L26/L44; `USAGE.md`
   path strings + rebased relative link), remove the now-empty `score/mw/com/example/`
   tree, and remove/overwrite the probe placeholder
   `score/mw/com/doc/tutorial/com-api-example/BUILD`.
2. Re-run `.rust-queue/reports/check-plan.json` on `config=linux_x64` and write a fresh
   `native-check-summary.json`. The existing plan remains valid and is **not** weakened or
   modified (targets are the post-move, BUILD-derived labels; no QNX target).
3. Human reviewers decide the open items in `implementation.md` §7 offline.

## 7. Retained evidence / integrity

- `.rust-queue/reports/native-check-summary.json` — operator-supplied `attempt: 2`
  (`passed:false`, exit 1) **retained unchanged**; attempts 0 and 1 preserved as history.
- `.rust-queue/reports/{scope.md,implementation.md,review-packet.md,check-plan.json}` —
  retained unchanged; `check-plan.json` is not weakened.
- `.rust-queue/reports/correction-1.md`, `correction-2.md` — retained unchanged.
- `.rust-queue/reports/boundary-test.txt` and the comment-only probe
  `score/mw/com/doc/tutorial/com-api-example/BUILD` remain (agent cannot delete them);
  removal is part of §6.1.
- This correction applied **no source edit** and executed **no** native command (command
  stages are outside agent authority). No passing evidence is asserted, no counter reset,
  no qualification/release claim.
- `engineering_acceptance` remains **pending**.
