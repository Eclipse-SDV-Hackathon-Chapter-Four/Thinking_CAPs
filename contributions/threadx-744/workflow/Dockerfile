FROM ubuntu:24.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc-14 gcc-14-multilib g++-14 cmake ninja-build git ca-certificates \
    python3 python3-venv unifdef gawk tofrodos p7zip-full \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m venv /opt/verification \
    && /opt/verification/bin/pip install --no-cache-dir gcovr==8.6 \
    && ln -s /usr/bin/gcc-14 /usr/local/bin/gcc \
    && ln -s /usr/bin/gcov-14 /usr/local/bin/gcov
ENV PATH="/opt/verification/bin:${PATH}" CC=gcc-14
ENV CTEST_PARALLEL_LEVEL=1 CTEST_REPEAT_FAIL=1 CMAKE_BUILD_PARALLEL_LEVEL=4
WORKDIR /work
