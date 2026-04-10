# M-RAG 학술 기여 클레임 (C1~C4)

> 이 문서는 졸업논문 심사 및 향후 논문 투고를 위한 기여 클레임 정의입니다.  
> 각 클레임은 구현 파일, 경쟁 논문, 방어 전략, 인정해야 할 한계를 포함합니다.

---

## 기여 수준 요약

| 클레임 | 유형 | Novelty | 필요 증거 |
|--------|------|---------|-----------|
| C1 | 시스템/공학 | 중간 (SciRAG, CRAG 대비 차별화) | Ablation Stage 5 delta, UI 스크린샷 |
| C2 | 시스템/공학 | 중간 (CG-RAG, HippoRAG2 대비) | Pipeline D 데모, 소스 수 비교 |
| **C3** | **실험적** | **높음 — 선행 연구 없음** | RAGAS CAD on/off 비교 테이블, α 어블레이션 |
| C4 | 공학 | 중간 (arXiv preprint 기반) | Ablation Stage 6 delta, β 어블레이션 |

**C3가 논문의 핵심 기여입니다. C3는 실험 결과 없이 방어 불가능합니다.**

---

## C1: 5-파이프라인 동적 라우팅 + 투명한 라우트 배지

### 클레임 문구 (논문용)

> "We present a query routing system that classifies academic paper queries into five semantic categories — simple QA, section-specific, comparative, citation-tracking, and summarization — and routes each to a specialized retrieval pipeline. Unlike existing RAG systems that apply uniform retrieval strategies, our router makes its decision visible to the user via a route badge in the UI, providing full interpretability. The routing logic is auditable through published configuration (ROUTE_MAP in config.py) and a keyword-score computation, contrasting with commercial systems whose routing is opaque."

### 구현 파일

- `backend/modules/query_router.py` — QueryRouter, RouteType enum, RouteDecision
- `backend/config.py` — ROUTE_MAP (라우팅 키워드 설정)
- `backend/pipelines/pipeline_{a~e}_*.py` — 5개 파이프라인 구현
- `frontend/src/components/chat/RouteBadge.tsx` — 라우트 배지 UI

### 경쟁 논문 대응

| 논문 | 차이점 |
|------|--------|
| Gao et al. (2024) "Modular RAG" [arXiv 2407.21059] | 이론 프레임워크 제시. 본 연구는 학술 논문 도메인에 특화된 구체적 인스턴스화 |
| Self-RAG (Asai et al., ICLR 2024) | LLM 생성 reflection 토큰으로 라우팅. 본 연구는 규칙 기반 — 추론 오버헤드 없음, 완전 감사 가능 |
| SciRAG (arXiv 2511.14362) | 섹션 인식 검색 있으나 단일 파이프라인. 5-way 동적 분기 없음 |

### 방어 전략

- Ablation 6단계 중 Stage 5 추가 시 성능 향상 delta가 라우팅의 기여를 정량화
- UI의 라우트 배지는 논문의 Figure로 사용 가능 (투명성 시각화)
- 키워드 스코어 로직이 `config.py`에 완전 공개되어 재현 가능

### 인정해야 할 한계

- 키워드 기반 라우팅은 비관습적 표현 쿼리에서 오분류 가능
- 학습 기반 라우터(distilbert-multilingual 분류기 등) 대비 정확도 낮을 수 있음
- **Future Work**: 쿼리-경로 쌍 레이블 데이터 구성 후 경량 분류기로 교체

---

## C2: arXiv API 인용 추적 + 쿼리 시 코퍼스 자동 확장

### 클레임 문구 (논문용)

> "Pipeline D implements query-triggered corpus expansion: when a user asks about citations or references, the system automatically parses the reference section of uploaded papers, queries the arXiv API for cited paper metadata and PDFs, downloads and indexes them into the vector store, and reruns hybrid retrieval over the expanded corpus. This allows the knowledge base to grow automatically in response to user intent, without manual curation."

### 구현 파일

- `backend/modules/citation_tracker.py` — arXiv API 연동, 레퍼런스 파싱, PDF 다운로드
- `backend/pipelines/pipeline_d_citation.py` — 전체 인용 추적 파이프라인
- `backend/config.py` — ARXIV_MAX_RESULTS (최대 수집 논문 수)

### 경쟁 논문 대응

| 논문 | 차이점 |
|------|--------|
| CG-RAG (SIGIR 2024) | 인용 그래프 다중 홉 추론 가능하나 오프라인 그래프 사전 구축 필요. 본 연구는 쿼리 시 on-demand 확장 |
| HippoRAG2 (Gutiérrez et al., arXiv 2025) | 오프라인 그래프 구축. 본 연구는 온라인, 동적 |

