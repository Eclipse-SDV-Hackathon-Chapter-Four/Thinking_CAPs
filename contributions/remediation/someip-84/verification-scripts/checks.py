# Copyright (c) 2026 Contributors to the Eclipse Foundation
# SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
# AI Disclosure: This scratch verification helper was generated with OpenAI Codex.
# AI portions are offered under CC0-1.0; copyrightable curation retains Apache-2.0.
# Human review pending. Assisted-by: OpenAI Codex (model revision unavailable)
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, '/home/jefferson/s-core_sw_fabric/src')
from score_sw_fabric.storage import validate_run_root

ROOT = Path(__file__).resolve().parents[2]
NATIVE = ROOT / 'native'
TASK = NATIVE / '.llm_tmp'
env = os.environ.copy()
custom = json.loads((TASK / 'environment.json').read_text())
env.update({k: v for k, v in custom.items() if k != 'PATH_PREFIX'})
env['PATH'] = custom['PATH_PREFIX'] + ':' + env['PATH']
OUT = TASK / 'evidence'
OUT.mkdir(exist_ok=True)

def run(name, argv, timeout=1200):
    validate_run_root(ROOT)
    start = time.time()
    with (OUT / (name + '.stdout')).open('w') as stdout, (OUT / (name + '.stderr')).open('w') as stderr:
        try:
            result = subprocess.run(argv, cwd=NATIVE, env=env, stdout=stdout, stderr=stderr, timeout=timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
    record = {'argv': argv, 'cwd': str(NATIVE), 'exit_code': code, 'elapsed_seconds': time.time() - start, 'source_hashes': {name: hashlib.sha256((NATIVE / name).read_bytes()).hexdigest() for name in subprocess.check_output(['git', 'diff', '--name-only'], cwd=NATIVE, text=True).splitlines()}, 'environment_overrides': custom}
    (OUT / (name + '.command.json')).write_text(json.dumps(record, indent=2) + '\n')
    print(name, code, round(record['elapsed_seconds'], 1), flush=True)
    return code

mode = sys.argv[1]
if mode == 'native':
    run('bazel-format', [str(TASK / 'bin/bazel'), '--batch', 'test', '--jobs=2', '//:format.check'])
    run('bazel-socom-unit', [str(TASK / 'bin/bazel'), '--batch', 'test', '--jobs=2', '//score/socom/test/unit:socom_test', '--nocache_test_results'])
elif mode == 'precommit':
    run('precommit-all-files', ['pre-commit', 'run', '--all-files'], 1800)
elif mode == 'baseline-control-retry':
    source = TASK / 'baseline-service-identifier.cpp'
    source.write_bytes(subprocess.check_output(['git', 'show', 'HEAD:score/socom/impl/service_identifier.cpp'], cwd=NATIVE))
    google = TASK / 'googletest'
    binary = TASK / 'baseline-regressions'
    flags = ['-std=c++17', '-Wall', '-Wextra', '-Werror', '-pthread', '-I.', '-Iscore/socom/impl', '-I' + str(google / 'googletest/include'), '-I' + str(google / 'googletest')]
    if not run('baseline-control-retry-compile', ['/usr/bin/x86_64-linux-gnu-g++-12', *flags, str(source), 'score/socom/impl/string_registry.cpp', 'score/socom/test/unit/service_identifier_tests.cpp', str(TASK / 'gcc-gtest-all.cc.o'), str(TASK / 'gcc-gtest_main.cc.o'), '-o', str(binary)], 240):
        code = run('baseline-control-retry-test', [str(binary), '--gtest_filter=ServiceInstanceIdentifierTest.KeysDifferingOnlyInMinorVersionAreDuplicates', '--gtest_output=json:' + str(OUT / 'baseline-control-tests.json')], 60)
        result = {'baseline_subject_sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'expected_failure': code == 1, 'exit_code': code, 'scope': 'Original comparator with current regression harness; candidate compilation/test remains separate.'}
        (OUT / 'baseline-control-result.json').write_text(json.dumps(result, indent=2) + '\n')
elif mode in ('focused', 'focused-clang-retry'):
    google = TASK / 'googletest'
    if not google.exists():
        code = run('googletest-acquisition', ['git', 'clone', '--depth=1', '--branch=v1.18.0', 'https://github.com/google/googletest.git', str(google)], 120)
        if code:
            sys.exit(code)
    (OUT / 'googletest-source.json').write_text(json.dumps({'url': 'https://github.com/google/googletest', 'tag': 'v1.18.0', 'commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=google, text=True).strip()}, indent=2) + '\n')
    compilers = [('gcc', '/usr/bin/x86_64-linux-gnu-g++-12'), ('clang', '/home/jefferson/.local/share/s-core-tools/llvm-19.1.7/usr/lib/llvm-19/bin/clang++')]
    if mode == 'focused-clang-retry':
        compilers = [('clang-recorded-profile', compilers[1][1])]
    for label, compiler in compilers:
        flags = ['-std=c++17', '-Wall', '-Wextra', '-Werror', '-pthread', '-I.', '-I' + str(google / 'googletest/include'), '-I' + str(google / 'googletest')]
        objects = []
        for source in ['gtest-all.cc', 'gtest_main.cc']:
            obj = TASK / (label + '-' + source + '.o')
            # Historical native packet compiles third-party GoogleTest without
            # -Werror, while retaining -Werror for the actual project sources.
            vendor_flags = [f for f in flags if f != '-Werror'] if mode == 'focused-clang-retry' else flags
            if run(label + '-' + source, [compiler, *vendor_flags, '-c', str(google / 'googletest/src' / source), '-o', str(obj)], 240):
                break
            objects.append(str(obj))
        if len(objects) != 2:
            continue
        binary = TASK / (label + '-regressions')
        if not run(label + '-compile', [compiler, *flags, 'score/socom/impl/service_identifier.cpp', 'score/socom/impl/string_registry.cpp', 'score/socom/test/unit/service_identifier_tests.cpp', *objects, '-o', str(binary)], 240):
            run(label + '-tests', [str(binary), '--gtest_output=json:' + str(OUT / (label + '-tests.json'))], 120)
