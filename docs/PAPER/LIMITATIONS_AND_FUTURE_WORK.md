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
- SCD: 4개 메트릭 및 한국어 비율 모두 중립(직접 측정 Δ −0.014) — **현 형태에서 null 결과**

상세는 `experiments/reports/phase8_official_evaluation_summary.md`,
`phase8_limitations.md`, `phase8_scd_failure_analysis.md` 참조.

## SCD null 결과의 원인 (핵심 향후 과제)

원문 방법(arXiv 2511.09984)은 (1) 비목표어 β 페널티, (2) 목표어 α 부스트, (3)
cold-start warm-up 세 요소를 갖지만, 본 구현은 (1)만을 그것도 가법 상수(−0.3)로
적용했다. 그 결과 한국어 토큰을 끌어올리지 못하고(α 부재), 확신 있는 영어 연속에
너무 약하며(가법 −0.3), 초기 붕괴를 방어하지 못한다(warm-up 부재). 재현을 위해
α 부스트 + 곱셈적 스케일링 + warm-up을 복원한 뒤 (α, β, T_start)를 드리프트
목표로 튜닝하는 것이 1순위 후속 과제다.

## 기타 향후 과제

- 더 큰 논문 집합·독립 작성 쿼리로 외적 타당성 강화
- judge 모델 강건성 검증(2차 judge 교차 채점) 및 인간 평가 비교
- 수치 환각·쿼리 유형별 세부 분석(현 실험 미측정)
- vLLM 기반 고효율 서빙과 CAD/SCD 재설계
- 서비스 배포용 다중 GPU 추론 서버 분리, 부하 테스트, 관측성 강화

