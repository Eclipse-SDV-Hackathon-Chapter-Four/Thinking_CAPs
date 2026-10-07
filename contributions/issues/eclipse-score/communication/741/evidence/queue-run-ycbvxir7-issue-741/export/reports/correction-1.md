# Correction 1 — Issue #741 (Rust COM API example move)

Status: **BLOCKED — no source change applied; blocker recorded.**
Engineering acceptance: **pending** (unchanged). Prior failed evidence retained.

This correction reads the operator-supplied bounded native result
(`.rust-queue/reports/native-check-summary.json`, sha256 of `native_result.json`
`f1ee60ee494c0f6d2131e3310d4a972ffafbcb6af9202aa81b67eca3653ea9d9`) and the latest
workspace state. It does **not** reset counters, weaken checks, or fabricate evidence.

## 1. Binding

| Field | Value |
| --- | --- |
| Issue / baseline | `eclipse-score/communication` #741 / `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Mode / platform | `implementation`; Linux only (`linux_x64`); DeepSeek Flash only |
| Measured subject hash | `bed9d5e017cff81a6adca2dedeca73e106853858834f31ebfc2d5b24180c42ac` |
| Native result | `jobs/741/execution/check-0/native-result.json` (exit 1; `passed:false`) |

## 2. Measured native result (operator-supplied, not reproduced here)

`kind: measured_native_command`, `attempt: 0`, `passed: false`, `engineering_acceptance: pending`.
The single bounded check is a **query** with `exit_code: 7`, `timed_out: false`,
`infrastructure_error: null`:

```
targets:
  //score/mw/com/doc/tutorial/com-api-example:all
  //score/mw/com/doc/tutorial/com-api-example/com-api-gen:all
ERROR: no such package 'score/mw/com/doc/tutorial/com-api-example/com-api-gen':
BUILD file not found ... - score/mw/com/doc/tutorial/com-api-example/com-api-gen
```

The first target resolves (a probe placeholder `BUILD` exists); only the
`com-api-gen` subpackage is absent. This is **not** `infrastructure_unavailable`
and not a toolchain/network error: the measured failure is a genuine
source-state failure.

## 3. Root cause (measured in this workspace)

The requested change (issue #741) is a filesystem relocation of
`score/mw/com/example/com-api-example/` (13 files) to
`score/mw/com/doc/tutorial/com-api-example/`. **The relocation was never applied.**
`glob` confirms all 13 source files are still at the old path and the destination
holds only the comment-only probe `BUILD` created by the draft stage:

- present at old path: `BUILD`, `USAGE.md`, `main.rs`, `tests_using_tokio_runtime.rs`,
  `src/{lib,consumer,producer}.rs`, `com-api-gen/{BUILD,com_api_gen.rs,vehicle_gen.cpp,vehicle_gen.h}`,
  `etc/{logging.json,mw_com_config.json}`.
- present at new path: `score/mw/com/doc/tutorial/com-api-example/BUILD` (probe placeholder only).

So the measured defect is "the destination package does not exist", and its cause is
the un-applied move — not a defect in a moved source or test.

## 4. Why this correction cannot apply the move (measured boundary)

Probed directly in this correction session:

1. **No delete/rename primitive.** The granted tools are read/write/edit/glob only;
   `write_file` creates/overwrites but cannot remove a path, and every `shell`
   invocation is denied (`Bound Rust workspace/file-tool boundary`, observed for
   `git status`). A "move" therefore cannot remove the 13 source paths, including
   the old package's `BUILD`.
2. **Source configs are unreadable.** `read_file` on `score/**/*.json` is denied by
   the boundary. Re-measured here for
   `score/mw/com/example/com-api-example/etc/logging.json` (with and without
   `limit`) and for an unrelated tutorial config
   `score/mw/com/doc/tutorial/chapter_1/logging.json` — all return
   `Bound Rust workspace/file-tool boundary`. The two required `etc/*.json`
   configs therefore cannot be carried byte-for-byte.
3. **Network/history unavailable.** `web_fetch` (raw upstream source) is denied, and
   `.git` reads / `grep` are unavailable, so the config bytes cannot be recovered
   from upstream or history either.

A faithful move requires (a) deleting/renaming the 13 source paths and (b) copying
the two `etc/*.json` files verbatim. Neither is possible within this boundary.

## 5. Why no additive "fix" was made

Creating the destination tree by `write_file` alone would:

- leave the old `//score/mw/com/example/com-api-example:*` package alive (not a move,
  a duplicate), and
- produce a **broken** destination package, because `BUILD` references
  `etc/logging.json` / `etc/mw_com_config.json` as `data`, plus `MW_LOG_CONFIG_FILE`
  env and the `main.rs` clap default; those two configs cannot be reproduced without
  reading them. Guessing their content would fabricate source data.

Creating only the destination `com-api-gen/BUILD` (the minimum to satisfy the query)
would produce a hollow, non-buildable package — i.e. trading a *query* failure for a
*build* failure while fabricating progress. Per the workflow this is not done:
**no code was changed and no check was weakened.**

## 6. Prerequisite that is missing (disposition: blocker)

Required capability not present in the agent boundary for this change:

- a filesystem **rename/delete** primitive (or an authorized `git mv`/`mv` stage) to
  relocate/remove the 13 source paths, and
- **read access** to the two `score/.../etc/*.json` config files so they can be
  moved byte-for-byte.

Until one of those is provided, the measured target
`//score/mw/com/doc/tutorial/com-api-example/com-api-gen:all` (and the package graph
behind it) cannot exist, and no correct source correction is possible. This correction
therefore records the blocker instead of changing code, per the correction protocol.

## 7. Required next action (for an actor with filesystem authority)

Apply the fully-specified change in `.rust-queue/reports/implementation.md` §4
(13 renames preserving bytes + the 6 reference-edit groups; remove the empty
`score/mw/com/example/` tree and the probe placeholder), then re-run
`.rust-queue/reports/check-plan.json` on `linux_x64` and write a fresh
`native-check-summary.json`. The existing check plan remains valid and is **not**
modified.

## 8. Retained evidence / integrity

- `.rust-queue/reports/native-check-summary.json` — prior **failed** result retained
  unchanged (attempt 0, `passed:false`, exit 1).
- `.rust-queue/reports/{scope.md,implementation.md,review-packet.md,check-plan.json}` —
  retained unchanged; `check-plan.json` is not weakened.
- This correction applied **no source edit** and executed no native command
  (command stages are outside agent authority). No passing evidence is asserted.
- `engineering_acceptance` remains **pending**; no qualification/release claim.
