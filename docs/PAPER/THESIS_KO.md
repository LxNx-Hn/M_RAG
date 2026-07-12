# M-RAG: 한국어 질의-영어 논문 RAG를 위한 HyDE × CAD × SCD 요인 분석

## 1. 초록

검색 증강 생성(Retrieval-Augmented Generation, RAG)은 외부 문서를 검색한 뒤 검색 근거에 조건화하여 답변을 생성한다. 그러나 한국어 사용자가 영어 학술논문을 질의하는 환경에서는 일반적인 단일언어 RAG보다 두 가지 문제가 추가된다. 첫째, 한국어 질의와 영어 학술 문장 사이의 언어·문체 차이를 넘어 관련 근거를 찾아야 한다. 둘째, 영어 근거를 사용하면서도 검색 문맥에 충실하고 안정적인 한국어 답변을 생성해야 한다. 관련 문단이 검색되더라도 생성 모델은 사전학습 지식에 의존한 환각을 추가하거나, 한국어 답변에 불필요한 영어 문장을 섞거나, 수치·기술 근거를 정확히 보존하지 못할 수 있다.

본 논문은 고정된 Paper-RAG 검색 backbone 위에서 HyDE(Hypothetical Document Embeddings), CAD(Context-Aware Decoding), 한국어 대상 SCD(Soft Constrained Decoding)의 효과를 완전요인실험으로 분석한다. HyDE는 검색 질의를 가상 답변 형태로 확장하는 검색 측 요소, CAD는 문맥 조건부 분포와 무문맥 분포를 대조하는 생성 측 충실도 제어, SCD는 디코딩 중 비목표 언어 토큰의 영향을 조절하는 언어 제어로 정의한다. 실험은 HyDE, CAD, SCD의 on/off 조합 8개와 19개 질의로 152개 답변을 생성하였다. 생성 모델은 Mi:dm 2.0 Base이며, BGE-M3·BM25·가중 RRF·CrossEncoder reranking으로 구성된 검색 backbone은 고정하였다.

원본 주실험은 NVIDIA NIM의 고정 judge와 RAGAS를 사용해 608개 지표 셀 중 583개를 채점하였다. CAD는 faithfulness를 paired `+0.044` 개선하였다. HyDE는 answer relevancy `+0.070`, context recall `+0.026`을 높였지만 context precision은 `−0.056` 낮춰 recall-precision trade-off를 보였다. 원본 `penalty_additive` v1 SCD는 faithfulness `+0.009`, 직접 한국어 비율 `−0.014`로 사실상 null 결과였다. 이후 참조 논문에 충실한 `reference_scd`를 별도 실험으로 재현한 결과, 직접 한국어 준수율은 76개 대응쌍에서 평균 `+0.2203` 증가했고 68쌍이 개선되었다. 그러나 대칭 전처리와 `gpt-4o`, 고정 `gpt-4.1-2025-04-14` 교차 judge 평가에서는 faithfulness의 방향이 확정되지 않았고 answer relevancy의 음의 효과도 judge 간 비영점 신뢰구간으로 재현되지 않았다. 따라서 SCD가 한국어 준수율을 개선한다는 결론과 RAG 품질을 개선하거나 저하시킨다는 결론을 분리한다.

본 연구의 기여는 새로운 범용 RAG 알고리즘을 제안하는 것이 아니라, 한국어 질의-영어 논문 RAG에서 세 요소를 분해해 재현 가능하게 비교하고, 실패한 v1 구현과 교정된 구현을 구분하며, 언어 준수 개선이 곧 RAG 품질 개선을 의미하지 않음을 보인 데 있다. 질의 유형별 효과와 숫자 환각률은 표본 및 전용 주석 부족으로 본 실행의 결과 주장에 포함하지 않는다.

**주제어:** 검색 증강 생성, 학술논문 질의응답, HyDE, Context-Aware Decoding, Soft Constrained Decoding, 한국어, 언어 이탈, RAGAS

## 2. 서론

