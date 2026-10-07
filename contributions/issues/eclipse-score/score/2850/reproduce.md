# Reproduce and verify

Follow [the selected branch instructions](integration-20261007/reproduce.md) before the native checks below. The initial PR base is `harness`; do not apply this adapter patch directly to main or submit the independent alternative as a second contribution.

Verify the entire contribution packet without executing archived source:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 contributions/issues/eclipse-score/score/2850/verify_packet.py
```

Verify/reproduce the [native implementation](native-adapter/reproduce.md) separately.
The previous chatbot reproduction guide is retained as
[native-adapter/evidence/history/prior-reproduce.md](native-adapter/evidence/history/prior-reproduce.md).
Integrity checks do not grant engineering acceptance.
