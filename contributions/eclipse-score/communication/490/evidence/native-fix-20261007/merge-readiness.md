# Communication #490: merge readiness

Local engineering status: the issue implementation and selected native checks are complete for the documented scope. Native engineering acceptance and merge readiness remain pending. No PR, push, issue closure or comment was made.

## Prepared work products

- Current-main-based patch and portable branch bundle; clean patch application produces the exact candidate Git tree.
- Source/lock/policy/tool/environment bindings and changed native source; requirement, design, unsafe/ownership/concurrency assessment in [review-packet.md](review-packet.md).
- PR title/body with issue reference, measured validation and reviewer decisions.
- Raw native logs, test XML/BEP, Clippy aspect reports, format results, reproduction instructions and hash manifests; old failures and drafts preserved.

## Project gates

Source: [main rules](https://api.github.com/repos/eclipse-score/communication/rules/branches/main), observed in [context/merge-rules.json](context/merge-rules.json), and [CONTRIBUTING.md](native-context/CONTRIBUTING.md), bound to `c77751819b8885a902540dbef7f0fe25cf85d51c`. No local or inherited communication PR template was found in the captured repository/organization listing.

| Gate | State | Completion route |
| --- | --- | --- |
| `eclipsefdn/eca` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `GCC15 / Build & Test` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `QCC - Build & Test` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `Address & Undefined Behavior Sanitizer / Build & Test` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `Thread Sanitizer / Build & Test` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `Linters / clang-tidy` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `Linters / clippy` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `Linters / ruff` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |
| `review-checklists` | Pending | Publish reviewed candidate to a native PR; obtain this exact check on its revision. |

| Approving review | Pending | At least one approval, including code-owner review; stale approvals dismissed on push. Extra approval required for unattributed changes by the ruleset. |
| Engineering applicability / design acceptance | Pending offline | Approve isolated runtime lifecycle, bounded FIFO/no-replay semantics, explicit clone registration for multicast and panic on overlapping async receives. Confirm test-only dynamic allocation and any additional requirements/qualification obligations. |
| Merge queue | Pending | Maintainer queues the approved PR; all-green policy applies. |
| Full repository tests / format / copyright | Unrun locally | Follow native CONTRIBUTING instructions and required CI; retain any failures or documented maintainer dispositions. |

The repository's review-checklists configuration currently has `checklists: []`; the required status check still must run. A passing selected local suite or compiler name does not establish tool qualification, safety release acceptance, QNX validity or a passing full CI matrix.

Concrete next action: review the proposed decisions, confirm author ECA eligibility, then publish this candidate as a draft PR and run the native gates. The packet contains everything prepared locally; human approvals and server-side CI results cannot be replaced by files in this packet.
