#!/usr/bin/env bash
# Alice Cloud local environment template.
# Copy this file outside git or source it manually on Alice after replacing
# placeholders. Never commit real secrets, tokens, passwords, or private keys.

export JWT_SECRET_KEY="CHANGE_ME"
export LOAD_GPU_MODELS="true"
export GENERATION_MODEL="K-intelligence/Midm-2.0-Base-Instruct"
export DATABASE_URL="sqlite+aiosqlite:///./mrag.db"
export MRAG_API_BASE="http://127.0.0.1:8000"

export HF_HOME="${HOME}/.cache/huggingface"
export TRANSFORMERS_CACHE="${HF_HOME}"
export HF_HUB_CACHE="${HF_HOME}"
export HF_TOKEN="__SET_IN_ENV_NOT_IN_REPO__"

export MRAG_RUNNER_EMAIL="runner@example.invalid"
export MRAG_RUNNER_USERNAME="mrag_runner"
export MRAG_RUNNER_PASSWORD="CHANGE_ME"

# Optional Phase 10-only evaluation settings. Keep disabled unless a later
# explicit evaluation phase approves OpenAI or official RAGAS usage.
export OPENAI_JUDGE_MODEL="gpt-4o"
export OPENAI_API_KEY="__OPTIONAL_PHASE10_ONLY__"
