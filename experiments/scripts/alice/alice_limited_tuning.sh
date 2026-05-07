#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

MODEL_NAME="${MODEL_NAME:-K-intelligence/Midm-2.0-Base-Instruct}"
QUERY_SPLIT="${QUERY_SPLIT:-tuning_queries}"
QUERY_LIMIT="${QUERY_LIMIT:-5}"
MAX_SAMPLES="${MAX_SAMPLES:-5}"
PROFILE="${PROFILE:-current_defaults}"
AXIS_CONFIG="${AXIS_CONFIG:-hyde_off__no_decoder_control}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-512}"
TEMPERATURE="${TEMPERATURE:-0.0}"
OPENAI_ENABLED="${OPENAI_ENABLED:-0}"
RAGAS_ENABLED="${RAGAS_ENABLED:-0}"
OUTPUT_FILE="${OUTPUT_FILE:-experiments/results/tuning/phase7_6B_limited_tuning_current_defaults_5samples.jsonl}"

if [ "${CONFIRM_ALICE_LIMITED_TUNING:-0}" != "1" ]; then
  echo "CONFIRM_ALICE_LIMITED_TUNING=1 is required for Alice limited tuning."
  exit 2
fi

if [ "$QUERY_SPLIT" != "tuning_queries" ] || [ "$QUERY_LIMIT" -gt 5 ] || [ "$MAX_SAMPLES" -gt 5 ]; then
  echo "Alice limited tuning is hard-limited to tuning_queries with query_limit<=5 and max_samples<=5."
  exit 2
fi

if [ "$PROFILE" != "current_defaults" ] || [ "$AXIS_CONFIG" != "hyde_off__no_decoder_control" ]; then
  echo "Alice limited tuning currently allows only current_defaults and hyde_off__no_decoder_control."
  exit 2
fi

if [ "$MODEL_NAME" != "K-intelligence/Midm-2.0-Base-Instruct" ]; then
  echo "Alice limited tuning requires K-intelligence/Midm-2.0-Base-Instruct."
  exit 2
fi

if [ "$OPENAI_ENABLED" != "0" ] || [ "$RAGAS_ENABLED" != "0" ]; then
  echo "OpenAI and RAGAS must remain disabled for Alice limited tuning."
  exit 2
fi

python experiments/runners/run_alice_tuning.py \
  --execute-limited-tuning \
  --confirm-alice-limited-tuning \
  --query-split "$QUERY_SPLIT" \
  --query-limit "$QUERY_LIMIT" \
  --max-samples "$MAX_SAMPLES" \
  --profile "$PROFILE" \
  --axis-config "$AXIS_CONFIG" \
  --generation-model "$MODEL_NAME" \
  --model-variant base \
  --model-role alice_thesis_limited_tuning \
  --collection-name local_gt__papers \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --temperature "$TEMPERATURE" \
  --output-file "$OUTPUT_FILE"
