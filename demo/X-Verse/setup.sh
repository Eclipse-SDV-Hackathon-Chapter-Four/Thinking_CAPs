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

# Run from the checkout itself, wherever it lives (e.g. Thinking_CAPs/demo/X-Verse).
AUTOVERSE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$AUTOVERSE_DIR"

usage() {
    cat <<EOF
Usage: $0 <command>
This script is for setting up the XVerse environment and repos after cloning the repo and before 'run_autoverse.py'.
- Installs system packages python3-pip, rust-just, vcstool.
- Runs 'just' command install-zenoh
- Optionally runs 'just' commands to install CARLA server and client
- Optionally runs 'just' commands to install rust language and tools.
- Optionally runs 'just' commands to setup Logitech G920 steering wheel.
- Optionally sets up cuttlefish emulator.
- Optionally prepares the ThreadX AZ3166 lighting ECU (Thinking_CAPs).
- Links ~/autoverse to this checkout when it lives elsewhere.
- Sets up each necessary sub-repo, and warns about existing component
  checkouts that are not on the branch/tag in autoverse.repos.

Options:
    --carla      Download and install CARLA server and client. Does not by default.
    --rust       Install rust language and tools. Does not by default.
    --steer      Setup Logitech G920 steering wheel. Does not by default.
    --cuttlefish Download, install, and run the cuttlefish emulator repo
    --threadx    Install the bridge dependencies (python-can, pyserial) for the
                 ThreadX AZ3166 board and add you to the dialout group.
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


## run_autoverse.py and the component scripts expect the checkout at
## ~/autoverse. When it lives elsewhere (e.g. Thinking_CAPs/demo/X-Verse),
## link it there instead of moving it.
if [[ "$AUTOVERSE_DIR" != "$HOME/autoverse" ]]; then
    if [[ ! -e "$HOME/autoverse" ]]; then
        ln -s "$AUTOVERSE_DIR" "$HOME/autoverse"
        echo "Linked ~/autoverse -> $AUTOVERSE_DIR"
    elif [[ "$(readlink -f "$HOME/autoverse")" != "$AUTOVERSE_DIR" ]]; then
        echo -e "\033[1;33m~/autoverse already exists and is another checkout; run_autoverse.py will use that one.\033[0m"
    fi
fi

## MISSING INSTALL DOCKER WITH AN ENTIRE SEPARATE SCRIPT MAYBE?





## tools and root repo
sudo apt update
sudo apt install -y curl git python3-pip
pip install --user rust-just vcstool psutil

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
    # Zenoh2CAN bridge over the board's SLCAN serial port (Thinking_CAPs/ThreadX/ctl.sh)
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
    ./ctl.sh up
popd

## zenoh bridge
pushd bridges/someip/zenoh-someip-bridge
    sudo apt-get install git-lfs
    git lfs install
    git lfs pull
    ./scripts/ctl.sh up
popd

if [ $INSTALL_CUTTLEFISH == "true" ]; then
    pushd aaos_digital_cluster/cuttlefish_emulator
        sudo apt install -y android-tools-adb
        ./ctl.sh make
    popd
fi

## Steps that need a container shell or local paths, so they are not run here.
cat <<EOF

Next steps:
- S-CORE cruise-control diagnostics (SOVD, DTC CC.LostCommunication): build
  the server once, inside the S-CORE devcontainer as root, from vecu/s-core:
      bash third_party/build-diag-gateway.sh
  and point OPENSOVD_DIR at your OpenSOVD checkout (fault profile + storage)
  before starting S-CORE, e.g.  export OPENSOVD_DIR=\$HOME/OpenSOVD
- Zenoh router: run_autoverse.py starts one in Docker (eclipse/zenoh:1.3.4)
  when nothing answers on tcp/127.0.0.1:7447.
- Start everything:  python3 run_autoverse.py --enable-camera-display --vcu-zenoh
EOF
