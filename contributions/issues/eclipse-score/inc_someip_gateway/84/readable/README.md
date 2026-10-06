# Selected native evidence

These JSON results and six integration XML files were copied byte-for-byte from
the complete portable archive. `artifact-manifest.json` in the issue directory
pins their identities. Full command records, stdout/stderr, benchmark outputs and
flamegraphs remain in the archive.

- `evidence/compiler_diagnostics/`: GCC/Clang GoogleTest results and command outcome.
- `evidence/format_precommit/`: formatting gate result.
- `evidence/native_tests/`: native unit result.
- `evidence/native_integration/`: integration result and per-target XML.
- `evidence/native_performance/`: native profiling result.
- `reused-evidence.json`: original checks reused for the unchanged candidate.

Absolute paths inside records identify the original measurement environment.
Use the portable archive's relative layout to inspect the retained files.
