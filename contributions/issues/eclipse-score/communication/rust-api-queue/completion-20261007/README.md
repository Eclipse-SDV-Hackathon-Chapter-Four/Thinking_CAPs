# Communication contribution completion packet

Integrated candidate for #1261 (configured LoLa deployments), #250 and #560 on current-main baseline `cef680454e8586daca9f953084dca33fb3759d0c`. Discovery uses one selected configured instance deployment and quality level per LoLa type; type-only declarations without an instance deployment and entirely unconfigured interface types remain outside this contribution. The broader #1261 request remains open.

Candidate: `8f7695f09614c979b8a5f4721e9f2346d500d127`; patch SHA-256: `b8f1dcd9b5ca6d8594c0ad249eb5c2336ada471e3e77049becfed109f6fab04b`. The candidate is a local unsigned review commit; no PR has been published or merged.

The implementation resolves the competing bridge names, preserves IRuntime and Runtime layout, corrects callback ownership on new registrations, replaces unit errors and resolves strict diagnostics in changed code. Tests, detailed design and user examples accompany the changes.

- [Measured checks](CHECKS.md) and [machine-readable inventory](expected-checks.json)
- [Acceptance and design trace](ACCEPTANCE-TRACE.md)
- [API/ABI and migration review](API-ABI-REVIEW.md)
- [License-header audit](LICENSE-HEADERS.md)
- [Diagnostic disposition](WARNING-DISPOSITION.md)
- [Sanitizer coverage and exclusions](SANITIZER-COVERAGE.md)
- [Human/IP review subjects](HUMAN-IP-REVIEW.md) and [IP submission draft](IP-SUBMISSION.md)
- [Merge requirements](MERGE-ARTIFACTS.md)
- [PR title](PR-TITLE.txt) and [description](PR-BODY.md)
- [Reproduction and offline review](REPRODUCE.md)
- [Integrated patch](communication-integrated.patch), [full Git bundle](communication-integrated.bundle), [complete source archive](communication-source.tar.gz) and [source identity](source-identity.json)

Run `python3 verify.py` to verify the sealed inventory. Human engineering/rights/IP acceptance, official ECA status, QCC execution and protected PR/merge-group checks remain pending. Local evidence does not establish merge readiness. See the check inventory for every failed or unavailable local check.
