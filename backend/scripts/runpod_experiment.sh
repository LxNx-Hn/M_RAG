#!/bin/bash
# ================================================
# M-RAG 전체 실험 — RunPod 자동화 스크립트
# ================================================
#
# 지원 모델:
#   - MIDM Mini (2.3B, bfloat16 ~5GB)  → 12GB+ GPU
#   - MIDM Base (11.5B, bfloat16 ~23GB) → 24GB+ GPU (A100/H100)
#
# Usage:
#   # 1. RunPod에 스크립트 업로드
#   scp scripts/runpod_experiment.sh root@<pod-ip>:/workspace/
#
#   # 2-A. Base 모델 실행 (기본, A100/H100)
#   ssh root@<pod-ip> "bash /workspace/runpod_experiment.sh"
#
#   # 2-B. Mini 모델 실행 (RTX 3090/4090 등 12GB+)
#   ssh root@<pod-ip> "bash /workspace/runpod_experiment.sh mini"
#
#   # 2-C. 쿼리 수 조절 (빠른 테스트)
#   ssh root@<pod-ip> "bash /workspace/runpod_experiment.sh base 5"
#
#   # 3. 결과 다운로드
#   scp root@<pod-ip>:/workspace/M_RAG/backend/evaluation/results/*.json ./results/
#   scp root@<pod-ip>:/workspace/experiment_log.txt ./results/
#
# ================================================

set -e

MODEL_SIZE="${1:-base}"   # base or mini
MAX_QUERIES="${2:-10}"    # 쿼리 수 (기본 10)

echo "================================================"
echo "M-RAG Full Experiment on RunPod"
echo "Model: MIDM $MODEL_SIZE"
echo "Max queries: $MAX_QUERIES"
echo "Started: $(date)"
echo "================================================"

# ─── 1. 환경 설정 ───
cd /workspace

if [ ! -d "M_RAG" ]; then
    echo "[1/6] Cloning repository..."
    git clone https://github.com/<YOUR_USERNAME>/M_RAG.git
else
    echo "[1/6] Updating repository..."
    cd M_RAG && git pull && cd ..
fi

cd M_RAG/backend

# ─── 2. 의존성 설치 ───
echo "[2/6] Installing dependencies..."
pip install -q torch --index-url https://download.pytorch.org/whl/cu121
pip install -q -r requirements.txt
pip install -q accelerate

if [ "$MODEL_SIZE" = "base" ]; then
    pip install -q bitsandbytes>=0.43.0 2>/dev/null || true
fi

# ─── 3. 모델 다운로드 ───
echo "[3/6] Downloading models..."
export HF_HOME=/workspace/hf_cache
python scripts/download_models.py

# ─── 4. 실험용 논문 준비 (BERT paper) ───
echo "[4/6] Preparing test paper..."
PAPER_PDF="data/1810.04805_bert.pdf"

if [ ! -f "$PAPER_PDF" ]; then
    echo "  Downloading BERT paper from arXiv..."
    python -c "
import requests
r = requests.get('https://arxiv.org/pdf/1810.04805.pdf', timeout=60,
                 headers={'User-Agent': 'Mozilla/5.0'})
with open('$PAPER_PDF', 'wb') as f:
    f.write(r.content)
print(f'  Downloaded: {len(r.content)} bytes')
"
fi

# ─── 5. 모델 선택 ───
if [ "$MODEL_SIZE" = "mini" ]; then
    export GENERATION_MODEL="K-intelligence/Midm-2.0-Mini-Instruct"
    echo "[5/6] Using MIDM Mini (2.3B)"
else
    export GENERATION_MODEL="K-intelligence/Midm-2.0-Base-Instruct"
    echo "[5/6] Using MIDM Base (11.5B)"
fi
export LOAD_GPU_MODELS=true

# ─── 6. 전체 실험 실행 ───
echo "[6/6] Running experiments (Table 1~4, $MAX_QUERIES queries)..."
echo ""

python -X utf8 scripts/run_all_experiments.py \
    --paper-pdf "$PAPER_PDF" \
    --collection "runpod_${MODEL_SIZE}_eval" \
    --max-queries "$MAX_QUERIES" \
    2>&1 | tee /workspace/experiment_log.txt

# ─── 완료 ───
echo ""
echo "================================================"
echo "Experiment Complete!"
echo "Model: MIDM $MODEL_SIZE"
echo "Finished: $(date)"
echo "================================================"
echo ""
echo "Result files:"
ls -la evaluation/results/full_experiment_*.json 2>/dev/null || echo "  (no results found)"
echo ""
echo "Download:"
echo "  scp root@\$(hostname -I | awk '{print \$1}'):$(pwd)/evaluation/results/*.json ./results/"
echo "  scp root@\$(hostname -I | awk '{print \$1}'):/workspace/experiment_log.txt ./results/"
