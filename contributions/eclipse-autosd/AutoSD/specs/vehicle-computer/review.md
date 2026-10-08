# F012 convergence review

Prepared 4 October 2026. ASD001–012 map to the [retained artifact packet](../../artifacts/README.md).
The final fresh-overlay/new-native-target run passes 13 local CARLA/diagnostic
checks, 16 managed checks, four CAN-contract checks, three optional timeout
checks, actual GRE capture, reboot and complete owned cleanup. Source, image,
container, binary and artifact hashes identify the measured implementation.

The bridge and vehicle controller/subscriber sources were reused unchanged.
The existing Cruise Control runtime was not started or modified. The openDuT
helper now derives management addresses from its configured subnet; its default
172.30.77.0/24 retains the previous addresses. A separate 172.30.78.0/24 bench
was exercised and removed, preserving an unrelated existing network. Existing
contribution artifacts still pass their retained-hash verifier; the older native
Cruise Control campaigns were not rerun for this slice.

Process boundaries are preserved: ThreadX control does not wait for HTTP reads.
Observations use real ThreadX records and the guest boot/monotonic clock. Missing
or expired data remains unavailable. The fault journal is bounded/persistent and
explicitly distinguished from native DFM; this is the first lighting-specific
adapter, without reusing the Cruise Control schema. SELinux stays enforcing.

Specification/plan/task records were consolidated alongside prototype work;
they did not precede the first prototype in the constitution's prescribed order.
The user explicitly authorized this reversible implementation. Final requirement
coverage, runtime convergence and reproduction evidence are recorded here.

Shared dashboard/Test Manager admission, native DFM lighting faults, physical
CAN hardware, embedded ThreadX timing, human signoff, production qualification,
upstream review and judging remain outside this measured slice. No outreach or
upstream publication was performed. Private credentials and runtime payloads
remain ignored; preparation classification is retained.
