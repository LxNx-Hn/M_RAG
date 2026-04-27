# Alice Cloud GPU 실험 가이드

- 기준 날짜: 2026-04-27
- 대상 환경: Alice Cloud GPU 인스턴스 (A100 40GB 이상 권장)
- 작업 경로: `/home/elicer/M_RAG`

---

## 빠른 시작 요약

```bash
# 1. 레포 클론
git clone https://github.com/lxnx-hn/M_RAG.git /home/elicer/M_RAG

# 2. 환경 설정
cd /home/elicer/M_RAG
python -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend/requirements.txt

# 3. 환경변수 설정 (.env 파일)
cp backend/.env.example backend/.env
# → OPENAI_API_KEY 입력 필수

# 4. 모델 캐시
export HF_HOME=/home/elicer/.cache/huggingface
cd backend
python scripts/download_models.py

# 5. 논문 PDF 다운로드 (자동 또는 수동)
python scripts/download_test_papers.py

# 6. 실험 전체 실행
python scripts/master_run.py
```

---

## 1. GPU 인스턴스 사양 요구사항

| 항목 | 최소 | 권장 |
|---|---|---|
| GPU VRAM | 24 GB | 40 GB (A100) |
| 시스템 RAM | 32 GB | 64 GB |
| 디스크 | 100 GB | 200 GB |
| Python | 3.10 이상 | 3.11 |
| CUDA | 12.1 이상 | 12.1 |

Base 모델 (`K-intelligence/Midm-2.0-Base-Instruct`)은 VRAM 약 14–18 GB 사용.  
임베딩 모델 + 리랭커 + 생성 모델 동시 로드 시 24 GB 이상 확보 권장.

---

## 2. 최초 환경 설정

### 2-1. 레포 클론

```bash
git clone https://github.com/lxnx-hn/M_RAG.git /home/elicer/M_RAG
cd /home/elicer/M_RAG
```

### 2-2. Python 가상환경 생성

```bash
python -m venv .venv
source .venv/bin/activate
```

활성화 확인:
```bash
which python
# /home/elicer/M_RAG/.venv/bin/python
```

### 2-3. 의존성 설치

```bash
# PyTorch (CUDA 12.1 빌드)
pip install torch --index-url https://download.pytorch.org/whl/cu121

# 나머지 의존성
pip install -r backend/requirements.txt
```

설치 확인:
```bash
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"
# True  NVIDIA A100-SXM4-40GB
```

---

## 3. 환경변수 설정

### 3-1. .env 파일 생성

```bash
cd /home/elicer/M_RAG
cp backend/.env.example backend/.env
```

### 3-2. 필수 항목 설정

`backend/.env` 를 편집기로 열어 다음을 설정:

```env
# ── 필수 ──
OPENAI_API_KEY=sk-...       # GT 생성 (GPT-4o). 없으면 로컬 Naive RAG fallback

# ── 실험 경로 기본값 (수정 불필요) ──
GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct
LOAD_GPU_MODELS=true
DATABASE_URL=sqlite+aiosqlite:///./mrag.db

# ── JWT: master_run.py가 자동 발급 (수정 불필요) ──
# JWT_SECRET_KEY=            # 비워두면 master_run.py가 ephemeral 키 자동 생성
```

> **OPENAI_API_KEY 없이 실행하면:** STEP 5에서 로컬 Naive RAG로 GT를 생성합니다.  
> GT의 독립성이 낮아지므로 논문 실험에는 OPENAI_API_KEY 설정을 강력히 권장합니다.

### 3-3. HuggingFace 캐시 경로 설정 (선택)

Alice Cloud 영구 스토리지가 있다면:
```bash
export HF_HOME=/home/elicer/.cache/huggingface
```

설정 없으면 `backend/.cache/huggingface` 를 자동으로 사용합니다.

---

## 4. 모델 다운로드

```bash
cd /home/elicer/M_RAG/backend
python scripts/download_models.py
```

다운로드 대상:
- `K-intelligence/Midm-2.0-Base-Instruct` — 생성 모델 (논문 기준)
- `BAAI/bge-m3` — 임베딩 모델
- `cross-encoder/ms-marco-MiniLM-L-6-v2` — 리랭커

