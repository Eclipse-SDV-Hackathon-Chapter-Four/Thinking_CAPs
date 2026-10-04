# README clean replay — external SSD

The corrected procedure is [fresh-workspace.md](fresh-workspace.md). Testing on
4 October 2026 uses new sources, Python environments, native outputs, simulator
installations, Android state, openDuT state and dashboard state on the external
Lexar SSD. Host prerequisites, the LLVM compiler, Cargo downloads and Docker
layers are shared. This is verification on the existing host, rather than an
empty-machine installation or independent contributor signoff.

The first clean replay passed native builds, 42 core and 46 physical checks,
33 browser checks, Android boot/APK installation, actual baseline driving,
and supervisor stop/resume. It also found two additional problems: graceful
middleware shutdown was an ambiguous collector-loss disturbance, and optional
desktop browser discovery could make Android startup fail. Both are corrected.

The subsequent replay also passed native builds, core and physical checks,
browser checks, Android installation, live vehicle telemetry and stop/resume.
The next fresh replay was stopped at the user's request on 4 October 2026.
README corrections and SSD evidence are preserved. Installation on another
computer remains unverified.
