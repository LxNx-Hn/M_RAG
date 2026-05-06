#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

STAGE="tuning"
if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  echo "Usage: bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage <tuning|freeze-check|main-generation|optional-final>"
  echo "Default stage is tuning in dry-run/plan-only mode."
  exit 0
elif [ "${1:-}" = "--stage" ]; then
  STAGE="${2:-}"
elif [ $# -gt 0 ]; then
  echo "Usage: bash experiments/scripts/alice/alice_thesis_run_plan.sh --stage <tuning|freeze-check|main-generation|optional-final>"
  exit 2
fi

EXECUTE="${EXECUTE:-0}"
OPENAI_ENABLED="${OPENAI_ENABLED:-0}"
RAGAS_ENABLED="${RAGAS_ENABLED:-0}"
FROZEN_PARAMS="experiments/configs/frozen_params.yaml"

if [ "$OPENAI_ENABLED" != "0" ] || [ "$RAGAS_ENABLED" != "0" ]; then
  echo "OpenAI and RAGAS are disabled for Alice generation planning."
  exit 2
fi

case "$STAGE" in
  tuning)
    if [ "$EXECUTE" = "1" ]; then
      if [ "${CONFIRM_ALICE_TUNING:-0}" != "1" ]; then
        echo "CONFIRM_ALICE_TUNING=1 is required for real tuning."
        exit 2
      fi
      echo "Real tuning execution is not enabled by this planning script. Use the later explicitly approved tuning phase."
      exit 3
    fi
    python experiments/runners/run_tuning_plan.py --dry-run --plan-only --query-split tuning_queries --limit 5 --no-openai
    ;;
  freeze-check)
    if [ -f "$FROZEN_PARAMS" ]; then
      echo "freeze_ready: true"
      echo "frozen_params: $FROZEN_PARAMS"
    else
      echo "freeze_ready: false"
      echo "missing: $FROZEN_PARAMS"
      echo "Run Phase 8 freeze only after approved tuning evidence exists."
    fi
    ;;
  main-generation)
    if [ ! -f "$FROZEN_PARAMS" ] && [ "${CONFIRM_FROZEN_PARAMS:-0}" != "1" ]; then
      echo "Main generation requires $FROZEN_PARAMS or CONFIRM_FROZEN_PARAMS=1."
      exit 2
    fi
    if [ ! -f "$FROZEN_PARAMS" ] && [ "${CONFIRM_FROZEN_PARAMS:-0}" = "1" ]; then
      echo "WARNING: CONFIRM_FROZEN_PARAMS=1 was set without $FROZEN_PARAMS."
      echo "Proceeding in planning mode only; do not run thesis main generation before Phase 8 freeze."
    fi
    if [ "$EXECUTE" = "1" ]; then
      echo "Real main generation is not enabled by this planning script. Use the later explicitly approved main-generation phase."
      exit 3
    fi
    python experiments/runners/run_generation.py --dry-run --plan-only --query-split decoder_main_queries --config-limit 2 --limit 3 --no-openai
    ;;
  optional-final)
    if [ "${CONFIRM_OPTIONAL_FINAL:-0}" != "1" ]; then
      echo "optional-final requires CONFIRM_OPTIONAL_FINAL=1 even for planning."
      exit 2
    fi
    if [ "$EXECUTE" = "1" ]; then
      echo "Real optional final generation is not enabled by this planning script."
      exit 3
    fi
    python experiments/runners/run_generation.py --dry-run --plan-only --query-split candidate_final_eval_queries --config-limit 2 --limit 3 --no-openai
    ;;
  *)
    echo "Supported stages: tuning, freeze-check, main-generation, optional-final"
    exit 2
    ;;
esac
