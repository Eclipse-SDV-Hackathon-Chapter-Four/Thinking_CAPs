#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# One demo run: drives path A (S-CORE app -> our adapter -> OpenSOVD gateway)
# and path B (ECU simulator -> DoIP -> CDA), compares every observed value with
# the value expected before the run, and writes the evidence.
#
# Path A follows whatever the gateway serves: the HVAC example (12 assertions)
# or the cruise control with the stand-in app (13 assertions, DEMO=cruise).
#
# Needs: the CDA stack (demo/start.sh) and the gateway on :7690.
# Exit code: 0 only if every assertion passed.

set -uo pipefail

GATEWAY=${GATEWAY:-http://127.0.0.1:7690/sovd/v1}
CDA=${CDA:-http://127.0.0.1:20002/vehicle/v15}
SIM=${SIM:-http://127.0.0.1:8181}
ECU=${ECU:-flxc1000}
DTC=${DTC:-01E240}
DTC_MASK=${DTC_MASK:-2F}
DEBOUNCE_TIMEOUT_S=${DEBOUNCE_TIMEOUT_S:-15}

ROOT=$(cd "$(dirname "$0")/.." && pwd)
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
OUT=${OUT:-$ROOT/evidence/runs/$RUN_ID}
mkdir -p "$OUT/raw"

HVAC="$GATEWAY/components/hvac/data"
CRUISE="$GATEWAY/components/cruise/data"
T0=$(date +%s.%N)
FAILS=0
ROWS=()

since() { printf '%.3f' "$(echo "$(date +%s.%N) - $T0" | bc)"; }
log() { printf '[T+%ss] %s\n' "$(since)" "$*" | tee -a "$OUT/timeline.log"; }

# assert <path> <name> <expected> <observed>
assert() {
    local verdict=PASS
    [[ "$3" == "$4" ]] || { verdict=FAIL; FAILS=$((FAILS + 1)); }
    ROWS+=("$1|$2|$3|$4|$verdict")
    log "$verdict  [$1] $2: expected=$3 observed=$4"
}

# save <name> <curl args...>: GET/PUT and keep the raw body
save() {
    local name=$1
    shift
    curl -s "$@" > "$OUT/raw/$name.json"
    cat "$OUT/raw/$name.json"
}

cda_token() {
    curl -s -X POST "$CDA/authorize" -H 'Content-Type: application/json' \
        -d '{"client_id":"test","client_secret":"secret"}' | jq -r .access_token
}

log "run $RUN_ID start"

# --- preconditions --------------------------------------------------------
for url in "$GATEWAY/components" "$SIM/" "${CDA%/vehicle/v15}/health/ready"; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "$url")
    [[ "$code" =~ ^2 ]] || { log "ABORT: $url answered $code - start the stack first"; exit 2; }
done

# --- path A: S-CORE app -> sovd_adapter -> OpenSOVD gateway -----------------
# poll <url> <jq filter> <wanted>: re-read until the value matches or the debounce timeout ends
poll() {
    local start value=""
    start=$(date +%s.%N)
    while (( $(echo "$(date +%s.%N) - $start < $DEBOUNCE_TIMEOUT_S" | bc) )); do
        value=$(curl -s "$1" | jq -r "$2")
        [[ "$value" == "$3" ]] && break
        sleep 0.25
    done
    echo "$value"
}

path_a_hvac() {
    log "path A: reset"
    curl -s -o /dev/null -X PUT "$HVAC/sensor_stuck" -H 'Content-Type: application/json' -d '{"data":{"stuck":false}}'
    sleep "${PASSED_SETTLE_S:-3}"

    ids=$(save a-data-list "$HVAC" | jq -r '[.items[].id] | join(",")')
    assert A "gateway serves diag_api resources" "cabin_temp,sensor_fault_status,sensor_stuck" "$ids"
    demo=$(jq -r '[.items[].id | select(startswith("demo."))] | length' "$OUT/raw/a-data-list.json")
    assert A "no demo.* ids left" "0" "$demo"
    assert A "fault status before injection" "passed" "$(save a-status-before "$HVAC/sensor_fault_status" | jq -r .data.status)"

    log "path A: inject stuck sensor over SOVD"
    code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$HVAC/sensor_stuck" -H 'Content-Type: application/json' -d '{"data":{"stuck":true}}')
    assert A "injection accepted" "204" "$code"
    assert A "status right after injection" "prefailed" "$(save a-status-prefailed "$HVAC/sensor_fault_status" | jq -r .data.status)"

    inject_t=$(date +%s.%N)
    status=""
    while (( $(echo "$(date +%s.%N) - $inject_t < $DEBOUNCE_TIMEOUT_S" | bc) )); do
        status=$(curl -s "$HVAC/sensor_fault_status" | jq -r .data.status)
        [[ "$status" == failed ]] && break
        sleep 0.25
    done
    debounce_s=$(printf '%.2f' "$(echo "$(date +%s.%N) - $inject_t" | bc)")
    save a-status-failed "$HVAC/sensor_fault_status" > /dev/null
    assert A "status after debounce" "failed" "$status"
    log "path A: debounce qualified after ${debounce_s}s"

    t1=$(jq -r .data.value < <(save a-temp-1 "$HVAC/cabin_temp"))
    sleep 1
    t2=$(jq -r .data.value < <(save a-temp-2 "$HVAC/cabin_temp"))
    assert A "stuck reading is frozen" "$t1" "$t2"

    log "path A: clear"
    curl -s -o /dev/null -X PUT "$HVAC/sensor_stuck" -H 'Content-Type: application/json' -d '{"data":{"stuck":false}}'
    cleared=""
    for _ in $(seq 1 $((DEBOUNCE_TIMEOUT_S * 4))); do
        cleared=$(curl -s "$HVAC/sensor_fault_status" | jq -r .data.status)
        [[ "$cleared" == passed ]] && break
        sleep 0.25
    done
    assert A "status after clear" "passed" "$cleared"
}

path_a_cruise() {
    local put='-s -o /dev/null -w %{http_code} -X PUT -H Content-Type:application/json'
    log "path A: reset"
    curl $put "$CRUISE/speed_sensor_stuck" -d '{"data":{"stuck":false}}' > /dev/null
    sleep "${PASSED_SETTLE_S:-3}"

    ids=$(save a-data-list "$CRUISE" | jq -r '[.items[].id] | join(",")')
    assert A "gateway serves the cruise resources" "vehicle_speed,cruise_state,speed_sensor_fault_status,speed_sensor_stuck" "$ids"
    demo=$(jq -r '[.items[].id | select(startswith("demo."))] | length' "$OUT/raw/a-data-list.json")
    assert A "no demo.* ids left" "0" "$demo"
    assert A "fault status before injection" "passed" "$(save a-status-before "$CRUISE/speed_sensor_fault_status" | jq -r .data.status)"
    # after a previous run the app waits in standby for the driver; re-engaging is not ours to do
    assert A "cruise control engaged" "active" "$(save a-state-before "$CRUISE/cruise_state" | jq -r .data.state)"

    log "path A: inject stuck speed sensor over SOVD"
    code=$(curl $put "$CRUISE/speed_sensor_stuck" -d '{"data":{"stuck":true}}')
    assert A "injection accepted" "204" "$code"
    assert A "status right after injection" "prefailed" "$(save a-status-prefailed "$CRUISE/speed_sensor_fault_status" | jq -r .data.status)"

    inject_t=$(date +%s.%N)
    status=$(poll "$CRUISE/speed_sensor_fault_status" .data.status failed)
    debounce_s=$(printf '%.2f' "$(echo "$(date +%s.%N) - $inject_t" | bc)")
    save a-status-failed "$CRUISE/speed_sensor_fault_status" > /dev/null
    assert A "status after debounce" "failed" "$status"
    log "path A: debounce qualified after ${debounce_s}s"
    state=$(poll "$CRUISE/cruise_state" .data.state unavailable)
    save a-state-after "$CRUISE/cruise_state" > /dev/null
    assert A "cruise control reacts (their logic)" "unavailable" "$state"

    log "path A: clear"
    curl $put "$CRUISE/speed_sensor_stuck" -d '{"data":{"stuck":false}}' > /dev/null
    assert A "status after clear" "passed" "$(poll "$CRUISE/speed_sensor_fault_status" .data.status passed)"
    log "path A: cruise control now $(save a-state-cleared "$CRUISE/cruise_state" | jq -r .data.state) (waits for the driver)"
}

components=$(curl -s "$GATEWAY/components" | jq -r '[.items[].id] | join(",")')
case $components in
    cruise) path_a_cruise ;;
    hvac) path_a_hvac ;;
    *) log "ABORT: gateway serves '$components', expected hvac or cruise"; exit 2 ;;
