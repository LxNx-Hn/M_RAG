# 60개 질의 RAG-Cube 실험 검증

이 문서는 저장된 생성·평가 artifact를 읽어 자동 생성한다.

## 생성 검증

| 항목 | 결과 |
|---|---:|
| 질의-대상문서 쌍 | 60 |
| RAG-Cube 조건 | 8 |
| 생성 record | 480 |
| 조건별 record | 60 |
| 대상 문서 | 4 |
| HyDE primary 대응쌍 | 60 |
| CAD 동일 문맥 primary 대응쌍 | 60 |
| SCD ON/OFF 대응쌍 | 240 |

고정 생성 모델은 `K-intelligence/Midm-2.0-Base-Instruct`이며, 각 record는 deterministic greedy decoding, context 5개, CAD alpha=0.5, reference SCD(alpha=1.1, beta=0.9, T_start=5)를 기록한다.

## 품질 평가 범위

| 항목 | 값 |
|---|---:|
| RAGAS metric cell | 1915 / 1920 |
| faithfulness 명제 공백 cell | 5 |
| answer relevancy·context precision·context recall | 480 / 480씩 |
| HyDE faithfulness primary | 60 paired queries |
| CAD faithfulness primary | 58 paired queries |

faithfulness 명제 공백은 원본 평가 결과에 그대로 보존한다. 해당 지표의 대응 비교는 양쪽 점수가 존재하는 질의 단위로 계산하며, 다른 지표와 생성·언어 분석의 표본 수는 유지한다.

## 원본 artifact 해시

| 경로 | SHA-256 |
|---|---|
| `experiments\results\main_generation\main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl` | `916817150e40e0d2803f7e145633d13737c2304d17efdc4d42dc65cb4ed007d5` |
| `experiments\results\extended_validation\extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl` | `93c0932f4f5071bf726e4cd5a31c7a9cc02ef243775fdef99a1a0d486b51f41e` |
| `experiments\results\evaluation\main-hyde-cad-scd-reference-scd-gpt4o-official\merged.ragas_scores.json` | `700a2932a03bf615aab849297d6114968aafeff9bd49c0dfa0659050e8a4ef08` |
| `experiments\results\evaluation\ext60_gpt4o\merged.ragas_scores.json` | `fc705e3d3580246d53f17ff179027c2b43f3584f785fea3f047934ff2178476b` |
| `experiments\data\query_splits\decoder_main_queries.json` | `378a7a3e6ffb446759b228943010e2a4861d4efb9626f3d066dae40d43410ff5` |
| `experiments\data\query_splits\extended_validation_questions.json` | `91e9c1da0dec40c32a8370881cf708b2b4229a7d40d15206ab5f1cd78803061c` |
| `experiments\results\analysis\extended_validation_60_analysis.json` | `50870fc6c48407b22daf32861465accd459bd3972e5a80c58a3bb822d23a8e4d` |

## 최종 근거 범위

최종 원고는 60-query 주 평가와 240개 SCD ON/OFF 대응쌍의 한국어 문자 비율 분석을 사용한다. 별도의 SCD 대칭 정규화·다중 judge 패널은 최종 원고의 수치, 표, 그림, 결론에 포함하지 않는다.
