# US41 offline Linux jq review report

The exact native-source-bound Linux jq 1.7 binary was acquired and verified against
original native **SHA-384 integrity**. Its independent native repository query passes;
configured Linux analysis then stops at the unlisted pinned BSD tar binary. Engineering
acceptance and broader native/live qualification remain pending offline.

[HTTP receipt](payload-provenance.json) records **one completed 2,319,424-byte request**,
allowed redirect origins, exact bytes and no retries. Native SHA-384 is
`e30275e4da3115feebd597f961519478c3f1fe97d69527cc2562c572ee1f51c0457b92f804ea45fe78c42bc007e7ca1d`.
The separately measured SHA-256 is
`2f312b9587b1c1eddf3a53f9a0b7d276b9b7b94576c85bda22808ca950569716`,
which matches the release checksum-list entry. Release asset digest remains **null**;
that field is not filled from the checksum list or acquired bytes. [Acquisition plan](acquisition-plan.json)
and [operator binding](acquisition-operator-before.json) preserve pre-download native
readiness/source-lock/limit/operator hashes. The copied [jq readiness](jq-readiness.json)
is the unchanged inherited US40 pre-acquisition snapshot; this report and [results](jq-results.json)
supply current measured facts without rewriting that source-bound snapshot.

[Source provenance](provenance-results.json) binds jq release tag commit
`11c528d04d76c9b9553781aa76b073e4f40da008`. jq's actual source COPYING and the Oniguruma submodule
COPYING are separately Git-blob/SHA-256-bound; the Oniguruma gitlink commit remains
`d2f1a14ced5d5d461acac0da0d477ab240a7ab5f`. Native wrapper/module license bytes are
separate from these licenses and from actual binary findings. No builder execution,
independent binary-build reproduction or complete linked-component licensing is inferred.

[Static binary assessment](binary-assessment.json) identifies a **64-bit little-endian
x86_64 ELF executable**, machine 62, type 2, with **no PT_INTERP header**. This static
structure does not prove runtime compatibility. It is a standalone binary, with no
archive entries or companion archive license files to inventory. A bounded scan of
ASCII printable sequences found **zero strings matching declared notice patterns**;
this is not a claim that licensing obligations are absent. Complete component licensing,
execution compatibility and accepted tool qualification remain unassessed. jq was never
executed, including for version/license output. The original source licenses stay intact.

Together with 33 inherited exact inputs, the set is **34 inputs / 554,191,038 bytes**.
[Input manifest](public-module-manifest.json) binds source URLs, sizes and measured
SHA-256 paths on the fresh SSD. jq additionally retains original native integrity and
SHA-384. Large inputs stay on the bound workspace; packet files retain provenance,
source licenses, binary findings, complete native outputs, operators and measured records.
[Limits](stage-limits.json) are 34 inputs, 256 MiB/inherited input, 8 MiB/new binary and
static read, 1 GiB aggregate/mirror bytes, one 120-second payload request, sixteen 2 MiB
metadata responses, 2 MiB static notice excerpts and 20 GiB free reserve. No archive
expansion/members are admitted. At most three 120-second native probes are permitted;
two distinct probes were used with no configured retry after the out-of-scope failure.

[Workspace](workspace.json) uses the mounted registered **1 TiB ext4 SSD build image**,
current device 1819, image UUID `11c42dee-73a3-4c2b-ab42-a0440011d9e0`, backing SSD UUID
`002B-CE31` on exfat. Historical inputs are independently verified read-only on the same
volume; old storage/device records, queues and caches remain unchanged. No resize,
repair, reformat, global storage migration or private-state copy occurs. [Volume bindings](historical-input-volume-bindings.json)
and [runtime binding](current-runtime-binding.json) retain measured checks. The fresh
740-file native source copy has no Git hooks; original source baseline
`7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`, source/locks, Bazel 8.7.0 and verified
Python 3.12.14 mirror runtime remain unchanged. Namespace probes hide real home, deny
external networking and expose only fresh bound writable scratch. The loopback mirror
serves exact listed inputs; native warnings remain enabled and preserved.

The independent unconfigured query of
`@@aspect_bazel_lib++toolchains+jq_linux_amd64//:jq_toolchain` exits **0 in 3.723 seconds**.
[Complete query record](native-probes/linux-jq-repository-query.json) has **zero mirror
requests**: the prepared verified content-addressed cache supplies the bytes. [Materialization](materialized-dependencies.json)
binds the completed repository marker, generated files and jq's actual executable hash,
mode and native SHA-384. Successful loading does not establish payload execution,
qualified tool readiness, native compilation/test or engineering acceptance.

