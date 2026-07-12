# M-RAG 구조 쉽게 이해하기

## 한 줄 설명

M-RAG는 한국어 질문으로 영어 논문을 탐색하는 논문 리뷰 서비스다. 연구의 핵심은 서비스 라우터 자체가 아니라, 고정된 Paper-RAG backbone 위에서 HyDE, CAD, SCD가 답변 품질에 미치는 영향을 분해하는 것이다.

## 두 개의 층

| 층 | 역할 |
|---|---|
| 연구 실험층 | HyDE/CAD/SCD 8-config factor analysis |
| 서비스층 | FastAPI + React 기반 A-F 논문 리뷰 기능 |

서비스층은 졸업작품 구현이다. 연구 실험층의 결과를 바탕으로 query-type-aware policy를 만들 수 있다.

## 연구 실험층

고정하는 것:

- dense retrieval
- BM25 sparse retrieval
- RRF rank fusion
- reranker
- generation settings
- `top_k`, `rerank_top_n`, `cad_alpha`, `scd_beta`

바꾸는 것:

- HyDE on/off
- CAD on/off
- SCD on/off

그래서 전체 config는 8개다.

## 세 가지 factor

### HyDE

질문을 바로 검색하지 않고, 질문에 대한 가상의 답변 형태를 만들어 검색한다. 한국어 질문과 영어 논문 문장 사이의 표현 차이를 줄이는 역할이다.

### CAD

문서가 있는 상태의 logits와 문서가 없는 상태의 logits를 비교해, 문서 근거가 있을 때 강해지는 토큰을 더 선호하게 한다.

```text
cad_scores = (1 + alpha) * context_scores - alpha * no_context_scores
```

### SCD

한국어 답변을 유지하기 위한 Soft Constrained Decoding이다. 영어 문장으로 drift되는 것을 줄이되, 모델명, 데이터셋명, 수식, 약어 같은 기술 용어는 whitelist로 보존해야 한다.

## 서비스층

| Route | 기능 |
|---|---|
| A | 단순 QA |
| B | 섹션 중심 QA |
| C | 문서 비교 |
| D | 인용 / 특허 관련 조회 |
| E | 구조화 요약 |
| F | 퀴즈 / 플래시카드 |

이 route들은 사용자 경험을 위한 기능이다. 논문의 Table 5는 실험의 전역 효과를 바탕으로 route별 임시 factor 정책을 정리하지만, route별 정량 최적화 결과는 아니다.

## API 호환성

현재 서비스는 다음 API 호환성을 유지한다.

- `QueryRequest`
- `QueryResponse`
- SSE `metadata`, `token`, `done`, `error`
- paper APIs
- citation APIs
- `activePaperId -> doc_id_filter`
- compare route target selection metadata

## 평가층

평가는 두 갈래로 분리한다.

- 공식 RAGAS runner: 원래 Phase 8은 NVIDIA NIM judge, 완료된 `reference_scd` 예외는 `gpt-4o`와 고정 `gpt-4.1` 교차 judge
- RAGAS-inspired lightweight evaluator: 서비스/로컬 경량 judge로, 공식 RAGAS 결과와 분리

실제 결과는 `docs/PAPER/THESIS.md`와 `experiments/reports/`의 최신 보고서만 인용한다.
`reference_scd` 언어 결과는 직접 측정이다. 대칭 패널에서도 `gpt-4o`의 0이 아닌
answer-relevancy 구간이 고정 `gpt-4.1`에서 재현되지 않았으므로, SCD의 인과적 RAG
품질 효과로 쓰지 않는다.

## 결과 작성 규칙

- 미실행 항목은 pending으로, 완료 항목은 검증된 artifact 범위 안에서만 쓴다.
- query를 새로 꾸며내지 않는다.
- service-route qualitative example을 main experiment result로 쓰지 않는다.
- route system을 새로운 algorithm처럼 쓰지 않는다.
