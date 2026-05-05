# 실험표 해석 가이드

이 문서는 Phase 5 이후의 표 구조를 설명한다. 결과 수치는 승인된 실험이 끝난 뒤 검증된 산출물에서만 채운다.

## Table 1. Experimental Setup

확인할 것:

- fixed Paper-RAG backbone이 고정되어 있는가
- tuning query와 main query가 분리되어 있는가
- HyDE/CAD/SCD 외의 변수가 main matrix에서 바뀌지 않는가
- 모델, 생성 설정, `top_k`, `rerank_top_n`, `cad_alpha`, `scd_beta`가 freeze rule을 따르는가

## Table 2. Main HyDE × CAD × SCD Factorial Ablation

8개 config를 같은 query split에서 비교한다.

볼 지표:

- evidence support
- numeric hallucination
- language drift
- Korean answer ratio

해석 원칙:

- HyDE 효과는 HyDE on 평균과 HyDE off 평균의 차이로 본다.
- CAD 효과는 CAD on 평균과 CAD off 평균의 차이로 본다.
- SCD 효과는 SCD on 평균과 SCD off 평균의 차이로 본다.
- CAD+SCD 조합은 단순 합보다 나은지 또는 충돌하는지 별도 확인한다.

## Table 3. Effect Delta Summary

Table 2의 결과를 effect 단위로 요약한다.

주의할 점:

- delta가 작으면 방법이 실패했다고 바로 결론내리지 말고 query type별 분해를 본다.
- 모든 점수가 평평하면 evaluator, query answerability, retrieval variance를 먼저 점검한다.
- 결과를 route policy로 연결할 때는 평균만 보지 말고 query type별 패턴을 본다.

## Table 4. Query-Type Breakdown

질문 유형별로 어떤 factor가 유리한지 본다.

예상 분석 질문:

- numeric 질문에서 CAD가 unsupported number를 줄였는가
- method 질문에서 HyDE가 evidence retrieval을 개선했는가
- Korean answer 유지에는 SCD가 충분했는가
- summary나 comparison 질문에서 decoder control이 답변 품질을 과도하게 제한하지 않았는가

## Table 5. Numeric Hallucination and Evidence Support

수치 질문은 별도로 본다.

점검 순서:

1. 답변 수치가 evidence에 실제로 있는가
2. 단위, 소수점, 비교 대상이 유지되었는가
3. CAD 적용 시 unsupported numeric claims가 줄었는가
4. HyDE가 정확한 수치 evidence를 더 잘 찾았는가

## Table 6. Language Drift and Korean Answer Ratio

SCD는 한국어 답변 유지가 목표지만 기술 용어를 억지로 번역하면 안 된다.

점검 순서:

1. 한국어 문장 비율이 높아졌는가
2. 영어 문장이 불필요하게 섞인 비율이 줄었는가
3. 모델명, 데이터셋명, 수식, 약어가 whitelist로 보존되었는가
4. SCD beta가 너무 강해서 답변 자연성이 떨어지지 않았는가

## Table 7. Routed Policy for Graduation-Project System

이 표는 실험 결과를 서비스 정책으로 연결한다.

주의:

- A-F route는 thesis method가 아니라 service feature다.
- policy는 Table 2-6의 분석에서 파생되어야 한다.
- service-route qualitative examples를 quantitative result처럼 쓰지 않는다.

## Appendix Tables

- A1: CAD alpha / SCD beta sensitivity
- A2: reference implementation audit
- A3: query audit and split statistics
- A4: cost / run-size estimation
- A5: service route qualitative examples
- A6: frontend-backend runtime compatibility audit

## 숫자가 이상할 때 점검 순서

1. query split leakage가 없는지 확인
2. 검색 결과가 실제로 다른지 확인
3. evaluator가 라벨을 제대로 반환하는지 확인
4. GT 또는 reference answer가 비어 있지 않은지 확인
5. 이전 result JSON을 재사용하지 않았는지 확인
6. dry-run에서 config 순서와 query counts가 맞는지 확인
