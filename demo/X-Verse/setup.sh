#!/usr/bin/env bash

# This script is for setting up the XVerse environment and repos
# after cloning the repo and before 'run_autoverse.py'.
# by rodrigo/shima
# All commands are taken from the README of each (sub-)repo

set -euo pipefail

# Check if the script is being sourced.
if ( return 0 2>/dev/null ); then
    echo -e "\033[1;33mThis script is not meant to be sourced.\033[0m"
    exit 1
fi

INSTALL_CARLA="false"
INSTALL_RUST="false"
SETUP_STEER="false"
INSTALL_CUTTLEFISH="false"
SETUP_THREADX="false"
REBUILD_DIAG="false"
ORIG_ARGS=("$@")

# Run from the checkout itself, wherever it lives (e.g. Thinking_CAPs/demo/X-Verse).
AUTOVERSE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$AUTOVERSE_DIR"

# ~/autoverse for tools that expect the checkout there: a link to this one,
# so there is a single copy (a sync of Thinking_CAPs demo/X-Verse updates it).
# An existing ~/autoverse (checkout or link) is never touched.
if [[ "$AUTOVERSE_DIR" != "$HOME/autoverse" ]]; then
    if [[ ! -e "$HOME/autoverse" && ! -L "$HOME/autoverse" ]]; then
        ln -s "$AUTOVERSE_DIR" "$HOME/autoverse"
        echo "Linked ~/autoverse -> $AUTOVERSE_DIR"
    elif [[ "$(readlink -f "$HOME/autoverse")" != "$(readlink -f "$AUTOVERSE_DIR")" ]]; then
        echo -e "\033[1;33mNote: ~/autoverse is another checkout ($(readlink -f "$HOME/autoverse")); this setup uses $AUTOVERSE_DIR.\033[0m"
    fi
fi

usage() {
    cat <<EOF
Usage: $0 <command>
This script is for setting up the XVerse environment and repos after cloning the repo and before 'run_autoverse.py'.
- Installs host tools, Docker Engine + Compose plugin (if missing) and
  checks /dev/kvm (needed by Android Cuttlefish).
- Installs python packages rust-just, vcstool.
- Runs 'just' command install-zenoh
- Optionally runs 'just' commands to install CARLA server and client
- Optionally runs 'just' commands to install rust language and tools.
- Optionally runs 'just' commands to setup Logitech G920 steering wheel.
- Optionally sets up cuttlefish emulator.
- Optionally prepares the ThreadX AZ3166 lighting ECU (external_hackathon_ecus/ThreadX).
- Works from any checkout location (~/autoverse is not required). When the
  checkout is elsewhere (e.g. Thinking_CAPs demo/X-Verse) and ~/autoverse does
  not exist, ~/autoverse is created as a link to it, for tools that expect it.
- Sets up each necessary sub-repo, and warns about existing component
  checkouts that are not on the branch/tag in autoverse.repos.
- Builds S-CORE, including its cruise-control diagnostics server.
- Builds the OpenSOVD vECU images (external_hackathon_ecus/OpenSOVD: gateway,
  SOVD Adapter Console, CDA + ECU simulator), so its first start fits
  run_autoverse.py's start timeout.

Options:
    --carla      Download and install CARLA server and client. Does not by default.
    --rust       Install rust language and tools. Does not by default.
    --steer      Setup Logitech G920 steering wheel. Does not by default.
    --cuttlefish Download, install, and run the cuttlefish emulator repo
    --threadx    Install the bridge dependencies (python-can, pyserial) for the
                 ThreadX AZ3166 board and add you to the dialout group.
    --rebuild-diag
                 Rebuild the S-CORE cruise-control diagnostics server even if
                 it was already built.
    -h|--help    Show this message.

Examples:
    $0 --carla
    $0 --rust
EOF
    exit 0
}


while [[ $# -gt 0 ]]; do
  case "$1" in
    --carla)
        INSTALL_CARLA="true"
        shift
        ;;
    --rust)
        INSTALL_RUST="true"
        shift
        ;;
    --steer)
        SETUP_STEER="true"
        shift
        ;;
    --cuttlefish)
        INSTALL_CUTTLEFISH="true"
        shift
        ;;
    --threadx)
        SETUP_THREADX="true"
        shift
        ;;
    --rebuild-diag)
        REBUILD_DIAG="true"
        shift
        ;;
    *)
        usage
        ;;
  esac
