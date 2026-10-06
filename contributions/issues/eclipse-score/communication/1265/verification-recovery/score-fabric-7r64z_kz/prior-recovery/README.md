# Communication #1265 — assessment retained; native verification failed

The generic S-CORE Rust workflow is implemented and installed. The contribution
contains a documentation patch assessing the existing pastey0.2.3 dependency;
no Rust implementation, dependency version, API, lock or native policy changed.

Final supervised Fabro run `01M482VTQYK6T74SS0SVTPGCX4` completed with failed
lifecycle. Worker preflight passed. The exact locked download_utils1.2.2 cache
remedy passed source/SRI/payload/canonical-ID checks. Native analysis progressed
to compilation, where the pinned Ferrocene compiler required GLIBCXX_3.4.32 and GLIBC2.36/2.38/2.39
symbols unavailable on the measured GLIBC2.35 host. **Zero of three selected
tests executed**: one failed to build, two were skipped. Copyright did not run.
Verification and export stages report failure; export retains the failure evidence.

Recovery fixes are exhausted at **3/3**. The supervisor audited bound inputs and
terminal evidence. No fourth fix or further native run was attempted. The private
server stopped; native provider usage is zero and its model list is empty.

See [verification report](verification-report.json), [correction ledger](correction-ledger.json),
[raw native log](execution/logs/communication-macro-tests.log),
[patch](communication-1265.patch), and [supervisor review](supervisor-review.md).
All original175 and paused253 subjects remain byte-exact under `prior-attempt/`
and `prior-recovery/`, including their manifests. These are explicitly carried
historical evidence, not fresh tests. The new workspace was allocated after the
reboot changed the mount device; immutable sources/public caches were hash-verified,
with no queues, private state or previous build outputs imported.

Offline engineering acceptance, compiler qualification/use-case evidence,
communication adoption, unavailable QNX and full CI remain pending as recorded.
The issue is open. No publication or accepted fix is claimed. Further native work
needs a compatible build environment and a newly authorized correction budget.
