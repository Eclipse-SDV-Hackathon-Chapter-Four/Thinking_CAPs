#!/usr/bin/env bash
# S32K148EVB helper: PEmicro GDB server, flash, reset and console capture.
#
#   board.sh server-start | server-stop | status
#   board.sh flash <elf>          load the image (OpenBSW test/pyTest/flash.gdb)
#   board.sh reset <elf>          reset and run (OpenBSW test/pyTest/reset.gdb)
#   board.sh console <seconds> [file]   capture the board console (OpenSDA CDC, 115200)
#
# Tools on the build volume: tools/pemicro (PEmicro GDB server 10.02 from the
# com.pemicro.debug.gdbjtag.pne update site) and the Arm GNU Toolchain 14.3.rel1.
# Needs the PEmicro OpenSDA driver (udev rule 58-pemicro.rules, libp64).
set -euo pipefail
source "$(dirname "$0")/storage.sh"

PEMICRO="$OBSW_WORKSPACE/tools/pemicro/lin"
export PATH="$OBSW_WORKSPACE/tools/arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-eabi/bin:$PATH"
DEVICE="${S32K_DEVICE:-NXP_S32K1xx_S32K148F2M0M11}"
PIDFILE="$OBSW_WORKSPACE/tmp/pegdbserver.pid"
LOG="$OBSW_WORKSPACE/tmp/pegdbserver.log"

console_port() {
  # the OpenSDA CDC port of the P&E debugger (vendor 1357)
  for tty in /dev/ttyACM*; do
    [[ -e "$tty" ]] || continue
    if udevadm info -q property -n "$tty" 2>/dev/null | grep -q "ID_VENDOR_ID=1357"; then
      echo "$tty"; return
    fi
  done
  echo "error: no OpenSDA console port found" >&2; return 1
}

server_running() { ss -ltn | grep -q "127.0.0.1:7224 "; }

case "${1:-status}" in
  server-start)
    if server_running; then echo "GDB server already running"; exit 0; fi
    (cd "$PEMICRO" && nohup ./pegdbserver_console -startserver -device="$DEVICE" > "$LOG" 2>&1 & echo $! > "$PIDFILE")
    for _ in $(seq 1 40); do server_running && break; sleep 0.5; done
    if server_running; then grep -E "OpenSDA|Device is|Server 1" "$LOG"; else cat "$LOG"; exit 1; fi
    ;;
  server-stop)
    if [[ -f "$PIDFILE" ]] && kill "$(cat "$PIDFILE")" 2>/dev/null; then echo "stopped"; fi
    rm -f "$PIDFILE"
    ;;
  status)
    server_running && echo "GDB server: running" || echo "GDB server: stopped"
    lsusb | grep -i "1357:" || echo "no OpenSDA debugger on USB"
    console_port || true
    ;;
  flash)
    server_running || "$0" server-start
    (cd "$OBSW_SRC/test/pyTest" && arm-none-eabi-gdb -batch -x flash.gdb "${2:?elf}")
    ;;
  reset)
    server_running || "$0" server-start
    (cd "$OBSW_SRC/test/pyTest" && arm-none-eabi-gdb -batch -x reset.gdb "${2:?elf}")
    ;;
  console)
    port="$(console_port)"
    out="${3:-/dev/stdout}"
    sg dialout -c "'$OBSW_VENV/bin/python' - '$port' '${2:-10}' '$out'" <<'EOF'
import sys, time, serial
port, seconds, out = sys.argv[1], float(sys.argv[2]), sys.argv[3]
with serial.Serial(port, 115200, timeout=0.2) as s, open(out, "ab") as f:
    end = time.time() + seconds
    while time.time() < end:
        data = s.read(4096)
        if data:
            f.write(data); f.flush()
EOF
    ;;
  *) echo "usage: $0 server-start|server-stop|status|flash <elf>|reset <elf>|console <s> [file]" >&2; exit 2 ;;
esac
