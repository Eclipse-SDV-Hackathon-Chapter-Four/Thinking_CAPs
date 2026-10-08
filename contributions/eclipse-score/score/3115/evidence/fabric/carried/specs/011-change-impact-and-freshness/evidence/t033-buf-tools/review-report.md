# Cached Linux Buf tools and the remaining compiler dependency

The three Linux Buf v1.47.2 executables selected by the original-lock-bound wrapper
are imported only from existing cache. Each archive-list hash, URL and byte count
matches. No new remote HTTP or binary download occurs. The initial input set contains
28 files totaling 99,394,665 bytes, within the 32-file/64 MiB-per-file/128 MiB-total
bounds. All 740 original native files, lockfiles and inspected hooks remain unchanged.
The Python 3.12.14 runtime is reused read-only from its verified storage-bound workspace.
Credentials and private state are hidden from native execution; tool storage stays unchanged.

The one actual configured Linux `cquery deps(set(...))` covers the same five historical
pilot labels. It exits 1 after 6.933 seconds, without timeout. All 68 metadata responses
and sixteen asset response writes complete and match their exact input hashes. The
three Buf executable writes account for 74,551,752 bytes. [Raw native evidence](buf-results.json)
binds the command, source/tool/operator hashes, per-probe input snapshot, downloader
configuration and complete stdout/stderr. Attempted response bytes and completed writes
remain separate from native materialization.

[Completed repository evidence](materialized-dependencies.json) records the genuine
Buf toolchain repository marker, all source/generated-file hashes and exact executable
hashes/modes for `buf`, `protoc-gen-buf-breaking` and `protoc-gen-buf-lint`. The Go rules
repository, previously incomplete, now has a completed marker. Kotlin and both Bats
core aliases also complete. These records establish native materialization. No Buf tool
execution, native compilation or native test execution is observed; configured analysis
still fails and does not establish engineering readiness.

Native analysis now refuses the Linux x86_64 Ferrocene compiler archive at
`https://github.com/eclipse-score/ferrocene_toolchain_builder/releases/download/1.3.1/ferrocene-779fbed05ae9e9fe2a04137929d99cc9b3d516fd-x86_64-unknown-linux-gnu.tar.gz`.
[Compiler readiness](ferrocene-readiness.json) retains its original extension repository
attributes and exact compiler/coverage-tools/Miri-sysroot hashes and URLs. The wrapper,
BUILD and LICENSE bytes are verified against the original-lock-bound Rust module archive
and actual native repository. The compiler, coverage tools and Miri sysroot are absent
from the inspected existing cache. Their sizes and payload licensing/qualification remain
unmeasured; the wrapper's license does not accept the payloads.

The current scope permits three cached Buf binaries, source archives/patches and pinned
checksum metadata. It excludes compiler acquisition and execution. The stage stops after
one of eight allowed probes because an unchanged retry would reproduce the same denied
compiler dependency. [The next operation draft](ferrocene-next-stage-draft.json) preserves
missing inputs and unresolved size bounds; it proposes measuring exact Linux compiler
inputs and preparing explicit storage/input limits before a fresh retry. It performs no
compiler acquisition and grants no engineering acceptance.

The namespace denies all unlisted downloads and external networking; QNX downloads and
execution stay skipped per the owner's instruction and absent license. All owned native
processes are reaped and the loopback mirror is closed. The report contains no offline
human decision, native applicability acceptance, paid model request, live Fabro admission,
publication or release.

Twenty-two historical packets (5,374 file subjects), T032's twenty reviewed subjects,
310 fabric source/test subjects, 740 original native files and 405 imported cache markers
are verified unchanged. Previous 223 tests, Ruff and mypy over 152 source files are carried
with unchanged source hashes; fresh frozen dependency, foundation, pinned Spec Kit, package,
trace and control consistency checks are recorded separately. The historical five-label
loading success is preserved. Full configured Linux analysis/build/tests, accepted impact
scope, native roles and live B1–B5/T033 qualification remain incomplete. Review remains offline.