예상 소요 시간: 30–60분 (첫 실행 기준, 네트워크 속도에 따라 상이).

---

## 5. 논문 PDF 준비

### 방법 A: 자동 다운로드 스크립트

```bash
cd /home/elicer/M_RAG/backend
python scripts/download_test_papers.py
```

다운로드 대상 논문 (7편):
| 파일명 | 논문 |
|---|---|
| `paper_nlp_bge.pdf` | BGE-M3 임베딩 |
| `paper_nlp_rag.pdf` | RAG 기초 |
| `paper_nlp_cad.pdf` | CAD 논문 |
| `paper_nlp_raptor.pdf` | RAPTOR |
| `1810.04805_bert.pdf` | BERT |
| `2101.08577.pdf` | Cross-lingual 논문 |
| `paper_korean.pdf` | 한국어 NLP 논문 |

### 방법 B: 수동 업로드

Alice Cloud 파일 업로드 기능을 이용해 PDF를 `backend/data/` 경로에 직접 업로드 후:
```bash
python scripts/master_run.py --skip-download
```

---

## 6. Git Push 자격증명 설정 (결과 자동 회수용)

실험 완료 후 `master_run.py` 가 STEP 13에서 결과를 자동 commit + push 합니다.  
로컬 PC에서 `git pull` 만으로 결과를 받으려면 push 자격증명이 필요합니다.

### Personal Access Token 방식 (권장)

```bash
# GitHub Personal Access Token 발급: github.com → Settings → Developer settings → PAT
git remote set-url origin https://lxnx-hn:<TOKEN>@github.com/lxnx-hn/M_RAG.git
git config user.email "lxnx.kiki@gmail.com"
git config user.name "KiKi"
```

확인:
```bash
git push --dry-run origin main
# 오류 없으면 정상
```

> push 자격증명이 없어도 실험은 완주됩니다. STEP 13 실패는 `abort_on_failure=False` 이므로 파이프라인을 중단하지 않습니다. 이 경우 Alice Cloud에서 직접 결과 파일을 복사해야 합니다.

---

## 7. 실험 실행

### 7-1. 표준 실행 (PDF 이미 있을 때)

```bash
cd /home/elicer/M_RAG/backend
source ../.venv/bin/activate

python scripts/master_run.py --skip-download
```

### 7-2. 처음부터 실행 (PDF 자동 다운로드 포함)

```bash
python scripts/master_run.py
```

### 7-3. 백그라운드 실행 (세션 종료에도 안전)

```bash
nohup python scripts/master_run.py --skip-download \
  > /home/elicer/M_RAG/backend/scripts/master_run_stdout.log 2>&1 &

echo "PID: $!"
```

진행 확인:
```bash
tail -f /home/elicer/M_RAG/backend/scripts/master_run.log
```

### 7-4. 실험 단계 구성

| STEP | 내용 | abort_on_failure |
|---|---|---|
| 1 | 패키지 설치 확인 | 아니오 |
| 2 | PDF 다운로드 | 아니오 |
| 3 | API 서버 기동 | **예** |
| 4 | 논문 인덱싱 (7편 ChromaDB) | **예** |
| 5 | GT 생성 (GPT-4o 또는 로컬) | **예** |
| 6 | Track 1 ablation → `table1_track1.json` | **예** |
| 7 | decoder ablation → `table2_decoder.json` | **예** |
| 8 | CAD alpha sweep → `table2_alpha.json` | **예** |
| 9 | SCD beta sweep → `table2_beta.json` | **예** |
| 10 | Track 2 domain → `table3_domain.json` | **예** |
| 11 | 마크다운 변환 → `TABLES.md` | **예** |
| 12 | 결과 검증 | **예** |
| 13 | git push | 아니오 |
| 14 | API 서버 종료 | 아니오 |

abort_on_failure=예 인 STEP은 실패 시 파이프라인이 즉시 중단됩니다.

### 7-5. 예상 소요 시간

| STEP | 예상 시간 |
|---|---|
| 3 서버 기동 (모델 로드) | 5–15분 |
| 4 논문 인덱싱 | 10–20분 |
| 5 GT 생성 (GPT-4o) | 20–40분 |
| 6–10 평가 전체 | 4–8시간 |
| **총합** | **5–10시간** |

---

