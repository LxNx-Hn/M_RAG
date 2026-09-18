# 60-query 최종 주장 맵

| 주장 범주 | 원고에 사용할 결과 | 근거 | 표본·분석 단위 |
|---|---|---|---|
| 실험 범위 | 기존 19개 retained query와 41개 held-out extension을 합친 60개 질의에 8개 조건을 적용해 480개 답변을 생성했다. | `experiments/configs/extended_validation_method.json`, `EXPERIMENT_60_VALIDATION.md` | 문서별 15개, 조건별 60 record |
| HyDE | CAD·SCD OFF 비교에서 answer relevancy +0.0805, 95% CI [+0.0110, +0.1514] | `extended_validation_60_analysis.json` | 60 paired queries |
| HyDE 보조 지표 | faithfulness +0.0436, context precision -0.0343, context recall 0.0000 | `extended_validation_60_analysis.json` | 60 paired queries |
| CAD | 동일 검색 문맥에서 faithfulness +0.0288, answer relevancy -0.0073 | `extended_validation_60_analysis.json` | faithfulness 58 complete pairs, 나머지 60 |
| SCD 동일 문맥 | HyDE OFF 동일 문맥에서 Korean-character ratio +0.2182, 95% CI [+0.1880, +0.2487] | `extended_validation_60_analysis.json` | 120 pairs |
| SCD 전체 | 같은 query와 HyDE·CAD configuration을 짝지은 240쌍에서 Korean-character ratio +0.2289, 95% CI [+0.2051, +0.2532] | `extended_validation_60_analysis.json` | 240 pairs, query-clustered bootstrap |
| Configuration 평균 | 표 5-2에 8개 configuration 평균을 제시한다. SCD ON RAGAS는 5.2절의 한국어 context preprocessing을 적용한 저장 평가값이다. | RAGAS score artifacts | configuration별 generation 60 |

## 분석 연결

- HyDE: retrieval provenance와 answer relevancy 대응 변화.
- CAD: identical retrieved/reranked/context 조건의 generation-side 변화와 duration.
- SCD: Korean-character ratio와 stored answer의 출력 언어 변화.
- E01~E06: `evidence_manifest_60q.json`, `EVIDENCE/IO_CASES/raw/*.txt`, PNG가 같은 query/config를 가리킨다.
- Source SHA-256은 `evidence_manifest_60q.json`, 부록 C, `EXPERIMENT_60_VALIDATION.md`, HWP copy file에서 동일한 값을 사용한다.