학술논문은 초록, 서론, 방법, 실험, 결과, 한계, 참고문헌처럼 기능이 다른 구역으로 구성된다. “F1 점수가 얼마인가?”와 같은 질문에는 정확한 숫자 근거가 필요하고, “방법론을 설명하라”는 질문에는 방법 절의 문맥이 필요하다. 문서 비교는 두 논문에서 균형 있게 근거를 가져와야 하며, 인용 질의는 서지정보를 정확하게 다뤄야 한다.

RAG는 외부 문서를 검색하여 생성 모델에 제공하지만, 검색 성공만으로 정답이 보장되지는 않는다. 다국어 dense retrieval은 한국어 질의와 영어 문단의 의미를 연결할 수 있지만 숫자·약어·모델명 같은 표면 문자열을 놓칠 수 있다. 반대로 sparse retrieval은 정확한 용어에 강하지만 언어가 다른 의미적 표현에는 약하다. 긴 문맥은 핵심 근거를 묻히게 할 수 있고, 생성 모델은 검색 근거보다 파라미터 기억을 우선할 수 있다.

생성 단계에는 출력 언어 문제도 있다. 사용자가 한국어로 질문하고 문맥이 영어일 때 모델은 영어 구나 문장을 그대로 복사하거나 혼합 언어 답변을 만들 수 있다. 하지만 모든 영어 토큰을 억제해서도 안 된다. `BERT`, `RAG`, `BM25`, 데이터셋명, 수식, 인용처럼 학술 한국어에서 자연스럽게 유지되는 기술 용어는 보존해야 한다.

본 연구는 다음 세 요소에 범위를 한정한다.

- **HyDE:** 질의를 가상의 답변형 문서로 바꾸어 검색 표현을 확장한다.
- **CAD:** 같은 모델의 문맥 조건부 확률과 무문맥 확률을 대조해 문서 근거와 무관한 토큰을 억제한다.
- **SCD:** 목표 언어 토큰을 증폭하고 방해 언어 토큰을 감쇠하되 중립 기호와 기술 용어를 보존한다.

M-RAG 서비스는 논문 업로드, 검색, 출처 표시, A-F 질의 경로를 제공하지만 서비스 router 자체를 새로운 논문 알고리즘으로 주장하지 않는다. 논문의 핵심은 고정 backbone 위에서 세 요소의 효과를 분해하는 것이다.

> **핵심 주장:** 고정된 Paper-RAG 검색 backbone 위에서 HyDE × CAD × SCD 완전요인실험을 수행하고, 각 요소의 효과와 상호작용을 분석하여 한국어 질의-영어 논문 RAG의 전역 구성 정책을 제한적으로 도출한다. 질의 유형별 최적 정책은 후속 연구로 남긴다.

## 3. 배경

### 3.1 검색 증강 생성

RAG는 질의 `q`에 대해 문서 집합 `D`에서 문맥 `Cq`를 검색하고, 생성 모델이 질의와 문맥에 조건화된 답변 `y`를 생성한다 [1].

```text
y = LM(q, Cq)
```

검색이 관련 근거를 놓치면 생성 모델은 그 정보를 사용할 수 없고, 검색이 성공해도 모델이 근거를 무시하면 환각이 발생할 수 있다. 따라서 본 연구는 검색 측 제어와 디코딩 측 제어를 서로 다른 실험 축으로 다룬다.

### 3.2 Dense·Sparse·Hybrid Retrieval

BGE-M3는 한국어 질의와 영어 문단을 공유 벡터 공간에 표현하여 다국어 의미 검색을 지원한다 [3]. 하지만 벡터 압축은 숫자, 약어, 수식과 같은 정확 문자열을 약화할 수 있다. BM25는 어휘 중복을 이용하므로 정확 용어에 강하다 [4]. 본 시스템은 두 순위의 raw score를 직접 더하지 않고 dense 0.6, BM25 0.4 가중 Reciprocal Rank Fusion을 사용한다 [5].

```text
weighted_RRF(d) = 0.6 / (k + rank_dense(d))
                + 0.4 / (k + rank_BM25(d))
```

후보 문단은 `ms-marco-MiniLM-L-6-v2` CrossEncoder로 reranking한다 [6,7]. 이 검색·재정렬 과정은 주실험에서 고정된다.

### 3.3 HyDE

