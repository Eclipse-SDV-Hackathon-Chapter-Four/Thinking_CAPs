# Source-based observations
CARLA0.9.15 `CarlaServer.cpp` binds `version` asynchronously, and `rpc/Server.h` runs
async bindings on worker threads. A timeout does not establish a stopped engine or GPU root
cause. Actual raw version RPC succeeds after startup; a freshly created Python client returns
0.9.15. Earlier reused client world/version timeouts are retained. Controlled comparison is next.
Sources: https://github.com/carla-simulator/carla/blob/0.9.15/Unreal/CarlaUE4/Plugins/Carla/Source/Carla/Server/CarlaServer.cpp
and https://github.com/carla-simulator/carla/blob/0.9.15/LibCarla/source/carla/rpc/Server.h.
GDB12 separate-symbol lookup hits an internal error; symbol-free unwind is unreliable beyond
the first sampled address. addr2line resolves that address to an Unreal tick task. No engine
stall/root cause is inferred from that limited debugger evidence.

Controlled real comparison (`contributions/shared/evidence/f009-client-comparison`): early client created before
launch still times out after a fresh client reaches server0.9.15, a real world and advancing
frames. This establishes the harness startup-client problem on this environment. All original
blocked evidence remains valid for its old client behavior; it did not establish an engine
readiness root cause. Actual map is Town10HD_Opt despite the requested startup URL.