done

## prevent fullscreen app from minimizing on focus loss
LINE_TO_ADD='export SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS=0'

# Check if the line already exists in .bashrc
if ! grep -Fxq "$LINE_TO_ADD" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# Prevent Pygame/SDL fullscreen apps from minimizing on focus loss" >> ~/.bashrc
    echo "$LINE_TO_ADD" >> ~/.bashrc
fi


## host tools (README "Install host tools")
sudo apt update
sudo apt install -y git git-lfs curl wget unzip python3-pip python3-venv \
    x11-xserver-utils xdg-utils adb ca-certificates

## Docker Engine + Compose plugin, from Docker's official Ubuntu repository
## (https://docs.docker.com/engine/install/ubuntu/)
if ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
    echo "installing Docker Engine and the Compose plugin"
    sudo install -m 0755 -d /etc/apt/keyrings
    sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
    sudo chmod a+r /etc/apt/keyrings/docker.asc
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" \
        | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
fi
# Docker usable by the normal user. A new group applies from the next login,
# so re-run this script once under that group to finish in this session.
if ! docker info >/dev/null 2>&1; then
    if ! id -nG "$USER" | tr ' ' '\n' | grep -qx docker; then
        sudo usermod -aG docker "$USER"
        echo "Added $USER to the docker group; it applies from the next login."
    fi
    if [[ -z "${AUTOVERSE_SETUP_SG:-}" ]] && getent group docker | cut -d: -f4 | tr ',' '\n' | grep -qx "$USER"; then
        echo "Continuing the setup with the docker group ..."
        export AUTOVERSE_SETUP_SG=1
        exec sg docker -c "$(printf '%q ' "$AUTOVERSE_DIR/setup.sh" "${ORIG_ARGS[@]}")"
    fi
    echo -e "\033[1;31mDocker is not usable by $USER. Check 'docker info' (is the daemon running?).\033[0m"
    exit 1
fi

## KVM for Android Cuttlefish (hardware virtualization, /dev/kvm). Cuttlefish
## runs in a privileged container, so no extra user group is needed.
if [[ ! -e /dev/kvm ]]; then
    if grep -qw vmx /proc/cpuinfo; then
        sudo modprobe kvm_intel || true
    elif grep -qw svm /proc/cpuinfo; then
        sudo modprobe kvm_amd || true
    fi
fi
if [[ ! -e /dev/kvm ]]; then
    echo -e "\033[1;31m/dev/kvm is missing: enable virtualization (VT-x/AMD-V) in the BIOS/UEFI, or nested virtualization when this is a VM. Android Cuttlefish needs it.\033[0m"
    exit 1
fi

## python tools and root repo
pip install --user rust-just vcstool psutil

## The Cuttlefish vECU moved from aaos_digital_cluster/cuttlefish_emulator to
## vecu/aaos_cuttlefish (2026-10-07). Move an existing checkout, with its
## downloaded images (several GB), instead of cloning and downloading again.
## Its container bind-mounts runtime/ from the old path, so it is removed;
## ./ctl.sh start creates it again (the APK then comes through the OTA stack).
if [[ -d aaos_digital_cluster/cuttlefish_emulator/.git && ! -e vecu/aaos_cuttlefish ]]; then
    echo "moving aaos_digital_cluster/cuttlefish_emulator to vecu/aaos_cuttlefish"
    if docker inspect cuttlefish-orchestration-cont --format '{{range .Mounts}}{{.Source}}{{"\n"}}{{end}}' 2>/dev/null \
            | grep -q "/aaos_digital_cluster/cuttlefish_emulator/"; then
        docker rm -f cuttlefish-orchestration-cont
    fi
    mkdir -p vecu
    mv aaos_digital_cluster/cuttlefish_emulator vecu/aaos_cuttlefish
    rmdir aaos_digital_cluster 2>/dev/null || true
fi

vcs import . < autoverse.repos ## DO NOT MERGE COMMENTED - temp workaround for carla 0.9.16 - manually changed, not committed

