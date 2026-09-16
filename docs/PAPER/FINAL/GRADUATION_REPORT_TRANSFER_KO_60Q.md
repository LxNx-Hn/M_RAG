# 졸업자격실험보고서

## 한국어 질의 기반 영어 학술문서 RAG에서 HyDE·CAD·SCD 조합 실험

# 초록

검색 증강 생성(Retrieval-Augmented Generation, RAG)은 외부 문서를 검색하고 그 근거를 생성 모델의 문맥으로 제공한다. 한국어 사용자가 영어 학술문서를 질의하는 환경에서는 한국어 질의와 영어 문서 표현의 차이, 검색된 근거가 생성에 반영되는 정도, 영어 문맥으로 인한 출력 언어 이탈을 함께 다룰 필요가 있다. 본 연구는 이 문제와 관련된 기존 기법인 Hypothetical Document Embeddings(HyDE), Context-Aware Decoding(CAD), Soft Constrained Decoding(SCD)을 각각 검색 표현 확장, 문맥 기반 생성 제어, 한국어 출력 언어 제어의 실험 요인으로 둔다. 세 요인의 적용 여부를 독립적인 이진 요인으로 둔 2×2×2 조합 실험을 본 연구에서는 RAG-Cube로 지칭한다.

실험은 BGE-M3 dense retrieval, BM25 sparse retrieval, weighted Reciprocal Rank Fusion, CrossEncoder reranking, K-intelligence/Midm-2.0-Base-Instruct를 고정 Paper-RAG backbone으로 사용하였다. RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 네 영어 학술·기술 문서에 문서별 15개씩 총 60개의 한국어 질의-대상문서 쌍을 구성하고, 각 쌍에 여덟 configuration을 적용하여 480개 generation record를 저장하였다. HyDE의 주 비교는 CAD와 SCD가 OFF인 60 대응쌍이며, CAD의 주 비교는 동일 검색 문맥을 공유하는 대응쌍이다. SCD는 같은 query·HyDE·CAD 조건의 ON/OFF 240쌍을 사용한다.

HyDE 적용 시 answer relevancy 평균 변화는 +0.0805이고 95% 신뢰구간은 [+0.0110, +0.1514]였다. Faithfulness는 +0.0436, context precision은 -0.0343, context recall은 0.0000으로 지표별 방향이 달랐다. CAD의 동일 문맥 비교에서 faithfulness는 완결된 58쌍에서 +0.0288, answer relevancy는 60쌍에서 -0.0073이었다. SCD 적용은 240개 대응쌍에서 한국어 문자 비율을 평균 +0.2289 높였고, 95% 신뢰구간은 [+0.2051, +0.2532]였다. HyDE OFF 동일 문맥 120쌍에서도 변화는 +0.2182였다. 결과는 세 기법을 모두 적용할수록 모든 측정값이 상승하는 구조가 아니라, 검색 관련성·근거 충실도·출력 언어 유지라는 목적에 따라 유리한 configuration이 달라짐을 보여준다.

주요어: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, 한국어 질의, 영어 학술문서, 언어 이탈

# 1. 서론

## 1.1 연구배경 및 목적

대규모 언어모델은 자연어 질의에 대해 문장 형태의 응답을 생성할 수 있어 학술정보 탐색에도 활용된다. 그러나 학습된 지식만으로 특정 논문의 수치·방법·결론을 확인하는 경우, 답변이 실제 문서의 어느 근거에 연결되는지 추적하기 어렵다. RAG는 질의와 관련된 외부 문서를 검색하고 그 내용을 생성 문맥으로 제공함으로써 이 문제를 다룬다[1].

한국어로 질문하고 영어 학술문서를 대상으로 답하는 환경에서는 한 언어 안에서의 RAG와 다른 조건이 나타난다. 질의와 문서 사이에는 언어 및 학술적 표현 방식의 차이가 존재한다. 검색된 문맥이 있어도 생성 모델은 문맥의 내용을 충분히 반영하지 않을 수 있다. 또한 영어 근거 문맥은 답변을 영어 또는 혼합 언어로 이끌 수 있다. 본 연구의 목적은 이 세 문제와 연결되는 HyDE, CAD, SCD를 하나의 고정 backbone 안에서 독립 요인으로 비교하고, 각 기법의 적용 결과를 목적별 지표로 해석하는 데 있다.

