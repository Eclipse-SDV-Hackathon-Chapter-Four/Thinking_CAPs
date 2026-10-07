# Communication #560 — Codex supervisor, attempt 1

Static review only. No native build, test, service start, source edit or engineering acceptance was performed by this supervisor. Native measurement is pending for this report.

## Bound subject and authority

- Workspace: `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-rust-560-codex-eppa905r/workspaces/560`.
- Incoming source-vector SHA-256: `839b2589fcf094031ca952cc26e5cd3f3125db31723b7d1127e23812d8e5dbb4`; all 2,190 paths exist. Fresh read-only hashing finds changes in only the two authorized files.
- Current `subscription_state_app.rs` SHA-256: `119c05269330945392776bf0834a47933f8c3c4027de91cbc0d749717a6d9228`.
- Current `BUILD` SHA-256: `27c83f6f777e3b572f44fd2f4d46c0c836b09515ff84a4c8de45b9b3d92df01c`.
- Reviewed the immutable previous Codex review and supplied authority/binding. Historical corrections remain 3; this newly authorized Codex budget has attempt 1 reserved, 1/3 used and 2 remaining. Other queue budgets are unaffected. Linux x86_64 only; QNX excluded.

Source locations below are relative to `score/mw/com/test/basic_rust_api/subscription_state_apis/`.

## Static verdict

No blocking defect identified in these changes. They address all three findings from the previous review; build and behavioral success remain unmeasured here.

1. **Builder selection:** `subscription_state_app.rs:118` and `:125` explicitly select `LolaRuntimeBuilderImpl`. Supporting native `com-api-runtime-lola/runtime.rs:59` declares its default bridge as `LolaFFIBridge`; the annotation therefore resolves the formerly unconstrained generic builder toward the production bridge. It does not prove compilation succeeds.

2. **Ownership on failure:** `:295–315` polls through `self.child.as_mut()`, retaining ownership across FINISH acknowledgement errors, exit timeout and injected wait errors. `:316` releases the child handle only after an observed exit. Existing `Drop` at `:398–410` can then kill/reap a still-owned child before joining its stdout reader. This repairs the specific previous lost-handle branch.

3. **Exit result:** `:320–322` rejects an unsuccessful provider exit despite a prior FINISH acknowledgement. `:317–318` also propagates reader panic. Controller completion at `:497–499` remains gated on successful `finish()`.

4. **Shared setup:** `:437–470` factors piped-child setup without replacing the production provider. Both current callers configure piped stdin/stdout; the production caller still spawns the same executable with `--provider` at `:422–434`.

5. **Focused subprocess tests:** `:981–1009` cover acknowledgement followed by exit 0, acknowledgement followed by exit 7, and injected wait error with a live owned child followed by Drop/reaping. The third test uses `exec sleep`, avoiding a stub grandchild holding stdout open. `BUILD:45–52` adds the native `rust_test` on the actual binary crate, restricted to Linux x86_64. These cases test controller process lifecycle, not subscription callbacks or LoLa correctness.

## Production harness and verification limits

The separate five-case production harness remains intact: notifications (`:712`), replacement (`:756`), unset (`:808`), false-return then drop (`:863`) and active-handler drop (`:906`). Controller/provider entry points build separate production runtimes; the five Python cases in `integration_test/test_subscription_state_apis.py:35–61` invoke that controller and wait for completion. None uses the cfg(test) shell providers or injected wait function. Phase acknowledgements, synchronous state queries, disposal counters, callback observations and marker reception provide concrete checks; passing subprocess cases cannot substitute for these five native integration cases.

Limits: the wait error is injected, not a reproduced OS error. Timeout, acknowledgement failure, pipe-setup failure and reader panic are not separately tested by the three new cases. The unchanged Drop cleanup ignores kill/wait errors and joins without its own timeout; successful cleanup of the owned direct child is not a universal deadline or descendant-cleanup guarantee. No present production provider descendant was identified. These limits do not recreate the repaired lost-handle branch.

Required measured follow-up is the bound build, all three new subprocess cases, all five real production cases, selected existing regressions, native Clippy and explicit-label queries. Retain raw logs, case inventories, source hashes and failures; do not infer readiness from static review or carry earlier results onto changed subjects without justified binding. Native qualification, trace/applicability and authorized offline acceptance remain pending.

Supervisor recommendation: proceed with the already authorized native measurement; do not edit frozen sources based on this report.

