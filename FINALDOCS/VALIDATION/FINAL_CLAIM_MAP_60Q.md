# 60-query 최종 주장 맵

| 주장 범주 | 최종 원고에 사용할 문장 범위 | 근거 | 표본·해석 기준 |
|---|---|---|---|
| 실험 범위 | 4개 대상 문서의 60개 질의-문서 쌍에 8개 조건을 적용해 480개 답변을 생성했다. | `EXPERIMENT_60_VALIDATION.md` | 각 조건 60 record |
| RAG-Cube | HyDE, CAD, SCD를 독립 이진 요인으로 둔 2×2×2 조합 실험을 RAG-Cube로 지칭한다. | 실험 설계와 8개 config record | 세 요인의 적용 위치와 통제 비교를 중심으로 설명 |
| HyDE | CAD·SCD OFF 통제 비교에서 answer relevancy는 +0.0805, 95% CI [+0.0110, +0.1514]였다. | `FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md` 및 `experiments/results/analysis/extended_validation_60_analysis.json` | 60 대응 질의 |
| HyDE 보조 지표 | Faithfulness는 평균 +0.0436, CI [-0.0262, +0.1153]이며, context precision은 -0.0343, context recall은 0.0000이었다. | `FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md` 및 `experiments/results/analysis/extended_validation_60_analysis.json` | answer-level과 context-level 지표를 각각 제시 |
| CAD | 동일 문맥 비교에서 faithfulness는 58 완결 쌍에서 +0.0288, answer relevancy는 60쌍에서 -0.0073이었다. | `FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md` 및 `experiments/results/analysis/extended_validation_60_analysis.json` | faithfulness CI [-0.0367, +0.0934], answer relevancy CI [-0.0855, +0.0719] |
| SCD | 240 ON/OFF 대응쌍에서 한국어 문자 비율은 +0.2289, 95% CI [+0.2051, +0.2532]였다. | `FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md` 및 `experiments/results/analysis/extended_validation_60_analysis.json` | 219 증가, 10 감소, 11 동률 |
| SCD 동일 문맥 | HyDE OFF 동일 문맥 120쌍에서도 한국어 문자 비율 변화는 +0.2182, 95% CI [+0.1880, +0.2487]였다. | `FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md` 및 `experiments/results/analysis/extended_validation_60_analysis.json` | 출력 언어 제어의 직접 비교 |
| 조합별 결과 | 최고 configuration은 지표별로 달랐다. Faithfulness H1C1S0, answer relevancy H1C0S0, context precision H0C0S1, context recall H0C0S0/H1C0S0 동률, Korean ratio H1C0S1이다. | `FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md` 및 `experiments/results/analysis/extended_validation_60_analysis.json` | 지표별 최고 configuration을 각각 제시 |

## 해석 기준

- HyDE는 CAD·SCD OFF paired contrast와 retrieval provenance를 함께 제시한다.
- CAD는 same-context paired result, 유효 표본 수, generation duration을 함께 제시한다.
- SCD는 Korean-character ratio를 output-language control 지표로 제시한다.
- configuration 평균과 paired contrast는 각각 조합 수준과 요인 수준의 결과로 구분한다.
- 60-query 최종 결과는 해시로 고정한 generation·evaluation·analysis artifact를 기준으로 제시한다.

## 사용 전 대조 규칙

본문, 표, 그림의 수치는 `FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md`와 그 문서가 해시로 고정한 `experiments/results/analysis/extended_validation_60_analysis.json`을 함께 대조한다. Faithfulness가 포함된 비교에는 해당 표본 수를 표기한다. 실제 응답 예시는 `FINALDOCS/DATA/evidence_manifest_60q.json`에 기록된 저장 excerpt와 provenance를 사용한다.
