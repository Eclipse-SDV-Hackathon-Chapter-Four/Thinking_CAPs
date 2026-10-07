# Offline payload and settings findings

Implementation payload preflight is complete. Both actual native requests fit the
unchanged context guard after explicit projection. Success means reports exported;
each agent receives a deliberate local HTTP 400 refusal and produces no candidate.

| Arm | Native request bytes | Tools removed | Initial projected bytes | With explicit profile | Remaining bytes |
| --- | ---: | ---: | ---: | ---: | ---: |
| Baseline | 30,882 | 13 | 23,802 | 23,875 | 125 |
| Optimized | 27,640 | 13 | 20,560 | 20,633 | 3,367 |

Both use exact prepared source prompts and the same settings. These are serialized
request sizes, not provider tokens or whole-task savings. The baseline margin is narrow;
every future request must pass the existing meter. Dynamic worker metadata, correction,
failed-check feedback and review require their own bound stage envelopes and cannot be
assumed to fit this implementation measurement.

Native settings differ from the declared draft: `low` enables thinking under the current
[official chat contract](https://api-docs.deepseek.com/api/create-chat-completion/), while
non-thinking requires an explicit switch. The JSON output format was absent too. The
optional pinned projection now supplies `thinking.type=disabled`, `reasoning_effort=none`
and `response_format.type=json_object` together. The task already instructs JSON output,
as required by [the official JSON guide](https://api-docs.deepseek.com/guides/json_mode/).
No other provider controls, model name, source message or output ceiling change.

The [proposed profile](request-projection-proposal.json) is a draft field for future
private operator instructions. It is not a real run instruction or acceptance. Production
verification enforces its exact shape and instruction SHA; fresh loopback tests confirm
the transmitted body and meter SHA/byte count. Added profile bytes count toward limits.
Unmodified old instructions keep their previous parameters, so historical evidence is
not relabeled as non-thinking JSON behavior.

The native transport captures complete raw request bodies before the endpoint refuses
them. Projection of those exact bodies is local. Effective live response model, JSON
quality, provider tokenization/usage, cache and billing remain unobserved. Failed native
agent usage defaults do not become known zero provider usage. The endpoint has no upstream
request code and uses a synthetic key in an isolated private SQL vault, which is removed
before shutdown. Native tool refusals are installed but have no visit, since no reply can
request a tool. Tool declaration projection is exercised; tool execution is not.

Both workflows contain only start, implementation, report and exit nodes. Human review
remains offline. No SDK download or native target build is attempted. The unchanged
[scope choices](../t033-p704-admission/review-report.md) and blank owner record still
require the native check denominator, impact/work products, QNX applicability/dependency
resolution and named verification/review roles. A short `go` does not supply those facts.

Next, bind the actual measured wrapper and explicit profile into proposed implementation,
correction and review runtime envelopes. Keep execution refused while the native-owner
record remains unfilled; do not convert this local payload qualification into a paid trial.