HyDE는 질의를 가상의 문서 형태로 확장하여 검색 표현을 보완하는 방법이다[2]. CAD는 문맥이 있는 조건과 없는 조건의 token distribution을 대조해 생성에서 문맥의 영향을 강조하는 decoding 방법이다[3]. SCD는 목표 언어와 비목표 언어 토큰에 서로 다른 제약을 적용하여 다국어 RAG의 언어 이탈을 완화하는 방법이다[4]. 본 연구는 이 기법들을 새로 제안하는 것이 아니라, 한국어 질의·영어 학술문서 조건에서 각각의 역할과 조합별 결과를 적용·비교한다.

## 1.2 연구범위

연구 범위는 네 영어 학술·기술 문서와 그 문서를 대상으로 한 60개 한국어 질의-대상문서 쌍이다. 모든 질의는 하나의 대상 문서와 연결되며, 각 문서에는 15개 질의가 배정된다. 고정 backbone과 decoding 조건을 유지한 채 HyDE, CAD, SCD의 ON/OFF만 바꾸어 총 여덟 configuration을 실행한다. 최종 분석에는 저장된 480개 generation record, RAGAS 평가 결과, 한국어 문자 비율, generation duration, retrieved·reranked chunk ID 및 answer excerpt를 사용한다.

본 보고서는 Paper-RAG 실험 프로그램과 그 결과를 다룬다. 서비스 화면, API, 웹 route, 배포 기능은 연구 요인이나 실험 결과로 다루지 않는다. 품질 수치는 60-query 주 평가에서 사용한 단일 protocol에 한정하며, 별도 정규화·다중 judge 비교 panel은 본문 결과·그림·표·결론에 포함하지 않는다.

# 2. 이론적 배경

## 2.1 Retrieval-Augmented Generation

RAG는 질의에 관련된 문서 조각을 검색해 생성 모델의 입력 문맥으로 제공하는 구조이다. 문서 집합을 D, 질의를 q, 검색 문맥을 C, 답변을 y라 하면 과정은 Retrieve(q, D)로 C를 얻고, language model이 q와 C를 바탕으로 y를 생성하는 흐름으로 설명할 수 있다. 검색 단계의 결과와 생성 단계의 답변은 서로 관련되지만 같은 측정 대상은 아니다. 따라서 본 연구에서는 answer-level 지표와 context-level 지표를 분리해 기록한다.

## 2.2 Hybrid Retrieval과 재정렬

고정 backbone은 BGE-M3 기반 dense retrieval과 BM25 기반 sparse retrieval을 결합한다. Dense retrieval은 질의와 문서의 의미적 유사성을 표현하고, BM25는 전문용어·수치·약어 같은 표면적 일치를 보완한다[5][6]. 두 순위는 weighted Reciprocal Rank Fusion으로 결합한 뒤 CrossEncoder가 후보를 재정렬한다[7][8]. 저장 record에는 retrieval pool 8개, rerank top-N 8개, 최종 문맥 5개와 각 단계의 chunk ID가 남아 있어, 조건 간 검색 변화와 생성 결과를 분리해 확인할 수 있다.

## 2.3 Hypothetical Document Embeddings

HyDE는 질의에 대한 가상의 답변 또는 문서를 생성하고 그 표현을 검색에 이용한다[2]. 짧은 질의가 대상 문서의 학술적 표현과 차이가 클 때, 가상 문서는 검색 표현을 확장하는 매개가 될 수 있다. 본 연구에서는 HyDE ON/OFF에 따라 검색 결과가 바뀌는 end-to-end 효과를 answer relevancy와 retrieval record를 함께 사용해 분석한다. HyDE로 생성된 가상 문서는 근거 문서가 아니므로, 검색 변화가 모든 질의에서 같은 방향의 품질 변화를 만든다고 전제하지 않는다.

## 2.4 Context-Aware Decoding

