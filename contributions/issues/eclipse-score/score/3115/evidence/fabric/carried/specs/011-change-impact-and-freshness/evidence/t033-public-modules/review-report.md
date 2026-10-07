# Verified public inputs, module extraction and pilot package loading

The exact public `score_toolchains_rust` v0.10.0 archive and registry version patch
are acquired without credentials and match the native integrity pins. The archive
is 63,963 bytes and the patch 269 bytes; HTTP status, URLs, redirects and SHA-256
are retained. Thirteen further public inputs are imported from the existing cache
after hash checks. The prepared fifteen-input set contains 22,210,144 bytes.

[Input bindings](public-module-manifest.json) connect every archive/patch to its
registry source declaration and the original lock. [Selected declarations](dependency-source-bindings.json)
retain the actual registry bytes. Only the two missing Rust inputs are fetched
remotely; all other inputs use existing verified bytes. No SDK or binary toolchain
payload is acquired remotely. Native source/module/lockfiles and checksums stay unchanged.

Eight real native probes use Bazel 8.7.0 in a fresh bound SSD workspace. Each serves
all 68 captured public metadata pages without misses. Exact loopback routes preserve
archive filenames. Native HTTP delivery is observed for eight module archives,
totaling 22,207,875 bytes. Patch inputs are available in the writable native cache;
the Rust module finishes with version `0.10.0`. Delivery, integrity, completed
repository materialization and configured target analysis remain separate results.

| Probe input expansion | Measured next outcome |
| --- | --- |
| Rust source/version patch and Perl rules | `aspect_rules_esbuild` archive refused; Rust and Perl materialize |
| esbuild rules archive/patch | `aspect_rules_js` archive refused |
| JavaScript rules archive/patch | `aspect_tools_telemetry` archive refused; native crash stack retained |
| Telemetry support archive/patch | `rules_nodejs` archive refused |
| Node rules archive/patch | `yq.bzl` archive refused |
| yq rules archive/patch | `rules_kotlin` archive refused; native crash stack retained |
| Kotlin rules archive/patch | Bats core archive refused; native crash stack retained |
| Direct unconfigured query of the five pilot labels | Exit 0, exact five labels returned |

[Native results](modules-results.json) preserve complete command/output/request
records. Each probe pins its exact input manifest snapshot; later cache population
does not change earlier evidence. The attempt counter correction counts native
result records separately from input snapshot files; both operator versions are
retained, and the original eight-attempt ceiling stays fixed.

[Completed repositories](materialized-modules.json) retain native marker and source
hashes for seven modules: Rust toolchain rules, Perl rules, esbuild rules, JavaScript
rules, telemetry support, Node rules and yq rules. The Kotlin archive is delivered
with its exact hash, but its completed marker/source repository is absent when the
stage closes. Successful Kotlin extraction is not established. The positive final
query measures target package loading only; it performs no configured dependency
analysis, compilation or tests and accepts no broader engineering scope.

The final configured analysis refuses
`https://github.com/bats-core/bats-core/archive/v1.10.0.tar.gz`.
[Bats readiness](bats-readiness.json) binds the genuine declaration and checksum
tables through `aspect_bazel_lib` 2.22.0's original lock-bound module archive. The
selected declaration and license bytes match that archive exactly. Its default
helper library inputs remain declared discovery, without successful native fetch:

| Input | Measured cache availability | Stage use |
| --- | --- | --- |
| bats-core v1.10.0 | 159,353 bytes available, expected SHA-256 verified | Not imported; native URL refused |
| bats-support v0.3.0 | Absent | Not fetched/imported |
| bats-assert v2.1.0 | Absent | Not fetched/imported |
| bats-file v0.4.0 | Absent | Not fetched/imported |

The eight-attempt stage is exhausted. The next technical step is to prepare these
source-bound public testing dependency archives in a fresh bounded stage and then
retry configured Linux analysis. Further dependencies may appear; no complete
closure, accepted verification denominator or native impact/work-product mapping
is inferred from these inputs.

Every native probe hides the real home, clears the environment, isolates external
networking and restricts persistent writes to the selected workspace. The mirror
permits only exact captured input routes; other downloads, including QNX, refuse.
All processes are reaped and mirrors closed. QNX remains skipped because the owner
has no license; its applicability and platform qualification remain unresolved.

Twenty earlier packets, T032's twenty reviewed subjects, all 310 fabric source/test
subjects and the 740 original native files remain unchanged. Existing 223 tests and
static checks are carried by unchanged source hashes. Fresh frozen, foundation,
package, Spec Kit and trace checks are recorded separately. No native build/test,
paid model request, live Fabro admission, publication or human acceptance occurs.
T033, reviewer roles, full expected scope/impact and live output feasibility remain
pending offline, outside workflows.
