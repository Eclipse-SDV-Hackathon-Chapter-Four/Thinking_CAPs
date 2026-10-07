# ThreadX #744 implementation notes

Implementation is ready for the deterministic driver's patch freeze, native verification,
and independent review. These are implementation-stage local observations, not driver
verdicts or final acceptance. Human provenance review and verification remain pending.
No commit, sign-off, push, publication, external message, or orchestration/policy-state
edit was performed.

## Starting point and references

The initial checkout was clean at `e73752681bd405deddf247d1cf2b899d502dceaa`, on the
admitted issue branch. No existing fix or regression needed preserving. Before editing,
I read `implementation-plan.md`, `admission.json`, `issue.json` (body and empty comment
list), `upstream-rules.json`, upstream `CONTRIBUTING.md` including its C99/style/MISRA
and attribution conventions, and
`/home/jefferson/Thinking_CAPs/contributions/threadx-744/regression-design.md`.
I inspected the existing native `thread_transition` CMake/recorder pattern, the real
Linux port, common/SMP headers and shims, and the existing planner probe and run logs.
No applicable AGENTS.md was found. The issue's historical SMP macro failure is already
resolved in this base; I did not redo that fix.

## Production change and conversion trace

Only `common/src/tx_thread_create.c` changes in production. Both conversions now use
`ALIGN_TYPE` casts in MISRA and non-MISRA configurations, matching current SMP code.
The original alignment expression, fill order, ULONG-sized guard reservations, sizes,
created-list handling, and all other execution paths are preserved. The function
header describes address preservation without inventing a future release identifier.
An explicit deviation comment names MISRA C:2012/2023 Rule 11.6 and C:2004 Rule 11.3.
This is a justified implementation-defined pointer/integer conversion, not a claim
that formal MISRA analysis or certification has passed.

The traced contracts are:

- Linux/GNU x86_64 declares `ULONG` as unsigned int (4 bytes) and `ALIGN_TYPE` as
  unsigned long long (8 bytes), explicitly for alignment and pointer storage; native
  pointers are 8 bytes. The new arithmetic retains that port contract.
- The old MISRA `TX_POINTER_TO_ULONG_CONVERT` invokes
  `ULONG _tx_misra_pointer_to_ulong_convert(VOID *ptr)`, whose `(ULONG) ptr` cast
  loses high bits before assignment to ALIGN_TYPE. The reverse macro casts its input
  to ULONG before `VOID *_tx_misra_ulong_to_pointer_convert(ULONG input)`.
- `TX_POINTER_TO_ALIGN_TYPE_CONVERT` and `TX_ALIGN_TYPE_TO_POINTER_CONVERT` exist
  only in the non-MISRA branch of `common/inc/tx_api.h`. Calling them unconditionally
  would introduce a build failure. No helper API or global width change is necessary.
- After alignment, the existing `TX_VOID_TO_UCHAR_POINTER_CONVERT`,
  `TX_UCHAR_POINTER_ADD`, and `TX_UCHAR_TO_VOID_POINTER_CONVERT` preserve the pointer
  itself. Their MISRA helpers return `UCHAR *`, accept `UCHAR *, ULONG amount`, and
  return `VOID *`, respectively. Only the small byte count is ULONG.
- Linux x86_64 timeout setup stores the TX_THREAD pointer in the VOID-pointer timer
  extension instead of the scalar timeout parameter. The regression checks this.
- Stack/highest usage fields are VOID pointers, and the real stack-check helper takes
  `TX_THREAD *, VOID **highest_stack`. Linux's real builder already uses ALIGN_TYPE
  for its fake initial stack address. Trace ULONG fields are unchanged and tracing is
  disabled only in this focused lane.
- SMP creation already uses the same two casts. SMP header macros and the two shim
  signatures above retain their explicit ULONG contracts. Linux SMP uses unsigned
  long ULONG and the default ALIGN_TYPE = ULONG (LP64); it lacks this width mismatch.
  SMP production remains unchanged. The separate module-manager narrowing expression
  is outside the authorized scope.

Existing production copyright and AI-disclosure lines are preserved. All new regression
files name Codex (gpt-6.1-sol), use MIT and CC0-1.0 attribution, and state honestly that
human provenance review and verification are pending.

## Native regression and CI discovery

