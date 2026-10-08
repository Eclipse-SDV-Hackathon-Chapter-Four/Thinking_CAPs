# Delegated review found and corrected harness false-positive

The user asked the agent to perform the review and clarified that the UI is `fabro_dashboard`. Its current same-Wi-Fi URL is http://172.18.17.0:8787; the read-only dashboard already serves the dedicated Fabro source and prior run.

Source review found the native process wrapper accepts 137/143 as successful exits by default. The new isolated candidate in `final-review/verification-run/candidate/` asserts application.ret_code == 0 after the process context exits. Eight isolated before/after cases reproduce and reject the two signal false-positives; these fixtures do not replace native checks.

Fabro `01M4878Q65ENC6PJ5AEJ6NMWB3` is rerunning all five required commands with fresh tests. The owned disposable build workspace/cache is reused only after the predecessor terminated. Prior portable candidate, measurements, products and source hashes remain unchanged. Old original scratch/loop27 records and the other optimization session remain unchanged.

No additional paid model calls or supervisor retries. Agent review will propose technical/copyright dispositions; human engineering acceptance, ECA and publication remain pending.
