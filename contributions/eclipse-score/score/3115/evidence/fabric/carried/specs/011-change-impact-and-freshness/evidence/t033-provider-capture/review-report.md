# Offline provider capture review

The production HTTP boundary previously recorded usage but did not pin the retained
response bytes. A completed candidate envelope with altered source content and identical
usage could pass observed-ticket capture. Reasoning changes and a same-directory
substituted meter also passed the witness check. Initial regression failures and a
focused valid-content reproduction are retained in repository-checks/.

The first content test inadvertently changed a contract field as well as candidate
content. Its failure remains historical; the corrected focused reproduction changes
only valid candidate content and proves it was applied before the fix. The new response
SHA-256/size binding prevents that substitution. Witnesses also match the configured
instruction path/SHA, task and meter path, reasoning count and non-stopped meter. Multiple
observed stage tickets are refused rather than implicitly selecting the latest. Existing
capture receipts are preserved and yield a deterministic replay/order refusal.

Nineteen focused cases pass: four completed JSON/SSE cases with reported or absent
reasoning counts; ten content/digest/size/task/instruction/meter/reasoning/stop tampering
cases; one ambiguous-ticket case; two usage failures; and two truncated-result cases.
The scoped wider regression has 157 distinct checks: 156 initially passed and one lacked
SCORE_FABRO_BIN; that check passes when configured with the pinned native executable.
The latest capture-helper rerun passes all nineteen cases. Initial failures are retained.
An initial documentation check ran during replacement of local-results.json and
reported its missing link; the final check passes with the complete exported packet.

Eight exported probes use real HTTP on both loopback legs, with proxies disabled and
only a synthetic key. A test-only opener redirects the production fixed upstream URL
to the local emulator. Production endpoint configuration and provider admission are
unchanged. Three fixture candidates apply; five probes refuse capture. All original
requests/responses, altered bytes, usage, source inventories, binding summaries and
endpoint shutdown records are retained under local-cases/. Sixteen owned sockets and
their serving threads close. Eight initial probes remain under local-cases-initial/;
the current set repeats them with a byte-pinned operator export after formatting.
Both sets have closed endpoints: sixteen total synthetic requests, thirty-two closed
owned sockets, zero paid requests. No private Fabro server or agent execution is started.

Missing/inconsistent usage produces a transport refusal, retains the raw reply and
reservation, and stops continuation. Truncated structured results can have observed
accounting but cannot apply a candidate. Missing reasoning remains null. Reported
synthetic counts and derived cost bounds remain separate from null actual bills.
These records establish neither real provider tokenization/pricing nor cost savings.

Offline decisions remain unresolved: native source-to-Need impact mapping and accepted
P704 expected-set/tailoring/criteria/roles; QNX SDK dependency closure/applicability;
actual Fabro agent request/response and feedback consumption; genuine live DeepSeek
behavior; and T033/B1–B5 engineering qualification. No test or report accepts those
decisions. T032/T033 human markers and eight historical packets are preserved.

The next useful local step is a provider-disabled Fabro agent request/response and
feedback-consumption probe against a loopback emulator, using the corrected byte
bindings and preserving actual native stage identities. Review stays outside the
workflow; publication remains deferred.
