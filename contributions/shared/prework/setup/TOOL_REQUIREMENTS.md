# Tool Requirements - Prerequisites

## Required Tools

### Development Tools

| Tool | Version | Purpose | Install Command |
|------|---------|---------|-----------------|
| **Rust** | 1.88+ | Build OpenSOVD, CDA | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| **Cargo** | Latest | Rust package manager | Comes with Rust |
| **Git** | 2.40+ | Version control | `brew install git` |
| **Docker** | 24.0+ | Containers | `brew install --cask docker` |
| **Docker Compose** | 2.20+ | Multi-container | Comes with Docker |

### Build Tools

| Tool | Version | Purpose | Install Command |
|------|---------|---------|-----------------|
| **Bazel** | 7.0+ | S-CORE build | `brew install bazel` |
| **CMake** | 3.25+ | C++ build | `brew install cmake` |
| **Python** | 3.11+ | Scripts, server | `brew install python@3.11` |
| **Node.js** | 18+ | Dashboard (optional) | `brew install node` |

### Verification Commands

```bash
# Check Rust
rustc --version    # Should show 1.88+
cargo --version

# Check Docker
docker --version   # Should show 24.0+
docker compose version

# Check Bazel
bazel --version    # Should show 7.0+

# Check Python
python3 --version  # Should show 3.11+
```

---

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | macOS 13+ / Ubuntu 22.04 | macOS 14 / Ubuntu 24.04 |
| **RAM** | 8 GB | 16 GB |
| **Disk** | 20 GB free | 50 GB free |
| **CPU** | 4 cores | 8+ cores |

---

## Rust Toolchain Setup

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add nightly (for opensovd-core)
rustup install nightly-2026-05-07
rustup default stable

# Add targets
rustup target add x86_64-unknown-linux-gnu
rustup target add aarch64-unknown-linux-gnu

# Install components
rustup component add clippy rustfmt
```

---

## Docker Setup

```bash
# Start Docker daemon
open -a Docker

# Verify
docker ps

# Pull required images
docker pull ghcr.io/eclipse-opensovd/opensovd-gateway:latest
docker pull rust:1.88
docker pull python:3.11-slim
```

---

## Repository Clones (Day 1)

```bash
# Create workspace
mkdir -p ~/hackathon && cd ~/hackathon

# Clone repositories
git clone https://github.com/eclipse-opensovd/opensovd-core
git clone https://github.com/eclipse-opensovd/classic-diagnostic-adapter
git clone https://github.com/eclipse-score/inc_diagnostics

# Verify clones
ls -la
```

---

## Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc

export RUST_BACKTRACE=1
export CARGO_NET_GIT_FETCH_WITH_CLI=true

# For opensovd-core nightly
export RUSTUP_TOOLCHAIN=nightly-2026-05-07
```

---

## VS Code Extensions (Recommended)

| Extension | Purpose |
|-----------|---------|
| rust-analyzer | Rust IDE support |
| CodeLLDB | Rust debugging |
| Docker | Docker support |
| GitLens | Git visualization |
| Markdown All in One | MD editing |

---

## Network Requirements

| Port | Protocol | Purpose |
|------|----------|---------|
| 7690 | TCP | OpenSOVD REST API |
| 7700 | TCP | mw::com gateway |
| 8080 | TCP | Dashboard |
| 30509 | UDP | SOME/IP |

```bash
# Check ports are free
lsof -i :7690
lsof -i :7700
lsof -i :8080
```

---

## Pre-Hackathon Checklist

- [ ] Rust 1.88+ installed
- [ ] Docker running
- [ ] Bazel installed
- [ ] Python 3.11+ installed
- [ ] Git configured
- [ ] GitHub account ready
- [ ] Repositories cloned
- [ ] Docker images pulled
- [ ] VS Code set up

---

*Requirements prepared for Eclipse SDV Hackathon 2026*
