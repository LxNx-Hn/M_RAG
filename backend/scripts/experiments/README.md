# 실험 보조 스크립트

- `master_run.py` 와 별도로 보존하는 실험 전용 스크립트 묶음
- RunPod, 단일 논문 실험, 비교 실험처럼 메인 로컬 실행 경로 밖의 작업에 사용
- 현재 기준 표준 로컬 실험 러너는 여전히 `backend/scripts/master_run.py`

## 포함 스크립트

- `run_all_experiments.py` 단일 논문 기준 레거시 일괄 실험
- `run_c3_experiment.py` C3 CAD 관련 별도 비교 실험
- `runpod_experiment.sh` RunPod 원격 실행 보조 스크립트

## 운영 메모

- 이 폴더의 스크립트는 보존 대상
- 향후 RunPod 환경 실험, 원격 GPU 실험, 서빙 전환 실험에 재사용 가능
- `vLLM` 연동은 아직 구현되어 있지 않음
- 현재 생성 경로는 `modules/generator.py` 가 직접 모델을 로드하는 구조
