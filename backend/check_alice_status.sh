#!/usr/bin/env bash
set -euo pipefail

cd /home/elicer/M_RAG/backend

echo "--- master_run / uvicorn ---"
ps -eo pid,ppid,etime,%cpu,%mem,cmd | grep -E "run_alice_full|master_run.py|uvicorn" | grep -v grep || true

echo
echo "--- gpu ---"
nvidia-smi --query-gpu=utilization.gpu,memory.used,memory.total --format=csv,noheader

echo
echo "--- latest log tail ---"
tail -n 40 alice_full.log || true
