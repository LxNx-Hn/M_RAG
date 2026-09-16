# 졸업자격실험보고서

## 한국어 질의 기반 영어 학술문서 RAG에서 HyDE·CAD·SCD 조합 실험

# 초록

검색 증강 생성(Retrieval-Augmented Generation, RAG)은 외부 문서를 검색하고 그 근거를 생성 모델의 문맥으로 제공한다. 한국어 사용자가 영어 학술문서를 질의하는 환경에서는 한국어 질의와 영어 문서 표현의 차이, 검색된 근거가 생성에 반영되는 정도, 영어 문맥으로 인한 출력 언어 이탈을 함께 다룰 필요가 있다. 본 연구는 이 문제와 관련된 기존 기법인 Hypothetical Document Embeddings(HyDE), Context-Aware Decoding(CAD), Soft Constrained Decoding(SCD)을 각각 검색 표현 확장, 문맥 기반 생성 제어, 한국어 출력 언어 제어의 실험 요인으로 둔다. 세 요인의 적용 여부를 독립적인 이진 요인으로 둔 2×2×2 조합 실험을 본 연구에서는 RAG-Cube로 지칭한다.

실험은 BGE-M3 dense retrieval, BM25 sparse retrieval, weighted Reciprocal Rank Fusion, CrossEncoder reranking, K-intelligence/Midm-2.0-Base-Instruct를 고정 Paper-RAG backbone으로 사용하였다. RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 네 영어 학술·기술 문서에 문서별 15개씩 총 60개의 한국어 질의-대상문서 쌍을 구성하고, 각 쌍에 여덟 configuration을 적용하여 480개 generation record를 저장하였다. HyDE의 주 비교는 CAD와 SCD가 OFF인 60 대응쌍이며, CAD의 주 비교는 동일 검색 문맥을 공유하는 대응쌍이다. SCD는 같은 query·HyDE·CAD 조건의 ON/OFF 240쌍을 사용한다.

HyDE 적용 시 answer relevancy 평균 변화는 +0.0805이고 95% 신뢰구간은 [+0.0110, +0.1514]였다. Faithfulness는 +0.0436, context precision은 -0.0343, context recall은 0.0000으로 지표별 방향이 달랐다. CAD의 동일 문맥 비교에서 faithfulness는 완결된 58쌍에서 +0.0288, answer relevancy는 60쌍에서 -0.0073이었다. SCD 적용은 240개 대응쌍에서 한국어 문자 비율을 평균 +0.2289 높였고, 95% 신뢰구간은 [+0.2051, +0.2532]였다. HyDE OFF 동일 문맥 120쌍에서도 변화는 +0.2182였다. 결과는 세 기법을 모두 적용할수록 모든 측정값이 상승하는 구조가 아니라, 검색 관련성·근거 충실도·출력 언어 유지라는 목적에 따라 유리한 configuration이 달라짐을 보여준다.

주요어: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, 한국어 질의, 영어 학술문서, 언어 이탈

# 1. 서론 [스타일=장제목]

## 1.1 연구배경 및 목적 [스타일=절제목]

대규모 언어모델은 자연어 질의에 대해 문장 형태의 응답을 생성할 수 있어 학술정보 탐색에도 활용된다. 그러나 학습된 지식만으로 특정 논문의 수치·방법·결론을 확인하는 경우, 답변이 실제 문서의 어느 근거에 연결되는지 추적하기 어렵다. RAG는 질의와 관련된 외부 문서를 검색하고 그 내용을 생성 문맥으로 제공함으로써 이 문제를 다룬다[1].

한국어로 질문하고 영어 학술문서를 대상으로 답하는 환경에서는 한 언어 안에서의 RAG와 다른 조건이 나타난다. 질의와 문서 사이에는 언어 및 학술적 표현 방식의 차이가 존재한다. 검색된 문맥이 있어도 생성 모델은 문맥의 내용을 충분히 반영하지 않을 수 있다. 또한 영어 근거 문맥은 답변을 영어 또는 혼합 언어로 이끌 수 있다. 본 연구의 목적은 이 세 문제와 연결되는 HyDE, CAD, SCD를 하나의 고정 backbone 안에서 독립 요인으로 비교하고, 각 기법의 적용 결과를 목적별 지표로 해석하는 데 있다.

HyDE는 질의를 가상의 문서 형태로 확장하여 검색 표현을 보완하는 방법이다[2]. CAD는 문맥이 있는 조건과 없는 조건의 token distribution을 대조해 생성에서 문맥의 영향을 강조하는 decoding 방법이다[3]. SCD는 목표 언어와 비목표 언어 토큰에 서로 다른 제약을 적용하여 다국어 RAG의 언어 이탈을 완화하는 방법이다[4]. 본 연구는 이 기법들을 새로 제안하는 것이 아니라, 한국어 질의·영어 학술문서 조건에서 각각의 역할과 조합별 결과를 적용·비교한다.

[스타일=본문]

학술문서 질의응답에서 사용자가 실제로 필요로 하는 것은 문서의 제목이나 널리 알려진 요약이 아니라, 특정 방법의 정의, 실험 설정의 조건, 표에 기록된 수치, 저자가 제시한 한계처럼 문서 내부의 세부 근거에 연결된 답변인 경우가 많다. 생성 모델만을 사용하면 문장은 자연스럽더라도 해당 문서에 없는 일반 지식이 섞일 수 있으며, 답변을 확인하는 사람은 어느 문단이 근거인지 다시 찾아야 한다. RAG는 이 문제를 검색과 생성의 연결로 다루지만, 검색 결과가 존재한다는 사실만으로 문서 기반 답변이 보장되지는 않는다. 따라서 본 연구는 검색된 근거의 선택과 그것을 사용하는 생성 과정, 그리고 답변 언어의 유지라는 세 지점을 분리해 본다.

[스타일=본문]

한국어 질의와 영어 학술문서의 조합은 같은 언어 안에서의 문서 검색보다 더 복합적인 조건을 만든다. 사용자는 한국어로 개념을 서술하지만, 대상 논문은 영어의 전문 용어와 문장 구조로 그 개념을 표현한다. 예를 들어 방법의 기능을 묻는 한국어 질문은 영어 논문에서 model selection, conditioning, decoding, reranking과 같이 서로 다른 표현으로 나타날 수 있다. 표면 단어의 일치가 약한 상황에서는 관련 근거를 찾는 검색 표현 자체가 결과에 영향을 준다. 반대로 해당 근거가 검색되더라도, 영어 문맥이 길게 제공된 환경에서 생성 모델이 질문의 한국어 형식과 답변 언어를 유지하는지는 별개의 문제다.

[스타일=본문]

이 연구는 세 기법을 단일한 성능 향상 장치로 취급하지 않는다. HyDE는 질의와 문서 사이의 표현 간격을 줄이기 위한 retrieval-side intervention이고, CAD는 이미 선택된 문맥이 token 선택에 미치는 영향을 강조하는 generation-side intervention이며, SCD는 목표 언어 토큰을 선호하도록 하는 output-language intervention이다. 적용 위치와 직접 목표가 다르므로 세 방법을 같은 하나의 수치로 서열화하면 각 방법이 해결하려는 문제를 흐릴 수 있다. 이에 따라 본문에서는 HyDE의 경우 answer relevancy와 검색 변경 사례를, CAD의 경우 동일 문맥의 생성 차이와 실행 시간, SCD의 경우 한국어 문자 비율과 동일 입력 대응쌍을 중심으로 해석한다.

[스타일=본문]

RAG-Cube는 HyDE, CAD, SCD의 사용 여부를 각각 H, C, S로 표시한 2×2×2 조합이다. H0C0S0은 세 요인을 모두 끈 기준 configuration이고, H1C1S1은 세 요인을 모두 적용한 configuration이다. 이 표기는 개별 기법을 설명하기 위한 약칭이면서, 어떤 평균과 사례가 어느 조건에서 나온 것인지 추적하는 장치이기도 하다. 같은 query ID가 여덟 configuration에서 반복되므로, 평균만이 아니라 동일 질문의 검색 ID·문맥·답변·점수를 대조할 수 있다. 연구의 분석 단위는 단순한 전체 평균이 아니라 이 대응 관계를 가진 질의-대상문서 쌍이다.

[스타일=본문]

최종 실험은 네 개의 영어 학술·기술 문서를 대상으로 문서별 15개씩 구성한 60개 한국어 질의-대상문서 쌍을 사용한다. 60개 질의에 여덟 configuration을 모두 적용하여 480개 generation record를 저장했고, 각 record에는 조건명, retrieval과 rerank의 chunk ID, 최종 문맥, 생성 답변, 실행 시간, decoder metadata를 남겼다. 이 규모는 이전의 소규모 초안을 되풀이하는 것이 아니라, 동일한 고정 backbone 아래에서 질의 집합을 60개까지 확장하여 통제 대비와 configuration별 패턴을 다시 계산한 결과다. 본문 수치와 그림은 이 480개 저장 기록과 두 merged evaluation artifact에서 파생한다.

[스타일=본문]

연구 질문은 다음과 같이 정리한다. 첫째, CAD와 SCD를 끈 조건에서 HyDE를 적용할 때 answer relevancy와 나머지 RAGAS 지표는 어떻게 변하는가. 둘째, 검색 문맥을 동일하게 유지한 조건에서 CAD는 생성 결과와 실행 시간에 어떤 차이를 만드는가. 셋째, 같은 query·HyDE·CAD 조건에서 SCD는 한국어 출력 유지라는 직접 목표에 어떤 변화를 만드는가. 넷째, 여덟 configuration의 평균을 나란히 놓았을 때 지표별 최고 조건과 trade-off는 어떻게 달라지는가. 이 질문은 새로운 알고리즘의 보편적 우월성을 주장하기보다, 한국어 질의 기반 영어 문서 RAG라는 적용 환경에서 기존 방법들의 역할을 분해해 해석하는 데 목적이 있다.

[스타일=본문]

논문의 기여는 세 가지로 정리할 수 있다. 첫째, 검색 표현·문맥 기반 생성·출력 언어 제어에 대응하는 세 기존 기법을 하나의 고정 backbone에서 독립 이진 요인으로 기록한다. 둘째, 60개 질의와 480개 저장 답변을 사용해 통제 비교, configuration 평균, 실제 입출력 사례를 서로 보완하는 증거로 제시한다. 셋째, 본문에 사용한 수치뿐 아니라 query ID, configuration, 저장 점수, chunk ID, answer excerpt를 read-only evidence replay UI에서 다시 표시하여 결과 해석의 근거를 확인할 수 있게 한다. 이 UI는 모델을 새로 실행하거나 답변을 다시 만들지 않고 보존된 artifact만 읽는다.

## 1.2 연구범위 [스타일=절제목]

연구 범위는 네 영어 학술·기술 문서와 그 문서를 대상으로 한 60개 한국어 질의-대상문서 쌍이다. 모든 질의는 하나의 대상 문서와 연결되며, 각 문서에는 15개 질의가 배정된다. 고정 backbone과 decoding 조건을 유지한 채 HyDE, CAD, SCD의 ON/OFF만 바꾸어 총 여덟 configuration을 실행한다. 최종 분석에는 저장된 480개 generation record, RAGAS 평가 결과, 한국어 문자 비율, generation duration, retrieved·reranked chunk ID 및 answer excerpt를 사용한다.

본 보고서는 Paper-RAG 실험 프로그램과 그 결과를 다룬다. 서비스 화면, API, 웹 route, 배포 기능은 연구 요인이나 실험 결과로 다루지 않는다. 품질 수치는 60-query 주 평가에서 사용한 단일 protocol에 한정하며, 별도 정규화·다중 judge 비교 panel은 본문 결과·그림·표·결론에 포함하지 않는다.

[스타일=본문]

연구 범위를 대상 문서별 질의-문서 쌍으로 고정한 이유는 검색 결과의 해석 가능성을 확보하기 위해서다. 각 질의는 하나의 논문 또는 기술 보고서와 연결되고, 검색은 그 대상 문서의 chunk 집합에서 수행된다. 따라서 한 질문에 대해 문서 집합 전체를 임의로 넓히는 open-domain 검색의 성능을 측정하는 것이 아니다. 본 실험은 사용자가 확인하려는 학술문서가 이미 정해진 상황에서, 한국어 질문과 영어 근거 사이의 표현 차이 및 생성 조건이 어떤 결과를 만드는지 분석하는 application study다.

[스타일=본문]

고정 backbone은 dense retrieval, sparse retrieval, fusion, reranking, 다섯 개 생성 문맥, 생성 모델과 greedy decoding을 포함한다. 이 구성 자체의 최적성을 새로 탐색하지 않으며, 각 configuration에서 backbone을 바꾸지 않는다. HyDE ON은 dense retrieval의 입력 표현을 바꾸고, CAD ON과 SCD ON은 생성 단계에 적용된다. 이 경계는 결과를 해석할 때 중요하다. 예를 들어 HyDE의 ON/OFF 차이는 retrieval-side pipeline 전체의 end-to-end 차이이며, CAD의 주 비교는 동일한 retrieval·rerank·contexts가 기록된 경우에 한해 generation-side 차이로 읽는다.

[스타일=본문]

품질 평가는 저장된 RAGAS score에서 faithfulness, answer relevancy, context precision, context recall을 읽어 수행한다. 네 지표는 서로 다른 질문에 답한다. 답변이 근거에 의해 뒷받침되는 정도와 질문에 직접 대응하는 정도는 answer-level 관찰이고, 검색 문맥의 관련성과 필요한 근거의 포함 정도는 context-level 관찰이다. 본 연구는 이 네 값을 평균 하나로 합성하지 않는다. 지표별 최고 configuration, 대응쌍의 평균 차이, 신뢰구간, win/loss/tie를 병렬로 제시하여 서로 다른 방향의 결과를 숨기지 않는다.

[스타일=본문]

SCD의 범위도 명확히 제한한다. Korean-character ratio는 답변 안의 한글 문자 수를 한글 문자와 ASCII 영문자 수의 합으로 나누어 계산한 직접 언어 지표다. 이 값이 높다는 사실은 사용자가 요청한 한국어 출력에 더 가까워졌다는 증거가 될 수 있으나, 그 자체로 근거 충실도·질문 적합성·문장 자연스러움을 확정하지 않는다. 본문은 SCD의 언어 유지 결과를 직접 결과로 제시하고, 별도 정규화나 교차 judge sensitivity panel을 일반 RAG 품질 결론으로 확대하지 않는다.

[스타일=본문]

마지막으로 이 보고서는 연구 실험과 별도 서비스 구현을 구분한다. 저장소에 문서 업로드와 대화 기능이 존재하더라도, 그러한 기능의 실행 상태나 배포 준비도는 본 논문의 실험 변수나 평가 결과가 아니다. 본문에서 언급하는 UI는 오직 저장된 실험 artifact의 query·answer·score·retrieval provenance를 read-only로 보여 주는 evidence replay UI다. 따라서 이 UI는 새로운 inference 결과나 사용자 경험 효과를 주장하는 근거가 아니라, 이미 계산된 연구 결과를 검토 가능한 형태로 재현하는 증빙 인터페이스다.

## 1.3 연구 질문, 분석 관점 및 논문 구성 [스타일=절제목]

[스타일=본문]

