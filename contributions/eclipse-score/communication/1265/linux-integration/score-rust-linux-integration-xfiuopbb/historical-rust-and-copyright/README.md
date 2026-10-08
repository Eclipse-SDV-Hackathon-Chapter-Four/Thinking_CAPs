# Communication #1265 — Rust verification passed; copyright findings remain

The generic S-CORE Rust issue workflow is implemented and installed. This
contribution documents the existing pastey 0.2.3 dependency, usage patterns,
provenance, licenses, alternatives and qualification/adoption obligations.
The patch changes the Rust README and adds an assessment. Production Rust,
dependencies, APIs, compiler pins, locks and native policies are unchanged.

**All three selected native Rust targets passed: 33 cases passed and two doctest
cases were ignored.** The pinned Ferrocene compiler ran in a hash-bound private
Ubuntu Noble library namespace. Native run `01M484ZS5EGJ8E5KH83XXN7PCB` executed
the cases. Subsequent copyright-only runs carry that evidence through verified
unchanged source, configuration, runtime and test-log hashes; tests were not repeated.

Copyright verification remains failed. The archive first needed disposable Git
metadata. The default native rule then passed two Bazel labels as invalid Git
paths. An explicit operator wrapper resolved only those two labels, retaining
every other argument, template, configuration and input path. The resulting
unchanged native checker reported **204 findings on 204 baseline-identical files**:
96 missing headers, 107 format findings and one duplicate header. Findings remain
pending native review; no false-positive, acceptance or suppression decision is made.
Native templates exclude Markdown. The assessment's Apache-2.0 SPDX notice was
separately inspected as text; that is not native Markdown copyright coverage.

Final run `01M4863C6JY8WNMY9T44H47XV8` has failed lifecycle: preflight passed,
verify/export failed. Export retained the failure evidence and returned failure.
The fresh recovery exhausted **3/3 fixes**; no further repair, broad copyright
cleanup or relaunch occurred. All owned private servers stopped; native Fabro
model lists are empty and recorded token usage is zero.

See [verification report](verification-report.json), [patch](communication-1265.patch),
[native Rust logs](execution/logs/communication-macro-tests.log),
[copyright findings](copyright-findings.json), [correction ledger](correction-ledger.json),
[supervisor review](supervisor-review.md), and [PR draft](pr-description.md).
The packet preserves previous 175- and 515-subject contributions, including nested
historical manifests, source notices, exact image/checksum inputs and all raw attempts.

Results apply to baseline `e3d126c2d7569345cf5f790310702eb00cd86b06`. Observed
upstream HEAD `81a540e196421d7613350d77068e9a886eccbac6` differs in a C++/Rust FFI
header. The documentation patch checks cleanly against its unchanged README;
native verification of that newer baseline remains pending. Compiler qualification,
communication adoption, QNX/full CI and human engineering acceptance remain pending.
The issue is open; no publication or accepted fix is claimed.

Operational deviation: one non-build Bazel help query extracted an installation
into its default cache. Its exact cache delta was not measured. All native build
outputs remained bound to the SSD; no queues or global storage configuration were
migrated. The [deviation record](execution/auxiliary-help-storage-deviation.json)
remains explicit rather than claiming zero global cache writes.