## vcs import does not switch a component that was already checked out.
## Point out the ones that are not on the manifest's branch/tag.
python3 - <<'PYEOF'
import subprocess, yaml
repos = yaml.safe_load(open("autoverse.repos"))["repositories"]
def git(path, *args):
    r = subprocess.run(["git", "-C", path, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""
for path, spec in repos.items():
    want = str(spec["version"])
    have = git(path, "branch", "--show-current") or git(path, "describe", "--tags", "--exact-match")
    if have and have != want:
        print(f"\033[1;33m{path} is on '{have}', autoverse.repos wants '{want}':\033[0m"
              f"  git -C {path} switch {want}  (or: git -C {path} checkout {want} for a tag)")
PYEOF

just install-zenoh

if [ $SETUP_THREADX == "true" ]; then
    echo "preparing the ThreadX AZ3166 lighting ECU"
    # Zenoh2CAN bridge over the board's SLCAN serial port (external_hackathon_ecus/ThreadX/ctl.sh)
    pip install --user "python-can==4.2.2" "pyserial==3.5"
    if ! id -nG "$USER" | tr ' ' '\n' | grep -qx dialout; then
        sudo usermod -aG dialout "$USER"
        echo "Added $USER to dialout (serial port access); it applies from the next login."
    fi
fi


if [ $INSTALL_CARLA == "true" ]; then
    echo "installing carla"
    just install-server || true # brute workaround - ignore error if the server is already installed
    just install-client
fi

if [ $INSTALL_RUST == "true" ]; then
    echo "installing rust"
    just install-rust
fi

if [ $SETUP_STEER == "true" ]; then
    echo "setting up steering wheel"
    just setup-g920-steer
fi

## s-core
pushd vecu/s-core
    source ./prepare.sh
    # ./clean.sh
    ./make.sh
    # Cruise-control diagnostics server (SOVD, DTC CC.LostCommunication), on
    # Eclipse inc_diagnostics. It must be built inside the devcontainer as root
    # (it patches the toolchain sysroot in root's Bazel cache); entrypoint.sh
    # starts it from cc_s-core/.local/cruise-gateway.
    if [[ "$REBUILD_DIAG" == "true" || ! -x cc_s-core/.local/cruise-gateway/cruise-control-diag ]]; then
        devcontainer_id=$(docker ps -q --filter "label=devcontainer.local_folder=$(pwd -P)" | head -n 1)
        if [[ -z "$devcontainer_id" ]]; then
            echo -e "\033[1;31mS-CORE devcontainer is not running (prepare.sh should have started it).\033[0m"
            exit 1
        fi
        docker exec -u root -w "/workspaces/$(basename "$(pwd -P)")" "$devcontainer_id" \
            bash -lc 'bash third_party/build-diag-gateway.sh'
    fi
    ./ctl.sh up
popd

## zenoh bridge
pushd bridges/someip/zenoh-someip-bridge
    sudo apt-get install git-lfs
    git lfs install
    git lfs pull
    ./scripts/ctl.sh up
popd

## OpenSOVD vECU (gateway, SOVD Adapter Console, CDA + ECU simulator): build the
## images now; run_autoverse.py starts it with ./ctl.sh up (same folder as
## run_autoverse.py uses; OPENSOVD_VECU_DIR overrides it).
pushd "${OPENSOVD_VECU_DIR:-$AUTOVERSE_DIR/external_hackathon_ecus/OpenSOVD}"
    ./ctl.sh build
popd

if [ $INSTALL_CUTTLEFISH == "true" ]; then
    pushd vecu/aaos_cuttlefish
        sudo apt install -y android-tools-adb
        ./ctl.sh make
    popd
fi

## Steps that need a container shell or local paths, so they are not run here.
cat <<EOF

Next steps:
- S-CORE diagnostics: built above; rebuild with  ./setup.sh --rebuild-diag
  Only the legacy SOVD provider (SDV_DIAG_APP=legacy) needs an OpenSOVD
  checkout:  export OPENSOVD_DIR=<path to OpenSOVD>
- Hackathon ECUs in external_hackathon_ecus/: OpenSOVD (images built above;
  run_autoverse.py starts it and opens the SOVD Adapter Console on
  http://localhost:8080), ThreadX (started when the AZ3166 board is plugged
  in; prepare with --threadx), and the v1 demo_console (run by hand).
- Zenoh router: run_autoverse.py starts one in Docker (eclipse/zenoh:1.3.4)
  when nothing answers on tcp/127.0.0.1:7447.
- Start everything:  python3 $AUTOVERSE_DIR/run_autoverse.py --enable-camera-display --vcu-zenoh
EOF
