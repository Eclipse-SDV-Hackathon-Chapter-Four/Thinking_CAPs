# Native bounded correction and operator restart refusal

[Offline report](review-report.md) · [Measured verification](verification.json) ·
[Repository checks](validation-results.json) · [Historical preservation](preserved-subjects.json) ·
[Next P704 trial readiness](p704-trial-readiness.json)

Three actual private Fabro workflows consume six synthetic local SSE responses. Two
workflows apply a service-ID fault, collect failed evidence, transmit the exact fresh
feedback to one correction agent, restore the historical candidate and collect again.
The corrected local oracle passes while required native XML remains missing.

Nine expected refusals are retained: correction without failed checks, and four
restarted-operator refusals per corrected worker. The interruption case explicitly
injects a persisted stopped marker and exits a child with code 73; it does not claim
a crash during application or native checkpoint resume. All paths export reports and
exit without human nodes. Owned servers, endpoints and meters close. No paid request,
new model generation, native functional test or engineering acceptance occurs.
