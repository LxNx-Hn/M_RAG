# Alice Cloud GPU 실험 가이드

- 기준 날짜: 2026-04-28
- 대상 환경: Alice Cloud GPU 인스턴스 (A100 40GB 이상 권장)
- 작업 경로: `/home/elicer/M_RAG`

---

## 순서 요약

```text
1. 레포 클론
2. 패키지 설치
3. .env 파일 설정 (OPENAI_API_KEY)
4. git push 자격증명 설정
5. HuggingFace 모델 다운로드
6. 논문 PDF 다운로드
7. 실험 실행 (백그라운드)
8. 로그 확인
9. 결과 수신 (로컬 PC git pull)
```

---

## 1단계. 레포 클론

```bash
git clone https://github.com/lxnx-hn/M_RAG.git /home/elicer/M_RAG
cd /home/elicer/M_RAG
```

---

## 2단계. 패키지 설치

```bash
python -m venv .venv
source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend/requirements.txt
```

설치 확인:
```bash
python -c "import torch; print(torch.cuda.is_available())"
# True
```

---

## 3단계. .env 파일 설정

```bash
cp backend/.env.example backend/.env
nano backend/.env
```

`nano` 편집기가 열리면 `OPENAI_API_KEY=` 오른쪽에 키를 입력합니다:

```env
OPENAI_API_KEY=sk-...여기에입력
```

저장: `Ctrl+O` → `Enter` → `Ctrl+X`

> OPENAI_API_KEY 없이도 실행은 됩니다. 단, 평가 기준점(GT)을 로컬 모델로 생성해서 논문 결과 신뢰도가 낮아집니다.

---

## 4단계. git push 자격증명 설정

실험 완료 후 결과를 자동으로 push하려면 필요합니다.

**GitHub에서 토큰 발급:**

```text
github.com → Settings → Developer settings
→ Personal access tokens → Tokens (classic)
→ Generate new token → repo 권한 체크 → 생성
```

**Alice Cloud 터미널에서 입력 (작은따옴표로 감싸야 함):**
```bash
git remote set-url origin 'https://lxnx-hn:<발급한토큰>@github.com/lxnx-hn/M_RAG.git'
git config user.email "lxnx.kiki@gmail.com"
git config user.name "KiKi"
```

확인:
```bash
git push --dry-run origin main
# 오류 없으면 정상
```

> 이 설정 없이도 실험은 완주됩니다. 결과 파일은 Alice Cloud에 남아있고 나중에 수동 push 하면 됩니다.

---

## 5단계. HuggingFace 모델 다운로드

```bash
cd /home/elicer/M_RAG/backend
source ../.venv/bin/activate
python scripts/download_models.py
```

다운로드 대상 (첫 실행에 30–60분 소요):

- `K-intelligence/Midm-2.0-Base-Instruct` — 생성 모델
- `BAAI/bge-m3` — 임베딩 모델
- `cross-encoder/ms-marco-MiniLM-L-6-v2` — 리랭커

---

## 6단계. 논문 PDF 다운로드

```bash
cd /home/elicer/M_RAG/backend
python scripts/download_test_papers.py
```

다운로드 확인:
```bash
ls data/*.pdf
```

7개 파일이 있어야 합니다:

```text
paper_nlp_bge.pdf  paper_nlp_rag.pdf  paper_nlp_cad.pdf
paper_nlp_raptor.pdf  1810.04805_bert.pdf  2101.08577.pdf
paper_korean.pdf
```

> 스크립트 다운로드가 실패하면 로컬 PC에서 파일을 준비해 Alice Cloud 파일 업로드 기능으로 `backend/data/` 경로에 올립니다.

---

## 7단계. 실험 실행 (백그라운드)

세션이 끊겨도 실험이 계속 돌도록 `nohup`으로 실행합니다.

```bash
cd /home/elicer/M_RAG/backend
source ../.venv/bin/activate
nohup python scripts/master_run.py --skip-download \
  > scripts/master_run_stdout.log 2>&1 &
echo "PID: $!"
```

---

## 8단계. 실험 진행 확인

```bash
tail -f /home/elicer/M_RAG/backend/scripts/master_run.log
```

`Ctrl+C` 로 로그 보기를 빠져나와도 실험은 계속 실행됩니다.

진행 단계별 예상 시간:

| 단계 | 내용 | 예상 시간 |
|---|---|---|
| STEP 3 | API 서버 기동 + 모델 로드 | 5–15분 |
| STEP 4 | 논문 7편 인덱싱 | 10–20분 |
| STEP 5 | GT 생성 (GPT-4o) | 20–40분 |
| STEP 6–10 | 평가 전체 실행 | 4–8시간 |
| **합계** | | **5–10시간** |

완료 확인:
```bash
grep "MASTER RUN COMPLETE\|failed" /home/elicer/M_RAG/backend/scripts/master_run.log
```

---

## 9단계. 결과 수신

실험이 완료되면 결과가 자동으로 push됩니다. 로컬 PC에서:

```bash
cd C:\Users\KiKi\Desktop\CODE\M_RAG
git pull origin main
type backend\evaluation\results\TABLES.md
```

Alice Cloud에서 직접 확인하려면:
```bash
cat /home/elicer/M_RAG/backend/evaluation/results/TABLES.md
```

---

## 중단 후 재개

중단됐다면 그냥 7단계 명령을 다시 실행하면 됩니다.  
완료된 config/paper는 자동으로 건너뜁니다.

```bash
cd /home/elicer/M_RAG/backend
source ../.venv/bin/activate
nohup python scripts/master_run.py --skip-download \
  > scripts/master_run_stdout.log 2>&1 &
```

---

## 트러블슈팅

### `.env.example` 복사 실패

```bash
ls backend/.env.example
# 없으면:
git pull origin main
cp backend/.env.example backend/.env
```

### `git remote set-url` 오류 (No such file or directory)

URL 전체를 반드시 **작은따옴표**로 감싸야 합니다:
```bash
git remote set-url origin 'https://lxnx-hn:<토큰>@github.com/lxnx-hn/M_RAG.git'
```

### CUDA out of memory

```bash
nvidia-smi
# VRAM 확인 후 인스턴스 업그레이드
```

### STEP 5 abort (GT 0개)

`backend/.env` 에서 OPENAI_API_KEY 확인. 키 없이 실행하려면:
```bash
# .env에서 OPENAI_API_KEY 줄 비워두거나 삭제 후 재실행
python scripts/master_run.py --skip-download
```

### 락 파일 잔존

```bash
rm /home/elicer/M_RAG/backend/scripts/master_run.lock
```

### 결과 파일 수동 push (STEP 13 실패 시)

```bash
cd /home/elicer/M_RAG
git add backend/evaluation/results/
git commit -m "feat: add experiment results"
git push origin main
```

---

## 파일 경로 참조

| 파일 | 설명 |
|---|---|
| `backend/scripts/master_run.py` | 실험 오케스트레이터 |
| `backend/scripts/master_run.log` | 실험 전체 로그 |
| `backend/.env` | 환경변수 (gitignore) |
| `backend/data/` | PDF 원본 (gitignore) |
| `backend/evaluation/data/track1_queries.json` | Track 1 쿼리 60개 |
| `backend/evaluation/data/track2_queries.json` | Track 2 쿼리 28개 |
| `backend/evaluation/results/` | 결과 JSON + TABLES.md |
| `backend/.cache/huggingface/` | 모델 캐시 (gitignore) |
