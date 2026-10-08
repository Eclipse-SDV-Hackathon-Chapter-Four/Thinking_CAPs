#!/usr/bin/env python3
"""Verify imported evidence bytes; optionally restore a portable queue copy."""

import argparse
import hashlib
import json
import shutil
from pathlib import Path, PurePosixPath


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def confined(root, relative):
    value = PurePosixPath(relative)
    if value.is_absolute() or ".." in value.parts or not relative:
        raise ValueError(f"Unsafe artifact path: {relative}")
    path = root.joinpath(*value.parts)
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"Artifact leaves packet: {relative}")
    return path


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def verify(contributions, restore=None):
    packet = contributions / "communication-bug-queue-20261006"
    inventory = load(packet / "import-source-inventory.json")
    manifest = load(packet / "import-artifact-manifest.json")["files"]
    actual = {p.relative_to(packet).as_posix() for p in packet.rglob("*")
              if p.is_file() and p.name != "import-artifact-manifest.json"}
    if actual != set(manifest):
        raise ValueError("Imported outer manifest does not cover every stored file")
    checked = {}
    for relative, expected in manifest.items():
        checked[relative] = digest(confined(packet, relative))
        if checked[relative] != expected:
            raise ValueError(f"Stored artifact mismatch: {relative}")
    blobs = {}
    for relative, expected in inventory["files"].items():
        if relative not in inventory["large_files"]:
            if checked.get(relative) != expected:
                raise ValueError(f"Imported source mismatch: {relative}")
            if confined(packet, relative).stat().st_size != inventory["file_sizes"][relative]:
                raise ValueError(f"Imported source size mismatch: {relative}")
            continue
        description = inventory["large_files"][relative]
        pointer = load(confined(packet, relative + ".parts.json"))
        if pointer != {"original": relative, **description}:
            raise ValueError(f"Large-file pointer mismatch: {relative}")
        if expected not in blobs:
            whole = hashlib.sha256()
            size = 0
            for part in description["parts"]:
                file = confined(packet, part["path"])
                if checked[part["path"]] != part["sha256"] or file.stat().st_size != part["size_bytes"]:
                    raise ValueError(f"Part mismatch: {part['path']}")
                with file.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        whole.update(chunk)
                        size += len(chunk)
            blobs[expected] = (whole.hexdigest(), size)
        if blobs[expected] != (expected, inventory["file_sizes"][relative]):
            raise ValueError(f"Reassembled archive identity mismatch: {relative}")

    sync_root = contributions / "communication-1167"
    history = sync_root / "import-history/2026-10-07-before-sync"
    sync = load(history / "sync-record.json")
    for relative, expected in sync["copied"].items():
        if digest(confined(sync_root, relative)) != expected:
            raise ValueError(f"Latest #1167 record mismatch: {relative}")
    for relative, expected in sync["preserved_before_sync"].items():
        if digest(confined(history, relative)) != expected:
            raise ValueError(f"Historical #1167 record mismatch: {relative}")

    if restore is not None:
        if restore.exists() and any(restore.iterdir()):
            raise ValueError("Restore destination must be an empty directory")
        restore.mkdir(parents=True, exist_ok=True)
        for relative in inventory["files"]:
            output = confined(restore, relative)
            output.parent.mkdir(parents=True, exist_ok=True)
            if relative in inventory["large_files"]:
                with output.open("xb") as stream:
                    for part in inventory["large_files"][relative]["parts"]:
                        with confined(packet, part["path"]).open("rb") as source:
                            shutil.copyfileobj(source, stream, 1024 * 1024)
            else:
                shutil.copyfile(confined(packet, relative), output)
            if digest(output) != inventory["files"][relative]:
                raise ValueError(f"Restored source mismatch: {relative}")

    return {
        "status": "verified",
        "scope": "Imported byte integrity; native checks not rerun; no engineering acceptance",
        "queue_source_files": len(inventory["files"]),
        "queue_source_bytes": sum(inventory["file_sizes"].values()),
        "large_file_paths": len(inventory["large_files"]),
        "unique_large_blobs": len(blobs),
        "stored_payload_files": len(manifest),
        "synced_1167_records": len(sync["copied"]),
        "preserved_1167_records": len(sync["preserved_before_sync"]),
        "restore_destination": str(restore) if restore is not None else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path,
                        default=Path(__file__).resolve().parents[3] / "contributions")
    parser.add_argument("--restore-to", type=Path,
                        help="Restore original queue files into a separate empty directory")
    args = parser.parse_args()
    try:
        result = verify(args.root.resolve(), args.restore_to)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "failed", "error": str(exc)}, indent=2))
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
