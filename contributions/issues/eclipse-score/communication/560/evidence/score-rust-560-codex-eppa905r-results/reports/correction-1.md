# #560 — Codex correction 1 of the additional allowance

User authorized up to three new corrections made by Codex. Historical three attempts
remain recorded. This correction changes only subscription_state_app.rs and its
BUILD under the previously added subscription_state_apis test package; native library,
FFI, C++ source, dependencies, toolchain pins, policies and licenses remain unchanged.

Local review C1: both entry points explicitly type the LolaRuntimeBuilderImpl binding,
matching the source's default production LoLa bridge and existing sync consumer.
Local C2: FINISH acknowledgement is followed by observed child termination and an
explicit successful ExitStatus requirement; reader panic also propagates as failure.
Local C3: try_wait borrows self.child, so acknowledgement, polling-error and timeout
paths retain the owned child for Drop to kill/reap before joining stdout. The handle
is released only after reaping. Piped-child setup is shared by production and tests.

Three native cfg(test) subprocess cases cover successful FINISH/exit, acknowledged
exit 7 rejection, and an injected wait error with a live direct child, followed by
owned-child reaping on Drop. Stub child uses exec sleep, avoiding inherited stdout
from a grandchild. These helper tests are supplementary controller checks; the five
production integration scenarios still spawn the real LoLa provider in another role
of the production executable. No mock notification or direct trampoline substitutes.

Measured native run 01M49A1PAGCVD0BTQPQ6RDPF3F passed all five command groups: binary
build, three helper cases, five production cases plus three sync and three async
regressions, native binary Clippy and explicit-label query. The helper target's XML
has a one-test process wrapper; the raw libtest log records all three named cases.
Production/regression XML enumerates 5+3+3 cases with zero failures/errors/skips.
Native commands, logs, BEP, source hashes and result bindings accompany this report.
Fabro executed only command stages; source corrections were made by this Codex session.

Clippy executed AspectRulesLintClippy on the binary and returned success with two
warnings: unread Observation.invocation and manual_is_multiple_of. Warnings remain
visible; no suppression or policy change was made. Test-code Clippy is not measured.
Wait-error case injects an error rather than reproducing an OS fault. Timeout,
acknowledgement/pipe failures, reader panic, descendant cleanup and arbitrary
concurrency are not exhaustively measured. Existing Drop still ignores kill/wait
errors and does not provide a universal cleanup deadline. Native ownership on future
binding errors, downstream/example coverage, trace/applicability, qualification and
offline human engineering acceptance remain pending.

Disposition: measured scoped correction passes; no second source correction needed
for the three reviewed defects. One of three new attempts used, two unused. This
does not close the upstream issue, establish safety qualification or accept engineering
decisions. Preserve the failed history and immutable prior contributions.