본 연구의 첫 번째 연구 질문은 “한국어 질문과 영어 학술문장의 표현 차이가 존재할 때, HyDE 기반 검색 표현 확장이 최종 답변의 질문 적합성과 근거 관련성에 어떤 변화를 만드는가”이다. 이 질문은 HyDE가 문서 집합 전체에서 절대적으로 우수한 검색 방법인지 묻는 것이 아니다. 한국어 질의, 영어 대상 문서, BGE-M3·BM25·weighted RRF·CrossEncoder로 고정한 backbone에서 H1C0S0과 H0C0S0의 차이가 어떠한지를 묻는다. 따라서 HyDE 결과는 질의 번역, hypothetical document 생성, dense retrieval 표현 변경을 모두 포함하는 end-to-end 검색 확장 효과로 한정한다.

[스타일=본문]

두 번째 연구 질문은 “검색 입력이 같은 상태에서 CAD가 생성 결과를 어떻게 변화시키는가”이다. 이 질문을 위해 H0C0S0과 H0C1S0을 비교하되, contexts, retrieved chunk IDs, reranked chunk IDs가 모두 같은 record만 primary contrast에 사용한다. 답변이 달라졌다는 사실만으로 CAD의 효과를 말하지 않고, 먼저 입력이 정말 같은지 확인한다. faithfulness의 5개 결측은 원본 평가 상태 그대로 두고 양쪽 score가 완결된 58쌍만 해당 지표에 사용한다. 이 선택은 표본 수를 보기 좋게 맞추기보다 생성-side comparison의 해석 조건을 보존하기 위한 것이다.

[스타일=본문]

세 번째 연구 질문은 “SCD가 영어 근거 문맥 아래에서 한국어 답변을 유지하는 직접적인 변화와 어떤 관련을 갖는가”이다. 이를 위해 같은 query·HyDE·CAD 조합의 SCD OFF/ON 240쌍을 만들고 Korean-character ratio의 차이를 계산한다. 여기서 핵심은 ratio가 내용 품질의 대리 점수가 아니라는 점이다. ratio는 output language에 관한 직접 관찰이고, answer relevancy와 faithfulness는 별도 자동 평가 결과다. HyDE OFF에서 retrieval·rerank·contexts가 같은 120쌍을 따로 제시하는 이유도 검색 변경 없이 output-language control이 관찰되는지 확인하기 위해서다.

[스타일=본문]

네 번째 연구 질문은 “2×2×2 조합의 각 configuration이 어떤 trade-off profile을 보이는가”이다. 이 질문에는 primary contrast와 다른 분석 단위를 사용한다. H0C0S0부터 H1C1S1까지 여덟 조건의 평균을 나란히 놓고 faithfulness, answer relevancy, context precision, context recall, Korean ratio, generation duration을 분리해 본다. 한 configuration이 모든 열의 최고값이 되지 않는다면, 그 결과는 실패가 아니라 목적별 선택이 필요하다는 정보다. 본 연구는 지표를 임의 가중치로 합쳐 하나의 종합점수를 만들지 않으며, 사용 목적과 비용을 숨기는 단순 순위를 만들지 않는다.

[스타일=본문]

논문의 분석 관점은 수치, 입력 provenance, 실제 출력의 세 층으로 구성한다. 첫째, paired mean, bootstrap interval, win/loss/tie는 60개 질의에서 관찰된 방향과 불확실성을 요약한다. 둘째, query ID, configuration, chunk ID, contexts identity는 어느 비교가 retrieval change를 포함하고 어느 비교가 동일 입력인지 확인한다. 셋째, read-only evidence replay UI는 선택된 저장 답변과 score를 화면에서 그대로 보여 준다. 어느 한 층만으로는 충분하지 않다. 평균만으로는 한 사례의 입력 차이를 알 수 없고, 한 사례만으로는 60-query 경향을 말할 수 없으며, provenance 없이 작성된 답변 화면은 연구 증거가 될 수 없다.

[스타일=본문]

이후 2장에서는 RAG, hybrid retrieval, HyDE, CAD, SCD, 평가와 재현성에 관한 관련 연구를 본 실험의 분석 축과 연결한다. 3장에서는 실험 요구사항과 comparison contract를, 4장에서는 저장 record와 artifact 재현 흐름을 설명한다. 5장에서는 60-query 구성·평가 방법·조합별 결과·요인별 해석·실제 UI 사례·종합 논의·한계를 순서대로 제시한다. 6장은 수치의 반복이 아니라 연구 질문별 결론, 구성 선택의 함의, 후속 검증 방향을 종합한다. 이 구성은 논문을 실험 결과의 압축본이 아니라 설계 근거와 해석 경계를 함께 제공하는 연구 문서로 만들기 위한 것이다.

# 2. 이론적 배경 [스타일=장제목]

## 2.1 Retrieval-Augmented Generation [스타일=절제목]

RAG는 질의에 관련된 문서 조각을 검색해 생성 모델의 입력 문맥으로 제공하는 구조이다. 문서 집합을 D, 질의를 q, 검색 문맥을 C, 답변을 y라 하면 과정은 Retrieve(q, D)로 C를 얻고, language model이 q와 C를 바탕으로 y를 생성하는 흐름으로 설명할 수 있다. 검색 단계의 결과와 생성 단계의 답변은 서로 관련되지만 같은 측정 대상은 아니다. 따라서 본 연구에서는 answer-level 지표와 context-level 지표를 분리해 기록한다.

## 2.2 Hybrid Retrieval과 재정렬 [스타일=절제목]

고정 backbone은 BGE-M3 기반 dense retrieval과 BM25 기반 sparse retrieval을 결합한다. Dense retrieval은 질의와 문서의 의미적 유사성을 표현하고, BM25는 전문용어·수치·약어 같은 표면적 일치를 보완한다[5][6]. 두 순위는 weighted Reciprocal Rank Fusion으로 결합한 뒤 CrossEncoder가 후보를 재정렬한다[7][8]. 저장 record에는 retrieval pool 8개, rerank top-N 8개, 최종 문맥 5개와 각 단계의 chunk ID가 남아 있어, 조건 간 검색 변화와 생성 결과를 분리해 확인할 수 있다.

## 2.3 Hypothetical Document Embeddings [스타일=절제목]

HyDE는 질의에 대한 가상의 답변 또는 문서를 생성하고 그 표현을 검색에 이용한다[2]. 짧은 질의가 대상 문서의 학술적 표현과 차이가 클 때, 가상 문서는 검색 표현을 확장하는 매개가 될 수 있다. 본 연구에서는 HyDE ON/OFF에 따라 검색 결과가 바뀌는 end-to-end 효과를 answer relevancy와 retrieval record를 함께 사용해 분석한다. HyDE로 생성된 가상 문서는 근거 문서가 아니므로, 검색 변화가 모든 질의에서 같은 방향의 품질 변화를 만든다고 전제하지 않는다.

## 2.4 Context-Aware Decoding [스타일=절제목]

CAD는 문맥이 포함된 생성 분포와 문맥이 없는 생성 분포를 대조해 문맥 조건의 영향을 반영한다[3]. 본 실험에서는 CAD alpha=0.5를 기록하고, CAD ON/OFF 비교 시 검색 문맥이 byte 수준으로 같은 대응쌍을 사용한다. 이 설계는 retrieval 자체의 변화와 decoding 차이를 구분하기 위한 것이다. CAD는 별도의 무문맥 branch를 계산하므로 generation duration도 함께 제시한다.

## 2.5 Soft Constrained Decoding과 언어 이탈 [스타일=절제목]

다국어 RAG에서 질의 언어와 근거 문서 언어가 다르면 답변의 언어가 문맥 언어 쪽으로 이동할 수 있다. SCD는 vocabulary를 목표 언어·비목표 언어·중립 토큰으로 구분하고, decoding 단계에서 token score에 제약을 적용한다[4]. 본 실험의 reference SCD는 alpha=1.1, beta=0.9, Tstart=5로 기록되어 있다. 한국어 문자 비율은 한글 문자 수를 한글 문자와 ASCII 영문자 수의 합으로 나눈 값이며, LLM judge와 독립적으로 계산한다.

## 2.6 RAG 평가 [스타일=절제목]

HyDE와 CAD의 품질 비교에는 faithfulness, answer relevancy, context precision, context recall을 사용한다[9]. 각 지표는 60개 대응 질의에서 ON-OFF 차이를 계산하고 paired bootstrap 95% 신뢰구간을 제시한다. Faithfulness의 일부 record는 원본 평가에서 빈 명제 집합으로 저장되어 있으므로, 해당 지표는 양쪽 점수가 존재하는 대응쌍만 사용하며 CAD 주 비교의 완결 표본 수는 58이다. SCD의 직접 평가는 동일 query·HyDE·CAD 조건의 ON/OFF 답변에서 계산한 한국어 문자 비율 차이를 사용한다.

[스타일=본문]

RAG의 기본 흐름은 질의 q와 문서 집합 D에서 검색 문맥 C를 얻고, 생성 모델이 q와 C를 조건으로 답변 y를 생성하는 과정으로 표현할 수 있다. 검색 단계는 필요한 근거의 후보를 선택하고, 생성 단계는 선택된 근거를 자연어 답변으로 조직한다. 두 단계는 연결되어 있지만 같은 오류를 뜻하지 않는다. 필요한 문단이 검색되지 않은 경우에는 context recall의 문제가 나타날 수 있고, 관련 문단이 검색되었으나 답변에 충분히 반영되지 않은 경우에는 faithfulness 또는 answer relevancy의 문제가 나타날 수 있다. 그래서 본 연구는 retrieval record와 answer-level score를 하나의 총점으로 합치지 않고 별도 열로 저장한다.

[스타일=본문]

Hybrid retrieval은 서로 다른 실패 양식을 보완하기 위한 고정 구성이다. Dense retrieval은 한국어 질의와 영어 passage 사이의 의미적 근접성을 활용하므로 어휘가 달라도 관련 후보를 찾을 가능성을 제공한다. BM25는 모델명, 데이터셋 이름, 수치, 약어처럼 표면 일치가 중요한 경우에 강한 신호를 제공한다. 두 결과는 raw similarity를 직접 더하지 않고 rank 기반 weighted RRF로 결합한다. dense 경로에는 0.6, BM25 경로에는 0.4의 가중치를 고정했고, 결합 후보는 CrossEncoder가 질의와 passage를 함께 보며 재정렬한다. 이 선택은 본문에서 비교하는 H·C·S 이외의 검색 규칙을 고정하기 위한 것이다.

[스타일=본문]

재정렬 뒤의 문맥 구성도 결과 해석에서 빠질 수 없다. 최종 생성 모델은 검색 후보 전체가 아니라 상위 다섯 문맥을 입력으로 받는다. 따라서 retrieved chunk ID와 reranked chunk ID, 실제 contexts를 함께 보존해야 한다. HyDE OFF와 ON에서 이 ID들이 달라지면 HyDE의 차이는 단순한 decoder 효과가 아니라 바뀐 검색 근거를 포함한 end-to-end 결과다. 반대로 CAD 비교에서 세 항목이 동일하게 확인되면 answer 차이는 검색 입력 변화가 아니라 decoding 조건과 연결해 해석할 수 있다. 이 distinction은 평균값의 인과적 범위를 과장하지 않기 위한 설계 원칙이다.

[스타일=본문]

HyDE는 relevance label이 없는 dense retrieval에서 질의 표현을 문서에 가까운 서술로 확장하는 방식이다. 본 실험의 HyDE ON pipeline은 한국어 질의를 영어 검색 표현으로 바꾸고 hypothetical document를 생성한 뒤, 그 문서를 dense retriever에 제공한다. hypothetical document는 실제 논문 passage나 답변의 근거가 아니다. 그것은 검색을 위한 표현일 뿐이며, 최종 답변은 여전히 검색된 영어 문맥에서 구성된다. 따라서 HyDE가 answer relevancy의 양의 차이와 함께 관찰되더라도 그 결과는 번역·가상 문서·dense retrieval 변경을 포괄하는 pipeline effect로만 해석한다.

[스타일=본문]

CAD의 핵심은 문맥을 넣은 next-token distribution과 문맥을 제거한 distribution을 대조하는 데 있다. 문맥이 있는 logits를 z_ctx, 문맥이 없는 logits를 z_noctx라고 하면, 본 실험의 고정 alpha=0.5 조건은 두 분포의 차이를 반영해 문맥에 의해 더 강해진 token을 상대적으로 강조한다. 이 방식은 검색 결과를 새로 고르지 않는다. 다만 매 생성 단계에서 두 branch를 계산하므로 실행 시간이 늘어날 수 있다. 그래서 CAD는 평균 faithfulness나 answer relevancy뿐 아니라 condition별 generation duration을 함께 보고해야 하며, 더 느린 조건을 단순히 품질만으로 선택하지 않는다.

[스타일=본문]

SCD는 language drift를 token selection의 문제로 다룬다. 본 실험의 reference SCD는 warm-up 단계 이후 한국어 목표 토큰의 raw logit에 alpha=1.1을 적용하고, 비목표 영어 토큰에는 beta=0.9를 적용하며, 공백·숫자·문장부호처럼 언어에 직접 종속되지 않는 중립 토큰은 유지한다. Tstart=5는 처음 몇 token에서 제약을 강하게 적용하지 않는 설정이다. CAD와 SCD가 함께 적용될 때에는 CAD score를 먼저 구성한 뒤 SCD processor를 적용한다. 이 순서는 모든 SCD ON record의 metadata로 남아 있어, 설정을 문서 설명만으로 추정하지 않도록 한다.

[스타일=본문]

RAGAS의 네 지표와 Korean-character ratio는 역할이 다르다. Faithfulness는 답변의 주장이 주어진 context로부터 뒷받침되는 정도, answer relevancy는 답변이 질문에 직접 반응하는 정도를 관찰한다. Context precision과 recall은 답변이 아니라 검색 문맥의 관련성과 필요한 근거의 포함을 관찰한다. Korean-character ratio는 표면적 언어 성향을 직접 계산한다. 따라서 SCD가 ratio를 올렸다는 결과를 일반적인 RAG quality 향상으로 바꾸어 말할 수 없고, HyDE가 answer relevancy를 높였다고 해서 모든 context metric이 올라갔다고 말할 수도 없다. 본 보고서는 이 지표들의 개념적 경계를 결과 해석 전반에서 유지한다.

[스타일=본문]

대응 비교의 신뢰구간은 질의를 재표집 단위로 하는 paired bootstrap으로 계산한다. 같은 query ID의 ON과 OFF 차이를 먼저 구한 뒤, 질의를 단위로 재표집해 평균 차이의 분포를 만든다. 이 방법은 configuration 평균만 나열할 때 생길 수 있는 개별 질문의 영향 은폐를 줄인다. 품질 지표의 win/loss/tie는 차이가 +0.01보다 크면 win, -0.01보다 작으면 loss, 그 사이면 tie로 집계한다. SCD ratio는 실제 사용자가 체감할 수 있는 언어 전환과 구분하기 위해 ±0.02 practical band를 사용한다. 이 보조 집계는 검정의 대체물이 아니라 평균과 신뢰구간을 읽는 데 필요한 질의별 방향 정보다.

[스타일=본문]

학술문서 RAG에서 문맥의 길이와 배치도 검색 품질과 별개로 고려할 필요가 있다. 같은 다섯 passage라도 질문에 직접 답하는 문장이 앞·뒤 어느 위치에 놓이는지, passage 내부의 부연 설명이 어느 정도 포함되는지에 따라 생성 모델이 활용하는 방식이 달라질 수 있다. 본 backbone은 reranking 결과를 받아 문맥을 선택·정렬·압축하는 규칙을 고정한다. 이 규칙을 모든 configuration에 동일하게 적용함으로써, H·C·S의 효과와 문맥 길이 정책의 효과를 동시에 바꾸지 않는다. 다만 HyDE ON은 검색 후보 자체를 바꿀 수 있으므로, 최종 문맥 변화는 HyDE pipeline effect에 포함된다.

