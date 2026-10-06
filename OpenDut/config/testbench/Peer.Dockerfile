FROM ghcr.io/eclipse-opendut/opendut-edgar@sha256:3dd9a2aa082490a5c5cf2f540bbac8adcb09bad36226acef6f06f26b30f16520
RUN apt-get update && apt-get install -y --no-install-recommends iproute2 iputils-ping tcpdump jq ca-certificates && rm -rf /var/lib/apt/lists/*
COPY peer-entrypoint.sh /sdv-peer-entrypoint.sh
ENTRYPOINT ["/bin/sh", "/sdv-peer-entrypoint.sh"]
