# Communication #1265: resumed, storage unavailable

User resumed the same supervised recovery. One of three corrections remains used;
two remain. The registered external SSD (UUID `002B-CE31`) is absent. No native
run, cache mutation, queue migration or new test result occurred during this resume.
Internal storage was measured at approximately 9.6 GiB free; analysis alone used a
fresh bound internal workspace. Existing native build work remains on the SSD.

Both historical packets passed all manifest checks: original 175 subjects and paused
253 subjects. These are **carried evidence**, not fresh native checks. The issue is
still open and the selected upstream commit remains unchanged. The latest native
run failed fetching locked download_utils 1.2.2 before any tests ran.

Pinned [Bazel 8.7.0 DownloadCache source](https://raw.githubusercontent.com/bazelbuild/bazel/8.7.0/src/main/java/com/google/devtools/build/lib/bazel/repository/cache/DownloadCache.java)
confirms SHA512 canonical-ID markers use 128 hexadecimal digits and hash the UTF-8
canonical ID with the payload key algorithm. Hashing the exact locked archive URL
reproduces the historical marker. The prepared helper verifies source, root lock,
metadata, payload SHA512 and SHA256, and marker before copying into the owned cache.
Its syntax passed; execution and physical input verification remain pending.

Reconnect the registered SSD. Validate its binding before any work. If reboot changed
the mount device, keep the old guard intact, allocate a new measured build root, and
import only independently verified immutable inputs with carried-evidence labels.
Never migrate private Fabro state or queues. Correction 2 is recorded only when the
verified cache remedy is applied and separately frozen run inputs are prepared.

Qualification, compiler AoU, communication adoption, QNX and full CI remain pending
where already recorded. Human engineering acceptance stays offline. No publication
or paid provider call is authorized. The contribution registry retains the prior
failed attempt until a complete new measured verification packet exists.
