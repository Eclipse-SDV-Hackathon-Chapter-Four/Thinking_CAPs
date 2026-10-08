#!/usr/bin/env python3
"""Verify the retained AutoSD evidence hashes without starting runtime services."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--directory', type=Path, default=ROOT / 'artifacts/vehicle-computer')
    p.add_argument('--sources', action='store_true', help='Also compare the currently checked-out application sources')
    a = p.parse_args()
    directory = a.directory.resolve()
    failures = []
    def verify(base, entries):
        for name, expected in entries.items():
            path = (base / name).resolve()
            if not path.is_relative_to(base) or not path.is_file():
                failures.append(name + ': unavailable or outside directory')
            elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                failures.append(name + ': SHA-256 mismatch')
    entries = json.loads((directory / 'manifest.json').read_text())['files']
    verify(directory, entries)
    if a.sources:
        # Provenance records the earlier root layout; translate it to where each component lives now.
        relocated = {'AutoSD/': 'contributions/eclipse-autosd/AutoSD/', 'OpenSOVD/': 'contributions/eclipse-opensovd/OpenSOVD/',
                     'ThreadX/': 'demo/X-Verse/external_hackathon_ecus/ThreadX/'}
        sources = json.loads((directory / 'provenance.json').read_text())['source_files']
        sources = {next((new + name[len(old):] for old, new in relocated.items() if name.startswith(old)), name): sha
                   for name, sha in sources.items()}
        verify(ROOT.parents[2], sources)
    print(json.dumps({'status': 'failed' if failures else 'passed', 'artifact_files': len(entries),
                      'current_sources_checked': a.sources, 'failures': failures}, indent=2))
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
