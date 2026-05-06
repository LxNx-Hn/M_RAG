#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

MODEL_NAME="${MODEL_NAME:-K-intelligence/Midm-2.0-Base-Instruct}"
QUERY_SPLIT="${QUERY_SPLIT:-tuning_queries}"
QUERY_LIMIT="${QUERY_LIMIT:-1}"
PROFILE="${PROFILE:-current_defaults}"
AXIS_CONFIG="${AXIS_CONFIG:-hyde_off__no_decoder_control}"
MAX_SAMPLES="${MAX_SAMPLES:-1}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-512}"
TEMPERATURE="${TEMPERATURE:-0.0}"
OPENAI_ENABLED="${OPENAI_ENABLED:-0}"
RAGAS_ENABLED="${RAGAS_ENABLED:-0}"
OUTPUT_FILE="${OUTPUT_FILE:-experiments/results/smoke/phase7_7_alice_base_smoke_1sample.jsonl}"
REPORT_FILE="${REPORT_FILE:-experiments/reports/phase7_7_alice_base_smoke_report.md}"

if [ "${CONFIRM_ALICE_BASE_SMOKE:-0}" != "1" ]; then
  echo "CONFIRM_ALICE_BASE_SMOKE=1 is required for Alice BASE smoke."
  exit 2
fi

if [ "$QUERY_SPLIT" != "tuning_queries" ] || [ "$QUERY_LIMIT" != "1" ] || [ "$MAX_SAMPLES" != "1" ]; then
  echo "Alice BASE smoke is hard-limited to tuning_queries, query_limit=1, max_samples=1."
  exit 2
fi

if [ "$PROFILE" != "current_defaults" ] || [ "$AXIS_CONFIG" != "hyde_off__no_decoder_control" ]; then
  echo "Alice BASE smoke requires profile=current_defaults and axis_config=hyde_off__no_decoder_control."
  exit 2
fi

if [ "$OPENAI_ENABLED" != "0" ] || [ "$RAGAS_ENABLED" != "0" ]; then
  echo "OpenAI and RAGAS must remain disabled for Alice BASE smoke."
  exit 2
fi

if [ "$MODEL_NAME" != "K-intelligence/Midm-2.0-Base-Instruct" ]; then
  echo "Alice BASE smoke requires MODEL_NAME=K-intelligence/Midm-2.0-Base-Instruct."
  exit 2
fi

mkdir -p "$(dirname "$OUTPUT_FILE")" "$(dirname "$REPORT_FILE")"

ALLOW_DOWNLOAD_FLAG=()
if [ "${ALLOW_MODEL_DOWNLOAD:-0}" = "1" ]; then
  ALLOW_DOWNLOAD_FLAG=(--allow-download)
fi

set +e
python experiments/runners/run_local_smoke.py \
  --execute-smoke \
  --alice-mode \
  --confirm-alice-base \
  --generation-model "$MODEL_NAME" \
  --model-variant base \
  --model-role alice_thesis_model_smoke \
  --phase-label phase7_7_alice_base_smoke \
  --output-file "$OUTPUT_FILE" \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --temperature "$TEMPERATURE" \
  "${ALLOW_DOWNLOAD_FLAG[@]}"
SMOKE_EXIT_CODE=$?
set -e

SMOKE_STATUS="output_missing"
SMOKE_RECORD_COUNT="0"
if [ -f "$OUTPUT_FILE" ]; then
  SMOKE_SUMMARY="$(SMOKE_OUTPUT_FILE="$OUTPUT_FILE" python - <<'PY'
import json
import os
from pathlib import Path

path = Path(os.environ["SMOKE_OUTPUT_FILE"])
rows = []
with path.open("r", encoding="utf-8") as handle:
    for line in handle:
        if line.strip():
            rows.append(json.loads(line))
status = rows[0].get("status", "unknown") if len(rows) == 1 else "invalid_record_count"
print(f"{status}|{len(rows)}")
PY
)"
  SMOKE_STATUS="${SMOKE_SUMMARY%%|*}"
  SMOKE_RECORD_COUNT="${SMOKE_SUMMARY##*|}"
fi

cat > "$REPORT_FILE" <<EOF
# Phase 7.7 Alice BASE Smoke Report

- status: $SMOKE_STATUS
- command_exit_code: $SMOKE_EXIT_CODE
- output_file: $OUTPUT_FILE
- output_record_count: $SMOKE_RECORD_COUNT
- model: $MODEL_NAME
- query_split: $QUERY_SPLIT
- query_limit: $QUERY_LIMIT
- profile: $PROFILE
- axis_config: $AXIS_CONFIG
- max_samples: $MAX_SAMPLES
- thesis_grade_result: false
- openai_used: false
- ragas_used: false
- gt_regenerated: false

Alice BASE smoke artifacts are execution-path validation only. Thesis-grade
claims require the later approved tuning, freeze, main generation, and
evaluation phases.
EOF

echo "Alice BASE smoke output: $OUTPUT_FILE"
echo "Alice BASE smoke report: $REPORT_FILE"
exit "$SMOKE_EXIT_CODE"
