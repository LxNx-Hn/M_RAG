#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

export OPENAI_ENABLED=0
export RAGAS_ENABLED=0
export GT_REGENERATION_ENABLED=0

RUNNER="experiments/runners/run_extended_validation.py"
RESULT_DIR="experiments/results/extended_validation"
RESULT_FILE="$RESULT_DIR/extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl"
REFERENCE_SPLIT="extended_validation_literal_gt"

echo "[0/4] Literal GT audit against checked-in source PDFs"
python experiments/scripts/audit_extended_gt_literal.py --no-write-report

echo "[1/4] Extended reference-SCD validation preflight"
python "$RUNNER" --dry-run

if [ "${EXECUTE:-0}" != "1" ]; then
  echo "preflight_only: true"
  echo "reference_split: $REFERENCE_SPLIT"
  echo "To execute the 41 x 8 matrix, set EXECUTE=1, CONFIRM_EXTENDED_VALIDATION_8CONFIG=1, and CONFIRM_SCD_V2_GENERATION=1."
  exit 0
fi

if [ "${CONFIRM_EXTENDED_VALIDATION_8CONFIG:-0}" != "1" ]; then
  echo "CONFIRM_EXTENDED_VALIDATION_8CONFIG=1 is required."
  exit 2
fi
if [ "${CONFIRM_SCD_V2_GENERATION:-0}" != "1" ]; then
  echo "CONFIRM_SCD_V2_GENERATION=1 is required for final reference_scd generation."
  exit 2
fi

echo "[2/4] Generate 41 held-out queries x 8 configs with final reference_scd"
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

echo "[3/4] Re-audit literal GT after generation"
python experiments/scripts/audit_extended_gt_literal.py --no-write-report

echo "[4/4] Dry-validate RAGAS schema and 328/328 literal-reference coverage"
python experiments/evaluators/official_ragas_runner.py \
  --generation-results "$RESULT_FILE" \
  --query-split "$REFERENCE_SPLIT"

echo "extended_validation_generation_ready: true"
echo "records: 328"
echo "reference_split: $REFERENCE_SPLIT"
echo "gt_generation: manual_source_extraction_only"
echo "scd_mode: reference_scd"
echo "scd_params: alpha=1.1 beta=0.9 t_start=5"
echo "result_file: $RESULT_FILE"
echo "Scoring/preprocessing remains separate from Alice GPU generation, matching the retained final experiment workflow."
