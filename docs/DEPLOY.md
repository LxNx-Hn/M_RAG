# M-RAG 배포 가이드

## 목차
1. [시스템 요구사항](#1-시스템-요구사항)
2. [로컬 개발 환경 설정](#2-로컬-개발-환경-설정)
3. [다중 사용자 동시 접속 배포](#3-다중-사용자-동시-접속-배포)
4. [RunPod GPU 서버 배포](#4-runpod-gpu-서버-배포)
5. [Docker 컨테이너 배포](#5-docker-컨테이너-배포)
6. [모델 다운로드 및 캐싱](#6-모델-다운로드-및-캐싱)
7. [환경 변수 설정](#7-환경-변수-설정)
8. [실행 및 검증](#8-실행-및-검증)
9. [트러블슈팅](#9-트러블슈팅)

---

## 1. 시스템 요구사항

### 최소 사양 (검색만 가능, 생성 모듈 비활성화)

| 항목 | 요구사항 |
|---|---|
| OS | Windows 10+, Ubuntu 20.04+, macOS 12+ |
| Python | 3.10 이상 |
| RAM | 16GB |
| 저장공간 | 10GB (임베딩 모델 + ChromaDB) |
| GPU | 불필요 |

### 권장 사양 (전체 기능)

| 항목 | 요구사항 |
|---|---|
| OS | Ubuntu 22.04 LTS |
| Python | 3.10~3.12 |
| RAM | 32GB |
| VRAM | 24GB 이상 (A100 40GB 권장) |
| 저장공간 | 50GB |
| GPU | NVIDIA A100 / A6000 / RTX 4090 |
| CUDA | 12.1 이상 |

### 모델별 VRAM 요구량

| 모델 | VRAM (FP16) | 용도 |
|---|---|---|
| BGE-M3 | ~2GB | 임베딩 |
| ms-marco-MiniLM-L-6-v2 | ~0.5GB | 재랭킹 |
| MIDM-2.0-Base-Instruct (11.5B) | ~23GB (bfloat16) | 생성 (메인) |
| Llama-3.1-8B-Instruct | ~16GB | 생성 (비교 실험) |
| **합계 (동시 로드)** | **~18.5GB** | |

> CAD(Contrastive Decoding)는 생성 시 동일 모델을 2회 forward pass하므로 추가 VRAM ~2GB가 필요합니다.

---

## 2. 로컬 개발 환경 설정

### 2.1 Python 가상환경

```bash
# 프로젝트 디렉토리로 이동
cd M_RAG

# 가상환경 생성 및 활성화
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 2.2 의존성 설치

```bash
# PyTorch (CUDA 12.1 기준 — 본인 환경에 맞게 변경)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# CPU 전용 (GPU 없는 개발 환경)
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# 프로젝트 의존성
pip install -r requirements.txt
```

### 2.3 로컬 실행

```bash
# FastAPI 백엔드
uvicorn api.main:app --host 0.0.0.0 --port 8000

# 프론트엔드 (별도 터미널)
cd frontend && npm run dev   # http://localhost:5173

# Swagger 문서: http://localhost:8000/docs
```

---

## 3. 다중 사용자 동시 접속 배포

### 3.1 프로덕션 구성 요약

| 서비스 | 포트 | 역할 |
|---|---|---|
| FastAPI (uvicorn) | 8000 | RAG 파이프라인 API, JWT 인증, SSE 스트리밍 |
| React (Nginx) | 3000 | SPA 프론트엔드 서빙 |
| PostgreSQL | 5432 | 사용자/대화 기록 DB |
| ChromaDB | (파일) | 벡터 인덱스 영속 저장 |

### 3.2 프로덕션 아키텍처

```
사용자 브라우저
      │
      ▼
┌──────────┐     ┌──────────────────────────┐
│  Nginx   │────►│   FastAPI (:8000)        │
│  :443    │     │   uvicorn --workers 1    │
│  (SSL)   │     │   async I/O 동시 처리     │
└──────────┘     └──────────┬───────────────┘
                            │
              ┌─────────────▼──────────────┐
              │  GPU: MIDM-2.0 (bfloat16)  │
              │  CPU: BGE-M3 + Reranker    │
              │  DB:  ChromaDB (persistent) │
              └────────────────────────────┘
```

### 3.3 Nginx 리버스 프록시 설정

```nginx
# /etc/nginx/sites-available/m-rag
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;

    # 업로드 크기 제한
    client_max_body_size 50M;

    # API 백엔드
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300s;  # LLM 생성에 시간 소요
    }

    # Swagger 문서
    location /docs {
        proxy_pass http://127.0.0.1:8000;
    }
    location /openapi.json {
        proxy_pass http://127.0.0.1:8000;
    }

    # 정적 파일 (프론트엔드)
    location / {
        root /var/www/m-rag/dist;  # React 빌드 결과물
        try_files $uri $uri/ /index.html;
    }
}
```

### 3.4 프로세스 관리 (systemd)

```ini
# /etc/systemd/system/m-rag.service
[Unit]
Description=M-RAG FastAPI Server
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/m-rag
Environment="LOAD_GPU_MODELS=true"
Environment="HF_HOME=/opt/m-rag/.cache/huggingface"
ExecStart=/opt/m-rag/.venv/bin/uvicorn api.main:app \
    --host 127.0.0.1 --port 8000 --workers 1 --log-level info
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable m-rag
sudo systemctl start m-rag
sudo systemctl status m-rag
```

### 3.5 동시성 처리 주의사항

| 제약 | 이유 | 대응 |
|---|---|---|
| `workers=1` 고정 | GPU 모델은 프로세스 간 공유 불가 | async I/O로 동시성 확보 |
| LLM 추론은 동기적 | torch forward pass는 GIL 해제 안 됨 | 요청 큐잉 (동시 2-3건 처리) |
| 임베딩은 병렬 가능 | sentence-transformers 배치 처리 | 배치 인코딩으로 처리량 향상 |
| ChromaDB 동시 쓰기 | PersistentClient는 단일 프로세스 | 쓰기는 순차, 읽기는 병렬 |

> **규모 확장이 필요하면**: LLM 추론을 vLLM/TGI로 분리하고, FastAPI는 추론 서버에 HTTP 호출하는 구조로 전환.

---

## 4. RunPod GPU 서버 배포

### 3.1 Pod 생성

1. [RunPod](https://runpod.io) 로그인
2. **GPU Pods** → **Deploy**
3. 설정:
   - GPU: `NVIDIA A100 40GB` (또는 `A100 80GB`)
   - Template: `RunPod PyTorch 2.1` (CUDA 12.1 포함)
   - Disk: `50GB` (Container) + `50GB` (Volume, 모델 캐시용)
   - Expose Port: `8000` (API) + `3000` (React, 선택)

### 3.2 Pod 접속 및 환경 설정

```bash
# SSH 접속 (RunPod 대시보드에서 SSH 명령 확인)
ssh root@<pod-ip> -p <port> -i ~/.ssh/id_ed25519

# 프로젝트 클론
cd /workspace
git clone <your-repo-url> M_RAG
cd M_RAG

# 가상환경 (RunPod는 보통 시스템 Python 사용)
pip install -r requirements.txt

# 모델 캐시 디렉토리 설정 (Volume 마운트 경로)
export HF_HOME=/workspace/hf_cache
export TRANSFORMERS_CACHE=/workspace/hf_cache

# 모델 사전 다운로드 (Section 5 참조)
python -c "
from sentence_transformers import SentenceTransformer
SentenceTransformer('BAAI/bge-m3')
print('BGE-M3 downloaded')
"

python -c "
from sentence_transformers import CrossEncoder
CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
print('Reranker downloaded')
"

python -c "
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
tokenizer = AutoTokenizer.from_pretrained('K-intelligence/Midm-2.0-Base-Instruct', trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained('K-intelligence/Midm-2.0-Base-Instruct', torch_dtype=torch.bfloat16, device_map='auto', trust_remote_code=True)
print('MIDM downloaded')
"
```

### 4.3 실행

```bash
mkdir -p logs

# FastAPI 백엔드 (프로덕션)
LOAD_GPU_MODELS=true nohup uvicorn api.main:app \
  --host 0.0.0.0 --port 8000 --workers 1 \
  > logs/api.log 2>&1 &

# 로그 확인
tail -f logs/api.log
```

RunPod 대시보드 → **Connect** → **HTTP Service [8000]** 클릭.
Swagger 문서: `http://<pod-ip>:8000/docs`

### 3.4 비용 최적화

- **Spot Instance** 사용 시 ~70% 절감 (작업 중간에 중단될 수 있음)
- 사용하지 않을 때 **Pod Stop** → 디스크 비용만 발생
- Volume에 모델 캐시를 저장하면 재시작 시 다운로드 불필요

---

## 4. Docker 컨테이너 배포

### 4.1 Dockerfile

프로젝트 루트에 `Dockerfile`을 생성:

```dockerfile
FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

WORKDIR /app

# 시스템 패키지
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY . .

# 데이터/DB 디렉토리
RUN mkdir -p data chroma_db logs

# 포트
EXPOSE 8000

# 헬스체크
HEALTHCHECK CMD curl --fail http://localhost:8000/health || exit 1

# 실행
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
```

### 4.2 빌드 및 실행

```bash
# 빌드
docker build -t m-rag:latest .

# GPU 실행 (NVIDIA Container Toolkit 필요)
docker run -d \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/chroma_db:/app/chroma_db \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  -e LOAD_GPU_MODELS=true \
  --name m-rag \
  m-rag:latest

# CPU 전용 실행
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/chroma_db:/app/chroma_db \
  --name m-rag \
  m-rag:latest
```

### 4.3 Docker Compose

```yaml
# docker-compose.yml
version: "3.8"
services:
  m-rag:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./chroma_db:/app/chroma_db
      - hf_cache:/root/.cache/huggingface
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

volumes:
  hf_cache:
```

```bash
docker compose up -d
```

---

## 5. 모델 다운로드 및 캐싱

### 5.1 사전 다운로드 스크립트

`scripts/download_models.py`:

```python
"""모든 모델을 사전 다운로드하는 스크립트"""
from sentence_transformers import SentenceTransformer, CrossEncoder
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

print("[1/3] Downloading BGE-M3 embedding model...")
SentenceTransformer("BAAI/bge-m3")
print("  Done.")

print("[2/3] Downloading reranker model...")
CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
print("  Done.")

print("[3/3] Downloading MIDM-2.0-Base-Instruct...")
tokenizer = AutoTokenizer.from_pretrained(
    "K-intelligence/Midm-2.0-Base-Instruct",
    trust_remote_code=True,
)
model = AutoModelForCausalLM.from_pretrained(
    "K-intelligence/Midm-2.0-Base-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True,
)
print("  Done.")

print("\nAll models downloaded successfully!")
```

```bash
python scripts/download_models.py
```

### 5.2 캐시 경로

| 환경 | 기본 캐시 경로 |
|---|---|
| Linux | `~/.cache/huggingface/hub/` |
| Windows | `C:\Users\<user>\.cache\huggingface\hub\` |
| Docker | `/root/.cache/huggingface/hub/` |
| RunPod | `/workspace/hf_cache/` (Volume 마운트 권장) |

환경 변수로 변경:

```bash
export HF_HOME=/path/to/cache
export TRANSFORMERS_CACHE=/path/to/cache
```

---

## 6. 환경 변수 설정

| 변수 | 기본값 | 설명 |
|---|---|---|
| `HF_HOME` | `~/.cache/huggingface` | HuggingFace 모델 캐시 경로 |
| `CUDA_VISIBLE_DEVICES` | `0` | 사용할 GPU 번호 |
| `TOKENIZERS_PARALLELISM` | `false` | 토크나이저 병렬 처리 충돌 방지 |

`.env` 파일 예시:

```env
HF_HOME=/workspace/hf_cache
CUDA_VISIBLE_DEVICES=0
TOKENIZERS_PARALLELISM=false
```

---

## 7. 실행 및 검증

### 7.1 기본 실행

```bash
LOAD_GPU_MODELS=true uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 7.2 헬스체크

```bash
curl http://localhost:8000/health
```

### 7.3 기능별 검증 체크리스트

| # | 검증 항목 | 방법 |
|---|---|---|
| 1 | PDF 업로드 | 좌측 패널에서 PDF 업로드 → 논문 카드 표시 확인 |
| 2 | 섹션 인식 | 논문 카드에 섹션 태그(Abstract, Method 등) 표시 확인 |
| 3 | 단순 QA (A) | "이 논문에서 사용한 데이터셋이 뭐야?" 질의 |
| 4 | 섹션 특화 (B) | "결과가 어떻게 나왔어?" → 파이프라인 배지 `📑 섹션 특화 검색` 확인 |
| 5 | 논문 비교 (C) | PDF 2개 업로드 후 "두 논문 비교해줘" 질의 |
| 6 | 인용 추적 (D) | "인용 논문 분석해줘" → 인용 논문 목록 펼침 패널 확인 |
| 7 | 전체 요약 (E) | "이 논문 전체 요약해줘" → 구조화된 요약 확인 |
| 8 | CAD 토글 | 설정에서 CAD ON/OFF 후 동일 질의 비교 |
| 9 | 출처 표시 | 답변 하단 `📌 출처` 펼침 패널 확인 |

### 7.4 평가 실행

```bash
# RAGAS 평가
python -c "
from evaluation.ragas_eval import RAGASEvaluator, load_test_queries
samples = load_test_queries()
print(f'Loaded {len(samples)} test queries')
"

# Ablation Study (GPU 환경에서)
python -c "
from evaluation.ablation_study import ABLATION_CONFIGS
for c in ABLATION_CONFIGS:
    print(f'  {c.name}')
"
```

---

## 8. 트러블슈팅

### 8.1 자주 발생하는 문제

| 문제 | 원인 | 해결 |
|---|---|---|
| `CUDA out of memory` | VRAM 부족 | `config.py`에서 `MAX_NEW_TOKENS` 줄이기, 또는 더 큰 GPU 사용 |
| `ModuleNotFoundError: fitz` | pymupdf 미설치 | `pip install pymupdf` (패키지명 ≠ import명) |
| `ChromaDB migration error` | DB 버전 불일치 | `chroma_db/` 폴더 삭제 후 재시작 |
| 임베딩 모델 로딩 느림 | 첫 다운로드 | Section 5 사전 다운로드 스크립트 실행 |
| `trust_remote_code=True` 경고 | MIDM 모델 특성 | 정상 동작, 무시 가능 |
| BM25 검색 결과 없음 | `fit_bm25()` 미호출 | PDF 업로드 후 자동 호출됨. 수동: `hybrid_retriever.fit_bm25("papers")` |
| 한글 깨짐 | PDF 인코딩 문제 | pymupdf가 대부분 처리. 스캔 PDF는 OCR 필요 (미지원) |

### 8.2 GPU 확인

```bash
# CUDA 사용 가능 여부
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"

# VRAM 사용량 확인
nvidia-smi
```

### 8.3 로그 레벨 변경

`api/main.py` 상단의 로깅 레벨 변경:

```python
logging.basicConfig(level=logging.DEBUG)  # 상세 로그
```

### 8.4 ChromaDB 초기화

데이터 문제 시 벡터DB 초기화:

```bash
rm -rf chroma_db/
# 앱 재시작하면 자동 재생성
```

---

## 부록: 포트 포워딩 (원격 서버 접속)

RunPod/원격 서버에서 로컬 접속:

```bash
# SSH 터널링
ssh -L 8000:localhost:8000 root@<server-ip> -p <port>
```

브라우저에서 `http://localhost:8000/docs` 접속 (Swagger UI).
