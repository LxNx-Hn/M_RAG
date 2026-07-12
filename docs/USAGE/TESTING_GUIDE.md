# M-RAG 테스트 가이드

## 목적

로컬 검증과 CI 검증 절차를 정리한다.

## Backend 정적 검사

```bash
cd backend
python -m ruff check .
python -m black --check .
```

## Backend 테스트

```bash
python -m pytest tests/backend -q
```

`tests/backend/test_api.py`는 API 통합 스모크 성격이 강하다. 보호 라우트는 bearer token이 필요하므로 스크립트 내부 토큰 생성 경로를 확인하고 실행한다.

```bash
python -X utf8 tests/backend/test_api.py
```

## Frontend 검사

```bash
cd frontend
npm run lint
npm run build
```

## Track 2 자산/결과 검증

Track 2는 런타임에 GPT로 다시 생성하지 않고 checked-in 정적 템플릿 자산
`experiments/data/query_splits/query_templates.json`을 사용한다. 구조적 사실과
실측 결과를 구분하려면 아래 순서로 확인한다.

```bash
python -c "import json; d=json.load(open('experiments/data/query_splits/query_templates.json', encoding='utf-8')); print('total=', len(d['queries']))"
```

- 위 확인으로 정적 쿼리 자산이 유지되는지 검증한다.
- 실측(요인효과) 문장은 공식 scored 결과에서 확정한다. config별 평균과
  축별(HyDE/CAD/SCD) 요인효과는 아래로 확인한다.

```bash
python experiments/analyzers/aggregate_main_scores.py \
  --scores experiments/results/evaluation/main-hyde-cad-scd__decoder_main_queries__main_generation.ragas_scores.json \
  --generation experiments/results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl
```

- SCD의 한국어 준수(언어 드리프트) 문장은 직접 측정으로 확정한다.

```bash
python experiments/analyzers/scd_language_adherence.py \
  --generation experiments/results/main_generation/main-hyde-cad-scd__decoder_main_queries__main_generation.jsonl
```

“CAD가 faithfulness를 높인다”, “원래 `penalty_additive` v1 SCD는 null” 같은
Phase 8 문장은 위 결과 파일과 `experiments/reports/phase8_*`가 실제로 존재할 때만
사용한다. 보정된 `reference_scd`의 직접 언어 결과와 RAGAS 민감도 패널은 별도로
라벨링한다.

대칭 이중언어 후속 결과는 네트워크 호출 없이 다음 명령으로 재계산한다.

```bash
python experiments/analyzers/analyze_scd_symmetric_eval.py \
  --english-scores experiments/results/evaluation/reference-scd-symmetric-hyde-off-en-gpt4o/merged.ragas_scores.json \
  --korean-scores experiments/results/evaluation/reference-scd-symmetric-hyde-off-ko-gpt4o/merged.ragas_scores.json \
  --out-json experiments/results/analysis/reference_scd_symmetric_gpt4o.json \
  --out-md experiments/reports/reference_scd_symmetric_eval_report.md \
  --bootstrap-iterations 10000 --seed 20260712

python experiments/analyzers/analyze_scd_symmetric_eval.py \
  --english-scores experiments/results/evaluation/reference-scd-symmetric-hyde-off-en-gpt41-2025-04-14/merged.ragas_scores.json \
  --korean-scores experiments/results/evaluation/reference-scd-symmetric-hyde-off-ko-gpt41-2025-04-14/merged.ragas_scores.json \
  --out-json experiments/results/analysis/reference_scd_symmetric_gpt41_2025_04_14.json \
  --out-md experiments/reports/reference_scd_symmetric_eval_report_gpt41_2025_04_14.md \
  --bootstrap-iterations 10000 --seed 20260712
```

이 결과는 동일 context와 대칭 정규화를 사용한 생성 후 민감도 분석이다. 인과 또는
배포 판정으로 이름을 바꾸지 않는다. 두 judge의 interval class가 다르므로 한쪽만
선택해 주장하지 않는다.

## Docker build 확인

```bash
cd backend
docker build -t mrag-backend-ci .
```

```bash
cd frontend
docker build -t mrag-frontend-ci .
```

## 수동 API 체크

- `/health` 200 확인
- 토큰 없이 보호 라우트 401 확인
- 로그인 후 `/api/auth/me` 확인
- 문서 업로드 확인
- `/api/chat/search` 검색 결과 확인
- `/api/chat/query` 답변과 follow_ups 확인
- `/api/chat/query/stream` done 이벤트 확인
- `/api/chat/judge` label 판정 확인
- `/api/chat/export/ppt` PPTX 반환 확인
