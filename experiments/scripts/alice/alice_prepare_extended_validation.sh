#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

export HF_HOME="${HF_HOME:-$HOME/.cache/huggingface}"
export MRAG_CHROMA_DIR="${MRAG_CHROMA_DIR:-$ROOT_DIR/.alice_runtime/chroma_db}"
mkdir -p "$HF_HOME" "$MRAG_CHROMA_DIR"

export OPENAI_ENABLED=0
export RAGAS_ENABLED=0
export GT_REGENERATION_ENABLED=0

echo "[1/6] Repository/runtime setup"
CREATE_VENV="${CREATE_VENV:-1}" bash experiments/scripts/alice/alice_setup.sh

if [ -d ".venv" ]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "[2/6] Fail-closed literal GT audit for retained 19 + extension 41"
python experiments/scripts/audit_all_60_gt_literal.py \
  --report experiments/results/analysis/all_60_gt_literal_audit.json

echo "[3/6] Build clean fixed-backbone retrieval index + persisted BM25"
python experiments/scripts/alice/build_local_gt_index.py --reset

echo "[4/6] Static extended-validation readiness checks"
python -m pytest -q experiments/tests/test_extended_validation_ready.py
python -m compileall -q experiments/runners experiments/evaluators experiments/analyzers experiments/scripts

echo "[5/6] One-sample Mi:dm BASE execution smoke"
CONFIRM_ALICE_BASE_SMOKE=1 \
ALLOW_MODEL_DOWNLOAD="${ALLOW_MODEL_DOWNLOAD:-1}" \
bash experiments/scripts/alice/alice_base_smoke.sh

echo "[6/6] 41 x 8 extended validation dry preflight"
bash experiments/scripts/alice/alice_extended_validation.sh

echo "alice_extended_validation_prepared: true"
echo "all_60_literal_gt_audit: passed"
echo "all_60_gt_report: experiments/results/analysis/all_60_gt_literal_audit.json"
echo "HF_HOME: $HF_HOME"
echo "MRAG_CHROMA_DIR: $MRAG_CHROMA_DIR"
echo "Next command:"
echo "EXECUTE=1 CONFIRM_EXTENDED_VALIDATION_8CONFIG=1 CONFIRM_SCD_V2_GENERATION=1 bash experiments/scripts/alice/alice_extended_validation.sh"
