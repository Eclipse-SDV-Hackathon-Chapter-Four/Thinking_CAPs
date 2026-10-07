# Documentation failure resolved; review preparation

PR [#3307](https://github.com/eclipse-score/score/pull/3307) now targets native main `f42e760912e5f99e0db993de717155cc85679f6c` through a merge of current main. Upstream commit [6122462](https://github.com/eclipse-score/score/commit/612246278900b74218e099d4549600f9f8f16be2) corrects the Report Running interface's `fulfils` relation. The change is carried from upstream, and the PR diff contains only the proposed decision record.

Fresh baseline/candidate docs checks, candidate HTML and copyright checks pass. Documentation and schema warnings: zero. The export adds one proposed DR and leaves all 925 baseline needs unchanged. Source/tool/policy locks are unchanged. See [verification-report.json](verification-report.json), adjacent command records and complete logs. The rendered page is a build artifact.

The original failed runs remain in [upstream-preparation](../upstream-preparation/README.md). They describe the earlier baseline and are superseded for current PR validation. The old workspace failed storage validation after its mount device changed; a fresh bound disposable workspace was allocated without modifying that old run.

This packet records direct local execution. Hosted CI, publication and reviewer delivery are captured separately in `publication.json`. Marking the PR ready for review supplies no human acceptance, qualification, issue closure or merge. The decision record remains proposed, version 2.
