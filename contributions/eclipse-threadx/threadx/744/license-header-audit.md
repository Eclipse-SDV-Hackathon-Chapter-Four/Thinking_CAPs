# License header audit

The automated [file-by-file report](artifacts/license-headers-final.json) audits every authored code/configuration file in this contribution scope. It checks leading comment headers rather than accepting license text embedded in test fixtures or ordinary code.

| Scope | Files | Header policy |
| --- | ---: | --- |
| Current ThreadX kernel patch | 5 | Preserve existing MIT copyright/disclosures; new AI-authored C and CMake files include MIT AND CC0-1.0, 2026 ThreadX contributors and the actual Codex model |
| Companion documentation patch | 1 | Preserve the chapter's existing Microsoft/Eclipse ThreadX copyright and MIT notice |
| Local workflow, tests, configuration and exploratory probe | 23 | Repository Apache-2.0 AND CC0-1.0, existing project copyright identity, Codex (gpt-6.1-sol) disclosure |

Added the missing MIT header and one existing-file AI marker to the modified parent `test/tx/cmake/CMakeLists.txt`. Added local headers to Python modules/tests, Fabro graphs, TOML configuration, Dockerfile and the exploratory C probe. New upstream SPDX conjunctions use uppercase `AND`, compatible with SPDX 2.x and 3.x tooling.

The deterministic gate runs during freeze, verification and immediately before publication. Missing/malformed headers, wrong SPDX identifiers, missing license URLs, changed or removed prior copyright/disclosures, and invalid AI attribution fail the gate. Its tests also reject license text after executable code and redirected source symlinks. Passing independent reviews cannot waive a failed or absent license check.

All 70 workflow tests passed, including header validation and the gate that
rejects absent/failed license checks. A fresh freeze also archives and removes
old PR drafts and review requests, including their exported mirrors, so earlier
passing claims cannot be presented as the result of later verification.

The user agreed to the reviewed dossier and supplied the ECA commit email in
separate messages. Their original text is preserved in the consent receipt;
only the approved human-reviewed sentence in the two new C files and their
CMake file was finalized. Fresh verification and independent reviews passed on that resulting patch,
with the disclosed SMP baseline failure retained. Publication passed the
canonical-wording audit for all 29 files. A header
alone is not evidence of actual human confirmation or Author-email ECA coverage.

Raw upstream policy/source snapshots and generated build outputs retain their original provenance and are listed separately with hashes. The duplicate raw build exports were verified against their loop4 originals before removal; full builds remain on loop4. Reports and compiler/test diagnostics remain exported. Historical snapshots are not silently rewritten or relabeled as newly authored code.

Policies: [Eclipse copyright headers](https://www.eclipse.org/projects/handbook/#ip-copyright-headers), [ThreadX contribution headers](https://github.com/eclipse-threadx/threadx/blob/e73752681bd405deddf247d1cf2b899d502dceaa/CONTRIBUTING.md#header-for-new-files), [SPDX 2.3 license expressions](https://spdx.github.io/spdx-spec/v2.3.1/SPDX-license-expressions/), [SPDX 3.0.1 license expressions](https://spdx.github.io/spdx-spec/v3.0.1/annexes/spdx-license-expressions/).