HyDE는 원 질의를 바로 embedding하는 대신 생성 모델이 만든 가상 답변형 문서를 embedding하여 관련 문서를 검색한다 [8]. 한국어 질의와 영어 학술 문장 사이의 표현 차이를 줄일 수 있지만, 생성된 가상 문서가 불필요한 개념을 추가하면 context precision이 낮아질 수 있다.

### 3.4 CAD

CAD는 문맥이 있을 때와 없을 때의 토큰 점수를 대조한다 [9]. 개념적으로 다음과 같이 표현된다.

```text
score_CAD = (1 + alpha) * logits_context - alpha * logits_no_context
```

문서가 없어도 모델이 쉽게 생성하는 토큰보다 실제 문맥에서 강해지는 토큰을 상대적으로 우선한다. 본 구현은 같은 생성 prefix를 사용해 무문맥 분기를 매 단계 다시 계산하는 정확성 우선 경로를 사용한다.

### 3.5 SCD와 언어 이탈

SCD는 다국어 RAG에서 출력이 근거 언어로 이동하는 language drift를 완화하는 training-free 디코딩 기법이다 [11]. 원본 v1은 방해 언어 토큰을 additive 방식으로 항상 감점했지만, 참조 방법의 목표 언어 boost, multiplicative scaling, cold-start warm-up을 구현하지 못했다. 교정된 `reference_scd`는 `alpha=1.1`, `beta=0.9`, `Tstart=5`를 적용한다. 목적은 모든 영문 기술어의 번역이 아니라 불필요한 영문 문장 이탈을 줄이는 것이다.

## 4. 관련 연구

Lewis 등 [1]은 검색 문서에 조건화된 생성의 기본 구조를 제시했다. RAG survey [2]는 검색, 증강, 생성 단계와 주요 설계 선택을 정리한다. BGE-M3 [3], BM25 [4], RRF [5], BERT reranking [6]은 본 연구의 고정 검색 backbone을 구성하는 근거다. MS MARCO [7]는 passage reranking 계열의 대표 학습·평가 자료로 관련성을 갖는다. 긴 문맥에서 중간 근거가 덜 사용되는 현상 [13]은 context ordering의 필요성을 뒷받침하고, BERGEN [14]은 RAG 비교 평가를 표준화하는 도구 방향을 보여준다.

HyDE [8]는 relevance label 없이 가상 문서를 사용해 dense retrieval을 개선하며, 국내 연구도 HyDE 기반 멀티홉 검색을 분석한다 [17]. CAD [9]와 contrastive decoding [10]은 생성 단계에서 분포를 대조하여 환각을 줄이는 방향을 제시한다. 국내 Contrastive CAD 연구 [18]도 관련 생성 제어를 다룬다.

Li 등 [11]은 다국어 RAG의 language drift를 분석하고 SCD를 제안한다. 본 논문은 이 방법을 한국어 질의-영어 논문 환경에서 요인으로 재현하며, 자체 신기법으로 주장하지 않는다. 생성 backbone으로 사용한 Mi:dm 2.0은 한국어 중심 이중언어 모델 연구 [15]와 연결된다. RAGAS [12]는 faithfulness, answer relevancy, context precision, context recall을 자동 평가하며, 국내 자동 평가 데이터셋 생성 연구 [16]도 한국어 RAG 평가의 필요성을 다룬다. 수정 SCD의 judge 예외로 사용한 `gpt-4o`는 공개 시스템 카드 [19]를 가진 모델이지만, 다국어 LLM judge는 언어에 따라 신뢰성이 달라질 수 있으므로 [20] 본 연구는 judge별 절대점수보다 같은 조건 안의 paired delta와 교차 judge 민감도를 중심으로 해석한다.

## 5. 문제 정의와 연구질문

한국어 질의 `q_ko`, 영어 논문 chunk 집합 `D_en`, 검색 문맥 `C`, 한국어 목표 답변 `y_ko`를 가정한다. 원하는 답변은 근거 충실성, 답변 관련성, 필요한 근거의 검색, 한국어 안정성을 만족해야 한다.

