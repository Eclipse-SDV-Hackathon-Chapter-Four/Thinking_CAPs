# Linux dependency loading with QNX skipped

The pinned Linux dependency load does not complete in the isolated probes. Three
different cache/configuration paths stop at the same Python index metadata lookup
for 67 packages. QNX execution remains skipped because the owner has no license.
No QNX SDK was downloaded or executed, and no compilation or tests ran.

The original archive matches SHA-256
`19dbc09f9424ff9d52a9f7ec8b64715c79cba32b4c063e0d41c158d657c5368c`;
all 740 source files match the retained native binding before and after the probes.
Bazel 8.7.0 and its exact executable digest are recorded in
[loading results](loading-results.json). Pre-commit/configuration and the QNX
credential helper were inspected as source before execution. The disposable source
has no Git directory or installed Git hooks. Reference repositories remain untouched.

| Probe | Native outcome | What it establishes |
| --- | --- | --- |
| Empty-cache pilot dependency query | Exit 37: local platform repository missing with fetch disabled | An empty cache is insufficient; this does not establish a QNX dependency failure |
| Query using 404 read-only repository overrides | Exit 37: Python index metadata failure, with native crash stack retained | Existing repository contents do not remove metadata evaluation in this path |
| Configured `x86_64-linux` pilot analysis using those overrides | Exit 2: Python index metadata failure while loading the base-library option | Linux analysis cannot yet proceed to the expected targets |
| Warm cache with exact marker copies | Exit 1: embedded `bazel_tools` missing | The initial import omitted Bazel's genuine embedded-tool symlink |
| Warm cache with the genuine embedded tools also bound | Exit 37: the same Python index metadata failure and crash stack | Completing that cache import still does not remove the metadata requirement |

All five probes use a measured `bwrap --unshare-net` namespace, a read-only root
and writable bound workspace. The real home is hidden and the environment is
cleared; private credentials are not supplied. Temporary home/dev/proc mounts are
separate namespace mounts. Native download controls remain enabled. Cold/warm
queries use `--nofetch`; override probes retain `--repository_disable_download`.
Every exact command, stdout, stderr, duration and reaped process outcome is retained
in [the result index](loading-results.json). No probe timed out. Repetition stopped
after the same metadata failure appeared through overrides, configured analysis and
direct warm-cache reuse.

The imported cache contains real previously acquired repositories and genuine
Bazel embedded tools. No SDK replacement, invented repository, changed checksum,
modified native module/lockfile or global cache configuration was introduced.
[Cache inputs](cached-repository-inputs.json), [warm imports](warm-cache-import.json)
and [selected dependency source pins](dependency-source-bindings.json) distinguish
historical local inputs from fresh remote verification. They do not establish trust
or native acceptance. The retained `score_tooling` warning reports requested 2.2.1
and resolved 2.2.2; its check was not disabled.

The five pilot labels remain the exact historical selection from the prior scope
review. No result establishes successful full Linux loading, the eighteen-row/135-label
denominator, transitive native impact closure, QNX applicability or native platform
readiness. The configured analysis stopped before QNX dependency resolution could
be established. The earlier QNX checksum failure therefore remains historical
evidence, separate from these new Python metadata failures.

The next useful technical step is to prepare public Python index metadata with an
explicit QNX download/credential denial, then repeat the same pinned Linux loading
and analysis. Keep original source and lockfile subjects unchanged and preserve
actual failures. Native scope/reviewer decisions remain offline; no live Fabro
instruction, provider request or publication follows from this report.
