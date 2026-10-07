# Codex review of #560 production integration draft

The draft requires changes. This user-requested Codex review confirms the measured
build blocker and identifies two additional defects in provider termination handling.
It adds review artifacts only: no source repair, native build/test, Fabro start,
DeepSeek invocation, budget reset or engineering acceptance occurred.

The subject is the immutable
[final integration contribution](../score-rust-560-integration-5sejq8fk-results/README.md),
native run `01M49707YMM6QGAPSX4ZDTV5NE`, baseline
`381d43dec900ab6a9076f3f30e7bfbdee019e26e`. Its manifest SHA-256 is
`479e54a9ca827336018a207ade8c7673fea6ff9beb0c3e81b6b994a03c018f85`;
all 164 payloads were verified before review. The final source-vector SHA-256 is
`839b2589fcf094031ca952cc26e5cd3f3125db31723b7d1127e23812d8e5dbb4`.
Machine-readable findings, precise source locations and input hashes are in
`review.json`; deterministic metadata checks are in `verification.json`.

## Findings, ordered by priority

1. **P1: Select the runtime builder's bridge type at both entry points.**
   [subscription_state_app.rs:118](../score-rust-560-integration-5sejq8fk-results/issues/560/changed-source/score/mw/com/test/basic_rust_api/subscription_state_apis/subscription_state_app.rs#L118)
   and line 125 construct `LolaRuntimeBuilderImpl::new()` without a type annotation,
   then pass the runtime into generic helpers. The bound native build reports E0283
   at both bindings. Consequently none of the five new production integration cases
   can run. The existing sync consumer annotates its builder at line 318. Proposed
   repair at both sites: `let mut builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();`.
   This proposal has not been applied or compiled; it does not establish that the
   remaining binary, packaging, tests or lint will pass.

2. **P2: Reject an unsuccessful provider exit after FINISH.**
   `subscription_state_app.rs:296` matches `Ok(Some(_))` and discards the exit
   status; `finish()` then returns `Ok(())`. The provider sends its FINISH
   acknowledgement at line 221 before returning through `provider_entry`, where
   the production runtime is dropped. If it aborts or exits nonzero during teardown
   after that acknowledgement, the controller can still print “completed” and exit
   successfully. This undermines the lifecycle scenarios' result. Preserve the exit
   status and require `status.success()` before reporting successful completion.
   Add a focused failure case with acknowledgement followed by nonzero exit when a
   further correction/test budget is authorized. This is a static finding, not an
   observed failure of the unexecuted native harness.

3. **P2: Retain child ownership through wait errors.**
   At `subscription_state_app.rs:292`, `self.child.take()` moves the only child
   handle into a local variable. The `try_wait()` error branch at line 305 returns
   without killing/reaping it or restoring it to the session. During unwinding by
   `?`, `ProviderSession::drop` finds no child to terminate but still joins the
   stdout reader at lines 395–396. If the provider is still alive with stdout open,
   this join can block beyond the advertised exit deadline. Rust's `Child` does not
   automatically kill or wait when its handle is dropped, as documented by the
   [Rust standard library](https://doc.rust-lang.org/std/process/struct.Child.html).
   Keep ownership in the session until reaping completes, or use a cleanup guard
   that handles every error path before joining. Exercise a wait-error path with a
   live child as a focused failure case if implementation resumes. The precise OS
   error and a native hang have not been reproduced; the cleanup guarantee is
   unsupported on this branch.

## Scope and evidence limits

All four newly added test-package files were reviewed, with selected supporting
public API, Rust subscription ownership/Drop, FFI trampoline/wrapper, C++ state
machine and existing consumer excerpts. This is not a complete audit of all twelve
preceding library/design files or arbitrary concurrency/FFI behavior. Hash verification
establishes packet integrity, not semantic adequacy or tool qualification.

The five cases target real LoLa notification, replacement, unset, false-return
disposal and active-handler drop, with phase-controlled withdrawal/reoffer, captured
disposal counters and main-thread queries. The subscription retains its proxy via
`_proxy: self.proxy_instance.clone()` in `consumer.rs:387`; letting the local consumer
leave scope in `discover_and_subscribe` is not itself evidence of a dangling proxy.
The callbacks do not re-enter the subscription, consistent with the documented
state-machine-lock restriction. These observations do not constitute passing tests.

Only the new binary's Linux build ran in the reviewed attempt, and it failed.
**Five defined cases, zero executed.** New integration, sync/async regression, Clippy
and explicit-label query groups were not reached. Prior passing measurements remain
carried evidence for the preceding source and do not validate this harness.

The Flash supervisor's compiler diagnosis and zero-case conclusion are supported.
Its blanket statement that no cleanup leak/deadlock path exists needs qualification
by finding 3. Section 8 item 11's claim about stale unit names in the current plan is
incorrect: the current check-plan contains the four new build/test/lint/query groups.
Do not infer that a documentation snippet was copied solely from a matching pattern.
The complete packet includes environment/compiler identity artifacts; identities are
not qualification. Original supervisor output remains unchanged.

## Continuation

#560's lifetime correction budget remains **3/3 used, zero remaining**. This Codex
review is separately authorized by the user's “review it using codex now” request;
it does not authorize a fourth correction or change other queue budgets. Source and
sealed prior evidence remain unchanged. No runtime was restarted. Offline human
engineering acceptance, native trace/applicability and qualification remain pending.

If the user explicitly revises the correction budget, address all three findings,
then run the bound Linux build, five-case integration target, existing regression
targets, native Clippy and explicit-label query. Retain full logs, actual case counts
and final source hashes. Additional obligations concerning FFI failure ownership,
concurrency, downstream/mock/example coverage and qualification remain open.
