# Contribution priorities for this repository

The complete [open-issue snapshot](artifacts/open-issues.md) contains 52 issues
from October 7, 2026. The selection below follows the integration in
[`demo/X-Verse/external_hackathon_ecus/ThreadX/CMakeLists.txt`](../../../../demo/X-Verse/external_hackathon_ecus/ThreadX/CMakeLists.txt) and
[`demo/X-Verse/external_hackathon_ecus/ThreadX/README.md`](../../../../demo/X-Verse/external_hackathon_ecus/ThreadX/README.md): a single-core Linux/GNU ThreadX
simulator, pinned to 6.5.1, driving a zonal lighting controller through threads,
a bounded queue, a timer and event flags, with SocketCAN and Zenoh integration.

| Issue | Why it makes sense | Dependency or scope constraint |
| --- | --- | --- |
| [#744](https://github.com/eclipse-threadx/threadx/issues/744) | The Linux x86_64 port has the pointer/`ULONG` width mismatch described by the issue. A focused stack-checking/MISRA regression improves the simulator configuration coverage. | First contribution. Work from current upstream `dev`; #741/#742 are already resolved. The flags must be enabled together to reproduce the defect; ordinary integration execution alone does not establish it. |
| [#792](https://github.com/eclipse-threadx/threadx/issues/792) | Linux simulator reliability is relevant to repeatable controller tests and host debugging. | Separate causal investigation involving ThreadX and NetX Duo; do not assume this application's behavior proves that issue. |
| [#685](https://github.com/eclipse-threadx/threadx/issues/685) | Accurate build and contribution instructions reduce friction for reproducing the host integration. | Reconcile the current guide and merged documentation before proposing another documentation change. |
| [#684](https://github.com/eclipse-threadx/threadx/issues/684) | Coverage accounting affects confidence in thread, queue and timer behavior. | Compare compiler/configuration-dependent denominators and existing coverage work before changing thresholds. |

Open issues #752, #756 and #757 overlap fixes already merged into upstream
`dev`; an open issue alone does not justify duplicating those patches. SMP,
hardware-specific and module-manager work needs a separate reproduction and
admission because this integration uses the Linux single-core kernel.

The workflow currently executes only #744. The other candidates are recorded in
[issue-queue.json](issue-queue.json), rather than started automatically. It does
not change this application's immutable ThreadX dependency pin.
