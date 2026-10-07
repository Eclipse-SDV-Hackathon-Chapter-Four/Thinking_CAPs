# US38 offline Linux Ferrocene review report

The three exact original-lock-bound Linux Ferrocene inputs have been acquired and
verified. Both generated Linux Ferrocene repositories have completed native markers.
Configured Linux analysis remains failed at the unlisted Coreutils 0.1.0 archive.
This report supplies measurements for offline review; engineering acceptance remains
pending. No human decision, native build/test pass or live qualification is inferred.

| Input | Acquired bytes | SHA-256 |
| --- | ---: | --- |
| Compiler | 215,780,903 | `6fd7c7053a80463b2bfd24202de02e16959b18ed185c55b738148e9caac42eff` |
| Coverage tools | 8,299,605 | `9cf5d76b2e505bf2a8b2b47c60f191ac1273f87851ed387e53080b8e5d14dedf` |
| Miri sysroot | 65,742,537 | `143260fe3873249160d57b370717005828e129d3b6782448a32d8cc578384fe0` |

These three Linux payloads total **289,823,045 bytes** and **924,700,217 expanded bytes**.
Together with the 28 inherited inputs, the 31-file input set totals **389,217,710 bytes**.
No payload request was retried. [HTTP receipts](payload-provenance/) bind declared
lengths, exact URLs, redirect origins, acquired bytes and digests. Temporary signed
redirect queries are omitted from payload receipts; credentials were not supplied.
Large archives remain on their bound SSD workspace, with exact file paths in
[acquisition results](acquisition-results.json). Retained packet files include full
inventories, compiler notice bytes and source/HTTP provenance.

The release metadata/checksums and original native lock independently agree on each
payload digest. [Acquisition plan](acquisition-plan.json) binds the original lock,
release 1.3.1 builder commit `c356bc3b0ad42730c36da7fbc4612eb6be8fc269` and declared
Ferrocene source commit `779fbed05ae9e9fe2a04137929d99cc9b3d516fd`. Builder source
and its three local patches are retained with Git blob and SHA-256 checks. This is
source provenance, not an independent reproduction of the upstream binary build.
[Source and license provenance](source-and-license-provenance.json) preserves wrapper,
builder and compiler-source notices separately from the actual payload notices.
The compiler contains **26** matched license/copyright files, retained in full. The
coverage-tools and Miri archives contain no files matching the notice selection; their
licensing or qualification is not silently accepted based on the compiler's notices.

[Stage limits](stage-limits.json) explicitly replace the previous smaller stage bounds:
32 public inputs, 256 MiB/input, 512 MiB total, exactly three payload requests with
180-second bounds, 8 GiB expanded archive data, 100,000 members/archive, 20 GiB free
reserve, and at most three 120-second native attempts. The stage stops at its first
unchanged/out-of-scope prerequisite. The compiler's 13,733,840-byte COPYRIGHT.html
exceeded the initial reader's 2 MiB per-notice bound after payload verification.
The refusal and original operator remain retained. A measured separate reader
correction sets 16 MiB/notice and 32 MiB/archive before continuing from the already
verified payload; no compiler redownload or input-scope widening occurs.
Preparation also retains checksum path-prefix assertion refusals and a source-notice
directory's HTTP 404. The final parser checks exact digest and basename. Collection
retains its initial executable-bit assertion: a cargo completion file matched its
archive hash but is correctly nonexecutable. Final records explicitly compare source
and native executable bits. These are preserved operator failures, not hidden native
successes or altered payloads.

The owner confirmed the existing build image should be **1 TiB** and authorized
mounting it. The registered image UUID is unchanged. Storage selection first observed
an unavailable mount, then mounted the registered existing image. Its device number
changed from 1818 to 1819, so old workspace guards still correctly refuse reuse.
A fresh workspace binds the current mount; historical inputs receive independently
verified read-only bindings on the same UUID-bound volume. Old records/queues are
unchanged. Only the registration's capacity field was corrected from 128 GiB to
1 TiB. This session did not resize, reformat or repair the image.
[Volume input bindings](historical-input-volume-bindings.json) and
[capacity reconciliation](storage-capacity-reconciliation.json) retain that distinction.

One genuine isolated configured five-label `cquery` exited **1** in **23.691 seconds**,
without timeout. [Complete command/stdout/stderr/mirror record](native-probes/linux-pinned-ferrocene-analysis.json)
binds the native binary, operators, source archive and exact per-probe input manifest.
All **68** metadata and **25** asset responses completed, with no metadata misses or
interrupted response writes. Exact archive extraction produced the Linux compiler and
rules_rust Miri repository markers. Compiler, coverage and Miri materialization remains
separate from tool execution, native compilation/test or tool qualification. The native
log reports zero action processes; no compiler/coverage/Miri execution was observed.
The retained score_tooling version warning is not disabled or rewritten.
External networking is denied by the namespace; the loopback mirror serves only listed
inputs. QNX SDKs/variants, unlisted downloads and credentials stay denied.

The next observed missing input is:

- URL: `https://github.com/uutils/coreutils/releases/download/0.1.0/coreutils-0.1.0-x86_64-unknown-linux-musl.tar.gz`
- Native repository: `@@aspect_bazel_lib++toolchains+coreutils_linux_amd64`
- Declared SHA-256: `463648347b1fc337414a864bda960c9cbd1bd4a540f344c010ff5bb35199e6d7`

[Coreutils readiness](coreutils-readiness.json) binds the declaration through the
original-lock-hashed aspect_bazel_lib 2.22.0 registry source, verified module archive,
wrapper and preserved wrapper license. The payload is absent from the inspected
historical repository cache; its size and actual notices remain unknown. This is not
a machine-wide absence claim or input admission. The stage terminates before fetching
it, widening the allowlist, selecting another compiler or editing source/locks.

Fresh frozen sync, pinned Specify 1.0.12 version/prerequisites, foundation consistency,
package build, final control whitespace and trace audit pass. Unchanged source-bound
prior **223 scoped tests**, Ruff and mypy over **152 source files** are carried; they are
not rerun merely to restate validation. All **310** fabric source/test subjects,
**740** original native files, **3,484** retained runtime files, **405** original cache
markers, T032's **20** subjects and **23** historical sealed packets (**5,657** file
subjects) are checked unchanged. [Validation](validation-results.json),
[preservation](preservation-current.json) and [process closure](process-verification.json)
remain distinct records. Every owned native probe/mirror exits; no provider/private
server or background continuation starts.

Recorded 011 tasks are **133/135** complete after this technical stage. Human-owned
T032/T033 markers remain unchanged; this is not a whole-mission completion measure.
Full native expected-check denominator, transitive impact/work products, reviewer
roles, live B1–B5/T033 qualification and payload/tool qualification remain unresolved.
QNX is skipped per the owner, without accepting applicability or platform qualification.
PR publication remains deferred. No paid request, commit, push or publication occurs.

Next concrete action: measure and prepare the exact Linux Coreutils 0.1.0 payload with
source/cache/size/notices provenance and explicit finite bounds, then retry configured
analysis in a fresh bound stage. Do not reuse this stage's unused attempts or infer
missing-input bytes as zero. Human engineering decisions remain offline.

A first final foundation check refused a transient report link because the validation
record was generated after the check. Its exit-1 log and original finalizer are retained
under `repository-check-attempts/` and `operator-scripts/`. The corrected generation
order creates the pending validation record before the final check, then replaces it
with measured completed results. Current final checks are rerun; no failed attempt is
presented as a pass.
