# #1261: Claude correction and measured Linux verification

[review.md](review.md) contains the change list, measured results for all three attempts, the
issue-criteria mapping and the open obligations. The other contents are:

- **`export/`**: the correction patch against the sealed `hdmk9onj` candidate, the full patch
  against baseline `381d43de…`, and the subject hashes.
- **`changed-source/`**: the eight changed files.
- **`superseded-candidate/`**: the plan and notes removed from the native tree.
- **`execution/attempt-{1,2,3}/`**: raw Bazel logs, build-event JSONL, `native-result.json`
  and native test logs and XML.
- **`runtime/`**: the correction ledger, check plans, tool, overlay, storage and Docker bindings,
  the launcher and helper copies, and the final source subject vector.

**Result:** attempt 3/3 passed all four selected Linux groups (105 child cases passed, 2
doctests ignored, Clippy exit 0 with 4 warnings, one of them new). This is technical evidence
only. Engineering acceptance, scope (D1), buffering (D2), callback reclamation (D3), ABI (D4),
allocation policy (D6), QNX, trace and qualification remain pending offline. The Claude
#1261 allowance is used up (3/3, STOP). Prior counters are unchanged. No commit, publication
or Fabro/paid run occurred. `artifact-manifest.json` seals this packet.
