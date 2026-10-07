# Latest additional #751 evidence

The user-authorized extra deterministic attempt is finished. [Review the latest isolated #751 candidate](additional-751/REVIEW.md). The original three attempts and prior #751 failure remain preserved. The whole-queue assessment below is historical for #751; other issue obligations remain unchanged.

# Communication bug queue recovery

Complete source-bound draft artifacts are exported for offline review. Execution success does not mean engineering acceptance or issue closure.

| Issue | Focused checks | All checks | Artifacts |
|---|---|---|---|
| #1236 | failed_or_missing | failed_or_missing_checks | [draft and evidence](results/1236/PR-DRAFT.md) |
| #751 | failed_or_missing | failed_or_missing_checks | [draft and evidence](results/751/PR-DRAFT.md) |
| #1104 | failed_or_missing | failed_or_missing_checks | [draft and evidence](results/1104/PR-DRAFT.md) |
| #1031 | passed | failed_or_missing_checks | [draft and evidence](results/1031/PR-DRAFT.md) |

The queue used stable fabric b2aa9a7 and native source 381d43dec900, bound to loop1 UUID 11c42dee-73a3-4c2b-ab42-a0440011d9e0. Native terminal run: `01M49EMYET5T45EG92X8BQ6HF2`. Original and recovery workflow inputs, responses, refused patches, cancellations, logs, databases, source, LICENSE/NOTICE and contribution guideline remain preserved. See `offline-review-index.json` for exact hashes and `phases/` for complete run history.

All paid calls remain within the audited $8.839842 upper bound under the original $10 cap, including possible unreported transport retries. This is an admission bound; actual provider billing is unknown. Further paid calls are disabled. No artifacts have been pushed or published.

Unresolved obligations include existing copyright/lint debt, failures shown above, real Config Management production integration/non-duplicated traceability and missing analyzer location semantics. QNX is unmeasured. Review and resolve these before any upstream submission; human acceptance remains outside Fabro.

## Measured results and remaining failures

All four cumulative patches pass `git apply --check --whitespace=error` against the pristine pinned source. Full builds passed for all four candidates. #1236 and #751 complete checks are explicitly carried from the final source-repair run after matching current source and log hashes. #1104 carries only the labelled completed successful analyzer/format checks; its full build/tests and failed exact extraction/copyright were remeasured. All #1031 checks are fresh in this continuation. See `phases/verification-resume/final-evidence-freshness.json`.

- #1236: full tests502 passed,6 skipped; lint regression passed, but global buildifier enforcement still finds existing lint debt.
- #751: full tests501 passed,6 skipped,1 failed. `test_parse_production_targets_filters_external` expects the earlier list order, while the implementation returns sorted, deduplicated labels. The focused suite has10 passing cases and this1 failure. The finalized source archive has1659 entries and includes `proxy_binding_factory_impl.cpp`. The three source-fix attempts are exhausted; the expected-list correction remains unperformed.
- #1104: fresh full tests502 passed,6 skipped. The bound supplemental SARIF report retains1625 findings, has0 schema errors and0 placeholder URIs, and preserves all valid URI objects through normalization. Exact `impl/...` extraction still fails in the native shell action; normalization cannot reconstruct missing analyzer paths. No causal attribution is made for finding-count differences between runs.
- #1031: fresh full tests502 passed,6 skipped. Public AoU target, visibility, isolated consumer lock and TRLC validation pass. Actual production Config Management integration and FMEA/LOBSTER non-duplication remain unmeasured.

Copyright checks fail for all candidates. Native failures remain actionable; no baseline warning or failure is waived. No additional source correction or paid model call is authorized under the exhausted repair cap. Contributor identity/ECA, QNX and offline engineering acceptance remain pending.

## Portable artifacts

Current database archives and manifests: `phases/verification-resume/exports/native-databases/`. Earlier database archives remain in `native-databases/`; source-repair history and pre-continuation results remain under `phases/`. Incomplete exact-scope databases are exported with `native_finalized=false`, not described as successful extractions. The final native run dump is `phases/verification-resume/terminal-native-dump/`.

50 actual native safety products are in `results/1031/generated-safety-products/`. The verified archive of9289 native generated products is `results/1236/native-generated-products.tar.gz` with its member manifest. Original source, licenses, contribution guideline, tool pins, full raw analyzer reports, failed/truncated model output and source-bound commands/logs remain preserved. `review-manifest.json` binds the entire recovery directory.

Loop1 is restored to the original registered image and mount path. Kernel unchecked-filesystem warning is retained in `loop1-restored-status.json`; successful scoped probes do not establish exhaustive filesystem health. Storage must remain connected; no running workspace was migrated or global tool storage changed.
