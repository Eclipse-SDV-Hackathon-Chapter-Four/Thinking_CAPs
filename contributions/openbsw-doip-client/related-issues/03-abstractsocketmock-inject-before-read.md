# Issue draft — eclipse-openbsw/openbsw (bug report)

**Title:** AbstractSocketMock::inject() before any read copies from a null pointer

**Labels:** bug

---

**Describe the bug**

`tcp::AbstractSocketMock` (`libs/bsw/cpp2ethernet/mock`) sets `_dataReadWindow = {}` in
its constructor, so the read window has no data pointer. `inject()` extends the read
window from that pointer (`span(_dataReadWindow.data(), size + n)`), and
`readImplementation()` then copies from address 0.

**Steps to reproduce the bug**

[`evidence/ReproUpstreamFindingsTest.cpp`](evidence/ReproUpstreamFindingsTest.cpp),
test `InjectBeforeAnyReadReadsFromNull`: construct the mock, `inject()` three bytes,
`readImplementation()` them.

**Expected behavior and actual behavior**

Expected: the three bytes are read. Actual: segmentation fault in `etl::mem_copy` with
source `nullptr` ([`evidence/repro-output.txt`](evidence/repro-output.txt)).

**Environment**

Ubuntu 22.04, GCC 11.4, CMake preset `tests-posix-debug`, `main` at `b0550871`.

**Additional context**

Possible fix: initialise `_dataReadWindow` as `_injectedData.subspan(0, 0)` in the
constructor. Workaround in tests: call `readImplementation(nullptr, 0)` once, which
resets both windows.
