# F001 data model

Audit manifest schema_version=1 identifies preparation mode, wall observation timestamp,
repository name/path/revision/dirty paths/diff hashes, selected file digests and tool/image identities.
Runtime results hold check ID, status (passed/failed/blocked/skipped), reason and command evidence.
Overall failed dominates blocked, blocked dominates skipped, and passed requires every mandatory check.
No report equates available binaries with an operating vehicle.
