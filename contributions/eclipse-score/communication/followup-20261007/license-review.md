# License header verification

The final Communication and Config Management patches include notices on every
current code file. The independent audit enumerates 2,534 Communication files and
324 Config Management files, including empty package files, C/C++, Rust, Python,
Starlark, JavaScript, shell scripts, TRLC models, PlantUML sources, CodeQL queries
and suites, shell templates and lint fixtures. Packet-owned Python collectors
also carry the project notice. Their exact count and hashes are in
[license-header-audit.json](license-header-audit.json).

The policy is the [Eclipse Project Handbook copyright and license header
guidance](https://www.eclipse.org/projects/handbook/#ip-copyright-headers), applied
using the repositories' Apache-2.0 LICENSE, NOTICE and native header templates.
Existing numeric copyright years and ownership statements are retained.
Missing notices and unresolved `{year}` placeholders receive the current 2026
project notice; no corporate owner or contribution identity is invented.

The native copyright checker now scans each complete repository. Communication's
templates cover additional code extensions such as JavaScript, YAML and query
suites. Its literal template resource has its own license notice but contains
example headers that trigger duplicate detection; the supported exclusion file
handles that resource, as upstream S-CORE tooling does. The exclusion removes no
code file from inspection. The independent code audit complements the native
checker for extensions and fixture names that it cannot select directly.

Imported content retains its original terms:

- The modified MISRA query includes GitHub's original 2022 MIT copyright and
  complete license text, an MIT SPDX identifier and an explicit modification
  notice. Its separate LICENSE.md remains byte-identical to the native upstream
  license; the audit compares the inline text with that retained license.
- All six modified rules_build_error shell helpers retain CC0-1.0, with the SPDX
  identifier and upstream LICENSE reference immediately after the Bash shebang.
- Generated GitHub action bundles preserve all existing bundled third-party
  notices and program lines. The added header explicitly covers project-owned
  portions; a checked-in license banner is consumed by the build script so
  regeneration retains that notice.
- The Config Management formatter compatibility files retain their original
  Apache-2.0 notices and 2025 year from the previously pinned S-CORE tooling
  commit. Their native provenance is documented in `bazel/format/README.md`.

JSON lockfiles cannot contain inline comments. Native LICENSE and NOTICE cover
the project's lockfile material; embedded generated dependency content retains
its native licensing. Historical source snapshots, database archives, logs and
the frozen original contribution packet are retained with their original bytes.
They are evidence of earlier subjects, not the current files to submit.

The audit compares program bodies before and after notice normalization, retaining
every nonblank program line. Checker configuration, the bundle banner generator,
formatter migration and buildifier keyword ordering are recorded separately.
The primary patches contain the complete change. The `*-license-headers.patch`
extracts apply on top of their corresponding preserved pre-cleanup patches and
provide a separate review of the requested cleanup.

Native verification is recorded in [verification.md](verification.md) and
[required-checks.json](required-checks.json). License-header compliance does not
supply the outstanding consumer safety dispositions, hosted CI results or native
reviewer acceptance listed in [readiness.json](readiness.json).