CAD는 문맥이 포함된 생성 분포와 문맥이 없는 생성 분포를 대조해 문맥 조건의 영향을 반영한다[3]. 본 실험에서는 CAD alpha=0.5를 기록하고, CAD ON/OFF 비교 시 검색 문맥이 byte 수준으로 같은 대응쌍을 사용한다. 이 설계는 retrieval 자체의 변화와 decoding 차이를 구분하기 위한 것이다. CAD는 별도의 무문맥 branch를 계산하므로 generation duration도 함께 제시한다.

## 2.5 Soft Constrained Decoding과 언어 이탈

다국어 RAG에서 질의 언어와 근거 문서 언어가 다르면 답변의 언어가 문맥 언어 쪽으로 이동할 수 있다. SCD는 vocabulary를 목표 언어·비목표 언어·중립 토큰으로 구분하고, decoding 단계에서 token score에 제약을 적용한다[4]. 본 실험의 reference SCD는 alpha=1.1, beta=0.9, Tstart=5로 기록되어 있다. 한국어 문자 비율은 한글 문자 수를 한글 문자와 ASCII 영문자 수의 합으로 나눈 값이며, LLM judge와 독립적으로 계산한다.

## 2.6 RAG 평가

HyDE와 CAD의 품질 비교에는 faithfulness, answer relevancy, context precision, context recall을 사용한다[9]. 각 지표는 60개 대응 질의에서 ON-OFF 차이를 계산하고 paired bootstrap 95% 신뢰구간을 제시한다. Faithfulness의 일부 record는 원본 평가에서 빈 명제 집합으로 저장되어 있으므로, 해당 지표는 양쪽 점수가 존재하는 대응쌍만 사용하며 CAD 주 비교의 완결 표본 수는 58이다. SCD의 직접 평가는 동일 query·HyDE·CAD 조건의 ON/OFF 답변에서 계산한 한국어 문자 비율 차이를 사용한다.

# 3. 시스템 설계

## 3.1 연구 및 실험 요구사항

연구 요구사항은 질의와 대상 문서의 고정 연결, 여덟 조건의 완전한 generation record, 요인별 대응 비교, 저장 record에서의 재현 가능한 evidence, 표·그림·본문 수치의 동일성으로 구성한다. 표 3-1은 이 요구사항과 확인 기준을 정리한다.

[표 3-1] 연구 및 실험 요구사항 [스타일=표제목]

`tables_60q_csv/T3-1_Requirements.csv`

## 3.2 아키텍처 설계

실험 아키텍처는 한국어 질의, 영어 대상 문서, hybrid retrieval, reranking, 문맥 구성, 조건별 decoding, 저장, 평가·분석의 순서로 구성한다. 그림 1-1은 연구 환경의 입력과 출력 관계를, 그림 3-1은 RAG-Cube의 여덟 configuration을 제시한다. 그림 내부 번호는 없으며 실제 문서 편집 단계에서 캡션만 부여한다.

![연구 환경](figures_60q/fig1_1_research_setting.png)

