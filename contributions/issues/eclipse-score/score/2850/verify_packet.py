#!/usr/bin/env python3

# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

"""Verify this packet offline without extracting or executing archived source."""

import hashlib
import json
from pathlib import Path, PurePosixPath
import tarfile


ROOT = Path(__file__).resolve().parent


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def contained(root, relative):
    name = PurePosixPath(relative)
    if name.is_absolute() or '..' in name.parts:
        raise ValueError(f'Unsafe path: {relative}')
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'Path leaves packet: {relative}')
    return path


def main():
    packet = json.loads((ROOT / 'artifact-manifest.json').read_text())
    for name, expected in packet['files'].items():
        if digest(contained(ROOT, name)) != expected:
            raise ValueError(f'Packet hash mismatch: {name}')
    independent = packet.get('independent_packets_not_bound', [])
    for name in independent:
        parts = PurePosixPath(name).parts
        if len(parts) != 1 or parts[0] in ('.', '..'):
            raise ValueError('Independent artifact must be one named sibling entry')
    actual_files = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob('*')
                    if p.is_file() and p.name != 'artifact-manifest.json'
                    and p.relative_to(ROOT).parts[0] not in independent}
    if actual_files != set(packet['files']):
        raise ValueError('Packet contains missing or unmanifested files')
    source = json.loads((ROOT / 'evidence/source/source-manifest.json').read_text())
    archive = ROOT / 'evidence/source/s-core-bot-source.tar.gz'
    if digest(archive) != source['archive_sha256']:
        raise ValueError('Source archive hash mismatch')
    files = {}
    with tarfile.open(archive, 'r:gz') as bundle:
        seen = set()
        for member in bundle:
            contained(ROOT, member.name)
            if member.name in seen:
                raise ValueError(f'Duplicate archive entry: {member.name}')
            seen.add(member.name)
            if member.isfile():
                with bundle.extractfile(member) as stream:
                    files[member.name] = hashlib.file_digest(stream, 'sha256').hexdigest()
            elif not member.isdir():
                raise ValueError(f'Unsupported archive entry: {member.name}')
    if files != source['files']:
        raise ValueError('Source archive contents do not match source manifest')
    historical = ROOT / 'evidence/historical/local-release-1.0.0'
    original = json.loads((historical / 'release-manifest.json').read_text())
    for item in original['items']:
        path = contained(historical, item['path'])
        if digest(path) != item['sha256'] or path.stat().st_size != item['size']:
            raise ValueError(f'Historical release mismatch: {item["path"]}')
    print(f'Verified {len(packet["files"])} packet files, {len(files)} source files, '
          f'{len(original["items"])} original release artifacts.')
    print('Integrity only; tests not rerun; upstream acceptance not evaluated.')


if __name__ == '__main__':
    main()
