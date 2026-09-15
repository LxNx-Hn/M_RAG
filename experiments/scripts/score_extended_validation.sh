#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

RESULT_FILE="experiments/results/extended_validation/extended-hyde-cad-scd__extended_validation_questions__extended_validation_generation.jsonl"
OUT_DIR="experiments/results/evaluation/extended_validation"

if [ ! -s "$RESULT_FILE" ]; then
  echo "Missing generation result: $RESULT_FILE"
  exit 2
fi

LINES="$(wc -l < "$RESULT_FILE" | tr -d ' ')"
if [ "$LINES" != "328" ]; then
  echo "Expected 328 generation records, found $LINES."
  exit 3
fi

COMMON_ARGS=(
  --generation-results "$RESULT_FILE"
  --query-split extended_validation_questions
  --out-dir "$OUT_DIR"
  --judge nvidia_nim
  --judge-model meta/llama-3.3-70b-instruct
)

echo "[1/2] Dry validation"
python experiments/evaluators/official_ragas_runner.py "${COMMON_ARGS[@]}"

if [ "${EXECUTE:-0}" != "1" ]; then
  echo "score_preflight_only: true"
  echo "Set EXECUTE=1, CONFIRM_OFFICIAL_RAGAS_EXECUTION=1, and NVIDIA_API_KEY to score."
  exit 0
fi

if [ "${CONFIRM_OFFICIAL_RAGAS_EXECUTION:-0}" != "1" ]; then
  echo "CONFIRM_OFFICIAL_RAGAS_EXECUTION=1 is required."
  exit 4
fi
if [ -z "${NVIDIA_API_KEY:-}" ]; then
  echo "NVIDIA_API_KEY is required."
  exit 5
fi

echo "[2/2] Official RAGAS scoring with the same fixed NIM judge"
python experiments/evaluators/official_ragas_runner.py \
  "${COMMON_ARGS[@]}" \
  --execute