[스타일=본문]

Hybrid retrieval의 장점은 언제나 두 경로의 점수가 높다는 뜻이 아니다. 어떤 질문은 영어 논문의 고유 약어를 포함해 BM25의 표면 단서가 유용할 수 있고, 어떤 질문은 한국어의 설명형 표현과 영어의 학술적 서술 사이의 의미적 연결이 더 중요해 dense retrieval이 유용할 수 있다. weighted RRF는 두 rank list를 보존하면서 후보군을 만들고, CrossEncoder가 그 후보를 다시 평가한다. 따라서 H0/H1의 검색 차이를 해석할 때 dense 결과만 보거나 BM25 결과만 보는 것은 충분하지 않다. record에 남은 최종 IDs와 contexts는 pipeline 전체가 선택한 근거의 흔적이다.

[스타일=본문]

HyDE를 교차언어 환경에 적용할 때에는 hypothetical document의 역할을 특히 엄격하게 구분해야 한다. 한국어 질의를 영어로 변환해 문서형 서술을 생성하는 과정은 실제 논문의 내용을 복사하거나 사실을 보장하는 과정이 아니다. 그 문서는 dense space에서 검색에 유리한 표현을 제공할 수 있지만, 잘못된 상세 묘사를 포함할 수도 있다. 그래서 최종 answer는 hypothetical document가 아니라 대상 논문에서 검색·rerank된 contexts에 의해 뒷받침되어야 한다. 본문에 보이는 HyDE 사례도 가상 문서의 그럴듯함을 증명하는 용도가 아니라, 그 뒤에 실제 retrieved IDs가 달라졌는지를 보여 주는 용도다.

[스타일=본문]

CAD의 대조식은 context가 없을 때도 높은 확률을 갖는 일반적 token과, 주어진 context에서 상대적으로 강화되는 token을 구분하려는 시도다. 그러나 이러한 재가중은 정답 token만을 선택하도록 보장하지 않는다. 문맥 자체가 불완전하거나 질문이 한 문맥보다 여러 passage의 종합을 요구하면, 문맥 의존성을 강조하는 것이 답변의 간결성·관련성·근거성에 서로 다른 영향을 줄 수 있다. 이에 따라 CAD의 결과는 '문맥을 더 믿게 하므로 항상 더 faithful하다'는 명제로 바꾸지 않는다. 본 연구는 동일 input의 paired metric과 answer 사례, 그리고 생성 시간이라는 세 관찰을 함께 사용한다.

[스타일=본문]

SCD의 soft constraint는 vocabulary를 hard하게 제한하는 방식과 구분된다. target token을 남기고 distractor token을 완전히 금지하는 경우에는 고유명사, 인용, 수식, 영어 기술 용어처럼 학술 답변에 필요한 표현도 부자연스럽게 제한될 수 있다. reference SCD는 목표 토큰과 비목표 토큰의 raw logit에 서로 다른 계수를 곱하되 중립 token을 유지하는 방식이다. 따라서 ratio가 높아져도 영어 고유명사나 논문 제목이 모두 사라졌다는 뜻은 아니며, 한국어 답변 안에 필요한 영어 기술 용어가 남는 것은 언어 이탈과 구분해서 읽어야 한다.

[스타일=본문]

Korean-character ratio의 분모는 한글 문자와 ASCII 영문자를 사용한다. 숫자, 공백, 문장부호, 코드 기호는 비율을 직접 움직이지 않는다. 이 정의는 계산이 결정적이고 생성 모델이나 judge의 호출이 필요 없다는 장점이 있다. 반면 한국어 형태소의 정확성, 문장 구조, 번역 충실도, 기술 용어 사용의 적절성은 측정하지 않는다. 0.5 미만이라는 threshold도 언어 성향을 설명하기 위한 operational rule이지, 답변이 무조건 실패했다는 판정은 아니다. 본문에서 language drift screen을 제시할 때에는 이 측정 경계를 캡션과 해설에서 함께 밝힌다.

[스타일=본문]

평가 설계에서 paired comparison을 채택한 또 다른 이유는 질문 난이도의 영향을 줄이기 위해서다. 어떤 질문은 검색 문맥이 충분해도 답변이 길고 복합적일 수 있고, 어떤 질문은 한 문장으로 답할 수 있다. configuration별 전체 평균만 비교하면 질문 구성의 차이가 결과에 섞일 수 있다. 같은 query ID를 ON/OFF로 대응시키면 각 질문의 고유 난이도는 차이 계산에서 상당 부분 상쇄된다. 그래도 질의 수가 60개라는 범위와 자동 judge의 특성은 남으므로, bootstrap interval과 win/loss/tie를 보고 외적 일반화의 범위를 제한한다.

[스타일=본문]

faithfulness의 빈 명제 집합은 평가 시스템이 어떤 answer에서 검토 가능한 claim 집합을 만들지 못한 상태를 뜻한다. 이를 0으로 바꾸면 실제로 낮은 faithfulness를 받은 answer와 의미가 달라지고, 평균에 인위적 불이익을 줄 수 있다. 본 분석은 결측을 보존하고 지표별 valid paired count를 표기한다. 이 선택은 수치가 더 보기 좋게 나오도록 조정하는 대신 원본 evaluation artifact의 상태를 논문 독자가 다시 확인할 수 있게 한다. 결측이 존재한다는 사실 자체가 평가 프로토콜의 한계와 데이터 품질을 함께 설명하는 정보다.

[스타일=본문]

이론적 배경을 정리하면, RAG는 검색된 근거와 생성 답변의 연결을 다루는 기본 구조이고, hybrid retrieval과 reranking은 고정된 근거 선택 경로이며, HyDE는 검색 표현의 확장, CAD는 문맥 조건 분포의 대조, SCD는 output token 언어 성향의 조정이다. RAGAS와 Korean-character ratio는 각기 다른 결과 층위를 측정한다. 이후 장에서는 이 구분이 실제 record field와 분석 비교에서 어떻게 구현되었는지, 그리고 60-query 결과에서 어떤 차이로 관찰되었는지를 순서대로 제시한다.

## 2.7 관련 연구와 본 연구의 위치 [스타일=절제목]

[스타일=본문]

검색 증강 생성의 발전은 대체로 세 층위에서 이루어져 왔다. 첫째, 검색기의 표현력과 후보 선택을 개선하는 흐름이다. Dense Passage Retrieval은 질의와 passage를 각각 인코딩해 의미적으로 가까운 근거를 찾는 방식을 정립했고[10], 이후 대규모 임베딩 모델과 zero-shot 검색 벤치마크는 언어·도메인·질의 형식에 따라 검색 성능의 편차가 커질 수 있음을 보였다[20][21]. 둘째, 검색된 정보를 생성 모델이 실제로 활용하게 만드는 흐름이다. Fusion-in-Decoder는 여러 passage를 조건으로 답을 구성하는 방식을 제안했고[11], retrieval-augmented generation의 위치·길이·문맥 구성은 생성 단계의 활용률에도 영향을 준다는 점이 지적되어 왔다[12]. 셋째, 생성 자체를 자기 검증·대조·보정하는 흐름이다. Self-RAG와 Corrective RAG는 검색 여부와 근거의 품질을 더 적극적으로 다루며[15][16], contrastive decoding은 서로 다른 조건의 분포 차이를 이용해 token 선택을 조정한다[13].

[스타일=본문]

그러나 이 흐름들을 그대로 결합했다고 해서 한국어 질의-영어 학술문서 환경의 문제가 자동으로 해결되는 것은 아니다. 이 환경에서는 적어도 세 종류의 언어 경계가 동시에 존재한다. 질의는 한국어로 입력되고, 검색 대상은 영어 논문 passage이며, 최종 답변은 사용자에게 한국어로 제공되어야 한다. 한국어 질의가 영어 논문에서 사용하는 용어와 정확히 대응하지 않을 수 있고, 검색된 영어 문맥이 답변의 표면 언어를 영어 쪽으로 끌어갈 수 있으며, 생성 모델이 한국어 문장과 영어 고유명사·약어를 함께 다루어야 한다. 따라서 본 연구의 문제 설정은 새로운 RAG 알고리즘을 제안하는 것이 아니라, 이미 알려진 HyDE·CAD·SCD를 고정된 실제 시스템에 각각 또는 함께 적용했을 때 세 층위의 관찰값이 어떻게 달라지는지를 검증하는 응용·비교 연구이다.

[스타일=본문]

HyDE 관련 연구는 가상의 문서 표현이 짧거나 추상적인 질의와 대상 코퍼스의 표현 간 간극을 줄일 수 있음을 보여 주었다[2]. 본 연구는 그 아이디어를 한국어 질의와 영어 학술 passage 사이에 배치한다. 다만 한국어 질의의 영어 검색 표현과 hypothetical document가 함께 바뀌는 경로를 사용하므로, 여기서 관찰되는 변화는 순수한 dense retrieval의 효과로 환원할 수 없다. 번역 또는 query reformulation, 가상 문서 생성, 임베딩 검색, hybrid fusion, 재정렬, 최종 문맥 구성의 누적 결과다. 이 연구가 HyDE의 일반 성능을 선언하지 않고 `fixed-backbone application effect`라고 부르는 이유가 여기에 있다. 결과의 평균 차이가 작더라도 실제 retrieved ID와 answer 사례를 함께 제시해야 하는 이유도 동일하다.

[스타일=본문]

CAD는 문맥이 있을 때와 없을 때의 생성 분포를 대비시킨다는 점에서 retrieval method와 구별된다. 이 구별은 실험 설계에서 중요하다. 만약 CAD ON/OFF가 서로 다른 문맥을 입력으로 받는다면, 더 높은 또는 더 낮은 점수가 decoder 조정 때문인지 검색 근거의 변화 때문인지 알 수 없다. 그래서 본 연구에서는 query ID, HyDE, SCD가 같은 record를 묶고, CAD만 다른 조건에서 contexts와 최종 chunk IDs가 같은 대응쌍을 우선 확인한다. 이는 대조식 decoding 자체의 독립적 효과를 과장 없이 읽기 위한 최소 조건이다. 동일 input 아래에서도 CAD가 모든 지표를 같은 방향으로 움직이지 않는다면, 그 결과는 문맥 신호를 강화하는 일반 원리와 특정 논문 질의에서의 답변 품질이 일대일 대응하지 않는다는 근거가 된다.

[스타일=본문]

SCD는 언어 선호를 decoding 단계에서 부드럽게 조정한다는 점에서, 검색 전 번역이나 prompt로 목표 언어를 지시하는 방식과 구별된다. 본 연구에서 SCD를 평가할 때 단순히 “한국어 답변이 생성되었다”는 사례만으로 충분하지 않은 이유도 여기에 있다. 동일한 query·HyDE·CAD·context 조합의 SCD ON/OFF 답변을 직접 대응시켜야만, 관찰한 언어 성향 변화가 검색된 문서나 질문 묶음의 차이가 아니라 token-level 제약과 연결되었다고 말할 수 있다. 반대로 이 직접 비교가 Korean-character ratio라는 단일 운영 지표에 기반한다는 사실은, SCD가 사실성·관련성·번역 품질을 포괄적으로 개선했다는 주장을 제한한다. 본문은 이 성질을 SCD의 성공을 축소하는 근거가 아니라, 측정한 대상과 측정하지 않은 대상을 분명히 하는 연구 윤리로 취급한다.

[스타일=본문]

최근 RAG 연구는 end-to-end 평균 점수 하나만으로 시스템을 비교하는 데 주의를 요구한다. 서로 다른 retriever, reranker, generator, prompt, context window, judge model이 동시에 달라지면 개선의 원인을 단일 기법에 귀속하기 어렵다[17][19]. 또 자동 평가기는 빠르고 일관된 비교를 가능하게 하지만, 문항의 정답 범위·주장 추출·언어 혼합에 따라 판정의 불확실성을 가진다[9]. 본 연구는 이를 해결했다고 주장하지 않는다. 대신 (a) backbone과 생성 record의 contract를 고정하고, (b) 비교별로 변한 요인을 명시하며, (c) 원본 점수의 결측을 보존하고, (d) 표본 단위 paired bootstrap과 사례 화면을 함께 제공하는 방식으로, 결론이 어떤 artifact에서 왔는지를 추적 가능하게 한다.

[스타일=본문]

표 2-1은 관련 연구의 관심 대상과 본 연구의 연결 지점을 정리한다. 표의 “적용 범위”는 선행 연구를 재현했다는 뜻이 아니라, 그 연구가 제시한 개념을 본 실험에서 어떤 관찰 가능한 비교로 번역했는지를 뜻한다. 예를 들어 DPR과 BEIR은 본 연구가 새로운 retrieval benchmark를 구축했다는 근거가 아니라, 검색 표현과 도메인 이동을 구분해야 한다는 이론적 배경을 제공한다. 마찬가지로 Self-RAG나 CRAG는 본 시스템에 동일한 reflection 또는 corrective module이 구현되었다는 뜻이 아니라, 검색·생성의 실패를 분리해 다뤄야 한다는 비교 관점을 제공한다.

[표 2-1] 관련 연구와 본 실험의 연결 [스타일=표제목]

| 연구 흐름 | 대표 연구 | 본 연구에서의 적용 범위 | 본문 해석의 제한 |
|---|---|---|---|
| Dense retrieval | DPR[10], BEIR[20] | 한국어 질의와 영어 passage 사이의 검색 표현 간극을 HyDE 조건으로 관찰 | retriever 자체의 일반 순위 성능을 재측정한 것이 아님 |
| Multi-passage generation | FiD[11], long-context 분석[12] | rerank된 상위 5개 문맥을 고정해 answer/context 지표를 분리 | 문맥 길이·순서 정책을 탐색하지 않음 |
| Hypothetical-document retrieval | HyDE[2] | H1/H0의 end-to-end 대응 비교 및 retrieved ID 확인 | 가상 문서가 근거나 정답이라는 뜻이 아님 |
| Contrastive decoding | CAD[3], contrastive decoding[13] | 같은 input에서 C1/C0의 paired 비교 | alpha 최적화 또는 일반적 개선 주장 불가 |
| Corrective/reflective RAG | Self-RAG[15], CRAG[16] | 검색·생성·출력 문제를 별도 층위로 읽는 관점 | 해당 방법을 구현·비교한 것은 아님 |
| RAG evaluation | RAGAS[9], RAG survey[19] | 네 품질 지표와 artifact 기반 provenance 확인 | 자동 judge 결과를 인간 평가로 대체하지 않음 |

## 2.8 평가, 재현성 및 논문 서술의 원칙 [스타일=절제목]

[스타일=본문]

실험 논문에서 재현성은 동일한 평균값을 다시 인쇄할 수 있다는 뜻보다 넓다. 독자는 어떤 query가 어느 corpus에서 실행되었는지, 어떤 configuration이 적용되었는지, 어떤 record가 점수 산출에 포함되었는지, 표와 그림의 값이 어디에서 왔는지를 역추적할 수 있어야 한다. 본 연구는 generation JSONL, evaluation score JSON, 분석 CSV·JSON, evidence manifest를 분리해 보관하고, 본문 표는 이 저장 artifact에서 계산한 값을 참조한다. 이 구성은 온라인 모델 호출이나 새로운 retrieval 실행 없이도 이미 생성된 답변·문맥·점수의 대응을 재검토할 수 있게 한다. 즉, 본문에서 말하는 재현은 결과를 새로 만들어 동일한 숫자를 얻는 live reproducibility가 아니라, 보존된 실험 산출물로부터 보고된 결론을 확인하는 artifact-backed replay이다.

