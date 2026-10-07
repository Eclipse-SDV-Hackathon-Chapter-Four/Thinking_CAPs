# Communication #1167 — non-QNX contributor work complete

[PR #1335](https://github.com/eclipse-score/communication/pull/1335), head `2aead7cd18c96b907e086c8b59797b527f65567d`, now has [all six non-QNX fork Host jobs passing](https://github.com/jnsagai/communication/actions/runs/37652549770) with zero lint findings in the new test. GCC15 passes 507 tests (seven skipped) and module integration; ASan/UBSan/leak passes 506 (eight skipped); TSan passes 404 (110 skipped under native exclusions). New runtime/schema tests pass under GCC15 and ASan. QNX is excluded as requested.

The exact verified merge tree is `dcee6cdd36f7826eda8fe47cb75a578b769f65e2` on upstream `cef680454e8586daca9f953084dca33fb3759d0c`. Later upstream changes are recorded separately and await native CI. Source archives, patches, full logs, three native lint reports, test inventories, unchanged controls, formatting and ECA proof are in the [final verification packet](non-qnx-verification/README.md).

Copyright remains failed with 200 identical findings on the pinned baseline, zero PR additions. Seven header-eligible contribution files pass; two JSON files have no native header template. The original scoped human acceptance is preserved on its original source, without a follow-up acceptance or copyright waiver.

The PR remains unmerged: maintainers must approve native workflow execution, obtain required upstream statuses, approve the final source through code-owner review, determine inherited copyright handling and use the merge queue. Fork results do not satisfy upstream required contexts automatically. All predecessor evidence and the exhausted paid supervisor remain unchanged.

Repository-wide license scope requested by the user is also complete: [companion PR #1341](https://github.com/eclipse-score/communication/pull/1341) repairs 91 files and audits all 2,367 code/build/template paths, with zero code-header findings. [Header packet](repository-license-headers/README.md) contains the complete inventory, comment/AST preservation proof, formatting, 14 fixture tests, ECA and source archive. Its whole-repository checker retains 136 non-code findings; native CI/review remain pending.
