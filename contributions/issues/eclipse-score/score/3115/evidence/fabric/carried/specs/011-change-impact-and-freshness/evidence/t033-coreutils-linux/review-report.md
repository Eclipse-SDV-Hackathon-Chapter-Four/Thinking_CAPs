# US39 offline Linux Coreutils review report

The exact Linux Coreutils 0.1.0 archive was acquired and verified against the checksum
bound to the original native registry/module/wrapper. A separate native repository
query passes, completing the repository marker and verifying the extracted executable
hash/mode. Configured Linux analysis remains failed at the unlisted GCC 12.2.0 package.
Engineering acceptance and broader native/live qualification remain pending offline.

The acquired archive is **4,819,217 bytes**, SHA-256
`463648347b1fc337414a864bda960c9cbd1bd4a540f344c010ff5bb35199e6d7`.
[Actual HTTP receipt](payload-provenance.json) binds the exact requested URL, allowed
redirect origins, 200 status, Content-Length, completed bytes and native expected hash.
The release API provides **no asset digest**; that field stays null, and is not invented
from the downloaded bytes. [Acquisition plan](acquisition-plan.json) retains release
metadata, native source bindings, upstream tag commit
`18b963ed6f612ac30ebca92426280cf4c1451f6a` and Git-blob/SHA-256-verified source license.
[Archive inventory](archive-inventory.json) records **four** entries and **13,102,983**
expanded bytes, including **one** retained actual license and the executable. Source
license and actual payload license remain distinct records; no licensing/tool
qualification or independent upstream binary-build reproduction is accepted.

Together with the 31 inherited exact inputs, the set is **32 files / 394,036,927 bytes**.
[Input manifest](public-module-manifest.json) retains exact source URLs, hashes, sizes
and paths in the fresh bound SSD workspace. Large payloads remain there rather than
being duplicated in the repository. Packet files retain inventories, actual license,
source/HTTP provenance, operators, complete native outputs and report records.
[Stage limits](stage-limits.json) permit one new payload request, 64 MiB/new payload,
256 MiB/inherited input, 512 MiB aggregate, 32 files, 120 seconds/request, sixteen
2 MiB metadata responses, 512 MiB expanded new archive data, 10,000 members, 16 MiB
per notice/32 MiB notices per archive and a 20 GiB free reserve. At most three
120-second native probes are permitted, with no unchanged configured retries after
an out-of-scope failure. No request or acquisition retry occurs.

The new workspace selects the registered mounted **1 TiB ext4 image** on the external
SSD (underlying exfat); its device/UUID binding is measured and checked throughout.
Historical source/cache/runtime inputs remain read-only and independently hash-bound.
Old workspace/storage records, active queues, global tool storage and credentials are
unchanged. The 740-file original native source copy has no Git directory/hooks;
retained hook/configuration bytes are verified before probing. Bazel remains 8.7.0,
and the mirror uses the retained Python 3.12.14 runtime read-only. The host Python 3.10
is not used for fabric/native helpers. [Workspace](workspace.json),
[volume bindings](historical-input-volume-bindings.json) and
[runtime binding](current-runtime-binding.json) supply exact provenance.

One real isolated configured five-label `cquery` exits **1** in **12.252 seconds**:
[complete analysis record](native-probes/linux-pinned-coreutils-analysis.json).
All **68** metadata responses and **28** asset writes complete, with no metadata misses.
The mirror serves **400,435,242 bytes** across those responses. The archive allowlist
is preserved per probe; real home is hidden and external networking denied. QNX,
unlisted downloads and credentials remain denied. The native score_tooling version
warning remains visible/enabled and the native log reports zero action processes.

The configured failure reaches GCC before completing the Coreutils repository; no
Coreutils asset response occurs in this first probe. A changed failure ordering does
not establish new-payload extraction. Therefore one distinct, unconfigured query of
`@@aspect_bazel_lib++toolchains+coreutils_linux_amd64//:coreutils_toolchain` verifies
only the already admitted Coreutils repository:
[complete repository-query record](native-probes/linux-coreutils-repository-query.json).
It exits **0** in **2.221 seconds**, consumes the verified content-addressed archive
without any mirror requests, and produces a completed marker. Native executable
hash and mode match the archive in [materialization evidence](materialized-dependencies.json).
This separate query stays within the finite stage bound and adds no input; no further
configured retry follows the GCC boundary. Materialization is not Coreutils execution,
native compilation/test, full configured-analysis success or engineering acceptance.

The next observed missing native input is the Linux GCC package:

- URL: `https://github.com/eclipse-score/toolchains_gcc_packages/releases/download/v0.0.4/x86_64-unknown-linux-gnu_gcc12.tar.gz`
- Original lock extension: `@@score_bazel_cpp_toolchains+//extensions:gcc.bzl%gcc`
- Generated package repository: `score_gcc_x86_64_toolchain_pkg`
- Native compiler identifier/version: `gcc_12.2.0` / `12.2.0`
- SHA-256: `e9b9a7a63a5f8271b76d6e2057906b95c7a244e4931a8e10edeaa241e9f7c11e`
- Release-reported bytes: **157,834,687**, with a reported digest matching the lock.

[GCC readiness](gcc-readiness.json) binds exact original-lock attributes, native registry
source hash, verified score_bazel_cpp_toolchains 1.0.4 module archive, selected wrapper/
BUILD source and preserved wrapper license. The exact payload is absent from the
inspected historical cache; this is not a machine-wide absence claim. Release-reported
size is metadata, not acquired bytes. Payload notices/expanded size/execution and tool
qualification remain unmeasured/unaccepted. The source's inherited QNX license-path
field is metadata only; no QNX SDK, credentials or license file is accessed.

Including GCC would create **33 inputs / 551,871,614 reported bytes**, exceeding both
32-input and 512 MiB aggregate limits, as well as this stage's 64 MiB new-payload limit.
The readiness draft is not admission. No GCC payload is acquired/imported, no substitute
compiler is selected, no original source/lock/checksum changes, and no scope is widened.
A successor stage must declare measured new limits and actual payload provenance.

Fresh frozen sync, pinned Specify 1.0.12 version/prerequisites, foundation, package build,
final control whitespace and trace audit pass. Existing **223 scoped tests**, Ruff and
mypy over **152 source files** are carried by **310 unchanged source/test subjects**;
no new source tests or static analysis are run merely to restate unchanged validation.
All **24** historical packets (**5,825** file subjects), **20** T032 subjects, **740**
original native files, **3,484** retained runtime files and **405** historical cache
markers are verified unchanged. [Validation](validation-results.json),
[preservation](preservation-current.json) and [process closure](process-verification.json)
are separate records. Every owned probe/mirror exits; no private/provider server or
background continuation starts. No extension hooks are registered.

Recorded 011 tasks are **136/138** complete, with T032/T033 human markers preserved.
This is not a whole-mission completion measure. Full native expected-check denominator,
transitive impact/work products, reviewer authority, payload/tool qualification and live
B1–B5/T033 qualification remain pending. QNX is skipped because the owner has no license,
without accepting applicability or platform qualification. PR publication stays deferred.
No SDK, native compilation/test, paid request, commit, push or human decision follows.

Next concrete action: prepare the exact original-lock-bound Linux GCC 12.2.0 package
from release v0.0.4 with actual notices/expanded size and explicit new input-count/byte/
storage limits, then pursue configured Linux analysis in a fresh bounded stage. Preserve
all sealed packets and unused attempts; human engineering review remains offline.
