# ThreadX and AutoSD feasibility

**Current implementation:** [ThreadX zonal lighting](../demo/X-Verse/external_hackathon_ecus/ThreadX/README.md) now
implements brake/reverse control over SocketCAN and Zenoh2CAN on Linux. The
sensor/liveness role below is the original proposal. [AutoSD](../AutoSD/README.md)
now hosts this workload in a real QEMU/KVM guest with a separate native OpenSOVD
lighting App and an optional actual openDuT Ethernet/GRE path. The existing
S-CORE dashboard/DFM campaign admission remains separate work.

Component development is organized under [ThreadX](../demo/X-Verse/external_hackathon_ecus/ThreadX/README.md) and
[AutoSD](../AutoSD/README.md), with separate proposals and artifact status.
This document retains the shared feasibility research.

Prepared 4 October 2026 after the user asked whether ThreadX and AutoSD could be
integrated for hackathon points and clarified that “OpenSD” meant AutoSD.
The research below records the original proposed extension; current implementation
and evidence are linked above. No awarded bonus is established here.
The earlier brief's exclusion of new technologies solely for bonuses does not
override the user's newer request to evaluate these two technologies.

## Verified scoring rule

The [official evaluation forms](https://github.com/Eclipse-SDV-Hackathon-Chapter-Four/.github/blob/main/profile/Eclipse_SDV_Hackathon_2026_EvaluationForms.pdf)
list meaningful ThreadX use and meaningful AutoSD use at +0.10 each, in addition
to openDuT and Java/Jakarta EE. The combined bonus is capped at +0.40 and the final
score at 5.00. Code, configuration, deployment, integration, testing, a demo or a
reproducible setup must substantiate use. A technology name or logo alone cannot.
Thus these two additions could contribute +0.20; with the existing meaningful
openDuT integration, the potential technology bonus would be +0.30. These are
eligibility targets; judging and prepared-work eligibility are not established here.

## Proposed useful integration

| Addition | First bounded role | Demonstration and acceptance |
| --- | --- | --- |
| ThreadX | A small sensor/liveness test application using actual ThreadX threads, timers and queues; develop with the supported Linux simulation port before selecting hardware. | Run the actual RTOS component, capture its identity and sequence/timing observations, inject a controlled communication interruption through the managed testbench, observe an explicitly named component fault through OpenSOVD, recover, and inspect the result in Test Manager. Label Linux simulation clearly; never imply embedded hardware or certified deployment. |
| AutoSD | A separately booted AutoSD development VM serving as an additional application/test target for the integration. Prefer deploying the ThreadX simulation target and its diagnostic adapter together in this VM for the first slice. | Record the actual guest OS/image identity, run the integration workload inside the guest, attach a suitable guest interface to the openDuT-managed path, demonstrate nominal traffic, interruption and recovery, and reproduce from a pinned image/manifest. An Ubuntu container named AutoSD or a VM that only boots does not demonstrate this integration. |

The combined demonstration would be: actual ThreadX component on an AutoSD guest
→ openDuT-managed test connection → named diagnostic observation and fault history
through OpenSOVD → dashboard and deterministic campaign artifacts. This is an
additional test target; its observations must not impersonate the existing S-CORE
Cruise Control receiver. The current physical CARLA/S-CORE campaign remains the
reference demonstration. Do not move CARLA, rewrite its bridge, or replace the
verified controller solely to admit these extensions.

The [ThreadX hardware-support documentation](https://threadx.io/releases/6.5.1/home/main/hardware-support.html)
lists a GNU Linux simulation port for development and testing. That makes a host
prototype feasible without selecting an unavailable MCU. A hardware transition
requires a supported board, its actual port and fresh evidence; a simulator run
is not evidence of MCU timing or safety certification.

The [AutoSD Linux getting-started guide](https://docs.centos.org/automotive-sig-documentation/getting-started/getting-started-on-linux/)
describes development images and QEMU VMs. The [current image-build documentation](https://sigs.centos.org/automotive/latest/building/)
also describes declarative manifests and bootc images. Select one compatible
image/tool workflow and pin it; do not mix instructions or assume this host has
the builder, virtualization support or sufficient disk space.

## Admission and verification

1. Finish the current reproducible physical slice and retain a labelled saved replay.
2. Complete F010 planning before dashboard implementation. Its target/capability model
   should allow additional components without suggesting they are already deployed.
3. Admit a separate ThreadX Spec Kit feature: minimal useful application, bounded
   I/O, explicit simulation identity, actual service-loss/recovery evidence, cleanup
   and preserved existing control assertions. Pin source, licenses and build tools.
4. Admit a separate AutoSD Spec Kit feature after an environment preflight: image
   availability/digest, guest resources, virtualization, compatible userspace and
   the actual openDuT interface attachment. Validate networking and workload inside
   the guest before claiming platform integration.
5. Repeat the existing core/physical preservation checks after extension changes.
   Keep independent person reproduction, upstream approval and event eligibility
   separately pending until their own evidence exists.

No new middleware, public deployment or AAOS/FOTA work is required by this proposal.
The adapter's observation/fault contract, guest networking and dashboard run control
belong in the subsequent plans. Until executed and verified, both technology
integrations remain proposed and contribute no claimed bonus.