- **RQ1:** HyDE는 한국어 질의에 대한 영어 논문 근거 구성을 변화시키는가?
- **RQ2:** CAD는 고정 backbone에서 검색 근거에 대한 answer faithfulness를 변화시키는가?
- **RQ3:** 한국어 대상 SCD는 필요한 기술 용어를 보존하면서 language drift를 줄이는가?
- **RQ4:** CAD와 SCD를 함께 적용할 때 비가산적 상호작용이 나타나는가?
- **RQ5:** 측정된 전역 효과를 서비스 A-F 경로의 임시 기본값으로 어떻게 환원할 수 있는가?

가설은 방향을 유리하게 사후 설정하지 않는다. H1은 HyDE가 retrieval 지표를 변화시킨다는 것, H2는 CAD가 RAGAS faithfulness를 변화시킨다는 것, H3는 SCD가 직접 한국어 준수율을 변화시킨다는 것, H4는 두 디코딩 제어의 결합 효과가 비가산적일 수 있다는 것이다. 숫자 환각에 대한 별도 가설은 claim-level 숫자 주석을 수집하지 않았으므로 이번 실행에서 검정하지 않는다.

## 6. 시스템 개요

![M-RAG 시스템 개요](figures/system_overview.svg)

**그림 1.** M-RAG의 연구 계층과 서비스 계층. A-F router는 서비스 통합이며, HyDE × CAD × SCD 통제 실험이 논문의 연구 계층이다.

연구 계층은 `experiments/` 아래의 고정 Paper-RAG backbone과 완전요인실험으로 구성된다. 서비스 계층은 FastAPI backend와 React frontend로 논문 업로드, 텍스트 추출, chunking, vector indexing, 검색, reranking, 답변 생성, SSE streaming, 출처 표시, 후속 질문, 인용, 비교, 요약, 퀴즈 기능을 제공한다.

문서는 parsing과 section detection을 거쳐 chunk로 분할되고 embedding 및 BM25 색인에 저장된다. 사용자의 질의는 서비스 route를 선택한 후 hybrid retrieval, reranking, context construction을 거쳐 선택적 HyDE/CAD/SCD 제어와 함께 생성된다.

## 7. 고정 Paper-RAG Backbone

실험에서 변하지 않는 구성은 다음과 같다.

- Dense retrieval: BGE-M3
- Sparse retrieval: BM25
- Fusion: dense 0.6 / BM25 0.4 weighted RRF
- Reranking: `ms-marco-MiniLM-L-6-v2`
- Retrieval pool: 8
- Rerank top-n: 8
- Generation context: 5
- Generation model: `K-intelligence/Midm-2.0-Base-Instruct`
- Decoding: greedy, 최대 512 tokens

HyDE, CAD, SCD 외의 검색 방식, route별 로직, prompt 조건을 주실험에서 바꾸지 않는다. 이를 통해 관측 차이를 세 요인의 효과로 해석할 수 있는 내부 타당성을 확보한다.

## 8. 요인 분석 방법

![HyDE CAD SCD 완전요인 설계](figures/factorial_design.svg)

**그림 2.** 세 이진 요인의 8개 조합. 고정 입력과 backbone을 유지하면서 19개 질의에 대해 152개 답변을 생성했다.

HyDE는 retrieval query representation을 변경한다. CAD와 SCD는 retrieval 결과를 바꾸지 않고 생성 시 토큰 점수를 조절한다. 따라서 context recall처럼 검색에서 결정되는 지표가 CAD/SCD에 의해 크게 움직인다면 구현 또는 평가 오류를 의심해야 한다.

원본 SCD와 수정 SCD는 같은 결과로 합치지 않는다. 원본은 `penalty_additive v1`로 역사적 감사 산출물에 남기고, 수정 구현은 별도 `main-hyde-cad-scd-reference-scd` 실험 ID를 사용한다. 이는 실패 결과를 지우지 않으면서 최종 방법 주장을 올바른 구현에 연결하기 위한 정책이다.

## 9. 실험 설계

| 설정 | HyDE | CAD | SCD |
|---|---:|---:|---:|
| `hyde_off__no_decoder_control` | off | off | off |
| `hyde_off__cad_only` | off | on | off |
| `hyde_off__scd_only` | off | off | on |
| `hyde_off__cad_scd` | off | on | on |
| `hyde_on__no_decoder_control` | on | off | off |
| `hyde_on__cad_only` | on | on | off |
| `hyde_on__scd_only` | on | off | on |
| `hyde_on__cad_scd` | on | on | on |

