# M-RAG 인수인계

- 문서 기준 2026-04-25
- 다음 세션이 바로 이어받을 수 있도록 현재 기준만 남긴 인수인계 문서

## 현재 상태

- 로컬 연구 실행 표준 경로는 `backend/scripts/master_run.py`
- 생성 모델 기본값은 Mini
- Base 모델 경로는 유지
- 양자화 경로는 사용하지 않음
- `master_run.py` 에 안전한 stale uvicorn 정리 로직 반영
- README 에 파일 단위 코드 맵 반영
- 삭제는 아직 진행하지 않음

## 다음 세션 첫 명령

```powershell
cd C:\Users\KiKi\Desktop\CODE\M_RAG
.venv\Scripts\Activate.ps1
cd backend
python scripts\master_run.py --skip-download
```

## 확인할 로그

```powershell
Get-Content C:\Users\KiKi\Desktop\CODE\M_RAG\backend\scripts\master_run.log -Wait -Tail 40
```

## 성공 기준

- `STEP 12 - Validate results completed successfully.`
- `STEP 13 - Stop the API server subprocess cleanly completed successfully.`
- `MASTER RUN COMPLETE`

## 핵심 경로

- 메인 문서 `C:\Users\KiKi\Desktop\CODE\M_RAG\README.md`
- 실행 계획 `C:\Users\KiKi\Desktop\CODE\M_RAG\WORK_PLAN.md`
- 배포 가이드 `C:\Users\KiKi\Desktop\CODE\M_RAG\docs\DEPLOY.md`
- 아키텍처 `C:\Users\KiKi\Desktop\CODE\M_RAG\docs\ARCHITECTURE.md`
- 결과 폴더 `C:\Users\KiKi\Desktop\CODE\M_RAG\backend\evaluation\results`
- 실행 로그 `C:\Users\KiKi\Desktop\CODE\M_RAG\backend\scripts\master_run.log`

## 사용자 규칙

- 불필요 문서와 코드 삭제는 사용자 확인 전 금지
- Base 모델은 유지
- 양자화는 다시 넣지 않음
- 최신 문서는 항상 현재 상태 기준으로만 갱신

## 남아 있는 판단 포인트

- 실험 결과 산출물 정리 여부
- codex 작업 메모와 보고서 정리 여부
- 삭제 후보 문서와 데이터 정리 여부
