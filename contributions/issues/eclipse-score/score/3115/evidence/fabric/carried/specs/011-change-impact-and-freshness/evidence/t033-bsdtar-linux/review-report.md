# US42 offline Linux BSD tar review report

The exact native-source-bound Linux BSD tar v3.8.1-fix.1 binary was acquired and
verified against original native SHA-256. Its independent repository query passes;
configured Linux analysis fails at the unlisted pinned zstd binary. Engineering
acceptance and broader native/live qualification remain pending offline.

[Recovery verification](recovery-preparation.json) records the server interruption after
preparation. Completed source/cache/runtime preparation was hash-verified and reused,
without repeated acquisition or native probing. The fresh workspace remains on the
same registered mounted writable 1 TiB SSD image; no active work was relocated.

[HTTP receipt](payload-provenance.json) binds **one completed 1,774,384-byte request**,
exact requested URL, allowed redirect origins, no retry and native/acquired SHA-256
`fff8f72758a52e60fe82beae64b18e7996467013ffe8bec09173d1ba6b66e490`. Release-reported digest/size match original native authority.
[Acquisition plan](acquisition-plan.json) and [operator binding](acquisition-operator-before.json)
retain hashes recorded before acquisition, including original source/lock/readiness,
finite limits and operators. The copied [BSD tar readiness](bsdtar-readiness.json) is the
unchanged inherited US41 pre-acquisition snapshot; current measured facts reside in
[results](bsdtar-results.json) and this report. Native historical aspect-build URL and
canonical hermeticbuild URL stay separate; no source/lock/checksum substitution occurs.

[Source provenance](provenance-results.json) binds builder commit
`2215f4da9b1beeb288f9e46777a07a4c1513c894`, builder LICENSE, workflows, MODULE/BUILD/Bazel settings,
exact libarchive patch and libarchive v3.8.1 source COPYING at tag commit
`9525f90ca4bd14c7b335e2f8c84a4607b0af6bdf`, by Git blob and SHA-256. The builder
MODULE pins libarchive 3.8.1 and applies its retained patch; the workflows describe the
Linux musl build. Those source declarations are not independently reproduced build
provenance, nor cryptographically verified release attestations. Builder, libarchive
and wrapper licenses remain distinct from actual binary findings. Complete linked-
component licensing, runtime compatibility and accepted tool qualification stay unknown.
Retained upstream Markdown bytes use text evidence filenames, preserving content
without treating upstream relative links as repository documentation. None is executed.

[Binary assessment](binary-assessment.json) records a **64-bit little-endian x86_64 ELF
executable**, machine 62, type 2, without PT_INTERP. This static structure does not prove
runtime compatibility. Two exact static notice-pattern fragments totaling **28 bytes**
are retained with byte offsets/hashes. The declared scan is bounded and does not claim
complete licensing/component coverage. This standalone binary has no archive inventory
or companion archive notice files. No payload execution occurs, including help/version/
license output, and source licenses never imply accepted licensing or qualification.

The complete set is **35 inputs / 555,965,422 bytes**, with 34 inherited hash-bound inputs
copied without remote reacquisition. [Manifest](public-module-manifest.json) binds exact
large bytes to SSD paths/hashes/sizes; the packet retains metadata/source/licenses,
static findings, complete native outputs, operators and measured records. [Stage limits](stage-limits.json)
are 35 inputs, 256 MiB/inherited input, 8 MiB/new binary/static read, 1 GiB aggregate/mirror
bytes, one 120-second payload request, sixteen 2 MiB metadata responses, 2 MiB static
notice excerpts and 20 GiB free reserve. Archive expansion/member allowance is zero.
All **sixteen public metadata requests** are used for admitted BSD tar provenance.
Native execution permits three 120-second probes; two distinct probes are used, with
no unchanged/out-of-scope configured retry or successor metadata request.

[Workspace](workspace.json), [volume bindings](historical-input-volume-bindings.json)
and [runtime binding](current-runtime-binding.json) preserve measured same-UUID storage.
Image UUID is `11c42dee-73a3-4c2b-ab42-a0440011d9e0`, current device 1819, backing SSD
UUID `002B-CE31` on exfat. Old device/storage records, queues/caches and global tool
storage stay unchanged; no resize, repair, reformat or credentials/private-state copy
occurs. Fresh original native source has 740 files and no Git hooks, at baseline
`7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`; source/locks remain unchanged. Bazel is
8.7.0 and the verified retained mirror runtime is Python 3.12.14. Namespace probes hide
real home, deny external networking and expose only fresh bound writable scratch. The
loopback mirror serves exact listed bytes; QNX/unlisted inputs remain denied.

