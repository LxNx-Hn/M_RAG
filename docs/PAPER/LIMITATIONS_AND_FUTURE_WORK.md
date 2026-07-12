# 한계와 향후 과제

이 문서의 내용은 `docs/PAPER/THESIS.md` 15장(한계와 향후 과제)에 학술 논문 형식으로 통합되어 있다.

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
| 사전 정의 harm(기준 ≥0.7 → SCD-on <0.65) | 9/28 | **0/20** |

`reference_scd`의 RAG-quality 재평가는 NIM judge가 수렴하지 못한 뒤 해당 트랙에
한해 OpenAI `gpt-4o`를 사용했고, 0/608 null cells의 점수표를 만들었다. 다만
SCD-on record의 context만 한국어로 번역했으므로 번역 처치와 SCD가 결합되어 있다.
SCD-off 답변도 50/76이 한국어 비율 0.5 이상이었고 GT는 영어로 남았으며, HyDE-on
38쌍 중 25쌍은 검색 context도 달랐다. 따라서 faithfulness −0.048,
answer_relevancy −0.057, context_precision +0.030, context_recall −0.066은 그
비대칭 평가 프로토콜에서 관찰된 기술적 차이이지 SCD만의 인과 효과가 아니다.

이 한계를 줄이기 위한 대칭 후속 평가도 완료했다. HyDE-off 4개 config의 76개
record만 사용해 38개 SCD on/off 쌍의 검색 context가 byte 단위로 같은지 확인하고,
질문·답변·GT·중첩 context 전부에 같은 규칙으로 영어 및 한국어 정규화를 적용했다.
두 패널의 총 304개 지표 셀은 모두 채워졌다. 19개 query cluster를 10,000회 paired
bootstrap한 결과는 다음과 같다.

| 지표 | 영어 패널 mean delta [95% CI] | 한국어 패널 mean delta [95% CI] | 판정 |
|---|---:|---:|---|
| faithfulness | +0.0071 [−0.0596, +0.0714] | −0.0283 [−0.1044, +0.0510] | 양쪽 모두 0 포함, 방향 미확정 |
| answer relevancy | −0.0910 [−0.1725, −0.0240] | −0.0752 [−0.1501, −0.0138] | 양쪽 모두 음의 구간 |

같은 입력을 고정 `gpt-4.1-2025-04-14`로 교차 채점한 추가 304셀도 null 없이
완료했다.

| 지표 | 영어 cross-judge mean delta [95% CI] | 한국어 cross-judge mean delta [95% CI] | 판정 |
|---|---:|---:|---|
| faithfulness | −0.0579 [−0.1322, +0.0060] | −0.0326 [−0.0997, +0.0226] | 양쪽 모두 0 포함 |
| answer relevancy | −0.0327 [−0.0851, +0.0129] | −0.0356 [−0.1149, +0.0315] | 양쪽 모두 0 포함 |

따라서 `gpt-4o`의 answer-relevancy 음의 구간은 고정 cross-judge에서 재현되지
않았다. 생성 후 정규화이고, 두 judge가 같은 제공자에 속하며, 한국어 답변의 실제
번역 노출도 SCD-off 23/38, SCD-on 11/38로 달랐다. query cluster가 19개이고 사람
평가는 없다. 최종 판정은 “judge에 강건한 0이 아닌 RAG-quality 효과 없음”이다.

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
성공했다. 다만 15/26 threshold rescue이고 12/76 SCD-on 답변은 여전히 0.5
미만이므로 "완전 해결"은 아니다. 첫 RAG-quality 패널은 SCD-on-only 문맥 번역과
검색 변동이 섞인 민감도 분석이다. 후속 대칭 패널은 동일 검색 context와 양쪽 조건의
동일 정규화 규칙을 달성했지만, faithfulness 방향은 여전히 미확정이고 answer
relevancy의 `gpt-4o` 음의 구간은 고정 `gpt-4.1`에서 재현되지 않았다. 따라서 "SCD가 환각을 줄인다/늘린다"
또는 "RAG 품질을 인과적으로 낮춘다"는 결론은 보류하고, 독립 judge와 인간 평가로
검증해야 한다.
상세 분석은 `experiments/reports/reference_scd_rerun_report.md` 및
`reference_scd_rerun_report_KO.md`,
`experiments/reports/reference_scd_symmetric_cross_judge_report.md`에 둔다.

## 기타 향후 과제

- 더 큰 논문 집합·독립 작성 쿼리로 외적 타당성 강화
- 다른 제공자의 judge와 인간 평가로 추가 강건성 검증
- 맹검 인간 평가와 사전 설계로 post-generation 정규화 의존성 제거
- 더 강한 publication venue를 위해 query/corpus 규모를 확장하고 `reference_scd` 품질 효과를 재검증
- 수치 환각·쿼리 유형별 세부 분석(현 실험 미측정)
- vLLM 기반 고효율 서빙과 CAD/SCD 재설계
- 서비스 배포용 다중 GPU 추론 서버 분리, 부하 테스트, 관측성 강화

