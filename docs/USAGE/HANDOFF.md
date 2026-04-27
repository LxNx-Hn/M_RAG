# M-RAG 인수인계

- 문서 기준 2026-04-27
- 목적 다음 세션에서 바로 실험을 이어받을 수 있게 현재 상태와 첫 명령을 고정

## 현재 상태

- 로컬 연구 실행 주 경로는 `backend/scripts/master_run.py`
- 생성 모델 기본값은 Base
- Mini 모델 경로는 로컬 스모크 검증용으로 유지
- `master_run.py` 에 stale `uvicorn` 정리 로직 반영
- README 에 파일 단위 코드 맵 반영
- 문서 구조는 `README` 중심으로 정리 완료
- 이번 구현 범위에서는 plain generation 전환 외부 상용 LLM API 연동 `vLLM` 전환을 진행하지 않음
- 이유는 현재 논문 검증 경로가 CAD와 SCD 기반 생성 제어를 유지해야 하기 때문

## 다음 세션 첫 명령

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
.venv\Scripts\Activate.ps1
cd backend
python scripts\master_run.py --skip-download
```

## 다음 세션 시작 체크

- `Get-Process python -ErrorAction SilentlyContinue`
- `Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue`
- `nvidia-smi --query-gpu=memory.used,memory.free --format=csv,noheader,nounits`
- `backend/data/` 와 `backend/evaluation/data/` 입력 파일 존재 확인

## 확인할 로그

```powershell
Get-Content C:\Users\KiKi\Desktop\CODE\M_RAG\backend\scripts\master_run.log -Wait -Tail 40
```

## 성공 기준

- `STEP 12 - Validate results completed successfully.`
- `STEP 13 - Stop the API server subprocess cleanly completed successfully.`
- `MASTER RUN COMPLETE`
- `backend/evaluation/results/TABLES.md` 재생성
- 결과 값이 전부 동일 점수나 0 점수로 수렴하지 않음

## 연결 문서

- 메인 문서 `C:\Users\KiKi\Desktop\CODE\M_RAG\README.md`
- 실행 계획 `C:\Users\KiKi\Desktop\CODE\M_RAG\docs\USAGE\WORK_PLAN.md`
- 배포 가이드 `C:\Users\KiKi\Desktop\CODE\M_RAG\docs\USAGE\DEPLOY.md`
- 아키텍처 `C:\Users\KiKi\Desktop\CODE\M_RAG\docs\ARCHITECTURE.md`
- 결과 폴더 `C:\Users\KiKi\Desktop\CODE\M_RAG\backend\evaluation\results`
- 실행 로그 `C:\Users\KiKi\Desktop\CODE\M_RAG\backend\scripts\master_run.log`

## 사용자 규칙 메모

- 삭제 전에는 사용자 확인 필요
- Base 모델 기본 경로 유지
- 최신 문서 기준으로만 갱신
