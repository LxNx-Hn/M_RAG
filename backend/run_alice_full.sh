#!/usr/bin/env bash
set -euo pipefail

cd /home/elicer/M_RAG/backend
source ../.venv/bin/activate
source ./.alice_runtime_env.sh

if [[ "${OPENAI_API_KEY:-}" == "PUT_YOUR_OPENAI_API_KEY_HERE" ]] || [[ -z "${OPENAI_API_KEY:-}" ]]; then
  echo "[error] OPENAI_API_KEY is not set in backend/.alice_runtime_env.sh"
  echo "Please edit backend/.alice_runtime_env.sh and replace PUT_YOUR_OPENAI_API_KEY_HERE"
  exit 1
fi

python scripts/verify_deployment.py
python scripts/master_run.py --skip-download --push-results
