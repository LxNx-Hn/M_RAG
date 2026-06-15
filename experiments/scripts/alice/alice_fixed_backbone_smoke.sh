#!/usr/bin/env bash
# Phase 7.6B-2A: exactly ONE query-aware fixed-backbone retrieval smoke on Alice.
#
# This wrapper runs a single sample through the real Paper-RAG backbone
# (BGE-M3 dense + BM25 sparse + RRF + CrossEncoder rerank) using the query text.
# It refuses anything beyond one sample and refuses profile expansion, forbidden
# query splits, OpenAI, RAGAS, and GT regeneration. It will not run without the
# explicit confirmation environment variable.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

MODEL_NAME="${MODEL_NAME:-K-intelligence/Midm-2.0-Base-Instruct}"
QUERY_SPLIT="${QUERY_SPLIT:-tuning_queries}"
QUERY_LIMIT="${QUERY_LIMIT:-1}"
MAX_SAMPLES="${MAX_SAMPLES:-1}"
QUERY_ID="${QUERY_ID:-track1_0001}"
PROFILE="${PROFILE:-current_defaults}"
AXIS_CONFIG="${AXIS_CONFIG:-hyde_off__no_decoder_control}"
RETRIEVAL_MODE="${RETRIEVAL_MODE:-fixed_backbone}"
COLLECTION="${COLLECTION:-local_gt__papers}"
RETRIEVAL_POOL_TOP_K="${RETRIEVAL_POOL_TOP_K:-20}"
RERANK_TOP_N="${RERANK_TOP_N:-5}"
CONTEXT_CHUNK_COUNT="${CONTEXT_CHUNK_COUNT:-5}"
MAX_NEW_TOKENS="${MAX_NEW_TOKENS:-512}"
TEMPERATURE="${TEMPERATURE:-0.0}"
OPENAI_ENABLED="${OPENAI_ENABLED:-0}"
RAGAS_ENABLED="${RAGAS_ENABLED:-0}"
GT_REGENERATION="${GT_REGENERATION:-0}"
OUTPUT_FILE="${OUTPUT_FILE:-experiments/results/tuning/phase7_6B2A_fixed_backbone_retrieval_smoke_1sample.jsonl}"

if [ "${CONFIRM_ALICE_FIXED_BACKBONE_SMOKE:-0}" != "1" ]; then
  echo "CONFIRM_ALICE_FIXED_BACKBONE_SMOKE=1 is required for the fixed-backbone retrieval smoke."
  exit 2
fi

# Exactly one sample. No expansion of any kind.
if [ "$QUERY_SPLIT" != "tuning_queries" ] || [ "$QUERY_LIMIT" != "1" ] || [ "$MAX_SAMPLES" != "1" ]; then
  echo "Fixed-backbone smoke is hard-limited to tuning_queries, query_limit=1, max_samples=1."
  exit 2
fi

# Explicitly refuse forbidden / held-out splits.
case "$QUERY_SPLIT" in
  decoder_main_queries|candidate_final_eval_queries|service_route_queries|query_templates|query_type_analysis_queries)
    echo "Refusing forbidden query split for smoke: $QUERY_SPLIT"
    exit 2
    ;;
esac

# No profile expansion; current_defaults / hyde_off only.
if [ "$PROFILE" != "current_defaults" ] || [ "$AXIS_CONFIG" != "hyde_off__no_decoder_control" ]; then
  echo "Fixed-backbone smoke requires profile=current_defaults and axis_config=hyde_off__no_decoder_control."
  exit 2
fi

if [ "$RETRIEVAL_MODE" != "fixed_backbone" ]; then
  echo "This wrapper only runs retrieval_mode=fixed_backbone."
  exit 2
fi

if [ "$MODEL_NAME" != "K-intelligence/Midm-2.0-Base-Instruct" ]; then
  echo "Fixed-backbone smoke requires K-intelligence/Midm-2.0-Base-Instruct."
  exit 2
fi

if [ "$COLLECTION" != "local_gt__papers" ]; then
  echo "Fixed-backbone smoke requires collection local_gt__papers."
  exit 2
fi

if [ "$OPENAI_ENABLED" != "0" ] || [ "$RAGAS_ENABLED" != "0" ] || [ "$GT_REGENERATION" != "0" ]; then
  echo "OpenAI, RAGAS, and GT regeneration must remain disabled for the fixed-backbone smoke."
  exit 2
fi

python experiments/runners/run_alice_tuning.py \
  --execute-tuning-smoke \
  --confirm-alice-base \
  --retrieval-mode "$RETRIEVAL_MODE" \
  --query-split "$QUERY_SPLIT" \
  --query-limit "$QUERY_LIMIT" \
  --max-samples "$MAX_SAMPLES" \
  --query-id "$QUERY_ID" \
  --profile "$PROFILE" \
  --axis-config "$AXIS_CONFIG" \
  --generation-model "$MODEL_NAME" \
  --model-variant base \
  --model-role alice_thesis_fixed_backbone_smoke \
  --collection-name "$COLLECTION" \
  --retrieval-pool-top-k "$RETRIEVAL_POOL_TOP_K" \
  --rerank-top-n "$RERANK_TOP_N" \
  --context-chunk-count "$CONTEXT_CHUNK_COUNT" \
  --max-new-tokens "$MAX_NEW_TOKENS" \
  --temperature "$TEMPERATURE" \
  --output-file "$OUTPUT_FILE"
