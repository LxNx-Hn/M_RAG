# 한계와 향후 과제

이 문서는 `THESIS.md`와 `THESIS_KO.md`의 현재 실험 범위와 결과 해석을 요약한다.

## 실험 범위

- 영어 논문 4편, 한국어 질의 19개
- HyDE × CAD × SCD 8개 설정, 총 152개 생성
- HyDE 품질 대비 19쌍, CAD 품질 대비 19쌍
- SCD 언어 대응쌍 76개, 동일 문맥 대칭 품질 대응쌍 38개
- 생성 모델: `K-intelligence/Midm-2.0-Base-Instruct`
- 검색 backbone: BGE-M3, BM25, weighted RRF, CrossEncoder reranking
- 품질 지표: faithfulness, answer relevancy, context precision, context recall
- 언어 지표: 직접 한국어 비율과 0.5 기준 언어 이탈률

## 결과 요약

| 대비 | 측정 결과 | 해석 |
|---|---:|---|
| HyDE on−off<br>(CAD off, SCD off) | answer relevancy `+0.0303 [+0.0016, +0.0615]` | 작은 양의 차이, 나머지 품질 지표 구간은 0 포함 또는 경계 |
| CAD on−off<br>(HyDE off, SCD off) | faithfulness `+0.0023 [−0.0903, +0.0952]` | 동일 문맥 대비에서 품질 개선 미확인 |
| SCD on−off | 한국어 비율 `+0.2203`, 68/76 개선 | 한국어 언어 준수 증가 |
| SCD 언어 이탈 | 26/76 → 12/76 | 0.5 미만 출력 감소 |

SCD의 평균 한국어 비율 차이는 HyDE × CAD 네 조합에서 모두 양수였고, HyDE-off의 byte-identical context 38쌍에서도 `+0.2198`이었다. 대칭 품질 패널에서는 faithfulness의 네 신뢰구간이 모두 0을 포함했다. Answer relevancy 평균은 네 language-by-judge 패널에서 음수였지만 비영점 구간은 `gpt-4o`에서만 나타나 두 judge에서 반복되는 차이로 확인되지 않았다.

## 연구 한계

- 논문 4편과 질의 19개이므로 모든 학술 분야로 일반화할 수 없다.
- HyDE·CAD 품질 대비가 각각 19쌍이어서 신뢰구간이 넓다.
- RAGAS 품질 점수는 LLM judge와 언어 정규화 조건에 영향을 받는다.
- HyDE-on 셀은 가상 문서가 설정별로 다시 생성되어 CAD on/off 문맥이 충분히 일치하지 않았다. CAD 결론은 19/19 문맥이 같은 HyDE-off 대비에 한정한다.
- 사람 평가는 수행하지 않았다.
- 숫자 환각률은 숫자·단위·대상 entity를 연결한 전용 주석이 없어 측정하지 않았다.
- 질의 유형별 표본이 작아 A–F 경로별 정량 최적화 결과를 제시하지 않는다.
- CAD는 매 생성 step에서 무문맥 분기를 계산하므로 추론 비용이 증가한다.
- SCD의 언어 token partition은 tokenizer의 subword 구성에 영향을 받는다.
- 서비스 계층은 실제 다중 사용자 부하, 관측성, 장기 운영 검증이 더 필요하다.

## 향후 과제

- 8편 이상, 3개 이상 분야, 40개 이상 독립 질의로 외적 타당성 확대
- 모든 조합이 같은 HyDE 검색 결과를 공유하도록 생성 설계 고정
- 독립 제공자 judge와 블라인드 사람 평가 추가
- 숫자 근거 주석을 이용한 numeric hallucination 분석
- 충분한 유형별 표본을 이용한 A–F 경로 정책 검증
- CAD cache 최적화 전 정확성 parity test
- SCD tokenizer별 target·neutral·distractor partition 검증
- 서비스 부하 시험, 모니터링, 장애 복구 검증

현재 결과에서 가장 뚜렷한 차이는 SCD의 한국어 언어 준수 증가다. HyDE의 answer relevancy 차이는 작은 양의 값이며, CAD를 포함한 나머지 품질 효과는 더 큰 표본과 독립 평가로 확인해야 한다.