### 방어 전략

- arXiv에 공개된 논문의 인용 체인을 자동 추적하는 기능은 NotebookLM, SciRAG, PaperQA2 모두 미구현
- Pipeline D 전후 검색 가능 소스 수를 비교하여 코퍼스 확장 효과 정량화 가능

### 인정해야 할 한계

- **1-hop만 지원**: 인용된 논문의 인용 논문을 재귀적으로 추적하지 않음
- **arXiv 전용**: 저널 전용 논문(IEEE, ACM DL 등)은 자동 수집 불가
- **Future Work**: 2-hop 탐색 + Semantic Scholar API 연동으로 커버리지 확장

---

## C3 (핵심 기여): 한국어 학술 RAG에서 CAD 환각 억제 최초 실증

### 클레임 문구 (논문용)

> "We apply Context-Aware Contrastive Decoding (CAD; Shi et al., NAACL 2024) to a Korean-language academic paper QA system and evaluate its hallucination suppression effect through RAGAS faithfulness scores and ablation across α ∈ {0.1, 0.3, 0.5, 0.7, 1.0}. To our knowledge, no published work has evaluated CAD in a Korean-language academic RAG setting. The original CAD paper (Shi et al., 2023) evaluates English-only tasks (NQ, TriviaQA, WebQ, SQuAD). We demonstrate that CAD's parametric knowledge suppression transfers to Korean academic queries processed by a Korean-specialized LLM (MIDM-2.0-Base-Instruct), with CAD-on showing improved faithfulness scores compared to CAD-off."

### 구현 파일

- `backend/modules/cad_decoder.py` — CADDecoder (LogitsProcessor)
- `backend/evaluation/ragas_eval.py` — RAGAS 평가 + compare_cad_on_off()
- `backend/evaluation/ablation_study.py` — run_cad_korean_evaluation()
- `backend/config.py` — CAD_ALPHA (기본값 0.5)

### 문헌 갭 증거

아래 검색어로 확인한 결과, 한국어 학술 RAG에서 CAD를 평가한 논문이 없음 (2026년 4월 기준):

- `"contrastive decoding Korean RAG"` → 결과 없음
- `"context-aware contrastive decoding Korean"` → 결과 없음
- `"CAD Korean academic RAG"` → 결과 없음
- `"hallucination suppression Korean RAG"` → 일반 프롬프트 기법 연구만 존재

**원논문(Shi et al.) 평가 벤치마크**: NQ, TriviaQA, WebQ, SQuAD — 모두 영어. 한국어/학술 도메인 없음.

### 필수 실험 요구사항

이 클레임을 방어하려면 **반드시 실험 결과**가 필요합니다:

```
1. 최소 15개의 ground_truth가 설정된 쿼리 (test_queries.json의 cad_ablation 포함)
2. 하나의 표준 테스트 논문 선정 및 ground_truth 채움
3. compare_cad_on_off() 실행:
   - CAD on (α=0.5) vs CAD off 비교
   - RAGAS faithfulness, answer_relevancy delta 보고
4. run_cad_korean_evaluation() 실행:
   - α ∈ {0.1, 0.3, 0.5, 0.7, 1.0} 어블레이션
   - 논문 Table 2로 직접 사용
```

### 논문에서 표현하는 방법

```
"This is the first empirical evaluation of Context-Aware Contrastive Decoding
(CAD) in a Korean-language academic RAG setting."

주의: "Korean RAG에서 가장 좋은 방법"이라는 주장은 금지.
     "CAD를 Korean academic RAG에 적용하고 그 효과를 측정한 최초 연구"로 표현.
```

### 경쟁 논문 대응

| 논문 | 차이점 |
|------|--------|
| Shi et al. (NAACL 2024) [arXiv 2305.14739] | CAD 원논문. 영어 전용. 학술 도메인 없음. **인용하여 기반으로 삼아야 함** |
| SciRAG (2025) | CAD 또는 decoding-time 환각 억제 없음 |
| PaperQA2 | 신뢰도 점수 사용, decoding logit 개입 없음 |

### 인정해야 할 한계

- CAD는 2개의 forward pass를 수행하여 추론 오버헤드 발생 (첫 스텝 후 KV cache로 완화)
- α 최적값은 데이터셋에 따라 다를 수 있음
- 본 연구의 평가 규모가 작을 경우 (15~25 쿼리), 통계적 유의성에 주의

---

## C4: SCD로 영문 논문 컨텍스트에서 한국어 이탈 방지

### 클레임 문구 (논문용)

