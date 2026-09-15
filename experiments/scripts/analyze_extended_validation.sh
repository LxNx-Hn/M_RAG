#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

OLD_GEN="experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl"
NEW_GEN="experiments/results/extended_validation/extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl"
OLD_SCORE="experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
NEW_SCORE="experiments/results/evaluation/extended-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json"
OUT="experiments/results/analysis/extended_validation_60_analysis.json"

for path in "$OLD_GEN" "$NEW_GEN" "$OLD_SCORE" "$NEW_SCORE"; do
  if [ ! -s "$path" ]; then
    echo "Missing required artifact: $path"
    exit 2
  fi
done

python experiments/analyzers/analyze_extended_validation_60.py \
  --old-generation "$OLD_GEN" \
  --new-generation "$NEW_GEN" \
  --old-scores "$OLD_SCORE" \
  --new-scores "$NEW_SCORE" \
  --out "$OUT" \
  --bootstrap-iterations 200000 \
  --seed 20260713

echo "analysis_ready: $OUT"
