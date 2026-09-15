#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

RAW_FILE="experiments/results/extended_validation/extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl"
TRANSLATED_FILE="experiments/results/extended_validation/extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.context_ko_translated.jsonl"
OUT_DIR="experiments/results/evaluation/extended-hyde-cad-scd-reference-scd-gpt4o-official"
MERGED_FILE="$OUT_DIR/merged.ragas_scores.json"

if [ ! -s "$RAW_FILE" ]; then
  echo "Missing generation result: $RAW_FILE"
  exit 2
fi

LINES="$(wc -l < "$RAW_FILE" | tr -d ' ')"
if [ "$LINES" != "328" ]; then
  echo "Expected 328 generation records, found $LINES."
  exit 3
fi

echo "[1/4] Dry-validate the retained final SCD-on context-translation protocol"
python experiments/evaluators/translate_context_for_scd.py \
  --generation-results "$RAW_FILE" \
  --out "$TRANSLATED_FILE" \
  --judge openai \
  --judge-model gpt-4o

if [ "${EXECUTE:-0}" != "1" ]; then
  echo "score_preflight_only: true"
  echo "For real preprocessing/scoring set EXECUTE=1, CONFIRM_CONTEXT_TRANSLATION_EXECUTION=1, CONFIRM_OFFICIAL_RAGAS_EXECUTION=1, and OPENAI_API_KEY."
  exit 0
fi

if [ "${CONFIRM_CONTEXT_TRANSLATION_EXECUTION:-0}" != "1" ]; then
  echo "CONFIRM_CONTEXT_TRANSLATION_EXECUTION=1 is required."
  exit 4
fi
if [ "${CONFIRM_OFFICIAL_RAGAS_EXECUTION:-0}" != "1" ]; then
  echo "CONFIRM_OFFICIAL_RAGAS_EXECUTION=1 is required."
  exit 4
fi
if [ -z "${OPENAI_API_KEY:-}" ]; then
  echo "OPENAI_API_KEY is required for the retained gpt-4o translation/judge protocol."
  exit 5
fi

echo "[2/4] Translate SCD-on retrieved contexts only; generated answers stay unchanged"
python experiments/evaluators/translate_context_for_scd.py \
  --generation-results "$RAW_FILE" \
  --out "$TRANSLATED_FILE" \
  --judge openai \
  --judge-model gpt-4o \
  --execute

TRANSLATED_LINES="$(wc -l < "$TRANSLATED_FILE" | tr -d ' ')"
if [ "$TRANSLATED_LINES" != "328" ]; then
  echo "Expected 328 translated/copy-through records, found $TRANSLATED_LINES."
  exit 6
fi

echo "[3/4] Dry-validate RAGAS input and 328/328 ground-truth coverage"
python experiments/evaluators/official_ragas_runner.py \
  --generation-results "$TRANSLATED_FILE" \
  --query-split extended_validation_questions \
  --judge openai \
  --judge-model gpt-4o \
  --out-dir "$OUT_DIR"

echo "[4/4] Score with the retained gpt-4o protocol until zero null metric cells"
python experiments/evaluators/run_scoring_until_converged.py \
  --generation-results "$TRANSLATED_FILE" \
  --query-split extended_validation_questions \
  --judge openai \
  --judge-model gpt-4o \
  --out-dir "$OUT_DIR" \
  --max-workers 4 \
  --judge-timeout 900 \
  --task-timeout 2400 \
  --run-max-retries 10 \
  --run-max-wait 60 \
  --null-threshold 0 \
  --max-passes 8

if [ ! -s "$MERGED_FILE" ]; then
  echo "Merged score artifact missing: $MERGED_FILE"
  exit 7
fi

python - "$MERGED_FILE" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
data = json.loads(p.read_text(encoding="utf-8"))
rows = data.get("per_sample", [])
metrics = data.get("metrics", [])
nulls = sum(row.get(metric) is None for row in rows for metric in metrics)
if len(rows) != 328 or nulls != 0:
    raise SystemExit(f"score validation failed: rows={len(rows)} null_cells={nulls}")
print(f"scoring_ready: rows={len(rows)} null_cells={nulls}")
PY

echo "merged_scores: $MERGED_FILE"
