<!-- SPDX-License-Identifier: Apache-2.0 -->

# PR #6 gateway build — findings (2026-09-22)

Target: `bazel build --config=score_diag_x86_64_linux //score/opensovd-gateway:opensovd-gateway`
on [inc_diagnostics PR #6](https://github.com/eclipse-score/inc_diagnostics/pull/6),
head `b975ed41`, worktree `upstream/inc_diagnostics-pr6`. Host: Ubuntu 26.04.1,
Bazel 8.6.0 via bazelisk.

**Result: does not build.** PR #6's own CI agrees: *Build & test on host for target
platform x86_64-linux* failed on `b975ed41` (8 Sep 2026), as did format-check and
pre-commit.

## Finding 1 — the lockfile patch exists but is never applied

`opensovd_core` is pinned at `0cb4b250`, whose `cargo-bazel-lock.json` stores checksum
`05fd3517…`. crate_universe computes `421f7ad3…` and aborts:

```
Error: Digests do not match: Current Digest("05fd35…") != Expected Digest("421f7a…")
```

`patches/opensovd-core-cargo-bazel-lock.patch` changes exactly that line to `421f7ad3…`,
and `patches/BUILD.bazel` exports it — but the `git_override` for `opensovd_core` in
`MODULE.bazel` has no `patches =` entry, so it is never applied.

**Fix (verified locally):**

```starlark
git_override(
    module_name = "opensovd_core",
    commit = "0cb4b250643164d678389385aa94b6a92bb7f0c7",
    patch_strip = 1,
    patches = ["//patches:opensovd-core-cargo-bazel-lock.patch"],
    remote = "https://github.com/eclipse-opensovd/opensovd-core.git",
)
```

With this, dependency resolution passes. Log: `bazel-build-fixed.log`.

Do **not** use `CARGO_BAZEL_REPIN=true` instead: it re-resolves the dependency set
and fails the same way as Finding 2 (`bazel-build-repin.log`).

## Finding 2 — `aws-lc-sys` build script cannot link under the hermetic GCC sysroot

After Finding 1 is fixed, the build fails in the Cargo build script of
`aws-lc-sys 0.41.0` (TLS backend pulled in by opensovd-core):

```
x86_64-unknown-linux-gnu/bin/ld: cannot find /lib64/libm.so.6
```

Cause: the S-CORE GCC toolchain sysroot's `usr/lib/libm.so` is a linker script:

```
GROUP ( /lib64/libm.so.6  AS_NEEDED ( /lib64/libmvec.so.1 ) )
```

Those absolute paths only resolve inside the sysroot. The toolchain passes
`-Wl,--sysroot=external/score_bazel_cpp_toolchains…` as a **relative** path, which does
not resolve from the build-script runner's working directory, so `ld` searches the host.
On Ubuntu 24.04+/26.04 `/lib64` contains only `ld-linux-x86-64.so.2`, so the link fails.
It would only succeed by accident on a host that has `/lib64/libm.so.6`.

Not fixed here: every fix touches PR #6 or the host (`/lib64`, needs sudo). Candidate
upstream fixes, for the PR author to choose from:

- make the sysroot flag absolute (or `%sysroot%`-relative) in the toolchain's link args
  for build-script actions;
- a crate annotation giving `aws-lc-sys` a `build_script_env` that routes its
  compiler probe to a working toolchain;
- switch opensovd-core's rustls provider from `aws-lc-rs` to `ring` for the Bazel build.

## Impact on our plan

- P3 (the "before" shot of `score-demo` demo data) is **blocked** until PR #6 builds.
- Both findings are concrete, reproducible help for the PR #6 author — worth offering in
  the comment on inc_diagnostics #16.
- Our Day-2 adapter needs a building gateway. If PR #6 still fails at the event, the
  fallback dev loop is Cargo against `opensovd-core` (whose workspace builds clean), with
  the Bazel wiring done last.
