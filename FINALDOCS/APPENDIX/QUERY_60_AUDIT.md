# 60개 질의-대상문서 쌍 감사

이 보고서는 최종 RAG-Cube 실험의 60개 질의 메타데이터를 정리한다.
각 질의는 하나의 고정 대상 문서, 한국어 질문, 원문 페이지, 정답 근거 구간과 answerable 상태를 함께 가진다.

## 검증 결과

| 항목 | 값 |
|---|---:|
| 질의-대상문서 쌍 | 60 |
| 고유 query ID | 60 |
| 고유 한국어 질문 | 60 |
| 고정 대상 문서 | 4 |
| valid GT 및 answerable 질의 | 60 |
| 정답 근거 구간 보유 질의 | 60 |

## 대상 문서 분포

| 대상 문서 | 질의 수 |
|---|---:|
| Mi:dm K 2.5 Pro Technical Report | 15 |
| CAD | 15 |
| RAG Survey | 15 |
| RAPTOR | 15 |

## 질문 유형 분포

질문이 요구하는 답의 성격을 기준으로 네 범주를 적용한다.

| 유형 | 질의 수 |
|---|---:|
| 사실·정의 | 8 |
| 방법·절차 | 29 |
| 결과·비교 | 20 |
| 목적·기여 | 3 |

## 대상 문서 언어 메타데이터

| 메타데이터 값 | 질의 수 |
|---|---:|
| en | 60 |

## 전체 질의 목록

