# Claude handoff prompt

Paste the text below into Claude Code running on this computer with filesystem and shell access. A Claude chat without local tool access will need the referenced handoff and reports attached; do not claim to have inspected unavailable files.

---

You are taking over an Eclipse S-CORE communication bug contribution queue from Codex. Continue from the verified artifacts rather than reconstructing or restarting the work. Start in `/home/jefferson/s-core_sw_fabric`.

My goal is to prepare useful, reviewable fixes for suitable bugs in `eclipse-score/communication` using the non-optimized stable `s-core_sw_fabric`, following the native CONTRIBUTING guide. The selected queue contains issues #1236, #751, #1104 and #1031. Store all contribution artifacts under:

`/home/jefferson/eclipse_sdv_hackathon_2026/contributions`

The queue directory is:

`/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-bug-queue-20261006`

Use the following as your starting record, verified through 2026-10-07. Recheck current state and relevant subject hashes before relying on carried evidence.

## Read first

1. `/home/jefferson/s-core_sw_fabric/AGENTS.md`, `.specify/memory/constitution.md`, `docs/handoff/000-to-001.md` and relevant active spec `specs/011-change-impact-and-freshness/`. Historical planning stops have later task-specific authority; this task does not authorize unrelated fabric development.
2. `<queue>/recovery-1/RESUME.md` — current verified handoff.
3. `<queue>/state.json` and `<queue>/recovery-1/offline-followup/REVIEW-CHECKLIST-20261007.md` — queue state, remaining decisions and evidence gaps.
4. `<queue>/recovery-1/additional-751/REVIEW.md` and `offline-review-index.json` — latest #751 result.
5. `<queue>/recovery-1/REVIEW.md` and `offline-review-index.json` — whole-queue evidence. Their original #751 results are historical; the additional-751 package supersedes them for the latest candidate. Preserve the old failure record.
6. `<queue>/recovery-1/submission-obligations.md` and `native-source/CONTRIBUTING.md` — pinned contribution guideline and pending obligations.
7. Configuration, authority, repair ledgers, `frozen-inputs.json`, phase controls and `review-manifest.json` before any execution or evidence update.

Here `<queue>` means the full queue directory above. Read bounded relevant sections and summarize findings; keep complete raw reports outside conversation context. Resolve any missing path from the preserved manifests rather than inventing it.

## Current progress

Queue state: `finished_review_pending`. Execution and exports completed; no bug has human engineering acceptance or a verified issue closure.

All four latest candidates have successful Linux full builds and full test results of 502 passed, 6 skipped. These are historical measurements bound to exact source and tool hashes, not fresh checks merely because you read them today. Individual focused checks and overall readiness differ:

| Issue | Completed evidence | Remaining problem |
|---|---|---|
| #751 — CodeQL ignores production sources | Latest isolated candidate: 11 regression cases pass, required `proxy_binding_factory_impl.cpp` is extracted, CodeQL database finalized, formatting/build/full tests pass; cumulative patch passes pristine-baseline applicability | Copyright check fails; full query-analysis/SARIF phase for this candidate and QNX execution are unmeasured; external dependency coverage needs review |
| #1236 — buildifier enforcement | Regression and full build/tests pass | Global enforcement reports 27 warnings whose affected source bytes match the pristine baseline; the failure is not waived |
| #1104 — missing CodeQL locations | Full build/tests pass; supplemental SARIF retains 1,625 findings with zero schema errors and zero placeholder URIs | Exact implementation extraction fails in external `rules_build_error+/lang/private/script/try_build.bash`; missing locations and the precise invocation mechanism remain unresolved |
| #1031 — AoU traceability/visibility | AoU, visibility, separate-consumer lock, TRLC and full build/tests pass; native safety products exported | Real production Config Management integration and FMEA/LOBSTER non-duplication remain unmeasured |

For #751, all 204 copyright diagnostic subjects match pristine source bytes; none names a changed path. Counts: 96 missing headers, 107 wrong format, 1 duplicate. See `recovery-1/offline-followup/751-copyright-subject-review.json`. This is source comparison, not a pristine-baseline analyzer rerun, accepted deviation or permission to suppress the scanner.

The latest #751 CodeQL source archive has 1,658 entries versus 1,659 previously. Explicit path projection identifies one absent external `score_baselibs+/score/mw/log/detail/thread_local_guard.cpp`; no candidate source members were removed, added or changed in that comparison. Cause and complete external dependency coverage are unproven. Preserve the exact member paths, hashes and comparison limits. Do not claim that one named-source audit proves every production source is covered.

The cumulative patches include a shared root BUILD copyright scanner-input correction. Review its contribution scope; removing it would change the verified subject and invalidate affected evidence. Do not backdate headers or change copyright policy to clear baseline failures.

## Authority and limits — preserve these exactly