[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경 [스타일=그림제목]

![RAG-Cube 2×2×2](figures_60q/fig3_1_rag_cube.png)

[그림 3-1] HyDE, CAD, SCD의 독립 이진 요인으로 구성한 RAG-Cube 8개 조건 [스타일=그림제목]

## 3.3 상세설계

각 configuration은 같은 query ID와 대상 문서에 대해 실행되며, `config_name`, 요인 사용 여부, retrieval·rerank 결과, contexts, 생성 답변, duration, 오류 상태를 저장한다. SCD가 ON이면 SCD mode와 alpha·beta·Tstart도 저장한다. 표 3-2와 표 3-3은 여덟 조건 및 요인별 적용 위치와 비교 단위를, 표 4-4는 record의 주요 필드를 제시한다.

[표 3-2] RAG-Cube 8개 조건 [스타일=표제목]

`tables_60q_csv/T3-2_RAG-Cube.csv`

[표 3-3] 실험 요인별 적용 위치와 비교 단위 [스타일=표제목]

`tables_60q_csv/T3-3_Factor_Position.csv`

# 4. 프로그램 구현

## 4.1 시스템 환경

실험 generation record는 K-intelligence/Midm-2.0-Base-Instruct, deterministic greedy decoding, max_new_tokens=512을 기록한다. 검색은 BGE-M3 dense retrieval과 BM25 sparse retrieval을 weighted RRF로 결합하고 CrossEncoder로 재정렬한다. 검색 후보와 재정렬 후보는 각 8개이며 최종 문맥은 5개다. 표 4-1과 표 4-2는 실제 저장 record에 남은 실행 환경 및 고정 backbone을 정리한다.

[표 4-1] 실험 실행 환경 [스타일=표제목]

`tables_60q_csv/T4-1_Environment.csv`

[표 4-2] 고정 Paper-RAG backbone [스타일=표제목]

`tables_60q_csv/T4-2_Backbone.csv`

## 4.2 시스템 구성

실행 경로는 질의 입력, 필요할 때의 HyDE 검색 표현 생성, dense·sparse 검색과 RRF, reranking, 상위 문맥 선택, CAD와 SCD의 선택적 decoding, generation record 저장 순서다. 모든 configuration은 같은 data split과 backbone을 공유한다. 이 구조는 검색 표현을 바꾸는 HyDE, 생성 시 문맥 영향을 조절하는 CAD, 출력 토큰 언어 성향을 조절하는 SCD의 위치를 분리해 보여준다.

![Paper-RAG pipeline](figures_60q/fig4_1_pipeline.png)

[그림 4-1] 고정 Paper-RAG backbone에서 RAG-Cube 요인을 적용하는 실행 흐름 [스타일=그림제목]

## 4.3 시스템 구현

generation record는 query·문서·configuration의 연결을 식별하고, 검색과 reranking의 chunk ID, 최종 contexts, 답변, 시간, 요인 파라미터를 함께 보존한다. 따라서 결과 수치를 다시 계산할 때 별도의 모델 호출 없이 저장 artifact를 읽을 수 있다. 조건별 평균과 중앙 generation time은 표 4-3에 기록한다. CAD 조건의 시간은 문맥과 무문맥 분기를 함께 계산하는 기록이므로, 품질 결과와 별도의 실행 특성으로 해석한다.

[표 4-3] 조건별 평균 생성시간 [스타일=표제목]

`tables_60q_csv/T4-3_Runtime.csv`

[표 4-4] generation record 주요 필드 [스타일=표제목]

`tables_60q_csv/T4-4_Record_Fields.csv`

# 5. 실험

## 5.1 실험 대상과 구성

최종 질의 집합은 RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report에 각각 15개 질문을 연결한 60개 질의-대상문서 쌍이다. 모든 질의는 valid answer span과 answerable 상태를 가지며, 중복 query ID나 중복 한국어 질문은 없다. 여덟 RAG-Cube configuration을 모두 적용하여 480개 generation record를 생성했다. 표 5-1은 문서별 분포를 제시하며, 부록 A에는 query ID·질문·대상 문서·질문 유형·source page·answer span 여부를 원자료에서 옮긴다.

[표 5-1] 4개 문서 × 15개 질의 = 60 [스타일=표제목]

`tables_60q_csv/T5-1_Dataset.csv`

## 5.2 평가 및 분석 방법

RAGAS 품질 지표는 저장된 480개 score row에서 읽는다. 전체 1,920 metric cell 가운데 1,915개가 값으로 저장되어 있고, faithfulness의 5개 빈 명제 집합은 결측 상태를 유지한다. HyDE의 주 비교는 CAD OFF·SCD OFF의 60 대응쌍이다. CAD의 주 비교는 같은 검색 문맥을 가진 대응쌍이며, faithfulness만 58개 완결쌍을 사용한다. SCD는 동일 query·HyDE·CAD에서 SCD OFF와 ON의 한국어 문자 비율을 비교한다.

평균 차이는 ON-OFF로 계산한다. 각 품질 지표와 SCD 문자 비율은 query 단위 재표집으로 95% bootstrap 신뢰구간을 산출한다. Win, loss, tie는 품질 지표에서 +0.01 초과, -0.01 미만, 그 사이로 나누어 기록한다. 이 기준은 평균 하나만으로 질의별 방향 차이를 감추지 않기 위한 보조 정보다.

## 5.3 RAG-Cube 조합별 결과

표 5-2는 여덟 configuration의 평균 품질과 Korean ratio를 보여준다. Faithfulness가 가장 높은 조건은 H1C1S0(0.8599), answer relevancy가 가장 높은 조건은 H1C0S0(0.7633), context precision이 가장 높은 조건은 H0C0S1(0.7634)이다. Context recall은 H0C0S0과 H1C0S0이 0.9333으로 같고, Korean ratio는 H1C0S1이 0.8072로 가장 높다. 지표별 최고 조건이 달라 하나의 configuration을 전역적으로 우선하는 방식으로 해석하지 않는다.

[표 5-2] 8개 configuration 평균 품질 [스타일=표제목]

`tables_60q_csv/T5-2_Config_Scores.csv`

![8개 configuration 품질 행렬](figures_60q/fig5_1_quality_matrix.png)

[그림 5-1] RAG-Cube 8개 조건의 평균 품질 지표. 셀 값은 저장된 RAGAS score의 configuration별 평균이다. [스타일=그림제목]

## 5.4 HyDE 결과 및 해석

HyDE의 주 비교에서 answer relevancy 평균 변화는 +0.0805이고 95% CI는 [+0.0110, +0.1514]다. 60개 대응 질의에서 win/loss/tie는 29/15/16이며, 이 값은 본 연구에서 가장 명확한 HyDE 관련 결과다. Faithfulness 평균 변화는 +0.0436이고 CI는 [-0.0262, +0.1153]이며 win/loss/tie는 24/21/15다. Context precision은 -0.0343, context recall은 0.0000이고 context recall은 52개 질의가 tie에 해당한다.

따라서 HyDE를 적용한 검색 표현 확장은 answer-level 관련성과 연결되는 양의 평균 변화를 보였으나, retrieval과 answer의 모든 측정값이 같은 방향으로 움직였다고 해석할 수는 없다. 검색 ID가 실제로 바뀐 저장 사례에서는 HyDE OFF 답변이 BIC 활용 정보를 찾지 못한 반면 HyDE ON 답변은 최적 cluster 수 선택을 설명했다. 이 사례는 평균의 원인을 일반화하는 증거가 아니라, retrieval change와 answer-level 결과를 함께 확인하는 provenance 사례다.

[표 5-3] HyDE primary 통제 비교 [스타일=표제목]

`tables_60q_csv/T5-3_HyDE.csv`

![HyDE CAD forest](figures_60q/fig5_2_primary_forest.png)

[그림 5-2] HyDE와 CAD의 통제 비교. 점은 ON-OFF 평균 차이, 선은 95% bootstrap 신뢰구간이다. [스타일=그림제목]

![HyDE 저장 사례](figures_60q/fig5_6_hyde_retrieval_pair.png)

[그림 5-3] HyDE OFF와 ON의 저장 응답 사례. query ID, configuration, 저장 점수와 answer excerpt는 artifact replay 원문에서 재현한다. [스타일=그림제목]

## 5.5 CAD 결과 및 해석

CAD의 주 비교는 검색 문맥을 동일하게 유지하고 decoding만 달리한 대응쌍이다. Faithfulness는 완결된 58쌍에서 평균 +0.0288, 95% CI [-0.0367, +0.0934], win/loss/tie 21/24/13이다. Answer relevancy는 60쌍에서 -0.0073, CI [-0.0855, +0.0719], win/loss/tie 19/32/9이다. Context precision은 -0.0092, context recall은 -0.0167이며, context recall은 59개 질의가 tie다.

이 결과는 CAD의 문맥 기반 logit 조절을 하나의 공통 품질 순위로 요약하기보다, 지표별 방향과 실제 응답을 함께 검토하게 한다. H1C1S0은 configuration 평균 faithfulness가 가장 높으며, HyDE ON strata에서는 faithfulness와 context precision이 양의 방향을 보이는 pattern이 있다. 반면 동일 문맥 사례에는 CAD ON에서 faithfulness가 커진 경우와 작은 경우가 모두 저장되어 있다. 이 변동은 CAD의 비교를 조건별 trade-off와 응답 근거의 관점에서 해석하게 한다.

[표 5-4] CAD primary 동일 문맥 비교 [스타일=표제목]

`tables_60q_csv/T5-4_CAD.csv`

![CAD 동일 문맥 사례](figures_60q/fig5_7_cad_pair.png)

[그림 5-4] 동일 문맥 CAD OFF·ON 저장 응답 사례. retrieval·rerank ID와 contexts의 동일성은 replay 원문에서 확인한다. [스타일=그림제목]

## 5.6 SCD 출력 언어 결과 및 해석

SCD의 직접 목적은 영어 근거 문맥에서 한국어 출력 언어를 유지하는 것이다. 240 ON/OFF 대응쌍의 한국어 문자 비율 평균 변화는 +0.2289이고 95% CI는 [+0.2051, +0.2532]다. +0.02를 초과한 증가는 219개, -0.02보다 작은 감소는 10개, 그 사이 동률은 11개다. HyDE OFF에서 contexts·retrieved ID·reranked ID가 같은 120쌍에서도 평균 변화는 +0.2182, 95% CI는 [+0.1880, +0.2487]이다.

네 HyDE·CAD strata에서 SCD ON-OFF 평균 변화는 각각 +0.2047, +0.2317, +0.2511, +0.2283이다. 따라서 SCD는 output-language control이라는 직접 목표에서 안정적인 방향의 차이를 보인다. 이 수치는 faithfulness나 answer relevancy 같은 일반 RAG 품질 지표의 변화를 뜻하지 않으며, 문자 비율이 문법성·근거 정확성·전문용어 선택을 모두 대체하는 지표도 아니다.

[표 5-5] SCD configuration별 language result [스타일=표제목]

`tables_60q_csv/T5-5_SCD_Config.csv`

[표 5-6] SCD matched-pair summary [스타일=표제목]

`tables_60q_csv/T5-6_SCD_Paired.csv`

![SCD language adherence](figures_60q/fig5_3_scd_language.png)

[그림 5-5] HyDE·CAD strata별 SCD 적용에 따른 한국어 문자 비율 변화. 오차막대는 95% bootstrap 신뢰구간이다. [스타일=그림제목]

![SCD 동일 문맥 사례](figures_60q/fig5_5_scd_language_pair.png)

[그림 5-6] 동일 문맥 SCD OFF·ON 저장 응답 사례. 원문 answer excerpt와 점수는 replay 원문에서 유래한다. [스타일=그림제목]

## 5.7 대표 입출력 및 요구사항별 실행 결과

정상 QA 사례는 저장된 query ID `ext_raptor_011`에서 H0C0S0 답변과 RAGAS score를 재현한다. HyDE 사례는 `ext_raptor_004`, SCD 언어 사례는 `ext_rag_010`, CAD 사례는 manifest의 selected query ID와 configuration을 사용한다. 그림의 answer text는 저장 record를 새로 작성하지 않고 excerpt와 `[이하 생략]` 표시만 사용한다. 전체 terminal-style replay 원문은 부록 B와 `evidence_60q_raw/`에 보존한다.

![정상 QA 저장 사례](figures_60q/fig5_4_normal_answer.png)

[그림 5-7] 정상 QA 저장 응답 사례. 그림의 답변과 score는 저장된 generation·evaluation artifact에서 재현한다. [스타일=그림제목]

## 5.8 종합 논의

세 요인은 서로 다른 단계와 목표를 가진다. HyDE는 검색 표현을 확장하며 주 비교에서 answer relevancy의 양의 평균 변화와 연결된다. CAD는 같은 검색 문맥에서 생성 분포를 조절하며, faithfulness는 양의 평균 방향을 보이나 query별 변화와 신뢰구간을 함께 해석해야 한다. SCD는 답변 언어 유지라는 직접 측정값에서 가장 일관된 차이를 보인다. 따라서 H/C/S를 모두 ON으로 두는 방식이 모든 목적에 최적인 조합이라는 결론을 사용하지 않는다.

## 5.9 연구의 한계

본 연구는 네 문서와 60개의 한국어 질의-대상문서 쌍에 범위를 둔다. 품질 지표는 LLM-as-a-judge 기반 RAGAS protocol에 의존하며, faithfulness의 빈 명제 집합 다섯 건은 결측값으로 보존한다. 한국어 문자 비율은 출력 언어 성향을 수치화하지만 자연스러움과 내용의 정확성을 단독으로 판정하지 않는다. 향후에는 독립 도메인·문서 형식·질의 작성자를 늘리고, 사람의 blind evaluation과 다양한 generator·tokenizer 조건을 추가해 결과의 외적 타당성을 검토할 수 있다.

# 6. 결론

본 연구는 한국어 질의 기반 영어 학술문서 RAG에서 HyDE, CAD, SCD를 독립 이진 요인으로 구성한 RAG-Cube 조합 실험을 수행했다. 4개 문서와 60개 질의-대상문서 쌍, 8개 configuration, 480개 저장 generation record를 사용했다. HyDE의 주 비교에서 answer relevancy는 +0.0805였고, CAD의 동일 문맥 비교에서 faithfulness는 58 완결쌍에서 +0.0288이었다. SCD는 240 대응쌍에서 한국어 문자 비율을 +0.2289 높였으며, HyDE OFF 동일 문맥 120쌍에서도 +0.2182의 변화를 보였다.

이 결과는 기법별 목표와 지표별 결과를 구분해 적용하는 근거를 제공한다. HyDE·CAD·SCD의 조합은 단일 성능 순위가 아니라 검색 관련성, 근거 충실도, 출력 언어 유지라는 서로 다른 목적에 대한 configuration별 선택 문제로 다룰 수 있다. 저장된 query, context, retrieval ID, answer, score와 artifact hash를 함께 제공함으로써 본문의 수치와 실제 사례를 다시 대조할 수 있도록 구성했다.

# 참고문헌

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, 2020.

[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023.

[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024.

[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of AAAI*, 2026.

[5] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” *Findings of ACL*, 2024.

[6] S. E. Robertson et al., “Okapi at TREC-3,” *Text REtrieval Conference*, 1994.

[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009.

[8] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019.

[9] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024.

# 부록 A. 60개 질의 목록

`generated/QUERY_60_AUDIT.md`는 60개의 query ID, 대상 문서, 질문 유형, 실제 한국어 질문을 보존한다. 한글 이전 시 이 목록에 source page와 GT/answer span 열을 source split에서 추가한다.

# 부록 B. 추가 실제 응답 증빙

`evidence_60q_raw/normal_qa.txt`, `hyde_retrieval_change.txt`, `cad_higher_faithfulness_delta.txt`, `cad_lower_faithfulness_delta.txt`, `language_rescue.txt`는 terminal-style replay 원문이다. 각 파일은 selection rule, query ID, source artifact, configuration, 저장 RAGAS score, contexts 및 retrieved ID의 동일성, 저장 answer excerpt를 포함한다.

# 부록 C. 추가 정량 결과

문서별 탐색 분석은 `tables_60q_csv/Appendix_Paper.csv`, 질문 유형별 탐색 분석은 `tables_60q_csv/Appendix_QueryType.csv`에 수록한다. strata별 상세 결과는 `generated/hyde_strata_deltas_60q.csv`와 `generated/cad_strata_deltas_60q.csv`, runtime 상세는 `generated/runtime_summary_60q.csv`를 사용한다.

# 부록 D. 재현성 및 artifact provenance

원본 generation, evaluation, query split, analysis artifact의 SHA-256은 `generated/EXPERIMENT_60_VALIDATION.md`와 `generated/evidence_manifest_60q.json`에 기록한다. 파생 표·그림은 `build_60q_derived_data.py`, `build_tables_60q.mjs`, `build_figures_60q.py`를 사용해 원자료에서 다시 만든다.

# 부록 E. 실행 절차

다음 명령은 모델 호출 없이 저장 artifact를 재분석하고 evidence를 재생한다.

```powershell
python -X utf8 docs/PAPER/FINAL/build_query_60_audit.py
python -X utf8 docs/PAPER/FINAL/build_60q_derived_data.py
python -X utf8 docs/PAPER/FINAL/build_figures_60q.py
python -X utf8 docs/PAPER/FINAL/evidence_replay_60q.py list
python -X utf8 docs/PAPER/FINAL/evidence_replay_60q.py show hyde_retrieval_change
```