[스타일=본문]

이 구분은 특히 학술문서 RAG에 중요하다. 생성 모델과 judge API의 버전, 외부 서비스의 상태, GPU 실행 환경은 시간이 지나며 달라질 수 있다. 같은 prompt를 다시 호출해도 똑같은 답변이나 judge score가 재현된다고 가정할 수 없다. 반면 원본 generation record에는 query ID, condition, contexts, answer, retrieval ID, runtime metadata가 있고, evaluation artifact에는 해당 answer의 metric score와 결측 상태가 남아 있다. 이 기록을 유지하면 논문 독자는 수치가 어떤 예시의 일반화인지, 특정 metric의 분모가 왜 다른지, UI 사례가 실제 저장 answer와 일치하는지를 검토할 수 있다. 본 연구는 외부 환경이 변하지 않는다는 강한 가정을 두는 대신, 이미 수행한 실험의 provenance를 보존하는 방식을 택한다.

[스타일=본문]

또한 재현 가능한 연구 서술은 편의상 불리한 record를 제거하지 않아야 한다. 본 분석에서 faithfulness의 빈 명제 집합은 오류값 0이나 최고점으로 치환하지 않고 결측으로 남긴다. 이에 따라 유효 paired count가 metric마다 달라진다. CAD faithfulness의 주 비교가 58쌍인 반면 answer relevancy는 60쌍이라는 표기는 분석의 약점이 아니라 실제 분모를 공개하는 정보다. 같은 원칙으로 SCD의 언어 비율은 숫자·기호를 포함한 문장 길이가 아니라 한글과 ASCII 영문자의 구성 비율이라는 정의를 명시한다. 독자가 다른 정의를 선택하면 다른 값이 나올 수 있음을 문서가 숨기지 않기 위해서다.

[스타일=본문]

평가 결과를 논문으로 전환할 때에는 세 종류의 문장을 구별한다. 첫째는 `관찰`이다. 예를 들어 paired mean difference와 95% bootstrap interval, win/loss/tie 수, 실제 answer 문자열은 저장 artifact에서 직접 확인할 수 있는 사실이다. 둘째는 `해석`이다. HyDE가 일부 한국어 설명형 질의에서 영어 논문 표현에 가까운 후보를 찾았을 가능성, CAD가 문맥 의존성과 답변 직접성 사이의 긴장을 만들 수 있다는 설명은 관찰을 연결하는 논증이다. 셋째는 `한계와 가설`이다. 다른 학문 분야, 다른 모델, 더 큰 질의 집합에서도 같은 패턴이 유지되는지는 현재 artifact만으로 확정할 수 없다. 본문은 이 세 층위를 섞지 않고, 표·그림 캡션에는 관찰 근거를, 본문 해설에는 가능한 기제를, 결론에는 적용 범위를 각각 기록한다.

[스타일=본문]

사례 화면의 지위도 이 원칙에 포함된다. UI 화면은 사용자가 최종 시스템에서 어떤 한국어 질의와 영어 근거, 답변을 마주하는지를 보여 주는 질적 evidence이다. 그러나 화면 하나가 60개 질의 전체의 통계적 대표성을 증명하지는 않는다. 반대로 평균값만 제시하면 언어 이탈이나 retrieval change가 사용 경험에서 어떻게 나타나는지 알기 어렵다. 따라서 본 연구는 표 5장의 대응 통계와 그림의 여섯 UI replay를 결합하되, 화면은 전체 효과의 증명 대신 해당 조건에서 저장된 한 record의 재현 예시로 명시한다. 화면에 표시되는 query ID와 configuration은 표의 집계 단위와 연결되어 있어, 매력적인 예시만 따로 고른 서술이 되지 않도록 한다.

[스타일=본문]

마지막으로, 논문 형식 자체도 재현성의 일부다. 표 번호·그림 번호·캡션·출처·본문 인용이 서로 어긋나면 독자는 수치의 출처를 확인할 수 없다. 이 원고는 HWP 이전 시 장·절·본문·표제목·그림제목 스타일을 구분하고, 각 표와 그림에 삽입할 workbook sheet 또는 evidence image의 경로를 별도 안내서에 연결한다. 이는 Markdown 초안의 형식이 곧 제출물이라는 뜻이 아니다. 최종 HWP에서는 학교 양식의 표지·인준·목차·쪽번호·표/그림 목차를 적용해야 하며, 자동 변환 후 실제 쪽수를 점검해야 한다. 다만 원고 단계에서부터 자산의 출처와 배치 위치를 고정해 두면, HWP 편집 과정에서 결과 수치나 사례가 바뀌는 위험을 낮출 수 있다.

# 3. 시스템 설계 [스타일=장제목]

## 3.1 연구 및 실험 요구사항 [스타일=절제목]

연구 요구사항은 질의와 대상 문서의 고정 연결, 여덟 조건의 완전한 generation record, 요인별 대응 비교, 저장 record에서의 재현 가능한 evidence, 표·그림·본문 수치의 동일성으로 구성한다. 표 3-1은 이 요구사항과 확인 기준을 정리한다.

[표 3-1] 연구 및 실험 요구사항 [스타일=표제목]

`tables_60q_csv/T3-1_Requirements.csv`

## 3.2 아키텍처 설계 [스타일=절제목]

실험 아키텍처는 한국어 질의, 영어 대상 문서, hybrid retrieval, reranking, 문맥 구성, 조건별 decoding, 저장, 평가·분석의 순서로 구성한다. 그림 1-1은 연구 환경의 입력과 출력 관계를, 그림 3-1은 RAG-Cube의 여덟 configuration을 제시한다. 그림 내부 번호는 없으며 실제 문서 편집 단계에서 캡션만 부여한다.

![연구 환경](figures_60q/fig1_1_research_setting.png)