- Original automated queue model constraint: **DeepSeek Flash only**, registered model `deepseek-flash`, reasoning effort `medium`. Claude is the interactive handoff assistant; this does not authorize changing paid Fabro model stages or adding Claude API calls.
- Total paid queue cap remains **$10**. The conservative audited upper bound is **$8.839842**; actual provider billing is unknown. Earlier historical reservations remain preserved. Further paid calls are disabled; do not reset ledgers or treat the difference as available spending authority.
- Original deterministic source-fix limit is exhausted: **3/3** attempts in `recovery-1/native-repair-supervisor.json`.
- The user separately authorized **one extra deterministic expected-order correction for #751**, with zero paid calls. It is complete and exhausted: **1/1** in `recovery-1/additional-751/repair-ledger.json`. The correction changed only the test's expected sorted-label order, in an isolated copy. Original candidate and failed 501-pass/1-fail evidence remain preserved.
- No further source correction is authorized. Do not reinterpret this handoff as an extra retry. If a correction is needed, first prepare a concrete issue-scoped proposal and request an explicit new limit before applying it.
- No queue push, PR publication, merge, release, deployment, issue closure or automatic acceptance is authorized. Earlier publishing authority belonged to a separate #1167 contribution and does not apply to this queue.
- Human engineering review stays offline, outside Fabro. Do not invent acceptance, reviewer identity or signed decisions, and do not introduce human/wait-for-approval workflow nodes.
- Contributor account supplied by the user: `jnascimento6p0`. Commit identity/ECA and engineering acceptance remain unverified.
- Read-only diagnosis and review-artifact preparation may proceed without repeated permission requests. Preserve original evidence and history. Any evidence refresh must stay within existing authority, use pinned native tools, bind exact subjects and retain failures; do not spend money or use it as a hidden source-fix retry.

## Stable baseline and storage

- Stable fabric commit: `b2aa9a7a49a054621f38e59f3aef6d6e5daf3cce`. Another session has worked on optimization; do not use its evolving checkout as the execution baseline or modify its work.
- Native communication baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
- Frozen fabric copy:
  `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-3fhaccha/fabric`
- Original disposable recovery workspace:
  `/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-communication-bug-recovery-fw8j963z`
- Latest #751 source tree is `additional-751/issue-751` beneath that recovery workspace. Other original candidates are `issue-1236`, `issue-1031`, `issue-1104`; old `issue-751` must remain unchanged.
- Use **loop1**, formerly called loop27, backed by the existing Lexar image:
  `/media/jefferson/Lexar/.s-core-build/build-volume-v1.ext4`
  Mounted ext4 UUID: `11c42dee-73a3-4c2b-ab42-a0440011d9e0`.
- Verify current mount, writable state, UUID, backing image, source/control/tool hashes and registered storage binding before execution. Stop on disconnection; do not silently relocate work, reformat disks, migrate queues or change global tool storage. Use the existing `score_sw_fabric.storage`/`score-fabric storage` mechanisms.
- Credentials and private server state stay on internal storage. Never print tokens or copy credentials into contribution artifacts.
- A kernel unchecked-filesystem warning is recorded; scoped capability probes passed, but exhaustive filesystem health is not established. No new filesystem repair is authorized by this handoff.
- Reference repositories are read-only. Native builds use owned disposable copies, with hooks inspected first. All existing native build caches are retained.

Exact tool/image pins and measured commands are in `recovery-1/configuration.json` and native evidence records. Do not substitute a remembered CLI example or an unverified executable.

## Fabro and artifacts

Latest #751 run: `01M49GDJJ4DN4GV2Q07RQF4WRX` — terminal succeeded/completed, zero model tokens. Its overall native check status remains `failed_or_missing_checks` because copyright failed. Do not try to resume this terminal run or equate Fabro success with acceptance.

Previous verification/export continuation: `01M49EMYET5T45EG92X8BQ6HF2`. All prior repair, cancelled and refused-output records remain under `recovery-1/phases/`.

Latest #751 patch and PR draft:
- `recovery-1/additional-751/results/751/communication-751.patch`
- `recovery-1/additional-751/results/751/PR-DRAFT.md`

Full native evidence and terminal dump:
- `recovery-1/additional-751/results/751/evidence/`
- `recovery-1/phases/additional-751/terminal-native-dump/`

The latest database archive has all 944 regular members verified. The generated engineering-product archive has all 9,289 members verified. Their manifests and verification receipts are in the additional-751 package. Original source, LICENSE/NOTICE, native guidelines, other candidates' databases, safety products, raw analyzer reports and failed model output remain preserved.

Fabro dashboard phone URL, last verified on the same Wi-Fi:
`http://192.168.13.204:8787`

Native API endpoint: `http://127.0.0.1:43916`, routes under `/api/v1/runs/`. Revalidate service and network address if needed; neither is an authoritative engineering record. Preserve private authentication state.

## First action and expected output

Read and verify the concise handoff, queue state and relevant manifest bindings. Then give me a short assessment of what is already verified, what can be diagnosed without new source changes or paid calls, and the most useful next action. Prioritize #751's remaining coverage/analysis limits and #1104's extraction failure using existing bound evidence. Carry existing checks only after matching their exact subject hashes and label them as carried evidence; rerun relevant checks if an authorized subject changes.

Continue useful diagnosis and artifact preparation within the limits above. Keep me informed, but do not repeatedly ask permission for read-only work. Where a new repair, spend or publication would exceed authority, prepare a concrete reviewable proposal first and explain the exact exhausted limit.

Preserve and update a concise handoff when stopping. End repository-related final responses with:

`Next step: <concrete action or none>`

`Recommended model: <exact available model and brief task-specific reason>`

Naming a recommended model does not switch a session or authorize a paid call. If local access or a required binding cannot be verified, say exactly what is missing; do not invent execution or acceptance.
