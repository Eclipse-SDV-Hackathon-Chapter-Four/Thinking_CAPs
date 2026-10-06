# F002 local observation contract v1

Fields: schema_version=1, source_instance, source_session, boot_id, clock_domain=linux-clock-monotonic,
observed_at_monotonic_ns, received_at_monotonic_ns (speed only, nullable),
last_accepted_at_monotonic_ns (speed only, nullable), vehicle_speed nullable km/h,
target_speed km/h, cc_state engaged/disengaged, software_identity explicit configured build label.
Transport does not provide protected sequence/sample ID: sample_id=null; integrity_result=not_available.

Validate bounded JSON, exact schema, known source/session/boot/clock, no future timestamps,
finite nonnegative speed/target, receipt >= acceptance, heartbeat >= receipt, ordered session timestamps.
Derived view records separate receiver availability and speed freshness, receipt/acceptance age,
and configured thresholds. Collector loss invalidates live health even if cached values remain.
Unknown states stay unknown; timeout never mutates cc_state. Restart resets available observation.
