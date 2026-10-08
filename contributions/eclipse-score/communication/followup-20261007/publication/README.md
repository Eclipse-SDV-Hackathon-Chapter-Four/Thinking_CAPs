# Draft publication record

[PR #1342](https://github.com/eclipse-score/communication/pull/1342) is open as a draft for Jefferson Nascimento's review.
The existing fork was reused. The native source commit is `fb634728809bae2cacf485c9edab891a1ab20321`;
all 264 changed filenames and recorded changed-file bytes match the reviewed
packet. Strict Eclipse ECA validation passes for the actual commit. GitHub
reports mergeable; required checks/reviews still block merge. Auto-merge is off.

`PR-BODY.md` is verified against the remote body. `pull-request.json`,
`pull-request-files.json`, `initial-check-runs.json` and `result.json` record
the publication checkpoint. `eca-validation-*` records the actual-commit check.
The HTTPS push rejection is retained; existing SSH authentication published the
same unchanged source. Git 2.34.1 lacks `merge-tree --write-tree`; a temporary
real merge was clean and was then aborted to retain the verified source head.

The public evidence export is pinned to `fff9909a98b2a148b766ef1dada0a7e61d28aff8`. The export's own manifest
passes for 142 artifacts, including selected full logs and final SARIF. The
complete local packet retains archives and history omitted from that export.

#1031 production safety decisions are explicitly deferred in the PR body.
The Config Management companion remains local; no companion PR is published.
The license-header overlap with PR #1341 is called out for review.
