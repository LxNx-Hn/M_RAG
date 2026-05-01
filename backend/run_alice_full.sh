#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

if [[ -f "../.venv/bin/activate" ]]; then
  source ../.venv/bin/activate
fi

if [[ -f "./.alice_runtime_env.sh" ]]; then
  source ./.alice_runtime_env.sh
fi

if [[ "${OPENAI_API_KEY:-}" == "PUT_YOUR_OPENAI_API_KEY_HERE" ]] || [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "[error] OPENAI_API_KEY is not set."
  echo "Please set OPENAI_API_KEY environment variable or create backend/.alice_runtime_env.sh"
  exit 1
fi

python scripts/verify_deployment.py
python scripts/master_run.py --skip-download --push-results
