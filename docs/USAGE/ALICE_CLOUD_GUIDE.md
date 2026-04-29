# Alice Cloud GPU 실험 가이드

## 목적

Alice Cloud 환경에서 M-RAG 논문 실험을 실행하고, CAD 영향 구간만 선별 재실행한다.

## SSH 접속

Windows PowerShell 기준 접속 명령

```powershell
ssh -i "C:\Users\KiKi\Downloads\elice-cloud-ondemand-8f830e65-6dc9-4a87-b14a-dddf119010e5.pem" elicer@central-01.tcp.tunnel.elice.io -p 36319
```

## 권장 인스턴스

- A100 40GB 이상
- Storage 256GB 이상
- CUDA 포함 환경
- Docker가 없다면 `git clone + venv + SQLite` 경로 사용

## 저장소 준비

```bash
cd ~
git clone https://github.com/LxNx-Hn/M_RAG.git
cd M_RAG
```

이미 clone되어 있으면 fast-forward 기준으로 최신화한다.

```bash
git fetch origin
git pull --ff-only origin main
```

## 가상환경 준비

```bash
python -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend/requirements.txt
```

CUDA 확인

```bash
python -c "import torch; print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

## 환경변수

```bash
export JWT_SECRET_KEY=mrag-experiment-local-secret-2026
export LOAD_GPU_MODELS=true
export GENERATION_MODEL=K-intelligence/Midm-2.0-Base-Instruct
export DATABASE_URL=sqlite+aiosqlite:///./mrag.db
export MRAG_API_BASE=http://127.0.0.1:8000
export HF_HOME=$HOME/.cache/huggingface
export TRANSFORMERS_CACHE=$HF_HOME
export HF_HUB_CACHE=$HF_HOME
# Runner account credentials (defaults shown, env-overridable)
export MRAG_RUNNER_EMAIL=runner@mrag.local
export MRAG_RUNNER_USERNAME=master_runner
export MRAG_RUNNER_PASSWORD=MragRunner!2026x
```

## 모델 및 PDF 준비

```bash
cd ~/M_RAG/backend
source ../.venv/bin/activate
python scripts/download_models.py --llm-model K-intelligence/Midm-2.0-Base-Instruct
python scripts/download_test_papers.py --dry-run
python scripts/download_test_papers.py
```

`git pull` 후 `backend/data/`에 8편 전부 포함되어 있다. 별도 수동 복사는
필요 없다. 영어 NLP 4편은 필요하면 `download_test_papers.py`로 최신 arXiv
PDF로 다시 받아 덮어쓸 수 있다.

현재 기본 8편 논문 자산:

| 언어 | doc_id |
|------|--------|
| 영어 | paper_nlp_bge, paper_nlp_rag, paper_nlp_cad, paper_nlp_raptor |
| 한국어/MIDM | paper_midm, paper_ko_rag_eval_framework, paper_ko_rag_rrf_chunking, paper_ko_cad_contrastive |

## 쿼리 생성

`OPENAI_API_KEY`가 설정되어 있으면 `master_run.py`가 인덱싱 뒤 Track 1 논문별 특화 쿼리를 자동 생성한다. 저장소의 `track1_queries.json`은 런타임 생성을 위한 자리표시 파일이다. 생성 결과를 미리 확인하거나 수동 재생성할 때는 다음 명령을 사용한다.

```bash
export OPENAI_API_KEY=sk-...
export MRAG_API_TOKEN=...
python scripts/generate_queries.py \
  --papers paper_nlp_bge paper_nlp_rag paper_nlp_cad paper_nlp_raptor \
           paper_midm paper_ko_rag_eval_framework paper_ko_rag_rrf_chunking paper_ko_cad_contrastive \
  --output evaluation/data/track1_queries.json \
  --openai-model gpt-4o \
  --token "$MRAG_API_TOKEN" \
  --overwrite
```

## 전체 실험 실행

```bash
cd ~/M_RAG/backend
source ../.venv/bin/activate
export OPENAI_API_KEY=sk-...
nohup python scripts/master_run.py --skip-download --push-results > scripts/master_run_stdout.log 2>&1 &
echo $!
```

진행 확인

```bash
tail -f ~/M_RAG/backend/scripts/master_run.log
```

## CAD 영향 구간 부분 재실행

부분 재실행은 다음 절차를 따른다.

1. 현재 진행 상태 확인
2. 로그와 결과 백업
3. `git pull --ff-only`
4. API 서버 기동
5. CAD 영향 구간만 재실행

현재 단계 확인

```bash
cd ~/M_RAG/backend
grep -n "STEP " scripts/master_run.log | tail -n 20
```

백업

```bash
bash scripts/experiments/backup_alice_run.sh
```

부분 재실행

```bash
bash scripts/experiments/rerun_cad_affected.sh
```

이 스크립트는 다음을 수행한다.

- `scripts/master_run.log` 백업
- `evaluation/results/` 백업
- 기존 `master_run.py` 및 `uvicorn` 프로세스 정리
- `git pull --ff-only origin main`
- SQLite + Base 모델 기준 API 서버 기동
- runner 계정으로 토큰 획득 (register-or-login)
- Track 1 Full System 재실행
- Track 1 decoder 중 CAD 영향 config 재실행
- Track 1 alpha/beta sweep 재실행
- Track 2 domain 재실행
- `TABLES.md` 재생성
- 기존 결과 파일은 `_archive/<timestamp>/`로 보존 (삭제하지 않음)

## 결과 확인

```bash
cat ~/M_RAG/backend/evaluation/results/TABLES.md
```

## 자주 나는 문제

### Docker command not found

Alice 환경에 Docker가 없다는 뜻이다. `git clone + venv` 경로를 사용한다.

### GPU 사용량이 0

CPU용 torch가 설치되었을 가능성이 있다. CUDA wheel로 다시 설치한다.

```bash
pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu121
```

### 503 during indexing

API 서버가 DB 또는 모델 초기화를 끝내지 못했을 수 있다. `scripts/master_run.log`와 `/health` 상태를 확인한다.

### git pull 전 로그나 결과가 사라질까 걱정되는 경우

`scripts/master_run.log`는 git 추적 대상이 아니고, `evaluation/results`는 재실행 중 같은 경로에 다시 기록된다. Alice에서는 항상 `backup_alice_run.sh`를 먼저 실행한 뒤 pull한다.
