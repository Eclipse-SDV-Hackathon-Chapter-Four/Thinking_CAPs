# US40 offline Linux GCC review report

The exact original-lock-bound Linux GCC 12.2.0 package was acquired, hash-verified
and materialized by a separate native repository query. Configured Linux analysis
then failed at the unlisted Linux jq 1.7 binary. Engineering acceptance and broader
native/live qualification remain pending offline.

The archive contains **157,834,687 bytes**, SHA-256
`e9b9a7a63a5f8271b76d6e2057906b95c7a244e4931a8e10edeaa241e9f7c11e`.
[HTTP receipt](payload-provenance.json) records one completed request, exact native
hash, Content-Length and allowed redirect origins, with temporary signed queries
omitted. [Acquisition plan](acquisition-plan.json) was bound before acquisition to
original native lock/wrapper/readiness bytes and finite [limits](stage-limits.json).
Release v0.0.4 metadata reports the same digest and size. Its builder tag commit is
`563cde1915d9f0a6d44bc9caf8d9dd2e07fad813`; [source provenance](provenance-results.json)
and [Linux build configuration](builder-config-bindings.json) retain selected source
files by Git blob/SHA-256. None of these builder scripts were executed or reproduced.
The copied [GCC readiness](gcc-readiness.json) is the unchanged inherited pre-acquisition
US39 assessment; current acquisition/materialization facts are supplied by this report
and [results](gcc-results.json), rather than rewriting that source-bound snapshot.

[Archive inventory](archive-inventory.json) records **4,009 entries**, **413,630,217
expanded bytes**, and **76 retained actual notices / 1,063,180 bytes**.
Selected GCC/cc1/cc1plus executable hashes and modes are retained; source notices and
actual payload notices remain distinct. Preserved notices do not accept licensing or
tool qualification. No independent binary-build reproduction is claimed.

The complete set is **33 inputs / 551,871,614 bytes**, including 32 inherited hash-bound
inputs. [Manifest](public-module-manifest.json) points to exact bytes on the fresh SSD
workspace; large payloads remain there. The packet retains complete native outputs,
inventories/notices, metadata/HTTP/source receipts and archived operators. New bounds
are 33 inputs, 256 MiB/input/new payload, 1 GiB aggregate and mirror response bytes,
one 180-second payload request, sixteen 2 MiB metadata responses, 8 GiB expanded new
archive bytes, 100,000 members, 16 MiB/notice, 64 MiB/archive notices and 20 GiB free
reserve. Native execution permits at most three 120-second probes; two distinct probes
were used. No download retry or unchanged configured retry occurs.

[Workspace](workspace.json) binds the mounted registered **1 TiB ext4 build image** on
the external SSD. Its underlying filesystem is exfat. The current device binding is
1819, image UUID `11c42dee-73a3-4c2b-ab42-a0440011d9e0`, backing SSD UUID `002B-CE31`.
Historical inputs are independently bound read-only on the same volume with exact
hashes; old device records/queues/cache stay unchanged. No reformat, resize, repair,
global storage migration or credentials/private-state copy occurs. [Input volume
bindings](historical-input-volume-bindings.json) and [runtime binding](current-runtime-binding.json)
retain the measured checks. Native source is a fresh 740-file original copy without
Git hooks, at baseline `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`; native source and
locks stay unchanged. Bazel stays 8.7.0 and the verified mirror runtime stays Python
3.12.14. Namespace probes hide real home, deny external networking, and expose only
fresh bound writable scratch; exact listed inputs are served through loopback.

The first, unconfigured query of
`@@score_bazel_cpp_toolchains++gcc+score_gcc_x86_64_toolchain_pkg//:all_files`
exits **0** in **6.787 seconds**. Its **one completed mirror response** delivers the exact
157,834,687-byte GCC archive. [Complete query record](native-probes/linux-gcc-repository-query.json)
and [materialization evidence](materialized-dependencies.json) bind completed repository
marker, extracted regular-file hashes, symlink targets and selected executable hashes/modes.
This is native repository loading, with no compiler execution or native build/test.

The original configured five-label Linux `cquery` then exits **1** in **9.496 seconds**.
[Complete analysis record](native-probes/linux-pinned-gcc-analysis.json) retains all
**68 metadata and 28 asset response writes**, all completed with zero metadata misses,
serving **400,435,242 bytes**. The previously loaded GCC repository remains complete;
no second GCC mirror transfer occurs. The native score_tooling version warning stays
visible/enabled and the log reports zero action processes. The next unlisted dependency
stops analysis, with no further configured attempt or new input admission.

The next exact prerequisite is [Linux jq 1.7](jq-readiness.json):

- Native requested URL: `https://github.com/stedolan/jq/releases/download/jq-1.7/jq-linux-amd64`.
- Native repository: `@@aspect_bazel_lib++toolchains+jq_linux_amd64`.
- Native integrity: `sha384-4wJ15NoxFf7r1Zf5YVGUeMPx/pfWlSfMJWLFcu4fUcBFe5L4BOpF/njEK8AH58od`.
- Release-reported size: **2,319,424 bytes**; reported asset digest: **None**.

The checksum is **SHA-384**, explicitly preserved without inventing a native SHA-256.
Original-lock registry source, verified aspect_bazel_lib 2.22.0 module archive and exact
native wrapper bind the version/platform/URL/integrity. Public release metadata records
its canonical jqlang asset URL separately from the native historical stedolan URL.
The exact inspected SHA-384 cache path is absent;
SHA-256 cache keys were not assessed without an exact key, and this is not machine-wide
absence. Actual jq payload/license/tool compatibility remain unmeasured/unaccepted.
It was not downloaded, imported or executed. Adding jq creates **34 inputs /
554,191,038 reported bytes**, exceeding this stage's 33-input
allowlist even though its aggregate byte ceiling is larger. No host-tool substitution,
source/lock change or input-scope widening occurs.

The first foundation check found three report links to not-yet-written final records.
[The failure](retained-refusals/foundation-before-final-records.json) and complete log
are retained. Finalization writes measured preservation/process records and an explicit
pending validation record before the final foundation check; no native probe repeats.

Fresh frozen sync, pinned Specify 1.0.12 version/prerequisites, foundation, package build,
control whitespace and trace audit pass as recorded in [validation](validation-results.json).
The prior **223 scoped tests**, Ruff and mypy over **152 source files** are carried by
**310 unchanged source/test hashes**; no new source tests/static analysis were run.
All **25 historical packets / 5,922 file subjects**, **20 T032 subjects**, **740 original
native files**, **3,484 retained runtime files** and **405 historical cache markers**
remain unchanged in [preservation](preservation-current.json). [Process closure](process-verification.json)
records owned tools reaped and mirrors closed, without a private/provider server or
background continuation. No extension hooks are registered.

Recorded tasks are **139/141** complete, with T032/T033 human markers preserved; this
is not a whole-mission percentage. The historical T032/lifecycle #704 decisions remain
bound to their exact subjects. Full native expected-check scope, transitive impact/work
products, role authority, tool qualification and live B1–B5/T033 acceptance remain pending.
QNX stays skipped because the owner has no license. The inherited native QNX license-path
attribute is source metadata only: no license file, SDK or credentials are accessed.
No native compilation/test, paid request, publication, commit, push or human decision follows.

Next action: Prepare the exact source-bound Linux jq 1.7 binary with native SHA-384 integrity, actual payload/license provenance and explicit successor input bounds, then retry configured Linux analysis; keep QNX skipped.
