"""Prepare the exact locked public archive cache; never start a native run."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys

sys.path.insert(0, "/home/jefferson/s-core_sw_fabric/src")
from score_sw_fabric.storage import validate_run_root

SOURCE_URL = "https://bcr.bazel.build/modules/download_utils/1.2.2/source.json"
SOURCE_HASH = "c88be2bc48c98371d35665b805f307a647c98c83327345c918d9088822d77928"
ARCHIVE_URL = "https://gitlab.arm.com/bazel/download_utils/-/releases/v1.2.2/downloads/src.tar.gz"
ARCHIVE_SHA256 = "178175d89dcfa355a18d884304d342fb178c98e6f4b7f7fbe00c7d65ddf7b411"
DOWNLOAD_CACHE_HASH = "395d0c454985743cbda1943f66495e946634e23be23d86af94a368b5f547deb3"


def digest(path, algorithm):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def plain(path):
    assert path.is_absolute() and path.is_file(), str(path)
    assert not any(p.is_symlink() for p in (path, *path.parents)), str(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("payload", type=Path)
    parser.add_argument("metadata", type=Path)
    parser.add_argument("download_cache_source", type=Path)
    args = parser.parse_args()
    root = args.workspace.absolute()
    validate_run_root(root)
    for path in (args.payload, args.metadata, args.download_cache_source):
        plain(path)
    assert args.payload.stat().st_dev == root.stat().st_dev
    assert digest(args.download_cache_source, "sha256") == DOWNLOAD_CACHE_HASH
    assert digest(args.metadata, "sha256") == SOURCE_HASH
    lock = json.loads((root / "candidate/MODULE.bazel.lock").read_text())
    assert lock["registryFileHashes"][SOURCE_URL] == SOURCE_HASH
    meta = json.loads(args.metadata.read_text())
    assert meta["url"] == ARCHIVE_URL
    algorithm, encoded = meta["integrity"].split("-", 1)
    assert algorithm == "sha512"
    expected = base64.b64decode(encoded, validate=True).hex()
    assert len(expected) == 128 and digest(args.payload, algorithm) == expected
    assert digest(args.payload, "sha256") == ARCHIVE_SHA256
    # DownloadCache 8.7.0 hashes UTF-8 canonicalId with the payload KeyType.
    marker_name = "id-" + hashlib.sha512(ARCHIVE_URL.encode("utf-8")).hexdigest()
    marker = args.payload.parent / marker_name
    plain(marker)
    assert marker.stat().st_size == 0
    dest = root / "repository-cache/content_addressable/sha512" / expected
    assert not any(p.is_symlink() for p in (dest, *dest.parents))
    receipt = root / "locked-download-utils-cache-receipt.json"
    assert not receipt.exists(), "Preparation already recorded; inspect before reuse"
    validate_run_root(root)
    dest.mkdir(parents=True, exist_ok=True)
    for source, target in ((args.payload, dest / "file"), (marker, dest / marker_name)):
        if target.exists():
            plain(target)
            assert digest(source, "sha256") == digest(target, "sha256")
        else:
            temporary = target.with_name(target.name + ".rust-preparation")
            assert not temporary.exists()
            shutil.copyfile(source, temporary)
            assert digest(source, "sha256") == digest(temporary, "sha256")
            validate_run_root(root)
            os.replace(temporary, target)
    validate_run_root(root)
    assert digest(dest / "file", algorithm) == expected
    report = {
        "kind": "hash_verified_immutable_public_cache_copy",
        "source_archive": str(args.payload),
        "destination": str(dest / "file"),
        "metadata_url": SOURCE_URL,
        "metadata_sha256": SOURCE_HASH,
        "archive_hash_algorithm": algorithm,
        "archive_digest": expected,
        "archive_sha256": ARCHIVE_SHA256,
        "canonical_id": ARCHIVE_URL,
        "canonical_id_marker": marker_name,
        "marker_bytes": 0,
        "bazel_download_cache_source_sha256": DOWNLOAD_CACHE_HASH,
        "native_locks_changed": False,
        "queues_or_private_state_copied": False,
        "native_run_started": False,
    }
    receipt.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
