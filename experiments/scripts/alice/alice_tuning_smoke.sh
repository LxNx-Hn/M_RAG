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
OUTPUT_FILE="${OUTPUT_FILE:-experiments/results/tuning/phase7_6A_alice_tuning_adapter_smoke_1sample.jsonl}"

if [ "${CONFIRM_ALICE_TUNING_SMOKE:-0}" != "1" ]; then
  echo "CONFIRM_ALICE_TUNING_SMOKE=1 is required for Alice tuning adapter smoke."
  exit 2
fi

if [ "$QUERY_SPLIT" != "tuning_queries" ] || [ "$QUERY_LIMIT" != "1" ] || [ "$MAX_SAMPLES" != "1" ]; then
  echo "Alice tuning adapter smoke is hard-limited to tuning_queries, query_limit=1, max_samples=1."
  exit 2
fi

if [ "$PROFILE" != "current_defaults" ] || [ "$AXIS_CONFIG" != "hyde_off__no_decoder_control" ]; then
  echo "Alice tuning adapter smoke requires profile=current_defaults and axis_config=hyde_off__no_decoder_control."
  exit 2
fi

if [ "$OPENAI_ENABLED" != "0" ] || [ "$RAGAS_ENABLED" != "0" ]; then
  echo "OpenAI and RAGAS must remain disabled for Alice tuning adapter smoke."
  exit 2
fi

python experiments/runners/run_alice_tuning.py \
  --execute-tuning-smoke \
  --confirm-alice-base \
  --query-split "$QUERY_SPLIT" \
  --query-limit "$QUERY_LIMIT" \
  --max-samples "$MAX_SAMPLES" \
  --profile "$PROFILE" \
  --axis-config "$AXIS_CONFIG" \
  --generation-model "$MODEL_NAME" \
  --model-variant base \
  --collection-name local_gt__papers \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --temperature "$TEMPERATURE" \
  --output-file "$OUTPUT_FILE"
