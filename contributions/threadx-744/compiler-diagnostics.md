# Compiler and FreeRTOS configuration diagnostics

The stock FreeRTOS default build fails with GCC 14 at `tx_freertos.c:664`: `pcTaskGetName` passes `const char **` to `tx_thread_info_get`, whose name parameter is `CHAR **` unless `TX_ENABLE_CONST_NAMES` is enabled. This concerns an unchanged FreeRTOS compatibility file, outside #744's stack alignment correction.

A supported alternate configuration passed all three existing FreeRTOS tests using the same source, C99, 32-bit Linux/GNU port, GCC 14.2, and the existing validation image. `TX_ENABLE_CONST_NAMES` makes the API parameter type match the compatibility layer. The macro must be applied consistently to the kernel, layer, and tests.

The effective commands inside the validation container are:

```sh
cmake -S test/freertos/cmake -B /evidence/build/freertos-const -G Ninja \
  -DCMAKE_TOOLCHAIN_FILE=/work/cmake/linux.cmake \
  -DCMAKE_C_COMPILER=gcc-14 -DCMAKE_BUILD_TYPE=default_build \
  -DCMAKE_C_FLAGS_DEFAULT_BUILD=-DTX_ENABLE_CONST_NAMES
cmake --build /evidence/build/freertos-const --parallel 4
ctest --test-dir /evidence/build/freertos-const --output-on-failure \
  --no-tests=error --timeout 120 \
  --output-junit /evidence/diagnostics/freertos-const/test-results.xml
```

Configuration, build, and test each returned exit code 0. `txfr_queue_create_test`, `txfr_task_create_test`, and `txfr_sync_create_test` passed. These creation-path tests do not establish runtime coverage of `pcTaskGetName`; this diagnostic also establishes that the whole layer compiles with the supported const-name API configuration.

`cmake/linux.cmake` writes `CMAKE_C_FLAGS` as `CACHE INTERNAL`, replacing a direct `-DCMAKE_C_FLAGS=-DTX_ENABLE_CONST_NAMES` attempt. That ineffective first attempt was preserved in the loop4 diagnostics. The effective `CMAKE_C_FLAGS_DEFAULT_BUILD` option survives the toolchain and is present on compile commands. No warning suppression, test modification, or production source change was used.

Full logs and exact Docker command arrays are on loop4 under `evidence/diagnostics/freertos-const`; a concise manifest, configure output, CTest output, and JUnit results are mirrored under `artifacts/diagnostics/freertos-const`. The build directory is separate from active source-tree suite builds.

The upstream regression workflow selects `ubuntu-24.04` and calls `scripts/install.sh`, which installs `gcc-multilib` without naming a GCC version. It does not pin `CC` or `CMAKE_C_COMPILER`. The local validation image's `gcc` and `gcc-14` both resolve to GCC 14.2; `gcc-13` is absent. Therefore the local explicit GCC 14 default failure cannot be presented as a measurement of the current remote runner's compiler. The remote required FreeRTOS status still needs an actual PR run.

For deterministic workflow reporting, retain separate records for the stock default lane (with its actual failure) and this supported const-name lane (3/3 passing). Do not relabel this feature configuration as a stock default pass or use it to replace remote PR checks. The default compiler-profile mismatch and upstream compatibility defect need explicit disposition before asserting merge readiness.
