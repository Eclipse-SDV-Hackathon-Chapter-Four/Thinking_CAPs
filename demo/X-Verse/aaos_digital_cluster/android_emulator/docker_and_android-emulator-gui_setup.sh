#!/bin/bash
set -e


show_help() {
    echo ""
    echo "============================================"
    echo " DOCKER & ANDROID EMULATOR GUI SETUP — HELP"
    echo "============================================"
    echo "This script prepares Ubuntu 22.04 or WSL2 for running:"
    echo " - Docker Engine"
    echo " - Docker Compose Plugin"
    echo " - X11 GUI forwarding"
    echo " - Android SDK & Android Emulator inside Docker"
    echo ""
    echo "USAGE:"
    echo "  ./docker_and_android-emulator-gui_setup.sh"
    echo "  ./docker_and_android-emulator-gui_setup.sh --help"
    echo ""
    exit 0
}

[[ "$1" == "-h" || "$1" == "--help" ]] && show_help


echo "=== Checking internet connectivity... ==="
if ! ping -c 1 google.com > /dev/null 2>&1; then
    echo "❌ No internet connection detected. Aborting."
    exit 1
fi
echo "✔ Internet connection OK"
echo ""


echo "=== Checking APT repository health... ==="
if ! sudo apt update -y; then
    echo ""
    echo "❌ ERROR: 'apt update' failed."
    echo "This usually means a broken/expired/unsigned repository."
    echo "Fix APT sources before continuing."
    exit 1
fi
echo "✔ APT is healthy"
echo ""


### PLACEHOLDER: WSL2 DETECTION (Future usage if needed)
# if grep -qi microsoft /proc/version; then
#     echo "=== WSL2 detected ==="
#     if ls /mnt/wsl | grep -q "docker-desktop"; then
#         echo "⚠ Docker Desktop detected."
#         read -p "Install docker-ce inside WSL? (y/n): " confirm
#         if [[ "$confirm" != "y" ]]; then
#             echo "✔ Skipped docker-ce installation (using Docker Desktop backend)."
#             exit 0
#         fi
#     fi
# fi
# echo ""


echo "=== System update ==="
read -p "Proceed with system update & upgrade? (y/n): " do_update
if [[ "$do_update" == "y" ]]; then
    sudo apt update && sudo apt upgrade -y
    echo "✔ System updated"
else
    echo "✔ Skipped system update by user choice"
fi
echo ""


echo "=== Installing required dependencies ==="
deps=(ca-certificates curl gnupg lsb-release x11-xserver-utils unzip jq)

for pkg in "${deps[@]}"; do
    if dpkg -l | grep -q "^ii  $pkg"; then
        echo "✔ $pkg already installed"
    else
        echo "→ Installing $pkg ..."
        sudo apt install -y "$pkg"
    fi
done

echo "✔ All dependencies installed"
echo ""


echo "=== Docker Engine installation ==="

if command -v docker >/dev/null 2>&1; then
    echo "⚠ Docker already installed."
    read -p "Reinstall Docker CE anyway? (y/n): " reinstall
    if [[ "$reinstall" != "y" ]]; then
        echo "✔ Keeping existing Docker installation"
        SKIP_DOCKER_INSTALL=true
    fi
fi

if [[ "$SKIP_DOCKER_INSTALL" != true ]]; then
    echo "→ Adding Docker GPG key..."
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
        | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo "→ Adding Docker APT repository..."
    echo \
      "deb [arch=$(dpkg --print-architecture) \
      signed-by=/etc/apt/keyrings/docker.gpg] \
      https://download.docker.com/linux/ubuntu \
      $(. /etc/os-release && echo "$UBUNTU_CODENAME") stable" \
      | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    echo "→ Updating package list..."
    sudo apt update

    echo "→ Installing Docker..."
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    echo "→ Adding user to docker group..."
    sudo usermod -aG docker "$USER"

    echo "✔ Docker Engine installed successfully"
else
    echo "✔ Docker installation skipped"
fi
echo ""


echo "=== X11 Setup ==="

# GUARANTEE x11-xserver-utils IS INSTALLED
if ! command -v xhost >/dev/null 2>&1; then
    echo "→ xhost not detected — installing x11-xserver-utils..."
    sudo apt install -y x11-xserver-utils
fi

# DETECT DISPLAY VARIABLE
if [[ -z "$DISPLAY" ]]; then
    echo "❌ DISPLAY variable is not set."
    echo "Attempting to auto-configure DISPLAY for WSL2..."

    # Try resolving host IP
    HOST_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
    if [[ -n "$HOST_IP" ]]; then
        export DISPLAY="$HOST_IP:0"
        echo "✔ DISPLAY set to $DISPLAY"
    else
        echo "❌ Could not detect X11 host IP."
        echo "Set DISPLAY manually:"
        echo "  export DISPLAY=<your-ip>:0"
        exit 1
    fi
else
    echo "✔ DISPLAY is set to $DISPLAY"
fi

# ENABLE X11 ACCESS
echo "→ Enabling X11 access for Docker..."
xhost +local:docker || {
    echo "❌ Failed to enable X11 access via xhost."
    exit 1
}

echo "✔ X11 forwarding enabled"
echo ""


echo "=== Testing Docker... ==="

if ! docker run --rm hello-world >/dev/null 2>&1; then
    echo "❌ Docker test failed."
    echo "Check Docker permissions, service status, or Docker Desktop mode."
    exit 1
fi

echo "✔ Docker Engine working"
echo ""


echo "============================================"
echo "✔ Setup complete"
echo "============================================"
echo "NOTES:"
echo "- You may need to LOG OUT and log back in for docker group permissions."
echo "- Android Emulator can now run inside Docker."
echo "- WSL2 users: Emulator may be slower due to lack of KVM."
echo ""