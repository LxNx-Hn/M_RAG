# 실험표 해석 가이드

이 문서는 현재 완료된 실험표를 비전공자도 과장 없이 읽을 수 있도록 설명한다. 모든 수치는 `docs/PAPER/THESIS.md`와 공식 분석 산출물 기준이다. 측정하지 않은 값은 0이 아니며, 결과 주장에 포함하지 않는다.

## 먼저 구분해야 하는 두 실험

1. **원본 주실험:** `penalty_additive` v1 SCD를 포함한 19개 질의 × 8개 설정이다. NVIDIA NIM judge로 608개 지표 셀 중 583개가 채점됐다.
2. **수정 SCD 실험:** 논문에 충실한 `reference_scd` 구현을 별도 실험 ID로 실행했다. 직접 한국어 준수율과 대칭 전처리·교차 judge 결과를 보고한다.

두 실험은 SCD 구현과 judge가 다르므로 절대점수를 합치거나 한 표의 같은 모집단처럼 평균내면 안 된다.

## Table 1. Experimental Setup

이 표는 비교가 공정한지 확인하는 계약서다. Paper-RAG backbone, 생성 모델, 검색 후보 수, rerank 수, context 수, 생성 길이는 고정되고 HyDE/CAD/SCD만 바뀌어야 한다. `decoder_main_queries` 19개가 모든 8개 설정에 동일하게 사용됐는지도 확인한다.

## Table 2. Main HyDE × CAD × SCD Factorial Ablation

원본 주실험의 실제 평균 점수다.

- Faithfulness: 답변 주장이 검색 문맥에 의해 지지되는 정도
- Answer relevancy: 답변이 질문에 직접 대응하는 정도
- Context precision: 검색 문맥 중 유용한 부분의 비율
- Context recall: 필요한 근거가 검색 문맥에 포함된 정도
- Korean answer ratio: 중립 문자와 기술 용어를 고려한 직접 한국어 비율

이 표만 보고 가장 큰 셀을 “최고 모델”로 선언하지 않는다. 각 요소의 효과는 다른 두 요소가 같은 쌍을 비교한 Table 3에서 판단한다.

## Table 3. Effect Delta Summary

같은 조건에서 특정 요소만 켠 값에서 끈 값을 뺀 paired ON−OFF 차이다.

- CAD faithfulness `+0.044`: 원본 실험에서 가장 명확한 단일 축 개선이다.
- HyDE answer relevancy `+0.070`, context recall `+0.026`: 더 넓게 근거를 가져오는 경향이다.
- HyDE context precision `−0.056`: 더 넓게 찾는 대신 불필요한 문맥도 늘어나는 trade-off다.
- SCD v1 faithfulness `+0.009`, 한국어 비율 `−0.014`: 원본 `penalty_additive` 구현은 사실상 null 결과다.

이 SCD v1 결과를 수정된 `reference_scd` 결과로 소급해 덮어쓰지 않는다.

## 결과 주장에서 제외한 분석

질의 유형별 분석과 숫자 환각·별도 evidence-support 표는 이번 실행에서 계산하지 않았다.

- 질의가 19개뿐이라 유형별 셀은 신뢰할 만큼 크지 않다.
- 숫자 환각률은 값·단위·대상 엔터티를 근거와 대조한 claim-level 주석이 필요하지만 이번 실행에는 없다.

따라서 이 항목들은 빈 결과도, 0점도, 실패 점수도 아니다. 향후 더 큰 질의 집합과 별도 주석으로 평가해야 한다.

## Table 4. Language Drift and Korean Answer Ratio

이 표는 역사적 v1 실험의 언어 이탈을 보여준다. v1 SCD는 drift를 줄이지 못했다. 수정된 `reference_scd`는 별도 직접 측정에서 평균 paired delta `+0.2203`, 76쌍 중 68쌍 개선, 3쌍 악화, 5쌍 동률이었다. 그러나 12/76개의 SCD-on 답변은 여전히 한국어 비율 0.5 미만이므로 언어 이탈을 완전히 제거했다고 말할 수 없다.

## Table 5. Routed Policy for Graduation-Project System

이 표는 직접 측정표가 아니라 결과에서 제한적으로 도출한 서비스 기본값이다.

- CAD: 원본 실험의 faithfulness 개선을 근거로 기본 활성화 후보
- HyDE: recall이 중요한 비교·요약에서는 활성화 후보, precision이 중요한 섹션·인용 검색에서는 비활성화 후보
- `reference_scd`: 언어 제어가 필요한 작업에서 조건부 사용하되, 작업별 품질 검증 필요

A-F route 자체를 새로운 논문 알고리즘이나 유형별로 검증된 최적 정책이라고 주장하지 않는다.

## 수정 SCD 교차 judge 결과 읽기

대칭 후속 평가는 HyDE-off의 byte-identical context 38쌍을 영어·한국어로 정규화하고 10,000회 query-clustered bootstrap을 사용했다.

- Faithfulness: `gpt-4o`, 고정 `gpt-4.1-2025-04-14` 모두 방향을 확정하지 못했다.
- Answer relevancy: `gpt-4o`에서는 음의 신뢰구간이었지만, `gpt-4.1`에서는 0을 포함했다.
- 결론: 한국어 준수율 개선은 직접 지표로 확인됐지만, RAG 품질의 안정적인 개선 또는 저하는 확립되지 않았다.

## 숫자가 이상할 때 점검 순서

1. 원본 v1과 `reference_scd` 산출물을 섞지 않았는지 확인한다.
2. query split leakage와 19×8=152 레코드 완전성을 확인한다.
3. paired comparison에서 나머지 factor가 같은지 확인한다.
4. null 셀을 0으로 바꾸지 않았는지 확인한다.
5. judge 모델 ID와 전처리 언어가 같은 비교인지 확인한다.
6. 평균뿐 아니라 질의 단위 차이와 신뢰구간을 확인한다.

## 근거 문서

- `docs/PAPER/THESIS_KO.md`: 국문 전체 논문
- `docs/PAPER/THESIS.md`: 영문 전체 논문
- `experiments/reports/reference_scd_rerun_explainer_KO.md`: 수정 SCD 쉬운 설명
- `experiments/reports/reference_scd_symmetric_cross_judge_report.md`: 대칭 교차 judge 공식 보고서
- `docs/PAPER/REFERENCE_AUDIT_2026-07-11.md`: 참고문헌 정확성 감사