질의는 tuning, main, query-type analysis, candidate final evaluation, service qualitative example로 역할을 분리한다. tuning 질의를 main 결과에 재사용하지 않고, 질문 수를 맞추기 위해 복제하거나 answerability를 확인하지 않은 template를 정량평가에 포함하지 않는다.

주실험의 `decoder_main_queries`는 19개이며 4개 영어 논문을 대상으로 한다. 질의 유형은 simple QA, section method/result/abstract, cross-lingual, decoder ablation, numeric/factual 질문을 포함하지만 유형별 표본이 작으므로 유형별 효과를 결과 주장으로 사용하지 않는다.

## 10. 평가 방법

RAGAS 0.2.15를 사용해 faithfulness, answer relevancy, context precision, context recall을 계산한다 [12]. 원본 Phase 8 행렬은 고정 NVIDIA NIM judge `meta/llama-3.3-70b-instruct`, temperature 0과 로컬 BGE-M3 embedding을 사용했다. 608개 셀 중 583개가 채점됐으며, 큰 multi-context payload의 endpoint timeout으로 발생한 25개 null 셀은 평균에서 제외한다. null을 0으로 바꾸지 않는다.

직접 한국어 비율은 중립 기호와 기술 용어를 고려한 문자 기반 지표다. 수정된 `reference_scd` 품질 평가는 NIM이 대규모에서 수렴하지 못한 뒤 명시적 예외로 `gpt-4o`를 사용했고, 대칭 후속 평가는 `gpt-4o`와 고정 `gpt-4.1-2025-04-14`를 함께 사용했다. judge가 다른 절대점수는 직접 비교하지 않는다.

숫자 환각률은 숫자, 단위, 비교 대상, 연결된 entity를 근거와 대조한 claim-level 주석이 있어야 한다. 이번 실행에는 그 주석이 없으므로 측정 결과가 없다. 질의 유형별 분석도 19개 질의를 여러 유형으로 나누면 셀이 너무 작아 결과표에서 제외한다. 두 항목은 0점이 아니라 미측정 범위다.

## 11. 주실험 결과

### 11.1 설정별 결과

| 설정 | Faithfulness | Answer relevancy | Context precision | Context recall | 한국어 비율 |
|---|---:|---:|---:|---:|---:|
| `hyde_off__no_decoder_control` | 0.871 | 0.825 | 0.891 | 0.947 | 0.594 |
| `hyde_off__cad_only` | 0.926 | 0.805 | 0.914 | 0.947 | 0.524 |
| `hyde_off__scd_only` | 0.848 | 0.829 | 0.853 | 0.947 | 0.602 |
| `hyde_off__cad_scd` | 0.919 | 0.784 | 0.877 | 0.947 | 0.525 |
| `hyde_on__no_decoder_control` | 0.867 | 0.866 | 0.844 | 0.947 | 0.607 |
| `hyde_on__cad_only` | 0.917 | 0.906 | 0.845 | 0.974 | 0.588 |
| `hyde_on__scd_only` | 0.916 | 0.892 | 0.810 | 1.000 | 0.582 |
| `hyde_on__cad_scd` | 0.925 | 0.858 | 0.867 | 0.974 | 0.549 |

### 11.2 주효과

| 효과 | 지표 | Paired delta (승/패) |
|---|---|---:|
| HyDE | answer relevancy | +0.070 (28/18) |
| HyDE | context recall | +0.026 (4/3) |
| HyDE | context precision | −0.056 (19/18) |
| CAD | faithfulness | +0.044 (25/17) |
| CAD | context recall | 0.000 (1/2) |
| SCD v1 | faithfulness | +0.009 (16/17) |
| SCD v1 | 직접 한국어 비율 | −0.014 (22/24) |

CAD는 가장 큰 단일 축 faithfulness 개선을 보였다. HyDE는 answer relevancy와 recall을 높이지만 precision을 낮췄다. decoder-side CAD가 context recall을 거의 움직이지 않고 retrieval-side HyDE가 이를 움직인다는 점은 요인과 지표의 구조적 관계에 부합한다. `hyde_on__cad_scd`는 최고 수준의 faithfulness 0.925를 보이지만 이것만으로 강한 CAD×SCD 상호작용을 주장할 수 없다.

