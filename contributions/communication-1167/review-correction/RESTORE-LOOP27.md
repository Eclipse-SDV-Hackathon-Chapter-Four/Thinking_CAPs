# Historical loop27 restoration instructions — superseded

Do not run this script for the current task. The latest operator clarification permits the same verified image now attached as loop1; a fresh binding has been created without remounting. See `storage-reconciliation.json` and `verification-run/`. The instructions below preserve the earlier request and authentication blocker.

The operator reconfirmed `/dev/loop27`. The original registered ext4 image is currently mounted through `/dev/loop1` at its original path. Preliminary read-only script checks passed; privileged busy checks and the backing-image UUID check remain deferred. Neither sudo nor Polkit grants noninteractive administrator access in this session. No mount, attachment, storage record, queue or original candidate was changed.

From an internal-storage terminal directory, run:

```bash
sudo /usr/bin/python3 /home/jefferson/eclipse_sdv_hackathon_2026/contributions/communication-1167/review-correction/restore-loop27.py --restore
```

Authenticate directly in the terminal. The script refuses unexpected device/image/mount identities, occupied loop27, open filesystem users, other mounts or running containers. It uses a normal unmount, never a forced/lazy unmount, and never duplicates an image attachment or reformats storage. If an intermediate command fails, it attempts to restore the prior loop1 mount only when the image remains unmounted and its prior device is available. Review any failure rather than proceeding. The script passed read-only preflight only; its privileged restoration has not run.

After restoration, the assistant must verify the exact backing image, UUIDs, source `/dev/loop27`, original mount path and stable `score_sw_fabric.storage.validate_run_root` before any native execution. Do not edit the old mount_device record. Then create a fresh bound disposable workspace and isolated corrected candidate, run all five native checks without additional model calls, export complete results and retain offline engineering acceptance as pending. The original supervisor remains exhausted at three correction attempts.
