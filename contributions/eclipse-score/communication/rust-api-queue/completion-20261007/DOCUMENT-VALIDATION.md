# Native document validation observations

The full host build runs native dependable-element and architectural-design validators as well as compiling code. Bazel's successful action status does not establish that these documents passed their semantic checks.

The final full host-build source epoch reports two architectural-design errors for `message_passing_architectural_design` and 29 dependable-element errors for `mw_com_index`. The findings include missing public interfaces in the message-passing diagrams and component/unit aliases from the communication static diagrams absent from the generated Bazel model. The complete host-build log preserves every finding and its native source/line reference. The retained final validation logs and `evidence/run-metadata/document-validation-findings.json` record all 31 reported errors on the exact candidate source.

These diagnostics refer to existing native architecture diagrams and model definitions outside this contribution's changed-file set. They have not been dismissed, renamed, waived or accepted by this task. A native owner must assess their applicability and resolve the document/model correspondence under the adopted plan. No approved requirement, architecture or safety status is inferred from a nonfatal tool result.

The contribution supplies its proposed native-to-Rust acceptance/design trace, updated Rust detailed design, public scope/lifetime/error documentation and tested production examples. Those work products remain subject to human requirements/design/safety acceptance alongside the existing native validation findings.