### 11.3 원본 v1 언어 이탈

| 설정 | 언어 이탈률(한국어 비율 < 0.5) | 한국어 비율 |
|---|---:|---:|
| `hyde_off__no_decoder_control` | 0.26 | 0.594 |
| `hyde_off__cad_only` | 0.32 | 0.524 |
| `hyde_off__scd_only` | 0.26 | 0.602 |
| `hyde_off__cad_scd` | 0.37 | 0.525 |
| `hyde_on__no_decoder_control` | 0.26 | 0.607 |
| `hyde_on__cad_only` | 0.16 | 0.588 |
| `hyde_on__scd_only` | 0.26 | 0.582 |
| `hyde_on__cad_scd` | 0.37 | 0.549 |

v1 SCD-on 설정은 대응하는 SCD-off 설정보다 drift를 줄이지 못했다. 이 표는 교정된 `reference_scd` 결과로 소급 수정하지 않는다.

## 12. 수정된 reference_scd 결과

### 12.1 직접 한국어 준수율

교정 구현은 target-language multiplicative boost `alpha=1.1`, distractor multiplicative penalty `beta=0.9`, generated-token warm-up `Tstart=5`를 사용한다. 76개 대응쌍에서 SCD-on minus off 평균 한국어 비율은 `+0.2203`이었다. 68쌍이 개선, 3쌍이 악화, 5쌍이 동률이었다. 0.5 threshold 아래의 drift 답변 26개 중 15개를 구제했고, baseline 비율 0.7 이상인 20개 사례 중 사전 정의한 0.65 harm threshold 아래로 떨어진 사례는 없었다. HyDE-off의 byte-identical context 38쌍에서도 평균 `+0.2198`로 유지되었다.

그러나 3/76쌍은 악화되었고 SCD-on 12/76개는 여전히 0.5 미만이었다. 따라서 “언어 이탈 완전 제거”가 아니라 “직접 한국어 준수율의 큰 개선”으로 표현한다.

### 12.2 비대칭 `gpt-4o` 패널

첫 `gpt-4o` 패널은 152개 표본, 608/608 유효 셀을 제공한다. 이 프로토콜에서 SCD-on 차이는 faithfulness `−0.048`, answer relevancy `−0.057`, context precision `+0.030`, context recall `−0.066`이었다. 그러나 SCD-on 문맥만 한국어로 번역되었고 reference answer는 영어로 남았으며, HyDE-on 38쌍 중 25쌍은 검색 문맥도 달랐다. 따라서 이 값은 고립된 SCD 인과효과가 아니라 프로토콜별 민감도 결과다.

### 12.3 대칭 전처리와 교차 judge

후속 평가는 HyDE-off 76개 레코드, byte-identical context 38쌍을 고정했다. 질문, 답변, reference, nested context에 같은 점수 비의존 정규화 정책을 적용하고 영어·한국어 패널을 만들었다. 각 judge 패널은 304/304 유효 셀이며, 10,000회 deterministic query-clustered paired bootstrap을 사용했다.

`gpt-4o`에서 faithfulness는 영어 `+0.0071`, 95% CI `[−0.0596, +0.0714]`, 한국어 `−0.0283`, `[−0.1044, +0.0510]`로 모두 0을 포함했다. Answer relevancy는 영어 `−0.0910 [−0.1725, −0.0240]`, 한국어 `−0.0752 [−0.1501, −0.0138]`로 음의 구간이었다. 하지만 고정 `gpt-4.1-2025-04-14`에서는 영어 `−0.0327 [−0.0851, +0.0129]`, 한국어 `−0.0356 [−0.1149, +0.0315]`로 모두 0을 포함했고 faithfulness도 방향이 확정되지 않았다.

네 language-by-judge 패널의 answer relevancy 평균 방향은 음수지만 비영점 구간은 judge에 강건하지 않다. 정규화가 generation 이후 결과 변환이고, 두 judge가 같은 제공자이며, 한국어 답변 번역 노출이 SCD-off 23/38과 SCD-on 11/38로 다르고, 질의 cluster가 19개뿐이며, 사람 평가가 없기 때문에 SCD의 안정적인 품질 개선 또는 비용을 확정하지 않는다.

