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
cd backend
python -m pytest -q
```

`backend/tests/test_api.py`는 API 통합 스모크 성격이 강하다. 보호 라우트는 bearer token이 필요하므로 스크립트 내부 토큰 생성 경로를 확인하고 실행한다.

```bash
cd backend
python -X utf8 tests/test_api.py
```

## Frontend 검사

```bash
cd frontend
npm run lint
npm run build
```

## Track 2 자산/결과 검증

Track 2는 런타임에 GPT로 다시 생성하지 않고 checked-in 정적 자산
`backend/evaluation/data/track2_queries.json`을 사용한다. 구조적 사실과
실측 결과를 구분하려면 아래 순서로 확인한다.

```bash
cd backend
python -c "import json; d=json.load(open('evaluation/data/track2_queries.json', encoding='utf-8')); print('total=', len(d))"
```

- 위 확인으로 정적 자산(56개)이 유지되는지 검증한다.
- answerability 문장을 확정하려면 `pseudo_gt_track2.json`을 생성한 뒤 Not found 비율을 집계한다.

```bash
cd backend
python -c "import json; q=json.load(open('evaluation/data/pseudo_gt_track2.json', encoding='utf-8')).get('queries', []); n=sum(1 for x in q if x.get('ground_truth')=='Not found in document.'); print('not_found=', n, '/', len(q))"
```

- CAD gap 문장을 확정하려면 `table3_domain.json`을 생성한 뒤 config별 평균/차이를 확인한다.

```bash
cd backend
python -c "import json; d=json.load(open('evaluation/results/table3_domain.json', encoding='utf-8')); print(list(d.get('results', {}).keys()))"
```

정적 자산만으로는 “Not found 0%”, “CAD 격차가 더 선명하다” 같은 실측
문장을 확정할 수 없다. 그런 표현은 위 결과 파일이 실제로 생성된 뒤에만
사용한다.

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