| query ID | 대상 문서 | 유형 | 한국어 질문 |
|---|---|---|---|
| ext_cad_001 | CAD | 사실·정의 | 언어 모델이 생성 시 활용하는 prior knowledge와 context knowledge는 각각 어디에서 오는 정보입니까? |
| ext_cad_002 | CAD | 방법·절차 | CAD의 요약 실험에는 어떤 데이터셋과 평가 지표가 사용되었습니까? |
| ext_cad_003 | CAD | 방법·절차 | CAD의 지식 충돌 실험에는 어떤 두 데이터셋이 사용되었고 각각 무엇을 평가합니까? |
| ext_cad_004 | CAD | 방법·절차 | NQ-Swap 데이터셋은 기존 Natural Questions의 정답과 문서를 어떤 방식으로 변형해 만들어집니까? |
| ext_cad_005 | CAD | 방법·절차 | CAD 실험에서 요약 과제와 지식 충돌 과제에 사용한 α 값은 각각 얼마이며, 지식 충돌 과제에서 더 큰 값을 사용한 이유는 무엇입니까? |
| ext_cad_006 | CAD | 방법·절차 | CAD 논문의 베이스라인 디코딩은 요약 과제와 지식 충돌 과제에서 각각 어떤 샘플링 전략을 사용합니까? |
| ext_cad_007 | CAD | 방법·절차 | CAD가 실험에서 적용된 사전학습 및 instruction-finetuned 언어 모델 계열은 무엇입니까? |
| ext_cad_008 | CAD | 결과·비교 | 지식 충돌 과제에서 모델 크기가 커질수록 CAD의 성능 향상 폭은 어떤 경향을 보였습니까? |
| ext_cad_009 | CAD | 결과·비교 | LLaMA-30B에 CAD를 적용했을 때 XSUM에서 ROUGE-L, factKB, BERT-P 점수는 regular decoding과 비교해 어떻게 달라졌습니까? |
| ext_cad_010 | CAD | 사실·정의 | 외부 컨텍스트가 생성 토큰과 조건부 독립이라면 α가 0이 아니어도 CAD의 출력 분포에는 어떤 영향이 있습니까? |
| ext_cad_011 | CAD | 사실·정의 | CAD는 특정 instruction-finetuned 언어 모델에만 제한됩니까, 아니면 어떤 언어 모델에도 적용 가능한 디코딩 전략입니까? |
| ext_midm_001 | Mi:dm K 2.5 Pro Technical Report | 방법·절차 | Mi:dm K 2.5 Pro의 학습 데이터는 어떤 세 가지 경로를 통해 확보됩니까? |
| ext_midm_002 | Mi:dm K 2.5 Pro Technical Report | 방법·절차 | Mi:dm K 2.5 Pro는 한국어 중심 학습을 유지하기 위해 다국어 데이터를 한국어 코퍼스 대비 어느 정도 비율로 제한하며, 그 이유는 무엇입니까? |
| ext_midm_003 | Mi:dm K 2.5 Pro Technical Report | 결과·비교 | 응답 스타일 재작성 후 평균 응답 길이는 몇 % 증가했고, bullet_count=0인 응답의 비율은 어떻게 변했습니까? |
| ext_midm_004 | Mi:dm K 2.5 Pro Technical Report | 방법·절차 | Mi:dm K 2.5 Pro의 한국어 멀티턴 대화 데이터는 어떤 세 가지 차원을 기준으로 고품질 대화를 설계합니까? |
| ext_midm_005 | Mi:dm K 2.5 Pro Technical Report | 방법·절차 | Fusion SFT 단계에서 non-reasoning 데이터의 비중을 높인 목적은 무엇이며, 어떤 유형의 과제를 특히 보강합니까? |
| ext_midm_006 | Mi:dm K 2.5 Pro Technical Report | 결과·비교 | Fully asynchronous GSPO 학습은 synchronous 방식과 비교해 step time과 token throughput을 각각 어느 정도 개선했습니까? |
| ext_midm_007 | Mi:dm K 2.5 Pro Technical Report | 결과·비교 | LLM-as-a-Judge 기반 reward signal은 사람의 평가와 어느 정도의 일치율을 보였습니까? |
| ext_midm_008 | Mi:dm K 2.5 Pro Technical Report | 결과·비교 | Reasoning-enabled 평가에서 Mi:dm K 2.5 Pro가 HumanEval+와 τ²-Bench Telecom에서 기록한 점수는 각각 얼마입니까? |
| ext_midm_009 | Mi:dm K 2.5 Pro Technical Report | 결과·비교 | 한국어 red-teaming 평가에서 Mi:dm K 2.5 Pro의 Attack Success Rate는 얼마였으며 비교 모델들 가운데 어떤 수준이었습니까? |
| ext_rag_001 | RAG Survey | 방법·절차 | Advanced RAG의 pre-retrieval 단계는 인덱스와 사용자 질의를 각각 어떤 방향으로 최적화합니까? |
| ext_rag_002 | RAG Survey | 방법·절차 | Advanced RAG의 post-retrieval 단계에서 사용되는 두 가지 핵심 방법은 무엇입니까? |
| ext_rag_003 | RAG Survey | 방법·절차 | RAG에서 큰 청크와 작은 청크를 사용할 때 각각 어떤 장단점이 발생합니까? |
| ext_rag_004 | RAG Survey | 방법·절차 | 문서 청크에 타임스탬프 같은 메타데이터를 부여하면 time-aware RAG는 최신 정보를 어떻게 우선할 수 있습니까? |
| ext_rag_005 | RAG Survey | 방법·절차 | Reverse HyDE는 문서로부터 가상의 질문을 생성해 원래 질문과 답변 사이의 의미적 간극을 어떻게 줄입니까? |
| ext_rag_006 | RAG Survey | 방법·절차 | Multi-Query와 Sub-Query 방식은 원래 질의를 확장하거나 분해하는 방식에서 어떻게 다릅니까? |
| ext_rag_007 | RAG Survey | 방법·절차 | Iterative Retrieval, Recursive Retrieval, Adaptive Retrieval은 검색을 반복하거나 중단하는 방식에서 각각 어떻게 구분됩니까? |
| ext_rag_008 | RAG Survey | 방법·절차 | RAG 평가에서 요구되는 네 가지 핵심 능력은 무엇입니까? |
| ext_rag_009 | RAG Survey | 사실·정의 | RAG 평가에서 Negative Rejection은 어떤 능력을 측정합니까? |
| ext_rag_010 | RAG Survey | 결과·비교 | RAG와 파인튜닝을 비교할 때 지식 업데이트의 동적 특성과 해석 가능성 측면에서 RAG가 갖는 특징은 무엇입니까? |
| ext_raptor_001 | RAPTOR | 방법·절차 | RAPTOR는 초기 문서를 몇 토큰 길이의 청크로 나누며, 문장이 청크 경계를 넘을 때 어떻게 처리합니까? |
| ext_raptor_002 | RAPTOR | 방법·절차 | RAPTOR의 leaf node를 만들 때 텍스트 임베딩에 사용한 모델은 무엇입니까? |
| ext_raptor_003 | RAPTOR | 방법·절차 | RAPTOR의 GMM 클러스터링 전에 UMAP을 사용하는 이유는 무엇입니까? |
| ext_raptor_004 | RAPTOR | 방법·절차 | RAPTOR의 클러스터링 과정에서 Bayesian Information Criterion(BIC)은 어떤 결정을 내리는 데 사용됩니까? |
| ext_raptor_005 | RAPTOR | 방법·절차 | RAPTOR에서 클러스터별 요약을 생성하는 데 사용한 언어 모델은 무엇입니까? |
| ext_raptor_006 | RAPTOR | 결과·비교 | RAPTOR의 트리 구축 비용은 문서 길이가 증가할 때 build time과 token expenditure 측면에서 어떻게 확장됩니까? |
| ext_raptor_007 | RAPTOR | 방법·절차 | QASPER 데이터셋은 몇 개의 질문과 NLP 논문으로 구성되며, 논문에서는 어떤 지표로 성능을 평가합니까? |
| ext_raptor_008 | RAPTOR | 사실·정의 | QuALITY-HARD는 일반 QuALITY 질문 중 어떤 기준을 만족하는 질문들로 구성됩니까? |
| ext_raptor_009 | RAPTOR | 결과·비교 | QASPER에서 RAPTOR의 F1 Match 점수는 GPT-3, GPT-4, UnifiedQA를 사용할 때 각각 얼마였습니까? |
| ext_raptor_010 | RAPTOR | 결과·비교 | QuALITY의 한 스토리에서 RAPTOR가 전체 3개 계층을 검색했을 때의 성능은 leaf node 한 계층만 검색했을 때와 어떻게 달라졌습니까? |
| ext_raptor_011 | RAPTOR | 결과·비교 | Cinderella 사례의 정성 분석에서 RAPTOR의 tree-based retrieval이 DPR보다 주제형·멀티홉 질문에 유리했던 이유는 무엇입니까? |
| track1_0009 | RAG Survey | 목적·기여 | RAG가 LLM에서 사실적으로 부정확한 콘텐츠 생성을 줄이는 데 어떻게 기여합니까? |
| track1_0010 | RAG Survey | 방법·절차 | RAG의 Naive RAG 방법론은 어떤 과정으로 구성되어 있습니까? |
| track1_0012 | RAG Survey | 목적·기여 | RAG 시스템은 지식 집약적인 작업에서 어떻게 유리합니까? |
| track1_0015 | RAG Survey | 사실·정의 | RAG 프로세스에서 핵심적인 역할을 하는 세 가지 구성 기술은 무엇인가요? |
| track1_0016 | RAG Survey | 방법·절차 | RAG 방법론의 평가 방법은 어떻게 요약되어 있습니까? |
| track1_0019 | CAD | 결과·비교 | LLaMA-30B 모델에 CAD를 적용했을 때 CNN-DM 데이터셋에서 어떤 성과가 있었나요? |
| track1_0021 | CAD | 결과·비교 | CAD는 어떻게 잘못된 정보 생성을 줄이나요? |
| track1_0023 | CAD | 결과·비교 | CAD는 언어 모델이 생성하는 요약문의 사실적 정확성을 향상시키나요? |
| track1_0024 | CAD | 결과·비교 | CAD를 적용하지 않은 경우와 비교했을 때, knowledge conflict QA 데이터셋에서 LLaMA-30B의 성능은 어떻게 변화하나요? |
| track1_0025 | RAPTOR | 결과·비교 | RAPTOR 모델이 QuALITY 벤치마크에서 기존 성능을 얼마나 개선했나요? |
| track1_0026 | RAPTOR | 방법·절차 | RAPTOR의 트리 구조는 텍스트 클러스터링을 통해 어떻게 구축되나요? |
| track1_0027 | RAPTOR | 결과·비교 | RAPTOR가 여러 QA 작업에서 달성한 결과는 무엇인가요? |
| track1_0032 | RAPTOR | 결과·비교 | RAPTOR의 계층에서 검색된 노드가 어느 계층에서 오는지에 대한 연구 결과는 무엇인가요? |
| track1_0033 | Mi:dm K 2.5 Pro Technical Report | 사실·정의 | Mi:dm K 2.5 Pro 모델의 파라미터 수는 몇 개입니까? |
| track1_0034 | Mi:dm K 2.5 Pro Technical Report | 방법·절차 | Mi:dm K 2.5 Pro의 방법론에서 AST 분석은 어떤 목적으로 사용됩니까? |
| track1_0035 | Mi:dm K 2.5 Pro Technical Report | 결과·비교 | Mi:dm K 2.5 Pro 모델은 어떤 한국어 벤치마크에서 최첨단 결과를 달성했습니까? |
| track1_0036 | Mi:dm K 2.5 Pro Technical Report | 목적·기여 | Mi:dm K 2.5 Pro가 해결하려는 주요 문제는 무엇입니까? |
| track1_0037 | Mi:dm K 2.5 Pro Technical Report | 사실·정의 | Mi:dm K 2.5 Pro 모델의 컨텍스트 윈도우(context window) 길이는 얼마인가요? |
| track1_0040 | Mi:dm K 2.5 Pro Technical Report | 방법·절차 | Mi:dm K 2.5 Pro의 사후 훈련 파이프라인에서 모델 병합은 어떤 역할을 합니까? |

## 입력 근거

- `experiments/data/query_splits/decoder_main_queries.json`
- `experiments/data/query_splits/extended_validation_questions.json`
