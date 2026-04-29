# 실험표 해석 가이드

## 목적

실험표는 숫자를 채우는 것이 목적이 아니다. 어떤 모듈이 어떤 문제를 줄였는지 설명할 수 있어야 한다.

이 문서의 표 번호와 구성은 `docs/PAPER/THESIS.md` 6장(실험 결과)과 일치한다.

---

## Table 1: Track 1 모듈 누적 ablation

보는 법

- Naive RAG는 기준선이다
- 설정 1→2→3→4→5→6 순서로 모듈이 누적 추가된다
- 설정 2와 설정 1의 차이 = HyDE 쿼리 확장의 기여
- 설정 3과 설정 2의 차이 = 하이브리드 검색(BM25 + RRF)의 기여
- 설정 4와 설정 3의 차이 = CAD(α=0.5)의 기여
- 설정 5와 설정 4의 차이 = SCD(β=0.3)의 추가 기여
- 설정 6과 설정 5의 차이 = 컨텍스트 압축 + 섹션 필터의 기여

좋은 패턴

- Full System의 Faithfulness가 기준선보다 높음
- Context Precision이 하이브리드 검색 추가 단계에서 상승
- CAD 추가 시 Faithfulness가 뚜렷하게 상승

주의할 패턴

- 모든 설정의 Context Precision이 동일하면 평가 또는 검색 샘플링 문제 가능성
- Faithfulness가 모두 0.95 이상이면 judge가 차이를 구분하지 못할 수 있음

---

## Table 2: CAD/SCD 디코더 조합 비교

보는 법

- none(baseline), CAD only, SCD only, CAD+SCD 네 조합을 비교한다
- CAD only는 Faithfulness와 Numeric Hallucination Rate에 주목
- SCD only는 Language Drift Rate에 주목
- CAD+SCD는 두 지표가 동시에 개선되는지 본다

주의할 점

- CAD는 답변을 더 보수적으로 만들 수 있다
- SCD는 영어 전문용어(BERT, Transformer 등)까지 억제할 수 있다
- 둘을 같이 쓰면 디코딩 비용이 추가된다 (KV cache로 최소화)

---

## Table 3: CAD alpha sweep

보는 법

- alpha ∈ {0.0, 0.1, 0.3, 0.5, 0.7, 1.0}에서 Faithfulness 변화를 추적한다
- SCD는 비활성 상태이다
- 값이 클수록 파라메트릭 지식 억제가 강해진다

해석

- alpha=0.0은 CAD 비활성 (기준선)
- alpha가 너무 낮으면 환각 억제가 약하다
- alpha가 너무 높으면 답변 다양성이 줄고 생성 품질이 저하될 수 있다
- 최적 alpha는 Faithfulness와 Answer Relevancy의 균형점이다

---

## Table 4: SCD beta sweep

보는 법

- beta ∈ {0.1, 0.3, 0.5}에서 Language Drift Rate 변화를 추적한다
- CAD는 alpha=0.5으로 고정 활성 상태이다
- 값이 클수록 비한국어 토큰 억제가 강해진다

해석

- beta가 너무 낮으면 Language Drift 억제가 약하다
- beta가 너무 높으면 영어 기술 용어(모델명, 메서드명)가 부자연스럽게 억제된다
- 최적 beta는 Language Drift Rate과 Answer Relevancy의 균형점이다

---

## Table 5: Track 2 논문 도메인 특화 비교

보는 법

- Track 1 Full System을 기준선으로 하고 논문 도메인 특화 모듈의 추가 효과를 비교한다
- 섹션 필터(설정 2, 3)는 Context Precision에 영향을 주는 것이 자연스럽다
- RAPTOR 계층 검색(설정 4)은 전체 요약 질문에서 효과적이다
- 인용 추적(설정 5)은 참고문헌 관련 질의에서 Answer Relevancy에 기여한다

---

## 숫자가 이상할 때 점검 순서

1. 검색 결과가 실제로 달라지는지 `/api/chat/search`로 확인
2. Judge가 label을 제대로 반환하는지 `/api/chat/judge`로 확인
3. ground truth가 비어 있거나 잘못 연결되지 않았는지 확인
4. 같은 결과 JSON을 재사용하고 있지 않은지 확인
5. 전체 실험이 아닌 일부 resume 결과만 보고 있지 않은지 확인
6. `rank_labels` 방식과 `generate_judge` 방식의 점수 차이가 있는지 확인