esac

# --- path B: ECU simulator -> DoIP -> CDA (upstream, unmodified) ------------
TOKEN=$(cda_token)
active() { curl -s "$CDA/components/$ECU/faults" -H "Authorization: Bearer $TOKEN" | tee "$OUT/raw/$1.json" \
    | jq -r '[.items[]? | select(.status.mask != "00") | "\(.code)/\(.status.mask)"] | join(",")'; }

log "path B: clear ECU fault memory"
curl -s -o /dev/null -X DELETE "$SIM/$ECU/dtc/Standard"
assert B "active faults before injection" "" "$(active b-faults-before)"

log "path B: inject DTC 0x$DTC status 0x$DTC_MASK into the simulator"
code=$(curl -s -o /dev/null -w '%{http_code}' -X PUT "$SIM/$ECU/dtc/Standard" -H 'Content-Type: application/json' \
    -d "{\"id\":\"$DTC\",\"statusMask\":\"$DTC_MASK\",\"emissionsRelated\":false}")
assert B "injection accepted" "201" "$code"
assert B "CDA reports the DTC over SOVD" "$DTC/$DTC_MASK" "$(active b-faults-after)"

log "path B: clear"
curl -s -o /dev/null -X DELETE "$SIM/$ECU/dtc/Standard"
assert B "active faults after clear" "" "$(active b-faults-cleared)"

# --- verdict ---------------------------------------------------------------
{
    echo "# Demo run $RUN_ID"
    echo
    echo "| Path | Assertion | Expected | Observed | Verdict |"
    echo "|---|---|---|---|---|"
    for row in "${ROWS[@]}"; do
        IFS='|' read -r p n e o v <<< "$row"
        echo "| $p | $n | \`${e:-none}\` | \`${o:-none}\` | **$v** |"
    done
    echo
    echo "Debounce qualified after ${debounce_s} s. Raw responses in \`raw/\`, timeline in \`timeline.log\`."
    echo
    if ((FAILS == 0)); then echo "**Overall: PASS** (${#ROWS[@]} assertions)"; else echo "**Overall: FAIL** ($FAILS of ${#ROWS[@]} failed)"; fi
} > "$OUT/verdict.md"

printf '%s\n' "${ROWS[@]}" | jq -R 'split("|") | {path: .[0], assertion: .[1], expected: .[2], observed: .[3], verdict: .[4]}' \
    | jq -s --arg run "$RUN_ID" --arg debounce "$debounce_s" '{run: $run, debounce_s: ($debounce | tonumber), assertions: .}' > "$OUT/run.json"

log "run $RUN_ID done: $((${#ROWS[@]} - FAILS))/${#ROWS[@]} passed"
echo "evidence: $OUT"
exit $((FAILS > 0))
