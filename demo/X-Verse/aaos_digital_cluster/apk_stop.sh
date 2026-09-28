#!/bin/bash
set -e

show_help() {
    echo ""
    echo "============================================"
    echo " apk_stop.sh — HELP"
    echo "============================================"
    echo "This script stops the running APK inside the emulator"
    echo "without stopping the emulator or container."
    echo ""
    echo "USAGE:"
    echo "  ./apk_stop.sh                    # Interactive APK selection"
    echo "  ./apk_stop.sh <package_name>     # Direct package name"
    echo "  ./apk_stop.sh --help             # Show this help"
    echo ""
    echo "EXAMPLES:"
    echo "  ./apk_stop.sh                                   # Select from list"
    echo "  ./apk_stop.sh com.example.digitalclusterapp     # Direct"
    echo ""
    exit 0
}

[[ "$1" == "-h" || "$1" == "--help" ]] && show_help

COMPOSE_FILE="docker-compose.yml"
APK_DIR="./apk"

# Parse container name from docker-compose.yml
echo "=== Reading container_name from $COMPOSE_FILE ==="
CONTAINER_NAME=$(grep -E 'container_name:' "$COMPOSE_FILE" | awk '{print $2}')

if [ -z "$CONTAINER_NAME" ]; then
    echo "❌ No container_name found in docker-compose.yml"
    echo ""
    exit 1
fi

echo "✔ Container name: $CONTAINER_NAME"
echo ""

# Check if package name was provided as argument
if [ -n "$1" ]; then
    PACKAGE_NAME="$1"
    echo "=== Using provided package name ==="
    echo "Package: $PACKAGE_NAME"
    echo ""
else
    # Interactive APK selection
    echo "=== Searching for APK files in $APK_DIR ==="
    APK_FILES=($(ls $APK_DIR/*.apk 2>/dev/null || true))

    echo ""
    if [ ${#APK_FILES[@]} -eq 0 ]; then
        echo "❌ No APK files found in $APK_DIR"
        echo "Make sure your APK files are in the ./apk folder"
        echo ""
        exit 1
    fi

    if [ ${#APK_FILES[@]} -eq 1 ]; then
        APK_FILE="${APK_FILES[0]}"
        APK_BASENAME=$(basename "$APK_FILE")
        echo "Found only one APK:"
        echo "  → $APK_BASENAME"
        echo ""
        read -p "Stop this APK? (y/n): " CONFIRM
        [[ "$CONFIRM" != "y" ]] && echo "Canceled." && echo "" && exit 1
    else
        echo "Multiple APK files detected:"
        index=1
        for f in "${APK_FILES[@]}"; do
            echo "  [$index] $(basename "$f")"
            index=$((index + 1))
        done
        echo ""
        read -p "Select APK to stop: " CHOICE
        CHOICE=$((CHOICE - 1))
        APK_FILE="${APK_FILES[$CHOICE]}"
        APK_BASENAME=$(basename "$APK_FILE")
    fi

    echo ""
    echo "✔ Selected APK: $APK_BASENAME"

    echo ""
    echo "=== Extracting package name ==="

    # Use aapt to extract package name
    PACKAGE_NAME=$(aapt dump badging "$APK_FILE" | grep package:\ name | awk -F"'" '{print $2}')

    if [ -z "$PACKAGE_NAME" ]; then
        echo "❌ Could not extract package name via aapt"
        echo ""
        exit 1
    fi

    echo "✔ Package name: $PACKAGE_NAME"
    echo ""
fi

# Check if container is running
echo "=== Checking if container is running ==="
if ! docker ps --format '{{.Names}}' | grep -q "^$CONTAINER_NAME$"; then
    echo "❌ Container '$CONTAINER_NAME' is not running!"
    echo ""
    exit 1
fi

echo "✔ Container is running"
echo ""

# Get emulator device ID
echo "=== Getting emulator device ID ==="
DEVICE=$(docker exec "$CONTAINER_NAME" adb devices | grep "emulator-" | cut -f1)

if [ -z "$DEVICE" ]; then
    echo "❌ No emulator found in container!"
    echo ""
    exit 1
fi

echo "✔ Emulator device: $DEVICE"
echo ""

# Check if APK is running
echo "=== Checking if APK is running ==="
PID=$(docker exec "$CONTAINER_NAME" adb -s "$DEVICE" shell pidof "$PACKAGE_NAME" 2>/dev/null | tr -d '\r')

if [ -z "$PID" ]; then
    echo "ℹ APK '$PACKAGE_NAME' is not running"
    echo ""
else
    echo "✔ APK is running (PID: $PID)"
    echo ""
    
    echo "=== Force stopping APK ==="
    docker exec "$CONTAINER_NAME" adb -s "$DEVICE" shell am force-stop "$PACKAGE_NAME"
    echo "✔ APK stopped"
    echo ""
fi

# Clear APK data and cache
echo "=== Clearing APK data and cache ==="
docker exec "$CONTAINER_NAME" adb -s "$DEVICE" shell pm clear "$PACKAGE_NAME" 2>/dev/null || echo "  (package data cleared)"
echo ""

echo "✔ APK cleanup complete!"
echo "  Emulator is still running."
echo "  Container is still running."
echo ""
echo "To launch the APK again, run:"
echo "  docker exec $CONTAINER_NAME adb -s $DEVICE shell monkey -p $PACKAGE_NAME 1"
echo ""
