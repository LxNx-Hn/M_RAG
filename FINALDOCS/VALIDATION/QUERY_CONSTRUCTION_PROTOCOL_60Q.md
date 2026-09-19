# 60-Query Construction Protocol

## 1. 평가 집합

최종 평가 집합은 다음 네 영어 학술·기술 문서를 대상으로 문서별 15개씩 총 60개의 한국어 질의로 구성한다.

- RAG Survey
- CAD
- RAPTOR
- Mi:dm K 2.5 Pro Technical Report

모든 질의는 한국어 질문으로 영어 원문에서 근거를 검색하는 동일한 교차언어 조건을 사용한다.

## 2. 문서별 질의 구성

각 문서에는 동일한 질의 구성 절차를 적용한다.

1. 연구자가 문서의 주요 내용을 바탕으로 질문 표현과 범위를 정의하는 초기 질문 3개를 작성한다.
2. 초기 질문의 표현 방식과 범위를 기준으로 LLM이 대상 문서의 주요 내용을 질문 작성에 활용할 수 있는 형태로 요약한다.
3. 요약 결과를 15개의 내용 단위로 구분한다.
4. 각 내용 단위에서 한국어 평가 질의 1개를 구성한다.
5. 문서별 15개 질의를 확정하여 네 문서에서 총 60개 질의를 구성한다.

LLM은 문서 내용의 요약과 질의 구성 단계에 사용하며, 최종 평가 질의의 근거 확인은 원문 PDF를 기준으로 수행한다.

## 3. Human verification

각 질의에 대해 다음 항목을 원문 PDF와 대조한다.

- target document
- source page
- literal reference evidence
- answerability
- question type

정답 근거는 원문에서 확인되는 연속 구간으로 기록하고 질문과 근거의 대응 관계를 확인한다.

## 4. 최종 수용 기준

최종 평가 집합은 다음 조건을 충족하는 60개 질의로 구성한다.

- 4 documents × 15 queries = 60 queries
- 모든 질의에 target document가 연결됨
- 모든 질의에 source page가 연결됨
- 모든 질의에 원문 reference evidence가 연결됨
- 모든 질의가 원문 근거를 기준으로 답변 가능함

질문 유형은 사실·정의 8개, 방법·절차 29개, 결과·비교 20개, 목적·기여 3개로 분류한다.

## 5. Traceability

최종 분석에서 각 질의는 다음 경로로 추적한다.

`query_id → question → target_document → source_page → reference_evidence → 8 generation records → evaluation scores → paired analysis`

질의 목록과 source page·reference evidence는 `FINALDOCS/APPENDIX/QUERY_60_AUDIT.md` 및 원고 부록 A에서 확인한다.