The standalone project is `test/tx/cmake/thread_stack_alignment`; its two C sources
are in `test/tx/thread_stack_alignment`. It uses real Linux/GNU headers and compiles
actual common sources. Unsupported platforms fail standalone configuration explicitly.
Runtime preconditions require widths 4/8/8 and real storage above ULONG's maximum;
missing preconditions fail instead of masquerading as successful defect coverage.

The metadata executable compiles the real `tx_thread_create.c` and `tx_misra.c`.
There is also a non-MISRA control. Port/scheduler recorders have upstream signatures;
the builder records metadata and supplies a pointer into real storage without touching
corrupt stack addresses. The harness owns its five necessary thread globals; this base's
shim declares globals extern, and definitions live in `tx_thread_initialize.c`.

Each executable runs all 16 combinations of start offsets 0..3 and sizes 8192..8195.
Assertions cover full-width stored/recorded start and end, usable size, highest and initial
stack pointers, creation fields/state/status, timeout pointer, circular created-list
links/count, and balanced interrupt/preemption posture. Byte checks cover the complete
original fill region, both reserved guard boundaries, and padding on both sides.
Alignment expectations use remainder and byte offsets instead of duplicating the
production mask. All control blocks remain live for list validation.

The scheduling executable links a separate real Linux kernel using upstream common
and port CMake source lists, with both flags and supported `TX_TIMER_PROCESS_IN_ISR`.
Only a linker wrapper precedes the genuine port builder: it asserts valid full-width
metadata before allowing the builder to create application pthreads or dereference
the fake stack. The original source therefore fails safely before either application
thread is built. The fixed source creates worker and observer suspended, checks initial
metadata and padding, then uses actual `tx_thread_resume`, scheduling, timer sleep/wake,
and completion. Four CTest processes cover every start offset. Padding is checked after
creation and execution. This port models the caller's ThreadX stack with a fake stack
pointer; application execution uses Linux-managed pthread stacks, as in normal Linux
simulation. This is simulator execution, not embedded hardware verification.

Creating suspended threads allows the initial highest-pointer assertion before resume;
the real stack checker may legitimately update highest usage during resume. The metadata
recorder separately asserts create's initial highest-pointer contract. CTest timeouts
bound hangs, and scheduling cases are serial.

`test/tx/cmake/CMakeLists.txt` now adds this directory on Linux/GNU x86_64 independently
of the parent's selected feature configuration. The child resets only inherited directory
options/definitions and applies `-m64`, leaving all native32 targets and flags intact.
It selects its own feature macros and does not inherit regression instrumentation or
trace macros. Changed create code and new C tests compile with `-Werror`; unchanged
shim/kernel sources retain visible native64 warnings under `-Wall -Wextra`.
No diagnostic is suppressed and no existing warning gate or test is weakened.
These ordinary targets participate in the default build, and their tests are discovered
from the host CTest root. Existing `build_tx.sh`/`test_tx.sh` reach them through the parent
project, so neither upstream scripts nor workflows needed modification. Native64 test
objects are not coverage-instrumented; the original parent library coverage lane remains
intact. Final coverage acceptance is left to verification.

## Actual local commands and results

All commands ran from the source checkout. Exact argv, cwd, UTC start times, command
exit codes, and complete stdout/stderr logs are saved in
`implementation-checks/commands.jsonl` and its named `.log` files. The small local
`run.py` recorder reports the child command's exit code in that manifest; its own shell
exit is not used as verification. Build, archive, and object directories all reside
under `evidence/build` on `/dev/loop4`, confirmed by `df -T`. No `/tmp` build was used.

Tools were GCC 11.4.0, CMake 3.22.1, Ninja 1.10.1, and Arm GCC 10.3.1 for the compile-only
M4 checks. GCC 14 is absent. The driver's `/evidence` mount alias is not available in this
session; local commands used the actual sibling evidence directory.

The authoritative final red/green local runs are:

| Local command/log | Exit | Observed result |
| --- | ---: | --- |
| `final-original-configure`, `final-original-build` | 0 each | Final regression compiles against archived admitted original sources. |
| `final-original-ctest` | 8 | MISRA metadata: all 16 cases expose narrowed start/end (64 assertions fail). Four scheduling cases fail on full-width start before the real builder. Non-MISRA control passes. No crash/timeouts. |
| `final-fixed-build`, `final-fixed-ctest` | 0 each | All six standalone tests pass; 16 MISRA cases, 16 control cases, and real scheduling across all four offsets. |
| `host-configure-final`, `host-native64-build`, `host-native64-ctest` | 0 each | All six native64 tests build and pass from the normal host suite configured as `misra_build`. |
| `host-discovery`, `host-native64-commands` | 0 each | Parent discovers six new tests plus the existing native32 stack-checking test; generated native64 commands contain -m64 and both features without -m32 or parent regression/trace definitions. The native32 executable is unbuilt. |
| `host-native32-build` | 1 | Existing native32 library cannot compile: missing `bits/libc-header-start.h` multilib headers. |
| `reference-configure` | 1 | Requested gcc-14 compiler is not found in PATH. No GCC 14 build/runtime claim. |
| `compile-linux-*`, `compile-smp-linux-*`, `compile-cortex-m4-*` | 0 each | All 12 C99 create-service compile checks pass with -Wall -Wextra -Werror: four flag combinations on each port. SMP and M4 are compile-only. |
| `diff-check`, `ai-disclosure`, `port-consistency`, `evidence-integrity` | 0 each | Whitespace, tracked-file AI disclosure, no-regeneration port consistency, and red/green source identity/flag/header checks pass. New-file headers were checked explicitly because the upstream disclosure scanner scans tracked files only. |

Final negative sources were obtained by `git archive` of the admitted SHA's `common`
and `ports/linux/gnu` directories; final regression files were copied unchanged alongside
them. They are in `build/implementation-original-source`; negative binaries are in
`build/implementation-final-red`. Fixed binaries are in `build/implementation-green`;
parent integration binaries are in `build/implementation-host`. `evidence-integrity.log`
checks identical test content in both source trees and original create content against
`git show` at the admitted SHA. The final CMake attribution-only header was copied to
both trees without changing target definitions or C assertions.

Representative exact commands (relative to the source cwd):

```sh
cmake -S test/tx/cmake/thread_stack_alignment -B ../evidence/build/implementation-green -G Ninja -DCMAKE_C_COMPILER=gcc
cmake --build ../evidence/build/implementation-green -j 4
ctest --test-dir ../evidence/build/implementation-green -V
cmake -S ../evidence/build/implementation-original-source/test/tx/cmake/thread_stack_alignment -B ../evidence/build/implementation-final-red -G Ninja -DCMAKE_C_COMPILER=gcc
cmake --build ../evidence/build/implementation-final-red -j 4
ctest --test-dir ../evidence/build/implementation-final-red -V
cmake --build ../evidence/build/implementation-host --target tx_stack_alignment_misra tx_stack_alignment_control tx_stack_alignment_schedule -j 4
ctest --test-dir ../evidence/build/implementation-host -R thread_stack_alignment_native64 -V
```

Preserved intermediate failures are explained rather than discarded: the first harness
link failed because the plan assumed TX_THREAD_INIT still defines globals in the header;
this base declares them extern. The harness now supplies the required state. An initial
fixed scheduling run failed an invalid expectation that highest usage remains identical
to the initial stack pointer after resume. Creating suspended threads and checking before
real resume corrected that timing assumption, and the final test was rerun unchanged on
the original sources. A first parent configure used a relative toolchain path that CMake
could not locate; the corrected absolute path configured successfully. During one build,
shell tools stalled temporarily; no source edit occurred until that baseline completed.

Visible native64 baseline warnings are the existing three narrowing casts in tx_misra.c
and unused timeout_input in Linux x86_64 tx_thread_timeout.c. They appear on original and
fixed kernel builds. No warnings arise from the changed create service or the new tests.

## Remaining verification and questions

The deterministic driver still owns the complete freeze and native verification. Its
required command can target the standalone directory with gcc-14 in its provisioned
`/evidence/build/focused` environment; that directory was left unused locally.
Independent review, human provenance review, formal MISRA deviation acceptance, release
metadata decisions, and final remote checks remain pending. The release label was not
invented for this implementation.

Full native32 kernel/SMP/FreeRTOS regression runs and coverage gates are unavailable
locally without multilib; the reference GCC 14 lane is unavailable here. RISC-V, AArch64,
Windows, FVP, and real embedded execution were not performed. M4 compile success does
not establish reference Arm-toolchain qualification or hardware behavior. Original
invalid-pointer byte arithmetic is executed inside the buggy service during the safe
negative metadata test; this is not a sanitizer-clean baseline claim.

A companion documentation contribution, coordination/ECA/final-head checks, and code
owner/maintainer approval are contribution-stage obligations from the plan, outside this
local implementation scope. None is claimed complete. No author is claimed to have
personally reviewed this output.