The original configured five-label Linux cquery then exits **1 in 10.401 seconds**.
[Complete analysis record](native-probes/linux-pinned-jq-analysis.json) retains all
**68 metadata and 28 asset writes**, completed with zero metadata misses, serving
**400,435,242 bytes**. The native score_tooling version warning remains visible/enabled,
and the log reports zero action processes. It stops at the next unlisted dependency,
without another configured attempt or input-scope widening.

[The next prerequisite](bsdtar-readiness.json) is the exact Linux BSD tar binary:

- Native URL: `https://github.com/aspect-build/bsdtar-prebuilt/releases/download/v3.8.1-fix.1/tar_linux_amd64`.
- Native repository: `@@tar.bzl++toolchains+bsd_tar_toolchains_linux_amd64`.
- Wrapper module: **tar.bzl 0.7.0**; version/platform: **3.8.1-fix.1 / linux_amd64**.
- Native SHA-256: `fff8f72758a52e60fe82beae64b18e7996467013ffe8bec09173d1ba6b66e490`.
- Release-reported size: **1,774,384 bytes**, with a matching reported digest.
- Canonical asset URL: `https://github.com/hermeticbuild/bsdtar-prebuilt/releases/download/v3.8.1-fix.1/tar_linux_amd64`.

Original-lock registry source, verified module archive, wrapper versions/platforms/
toolchain/extensions and native license bytes are retained by exact hashes. The initial
collector refused equality between the historical native URL and the release's migrated
canonical URL. [That refusal](retained-refusals/canonical-url-refusal.json) retains the
original operator and exact metadata; correction preserves both URLs separately and
reuses the hash-bound metadata without refetching or repeating a native probe. Native
source/checksum authority remains unchanged; the reported digest still matches.
The exact inspected historical SHA-256 cache key is absent, with no machine-wide
absence claim. BSD tar bytes/notices/compatibility were not acquired, imported or
executed. Adding it would produce **35 inputs / 555,965,422
reported bytes**, exceeding the 34-input allowlist. Actual payload/source-license/tool
qualification remains unaccepted; a successor needs separate finite measured bounds.

The reporting process check initially matched its own ancestor shell's script text
as a native process. [That refusal](retained-refusals/process-match-refusal.json) and
original operator are retained; matching now requires the native executable name and
workspace-specific argv. No native probe repeats. The first foundation check also
found a relative link in the retained upstream README to an uncaptured CI file.
[The failure and resolution](retained-refusals/source-link-resolution.json) retain the
complete check/log. The exact tag/Git-blob-bound [linked build source](readme-linked-build-source.json)
is captured without modifying README or acquisition-plan bytes, and is never executed.
Final foundation checks run after the full report/measurement records exist.

Fresh frozen sync, pinned Specify 1.0.12 version/prerequisites, foundation, package build,
control whitespace and trace audit pass in [validation](validation-results.json).
Prior **223 scoped tests**, Ruff and mypy over **152 source files** are carried by
**310 unchanged source/test hashes**; no new source tests/static analysis were run.
All **26 historical packets / 6,115 subjects**, **20 T032 subjects**, **740 original
native files**, **3,484 runtime files** and **405 cache markers** remain unchanged in
[preservation](preservation-current.json). [Process closure](process-verification.json)
records all owned probes reaped/mirrors closed; no private/provider server or background
continuation starts. No extension hooks are registered. Reviewer checklist markers remain
unchanged with seven pending items; no human judgment is synthesized.

Recorded tasks are **142/144** complete, with T032/T033 human markers preserved and no
whole-mission percentage. Historical T032/lifecycle #704 decisions remain bound to
exact subjects. Full native expected-check scope, transitive impact/work products,
reviewer authority, tool qualification and live B1–B5/T033 acceptance remain pending.
QNX stays skipped because the owner has no license; inherited native license-path
attributes remain unread source metadata. PR publication remains deferred. No SDK,
compiler/native build/test, paid request, commit, push or human decision follows.

Next action: Prepare the exact source-bound Linux BSD tar v3.8.1-fix.1 binary with native SHA-256, actual payload/source-license provenance and explicit successor limits, then retry configured Linux analysis; keep QNX skipped.