The unconfigured query of
`@@tar.bzl++toolchains+bsd_tar_toolchains_linux_amd64//:bsdtar_toolchain`
exits **0 in 3.724 seconds**, with zero mirror requests and verified cache consumption.
[Query record](native-probes/linux-bsdtar-repository-query.json) and [materialization](materialized-dependencies.json)
bind completed marker/generated files and native tar executable hash/mode. This is
repository loading, without binary execution, compilation/test or qualification.

The original configured five-label Linux cquery exits **1 in 9.95 seconds**:
[complete analysis record](native-probes/linux-pinned-bsdtar-analysis.json). All **68
metadata responses** complete, with zero metadata misses. **31 asset responses are
attempted; 30 complete and one GCC response is interrupted by client disconnect**.
Completed response content totals **407,573,883 bytes**. The mirror's `served_bytes`
field is **565,408,570**, a reservation of response content sizes rather than a meter
of successfully delivered bytes. Actual bytes transferred for the interrupted response
remain **unknown**; its 157,834,687-byte declared content size is not complete delivery.
[The collector refusal](retained-refusals/incomplete-write-refusal.json) retains the
original all-completed predicate/operator. Correction counts actual completed and
interrupted writes separately without rerunning native analysis. The independent BSD
tar query stays complete. The native version warning remains enabled/visible; the log
reports zero action processes. No configured retry follows the out-of-scope zstd failure.

[Next prerequisite](zstd-readiness.json) binds the original-lock registry source,
verified aspect_bazel_lib 2.22.0 module archive and exact native wrapper/license:

- Native URL: `https://github.com/aspect-build/zstd-prebuilt/releases/download/v1.5.6-bcr1/zstd_linux_amd64`.
- Native repository: `@@aspect_bazel_lib++toolchains+zstd_linux_amd64`.
- Version/platform: **1.5.6-bcr1 / linux_amd64**.
- Native SHA-256 literal: `0F0BD1193509A598629D7FA745C4B0B6D5FA6719E0C94C01EF0F20E466D801A7`.
- Normalized digest: `0f0bd1193509a598629d7fa745c4b0b6d5fa6719e0c94c01ef0f20e466d801a7`.

The exact inspected historical SHA-256 cache key is absent;
this is not machine-wide absence. Public release size/digest/canonical owner metadata
is **unqueried**, as the finite sixteen-request budget is exhausted; null size and
combined byte total remain unknown, not zero. No zstd payload/license/compatibility is
acquired, imported, executed or accepted. Adding it would create **36 inputs**, outside
the 35-input allowlist; aggregate fit cannot be determined without size. A fresh stage
must first measure exact release/cache/source-license/size provenance and declare new
bounds before acquiring bytes. Do not substitute host zstd or change native source/locks.

Fresh frozen sync, pinned Specify 1.0.12 version/prerequisites, foundation, package build,
control whitespace and trace audit pass in [validation](validation-results.json).
Prior **223 tests**, Ruff and mypy over **152 source files** are carried by **310 unchanged
source/test hashes**; no new source tests/static analysis are run. [Preservation](preservation-current.json)
verifies **27 prior packets / 6,235 subjects**, twenty T032 subjects, 740 native originals,
3,484 runtime files and 405 cache markers unchanged. [Process closure](process-verification.json)
records owned probes reaped and mirrors closed, without a private/provider server or
background continuation. No extension hooks are registered; seven reviewer checklist
items and all human markers remain unchanged.

Tasks are **145/147** complete, preserving T032/T033 human markers without a whole-mission
percentage. Historical T032/lifecycle #704 decisions remain exact-subject-bound. Full
native expected-check scope, transitive impact/work products, reviewer authority, tool
qualification and live B1–B5/T033 acceptance remain pending offline. QNX stays skipped
because the owner has no license; native license-path attributes remain unread metadata.
PR publication remains deferred. No SDK, compiler/native build/test, paid request,
commit, push, publication or human decision follows.

Next action: Refresh exact native-bound Linux zstd v1.5.6-bcr1 release/cache/source-license/size provenance under a fresh metadata budget, then prepare the binary with explicit successor limits and retry configured Linux analysis; keep QNX skipped.
