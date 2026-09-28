#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd -- "$SCRIPT_DIR/../.." && pwd)"
BIN="${BIN:-$ROOT_DIR/target/release/ddd}"
OBJECTIVE="${OBJECTIVE:-infsteps180}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/results/tuan2_doquangvinh}"
PARSER_DIR="parse_results.py"
CSV_BATCH="${CSV_BATCH:-$SCRIPT_DIR/$PARSER_DIR}"
INSTANCE_TIMEOUT_SECS="${INSTANCE_TIMEOUT_SECS:-130}"
RAM_LIMIT_KB="${RAM_LIMIT_KB:-12000000}"

mkdir -p "$OUT_DIR"

INSTANCES=(
    origA1 origA2 origB1 origB2
    trackA1 trackA2 trackB1 trackB2 
    stationA1 stationA2 stationB1 stationB2 
)
CONFIGS=("MaxSATDefault" "MaxSATBase")

# chạy một instance
run_one() {
    local config="$1"
    local instance="$2"
    local json_out="$3"
    local temp_dir
    local stdout_log
    local stderr_log
    local solver

    temp_dir="$(dirname -- "$json_out")"
    stdout_log="$temp_dir/${instance}.stdout.log"
    stderr_log="$temp_dir/${instance}.stderr.log"

    if [[ "$config" == "MaxSATDefault" ]]; then
        solver="maxsat_ddd_ladder_sc"
    else
        solver="maxsat_ddd_ladder"
    fi

    echo "Running $config / $instance"
    if ! "$BIN" \
        -s "$solver" \
        --txt-instances \
        --instance-name-filter "$instance" \
        --instance-name-exact \
        --objective "$OBJECTIVE" \
        --json-output "$json_out" \
        >"$stdout_log" \
        2>"$stderr_log"; then
        echo "Failed: $config / $instance" >&2
        echo "See: $stdout_log and $stderr_log" >&2
        return 1
    fi
    echo "Done: $config / $instance"
}

run_config() {
    local config="$1"
    local json_out="${OUT_DIR}/${config}_${OBJECTIVE}.json"
    local temp_dir

    temp_dir="$(mktemp -d "${OUT_DIR}/${config}_tmp.XXXXXX")"

    # chạy instance, mỗi instance ghi vào một file JSON tạm
    for instance in "${INSTANCES[@]}"; do
        run_one "${config}" "${instance}" "${temp_dir}/${instance}.json"
    done

    # gom các JSON tạm thành JSON tổng
    python3 - "$temp_dir" "$json_out" "${INSTANCES[@]}" <<'PY'
import json
import sys
from pathlib import Path

temp_dir = Path(sys.argv[1])
json_out = Path(sys.argv[2])
instances = sys.argv[3:]

items = []
for instance in instances:
    temp_json = temp_dir / f"{instance}.json"
    data = json.loads(temp_json.read_text())
    if isinstance(data, list):
        items.extend(data)
    else:
        items.append(data)

for index, item in enumerate(items):
    item["index"] = index

json_out.write_text(json.dumps(items, indent=4))
print(f"Wrote {json_out}")
PY

    rm -rf "$temp_dir"

    # gọi parser để xuất JSON sang CSV
    python3 "$CSV_BATCH" "$json_out" --format compact --overwrite \
    && echo "CSV ok" || echo "CSV failed"
}

for config in "${CONFIGS[@]}"; do
    run_config "${config}"
done