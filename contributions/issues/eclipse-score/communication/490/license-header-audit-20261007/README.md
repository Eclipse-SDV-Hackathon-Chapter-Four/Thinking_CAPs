# Communication #490: license-header audit

[PR #1340](https://github.com/eclipse-score/communication/pull/1340) head `0b363baf2a0520c8e31b617378459457c197e9a7` matches the audited source. All 5 changed code/build files passed the native score_tooling 2.3.1 copyright checker with the repository's unmodified `third_party/cr_checker/templates.ini` and `config.json`. Every file contains the Eclipse contributor copyright, NOTICE reference, Apache-2.0 license text/URL and SPDX declaration. Raw verbose classifications are in checker.log, exact command/environment/exit in checker-result.json, and file/tool/template/config hashes in result.json.

The changed Markdown design document has its existing full Eclipse/Apache-2.0 HTML-comment header unchanged from upstream. No Markdown template is configured in the native checker; its complete header was checked separately and that method is recorded in result.json.

No source or header fix was necessary; native PR heads and previously measured behavior evidence are unchanged. Existing file years were preserved, and the new source files use 2026. The current native tool matches years structurally rather than enforcing the legacy config.json years list. This is validation of the complete changed-file set, not a claim that every unrelated upstream file passes the repository-wide checker.
