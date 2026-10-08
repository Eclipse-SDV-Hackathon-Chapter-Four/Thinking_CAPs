# Docker Setup Guide

## Required Containers

| Container | Purpose | Image |
|-----------|---------|-------|
| **X-Verse** | S-CORE stack | Built from Dockerfile |
| **opensovd-gateway** | SOVD server | `ghcr.io/eclipse-opensovd/opensovd-gateway` |
| **Dashboard** | Web UI | Python slim |

---

## X-Verse Container

### Location

```
cc_s-core/deployment/xverse/docker_setup/
├── docker-compose.yaml
├── Dockerfile
├── entrypoint.sh
├── vsomeip.json
├── vsomeip-local.json
└── vsomeip-router.json
```

### Build and Run

```bash
cd cc_s-core/deployment/xverse/docker_setup

# Build
docker-compose build

# Run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### docker-compose.yaml Structure

```yaml
version: '3.8'
services:
  xverse:
    build: .
    network_mode: host
    volumes:
      - /tmp:/tmp           # vSomeIP sockets
      - /dev/shm:/dev/shm   # LoLa IPC
    environment:
      - VSOMEIP_CONFIGURATION=/app/vsomeip.json
    restart: unless-stopped
```

### Exposed Ports

| Port | Protocol | Service |
|------|----------|---------|
| 7700 | TCP | gatewayd (mw::com) |
| 30509 | UDP | someipd (SOME/IP) |

---

## OpenSOVD Gateway Container

### Pull Image

```bash
docker pull ghcr.io/eclipse-opensovd/opensovd-gateway:latest
```

### Run

```bash
docker run -d \
  --name opensovd-gateway \
  --network host \
  -e SOVD_URL=http://localhost:7690/sovd \
  ghcr.io/eclipse-opensovd/opensovd-gateway:latest \
  --mock
```

### With Custom Configuration

```bash
docker run -d \
  --name opensovd-gateway \
  --network host \
  -v $(pwd)/config:/config \
  ghcr.io/eclipse-opensovd/opensovd-gateway:latest \
  --url http://localhost:7690/sovd
```

---

## Dashboard Container

### Simple Python Server

```bash
# Build
docker build -t dashboard -f Dockerfile.dashboard .

# Run
docker run -d \
  --name dashboard \
  -p 8080:8080 \
  -v $(pwd)/demo/live:/app \
  dashboard
```

### Dockerfile.dashboard

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY demo/live/ .

EXPOSE 8080

CMD ["python3", "-m", "http.server", "8080"]
```

---

## Full Stack docker-compose.yaml

```yaml
version: '3.8'

services:
  xverse:
    build: ./cc_s-core/deployment/xverse/docker_setup
    network_mode: host
    volumes:
      - /tmp:/tmp
      - /dev/shm:/dev/shm

  opensovd:
    image: ghcr.io/eclipse-opensovd/opensovd-gateway:latest
    network_mode: host
    depends_on:
      - xverse
    command: ["--mock", "--url", "http://localhost:7690/sovd"]

  dashboard:
    build:
      context: .
      dockerfile: Dockerfile.dashboard
    ports:
      - "8080:8080"
    depends_on:
      - opensovd
```

### Run Full Stack

```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f
```

---

## Cleanup Commands

```bash
# Stop all containers
docker-compose down

# Remove containers
docker rm -f xverse opensovd-gateway dashboard

# Remove images
docker rmi $(docker images -q)

# Clean system
docker system prune -a
```

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs xverse

# Check ports
lsof -i :7700
lsof -i :7690

# Check network
docker network ls
```

### vSomeIP Socket Issues

```bash
# Check /tmp
ls -la /tmp/vsomeip-*

# Fix permissions
chmod 777 /tmp
```

### Shared Memory Issues

```bash
# Check /dev/shm
ls -la /dev/shm

# Increase size if needed
mount -o remount,size=256M /dev/shm
```

---

## Network Diagram

```
┌─────────────────────────────────────────────────────┐
│                  HOST NETWORK                        │
│                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │
│  │   X-Verse   │  │  OpenSOVD   │  │  Dashboard  │ │
│  │             │  │             │  │             │ │
│  │ :7700 :30509│  │    :7690    │  │    :8080    │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘ │
│         │                │                │         │
│         └────────────────┴────────────────┘         │
│                          │                          │
└──────────────────────────┼──────────────────────────┘
                           │
                     Browser :8080
```

---

*Docker setup prepared for Eclipse SDV Hackathon 2026*
