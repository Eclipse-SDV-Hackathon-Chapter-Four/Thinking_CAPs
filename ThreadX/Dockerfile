FROM ubuntu:22.04 AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY CMakeLists.txt ./
COPY src ./src
COPY tests/test_protocol.c ./tests/test_protocol.c
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build -j 4 && ctest --test-dir build --output-on-failure

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 can-utils python3 python3-pip ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/threadx
COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt
ARG WITH_CARLA=0
RUN if [ "$WITH_CARLA" = 1 ]; then \
    python3 -m pip install --no-cache-dir carla==0.9.15 pygame==2.6.1 numpy==2.2.6; fi
COPY --from=build /src/build/threadx-zonal-lights /usr/local/bin/threadx-zonal-lights
COPY LICENSE /usr/share/licenses/threadx-zonal-lights/LICENSE
COPY THREADX-LICENSE.txt /usr/share/licenses/threadx/LICENSE.txt
COPY scripts ./scripts
COPY tests ./tests
CMD ["threadx-zonal-lights", "--interface", "vcan0"]
