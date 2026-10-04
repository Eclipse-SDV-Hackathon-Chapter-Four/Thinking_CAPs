#!/bin/bash
set -e

if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo ""
    echo "============================================"
    echo " run_apk.sh — HELP"
    echo "============================================"
    echo "This script runs inside the Docker container."
    echo "It:"
    echo " 1. Starts the Android emulator"
    echo " 2. Installs the APK"
    echo " 3. Launches the APK"
    echo " 4. Waits for app boot"
    echo ""
    echo "ARGUMENTS:"
    echo "  $1 = APK filename"
    echo "  $2 = package name"
    echo ""
    echo "Example:"
    echo "  /opt/run_apk.sh myApp.apk com.example.myapp"
    echo ""
    exit 0
fi

APK_FILENAME="$1"
PACKAGE_NAME="$2"
AVD_NAME=${AVD_NAME:-pixel_tablet_api34}

EMULATOR_REGISTER_TIMEOUT=300   # 5 minutes max
EMULATOR_BOOT_TIMEOUT=300       # 5 minutes max
APK_BOOT_TIMEOUT=120            # 2 minute max

if [ -z "$APK_FILENAME" ]; then
    echo "❌ No APK filename provided to run_apk.sh!"
    echo ""
    exit 1
fi

if [ -z "$PACKAGE_NAME" ]; then
    echo "❌ No package name provided to run_apk.sh!"
    echo ""
    exit 1
fi

APK_PATH="/apk/$APK_FILENAME"

echo "=== run_apk.sh parameters ==="
echo "APK: $APK_PATH"
echo "Package: $PACKAGE_NAME"
echo "AVD: $AVD_NAME"
echo "============================="


echo ""
echo "[0] Cleaning ADB..."
adb kill-server || true
pkill -f "adb" || true
sleep 2


echo ""
echo "[1] Starting ADB server cleanly..."
adb start-server
sleep 2


echo ""
echo "[2] Checking if emulator is already running..."

# Check via adb first
RUNNING=$(adb devices | grep "emulator-" | grep -v "offline" | cut -f1)
if [ ! -z "$RUNNING" ]; then
    echo "[INFO] Emulator already running and responsive: $RUNNING"
    DEVICE=$RUNNING
    SKIP_EMULATOR_START=true
else
    # Check via process list
    if pgrep -f "qemu-system" >/dev/null; then
        echo "[WARN] Emulator process detected but not in ADB. Killing stale process..."
        pkill -9 -f "qemu-system" || true
        sleep 3
        echo "[INFO] Stale emulator killed. Will start fresh."
    fi
fi

echo ""
if [ "$SKIP_EMULATOR_START" = true ]; then
    echo "[INFO] Attaching to existing emulator…"
else
    echo "[INFO] No running emulator detected. Starting a new one…"
fi

if [ "$SKIP_EMULATOR_START" != true ]; then
    echo ""
    echo "[3] Starting emulator: $AVD_NAME"
    emulator -avd "$AVD_NAME" \
        -gpu auto \
        -no-snapshot \
        -no-snapshot-load > /tmp/emulator.log 2>&1 &
fi


echo ""
echo "[4] Giving emulator time to start service..."
sleep 5


echo ""
echo "[5] Waiting for emulator to registering up and appear in adb..."

# Wait until emulator registers as "emulator-XXXX"
DEVICE=""
for ((i=1; i<=EMULATOR_REGISTER_TIMEOUT; i++)); do
    DEVICE=$(adb devices | grep "emulator-" | cut -f1)
    if [ ! -z "$DEVICE" ]; then
        echo ""
        echo "✔ Emulator detected as $DEVICE"
        break
    fi
    if [ $(($i % 2)) == 0 ]; then
        echo "  → Emulator registering in progress ($i/$EMULATOR_REGISTER_TIMEOUT)"
    fi
    sleep 1
done

if [ -z "$DEVICE" ]; then
    echo ""
    echo "❌ Emulator registering TIMED OUT since it never appeared in adb devices."
    exit 1
fi


echo ""
echo "[6] Waiting for Emulator boot completion..."

# Boot detection:
for ((i=1; i<=EMULATOR_BOOT_TIMEOUT; i++)); do
    if [ $(($i % 2)) == 0 ]; then
        BOOT_OK=$(adb -s "$DEVICE" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')
        if [ "$BOOT_OK" == "1" ]; then
            echo ""
            echo "✔ Emulator boot completed!"
            break
        fi
        echo "  → Emulator boot in progress... ($i/$EMULATOR_BOOT_TIMEOUT)"
    fi
    sleep 1
done

if [ -z "$BOOT_OK" ]; then
    echo ""
    echo "❌ Emulator boot TIMED OUT."
    exit 1
fi


echo ""
echo "[7] Installing APK: $APK_PATH"
adb -s "$DEVICE" install -r "$APK_PATH"
sleep 3


echo ""
echo "[8] Launching app: $PACKAGE_NAME"
adb -s "$DEVICE" shell monkey -p "$PACKAGE_NAME" 1

echo "  → apk boot in progress..."


echo ""
echo "[9] Waiting for app to fully boot (UI ready)..."

for ((i=1; i<=APK_BOOT_TIMEOUT; i++)); do
    IS_APP_PROCESS_DETECTED=$(adb -s "$DEVICE" shell pidof "$PACKAGE_NAME" 2>/dev/null | tr -d '\r')

    if [ -n "$IS_APP_PROCESS_DETECTED" ]; then
        echo ""
        echo "✔ App process detected!"
        break
    fi
    if [ $(($i % 2)) == 0 ]; then
        echo "  → waiting app process... ($i/$APK_BOOT_TIMEOUT)"
    fi
    sleep 1
done

if [ -z "$IS_APP_PROCESS_DETECTED" ]; then
    echo ""
    echo "❌ App process TIMED OUT."
    exit 1
fi


echo ""
for ((i=1; i<=APK_BOOT_TIMEOUT; i++)); do
    IS_APP_UI_FULLY_DISPLAYED=$(adb -s "$DEVICE" logcat -d | grep "Displayed $PACKAGE_NAME" 2>/dev/null | tr -d '\r')

    if [ -n "$IS_APP_UI_FULLY_DISPLAYED" ]; then
        echo ""
        echo "✔ App UI is fully rendering!"
        break
    fi
    if [ $(($i % 2)) == 0 ]; then
        echo "  → waiting for UI to finish rendering... ($i/$APK_BOOT_TIMEOUT)"
    fi
    sleep 1
done

if [ -z "$IS_APP_UI_FULLY_DISPLAYED" ]; then
    echo ""
    echo "❌ App UI rendering TIMED OUT."
    exit 1
fi

echo ""
echo "✔ DONE — App launched!"
