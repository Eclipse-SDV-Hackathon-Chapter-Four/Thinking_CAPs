# ThreadX #744 production fix and regression design

Reviewed the loop4 checkout's `common/src/tx_thread_create.c`, `common/inc/tx_api.h`, `common/src/tx_misra.c`, Linux/GNU port, and existing thread-transition/module-manager standalone test patterns. This document is design evidence; it does not claim a passing implementation.

## Production change

Use the two casts proposed in issue #744:

```c
    new_stack_start =  (ALIGN_TYPE) ((VOID *) stack_start);
    ...
    stack_start =  (VOID *) ((ALIGN_TYPE) updated_stack_start);
```

Remove the surrounding `TX_MISRA_ENABLE` branches. Preserve the existing alignment and size adjustment logic. Only `common/src/tx_thread_create.c` needs a production edit. Current `common_smp/src/tx_thread_create.c` already uses these casts, and issue #744 explicitly accepts this form, following the simulator fix from #742. This avoids changing the width or semantics of existing `ULONG` conversion helpers used elsewhere.

The apparently simpler change to call `TX_POINTER_TO_ALIGN_TYPE_CONVERT` and `TX_ALIGN_TYPE_TO_POINTER_CONVERT` in both configurations does **not** compile: those macros exist only in the non-MISRA branch of `tx_api.h`. Adding two new MISRA helpers would also work but expands the patch into header/shim API changes and raises SMP parity and assembly-shim obligations. It is unnecessary for this narrowly scoped correction.

Existing file attribution already includes the required AI assistance line. New files need the exact new-file copyright, license, and AI disclosure prescribed by upstream CONTRIBUTING.md; do not claim that human review has happened before it does.

## Native-width regression

Add a dedicated standalone CMake test directory, for example `test/tx/cmake/thread_create_stack`, with sources under `test/tx/thread_create_stack`. Configure this directory directly. The ordinary `test/tx/cmake` project forces `-m32`, which removes the critical condition `sizeof(ALIGN_TYPE) > sizeof(ULONG)` on the Linux simulator. Adding the two feature flags to that project alone would not reproduce #744.

Use C99 and CMake/CTest already present upstream. Gate the test on Linux/GNU with 64-bit pointers and the genuine port types. At runtime print and assert:

```text
sizeof(ULONG)=4 sizeof(ALIGN_TYPE)=8 sizeof(void*)=8
```

A missing width mismatch must produce an explicit skip or configuration error, never an apparent proof that the reported defect was tested. The regression CI job must execute an x86_64 native build.

Compile the actual `common/src/tx_thread_create.c` with `TX_MISRA_ENABLE` and `TX_ENABLE_STACK_CHECKING`. Compile and link the real `common/src/tx_misra.c` so the negative baseline reaches the genuine truncating helpers. Use function/data sections and linker garbage collection for unused shim services, or link the full ThreadX library as an alternative. Do not replace the pointer conversions with test reimplementations: a copied helper can pass while upstream behavior is wrong.

An isolated harness should provide only port/scheduler boundary stubs:

- `_tx_thread_stack_build`: record the metadata passed by the real create service and supply a safe fake stack pointer; do not dereference the potentially truncated stack address.
- `_tx_thread_interrupt_disable` and `_tx_thread_interrupt_restore`: record/balance posture.
- `_tx_thread_system_preempt_check`, `_tx_thread_system_resume`, `_tx_thread_shell_entry`, and `_tx_thread_timeout`: recorders or unreachable boundary stubs matching upstream prototypes.

This matches the existing `thread_transition` and `module_manager` technique. `tx_misra.c` defines `TX_THREAD_INIT`, so avoid defining the same thread globals in the harness. Supply any remaining required symbols identified by the linker. Keep tracing disabled for this narrow test. The real shim already contains unrelated 64-bit casts; capture diagnostics and do not silently make an unbuildable global `-Werror` demand part of the patch.

Call `_tx_thread_create` with `TX_DONT_START` to isolate stack preparation, while exercising its real fill, alignment, metadata, created-list, and successful-return path. A full Linux scheduler test can supplement this; it has more setup, host thread cleanup, and failure-by-segfault behavior and is not necessary to demonstrate this pointer defect precisely.

## Assertions and test matrix

Allocate real host memory with padding and derive a naturally aligned address using integer remainder arithmetic. Assert that it has nonzero bits above the `ULONG` range. On 64-bit Linux ordinary heap/stack allocations meet this condition; do not use fabricated pointers or dereference memory mapped at a guessed address. If the actual allocation is low, report the test precondition failure explicitly.

Run offsets `0 .. sizeof(ULONG)-1`, covering aligned and every misaligned input, plus sizes both divisible and not divisible by `sizeof(ULONG)`. Fill padding with sentinel bytes before each call. Expectations are based on caller-visible requirements:

- Return status is `TX_SUCCESS` and the thread remains suspended.
- Recorded and stored stack start is the first ULONG-aligned byte at or after the supplied start; full high address bits are retained.
- Effective size is rounded down to ULONG units, then reserves one ULONG, with an additional ULONG reserved for an adjusted start.
- Stored end equals expected start plus effective size minus one and remains within the supplied allocation.
- Stack-highest pointer equals the stack pointer supplied by the port boundary recorder.
- The original supplied stack region is filled with the expected pattern; sentinel bytes before/after that region remain untouched.
- Created-list count and links are valid, and interrupt/preemption posture balances.

Compute expected start using remainder plus byte offset rather than copying the production bit mask. Compare pointer equality, or cast to the port's `ALIGN_TYPE` for integer range comparisons; do not perform relational comparisons between pointers to unrelated/invalid objects. Reset only harness-owned state between cases, keeping created-list lifetime valid.

Build a native non-MISRA + stack-checking control target too. Optionally build a real 32-bit target if multilib is available; label it compatibility coverage and preserve the required 64-bit lane. Do not invent a custom 32-bit `ULONG` type when the upstream Linux port already supplies it.

## Demonstrating old failure and corrected success

Run the exact new regression against the pinned upstream parent revision before the production edit. Save configure/build output and CTest exit/result evidence. The old source should return a failure through metadata assertions rather than dereferencing an invalid pointer and crashing. All offsets whose supplied stack has high bits should expose truncation.

Apply only the two-cast production change and rerun the same test without changing expectations or stubs. Preserve successful logs, compiler/version, source commit, feature macros, width diagnostics, and exit codes. Keep the negative source checkout and build directories on loop4; store the evidence manifest and concise logs in this contribution folder.

Then run the relevant existing standard regression configurations, including the newly available MISRA configurations, and all applicable upstream checks. Inspect CI triggers: the new native regression must actually be reached by GitHub Actions, either as a focused separate lane in the existing regression workflow or a directly called standalone job. Document any baseline failures with the pinned revision and matching untouched-source results. A ready-to-merge statement additionally requires actual remote PR checks and maintainers/Eclipse status; local tests cannot replace them.
