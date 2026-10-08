# Opt-in native DFM write-through storage
Prepared 4 October 2026. Upstream base fault-lib12dac502616701734f90a61edca1326ae2ac6506.
Isolated worktree /home/jefferson/sdv-fault-lib-durability, branch hackathon/dfm-write-through.
No public PR or maintainer approval is claimed.

The selected KVS adapter updates a process-global cache without flushing. Its same-process
restart test can therefore pass while a new OS process sees no record. The new regression
fails against the unmodified adapter, retained in contributions/shared/evidence/f004-unpatched-process-restart.txt.
The patch adds new_write_through(dir,instance), preserving default new() policy. Explicit mode
flushes put/delete/clear before returning success and propagates backend errors. A failed
flush leaves the in-memory mutation intact; neither hardware nor power-loss durability is
promised. I/O runs on the storage caller thread, outside the control loop.

Only KeyNotFound means absent fault state. Other map-read errors now propagate rather than
return an empty/cleared state or overwrite a malformed catalog map. Tests cover six separate
OS-process write/read/delete/read/clear/read phases, flush-error propagation and corrupt-map
preservation. The native DFM query get_fault API returns these errors; get_all_faults upstream
still synthesizes defaults for storage errors, so this integration deliberately uses get_fault.

Validation at the pinned nightly-2025-07-14:138 DFM tests,66 native integration tests (including
real iceoryx2 IPC query/clear), one doctest passed; one upstream doctest remains ignored.
Clippy all-targets -Dwarnings passed. No pre-commit configuration is present at this pin;
Bazel/full CI is not claimed. Contribution agreement/maintainer/publication requirements
remain separate from locally prepared code.

Default diagnostic builds use pinned Git dependencies and Cargo.lock. The optional profile
uses this explicit exported patch and fault-build.lock through a private build source copy:
```sh
python3 contributions/eclipse-opensovd/OpenSOVD/scripts/build_fault_diagnostics.py --fault-source /home/jefferson/sdv-fault-lib-durability --target-dir /tmp/sdv-opensovd-research-target --output evidence/f004-fresh-build --check
```
Omit --fault-source to create an isolated pinned clone under ignored private build state and
apply the same patch. The script verifies base/diff/untracked inputs, then records hashes of
source, lock, catalog, patch and actual binary. It does not silently replace production Git
pins or compile an unpatched feature claiming durability. The optional API requires the new
constructor, so building that profile without the patch fails explicitly.