[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경 [스타일=그림제목]

![RAG-Cube 2×2×2](figures_60q/fig3_1_rag_cube.png)

[그림 3-1] HyDE, CAD, SCD의 독립 이진 요인으로 구성한 RAG-Cube 8개 조건 [스타일=그림제목]

## 3.3 상세설계 [스타일=절제목]

각 configuration은 같은 query ID와 대상 문서에 대해 실행되며, `config_name`, 요인 사용 여부, retrieval·rerank 결과, contexts, 생성 답변, duration, 오류 상태를 저장한다. SCD가 ON이면 SCD mode와 alpha·beta·Tstart도 저장한다. 표 3-2와 표 3-3은 여덟 조건 및 요인별 적용 위치와 비교 단위를, 표 4-4는 record의 주요 필드를 제시한다.

[표 3-2] RAG-Cube 8개 조건 [스타일=표제목]

`tables_60q_csv/T3-2_RAG-Cube.csv`

[표 3-3] 실험 요인별 적용 위치와 비교 단위 [스타일=표제목]

`tables_60q_csv/T3-3_Factor_Position.csv`

[스타일=본문]

실험 요구사항은 화면 기능의 수가 아니라 변인의 통제와 결과 추적 가능성으로 정의한다. 첫째, 각 query ID와 대상 paper가 고정되어야 한다. 둘째, 여덟 configuration이 빠짐없이 실행되어 같은 질문을 서로 비교할 수 있어야 한다. 셋째, 조건 이외의 backbone 요소는 고정되어야 한다. 넷째, 각 answer에 대해 retrieval·rerank 결과와 contexts가 보존되어야 한다. 마지막으로 표와 그림의 수치가 원본 generation과 evaluation artifact로 다시 연결되어야 한다. 표 3-1은 이 요구사항을 HWP 표로 옮길 수 있는 형태로 정리하며, 검증 기준은 모델의 새 실행이 아니라 저장 artifact의 존재와 field 일관성으로 확인한다.

[스타일=본문]

아키텍처는 입력, 검색 표현 구성, hybrid retrieval, 재정렬, 문맥 구성, conditional decoding, artifact 저장, 평가·분석의 흐름으로 나뉜다. 입력 단계에서는 query split의 한국어 질문과 대상 문서를 읽는다. HyDE OFF는 원질의를 dense retrieval에 제공하고, HyDE ON은 번역된 질의에서 만든 hypothetical document를 dense branch에 제공한다. BM25와 CrossEncoder에는 원질의를 유지한다. 이 설계는 HyDE를 dense retrieval 표현의 변경으로 제한하고, sparse와 reranking 경로를 통째로 바꾸는 별도의 기법으로 취급하지 않기 위한 것이다.

[스타일=본문]

검색 단계의 출력은 문장 형태의 답변보다 먼저 검토되어야 하는 연구 데이터다. 각 record에는 dense·sparse 후보를 결합한 뒤의 retrieved chunk ID와, CrossEncoder 후의 reranked chunk ID가 저장된다. 최종 contexts는 reranked 후보에서 선택된다. H0와 H1의 ID가 다르면 그 차이는 실패가 아니라 HyDE가 실제로 검색 표현을 바꿨다는 관측이다. 그러나 C0와 C1을 비교할 때에는 같은 query·paper에서 contexts, retrieved IDs, reranked IDs가 모두 동일한지 먼저 확인한다. 본문에서 CAD의 주 결과를 동일 문맥 58개 완결 faithfulness 쌍으로 제한한 이유가 이 설계에 있다.

[스타일=본문]

conditional decoding은 configuration 이름과 metadata를 함께 사용해 해석한다. CAD OFF에서는 기준 generation logits를 사용하고, CAD ON에서는 context/no-context 대조 branch의 결과를 사용한다. SCD OFF에서는 language score 조정을 하지 않으며, SCD ON에서는 reference_scd의 alpha·beta·Tstart와 mode가 record에 남는다. 같은 이름의 configuration이라도 실제 record가 해당 설정을 보존하지 않았다면 결과 비교의 근거가 약해진다. 이 때문에 표 4-4의 record field는 단순 구현 설명이 아니라, 실험 재현성과 claim provenance를 위한 최소 단위다.

[스타일=본문]

artifact 저장 뒤에는 generation과 evaluation을 분리한다. generation JSONL은 질문·문서·문맥·답변·조건·시간을, merged score JSON은 네 RAGAS 지표를 보존한다. derived-data builder는 두 묶음을 읽어 configuration 평균과 primary contrast를 계산하고, figure builder와 table builder는 이 파생 CSV와 JSON을 읽는다. 이 의존 관계는 본문에서 보이는 숫자가 임의의 표 편집 결과가 아니라, 파일 경로와 SHA-256으로 추적 가능한 source artifact에서 나왔음을 뜻한다. 모든 derived 단계는 read-only 입력을 전제로 하며, 논문 작성 중 retrieval, generation, judge 호출을 다시 실행하지 않는다.

[스타일=본문]

그림 3-1과 그림 4-1은 같은 시스템을 서로 다른 관점으로 보여 준다. 그림 3-1은 세 이진 요인의 조합 공간과 비교 관계를 보여 주고, 그림 4-1은 입력부터 artifact까지의 실행 흐름을 보여 준다. 두 그림을 구분하는 이유는 조건의 조합을 설명하는 도식과 실제 데이터 흐름을 설명하는 도식을 하나로 합치면 해석이 어려워지기 때문이다. HWP 이전 시 각 그림 아래에는 제공된 캡션을 붙이고, 표 제목은 해당 표의 위에 둔다. 그림 내부에 번호를 새로 넣지 않는 원칙도 유지한다.

[스타일=본문]

RAG-Cube 설계에서 configuration 이름은 단순 표기 이상의 역할을 한다. `hyde_off__no_decoder_control`처럼 저장된 config_name은 H0C0S0을 기계적으로 식별하고, use_hyde·use_cad·use_scd field는 이 이름과 실제 실행 metadata가 맞는지 확인하게 한다. 데이터 분석은 이름만 신뢰하지 않고 각 record의 boolean field와 parameter field를 함께 읽는다. 이 이중 확인은 전처리 과정에서 이름과 설정이 어긋나는 오류가 결과 표에 들어가는 것을 방지한다. 표 3-2의 H/C/S 표기는 사람이 읽기 쉬운 축약이고, JSONL의 config_name은 재현 계산을 위한 식별자다.

[스타일=본문]

비교 설계는 세 수준을 분리한다. 첫째, HyDE primary contrast는 C0S0 상태의 H1-H0 60쌍으로, 검색 표현 변경을 포함한다. 둘째, CAD primary contrast는 H0S0 상태의 C1-C0 중 동일 입력을 확인한 쌍으로, generation-side 차이를 본다. 셋째, SCD language contrast는 H와 C가 같은 S1-S0 240쌍으로, 출력 언어 제어를 본다. 네 번째로 configuration average는 실제 조합 전체의 기술통계다. 이 네 결과를 한 표의 같은 의미로 읽지 않는 것이 설계의 핵심이다. 특히 primary contrast의 paired delta와 8개 configuration의 평균 차이는 질문과 입력의 고정 조건이 다르다.

[스타일=본문]

데이터 흐름에서 query split과 generation artifact를 분리한 이유는 질의 자체가 결과에 맞추어 사후 변경되는 것을 막기 위해서다. query split에는 질문, 대상 문서, 질의 유형, reference 정보가 있고, generation 단계는 이를 읽어 여덟 configuration을 실행한다. 이후 평가 단계는 생성 답변과 contexts를 읽고 score를 별도 artifact로 저장한다. 분석 단계가 읽는 것은 원 query split, generation JSONL, merged score JSON이며, 그 외 presentation file은 파생 결과다. 이 순서가 유지되면 표의 숫자를 수정해도 source artifact와 맞지 않는지 verifier가 찾을 수 있다.

[스타일=본문]

CAD의 동일성 검사는 string-level contexts만 비교하지 않는다. retrieved IDs, reranked IDs, final contexts가 모두 같은지 확인한다. IDs가 같아도 context compression의 결과가 다르면 실제 모델 입력은 달라질 수 있고, contexts만 같아도 retrieval provenance가 다른 경우에는 분석 설명이 혼란스러울 수 있다. 본문 UI에서 세 가지 identity field를 나란히 보이는 것은 이 검사를 독자가 재수행할 수 있게 하기 위한 것이다. 동일성이 True인 CAD와 SCD 사례만을 입력 고정 사례로 부르고, False인 HyDE 사례는 검색 변화 사례로 별도 표시한다.

[스타일=본문]

replay UI의 selector는 답변이나 score를 파일에 복사해 두지 않는다. case registry에는 source path와 선택 규칙 또는 query/config selector만 있고, UI 실행 시 generation과 merged score artifact를 다시 읽는다. normal QA는 저장 score의 네 metric 평균과 ratio 조건으로 선택하고, language drift는 SCD OFF row 중 가장 낮은 ratio로 선택한다. SCD rescue와 HyDE retrieval change는 paired input identity 및 ID 변화 조건을 검사한다. CAD positive와 trade-off 사례는 선택한 query/config pair의 input identity가 더 이상 성립하지 않으면 화면을 만들지 못하도록 assertion을 둔다. 이 방식은 사례 화면이 논문을 위해 새로 작성된 answer가 아님을 보장한다.

[스타일=본문]

표·그림·원고의 관계도 설계에 포함된다. `build_60q_derived_data.py`는 source artifact에서 CSV와 Markdown review를 만들고, `build_tables_60q.mjs`는 같은 CSV를 Excel workbook으로 만들며, `build_figures_60q.py`는 derived summary와 selected evidence를 그림으로 구성한다. Workbook inspection dump나 preview PNG 같은 검토용 산출물은 final delivery에 포함하지 않는 임시물로 분류한다. 반면 `FINALDOCS/TABLES/TABLES_60Q.xlsx`, final PNG·SVG, UI replay output, manifest, validation report는 HWP 이전과 재검토에 필요한 delivery material이다.

[스타일=본문]

이 설계는 모델 실행을 다시 하지 않고도 일부 핵심 주장을 검토할 수 있게 한다. record 수, query 수, configuration 수, contexts identity, ratio, configuration mean, paired delta, bootstrap result는 저장 파일을 읽어 계산할 수 있다. 반면 새로운 문서나 새 generator에서 같은 결과가 재현되는지는 이 설계만으로 확인할 수 없다. 따라서 artifact replay는 기존 결과의 재현성 증거이지, 일반적인 제품 성능이나 미래 실행의 보장이 아니다. 이 차이를 명확히 하는 것이 논문 결과와 서비스 설명을 분리하는 이유다.

# 4. 프로그램 구현 [스타일=장제목]

## 4.1 시스템 환경 [스타일=절제목]

실험 generation record는 K-intelligence/Midm-2.0-Base-Instruct, deterministic greedy decoding, max_new_tokens=512을 기록한다. 검색은 BGE-M3 dense retrieval과 BM25 sparse retrieval을 weighted RRF로 결합하고 CrossEncoder로 재정렬한다. 검색 후보와 재정렬 후보는 각 8개이며 최종 문맥은 5개다. 표 4-1과 표 4-2는 실제 저장 record에 남은 실행 환경 및 고정 backbone을 정리한다.

[표 4-1] 실험 실행 환경 [스타일=표제목]

`tables_60q_csv/T4-1_Environment.csv`

[표 4-2] 고정 Paper-RAG backbone [스타일=표제목]

`tables_60q_csv/T4-2_Backbone.csv`

## 4.2 시스템 구성 [스타일=절제목]

실행 경로는 질의 입력, 필요할 때의 HyDE 검색 표현 생성, dense·sparse 검색과 RRF, reranking, 상위 문맥 선택, CAD와 SCD의 선택적 decoding, generation record 저장 순서다. 모든 configuration은 같은 data split과 backbone을 공유한다. 이 구조는 검색 표현을 바꾸는 HyDE, 생성 시 문맥 영향을 조절하는 CAD, 출력 토큰 언어 성향을 조절하는 SCD의 위치를 분리해 보여준다.

![Paper-RAG pipeline](figures_60q/fig4_1_pipeline.png)

[그림 4-1] 고정 Paper-RAG backbone에서 RAG-Cube 요인을 적용하는 실행 흐름 [스타일=그림제목]

## 4.3 시스템 구현 [스타일=절제목]

generation record는 query·문서·configuration의 연결을 식별하고, 검색과 reranking의 chunk ID, 최종 contexts, 답변, 시간, 요인 파라미터를 함께 보존한다. 따라서 결과 수치를 다시 계산할 때 별도의 모델 호출 없이 저장 artifact를 읽을 수 있다. 조건별 평균과 중앙 generation time은 표 4-3에 기록한다. CAD 조건의 시간은 문맥과 무문맥 분기를 함께 계산하는 기록이므로, 품질 결과와 별도의 실행 특성으로 해석한다.

[표 4-3] 조건별 평균 생성시간 [스타일=표제목]

`tables_60q_csv/T4-3_Runtime.csv`

[표 4-4] generation record 주요 필드 [스타일=표제목]

`tables_60q_csv/T4-4_Record_Fields.csv`

[스타일=본문]

실행 환경의 설명은 성능 수치를 일반화하기 위한 사양 광고가 아니라, 동일한 artifact를 어떤 고정 조건에서 만들었는지 기록하는 provenance다. generation record에는 K-intelligence/Midm-2.0-Base-Instruct, deterministic greedy decoding, max_new_tokens=512, retrieval pool 8개, rerank top-N 8개, 생성 문맥 5개가 남아 있다. 이 값들은 configuration마다 바꾸지 않았다. 따라서 H·C·S 조건 간의 차이를 읽을 때 생성 길이 상한이나 후보 수의 변경이 결과에 섞였다고 가정하지 않는다. 환경 표에는 record에 남은 실행 정보만 옮기며, 확인할 수 없는 장비 특성이나 서비스 운영 상태는 추가하지 않는다.

[스타일=본문]

dense retrieval과 BM25의 결합은 한 방법을 다른 방법의 fallback으로 취급하지 않는다. BGE-M3는 한국어 질의와 영어 문서의 의미적 근접성을 제공하고, BM25는 영어 문서 내부의 특정 약어·수치·고유명사에 대한 표면 단서를 제공한다. weighted RRF는 두 결과의 rank를 결합하고, CrossEncoder는 한국어 질의와 영어 passage를 함께 보며 후보 순서를 다시 정한다. 최종 answer가 어떤 문맥에서 나왔는지 확인하려면 단순히 answer text를 읽는 것에 그치지 않고, 그 answer와 함께 저장된 chunk ID 및 contexts를 봐야 한다. 이 구조가 evidence replay UI의 사례 화면에 ID와 문맥 동일성 여부를 같이 표시하는 이유다.

[스타일=본문]

HyDE의 구현 위치는 dense branch에 한정된다. 질문을 영어로 바꾸고 그 질문에 답할 듯한 hypothetical document를 만든 다음 dense retrieval query로 사용한다. 이 hypothetical document가 최종 generation prompt의 evidence로 들어가지는 않는다. 따라서 HyDE ON answer의 문장이 그 가상 문서와 비슷하다는 사실만으로 근거성이나 정답성을 주장할 수 없다. 구현상 중요한 검증은 H0와 H1이 다른 retrieved IDs 또는 reranked IDs를 갖는지, 그리고 바뀐 context에서 answer-level metric이 어떻게 달라졌는지다. 이 한계를 본문 사례 해석과 결론에서 함께 유지한다.

[스타일=본문]

CAD의 구현은 동일한 prompt에 두 branch를 만들어 context의 영향을 대조한다. 이 과정은 단일 branch보다 많은 계산을 요구하므로 실행 시간 기록이 필수다. 표 4-3의 평균 및 중앙 generation time은 CAD ON/OFF의 시간 차이를 확인하기 위한 보조 결과다. 시간 차이가 존재한다고 해서 모든 CAD ON answer가 더 좋거나 나쁘다는 뜻은 아니며, 품질 지표와 별도로 사용자가 선택해야 하는 비용이다. CAD 관련 결과는 동일 문맥에서의 paired quality 결과와 configuration 평균의 패턴을 나누어 제시해, 검색 변화가 섞일 수 있는 경우와 그렇지 않은 경우를 혼동하지 않는다.

[스타일=본문]

SCD 구현은 answer text를 사후 번역하거나 후처리로 한글을 덧붙이는 방식이 아니다. 생성 중 vocabulary token의 score를 조정하는 decoder processor이며, SCD ON record에는 mode와 alpha=1.1, beta=0.9, Tstart=5가 남는다. 이 점은 사용자에게 표시되는 answer가 저장 후 편집된 문장이 아니라 당시 decoding의 결과임을 확인하게 한다. Korean-character ratio도 그림을 만들기 위해 임의로 계산한 값이 아니라 저장된 generated_answer 문자열에서 결정적으로 다시 계산할 수 있다. UI replay는 이 문자열을 바꾸지 않고 display-only excerpt를 만든다.

[스타일=본문]

구현 결과를 저장한 record는 다음 검토 질문에 답할 수 있어야 한다. 특정 configuration이 정말 실행되었는가, SCD 파라미터가 약속한 값인가, H0/H1의 검색 결과가 실제로 달라졌는가, CAD 사례의 입력이 같은가, 답변과 score는 어떤 query ID에 속하는가, 실행 시간이 어느 record에서 계산되었는가가 그것이다. 표 4-4는 이 질문을 위해 필요한 필드를 정리한다. 이러한 기록이 없으면 결과 표의 평균을 다시 계산할 수 있어도, 한 사례의 의미를 input-to-output 흐름으로 검토하기 어렵다.

[스타일=본문]

최종 패키지에는 원고와 별도로 Excel workbook, 표별 CSV, PNG·SVG 그림, raw evidence replay output, data validation, cleanup manifest가 있다. Excel은 HWP 표로 복사하기 쉽게 sheet별 제목·출처·header row를 유지하고, 그림은 PNG 삽입본과 SVG 보관본을 구분한다. UI screenshot은 새 터미널 모형을 그린 이미지가 아니라 기존 `cli/evidence_replay.py`가 60-query artifact를 읽어 출력한 텍스트 UI를 그대로 렌더한 것이다. 이 방식은 답변·문맥·점수를 다시 쓰지 않으면서도 논문 독자가 실제 저장 record를 확인할 수 있게 한다.

# 5. 실험 [스타일=장제목]

## 5.1 실험 대상과 구성 [스타일=절제목]

최종 질의 집합은 RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report에 각각 15개 질문을 연결한 60개 질의-대상문서 쌍이다. 모든 질의는 valid answer span과 answerable 상태를 가지며, 중복 query ID나 중복 한국어 질문은 없다. 여덟 RAG-Cube configuration을 모두 적용하여 480개 generation record를 생성했다. 표 5-1은 문서별 분포를 제시하며, 부록 A에는 query ID·질문·대상 문서·질문 유형·source page·answer span 여부를 원자료에서 옮긴다.

[표 5-1] 4개 문서 × 15개 질의 = 60 [스타일=표제목]

`tables_60q_csv/T5-1_Dataset.csv`

## 5.2 평가 및 분석 방법 [스타일=절제목]

RAGAS 품질 지표는 저장된 480개 score row에서 읽는다. 전체 1,920 metric cell 가운데 1,915개가 값으로 저장되어 있고, faithfulness의 5개 빈 명제 집합은 결측 상태를 유지한다. HyDE의 주 비교는 CAD OFF·SCD OFF의 60 대응쌍이다. CAD의 주 비교는 같은 검색 문맥을 가진 대응쌍이며, faithfulness만 58개 완결쌍을 사용한다. SCD는 동일 query·HyDE·CAD에서 SCD OFF와 ON의 한국어 문자 비율을 비교한다.

평균 차이는 ON-OFF로 계산한다. 각 품질 지표와 SCD 문자 비율은 query 단위 재표집으로 95% bootstrap 신뢰구간을 산출한다. Win, loss, tie는 품질 지표에서 +0.01 초과, -0.01 미만, 그 사이로 나누어 기록한다. 이 기준은 평균 하나만으로 질의별 방향 차이를 감추지 않기 위한 보조 정보다.

[스타일=본문]

60개 질의 집합의 설계 단위는 “일반 상식 질문”이 아니라 특정 영어 학술문서에 답변 근거가 존재하는 한국어 질의-대상문서 쌍이다. 문서별로 15개를 배정한 이유는 하나의 문서에서만 잘 작동하는 configuration이 전체 평균을 지배하는 것을 줄이기 위해서다. 질의는 개념 정의, 방법의 목적, 절차·구성 요소, 비교 기준, 결과 해석처럼 서로 다른 질문 유형을 포함한다. 각 항목에는 query ID와 대상 문서뿐 아니라 source page, answerable 상태, answer span 관련 정보가 보존된다. 이 메타데이터는 질문을 사후에 결과에 맞춰 제외하거나 다른 문서의 답을 섞지 않았는지 확인하는 기준이 된다. 다만 4개 문서가 학술 문서의 모든 장르를 대표하지는 않으므로, 균등 배정은 표본 내 균형을 위한 선택이지 외적 대표성을 보장하는 표본추출은 아니다.

[스타일=본문]

각 query는 HyDE(H), CAD(C), SCD(S)의 ON/OFF 조합 여덟 개에서 생성된다. H0C0S0은 고정 backbone의 비교 기준점이며, H1C0S0은 검색 표현 확장을 포함한 HyDE pipeline의 효과를, H0C1S0은 같은 검색 입력 아래 CAD decoding의 효과를, SCD ON 조건들은 출력 언어 제어의 효과를 관찰하는 데 사용된다. 이 조합 표기는 세 기법을 하나의 덩어리로 취급하지 않게 한다. 예를 들어 H1C1S1의 score가 한 항목에서 높더라도, 그것은 세 요인을 동시에 바꾼 configuration의 상태이지 각 요인의 독립 효과 세 개를 더한 값이 아니다. 본문은 configuration table과 pairwise contrast table을 별도로 두어 이 두 독해 방식을 섞지 않는다.

[스타일=본문]

대응쌍을 만들 때의 핵심 키는 query ID다. HyDE primary는 동일 query의 H1C0S0과 H0C0S0을 연결한다. 이때 contexts가 달라질 수 있는 것은 설계상 허용되며, 오히려 HyDE가 검색 표현을 바꾼 결과의 일부다. CAD primary는 동일 query의 H0C1S0과 H0C0S0을 연결하되, stored contexts와 retrieved·reranked chunk ID가 모두 같은지 확인한다. 이 추가 조건이 충족되지 않으면 CAD의 decoder contrast에 포함하지 않는다. SCD direct pair는 query와 H·C 상태를 고정하고 S만 바꾼다. HyDE OFF subset에서는 context·ID 동일성을 다시 확인해, SCD의 언어 변화가 input 차이와 혼동되지 않도록 한다. 이러한 대응 규칙은 분석 후 수치가 잘 나오는 행만 선택하기 위한 규칙이 아니라, 각 연구 질문에서 무엇을 고정해야 하는지를 미리 정의한 contract다.

[스타일=본문]

품질 평가는 generation 결과를 새로 만들지 않고 저장된 evaluation artifact에서 읽는다. Faithfulness, answer relevancy, context precision, context recall은 서로 다른 분모와 실패 양식을 갖는다. Faithfulness는 생성 답변에서 추출된 claim과 context의 지지 관계를 평가하므로, 어떤 answer에서는 검토 가능한 claim이 추출되지 않아 빈 명제 집합이 남을 수 있다. 본 결과의 다섯 경우가 이에 해당한다. 이 record를 0점으로 치환하면 “낮은 점수를 받은 claim”과 “평가할 claim이 기록되지 않은 상태”를 혼동하게 되고, 임의의 최고점으로 치환하면 반대 방향의 왜곡이 생긴다. 그래서 원본 결측을 유지하고, 비교표에서 metric마다 유효 n을 적는다. 이 처리 방식은 평균의 외관보다 평가 artifact의 의미 보존을 우선한다.

[스타일=본문]

paired bootstrap은 configuration별 평균의 차이를 계산하는 절차와 다르다. 먼저 각 query i에 대해 d_i = score_ON,i - score_OFF,i를 구한다. 그 다음 60개 또는 해당 metric의 유효 query를 복원추출해 평균(d_i)을 반복 계산하고, 생성된 평균 분포의 2.5와 97.5 백분위를 95% interval로 사용한다. 같은 query의 두 조건을 함께 재표집하므로, 질문 난이도·문서의 서술 밀도·정답 범위처럼 양쪽 조건에 공통인 요소가 차이에 미치는 영향을 줄일 수 있다. 이 interval은 다른 corpus 전체에 대한 보편적 신뢰구간이나 사람 평가와의 일치도를 의미하지 않는다. 본 고정 60-query 표본에서 direction과 변동성을 읽기 위한 조건부 요약이다.

[스타일=본문]

win/loss/tie 집계는 bootstrap interval을 대체하지 않는 질의 수준 보조 분석이다. 품질 지표에서 +0.01보다 큰 차이를 win, -0.01보다 작은 차이를 loss로 두고 그 사이를 tie로 둔 것은 매우 작은 자동 judge 변동을 극적인 개선·악화로 읽지 않기 위해서다. SCD ratio에는 ±0.02 band를 사용해 문자 몇 개의 차이와 언어 성향의 눈에 띄는 이동을 구분한다. band의 선택이 완전히 값 중립적인 것은 아니므로, 본문은 raw mean과 interval을 먼저 제시하고 win/loss/tie를 그 해석을 보완하는 분포 정보로만 사용한다. 독자는 보조 집계가 어떤 threshold에 의존하는지 알 수 있고, 필요하면 raw artifact를 이용해 다른 practical threshold로 다시 집계할 수 있다.

[스타일=본문]

정량 결과와 사례 화면의 연결도 사전에 정한 selector로 관리한다. normal QA는 실제 저장 score와 context를 보여 주는 record, HyDE는 retrieval ID 변화가 있는 record, CAD는 input identity assertion을 통과한 positive와 trade-off record, SCD는 same-context language rescue record를 대상으로 한다. 화면을 만들 때 answer 원문을 고치거나 새로운 요약 답을 생성하지 않는다. 표시 공간 때문에 긴 문자열을 줄일 경우에만 원문 앞부분을 그대로 보이고 `[truncated]` 표기를 사용한다. 이 원칙은 사례가 평균을 가장 잘 지지하도록 편집된 데모가 되는 것을 막고, 독자가 raw replay output으로 돌아가 화면의 내용을 검증할 수 있게 한다.

## 5.3 RAG-Cube 조합별 결과 [스타일=절제목]

표 5-2는 여덟 configuration의 평균 품질과 Korean ratio를 보여준다. Faithfulness가 가장 높은 조건은 H1C1S0(0.8599), answer relevancy가 가장 높은 조건은 H1C0S0(0.7633), context precision이 가장 높은 조건은 H0C0S1(0.7634)이다. Context recall은 H0C0S0과 H1C0S0이 0.9333으로 같고, Korean ratio는 H1C0S1이 0.8072로 가장 높다. 지표별 최고 조건이 달라 하나의 configuration을 전역적으로 우선하는 방식으로 해석하지 않는다.

[표 5-2] 8개 configuration 평균 품질 [스타일=표제목]

`tables_60q_csv/T5-2_Config_Scores.csv`

![8개 configuration 품질 행렬](figures_60q/fig5_1_quality_matrix.png)

[그림 5-1] RAG-Cube 8개 조건의 평균 품질 지표. 셀 값은 저장된 RAGAS score의 configuration별 평균이다. [스타일=그림제목]

## 5.4 HyDE 결과 및 해석 [스타일=절제목]

HyDE의 주 비교에서 answer relevancy 평균 변화는 +0.0805이고 95% CI는 [+0.0110, +0.1514]다. 60개 대응 질의에서 win/loss/tie는 29/15/16이며, 이 값은 본 연구에서 가장 명확한 HyDE 관련 결과다. Faithfulness 평균 변화는 +0.0436이고 CI는 [-0.0262, +0.1153]이며 win/loss/tie는 24/21/15다. Context precision은 -0.0343, context recall은 0.0000이고 context recall은 52개 질의가 tie에 해당한다.

따라서 HyDE를 적용한 검색 표현 확장은 answer-level 관련성과 연결되는 양의 평균 변화를 보였으나, retrieval과 answer의 모든 측정값이 같은 방향으로 움직였다고 해석할 수는 없다. 검색 ID가 실제로 바뀐 저장 사례에서는 HyDE OFF 답변이 BIC 활용 정보를 찾지 못한 반면 HyDE ON 답변은 최적 cluster 수 선택을 설명했다. 이 사례는 평균의 원인을 일반화하는 증거가 아니라, retrieval change와 answer-level 결과를 함께 확인하는 provenance 사례다.

[표 5-3] HyDE primary 통제 비교 [스타일=표제목]

`tables_60q_csv/T5-3_HyDE.csv`

![HyDE CAD forest](figures_60q/fig5_2_primary_forest.png)

[그림 5-2] HyDE와 CAD의 통제 비교. 점은 ON-OFF 평균 차이, 선은 95% bootstrap 신뢰구간이다. [스타일=그림제목]

[그림삽입: FINALDOCS/EVIDENCE/UI_REPLAY/E04_hyde_retrieval_change.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-3] 기존 evidence replay UI가 표시한 HyDE OFF·ON 저장 응답 사례. query ID, configuration, 저장 점수와 answer excerpt는 60-query artifact에서 read-only로 재현한다. [스타일=그림제목]

## 5.5 CAD 결과 및 해석 [스타일=절제목]

CAD의 주 비교는 검색 문맥을 동일하게 유지하고 decoding만 달리한 대응쌍이다. Faithfulness는 완결된 58쌍에서 평균 +0.0288, 95% CI [-0.0367, +0.0934], win/loss/tie 21/24/13이다. Answer relevancy는 60쌍에서 -0.0073, CI [-0.0855, +0.0719], win/loss/tie 19/32/9이다. Context precision은 -0.0092, context recall은 -0.0167이며, context recall은 59개 질의가 tie다.

이 결과는 CAD의 문맥 기반 logit 조절을 하나의 공통 품질 순위로 요약하기보다, 지표별 방향과 실제 응답을 함께 검토하게 한다. H1C1S0은 configuration 평균 faithfulness가 가장 높으며, HyDE ON strata에서는 faithfulness와 context precision이 양의 방향을 보이는 pattern이 있다. 반면 동일 문맥 사례에는 CAD ON에서 faithfulness가 커진 경우와 작은 경우가 모두 저장되어 있다. 이 변동은 CAD의 비교를 조건별 trade-off와 응답 근거의 관점에서 해석하게 한다.

[표 5-4] CAD primary 동일 문맥 비교 [스타일=표제목]

`tables_60q_csv/T5-4_CAD.csv`

[그림삽입: FINALDOCS/EVIDENCE/UI_REPLAY/E05_cad_positive_same_context.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-4] 기존 evidence replay UI가 표시한 동일 문맥 CAD positive 사례. retrieval·rerank ID와 contexts의 동일성은 화면에서 확인한다. [스타일=그림제목]

## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절제목]

SCD의 직접 목적은 영어 근거 문맥에서 한국어 출력 언어를 유지하는 것이다. 240 ON/OFF 대응쌍의 한국어 문자 비율 평균 변화는 +0.2289이고 95% CI는 [+0.2051, +0.2532]다. +0.02를 초과한 증가는 219개, -0.02보다 작은 감소는 10개, 그 사이 동률은 11개다. HyDE OFF에서 contexts·retrieved ID·reranked ID가 같은 120쌍에서도 평균 변화는 +0.2182, 95% CI는 [+0.1880, +0.2487]이다.

네 HyDE·CAD strata에서 SCD ON-OFF 평균 변화는 각각 +0.2047, +0.2317, +0.2511, +0.2283이다. 따라서 SCD는 output-language control이라는 직접 목표에서 안정적인 방향의 차이를 보인다. 이 수치는 faithfulness나 answer relevancy 같은 일반 RAG 품질 지표의 변화를 뜻하지 않으며, 문자 비율이 문법성·근거 정확성·전문용어 선택을 모두 대체하는 지표도 아니다.

[표 5-5] SCD configuration별 language result [스타일=표제목]

`tables_60q_csv/T5-5_SCD_Config.csv`

[표 5-6] SCD matched-pair summary [스타일=표제목]

`tables_60q_csv/T5-6_SCD_Paired.csv`

![SCD language adherence](figures_60q/fig5_3_scd_language.png)

[그림 5-5] HyDE·CAD strata별 SCD 적용에 따른 한국어 문자 비율 변화. 오차막대는 95% bootstrap 신뢰구간이다. [스타일=그림제목]

[그림삽입: FINALDOCS/EVIDENCE/UI_REPLAY/E03_scd_rescue.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-6] 기존 evidence replay UI가 표시한 동일 문맥 SCD OFF·ON 저장 응답 사례. 원문 answer excerpt와 점수는 변경하지 않는다. [스타일=그림제목]

## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절제목]

정상 QA 사례는 저장된 query ID `ext_raptor_011`에서 H0C0S0 답변과 RAGAS score를 재현한다. HyDE 사례는 `ext_raptor_004`, SCD 언어 사례는 UI selector가 동일 input rescue 조건으로 선택한 record, CAD 사례는 input identity를 assertion으로 확인한 selected pair를 사용한다. 그림의 answer text는 저장 record를 새로 작성하지 않고 display-only truncation 표시만 사용한다. 전체 UI replay 원문은 `FINALDOCS/EVIDENCE/UI_REPLAY/raw/`에 보존한다.

[그림삽입: FINALDOCS/EVIDENCE/UI_REPLAY/E01_normal_qa.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-7] 기존 evidence replay UI가 표시한 정상 QA 저장 응답 사례. 답변과 score는 저장된 generation·evaluation artifact에서 재현한다. [스타일=그림제목]

## 5.8 종합 논의 [스타일=절제목]

세 요인은 서로 다른 단계와 목표를 가진다. HyDE는 검색 표현을 확장하며 주 비교에서 answer relevancy의 양의 평균 변화와 연결된다. CAD는 같은 검색 문맥에서 생성 분포를 조절하며, faithfulness는 양의 평균 방향을 보이나 query별 변화와 신뢰구간을 함께 해석해야 한다. SCD는 답변 언어 유지라는 직접 측정값에서 가장 일관된 차이를 보인다. 따라서 H/C/S를 모두 ON으로 두는 방식이 모든 목적에 최적인 조합이라는 결론을 사용하지 않는다.

## 5.9 연구의 한계 [스타일=절제목]

본 연구는 네 문서와 60개의 한국어 질의-대상문서 쌍에 범위를 둔다. 품질 지표는 LLM-as-a-judge 기반 RAGAS protocol에 의존하며, faithfulness의 빈 명제 집합 다섯 건은 결측값으로 보존한다. 한국어 문자 비율은 출력 언어 성향을 수치화하지만 자연스러움과 내용의 정확성을 단독으로 판정하지 않는다. 향후에는 독립 도메인·문서 형식·질의 작성자를 늘리고, 사람의 blind evaluation과 다양한 generator·tokenizer 조건을 추가해 결과의 외적 타당성을 검토할 수 있다.

[스타일=본문]

60개 질의 집합은 네 문서에 각각 15개씩 배정된 질의-대상문서 쌍으로 구성한다. 각 query는 고유 ID, 한국어 질문, 대상 paper, 질문 유형, source page와 answer span 상태를 갖는다. 이 정보는 부록 A의 query audit에서 전체 목록으로 확인한다. 문서별 질의 수가 같기 때문에 전체 평균이 특정 문서의 다수 샘플에 의해 일방적으로 결정되는 구조는 피했지만, 네 문서만으로 분야 전체의 일반성을 주장하지는 않는다. 문서별·질문 유형별 세부 집계는 본문 핵심 결론이 아닌 탐색 결과로 부록과 CSV에 분리한다.

[스타일=본문]

480개 generation record와 1,920개 RAGAS metric cell을 확인했을 때, 1,915개 cell에는 값이 있고 faithfulness의 5개 cell은 원본 평가에서 빈 명제 집합으로 기록되었다. 이 다섯 값을 0 또는 다른 값으로 대치하지 않았다. 그 결과 faithfulness에 관한 CAD primary 비교는 양쪽 값이 모두 존재하는 58쌍을 사용하고, answer relevancy 등 값이 완결된 지표는 60쌍을 사용한다. 표본 수의 차이는 불편한 예외가 아니라, 분석이 원본 evaluation 상태를 보존했음을 보여 주는 정보다. 표와 캡션에서도 n을 함께 표시해 서로 다른 지표의 paired count를 혼동하지 않도록 한다.

[스타일=본문]

RAG-Cube configuration 평균은 어떤 조건이 모든 목적에 가장 좋다는 판정을 제공하지 않는다. H1C1S0은 faithfulness 0.8599로 가장 높았고, H1C0S0은 answer relevancy 0.7633으로 가장 높았다. Context precision의 최고값 0.7634는 H0C0S1에서, context recall의 최고값 0.9333은 H0C0S0과 H1C0S0에서 나타났다. Korean ratio는 H1C0S1이 0.8072로 가장 높았다. 이러한 분산은 하나의 조건을 '최종 최고 성능'이라고 부르는 대신, 사용자가 문서 기반성·질문 관련성·문맥 구성·한국어 출력 중 무엇을 우선하는지에 따라 configuration을 선택해야 함을 뜻한다.

[스타일=본문]

HyDE의 primary comparison은 CAD OFF·SCD OFF에서 H1C0S0과 H0C0S0을 같은 60 query ID로 대응시킨다. answer relevancy의 ON-OFF 평균 차이는 +0.0805이고, 95% bootstrap CI는 [+0.0110, +0.1514]이며, practical win/loss/tie는 29/15/16이다. 이 값은 해당 통제 범위에서 HyDE pipeline과 answer-level 질문 적합성의 양의 평균 변화가 함께 관찰되었다는 의미다. 그러나 faithfulness는 +0.0436, CI [-0.0262, +0.1153]이고 24/21/15의 이질적인 방향을 보였다. 따라서 HyDE가 모든 질의에서 또는 모든 품질 지표에서 향상된다고 일반화하지 않는다.

[스타일=본문]

HyDE의 context precision 평균 변화는 -0.0343이고 context recall은 0.0000이다. 특히 context recall은 60개 중 52개가 tie이므로, 이 데이터에서 HyDE의 가장 뚜렷한 관찰은 recall 전반의 이동이 아니라 answer relevancy의 paired contrast다. 실제 replay 사례 `ext_raptor_004`에서는 H0가 BIC의 역할을 확인하지 못했지만 H1은 최적 cluster 수 선택이라는 내용을 답했다. 화면에는 두 configuration의 retrieved IDs와 reranked IDs가 서로 다름이 표시된다. 이 사례는 평균 효과의 원인을 증명하는 독립 표본이 아니라, HyDE가 검색 입력을 바꾼다는 설계상의 의미를 원자료로 확인하는 사례다.

[스타일=본문]

CAD의 primary comparison은 H0C1S0과 H0C0S0 사이에서 contexts·retrieved IDs·reranked IDs가 동일한 기록을 사용한다. faithfulness의 평균 차이는 완결된 58쌍에서 +0.0288, CI [-0.0367, +0.0934], win/loss/tie는 21/24/13이다. answer relevancy는 60쌍에서 -0.0073, CI [-0.0855, +0.0719], win/loss/tie는 19/32/9이다. confidence interval이 0을 포함하고 query별 방향도 한쪽으로 정렬되지 않았으므로, 이 주 비교만으로 CAD의 독립적 평균 품질 향상을 확정하지 않는다. 같은 입력에서 일부 답변이 개선되고 일부 답변이 짧아지거나 질문을 놓치는 현상은 모두 실제 record로 남아 있다.

[스타일=본문]

CAD는 configuration 평균에서 조건 의존적인 패턴도 보인다. H1C1S0은 8개 configuration 중 faithfulness가 가장 높고, HyDE ON strata에서 CAD 추가 시 faithfulness와 context precision이 양의 방향을 보이는 조합이 있다. 하지만 이 조합별 관찰은 HyDE가 retrieval을 바꿀 수 있는 경우를 포함하므로, 동일 문맥 CAD primary conclusion과 같은 강도로 읽지 않는다. 또한 CAD ON은 context/no-context branch를 모두 계산하므로 실행 시간 증가를 동반한다. 결과를 사용자가 채택할 때에는 작은 평균 차이와 query별 변동, 문맥 일치 여부, 시간 비용을 모두 함께 고려해야 한다.

[스타일=본문]

두 CAD 사례를 read-only UI에서 같이 제시한 이유도 평균의 양쪽 가능성을 숨기지 않기 위해서다. `ext_raptor_001`의 stored pair는 inputs가 같고 CAD ON에서 faithfulness가 0.2500에서 1.0000으로 변한 positive example이다. 반대로 `track1_0012`의 stored pair는 동일 input에서 CAD ON answer가 짧은 형태로 남아 faithfulness가 0.9375에서 0.5000으로 변한 trade-off example이다. 두 사례는 어느 하나가 CAD의 일반 효과를 결정한다는 뜻이 아니라, primary 평균의 넓은 불확실성과 질의별 변동을 사람이 읽을 수 있는 입력-출력 경로로 보여 준다.

[스타일=본문]

SCD의 직접 분석은 같은 query·HyDE·CAD 조건에서 SCD OFF와 ON을 대응시킨 240쌍을 사용한다. Korean-character ratio의 평균 변화는 +0.2289, CI는 [+0.2051, +0.2532]이고, +0.02를 초과한 증가는 219개, -0.02보다 작은 감소는 10개, 그 사이 동률은 11개다. 네 HyDE·CAD strata에서도 평균 변화는 각각 +0.2047, +0.2317, +0.2511, +0.2283으로 모두 양수다. 이는 특정 HyDE·CAD 조합 하나에만 국한되지 않는 output-language control의 패턴을 보여 준다.

[스타일=본문]

SCD 결과를 검색 변화와 분리해 보기 위해 HyDE OFF의 동일 contexts·retrieved IDs·reranked IDs 120쌍도 별도로 확인했다. 이 subset의 평균 Korean-character ratio 변화는 +0.2182, CI는 [+0.1880, +0.2487]이다. 즉 이 분석 범위에서는 retrieval input이 같아도 SCD ON/OFF의 출력 언어 성향이 달라진다. `ext_midm_005` replay 사례에서는 SCD OFF answer의 ratio가 0.0000이고 SCD ON answer의 ratio가 0.7713이며, 화면에 두 configuration의 input identity가 True로 표시된다. 다만 이 사례의 언어 비율 변화가 모든 문장의 문법성 또는 내용 품질을 보증하는 것은 아니다.

[스타일=본문]

대표 입출력의 검토는 정량 결과를 장식하기 위한 별도 예시가 아니다. normal QA 화면은 높은 저장 RAGAS 점수를 가진 record의 질문·답변·retrieved chunk와 evidence excerpt를 함께 보이고, language-drift 화면은 SCD OFF에서 실제로 영어 응답이 저장된 row를 보여 준다. HyDE 화면은 검색 ID가 달라진 pair를, CAD 화면은 입력이 같은 pair를, SCD 화면은 언어 rescue pair를 보여 준다. 각각의 화면은 `cli/evidence_replay.py`가 60-query generation·merged score artifact를 read-only로 해석한 결과다. 그림용으로 답변을 줄일 때도 원문 문자열을 바꾸지 않고 display-only truncation과 `[truncated]` 표지만 사용한다.

[스타일=본문]

종합하면 HyDE, CAD, SCD는 같은 층위의 선택지가 아니다. HyDE는 검색 표현을 넓혀 질문과 영어 학술문장의 간격을 줄이는 역할을 하며, 이 실험에서는 answer relevancy의 양의 paired contrast가 가장 명확하다. CAD는 주어진 문맥을 generation에서 더 반영하려는 방법이지만, 동일 문맥 comparison의 신뢰구간과 사례는 일률적 개선보다 조건별 변동을 보여 준다. SCD는 한국어 출력 유지라는 직접 측정값에서 가장 안정적인 방향을 보인다. 따라서 조합을 선택할 때는 하나의 합성 점수나 세 요인을 모두 ON으로 둔 설정이 아니라, 사용 목적과 시간 비용, 언어 요구, 저장 provenance를 함께 고려해야 한다.

[스타일=본문]

본 실험에는 몇 가지 한계가 남는다. 첫째, 네 개 영어 문서와 60개 한국어 질의에 한정되어 있으므로 다른 전공·문서 구조·질문 작성자에게 그대로 일반화할 수 없다. 둘째, RAGAS는 고정된 judge protocol의 자동 평가이며 사람의 blind review를 대체하지 않는다. 셋째, faithfulness의 빈 명제 집합 다섯 건은 결측으로 보존되어 지표별 표본 수가 다르다. 넷째, Korean-character ratio는 language adherence의 직접 지표일 뿐 answer correctness, citation completeness, readability의 전체 척도가 아니다. 다섯째, CAD와 SCD의 decoding 특성은 generator와 tokenizer에 의존할 수 있다. 이후 연구에서는 독립 문서 집합, 사람 평가, 다른 generator, 더 긴 문서와 다양한 문체를 포함한 반복이 필요하다.

[스타일=본문]

결과표를 읽을 때 configuration 평균과 paired result를 구분하는 것은 특히 중요하다. configuration 평균은 해당 조건에서 60개 질문이 만든 상태를 요약하지만, 두 configuration 사이에 무엇이 고정되어 있는지는 따로 말해 주지 않는다. HyDE ON/OFF는 검색 표현을 달리하므로 context가 바뀔 수 있고, CAD ON/OFF는 주 comparison에서 context를 고정해 decoder 차이를 본다. 두 결과 모두 유용하지만 같은 종류의 효과 크기라고 볼 수는 없다. 본문은 표 5-2를 조합 선택의 지도, 표 5-3과 표 5-4를 제한된 통제 대비로 사용한다.

[스타일=본문]

answer relevancy의 변화는 답변이 질문의 요구에 얼마나 직접 반응하는지를 보여 주지만, 질문에 길게 반응하는 답변이 언제나 더 좋은 근거 활용을 뜻하지는 않는다. faithfulness는 반대로 문맥과 답변의 지지 관계에 주목하지만, 질문의 핵심을 충분히 다루지 않은 짧은 답변도 일부 상황에서 높은 값을 얻을 수 있다. context precision과 recall도 retrieval document의 선택을 보여 줄 뿐, 실제 생성 문장이 그 정보를 사용했는지 직접 말하지 않는다. 이 때문에 본 연구는 네 지표 사이의 불일치를 오류로 제거하지 않고, 각 configuration이 어느 지표에서 유리한지 그대로 표기한다.

[스타일=본문]

HyDE의 해석에서 중요한 것은 가상 문서가 정답 reference가 아니라는 점이다. H1 condition의 hypothetic document는 질문을 문서형 영어 표현으로 바꿔 dense search를 돕는 중간 산출물이다. 따라서 화면에서 H1 answer가 더 구체적이라고 보이더라도, 그 구체성이 실제 retrieved context와 연결되는지는 chunk ID와 evidence excerpt를 읽어 확인해야 한다. UI E04는 이러한 검토 순서를 보여 준다. 먼저 H0/H1의 IDs가 다른지 확인하고, 다음으로 각 answer의 저장 점수를 보고, 마지막으로 answer 내용과 첫 evidence를 비교한다. 이 순서는 임의의 사례를 평균 효과의 설명으로 과대해석하지 않도록 한다.

[스타일=본문]

CAD의 positive와 trade-off 사례를 함께 실은 이유도 같은 원칙에 따른다. positive 사례만 제시하면 CAD가 항상 문맥 활용을 개선한다는 인상을 주고, trade-off 사례만 제시하면 CAD가 항상 실패한다는 인상을 준다. 실제 60-query primary contrast는 win과 loss가 모두 존재하고 신뢰구간도 0을 포함한다. 두 UI 화면은 inputs가 같다는 전제를 먼저 표시하므로, 독자는 점수 변화가 검색 대상 교체가 아니라 decoding condition과 함께 발생했음을 확인할 수 있다. 사례 선택은 답변을 수정해 대비를 강화하는 방식이 아니라, stored pair 중 정해진 selector를 사용한다.

[스타일=본문]

SCD의 ratio 증가도 답변을 단순히 한국어 글자로 치환한 결과가 아니다. E03의 same-context pair는 contexts, retrieved IDs, reranked IDs가 모두 동일한 상태에서 SCD processor 적용 여부만 다르다. 화면에 남은 영어 문장, 고유명사, 수치, 논문명은 language drift로 즉시 분류하지 않는다. ratio는 한글과 ASCII alphabet의 상대적 비중을 보여 주는 지표이므로, 기술 문서에서 필요한 영어 표기가 있는 한국어 답변과 영어로 지속되는 답변을 완전히 구분하지는 못한다. 그러므로 사용자는 ratio와 함께 실제 answer excerpt를 읽어야 하며, 본문도 이를 일반 quality 점수로 해석하지 않는다.

[스타일=본문]

실행 시간은 CAD의 비용을 판단할 때 필요한 맥락이다. decoder가 context branch와 no-context branch를 함께 계산하면 동일한 max_new_tokens 조건에서도 한 token을 고르는 과정이 길어질 수 있다. 표 4-3과 그림 5-10은 condition별 평균과 중앙값을 제공해, 단일 평균이 극단적인 긴 answer에 영향을 받는지를 함께 보게 한다. 이 시간은 사용자 서비스의 end-to-end latency나 네트워크 지연을 의미하지 않고, 저장된 experiment generation duration이다. 따라서 논문은 CAD의 비용을 이 backbone과 실행 환경에서 관찰한 상대적 특성으로 제한한다.

[스타일=본문]

재현 절차는 재실행 절차와 다르다. 모델을 다시 로드해 generation을 반복하면 하드웨어, tokenizer, package version, provider 상태에 의해 새로운 변동이 생길 수 있다. 본 패키지의 우선 검증은 이미 저장된 source artifact에서 query 수·record 수·configuration 수·score 수·paired count·figure/table source hash를 대조하는 것이다. `verify_finaldocs_60q.py`는 최종 원고에 60-query 결과 marker가 있는지, workbook에 필요한 sheet가 있는지, 그림 수가 충분한지, 패키지 파일이 존재하는지를 확인한다. evidence replay UI 역시 이 검증 원칙에 따라 network, model, judge 호출 없이 동작한다.

[스타일=본문]

한글 이전 시 표와 그림은 본문을 대체하는 장식이 아니라 논증의 일부로 배치한다. 표 5-2 뒤에는 한 configuration이 모든 지표에서 최고가 아니라는 해설을 두고, 표 5-3 뒤에는 HyDE answer relevancy contrast와 다른 지표의 범위를 함께 설명한다. 표 5-4 뒤에는 CAD의 58쌍 faithfulness와 60쌍 answer relevancy라는 표본 수 차이를 명시한다. 표 5-5와 표 5-6 뒤에는 SCD의 direct language effect와 동일 input subset을 구분한다. UI 그림은 그 다음에 배치해 수치가 실제 저장 answer·context와 어떤 관계인지 읽게 한다.

[스타일=본문]

이러한 구성은 연구 결과의 설득력을 결과가 좋은 사례만으로 만들지 않는다. score가 낮거나 answer가 불완전한 화면도 selector와 저장 원문을 유지한 채 남긴다. 결과의 한계, 결측, 비용, 지표의 경계, 사례 간 변동을 함께 기록해야 60-query 확장이 단순한 표본 수 증가를 넘어 해석 가능한 실험 보고서가 된다. 본문과 부록의 역할도 이 원칙에 맞춘다. 본문은 연구 질문에 직접 답하는 비교와 해석을 제공하고, 부록은 60개 query 목록, raw UI output, 탐색 CSV, artifact SHA, 검증 명령을 제공한다.

## 5.10 연구 질문별 통합 해석과 적용 범위 [스타일=절제목]

[스타일=본문]

첫 번째 연구 질문은 한국어 질의와 영어 학술문서의 표현 간격을 HyDE가 완화하는지에 관한 것이다. 이 질문에 대한 본 연구의 답은 제한적이지만 긍정적이다. H1C0S0과 H0C0S0을 60개 query ID로 대응한 주 비교에서 answer relevancy는 +0.0805, 95% bootstrap CI는 [+0.0110, +0.1514]였다. interval의 하한이 0보다 크고, practical band를 기준으로도 29개가 증가·15개가 감소·16개가 동률인 분포는 이 고정 pipeline에서 질문 적합성이 한 방향으로 이동했음을 뒷받침한다. 그렇다고 해서 HyDE가 “검색 성능을 0.0805 향상한다”는 결론은 아니다. 이 차이는 retrieval-only metric이 아니라 영어 검색 표현, hypothetical document, hybrid candidate, reranking, 그리고 그 문맥을 이용한 최종 answer를 모두 포함한 answer-level 결과다.

[스타일=본문]

HyDE 결과에서 faithfulness와 context 지표가 answer relevancy와 동일한 모양을 보이지 않는 점은 부정적인 부록이 아니라 핵심 해석 근거다. Faithfulness의 평균은 양수였지만 신뢰구간이 0을 포함했고, context precision은 음의 평균, context recall은 거의 이동하지 않았다. 만약 모든 지표가 같은 크기와 방향으로 움직였다면 검색·생성·judge가 하나의 단일 특성을 측정한다는 잘못된 인상을 줄 수 있다. 실제로 answer relevancy는 질문을 직접 다루는 정도를, context precision과 recall은 선택된 근거의 구성을, faithfulness는 answer claim과 context의 관계를 관찰한다. HyDE는 질문에 가까운 답을 구성하도록 검색 표현을 바꾸었을 수 있지만, 그 과정이 모든 문맥 지표를 동시에 개선해야 할 논리적 이유는 없다. 따라서 본 연구는 HyDE의 적용 판단에서 answer relevancy를 주된 관찰로 제시하되, 다른 지표의 불일치를 함께 공개한다.

[스타일=본문]

두 번째 연구 질문은 CAD가 같은 검색 근거 아래에서 문맥 기반 답변을 일관되게 개선하는지에 관한 것이다. 여기서는 확정적 개선이라는 답을 제시하지 않는다. 58개 완결 faithfulness pair의 평균 차이 +0.0288과 60개 answer relevancy pair의 평균 차이 -0.0073은 방향 자체가 지표에 따라 다르며, 두 95% interval 모두 0을 포함한다. win/loss/tie도 faithfulness 21/24/13, answer relevancy 19/32/9로 한쪽 방향에 압도적으로 모이지 않는다. 이 결과는 CAD가 무의미하다는 판정이 아니라, fixed alpha=0.5와 이 generator·질의 집합에서 CAD의 효과가 query·answer 형식·문맥 구성에 따라 달라질 수 있다는 증거다. 특히 CAD는 retrieval을 고정한 비교이므로, 이 불확실성을 HyDE의 search-side 변화로 설명해 버릴 수 없다.

[스타일=본문]

CAD의 해석에는 configuration 최고값과 통제 비교를 의도적으로 분리해야 한다. H1C1S0이 faithfulness 평균의 최고 configuration이라는 사실은 해당 여덟 조합 중 하나의 요약값이다. 그러나 H1 조건에는 HyDE에 의한 검색 변화가 포함될 수 있으므로, 그것만으로 CAD의 독립 효과를 판정할 수 없다. 반면 CAD primary pair는 문맥·retrieved ID·reranked ID가 동일한 record를 대조해 decoder 변화만을 읽으려 한다. 이 논문은 두 결과를 서로 모순으로 보지 않는다. 전자는 사용자가 실제 조합을 선택할 때 참고할 구성 수준의 지도이고, 후자는 한 요인의 인과적 범위를 좁히는 통제 분석이다. 독자는 구성 평균이 높다는 이유만으로 CAD를 항상 켜야 한다고 결론 내리지 않고, 요청되는 답변의 성격·허용 가능한 지연·해당 도메인의 validation 결과를 함께 봐야 한다.

[스타일=본문]

세 번째 연구 질문은 SCD가 영어 근거가 들어오는 조건에서도 한국어 출력 성향을 유지하는지에 관한 것이다. 240 matched pair 전체에서 +0.2289, 신뢰구간 [+0.2051, +0.2532]이라는 결과와 네 strata 모두 양수인 변화는 이 직접 목표에 관해 가장 강한 근거다. HyDE OFF에서 input identity를 별도로 확인한 120쌍에서도 +0.2182가 나타난 점은, 적어도 그 subset에서 관찰된 변화가 retrieved passage의 교체만으로 생긴 것이 아니라 SCD 적용 여부와 연결된다는 해석을 강화한다. 그러나 Korean-character ratio의 정의는 철저히 표면적이다. 한글 비율이 높아도 문장이 부자연스럽거나 근거를 오독할 수 있고, 한글 비율이 낮아도 인용문·고유명사·수식 때문에 필요한 영어가 포함될 수 있다. 따라서 SCD의 결론은 ‘한국어 출력 성향을 높였다’까지이며, ‘전체 답변 품질을 향상했다’가 아니다.

[스타일=본문]

네 번째 연구 질문은 H·C·S 조합 중 보편적으로 최적인 설정이 존재하는지에 관한 것이다. 표 5-2의 최고값이 서로 다른 configuration에 분산된 것은 부정적 결과가 아니라 RAG system selection이 다목적 문제임을 보여 준다. faithfulness, answer relevancy, context precision, context recall, Korean ratio는 서로 다른 실패 양식에 민감하다. 이를 가중치가 알려지지 않은 하나의 합산 점수로 바꾸면 사용 목적을 숨기고, 가중치 선택 자체가 결론을 좌우할 수 있다. 본 연구는 그런 합산 점수를 만들지 않았다. 대신 어떤 조건이 어떤 지표에서 최고였는지, HyDE와 CAD의 주 비교가 무엇을 고정했는지, SCD가 무엇을 직접 측정했는지를 분리해 제시한다. 이 선택은 ‘단일 우승 configuration’보다 사용자가 자신의 제약을 드러내고 선택하게 하는 더 정직한 결과 형식이다.

[스타일=본문]

실제 배치 관점에서 보면, 본 결과는 세 가지 확인 절차로 번역할 수 있다. 첫째, 사용자가 한국어로 묻지만 문서가 영어 논문인 시스템에서 질문 적합성을 우선한다면, 해당 corpus와 질의 유형에서 HyDE ON/OFF의 retrieved IDs와 answer relevancy를 먼저 재검토한다. 둘째, 이미 확보한 문맥에서 근거 기반 표현을 조절하려 한다면, CAD를 전역 default로 고정하기 전에 동일 context paired test와 generation duration을 확인한다. 셋째, 한국어 대화 경험이 요구사항이라면, SCD의 ratio뿐 아니라 실제 answer의 용어·고유명사·인용문을 사람이 읽어 언어 적합성을 점검한다. 이 세 절차는 본 실험의 값을 다른 서비스에 그대로 복사하는 recipe가 아니라, 각 기법이 작동하는 층위에 맞게 검증을 설계하는 방법이다.

[스타일=본문]

내적 타당성의 위협도 함께 검토할 필요가 있다. HyDE 비교에서는 검색 결과가 달라질 수 있으므로, answer 차이를 hypothetical document 하나의 효과라고 단정할 수 없다. CAD 비교는 입력 동일성을 확인하지만 fixed alpha 하나만 사용했으므로, 다른 alpha에서의 결과를 알 수 없다. SCD 비교는 동일 record를 강하게 통제하지만, 문자 비율이 사용자 선호와 완전히 일치하지 않는다. 또한 RAGAS score는 자동 judge의 판단이고, 질문 작성자·문서 선택·answer span의 범위는 결과에 영향을 줄 수 있다. 본 연구가 record 단위 provenance와 UI replay를 보존한 이유는 이러한 위협을 없애기 위해서가 아니라, 독자가 어떤 위협이 어느 결론에 영향을 주는지를 확인할 수 있게 하기 위해서다.

[스타일=본문]

결국 60-query 확장의 의의는 19개 결과를 단순히 더 많은 수로 치환한 데 있지 않다. 네 문서에 균등하게 배정된 60개 실제 한국어 질문, 여덟 조합의 완전한 generation record, 1,915개의 저장된 metric cell, 지표별 결측 상태, paired comparison, 그리고 read-only UI replay를 하나의 논증 구조로 연결했다는 데 있다. 이는 표본 수가 유한한 응용 연구에서 요구되는 최소한의 투명성을 제공한다. 다음 장은 이 결과를 다시 숫자만으로 요약하지 않고, 연구 질문에 대한 답·학술적 및 실무적 기여·제약·후속 연구의 순서로 종합한다.

# 6. 결론 [스타일=장제목]

## 6.1 연구 질문에 대한 답 [스타일=절제목]

본 연구는 한국어 질의 기반 영어 학술문서 RAG에서 HyDE, CAD, SCD를 독립 이진 요인으로 구성한 RAG-Cube 조합 실험을 수행했다. 4개 문서와 60개 질의-대상문서 쌍, 8개 configuration, 480개 저장 generation record를 사용했다. HyDE의 주 비교에서 answer relevancy는 +0.0805였고, CAD의 동일 문맥 비교에서 faithfulness는 58 완결쌍에서 +0.0288이었다. SCD는 240 대응쌍에서 한국어 문자 비율을 +0.2289 높였으며, HyDE OFF 동일 문맥 120쌍에서도 +0.2182의 변화를 보였다.

## 6.2 학술적 기여와 해석의 경계 [스타일=절제목]

이 결과는 기법별 목표와 지표별 결과를 구분해 적용하는 근거를 제공한다. HyDE·CAD·SCD의 조합은 단일 성능 순위가 아니라 검색 관련성, 근거 충실도, 출력 언어 유지라는 서로 다른 목적에 대한 configuration별 선택 문제로 다룰 수 있다. 저장된 query, context, retrieval ID, answer, score와 artifact hash를 함께 제공함으로써 본문의 수치와 실제 사례를 다시 대조할 수 있도록 구성했다.

[스타일=본문]

본 연구의 결론은 세 방법이 동일한 종류의 개선을 제공한다는 주장이 아니다. HyDE의 +0.0805 answer relevancy contrast는 검색 표현 확장이 질문 적합성에 연결될 수 있음을, CAD의 +0.0288 faithfulness 평균과 0을 포함하는 interval은 동일 문맥에서의 결과가 질의별로 달라짐을, SCD의 +0.2289 Korean-character ratio contrast는 목표 언어 유지라는 직접 목표에서 안정적인 변화를 보여 준다. 이 세 관찰은 서로 대체할 수 없고, 한 값을 다른 값의 증거로 사용하지 않는다.

[스타일=본문]

## 6.3 시스템 선택에 대한 함의 [스타일=절제목]

실무적 선택도 이 구분을 따른다. 질문과 영어 문서 표현의 간격이 큰 경우에는 HyDE의 retrieval-side 확장을 우선 검토할 수 있다. 이미 확보한 근거를 generation에서 더 강하게 반영하려는 경우에는 동일 context에서의 CAD 변동과 시간 비용을 함께 확인해야 한다. 한국어 답변을 유지해야 하는 경우에는 SCD의 언어 지표를 직접 확인할 수 있다. 그러나 이 선택들은 이 연구의 네 문서·60 query 범위를 넘는 보편적 규칙이 아니라, 저장된 configuration별 결과를 읽는 의사결정 틀이다.

[스타일=본문]

## 6.4 재현 가능한 연구 산출물의 기여 [스타일=절제목]

재현 가능성 측면에서 본 보고서는 최종 수치와 사례를 분리하지 않았다. query audit, 두 generation JSONL, 두 merged score JSON, 60-query analysis, Excel workbook, figure source, UI replay output과 validation manifest가 같은 `FINALDOCS` 구조로 연결된다. reader는 표의 평균을 보고 끝내지 않고, 특정 query ID에서 context가 같은지, retrieval IDs가 바뀌었는지, answer와 score가 어떤 configuration에 속하는지 확인할 수 있다. 이 연결은 새로운 모델 실행이 아니라 이미 저장된 연구 결과에 대한 검토 가능성을 제공한다.

[스타일=본문]

## 6.5 한계와 후속 연구 [스타일=절제목]

향후 연구에서는 서로 다른 전공의 논문, 더 많은 질의 작성자, 장문·표·수식이 많은 문서, 다른 generator 및 tokenizer에서 같은 비교를 반복할 필요가 있다. 특히 SCD의 언어 비율을 사람의 언어 적합성 판단과 연결하고, CAD의 비용과 품질을 작업별 효용으로 비교하며, HyDE의 번역과 hypothetical document 효과를 더 세분화할 수 있다. 이러한 후속 검증이 이루어져도 본 연구의 현재 결론은 변하지 않는다. 즉 한국어 질의 기반 영어 학술문서 RAG에서는 검색 표현, 근거 기반 생성, 출력 언어 제어를 구분하고, 목적에 맞는 지표와 provenance를 함께 제시해야 한다.

[스타일=본문]

본 논문의 첫 번째 기여는 방법을 발명했다는 선언이 아니라, 서로 다른 층위의 기법을 비교 가능한 실험 단위로 분해한 데 있다. HyDE는 검색 전 표현을 바꾸는 경로, CAD는 같은 입력을 받는 생성 분포의 조정, SCD는 목표 언어 token의 선호 조정으로 정의했다. 이 세 조작은 사용자에게는 모두 “답변 품질을 높이는 기능”처럼 보일 수 있으나, 실험적으로는 바뀌는 입력과 관찰해야 할 결과가 다르다. H·C·S를 이진 configuration으로 기록하고, HyDE에는 end-to-end 대응 비교를, CAD에는 input-identical 대응 비교를, SCD에는 same-condition output comparison을 적용한 구조는 그 차이를 문서화한다. 이 설계 덕분에 한 기법의 좋은 수치를 다른 기법의 증거로 옮겨 적지 않고, 서로 다른 데이터 생성 과정을 존중하는 결론을 제시할 수 있었다.

[스타일=본문]

두 번째 기여는 한국어 질의 기반 영어 논문 RAG의 언어 요구를 검색 정확도와 분리해 측정한 데 있다. 다국어 환경에서 영어 문맥을 사용한다는 사실은 오류가 아니다. 영어 논문 제목, 모델명, 인용구, 수치, 전문 용어는 한국어 답변에도 남을 수 있다. 문제는 그러한 필요한 표현과, 사용자가 한국어로 질문했음에도 설명 전체가 영어로 이동해 버리는 현상을 구별하는 것이다. 본 연구의 Korean-character ratio는 이 복잡한 언어 경험을 완전히 대변하지 않는 대신, 언어 성향이라는 제한된 대상을 결정적으로 계산한다. SCD의 양의 변화는 이 제한된 정의 안에서 강하게 지지되며, 동시에 사람의 언어 적합성 평가와 문체·용어 평가가 필요하다는 후속 과제를 명확하게 남긴다.

[스타일=본문]

세 번째 기여는 수치와 사례의 관계를 논문 본문 안에서 검증 가능하게 만든 것이다. 평균·신뢰구간·win/loss/tie는 60개 질의의 분포를 압축해 보여 주고, UI replay는 동일한 저장 record의 query·configuration·context·answer·score를 보여 준다. 둘 중 하나만으로는 충분하지 않다. 정량 표만 있으면 어떤 실패나 개선이 실제 답변에서 어떻게 나타났는지 알기 어렵고, 화면 예시만 있으면 선택 편향이나 전체 분포를 알기 어렵다. 본 연구는 raw evidence를 새 답변으로 재생성하지 않고 read-only rendering으로 표시하며, example이 통계 검정을 대체하지 않는다는 캡션을 유지한다. 이 구성은 결과를 더 좋아 보이게 하는 장식이 아니라, 60-query 결론이 추적 가능한 artifact에 기반한다는 증거 경로다.

[스타일=본문]

이 논문의 한계는 연구 질문별로도 다르게 작용한다. HyDE의 결론은 translation 또는 query reformulation과 hypothetical document를 분리하지 않았으므로, 어느 단계가 answer relevancy 변화에 더 크게 기여했는지 말하지 못한다. CAD의 결론은 하나의 alpha와 특정 decoding setup에 한정되므로, 다른 alpha·max token·prompt에서의 최적 조건을 알 수 없다. SCD의 결론은 character ratio와 저장된 answer에 기반하므로, 한국어의 자연스러움·정확한 번역·전문용어 보존을 독립 인간 평가로 확정하지 못한다. RAGAS도 절대적인 정답 심판이 아니며, claim extraction 실패가 faithfulness 결측으로 나타난다는 점이 이를 보여 준다. 이 한계들은 본 연구의 모든 결과를 무효화하는 이유가 아니라, 각각의 수치를 어느 질문에 답하는 근거로 사용할 수 있는지를 정하는 경계다.

[스타일=본문]

후속 연구는 단순히 질의 수를 더 늘리는 방식보다, 이 경계를 직접 시험하는 방식으로 설계될 필요가 있다. HyDE에는 원문 한국어 질의, 영어 reformulation, hypothetical document, 최종 retrieval을 분리한 ablation이 필요하다. CAD에는 alpha·context 길이·answer type별 다중 설정과 사용자 체감 지연을 결합한 평가가 필요하다. SCD에는 Korean-character ratio와 함께 blind human evaluation, 목표 언어 외 토큰의 기능적 분류, 고유명사·인용·수식 보존률이 필요하다. 또한 의학·법률처럼 근거 정확성이 특히 중요한 분야와 표·그림·수식이 많은 문서로 corpus를 넓혀야 한다. 이때도 결과를 하나의 전역 점수로 합치기보다, 연구 목적에 맞는 metric과 분모·결측·provenance를 명시하는 원칙을 유지해야 한다.

# 참고문헌 [스타일=참고문헌]

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, 2020.

[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023.

[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024.

[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of AAAI*, 2026.

[5] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” *Findings of ACL*, 2024.

[6] S. E. Robertson et al., “Okapi at TREC-3,” *Text REtrieval Conference*, 1994.

[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009.

[8] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019.

[9] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024.

[10] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” *Proceedings of EMNLP*, pp. 6769–6781, 2020.

[11] G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering,” *Proceedings of EACL*, pp. 874–880, 2021.

[12] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024.

[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023.

[14] P. Sarthi et al., “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval,” *Proceedings of ICLR*, 2024.

[15] A. Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection,” *Proceedings of ICLR*, 2024.

[16] S.-Q. Yan et al., “Corrective Retrieval Augmented Generation,” arXiv:2401.15884, 2024.

[17] Z. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” arXiv:2402.19473, 2024.

[18] D. Shin et al., “Mi:dm 2.0 Korea-centric Bilingual Language Models,” arXiv:2601.09066, 2026.

[19] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997, 2023.

[20] N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models,” *Proceedings of NeurIPS Datasets and Benchmarks Track*, 2021.

[21] N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” *Proceedings of EACL*, pp. 2014–2037, 2023.

# 부록 A. 60개 질의 목록

`generated/QUERY_60_AUDIT.md`는 60개의 query ID, 대상 문서, 질문 유형, 실제 한국어 질문을 보존한다. 한글 이전 시 이 목록에 source page와 GT/answer span 열을 source split에서 추가한다.

# 부록 B. 추가 실제 응답 증빙

`FINALDOCS/EVIDENCE/UI_REPLAY/raw/`의 여섯 파일은 기존 evidence replay UI가 출력한 60-query stored-artifact 원문이다. 각 파일은 selection rule, query ID, source artifact, configuration, 저장 RAGAS score, contexts 및 retrieved ID의 동일성, 저장 answer excerpt를 포함한다.

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