## 13. 논의

HyDE의 결과는 검색 확장이 recall과 answer relevancy를 높이는 동시에 precision을 낮출 수 있음을 보여준다. 따라서 모든 route에서 무조건 활성화하기보다 비교·요약처럼 여러 근거가 필요한 작업에 우선 적용하는 것이 합리적이다.

CAD의 faithfulness `+0.044`는 원본 행렬에서 가장 큰 단일 축 개선이다. 같은 생성 모델의 문맥/무문맥 분포를 대조한다는 설계 목적과 일치하며, retrieval 지표를 거의 움직이지 않았다는 점도 내부 타당성을 지지한다. 다만 표본이 작고 단일 원본 judge를 사용했으므로 모든 도메인에 일반화할 수 없다.

SCD 결과는 구현 충실도의 중요성을 보여준다. 단순 penalty-only v1은 목표 지표에서도 실패했지만 참조 방법을 복원한 구현은 직접 언어 준수율을 크게 개선했다. 동시에 자동 RAG 품질 평가는 judge와 정규화에 민감했다. 이는 “한국어를 더 많이 생성한다”와 “답변 품질이 좋아진다”가 서로 다른 주장임을 보여준다.

## 14. 서비스 통합

| 경로 | 서비스 목적 | 논문에서의 지위 | 임시 정책 |
|---|---|---|---|
| A | 단순 질의응답 | 서비스 기능 | CAD on, HyDE 선택, SCD 조건부 |
| B | 절 중심 질의응답 | 서비스 기능 | precision 우선 HyDE off, CAD on |
| C | 문서 비교 | 서비스 기능 | recall 우선 HyDE on, CAD on |
| D | 인용·서지 탐색 | 서비스 기능 | precision 우선 HyDE off, CAD on |
| E | 구조화 요약 | 서비스 기능 | HyDE on, CAD on |
| F | 퀴즈·플래시카드 | 서비스 기능 | HyDE 선택, CAD on |

이 표는 A-F route에서 직접 측정한 최적화 결과가 아니라 전역 요인효과를 서비스에 제한적으로 환원한 설계 지침이다. `reference_scd`는 언어 제어가 중요한 경우 사용할 수 있지만 작업별 품질 검증이 필요하다.

## 15. 한계와 향후 연구

첫째, 주실험은 4개 논문과 19개 질의에 한정되어 외적 타당성이 낮다. 독립적으로 작성한 100개 이상의 질의와 다양한 학술 분야가 필요하다. 둘째, 원본 행렬은 단일 고정 NIM judge를 사용했고 수정 SCD 후속 평가는 모두 OpenAI 제공자 judge를 사용했다. 독립 제공자 재현과 블라인드 사람 평가가 필요하다.

셋째, 숫자 환각률과 query-type 효과를 계산하지 않았다. 숫자별 근거 대조 주석과 충분한 유형별 표본을 사전에 설계해야 한다. 넷째, CAD는 매 토큰에서 무문맥 분기를 다시 계산하므로 비용이 증가한다. cache 최적화는 정확성 parity test 후 수행해야 한다. 다섯째, SCD token whitelist는 target tokenizer에 따라 subword 단위로 검증해야 한다.

여섯째, 서비스 계층은 배포 검증, 부하 시험, 관측성, 사용자 대상 robustness가 더 필요하다. 이는 요인분석의 결과와 별개인 제품 공학 과제다.

## 16. 결론

본 논문은 한국어 질의-영어 논문 RAG에서 HyDE, CAD, SCD를 고정된 Paper-RAG backbone 위의 세 독립 요인으로 분해하였다. 19개 질의와 8개 설정으로 152개 답변을 생성한 원본 행렬에서 CAD는 faithfulness를 `+0.044` 개선했고, HyDE는 answer relevancy와 recall을 높이는 대신 context precision을 낮췄다. 원본 `penalty_additive` v1 SCD는 null 결과였다.

