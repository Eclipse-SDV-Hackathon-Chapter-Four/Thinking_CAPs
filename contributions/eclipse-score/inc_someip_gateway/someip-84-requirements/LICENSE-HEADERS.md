# Native license header audit

Audited 243 tracked code/build files; all have
inline copyright, Apache license notice/link and SPDX identifiers. This covers
45 files changed by the full contribution.
All changed C++ files disclose AI assistance and the Apache-2.0 AND CC0-1.0
expression. Original notices are retained, including the Bazel Authors' valid
Apache notice (its HTTP license link and copyright syntax are preserved).

Added the standard project Apache header to `score/config/mw_someip_config.fbs`,
which previously relied on the existing REUSE annotation. The schema body and
license remain unchanged. This conventional header is copied from the project
header template and does not attribute existing schema code to an AI.

[Per-file hashes and findings](evidence/mapping-license-headers.json) record the
scope and criteria. The initial audit's overly narrow copyright/link matching
and genuine missing inline schema header remain recorded as history. Native
copyright and REUSE hooks pass in the final pre-commit run. These checks assess
notices and consistency; project IP acceptance remains pending.

Guidance: [Eclipse Project Handbook](https://www.eclipse.org/projects/handbook/),
native `AGENTS.md` and `.github/instructions/code-style.md` (included in the
policy snapshot). External fetched dependencies, generated build outputs and
ephemeral scratch are outside the authored native source audit.

