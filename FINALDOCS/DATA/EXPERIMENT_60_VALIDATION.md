# 60개 질의 RAG-Cube 실험 검증

이 문서는 저장된 생성·평가 artifact와 현재 source hash를 정리한다.

## 생성 검증

| 항목 | 결과 |
|---|---:|
| 기존 retained 질의 | 19 |
| held-out extension | 41 |
| 질의-대상문서 쌍 | 60 |
| RAG-Cube 조건 | 8 |
| 생성 record | 480 |
| 조건별 record | 60 |
| 대상 문서 | 4 |
| HyDE primary 대응쌍 | 60 |
| CAD 동일 문맥 primary 대응쌍 | 60 |
| SCD configuration-matched ON/OFF 대응쌍 | 240 |
| HyDE OFF 동일 문맥 SCD 대응쌍 | 120 |

고정 생성 모델은 `K-intelligence/Midm-2.0-Base-Instruct`이며 final answer는 deterministic greedy decoding, `max_new_tokens=512`로 생성하였다. HyDE hypothetical document는 temperature=0.1, top_p=0.9, sampling을 사용한다. CAD alpha=0.5, reference SCD는 alpha=1.1, beta=0.9, T_start=5를 사용한다.

## 평가 및 통계

RAGAS 0.2.15에서 OpenAI gpt-4o judge와 BAAI/bge-m3 embedding을 사용하였다. SCD ON quality evaluation은 retrieved context를 gpt-4o로 한국어 변환하고 generated answer는 그대로 유지했으며, SCD OFF는 저장된 영어 context를 사용하였다. Paired bootstrap은 query를 재표집 단위로 200,000회 수행했고 seed는 20260713이다.

| 항목 | 값 |
|---|---:|
| RAGAS metric cell | 1915 / 1920 |
| faithfulness 결측 cell | 5 |
| answer relevancy·context precision·context recall | 480 / 480씩 |
| HyDE faithfulness primary | 60 paired queries |
| CAD faithfulness primary | 58 paired queries |
| H0C1S0 faithfulness 평균 유효 n | 58 |
| H0C0S1 faithfulness 평균 유효 n | 57 |

## 핵심 결과

- HyDE answer relevancy: +0.0805, 95% CI [+0.0110, +0.1514].
- CAD same-context faithfulness: +0.0288, 95% CI [-0.0367, +0.0934], n=58.
- SCD HyDE-OFF same-context Korean-character ratio: +0.2182, 95% CI [+0.1880, +0.2487], n=120.
- SCD configuration-matched Korean-character ratio: +0.2289, 95% CI [+0.2051, +0.2532], n=240.

## 원본 artifact 해시

| 경로 | SHA-256 |
|---|---|
| `experiments\results\main_generation\main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl` | `916817150e40e0d2803f7e145633d13737c2304d17efdc4d42dc65cb4ed007d5` |
| `experiments\results\extended_validation\extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl` | `93c0932f4f5071bf726e4cd5a31c7a9cc02ef243775fdef99a1a0d486b51f41e` |
| `experiments\results\evaluation\main-hyde-cad-scd-reference-scd-gpt4o-official\merged.ragas_scores.json` | `0c10a2a5df0c7084919ed8a780b7ce200cb23939a37b76b026fc3f745dad61b9` |
| `experiments\results\evaluation\ext60_gpt4o\merged.ragas_scores.json` | `0b38b79b5f3a426197b275f61eacdb64d83814150deb1eb5ad5e4a338331f327` |
| `experiments\data\query_splits\decoder_main_queries.json` | `36c90ab2d4d13993a71abbfcab8f2a828e3487e802a68c228f4c97e3a482eac5` |
| `experiments\data\query_splits\extended_validation_questions.json` | `acc2211012904b23c30a4f16f70c18fbad4038c4a2ea76bcf1e602a5161efd23` |
| `experiments\results\analysis\extended_validation_60_analysis.json` | `6ec588a3a8cbe63e2cfe923286dfa3fad46c1a9cb4d59eb670bc6864e4455f57` |

## 최종 근거 범위

최종 원고는 60-query 분석 artifact와 저장 generation/evaluation record를 사용한다. 실제 질문·검색 근거·생성 답변 사례는 `FINALDOCS/EVIDENCE/IO_CASES/`의 E01~E06과 `evidence_manifest_60q.json`의 query/config provenance로 연결한다.
