# 참고문헌 재분류 설명

이 문서는 Phase 5 기준으로 참고문헌을 다시 분류한다. 목표는 "무엇을 실제 구현/실험 축으로 사용했는가"와 "무엇은 배경 또는 향후 과제인가"를 분리하는 것이다.

## 핵심 원칙

- 핵심 구현 참고문헌은 HyDE/CAD/SCD factor analysis와 고정 Paper-RAG backbone에 직접 필요한 문헌만 둔다.
- 서비스 라우팅은 졸업작품 시스템 통합 계층이므로, 라우터 자체를 새로운 thesis algorithm으로 주장하지 않는다.
- 경량 로컬 평가는 RAGAS-inspired 평가 설계로 설명한다. RAGAS 패키지를 실행한 결과로 쓰지 않는다.
- 결과 수치는 검증된 실험 산출물이 생기기 전까지 쓰지 않는다.

## Core Implementation

| 범주 | 문헌 역할 | M-RAG에서의 사용 |
|---|---|---|
| RAG original | 검색 결과를 생성 입력에 넣는 기본 패러다임 | fixed Paper-RAG backbone |
| RAG survey / best practices | RAG 구성요소와 설계 선택 배경 | backbone 설계 설명 |
| BGE-M3 | 다국어 dense retrieval | 한국어 질문과 영어 논문 청크를 같은 벡터 공간에서 검색 |
| BM25 | sparse keyword retrieval | 수치, 약어, 고유명사 매칭 보완 |
| RRF | dense/sparse rank fusion | 점수 단위가 다른 검색 결과 결합 |
| Passage re-ranking with BERT | cross-encoder reranking 배경 | 초기 검색 결과 재정렬 |
| MS MARCO | reranker 학습/평가 배경 | reranker 설명 보조 |
| HyDE | hypothetical document retrieval expansion | main experimental axis |
| CAD | Context-Aware Decoding | main experimental axis |
| SCD | Korean-target Soft Constrained Decoding | main experimental axis |

## Evaluation Reference

| 문헌 | Phase 5 위치 |
|---|---|
| RAGAS | 평가 지표 설계 배경 및 future-compatible skeleton |
| Local judge designs | lightweight evaluator / RAGAS-inspired evaluator |
| Language drift metrics | 한국어 답변 비율과 language drift 측정 설계 |
| Numeric hallucination metrics | 수치 주장과 evidence support 측정 설계 |

## Background

| 범주 | 사용 이유 |
|---|---|
| Korean or multilingual RAG | 한국어 질의와 영어 논문 근거의 불일치 문제 배경 |
| Language-drift studies | 출력 언어 제어 필요성 배경 |
| Lost in the Middle | 긴 컨텍스트에서 근거 위치 민감도 설명이 필요할 때 사용 |

## Related Work / Future Work

다음 계열은 core implementation으로 주장하지 않는다. 필요하면 관련연구 또는 향후 과제에서만 다룬다.

| 범주 | Phase 5 처리 |
|---|---|
| multi-query fusion methods | HyDE와 구분하고 future work로만 둠 |
| hierarchical retrieval trees | 현재 thesis 핵심 축에서 제외 |
| compression-specific RAG methods | backbone 설명의 배경으로만 제한 |
| self-reflective / corrective retrieval methods | route policy의 배경 또는 future work로만 제한 |
| graph-based RAG methods | future work |
| multimodal document retrieval methods | future work |
| agentic paper-QA systems | related work |
| late-interaction retrievers not implemented in runtime | background 또는 related work |

## Remove From Core Claims

다음 주장은 core claim에서 제거한다.

- A-F route itself is a new algorithm.
- The system produced verified improvements before the main matrix is run.
- The local evaluator is the same as executing the RAGAS package.
- Service-route qualitative examples are quantitative experiment queries.
- Any unsupported related-work method is implemented as a thesis method without code evidence.

## Safe Wording

Use:

- "HyDE/CAD/SCD factor analysis"
- "fixed Paper-RAG backbone"
- "Korean-query / English-paper RAG"
- "graduation-project service route"
- "RAGAS-inspired lightweight evaluator"
- "future RAGAS-compatible skeleton"

Avoid:

- claiming result values before verified artifacts exist
- presenting routed service integration as the core algorithmic contribution
- presenting unsupported related-work methods as implemented methods
