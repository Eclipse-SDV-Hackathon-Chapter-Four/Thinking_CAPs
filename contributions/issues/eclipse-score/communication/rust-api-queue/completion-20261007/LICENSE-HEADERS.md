# Source license-header audit

All 40 changed native code files (19 Rust, 5 C++, 2 headers, 3 Python and 11 Bazel BUILD files) carry the project copyright notice, NOTICE reference, Apache License Version 2.0 text and `SPDX-License-Identifier: Apache-2.0`. Both changed Markdown documents carry the project notice too. Existing ownership and creation years are retained; the new callback-ownership regression uses its 2026 creation year.

The four changed JSON configuration files contain no comments, as required by strict JSON. They remain covered by the native project LICENSE and NOTICE, supplied in `native-project/`. This follows the [Eclipse handbook guidance](https://www.eclipse.org/projects/handbook/#ip-copyright-headers), consulted 2026-10-07, on source notices where technically feasible.

The final file-by-file audit is `evidence/run-metadata/license-audit.json`; the native modified-file checker command and raw result are linked in CHECKS.md. Whole-repository inherited findings, if any, are reported separately and are not assigned to this contribution or silently relabeled as passing.

The two workspace support scripts and the offline packet verifier also carry Apache-2.0 SPDX notices, with the ownership statement from the Thinking_CAPs LICENSE. Retained execution scripts and historical evidence preserve their original provenance and are not part of the native PR source. Header checks establish notice presence; contributor rights, ECA and human/IP acceptance remain separate review obligations.

The final full-tree checker reports 200 findings: 96 missing headers, 103 wrong-format headers (including 14 preceded by other content), and one duplicate notice in the checker template file. Every reported file is byte-identical to the recorded upstream baseline, and none is changed by this contribution. The complete baseline-bound inventory is evidence/run-metadata/inherited-notice-findings.json. These remain visible native findings; the whole-repository check is recorded as failing.
