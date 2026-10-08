"""Bind submission preparation and unresolved contributor obligations into the handoff."""
import base64,datetime,hashlib,json,pathlib,shutil,subprocess
P=pathlib.Path('/home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167');S=P/'submission';Q=P/'final-review';D=Q/'verification-run'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def write(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
a=S/'before-submission-status';a.mkdir(exist_ok=True)
for name in ['session-handoff.json','CURRENT-STATUS.md','README.md','RESUME-HANDOFF.md','artifact-manifest.json','session-artifact-manifest.json']:
 if not (a/name).exists():shutil.copy2(P/name,a/name)
main=load(S/'preparation-result.json')['current_upstream_main'];guide=json.loads(subprocess.check_output(['gh','api',f'repos/eclipse-score/communication/contents/CONTRIBUTING.md?ref={main}'],text=True));(S/'upstream-CONTRIBUTING.md').write_bytes(base64.b64decode(guide['content']))
write(S/'contribution-guide-binding.json',{'commit':main,'url':f'https://github.com/eclipse-score/communication/blob/{main}/CONTRIBUTING.md','sha256':sha(S/'upstream-CONTRIBUTING.md'),'same_as_measured_baseline_guide':(S/'upstream-CONTRIBUTING.md').read_bytes()==(D/'candidate/CONTRIBUTING.md').read_bytes()})
(S/'PR-TITLE.txt').write_text('test: add dedicated integration coverage for idempotent COM APIs\n')
(S/'PR-BODY.md').write_text('''Adds one LoLa integration test covering repeated `OfferService`, `StopOfferService`, `StartFindService`, `Subscribe` and `Unsubscribe` calls. It compares discovered service identity/cardinality after duplicate offers, verifies absence after each stop, checks subscribed state and rejection after each unsubscribe, and verifies sample delivery and recovery with finite deadlines. The harness requires the application to exit 0.

Repeated discovery uses the same callback and instance specifier. Each returned search operation is checked for unchanged discovered service state and stopped; distinct operation handles follow the native implementation and existing watch-sharing/callback tests. Production APIs are unchanged.

The existing copyright checker BUILD/MODULE.bazel input strings are also corrected to filesystem paths. A separate utility patch is available for independent review.

Relates to #1167.

Validation on `e3d126c2d7569345cf5f790310702eb00cd86b06` with Bazel 8.7.0 and Ubuntu 24.04.4:

- Full build and formatting pass.
- Dedicated integration/schema tests: 2/2 pass; application exits 0.
- Full suite: 503 pass, 0 fail, 6 platform/configuration targets skipped; QNX runtime was not executed.
- Copyright reports 204 findings identical to the baseline with the checker-path correction, with no added findings. The untouched baseline checker fails before scanning its label-like paths. Inherited header repair remains separate scope; no waiver is claimed.

The patch also applies cleanly to upstream `9fa5a2f6cc78dd3f756df3ec3ea9466d38ee7dfd`. That newer upstream production subject has not been executed in the local native suite; the results above belong to the explicitly pinned baseline.
''')
(S/'HUMAN-DISPOSITION.md').write_text('''# Pending authorized contributor decision

This is an uncompleted decision record, not an agent approval. Reviewed subject: staged Git tree `1d790b6182be2fed1794bb287f8f9a868bde685f`, source vector SHA-256 `ddccd8f68c44de2b6de920c42c8999189cc3d1845268d9ce6e8dbad3da860e98`. Technical recommendation and measured evidence are complete in `../final-review/TECHNICAL-REVIEW.md` and `../final-review/final-binding-verification.json`.

- [ ] Authorized person records their identity, role, decision and authenticated origin for this subject.
- [ ] Person records the disposition of the scoped tests, separate checker utility repair, inherited 204 copyright failures and 6 platform skips.
- [ ] Contributor confirms ECA account linkage and the intended commit author email; official username lookup must resolve before claiming verified ECA.

Decision: pending. Reviewer/contributor role: not asserted. Date/origin: pending. No Signed-off-by declaration or agreement signature has been supplied by the agent.

Repository rule: “Agents draft; deterministic tools measure; authorized humans accept engineering decisions.” Source: `/home/jefferson/s-core_sw_fabric/AGENTS.md`. Contribution rule: `upstream-CONTRIBUTING.md` requires signing the ECA before contribution. Account linkage lookup: `eca-lookup.json`.
''')
(S/'README.md').write_text('''# Prepared submission for communication #1167

The exact previously measured source is staged on local branch `test/1167-api-idempotency-reviewed` in the externally bound disposable workspace recorded in `preparation-result.json`. No commit, sign-off or remote publication has occurred. `source.tar.gz` independently exports all 2,885 verified files; combined/test-only/utility patches and the source hash vector are here. `PR-TITLE.txt` and `PR-BODY.md` are ready for the eventual pull request.

Authenticated GitHub account: `jnsagai`. Official Eclipse ECA lookup returned HTTP 404: no user found with that username. This does not prove that no agreement exists under another unlinked account. ECA verification remains unresolved. Log in to https://accounts.eclipse.org, link GitHub `jnsagai`, and complete/check the ECA through https://www.eclipse.org/legal/eca/. The agent cannot sign the contributor’s legal agreement or invent a human decision. The uncompleted subject-bound decision record is `HUMAN-DISPOSITION.md`.

The patch applies cleanly to current upstream `9fa5a2f6cc78dd3f756df3ec3ea9466d38ee7dfd`, which is 10 commits ahead of the measured baseline. Its changes include LoLa skeleton/event-control code. This checks patch applicability only; the 503-pass/6-skip result remains bound to the measured baseline and is not relabeled as a current-main result. `upstream-comparison.json` preserves changed-path evidence. Current contribution guide matches the measured baseline guide; exact binding is in `contribution-guide-binding.json`.

Native run `01M4878Q65ENC6PJ5AEJ6NMWB3` and the completed technical review are preserved under `../final-review/`. No new Fabro run, paid call or supervisor retry was used for submission preparation. Credentials remain internal. Dashboard: http://172.18.17.0:8787 (`fabro_dashboard`).
''')
h=load(P/'session-handoff.json');h['submission_preparation']=str(S/'preparation-result.json');h['submission_packet']=str(S);h['eca_status']='unresolved_official_lookup_404_github_jnsagai';h['eca_lookup']=str(S/'eca-lookup.json');h['task_status']='agent_review_and_submission_preparation_complete_contributor_identity_resolution_required';h['next_obligation']='Contributor links GitHub jnsagai to their Eclipse account and confirms ECA; authorized human records subject-bound engineering disposition';h['next_obligation_authority']='Native CONTRIBUTING.md requires ECA; AGENTS.md prohibits synthesizing a human decision';h['new_native_runs_for_submission_preparation']=0;h['new_paid_calls_for_submission_preparation']=0;h['time_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(P/'session-handoff.json',h)
(P/'CURRENT-STATUS.md').write_text('''# Technical review and submission preparation complete

Completed native run `01M4878Q65ENC6PJ5AEJ6NMWB3`: build, formatting, focused tests (2/2) and all 503 executed full-suite tests pass; 6 targets skipped. Copyright retains 204 baseline-identical failures, no additions. Review found/fixed the signal-exit false-positive; complete bound evidence/products remain in `final-review/`.

The exact measured source is staged in an isolated disposable branch and exported in `submission/source.tar.gz`, with final PR title/body and three patches. The patch applies cleanly to newer upstream main; this does not extend the baseline test results to that changed subject.

Official ECA lookup for authenticated GitHub login `jnsagai` returns 404 (no user found). Contributor account linkage/ECA remains unresolved; only the contributor can sign the agreement. Formal engineering disposition remains an uncompleted human-owned record in `submission/HUMAN-DISPOSITION.md`. No commit/sign-off, remote push or PR has been made. No additional native run, paid call or supervisor retry occurred.

Mobile UI: [fabro_dashboard](http://172.18.17.0:8787), service `fabro-monitor.service`, source `someip`. Verified original storage image remains bound as loop1; prior records and the optimization session are unchanged.
''')
(P/'README.md').write_text((P/'README.md').read_text()+'\nSubmission preparation: [submission packet](submission/README.md), including the staged-source archive, final PR text, clean current-main applicability check and official ECA lookup. Eclipse currently cannot resolve GitHub `jnsagai`; contributor linkage/ECA and the uncompleted human decision remain outstanding.\n')
(P/'RESUME-HANDOFF.md').write_text((P/'RESUME-HANDOFF.md').read_text()+'\n## Latest submission preparation\n\nThe user delegated the next step. See `submission/README.md` and `submission/preparation-result.json`: an isolated branch stages the exact measured subject, full source archive is hash-verified, final PR title/body and all three patches are prepared. No commits or sign-offs were created. Patch applicability to current upstream main passed with an alternate Git index; the measured baseline subject remains unchanged. Current upstream is 10 commits ahead and includes production changes, so no baseline result is claimed for that new subject. Official ECA lookup for authenticated GitHub login `jnsagai` returned HTTP 404, no user found. Contributor may have an unlinked Eclipse account; this requires their account identity/linkage, not an agent signature. Await that information and the human-owned subject disposition; recheck official ECA before any verified-ECA claim. No new paid calls, native runs, retries, remote pushes or PRs occurred. A separate input request for the existing Eclipse username was made during this preparation.\n')
write(S/'artifact-manifest.json',{'kind':'submission_preparation_inventory','files':{str(f.relative_to(S)):sha(f) for f in S.rglob('*') if f.is_file() and not f.is_symlink() and f!=S/'artifact-manifest.json'}})
print('Submission files, unresolved ECA evidence and current handoff saved')