교정된 `reference_scd`는 직접 한국어 준수율을 평균 `+0.2203` 개선했지만, 대칭 전처리와 교차 judge 평가는 RAG 품질의 judge-robust 비영점 효과를 확립하지 못했다. 따라서 최종 정책은 CAD를 기본 faithfulness 제어 후보로, HyDE를 route 목적에 따른 선택 요소로, SCD를 언어 제어를 위한 조건부 요소로 둔다.

이 연구의 핵심 가치는 실패한 구현을 숨기지 않고 교정 실험과 분리 보존한 점, 측정하지 않은 숫자 환각과 질의 유형 결과를 주장하지 않은 점, 언어 준수 개선과 답변 품질을 구분한 점에 있다. 더 큰 질의 집합, 독립 judge, 사람 평가를 통한 재현이 다음 단계다.

## 17. 참고문헌

[1] P. Lewis et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," NeurIPS 33, 2020.

[2] Y. Gao et al., "Retrieval-Augmented Generation for Large Language Models: A Survey," arXiv:2312.10997, 2023.

[3] J. Chen et al., "M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation," Findings of ACL 2024, pp. 2318-2335, doi:10.18653/v1/2024.findings-acl.137.

[4] S. E. Robertson et al., "Okapi at TREC-3," TREC-3, 1994.

[5] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, "Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods," SIGIR 2009, pp. 758-759, doi:10.1145/1571941.1572114.

[6] R. Nogueira and K. Cho, "Passage Re-ranking with BERT," arXiv:1901.04085, 2019.

[7] P. Bajaj et al., "MS MARCO: A Human Generated Machine Reading Comprehension Dataset," arXiv:1611.09268, 2016.

[8] L. Gao et al., "Precise Zero-Shot Dense Retrieval without Relevance Labels," ACL 2023, pp. 1762-1777, doi:10.18653/v1/2023.acl-long.99.

[9] W. Shi et al., "Trusting Your Evidence: Hallucinate Less with Context-aware Decoding," NAACL 2024, pp. 783-791, doi:10.18653/v1/2024.naacl-short.69.

[10] X. L. Li et al., "Contrastive Decoding: Open-ended Text Generation as Optimization," ACL 2023, pp. 12286-12312, doi:10.18653/v1/2023.acl-long.687.

[11] B. Li, Z. Xu, and R. Xie, "Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation," AAAI, vol. 40, no. 37, pp. 31519-31526, 2026, doi:10.1609/aaai.v40i37.40417.

[12] S. Es et al., "RAGAs: Automated Evaluation of Retrieval Augmented Generation," EACL 2024 System Demonstrations, pp. 150-158, doi:10.18653/v1/2024.eacl-demo.16.

[13] N. F. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts," TACL, vol. 12, pp. 157-173, 2024, doi:10.1162/tacl_a_00638.

[14] D. Rau et al., "BERGEN: A Benchmarking Library for Retrieval-Augmented Generation," Findings of EMNLP 2024, pp. 7640-7663, doi:10.18653/v1/2024.findings-emnlp.449.

[15] D. Shin et al., "Mi:dm 2.0 Korea-centric Bilingual Language Models," arXiv:2601.09066, 2026.

[16] 김범석, 양진홍, "RAG 시스템 성능 평가를 위한 자동 데이터 셋 생성 프레임워크 비교 분석 연구," 한국정보전자통신기술학회 논문지, 18(2), pp. 143-154, 2025, doi:10.17661/jkiiect.2025.18.2.143.

[17] 김예은 외, "HyDE 기반 멀티 홉 검색 기법을 활용한 검색 성능 향상 방안," 경영정보학연구, 27(2), pp. 127-148, 2025, doi:10.14329/isr.2025.27.2.127.

[18] 장규식 외, "Contrastive CAD: 대형 언어 모델의 환각 완화를 위한 대조적 Context-Aware Decoding," HCLT-KACL 2024 논문집, 2024.

[19] OpenAI, "GPT-4o System Card," arXiv:2410.21276, 2024.

[20] X. Fu and W. Liu, "How Reliable is Multilingual LLM-as-a-Judge?", Findings of EMNLP 2025, pp. 11040-11053, doi:10.18653/v1/2025.findings-emnlp.587.