> "We implement Selective Context-aware Decoding (SCD; Li et al., arXiv 2511.09984, 2025) as MODULE 13B, applying non-target-language token penalties (β ∈ {0.1, 0.3, 0.5}) to prevent language drift when English academic paper chunks dominate the retrieval context. Combined with CAD (MODULE 13A), the system applies both decoding-time interventions simultaneously through HuggingFace's LogitsProcessorList, addressing two distinct failure modes: parametric knowledge interference (CAD) and language drift to English (SCD)."

### 구현 파일

- `backend/modules/scd_decoder.py` — SCDDecoder (LogitsProcessor)
- `backend/config.py` — SCD_BETA (기본값 0.3)
- `backend/evaluation/ablation_study.py` — Stage 6 (Full System) delta

### 경쟁 논문 대응

| 논문 | 차이점 |
|------|--------|
| Li et al. (arXiv 2511.09984, 2025) | SCD 원논문. 영문 RAG에서 타 언어 생성 방지 연구. 본 연구는 한국어 학술 RAG에 적용 |

### 주의사항

- Li et al. (2025)는 arXiv **preprint**이며 주요 학술지 게재 미확인 (2026년 4월 기준)
- 논문에서 인용 시: "following the approach proposed by Li et al. (2025, arXiv preprint)" 로 표현
- SCD 자체는 non-target-language token penalty 개념의 독립적 구현

### 인정해야 할 한계

- **기술 용어 패널티 문제**: SCD가 "BERT", "Transformer", "GPT" 같은 영어 기술 용어에도 패널티 적용
  - 현재 예외 목록: 숫자, 공백, 구두점만 — 학술 기술 용어 제외 필요
- **Future Work**: 논문 제목/초록에서 기술 용어를 추출하여 패널티 예외 목록 자동 구성

---

## 검증 vs 적용 범위 (포지셔닝)

### 검증 도메인 (논문에서 정량 평가)

- 학술 논문 4편 (RAGAS + Ablation, C1~C4 표)
- NLP/ML 논문, 비AI 논문, 한국어 논문, 일반 문서

### 적용 도메인 (기능 시연, 정량 평가 미수행)

- **강의/교재 PDF**: 정의/정리/증명/예제 섹션 감지, BNF/EBNF/코드 블록 보존, 수식 보존
- **특허 명세서**: 청구항/배경기술/상세한 설명 섹션 감지, Google Patents/KIPRIS 인용 특허 추적
- **일반 기술 문서**: 장/절 구조 감지, A경로 fallback

### 메시지

> M-RAG의 학술 기여(C1~C4)는 **논문 도메인에서 검증**되었으며, 강의/교재/특허 문서는 **적용 범위 확장 시연**입니다.
> 정량 평가는 논문 도메인에서만 수행하며, 강의/특허 시연은 기능 데모로 제시합니다.

---

## 논문 포지셔닝 전략

### 주장 계층

```
강한 주장 (데이터 필요):
  C3: "한국어 학술 RAG에서 CAD를 평가한 최초 연구"
  → RAGAS faithfulness delta 테이블 필요

중간 주장 (구현 증거):
  C1: "5-파이프라인 동적 라우팅 with 투명한 라우트 배지"
  C4: "CAD + SCD 이중 decoding-time 개입"
  → 코드 + Ablation 테이블

공학 기여 (데모 충분):
  C2: "쿼리 시 arXiv 코퍼스 자동 확장"
  → Pipeline D 실행 로그
```

### 심사위원 예상 질문 대응

**Q: NotebookLM도 비슷한 기능이 있지 않나요?**  
A: NotebookLM의 AI 아키텍처는 미공개입니다. 공개된 것은 웹 레이어(Angular, TypeScript, Firebase) 뿐이며, RAG 구조, 라우팅 전략, 환각 억제 방법은 알 수 없습니다. M-RAG는 모든 구성요소가 오픈소스로 공개되어 있어 재현 가능합니다.

**Q: 한국어 CAD 평가가 영어와 무엇이 다른가요?**  
A: 한국어는 MIDM 같은 언어 특화 LLM을 사용하며, 검색 컨텍스트가 영어(논문 원문)와 쿼리가 한국어인 크로스링구얼 상황입니다. 이 상황에서 CAD의 파라메트릭 지식 억제가 효과적으로 작동하는지 확인한 것이 기여입니다.

**Q: 평가 데이터셋이 충분한가요?**  
A: 15~25개의 CAD 어블레이션 전용 쿼리로 초기 평가합니다. 제한적인 규모를 인정하되, 이것이 "CAD가 Korean RAG에 적용 가능하다"는 존재 증명(existence proof)으로서의 기여임을 명확히 합니다.
