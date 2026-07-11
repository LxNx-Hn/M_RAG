# 한계와 향후 과제

이 문서의 내용은 `docs/PAPER/THESIS.md` 8장(한계와 향후 과제)에 학술 논문 형식으로 통합되어 있다.

## 논문 실험 한계

- CAD와 SCD는 생성 단계 제어이므로 추론 비용을 증가시킬 수 있음
- CAD는 질문 단독 입력의 생성 분포를 함께 계산하므로 디코딩 비용이 추가됨
- SCD의 언어 판별은 토큰과 문자 규칙에 영향을 받음
- 영어 기술 용어가 많은 학술 문서에서는 SCD 강도를 조정해야 할 수 있음
- 자동 평가는 judge 모델 품질에 영향을 받음
- 실험 결과는 사용한 논문 집합과 질의 구성에 따라 달라질 수 있음
- 운영 규모 확장과 다중 사용자 부하 검증은 서비스화 검증 단계에서 다룸

## 측정된 결과 요약

본 실험(19쿼리 × 8config = 152생성, Mi:dm 2.0 Base / A100 80GB, 고정 NIM judge
`meta/llama-3.3-70b-instruct`로 RAGAS 채점, 583/608 셀)에서:

- CAD: faithfulness +0.044 (paired 25승/17패) — 설계 목적대로 근거 충실성 향상
- HyDE: answer_relevancy +0.070, context_recall +0.026, context_precision −0.056 — recall/precision 트레이드오프
- SCD v1(`penalty_additive`): 4개 메트릭 및 한국어 비율 모두 중립(직접 측정 Δ −0.014; 상세 언어비율 분석 Δ −0.0137) — **v1 구현에서는 null 결과**

이후 완료된 `reference_scd` 재실험은 원문 논문(arXiv 2511.09984)에 맞춰
목표어 곱셈 부스트 `alpha=1.1`, 비목표어 곱셈 페널티 `beta=0.9`,
`Tstart=5` warm-up을 복원한 corrected implementation 결과다.

| 항목 | SCD v1(`penalty_additive`) | `reference_scd` |
|---|---:|---:|
| 언어비율 mean paired delta | −0.0137 | **+0.2203** |
| 한국어 증가 / 감소 (76쌍) | 22 / 24 | **68 / 3** |
| drift rescue @0.5 | 2/19 | **15/26** |
| 이미 좋은 답변 harm | 9/28 harmed | **0/20 harmed** |

`reference_scd`의 RAG-quality 재평가는 NIM judge가 60시간 이상 실행 후 첫 pass
38.6% null rate에 머물러 수렴하지 못했기 때문에, 해당 트랙에 한해 OpenAI
`gpt-4o`를 사용했다. 이 재평가는 SCD-on record의 context만 한국어로 번역해
cross-lingual judging confound를 통제했고, 0/608 null cells로 수렴했다.
그 결과 SCD는 language adherence에서는 결정적으로 성공했지만 RAGAS 품질에서는
faithfulness −0.048, answer_relevancy −0.057, context_recall −0.066으로 3/4
메트릭 비용을 보였고, context_precision만 +0.030으로 개선했다.

상세는 `experiments/reports/phase8_official_evaluation_summary.md`,
`phase8_limitations.md`, `phase8_scd_failure_analysis.md`,
`reference_scd_rerun_report.md`, `reference_scd_rerun_report_KO.md` 참조.

## SCD 재현 결과 (완료됨)

원문 방법(arXiv 2511.09984)은 (1) 비목표어 β 페널티, (2) 목표어 α 부스트, (3)
cold-start warm-up 세 요소를 갖지만, 본 구현은 (1)만을 그것도 가법 상수(−0.3)로
적용했다. 그 결과 한국어 토큰을 끌어올리지 못하고(α 부재), 확신 있는 영어 연속에
너무 약하며(가법 −0.3), 초기 붕괴를 방어하지 못한다(warm-up 부재). 이 원인
분석은 v1 실패 설명으로 유지된다.

다만 이 항목은 더 이상 미해결 향후 과제가 아니다. `reference_scd` rerun에서
α 부스트 + 곱셈적 스케일링 + warm-up을 원문 논문 설정(`alpha=1.1`,
`beta=0.9`, `Tstart=5`)으로 복원했고, 언어 이탈 제어 목표에서는 명확히
성공했다. 동시에 language-matched RAG-quality 평가에서는 faithfulness,
answer_relevancy, context_recall 비용이 확인되었다. 특히 "everything on"
(`hyde_on__cad_scd`) 설정의 faithfulness 개선(0.8159 → 0.8674, +0.0515)은
HyDE(+0.0732)와 CAD(+0.0187)에 기인하며, SCD 자체의 isolated faithfulness
기여는 −0.0480이다. 따라서 현재 결론은 "SCD는 언어 적응에는 성공하지만
환각 감소에는 기여하지 않고, 일부 RAG-quality 이득을 비용으로 지불한다"이다.
상세 분석은 `experiments/reports/reference_scd_rerun_report.md` 및
`reference_scd_rerun_report_KO.md`에 둔다.

## 기타 향후 과제

- 더 큰 논문 집합·독립 작성 쿼리로 외적 타당성 강화
- judge 모델 강건성 검증(2차 judge 교차 채점) 및 인간 평가 비교
- cross-lingual judging confound를 통제한 context-translation 평가 설계를 다른 언어쌍·backbone에도 확장
- 더 강한 publication venue를 위해 query/corpus 규모를 확장하고 `reference_scd` trade-off가 유지되는지 재검증
- 수치 환각·쿼리 유형별 세부 분석(현 실험 미측정)
- vLLM 기반 고효율 서빙과 CAD/SCD 재설계
- 서비스 배포용 다중 GPU 추론 서버 분리, 부하 테스트, 관측성 강화

