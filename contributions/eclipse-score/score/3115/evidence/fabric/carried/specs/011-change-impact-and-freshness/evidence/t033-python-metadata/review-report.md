# Public Python metadata and QNX download denial

The original 67-package metadata failure is cleared in the final native retry.
That retry consumes the 67 real captured public pages and then identifies one
additional package, `roman-numerals`. Its real page is now captured too: the prepared
mirror contains 68 packages, 11,268,375 bytes. The 68-package input has not yet been
consumed by a native retry. Full Linux loading/analysis remains incomplete.

[Prepared metadata](metadata-manifest.json) binds each public PyPI HTML response to
its URL, timestamp, status, byte count and SHA-256; raw pages and individual HTTP
records are retained. [Consumed metadata](consumed-metadata-manifest.json) separately
binds the actual 67-package input used by this turn's native probes. The mirror
serves those exact bytes, with no invented package data or SDK content.

| Native probe | Outcome | Interpretation |
| --- | --- | --- |
| Exact declared QNX SDK repository query | Exit 37; URL rewriter blocks the pinned QNX archive URL; zero mirror requests | Expected download denial is observed before any SDK bytes; its native crash stack is retained |
| Linux analysis with old read-only download cache | Exit 2; all 67 local pages delivered but metadata still fails | Local HTTP delivery alone did not complete native download/metadata handling |
| Linux analysis with new writable but empty download cache | Exit 32; pinned registry lookup denied | The downloader also refuses an unlisted registry host; cached registry inputs are needed |
| Linux analysis with writable cache and exact lock-bound registry files | Exit 2; 67 pages consumed, only `roman-numerals` returns 404 | The original metadata failure is cleared; one newly discovered page is required |

[Full results](metadata-results.json) retain exact commands, stdout/stderr, mirror
request hashes, configuration/source bindings and closed process/server outcomes.
No probe timed out. The four-attempt native stage is stopped; the newly prepared
68-package mirror is a distinct next input, not a successful retry or accepted check.

The new cache receives 685 real registry files matching the exact original
`MODULE.bazel.lock` hashes, totaling 1,187,780 bytes. Its 469 recorded negative
registry lookups remain distinct from absent positive-hash files; no positive hash
is missing. [Registry imports](registry-cache-import.json) preserve these identities.
The existing reference cache remains read-only. The initial operator/cache version
is retained alongside the corrected writable-cache operator.

Every native probe runs in a measured network namespace with the real home hidden,
cleared environment and writable disposable workspace. A loopback server serves only
captured `/simple/<package>/` metadata and returns 404 for missing content. The pinned
[Bazel 8.7.0 downloader implementation](https://github.com/bazelbuild/bazel/blob/8.7.0/src/main/java/com/google/devtools/build/lib/bazel/repository/downloader/UrlRewriterConfig.java)
applies rewrite, allow and block directives; this probe allows only loopback after
rewriting PyPI index paths and blocks all other remote hosts. A deny-only credential
helper supplies no access. The genuine declared QNX archive request is refused;
no QNX helper invocation is observed, no SDK is downloaded and no SDK executes.

All 740 original native source files, source/lockfile pins and license notices remain
unchanged. Native module/lockfiles, QNX checksums, package versions and registry
declarations are not edited. The `score_tooling` 2.2.1-requested/2.2.2-resolved warning
is retained without disabling its check. Eighteen earlier packets and source-bound
production tests remain unchanged; current repository checks are recorded separately.

The next technical step is to run the same pinned Linux analysis with the prepared
68-package mirror and writable, lock-bound cache. The five pilot labels remain the
historical selection; no result accepts the full eighteen-row/135-label scope,
native impact/work products, QNX applicability or reviewer roles. No compilation,
test pass, paid model request, live Fabro admission, publication or engineering
acceptance follows. Human decisions remain offline, outside workflows.
