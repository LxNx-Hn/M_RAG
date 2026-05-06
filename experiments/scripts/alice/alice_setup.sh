#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$ROOT_DIR"

LOG_DIR="${ALICE_SETUP_LOG_DIR:-experiments/reports}"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/alice_setup_$(date -u +%Y%m%dT%H%M%SZ).log"

echo "[Alice Setup] repository: $ROOT_DIR" | tee "$LOG_FILE"
echo "[Alice Setup] git ref: $(git rev-parse --short HEAD 2>/dev/null || echo unknown)" | tee -a "$LOG_FILE"
echo "[Alice Setup] python: $(python --version 2>&1)" | tee -a "$LOG_FILE"

python - <<'PY' | tee -a "$LOG_FILE"
import sys
print("python_executable", sys.executable)
print("python_version", ".".join(map(str, sys.version_info[:3])))
if sys.version_info < (3, 10):
    raise SystemExit("Python 3.10 or newer is recommended for Alice execution.")
PY

if command -v nvidia-smi >/dev/null 2>&1; then
  echo "[Alice Setup] nvidia-smi:" | tee -a "$LOG_FILE"
  nvidia-smi | tee -a "$LOG_FILE"
else
  echo "[Alice Setup] nvidia-smi not found." | tee -a "$LOG_FILE"
fi

python - <<'PY' | tee -a "$LOG_FILE"
try:
    import torch
except Exception as exc:
    print("torch_available false")
    print("torch_import_error", type(exc).__name__, str(exc)[:300])
else:
    print("torch_available true")
    print("cuda_available", torch.cuda.is_available())
    if torch.cuda.is_available():
        print("device_count", torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            p = torch.cuda.get_device_properties(i)
            print("device", i, p.name, "total_memory_gb", round(p.total_memory / 1024**3, 2))
PY

if [ "${CREATE_VENV:-0}" = "1" ]; then
  if [ ! -d ".venv" ]; then
    python -m venv .venv
  fi
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip
fi

if [ "${SKIP_PIP_INSTALL:-0}" != "1" ]; then
  if [ -f "backend/requirements.txt" ]; then
    python -m pip install -r backend/requirements.txt
  else
    echo "[Alice Setup] backend/requirements.txt not found; skipping pip install." | tee -a "$LOG_FILE"
  fi
else
  echo "[Alice Setup] SKIP_PIP_INSTALL=1; skipping dependency install." | tee -a "$LOG_FILE"
fi

if [ "${ALLOW_MODEL_DOWNLOAD:-0}" = "1" ]; then
  echo "[Alice Setup] ALLOW_MODEL_DOWNLOAD=1 set. User approved model cache preparation." | tee -a "$LOG_FILE"
  echo "[Alice Setup] No repository script is invoked here to avoid accidental model execution." | tee -a "$LOG_FILE"
else
  echo "[Alice Setup] Model download skipped. Set ALLOW_MODEL_DOWNLOAD=1 only when ready." | tee -a "$LOG_FILE"
fi

echo "[Alice Setup] setup_log: $LOG_FILE"
