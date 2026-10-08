"""Export an offline review index for a terminal, source-bound zero-model repair."""
import argparse,json,os,subprocess,time,tarfile
from native_measure import P,R,api,guard,hashes,sha,write

def main():
    args=argparse.ArgumentParser();args.add_argument('phase');a=args.parse_args();phase=P/'phases'/a.phase
    guard();identifier=(phase/'native-run-id').read_text().strip();summary=api('/api/v1/runs/'+identifier)
    if summary['lifecycle']['status']['kind'] not in {'succeeded','failed'}:raise ValueError('Run still active; no final review claims')
    write(phase/'terminal-native-summary.json',summary);write(phase/'terminal-native-state.json',api('/api/v1/runs/'+identifier+'/state'))
    env={**os.environ,'HOME':'/home/jefferson/.local/state/s-core/fabro/someip84-server/home','FABRO_AUTH_FILE':'/home/jefferson/.local/state/s-core/fabro/someip84-server/cli-auth.json','FABRO_SERVER':'http://127.0.0.1:43916','FABRO_NO_UPGRADE_CHECK':'true'}
    dump=phase/'terminal-native-dump'
    if not dump.exists():
        result=subprocess.run(['/home/jefferson/.local/share/s-core-tools/fabro-1b4fb152-agent32768/fabro','--json','dump','--output',str(dump),identifier],env=env,capture_output=True,text=True,timeout=120)
        (phase/'dump.stdout').write_text(result.stdout);(phase/'dump.stderr').write_text(result.stderr)
        if result.returncode:raise ValueError('Native terminal dump failed')
    archive=P/'native-source/communication-381d43dec900.tar.gz'
    native_manifest=json.loads((P/'native-source/manifest.json').read_text())
    if sha(archive)!=native_manifest['archive_sha256']:raise ValueError('Pristine baseline archive changed')
    pristine=R/'review-patch-checks'/a.phase
    if pristine.exists():raise ValueError('Review patch-check preparation already exists; inspect records before retrying')
    pristine.mkdir(parents=True)
    with tarfile.open(archive) as source:source.extractall(pristine,filter='data')
    baseline_hashes=hashes(pristine)
    from export_safety_products import export_products
    export_products(P/'results/1031/generated-safety-products')
    descriptions={
      1236:('Enforce buildifier lint diagnostics in host CI','The formatting check did not reject unused Starlark loads. Add a buildifier lint runner using the pinned native tool, fail on emitted diagnostics, and invoke it in host CI. Native positive/negative fixtures exercise a clean BUILD and an unused loaded symbol. Existing repository lint debt remains visible.'),
      751:('Extract and audit production sources in the CodeQL nightly database','The baseline nightly extraction omitted proxy_binding_factory_impl.cpp. Select configured C/C++ targets with testonly=0 from the dependency closure of the supplied production roots, including implementation_deps, and build them under tracing; audit the finalized source archive for explicitly required production files. A SARIF finding is not required for a source to be included in the database.'),
      1104:('Preserve unknown CodeQL locations without invalid file-root URIs','Some native SARIF related locations contain file:/ and a reordered artifact table contains a stale location index. Keep the complete raw report, remove invalid placeholder physical locations and artifact locations, and retain messages, IDs and explicit unknown-location metadata. Preserve valid paths. This is a bounded normalization workaround; it cannot reconstruct a file path that the analyzer did not provide.'),
      1031:('Expose the Communication AoU target to external consumers','Publish an alias for the existing AoU target, preserve its underlying native providers and safety-analysis dependency, update the public-target golden file, and document pinned tooling forwarding semantics. Test a component requirement derived from the existing AoU. Actual Config Management production integration and FMEA/LOBSTER non-duplication remain pending cross-repository review.')}
    rows=[]
    for number,(title,description) in descriptions.items():
        folder=P/'results'/str(number);result=json.loads((folder/'verify-result.json').read_text())
        expected=json.loads((folder/'candidate-hashes.json').read_text())
        if hashes(R/('issue-'+str(number)))!=expected:raise ValueError('Export subject drift: '+str(number))
        patch=folder/('communication-'+str(number)+'.patch')
        if not patch.exists():raise ValueError('Patch export missing')
        command=['git','-C',str(pristine),'-c','core.hooksPath=/dev/null','apply','--check','--whitespace=error',str(patch)]
        checked=subprocess.run(command,capture_output=True,text=True,timeout=30)
        write(folder/'pristine-patch-check.json',{'command':command,'exit_code':checked.returncode,'stdout':checked.stdout,'stderr':checked.stderr,'archive_sha256':sha(archive),'patch_sha256':sha(patch),'baseline_source_hashes':baseline_hashes,'candidate_source_manifest_sha256':sha(folder/'candidate-hashes.json'),'applied':False,'engineering_acceptance':'pending_offline_review'})
        if checked.returncode:raise ValueError('Exported patch does not apply to pristine pinned source: '+str(number))
        if hashes(pristine)!=baseline_hashes:raise ValueError('Read-only patch check changed its source')
        checks='\n'.join('- '+c.get('check','unknown')+': '+('exit '+str(c['exit_code']) if 'exit_code' in c else c.get('status','missing')) for c in result['checks'])
        scope='Exact impl/... extraction failure remains a failed check. The nightly projection is supplemental evidence. Lost analyzer paths remain unknown.' if number==1104 else ('The isolated external module checks visibility/provider and TRLC resolution only; it is not the production Config Management integration.' if number==1031 else ('Existing global buildifier lint findings are not waived or silently corrected.' if number==1236 else 'Production coverage is proven only for the measured source/archive, not every possible target or platform.'))
        text=f'# Draft: {title}\n\n{description}\n\nRelated issue: https://github.com/eclipse-score/communication/issues/{number}\n\nEach exported patch also includes the documented common root BUILD correction: pass filesystem names BUILD and MODULE.bazel to the copyright checker rather than Bazel labels. This enables the scanner without changing its policy; it still reports existing debt.\n\nOriginal Flash output is preserved in correction-response.txt. The canonical hunks, source-backed integration repairs, native formatting and bounded repair attempts have separate records; the final communication patch is cumulative.\n\nNative source baseline: `{json.loads((P/"configuration.json").read_text())["source_commit"]}`. Final execution: `{identifier}`. Engineering acceptance: pending offline review. No issue closure is claimed.\n\n## Validation\n\n{checks}\n\n{scope}\n\nCopyright/format/build/test failures are retained in `verify-result.json` and full `evidence/` logs. Before submission, a reviewer must resolve remaining failures, verify contributor/commit identity and accept the engineering/API decisions outside Fabro.\n\n## Artifacts\n\nPatch: `{patch.name}`. Changed source, exact commands, source hashes, logs, native test products and analyzer products are stored in this folder. Full databases and original source/licenses are in the recovery directory. These artifacts do not grant publishing authority.\n'
        (folder/'PR-DRAFT.md').write_text(text)
        write(folder/'artifact-manifest.json',{'files':{str(f.relative_to(folder)):sha(f) for f in folder.rglob('*') if f.is_file() and f.name!='artifact-manifest.json'}})
        rows.append({'issue':number,'status':result['status'],'targeted_checks':result['targeted_checks'],'source_sha256_manifest':sha(folder/'candidate-hashes.json'),'patch_sha256':sha(patch),'acceptance':'pending_offline_review'})
    audit=json.loads((P/'budget-audit.json').read_text());ledger=json.loads((P/'native-repair-supervisor.json').read_text())
    write(P/'offline-review-index.json',{'native_run_id':identifier,'native_terminal_state':summary['lifecycle']['status'],'source_bound':True,'issues':rows,'repair_history':ledger,'actual_provider_bill_usd':None,'all_calls_upper_usd_micros':audit['combined_upper_usd_micros'],'provider_policy':'Flash only; no further paid calls','engineering_acceptance':'pending_offline_review','published':False})
    table='\n'.join(f'| #{v["issue"]} | {v["targeted_checks"]} | {v["status"]} | [draft and evidence](results/{v["issue"]}/PR-DRAFT.md) |' for v in rows)
    (P/'REVIEW.md').write_text('# Communication bug queue recovery\n\nComplete source-bound draft artifacts are exported for offline review. Execution success does not mean engineering acceptance or issue closure.\n\n| Issue | Focused checks | All checks | Artifacts |\n|---|---|---|---|\n'+table+'\n\nThe queue used stable fabric b2aa9a7 and native source 381d43dec900, bound to loop1 UUID 11c42dee-73a3-4c2b-ab42-a0440011d9e0. Native terminal run: `'+identifier+'`. Original and recovery workflow inputs, responses, refused patches, cancellations, logs, databases, source, LICENSE/NOTICE and contribution guideline remain preserved. See `offline-review-index.json` for exact hashes and `phases/` for complete run history.\n\nAll paid calls remain within the audited $8.839842 upper bound under the original $10 cap, including possible unreported transport retries. This is an admission bound; actual provider billing is unknown. Further paid calls are disabled. No artifacts have been pushed or published.\n\nUnresolved obligations include existing copyright/lint debt, failures shown above, real Config Management production integration/non-duplicated traceability and missing analyzer location semantics. QNX is unmeasured. Review and resolve these before any upstream submission; human acceptance remains outside Fabro.\n')
    write(P/'review-manifest.json',{'files':{str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f.name!='review-manifest.json'}})
    print(json.dumps({'run_id':identifier,'issues':rows,'provider_bill':None,'engineering_acceptance':'pending_offline_review'}))
if __name__=='__main__':main()
