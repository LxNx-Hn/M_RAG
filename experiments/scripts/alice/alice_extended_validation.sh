#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

export OPENAI_ENABLED=0
export RAGAS_ENABLED=0
export GT_REGENERATION_ENABLED=0

RUNNER="experiments/runners/run_extended_validation.py"
RESULT_DIR="experiments/results/extended_validation"
RESULT_FILE="$RESULT_DIR/extended-hyde-cad-scd__extended_validation_questions__extended_validation_generation.jsonl"

echo "[1/3] Extended validation preflight"
python "$RUNNER" --dry-run

if [ "${EXECUTE:-0}" != "1" ]; then
  echo "preflight_only: true"
  echo "To execute the 41 x 8 matrix, set EXECUTE=1 and CONFIRM_EXTENDED_VALIDATION_8CONFIG=1."
  exit 0
fi

if [ "${CONFIRM_EXTENDED_VALIDATION_8CONFIG:-0}" != "1" ]; then
  echo "CONFIRM_EXTENDED_VALIDATION_8CONFIG=1 is required."
  exit 2
fi

echo "[2/3] Generate 41 held-out queries x 8 frozen configs"
python "$RUNNER" --execute

if [ ! -s "$RESULT_FILE" ]; then
  echo "Expected result file is missing or empty: $RESULT_FILE"
  exit 3
fi

LINES="$(wc -l < "$RESULT_FILE" | tr -d ' ')"
if [ "$LINES" != "328" ]; then
  echo "Expected 328 generation records, found $LINES."
  exit 4
fi

echo "[3/3] Dry-validate official RAGAS input schema and answer-span coverage"
python experiments/evaluators/official_ragas_runner.py \
  --generation-results "$RESULT_FILE" \
  --query-split extended_validation_questions

echo "extended_validation_generation_ready: true"
echo "records: 328"
echo "result_file: $RESULT_FILE"
echo "Official scoring remains a separate CPU+judge-API phase, identical to the existing main evaluation workflow."
