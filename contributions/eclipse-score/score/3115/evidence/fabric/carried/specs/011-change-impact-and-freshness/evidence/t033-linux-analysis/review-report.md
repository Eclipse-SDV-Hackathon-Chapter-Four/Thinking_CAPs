# Complete metadata input and remaining Linux analysis dependencies

Each of four real Bazel 8.7.0 probes consumes all 68 previously captured public PyPI
pages: 11,268,375 bytes per probe, zero misses. The prepared `roman-numerals` page is
now exercised. No Python metadata failure remains in the observed output. Configured
Linux analysis still fails; the final probe refuses the exact public
`score_toolchains_rust` 0.10.0 source archive before remote bytes arrive.

| Probe | Measured outcome | Limit |
| --- | --- | --- |
| Original no-fetch analysis | Exit 37; `score_toolchains_rust+` absent, fetch disabled | Full configured dependency analysis unavailable |
| Isolated repository materialization | Exit 37; native downloader refuses pinned `rules_perl` archive URL | Real registry metadata alone supplies no archive bytes |
| Verified public archive cache import | Exit 37; native `rules_perl` cache hit followed by rejection of extensionless `cacheprobe` filename | Matching bytes alone do not establish extraction success |
| Filename-preserving loopback archive route | Exit 37; native downloader refuses pinned Rust module archive URL | No archive HTTP request or successful `rules_perl` extraction is established |

[Native results](analysis-results.json) bind exact commands, isolated environments,
source/tool/operator hashes, downloader configurations, raw output/crash stacks and
all mirror requests. The last configuration permits only the exact cached public
`rules_perl-1.1.0.tar.gz` URL through loopback with its filename preserved. No request
reaches that archive route in this probe; the proposed extraction workaround remains
unqualified. All 68 metadata requests in each probe return 200 with exact input hashes.

[Module cache inputs](module-cache-inputs.json) distinguish availability and use.
The cached `rules_perl` 1.1.0 archive matches its SHA-256 declaration exactly and
contains 65,035 bytes. It is copied into the new writable cache and retained in this
packet. Its real native cache hit is observed in the third probe. The other two inputs
are absent from the measured cache:

| Required public input | Expected SHA-256 |
| --- | --- |
| `toolchains_rust` v0.10.0 archive | `52d483e4c2d5f41b3bbaaf7f0a98a32119ad465a6e7164ca5fa8fa5913b5eac3` |
| `module_dot_bazel_version.patch` | `7a15ca463d387eaa498c86ae8bef4124154b26b879330710e0832695a8c781bd` |

Their exact URLs and integrity fields come from the registry `source.json` bound by
the original `MODULE.bazel.lock`. [Selected registry sources](dependency-source-bindings.json)
retain the declarations and license headers. The next step is to prepare these exact
public bytes and then run a fresh bounded analysis with filename-preserving archive
routes. No successful download, patch application or native extraction is asserted.
More dependencies may become visible afterward; these inputs are not a complete closure.

The new SSD workspace contains the unchanged 740-file native original at baseline
`7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`, the exact pinned binary and 685 registry
files matching positive lock hashes. The 469 recorded negative registry results remain
distinct. Previously generated external repositories and genuine embedded tools are
read-only historical cache inputs. Hooks and configuration are inspected; no `.git`
hooks are copied or executed. Source/module/lockfiles, versions and SDK checksums stay
unchanged. The `score_tooling` requested/resolved version warning is retained.

Every probe has external networking isolated, the real home hidden, environment
cleared and persistent writes restricted to the bound disposable workspace. Only
captured loopback input routes are permitted; all other downloads, including QNX,
are blocked. The owner's no-license QNX skip remains explicit. No SDK, private
credential, compilation, test execution, paid provider request or publication occurs.

The four-attempt stage is exhausted. Processes are reaped and mirrors closed; no
unattended native run remains active. Nineteen historical packets, T032's twenty
reviewed subjects and all 310 fabric source/test subjects remain unchanged. Existing
223 tests and static checks are carried only by unchanged source hashes; fresh frozen,
foundation, package, Spec Kit and trace checks are recorded separately.

The five pilot labels remain the historical selection. This evidence accepts neither
the complete eighteen-row/135-label scope nor source impact, native work products,
QNX applicability, reviewer roles, live model output feasibility or T033. Human
engineering decisions remain offline, outside workflow execution.
