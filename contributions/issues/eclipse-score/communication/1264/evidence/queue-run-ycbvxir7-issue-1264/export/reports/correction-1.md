# Correction 1 — issue #1264 (`thiserror` usage in the Rust COM API)

Baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Mode: assessment (no product source patch). Platform: Linux `linux_x64`. No QNX.
Evidence of record: the failed `check0` native-stage output supplied by the operator.

## Prior failed result (retained, not reset)

`check0` failed before any native check ran. The bounded native result summary is the
collector traceback:

```text
Traceback (most recent call last):
  File ".../driver_linux.py", line 132, in <module>
    raise SystemExit(checks(number, sys.argv[3]))
  File ".../driver_linux.py", line 87, in checks
    assert all(isinstance(t, str) and t.startswith('//') and not any(c in t for c in '\n\r;`$') for t in item.get('targets', []))
AssertionError
```

This failure is preserved. It is a **check-plan schema violation**, not a compiler,
test, or infrastructure failure, and it did not produce any `native-check-summary.json`
(that file remains absent; no passing evidence exists and none is fabricated).

## Measured defect

The collector requires each `checks[].targets[]` entry to be a string that starts with
`//` (repo-internal Bazel label form `//package:target`). `check-plan.json` had one
entry that violated this: the second `query` check used the external-repo hub label
`@score_communication_crate_index//:thiserror` (from `score_com_concept/BUILD` line 31),
which does not start with `//` and therefore trips the assertion at driver line 87.

## Correction applied (measured defect only)

| File | Change | Purpose |
|------|--------|---------|
| `.rust-queue/reports/check-plan.json` | Second `query` check target changed from `@score_communication_crate_index//:thiserror` to the in-repo BUILD-derived label `//score/mw/com/rust/score_com_concept:score_com_concept`; `reason` updated to state that the external hub edge is resolved from the in-repo target that declares it and from `MODULE.bazel.lock` (`lockfile_mode=error`). | Make every target conform to the required `//package:target` form so the collector can consume the plan. |
| `.rust-queue/reports/review-packet.md` | "Required check" cell in the acceptance-trace table updated to the same in-repo query label, retaining the `@score_communication_crate_index//:thiserror` reference as a resolved source edge (not a check target). | Keep the packet consistent with the corrected plan. |

No check was removed, merged, downgraded, or otherwise weakened. The check's kind
(`query`), `native_obligation`, and `config` (`linux_x64`) are unchanged; the resolved
thiserror version/feature/provenance obligation is preserved and now anchored on the
in-repo target that actually declares the dependency edge. All other targets in the
plan already used the `//package:target` form and were left untouched.

## Not changed (deliberately)

- No product source, `BUILD`, `MODULE.bazel`, `MODULE.bazel.lock`, `.bazelrc`, CI, or
  lint-policy file was modified. This is an assessment task and the measured defect was
  confined to the agent-authored check plan.
- The `@score_communication_crate_index//:thiserror` edge remains truthfully recorded in
  `scope.md` §3, `dependency-assessment.md` §3 and §8, and the review packet as the
  source-declared dependency; it is simply not usable as a collector check target.
- No license/maintenance/native-status claim was added or upgraded. `native-check-summary.json`
  is still absent, the engineering retain/replace/internal decision is still pending an
  authorized human, and prior gaps (license text, advisories, traceability) remain open.

## Result of this correction

- The measured schema defect is removed: every `targets[]` value in `check-plan.json`
  now starts with `//` and contains none of the forbidden characters (`\n`, `\r`, `;`,
  `` ` ``, `$`).
- No native check has been executed by this correction; the plan remains "expected /
  unrun". Correctness of the corrected plan must be re-measured by the bound collector
  (the next deterministic stage); no passing result is claimed here.

## Next action

Re-run the deterministic `check` stage on the corrected `check-plan.json` through the
bound Linux collector against baseline `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Retain this file and the prior `check0` traceback as history.
