# 60-query 최종 주장 맵

| 주장 범주 | 원고에 사용할 결과 | 근거 | 표본·분석 단위 |
|---|---|---|---|
| 실험 범위 | 네 영어 학술·기술 문서에 한국어 질의 15개씩 총 60개를 구성하고 8개 실험 조건을 적용해 480개 생성 기록을 분석한다. 60개 질의 전체는 한국어 질의–영어 문서 검색의 cross-lingual 조건을 공유한다. | `EXPERIMENT_60_VALIDATION.md`, `TABLES_60Q.xlsx` | 문서별 15개, 조건별 60 record |
| HyDE | CAD·SCD OFF 비교에서 answer relevancy +0.0805, 95% CI [+0.0110, +0.1514] | `extended_validation_60_analysis.json` | 60 paired queries |
| HyDE 보조 지표 | faithfulness +0.0436, context precision -0.0343, context recall 0.0000 | `extended_validation_60_analysis.json` | 60 paired queries |
| CAD | 동일 검색 문맥에서 faithfulness +0.0288, answer relevancy -0.0073 | `extended_validation_60_analysis.json` | faithfulness 58 complete pairs, 나머지 60 |
| SCD 동일 문맥 | HyDE OFF 동일 문맥에서 Korean-character ratio +0.2182, 95% CI [+0.1880, +0.2487] | `extended_validation_60_analysis.json` | 120 pairs |
| SCD 전체 | 같은 query와 HyDE·CAD configuration을 짝지은 240쌍에서 Korean-character ratio +0.2289, 95% CI [+0.2051, +0.2532] | `extended_validation_60_analysis.json` | 240 pairs, query-clustered bootstrap |
| Configuration 평균 | 표 5-2에 8개 configuration 평균을 제시한다. SCD ON RAGAS는 5.2절의 한국어 context preprocessing을 적용한 저장 평가값이다. | RAGAS score 결과 | configuration별 generation 60 |
| 질문 유형 탐색 | 질문 유형은 simple_qa 16, section_method 22, section_result 20, section_abstract 2로 통일하고 B-2를 재계산한다. | `Appendix_QueryType`, RAGAS per-sample scores | 탐색적 하위집단 분석 |
| HyDE×CAD 조합 패턴 | 다른 요인 상태별 paired effect를 비교해 HyDE와 CAD의 효과 크기 변화를 조건군별로 제시한다. | 그림 5-6 / 저장 paired effect | strata별 paired-effect 비교 |

## 분석 연결

- HyDE: 검색 경로와 answer relevancy 대응 변화.
- CAD: identical retrieved/reranked/context 조건의 generation-side 변화와 duration.
- SCD: Korean-character ratio와 stored answer의 출력 언어 변화.
- E01~E06: `evidence_manifest_60q.json`, `EVIDENCE/IO_CASES/raw/*.txt`, PNG가 같은 query/config를 가리킨다.
- Source SHA-256은 내부 검증용 `evidence_manifest_60q.json`과 `EXPERIMENT_60_VALIDATION.md`에서 관리한다.
