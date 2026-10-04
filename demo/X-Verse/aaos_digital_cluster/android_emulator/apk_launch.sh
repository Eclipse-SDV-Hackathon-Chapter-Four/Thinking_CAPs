#!/bin/bash
set -e

show_help() {
    echo ""
    echo "============================================"
    echo " apk_launch.sh — HELP"
    echo "============================================"
    echo "This script:"
    echo " 1. Scans ./apk for APK files"
    echo " 2. Lets you pick an APK by index"
    echo " 3. Extracts the package name automatically"
    echo " 4. Exports APK + PACKAGE variables"
    echo " 5. Builds & starts the Docker Android Emulator container"
    echo ""
    echo "USAGE:"
    echo "  ./apk_launch.sh"
    echo "  ./apk_launch.sh --help"
    echo ""
    exit 0
}

[[ "$1" == "-h" || "$1" == "--help" ]] && show_help

APK_DIR="./apk"
echo "=== Searching for APK files in $APK_DIR ==="

APK_FILES=($(ls $APK_DIR/*.apk 2>/dev/null || true))

echo ""
if [ ${#APK_FILES[@]} -eq 0 ]; then
    
    echo "❌ No APK files found in $APK_DIR"
    echo "Make sure to unzip your APK ZIP first:"
    echo "  unzip file.zip -d apk"
    echo ""
    exit 1
fi

if [ ${#APK_FILES[@]} -eq 1 ]; then
    APK_FILE="${APK_FILES[0]}"
    APK_BASENAME=$(basename "$APK_FILE")
    echo "Found only one APK:"
    echo "  → $APK_BASENAME"
    echo ""
    read -p "Use this APK? (y/n): " CONFIRM
    [[ "$CONFIRM" != "y" ]] && echo "Canceled." && echo "" && exit 1
else
    echo "Multiple APK files detected:"
    index=1
    for f in "${APK_FILES[@]}"; do
        echo "  [$index] $(basename "$f")"
        index=$((index + 1))
    done
    echo ""
    read -p "Select APK to launch: " CHOICE
    CHOICE=$((CHOICE - 1))
    APK_FILE="${APK_FILES[$CHOICE]}"
    APK_BASENAME=$(basename "$APK_FILE")
fi

echo ""
echo "✔ Selected APK: $APK_BASENAME"

echo ""
echo "=== Extracting package name ==="

# Use aapt to extract package name
PACKAGE=$(aapt dump badging "$APK_FILE" | grep package:\ name | awk -F"'" '{print $2}')

if [ -z "$PACKAGE" ]; then
    echo "❌ Could not extract package name via aapt"
    echo ""
    exit 1
fi

echo "✔ Package name: $PACKAGE"

echo ""
echo "==> Allowing X11 access..."
xhost +local:docker

export APK_FILENAME="$APK_BASENAME"
export PACKAGE_NAME="$PACKAGE"

echo ""
echo "==> Building container..."
docker compose build

echo ""
echo "==> Starting container..."
docker compose up -d

echo ""
echo "==> DONE! Emulator should be booting and APK launching."
echo ""

# Run and keep container alive
# docker exec -it android-emulator-tablet /bin/bash -c "/opt/run_apk.sh $APK_FILENAME $PACKAGE_NAME && bash"

# Run and show output, then detach
# docker exec android-emulator-tablet /bin/bash -c "/opt/run_apk.sh $APK_FILENAME $PACKAGE_NAME && tail -f /dev/null"
docker exec android-emulator-tablet /bin/bash -c "/opt/run_apk.sh $APK_FILENAME $PACKAGE_NAME"

echo ""
echo "==> DONE! APK is running."
echo ""
echo "==> View logs via:"
echo "    docker logs -f android-emulator-tablet"
echo ""
echo "==> Enter the already running container via:"
echo "    docker exec -it android-emulator-tablet bash"
echo ""
