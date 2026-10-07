# Eclipse SDV Hackathon 2026 (Chapter Four) · SOVD Adapter Console (Demo Console v2.1)
# Goal: the console as a container next to the OpenSOVD gateway (demo/OpenSOVD/docker-compose.yaml).
# Host network: it reaches the Zenoh router (tcp/127.0.0.1:7447), the gateway (:7690), the CDA (:20002)
# and the ECU simulator (:8181) on localhost, and serves http://localhost:8080.
FROM python:3.12-slim
# Same Zenoh version as the autoverse router (eclipse/zenoh:1.3.4).
ARG ZENOH_VERSION=1.3.4
RUN pip install --no-cache-dir "eclipse-zenoh==${ZENOH_VERSION}"
WORKDIR /app
COPY *.py ./
COPY static/ static/
# No docker CLI inside: the console's Docker check is switched off (DOCKER_CONTAINERS empty).
ENV PYTHONUNBUFFERED=1 \
    SOVD_URL=http://127.0.0.1:7690 \
    ZENOH_CONNECT=tcp/127.0.0.1:7447 \
    DOCKER_CONTAINERS=""
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/api/config', timeout=1)"
CMD ["python", "server.py"]