## 8. 중단 재개 (--resume)

STEP 6–10 모두 `--resume` 플래그를 기본으로 전달합니다.  
중단된 경우 그냥 다시 실행하면 완료된 config/paper 는 건너뜁니다:

```bash
python scripts/master_run.py --skip-download
```

완료 판정 기준: 결과 JSON 내 `"status": "completed"` 필드.

---

## 9. 결과 확인

### 9-1. 로컬 확인

```bash
ls backend/evaluation/results/
# table1_track1.json  table2_decoder.json  table2_alpha.json
# table2_beta.json    table3_domain.json   TABLES.md

cat backend/evaluation/results/TABLES.md
```

### 9-2. 로컬 PC에서 결과 수신 (git pull)

```bash
# 로컬 PC에서
cd /path/to/M_RAG
git pull origin main
ls backend/evaluation/results/
```

---

## 10. 서버 기동 단독 확인 (선택)

master_run.py 를 쓰지 않고 API 서버만 먼저 확인하고 싶을 때:

```bash
cd /home/elicer/M_RAG/backend
source ../.venv/bin/activate

export JWT_SECRET_KEY=mrag-experiment-local-secret-2026
export LOAD_GPU_MODELS=true
export GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct
export DATABASE_URL=sqlite+aiosqlite:///./mrag.db

uvicorn api.main:app --host 0.0.0.0 --port 8000
```

```bash
# 다른 터미널
curl http://localhost:8000/health
# {"status":"ok"}
```

---

## 11. 트러블슈팅

### CUDA out of memory

원인: 임베딩 + 리랭커 + 생성 모델이 동시 로드되면 VRAM 부족 가능.  
대응: VRAM 40GB 이상 인스턴스로 업그레이드. 또는 Mini 모델로 smoke test:

```bash
GENERATION_MODEL=K-intelligence/Midm-2.0-Mini-Instruct \
  python scripts/master_run.py --skip-download
```

### API 서버가 600초 내 healthy 상태 미달

원인: 모델 로드 지연, 네트워크 파일시스템 속도 저하.  
대응:
1. `master_run.log` 에서 uvicorn 에러 확인
2. `backend/.cache/huggingface` 에 모델 파일 존재 여부 확인
3. GPU VRAM 확인: `nvidia-smi`

### 논문 인덱싱 실패

원인: PDF 파일 누락, API 서버 미기동.  
대응:
```bash
ls backend/data/*.pdf
curl http://localhost:8000/health
```

### GT 생성에서 0개 생성 (STEP 5 abort)

원인: OPENAI_API_KEY 무효 또는 네트워크 차단.  
대응: `.env` 에서 OPENAI_API_KEY 확인 또는 API 키 없이 재실행 (로컬 fallback):
```bash
# .env에서 OPENAI_API_KEY 줄 삭제 또는 주석 처리 후 재실행
python scripts/master_run.py --skip-download
```

### git push 실패 (STEP 13)

원인: push 자격증명 미설정. 파이프라인은 계속 진행됨 (abort=False).  
대응:
```bash
# 결과 직접 확인
ls backend/evaluation/results/
# 또는 자격증명 설정 후 수동 push
git push origin main
```

### 락 파일 잔존 (재실행 불가)

```bash
rm backend/scripts/master_run.lock
```

---

## 12. 핵심 파일 경로 참조

| 파일 | 설명 |
|---|---|
| `backend/scripts/master_run.py` | 전체 실험 오케스트레이터 |
| `backend/scripts/master_run.log` | 실험 전체 로그 |
| `backend/evaluation/data/track1_queries.json` | Track 1 쿼리 (60개, 7편) |
| `backend/evaluation/data/track2_queries.json` | Track 2 쿼리 (28개, 4편) |
| `backend/evaluation/data/pseudo_gt_track1.json` | STEP 5에서 생성, gitignore |
| `backend/evaluation/data/pseudo_gt_track2.json` | STEP 5에서 생성, gitignore |
| `backend/evaluation/results/` | 결과 JSON + TABLES.md (git 추적) |
| `backend/data/` | PDF 원본 (gitignore) |
| `backend/.cache/huggingface/` | HF 모델 캐시 (gitignore) |
| `backend/chroma_db/` | 벡터 DB (gitignore) |
