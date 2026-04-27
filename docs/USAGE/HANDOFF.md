# M-RAG 인수인계

- 문서 기준 2026-04-28
- 목적 다음 세션에서 바로 실험을 이어받을 수 있게 현재 상태와 첫 명령을 고정

## 현재 상태

- 실험 주 경로는 **Alice Cloud GPU** — `docs/USAGE/ALICE_CLOUD_GUIDE.md` 기준
- 생성 모델 기본값은 Base (`K-intelligence/Midm-2.0-Base-Instruct`)
- Mini 모델은 로컬 스모크 검증에서만 사용
- `master_run.py` 가 STEP 1–14 전체 오케스트레이션 담당
- `doc_id_filter` / `section_filter` 가 QueryRequest 및 파이프라인 A B E F 에 반영 완료
- Resume: `status: completed` 마커로 안전 재개 보장
- CAD adaptive=False 고정, fixed alpha [0.0, 0.1, 0.3, 0.5, 0.7, 1.0] 실험 경로
- plain generation 전환, 외부 LLM API, vLLM 전환은 현재 범위 외

## Alice Cloud 실험 시작 (주 경로)

전체 절차는 `docs/USAGE/ALICE_CLOUD_GUIDE.md` 참조.

```bash
# Alice Cloud 터미널
git clone https://github.com/lxnx-hn/M_RAG.git /home/elicer/M_RAG
cd /home/elicer/M_RAG
python -m venv .venv && source .venv/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
# → backend/.env 에 OPENAI_API_KEY 입력

cd backend
nohup python scripts/master_run.py --skip-download \
  > scripts/master_run_stdout.log 2>&1 &
tail -f scripts/master_run.log
```

## 로컬 스모크 점검 (보조 경로)

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
.venv\Scripts\Activate.ps1
cd backend
$env:GENERATION_MODEL = "K-intelligence/Midm-2.0-Mini-Instruct"
python scripts\master_run.py --skip-download
```

## 성공 기준

- `STEP 12 - Validate results completed successfully.`
- `STEP 13 - Stop the API server subprocess cleanly completed successfully.`
- `MASTER RUN COMPLETE`
- `backend/evaluation/results/` 아래 결과 JSON 5종 + `TABLES.md` 생성
- 결과 값이 전부 동일 점수나 0 점수로 수렴하지 않음

## 연결 문서

- Alice Cloud 가이드 `docs/USAGE/ALICE_CLOUD_GUIDE.md`
- 실행 가이드 인덱스 `docs/USAGE/README.md`
- 아키텍처 `docs/ARCHITECTURE.md`
- 논문 초안 `docs/PAPER/THESIS.md`
- 실행 로그 `backend/scripts/master_run.log`

## 사용자 규칙 메모

- 삭제 전에는 사용자 확인 필요
- Base 모델 기본 경로 유지
- 최신 문서 기준으로만 갱신
