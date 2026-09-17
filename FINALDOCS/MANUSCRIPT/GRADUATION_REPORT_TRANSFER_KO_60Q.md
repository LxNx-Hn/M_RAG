# 졸업자격실험보고서 [스타일=논문제목]

## 한국어 질의 기반 영어 학술문서 RAG에서 HyDE·CAD·SCD 조합 실험 [스타일=논문제목]

[학생명 입력] · [학번 입력] · [지도교수 입력] · [제출일 입력]

# 제출 페이지 [스타일=목차제목]

본 보고서는 동국대학교 컴퓨터공학과 졸업자격실험보고서로 제출한다.

제출자: [학생명 입력]  /  학번: [학번 입력]  /  지도교수: [지도교수 입력]  /  제출일: [제출일 입력]

# 인준 페이지 [스타일=목차제목]

위 보고서를 졸업자격실험보고서로 인준함.

지도교수: [지도교수 입력] (인)  /  심사위원: [심사위원 입력] (인)  /  인준일: [인준일 입력]

# 국문초록 [스타일=목차제목]

검색 증강 생성(Retrieval-Augmented Generation, RAG)은 외부 문서를 검색해 생성 모델의 문맥으로 제공함으로써 특정 문서에 근거한 질의응답을 가능하게 한다. 한국어로 질문하고 영어 학술문서에서 근거를 검색한 뒤 한국어로 답하는 환경에서는 질의와 문서의 언어·표현 차이, 검색 근거의 생성 단계 활용, 영어 문맥에 따른 출력 언어 이탈을 함께 고려해야 한다. 본 연구는 Hypothetical Document Embeddings(HyDE), Context-Aware Decoding(CAD), Soft Constrained Decoding(SCD)을 각각 검색 표현 확장, 문맥 기반 생성 제어, 한국어 출력 언어 제어의 실험 요인으로 두고 2×2×2 조합을 RAG-Cube로 구성하였다.

실험은 BGE-M3 dense retrieval, BM25 sparse retrieval, weighted Reciprocal Rank Fusion, CrossEncoder reranking, K-intelligence/Midm-2.0-Base-Instruct를 고정 Paper-RAG backbone으로 사용하였다. RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 네 문서에 문서별 15개씩 총 60개의 한국어 질의-대상문서 쌍을 구성하고, 여덟 configuration을 적용하여 480개 generation record를 저장하였다. HyDE는 CAD·SCD OFF의 60 대응쌍, CAD는 동일 검색 문맥 대응쌍, SCD는 같은 query·HyDE·CAD 조건의 240 ON/OFF쌍으로 비교하였다.

HyDE 적용 시 answer relevancy 평균 변화는 +0.0805이고 95% 신뢰구간은 [+0.0110, +0.1514]였다. Faithfulness는 +0.0436, context precision은 -0.0343, context recall은 0.0000으로 지표별 방향이 달랐다. CAD의 동일 문맥 비교에서 faithfulness는 완결된 58쌍에서 +0.0288, answer relevancy는 60쌍에서 -0.0073이었다. SCD는 240개 대응쌍에서 한국어 문자 비율을 평균 +0.2289 높였고, HyDE OFF 동일 문맥 120쌍에서도 +0.2182의 변화가 유지되었다.

결과는 검색 관련성, 근거 충실도, 출력 언어 유지의 목표에 따라 지표별로 서로 다른 configuration이 가장 높은 값을 보였음을 보여준다. 이에 따라 HyDE, CAD, SCD는 각 기법의 적용 위치와 직접 목적에 맞춘 지표를 중심으로 해석하였다.

주요어: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, 한국어 질의, 영어 학술문서, 언어 이탈

# Abstract [스타일=목차제목]

Retrieval-augmented generation (RAG) enables document-grounded question answering by retrieving external evidence and supplying it to a generator. When Korean questions target English academic documents and the expected answer language is Korean, retrieval and generation involve three coupled issues: cross-lingual mismatch between queries and evidence, use of retrieved context during generation, and output-language drift toward English. This study treats Hypothetical Document Embeddings (HyDE), Context-Aware Decoding (CAD), and Soft Constrained Decoding (SCD) as binary factors for retrieval-query expansion, context-aware generation, and Korean-output control, forming a 2×2×2 configuration called RAG-Cube.

The fixed Paper-RAG backbone combines BGE-M3 dense retrieval, BM25 sparse retrieval, weighted Reciprocal Rank Fusion, CrossEncoder reranking, and K-intelligence/Midm-2.0-Base-Instruct. Sixty Korean query-document pairs are constructed from four English academic or technical documents, and eight configurations are applied to every pair, yielding 480 stored generation records. HyDE is compared on 60 pairs with CAD and SCD disabled, CAD on identical-context pairs, and SCD on 240 matched on/off pairs.

HyDE increases answer relevancy by +0.0805 on average with a 95% bootstrap interval of [+0.0110, +0.1514]. Its changes in faithfulness, context precision, and context recall are +0.0436, -0.0343, and 0.0000, respectively. Under identical contexts, CAD changes faithfulness by +0.0288 on 58 complete pairs and answer relevancy by -0.0073 on 60 pairs. SCD increases the Korean-character ratio by +0.2289 across 240 matched pairs and by +0.2182 in the 120-pair HyDE-OFF identical-context subset. The highest-scoring configuration varies by metric, supporting objective-specific configuration selection based on retrieval relevance, faithfulness, and Korean-output control.

Keywords: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, Korean query, English academic document, language drift

# 목    차 [스타일=목차제목]

1. 서론 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
1.1 연구배경 및 목적 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
1.2 연구범위 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
1.3 연구 질문, 분석 관점 및 논문 구성 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
2. 이론적 배경 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
2.1 Retrieval-Augmented Generation ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
2.2 Hybrid Retrieval과 재정렬 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
2.3 Hypothetical Document Embeddings ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
2.4 Context-Aware Decoding ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
2.5 Soft Constrained Decoding과 언어 이탈 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
2.6 RAG 평가 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
2.7 관련 연구와 본 연구의 위치 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
3. 시스템 설계 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
3.1 연구 및 실험 요구사항 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
3.2 아키텍처 설계 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
3.3 상세설계 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
4. 프로그램 구현 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
4.1 시스템 환경 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
4.2 시스템 구성 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
4.3 시스템 구현 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5. 실험 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
5.1 실험 대상과 구성 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.2 평가 및 분석 방법 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.3 RAG-Cube 조합별 결과 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.4 HyDE 결과 및 해석 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.5 CAD 결과 및 해석 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.6 SCD 출력 언어 결과 및 해석 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.7 대표 입출력 및 요구사항별 실행 결과 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.8 종합 논의 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.9 연구의 한계 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6. 결론 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
6.1 연구 질문별 최종 답 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.2 실험 설계가 제공한 의미 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.3 적용 시 configuration 선택 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.4 제한점과 후속 검증 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
참고문헌 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
부록 A~D ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
# 그 림 목 차 [스타일=목차제목]

[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 3-1] HyDE·CAD·SCD RAG-Cube 8개 조건 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 4-1] 고정 Paper-RAG backbone 실행 흐름 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 4-2] generation·evaluation·analysis artifact 흐름 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-1] 60-query 평가 및 대응 비교 설계 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-2] RAG-Cube 8개 조건의 평균 품질 지표 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-3] HyDE·CAD 주 비교와 신뢰구간 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-4] RAG-Cube 조건별 생성 시간 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-5] SCD의 한국어 문자 비율 변화 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-6] HyDE·CAD strata별 품질 지표 변화 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]

# 표 목 차 [스타일=목차제목]

[표 2-1] 관련 연구와 본 실험의 연결 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 3-1] 연구 및 실험 요구사항 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 3-2] RAG-Cube 8개 조건 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 3-3] 실험 요인별 적용 위치와 비교 단위 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-1] 실험 실행 환경 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-2] 고정 Paper-RAG backbone ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-3] 조건별 평균 생성 시간 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-4] 생성 기록의 주요 필드 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-1] 4개 문서별 질의 구성 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-2] RAG-Cube 8개 조건의 평균 품질 지표 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-3] HyDE 주 비교 결과 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-4] CAD 동일 문맥 주 비교 결과 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-5] SCD 조합별 한국어 문자 비율 변화 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-6] SCD 대응쌍 분석 요약 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 A-1] 60개 질의-대상문서 쌍 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 B-1] 문서별 탐색 분석 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 B-2] 질문 유형별 탐색 분석 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 C-1] 주요 연구 artifact provenance ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 D-1] 저장 artifact 기반 점검 절차 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]

# 1. 서론 [스타일=장(1.)]

## 1.1 연구배경 및 목적 [스타일=절(1.1)]

대규모 언어모델은 자연어 질의에 대한 설명형 응답을 생성할 수 있어 학술정보 탐색에도 활용된다. 특정 논문의 방법, 실험 조건, 수치와 결론을 확인하는 작업에서는 답변과 실제 문서 근거의 연결이 중요하다. Retrieval-Augmented Generation(RAG)은 질의와 관련된 외부 문서를 검색해 생성 문맥으로 제공함으로써 문서 근거와 답변의 연결을 강화한다[1].

본 연구가 다루는 환경은 한국어로 질문하고 영어 학술·기술 문서에서 근거를 찾은 뒤 한국어로 답하는 질의응답이다. 이 조건에서는 세 가지 요소가 중요하다. 첫째, 한국어 질문과 영어 학술문장의 어휘·표현 차이를 연결하는 검색 표현이 필요하다. 둘째, 검색된 근거를 생성 단계에서 얼마나 충실하게 활용하는지 확인해야 한다. 셋째, 영어 문맥이 길게 제공되는 조건에서도 한국어 출력 언어를 안정적으로 유지할 필요가 있다.

이 세 문제와 연결해 HyDE는 질의를 가상의 문서 표현으로 확장하는 retrieval-side 기법으로 사용한다[2]. CAD는 문맥이 있는 분포와 없는 분포를 대조하여 생성에서 문맥의 영향을 조절하는 decoding 기법이다[3]. SCD는 목표 언어와 비목표 언어 토큰의 점수를 다르게 조정해 출력 언어 이탈을 완화한다[4]. 세 기법은 검색 표현, 근거 반영, 출력 언어라는 서로 다른 위치에 개입하므로 각 목적에 대응하는 결과를 분리해 분석한다.

본 연구의 목적은 동일한 Paper-RAG backbone에서 HyDE, CAD, SCD의 ON/OFF를 독립 요인으로 구성하고, 한국어 질의-영어 학술문서 환경에서 각 요인이 어떤 변화를 만드는지 통제된 대응 비교로 확인하는 것이다. 세 요인의 2×2×2 조합을 RAG-Cube로 지칭하며, configuration 평균과 동일 query의 검색 ID, contexts, 답변, 평가 점수를 함께 분석한다. 이 구조는 검색 단계와 decoding 단계에서 발생한 변화를 각각의 비교 단위로 추적할 수 있게 한다.

[그림삽입: FINALDOCS/FIGURES/fig1_1_research_setting.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경 [스타일=그림제목]

## 1.2 연구범위 [스타일=절(1.1)]

연구 대상은 RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 네 영어 학술·기술 문서와 문서별 15개씩 구성한 60개 한국어 질의-대상문서 쌍이다. 각 질의에는 여덟 RAG-Cube configuration을 모두 적용하여 480개 generation record를 저장하였다. 모든 configuration은 BGE-M3 dense retrieval, BM25 sparse retrieval, weighted RRF, CrossEncoder reranking, 상위 5개 문맥, Mi:dm 2.0 Base Instruct와 deterministic greedy decoding으로 구성된 동일 backbone을 공유한다.

비교 범위는 세 요인의 직접 목적에 맞춘다. HyDE는 CAD와 SCD를 끈 상태의 60 대응쌍으로 검색 표현 변경을 포함한 end-to-end 효과를 본다. CAD는 retrieved IDs, reranked IDs, contexts가 같은 대응쌍에서 generation-side 차이를 본다. SCD는 query·HyDE·CAD 조건을 고정한 240 ON/OFF쌍에서 한국어 문자 비율 변화를 측정하며, HyDE OFF의 동일 문맥 120쌍을 별도로 확인한다. 품질 평가는 저장된 RAGAS score를 사용하고, 결측은 원본 상태로 보존한다.

## 1.3 연구 질문, 분석 관점 및 논문 구성 [스타일=절(1.1)]

본 연구는 네 가지 질문을 다룬다. 첫째, H1C0S0과 H0C0S0의 대응 비교에서 HyDE가 answer relevancy와 다른 RAGAS 지표를 어떻게 변화시키는가. 둘째, 검색 입력을 동일하게 유지했을 때 CAD가 생성 품질과 실행 시간에 어떤 차이를 만드는가. 셋째, 같은 query·HyDE·CAD 조건에서 SCD가 한국어 출력 비율을 얼마나 변화시키는가. 넷째, 여덟 configuration의 평균을 함께 볼 때 지표별 최고 조건과 trade-off가 어떻게 달라지는가.

분석은 세 수준을 함께 사용한다. 대응 평균 차이와 bootstrap 신뢰구간은 전체 경향을 요약하고, retrieved·reranked chunk ID와 contexts identity는 비교 조건의 통제 상태를 확인한다. 저장 record의 실제 질문·근거·답변·점수는 대표 사례의 provenance를 제공한다. 본 연구는 평균값, 입력 provenance, 실제 응답을 함께 사용해 결과를 해석한다.

2장에서는 RAG와 세 실험 요인, 평가 및 관련 연구를 정리한다. 3장은 실험 요구사항과 비교 설계를, 4장은 구현과 artifact 저장 구조를 설명한다. 5장은 60-query 평가 결과와 사례를 제시하고, 6장은 주요 결과와 한계 및 후속 연구를 종합한다.

# 2. 이론적 배경 [스타일=장(1.)]

## 2.1 Retrieval-Augmented Generation [스타일=절(1.1)]

RAG는 질의와 관련된 외부 문서를 검색하고, 선택된 문맥을 생성 모델의 입력에 포함하여 답변을 만드는 구조이다[1]. 문서 집합을 D, 질의를 q, 검색 문맥을 C, 답변을 y라고 하면 과정은 Retrieve(q, D)로 C를 얻고, 생성 모델이 q와 C를 조건으로 y를 생성하는 흐름으로 설명할 수 있다. 학술문서 질의응답에서는 검색 단계와 생성 단계를 구분해 보는 것이 중요하다. 필요한 문단의 검색 상태와 검색 문단이 최종 답변에 반영되는 정도는 서로 다른 분석 대상이기 때문이다.

본 연구는 이러한 구분을 결과 기록에도 유지한다. retrieval과 reranking의 chunk ID, 최종 contexts를 답변과 함께 저장하고, context-level 지표와 answer-level 지표를 별도로 해석한다. 이 기록 구조는 검색 결과와 답변 품질을 서로 다른 단계에서 확인할 수 있게 한다.

[한글 수식 입력기 복붙용 — 최종 HWP에는 렌더링된 수식만 남김]

```text
C_q = Retrieve(q,D)
```

```text
y = LM(q,C_q)
```

## 2.2 Hybrid Retrieval과 재정렬 [스타일=절(1.1)]

고정 backbone은 BGE-M3 기반 dense retrieval과 BM25 기반 sparse retrieval을 결합한다. Dense retrieval은 질의와 passage의 의미적 유사성을 이용해 어휘가 정확히 일치하지 않아도 관련 후보를 찾는 데 유리하고, BM25는 모델명·약어·수치처럼 표면 일치가 중요한 표현을 보완한다[5][6]. 두 경로는 rank 기반 weighted Reciprocal Rank Fusion으로 결합하며[7], 후보는 CrossEncoder가 질의와 passage를 함께 보며 다시 정렬한다[8].

본 실험에서는 dense와 BM25 가중치를 각각 0.6과 0.4로 고정하고, retrieval pool과 rerank top-N을 8개로 설정한다. 최종 생성 모델에는 상위 5개 문맥을 제공한다. 이 규칙은 모든 RAG-Cube configuration에서 동일하게 유지한다. HyDE ON/OFF에서 retrieved ID나 final context가 달라지면 검색 표현 변경의 결과로 기록하고, CAD 비교는 IDs와 contexts가 동일한 대응쌍으로 구성한다.

이 연결은 한국어 질의와 영어 학술문서의 관계에서 특히 중요하다. 한국어 질문의 설명형 표현은 영어 원문의 제목, 섹션명, 방법론 용어와 직접 대응되는 단서가 적을 수 있다. 반대로 논문명, 데이터셋명, 모델 크기, 하이퍼파라미터처럼 정확한 표기가 필요한 질문에서는 표면 단서의 역할이 커진다. 본 backbone은 dense와 sparse 후보를 weighted RRF로 결합하고 CrossEncoder로 재정렬해 두 종류의 단서를 함께 활용한다. HyDE의 변화는 이 fusion과 reranking을 거친 최종 문맥 및 answer-level 결과와 함께 해석한다.

재정렬은 후보 passage의 우선순위를 결정하고, 생성 모델은 상위 다섯 문맥에서 질문에 필요한 내용을 선택·종합한다. 이 때문에 본 연구는 최종 contexts를 고정한 CAD 비교와 contexts 자체가 달라질 수 있는 HyDE 비교를 분리한다. 동일한 hybrid backbone은 검색 단계 변화와 decoding 단계 변화를 공통 기준 위에서 비교할 수 있게 한다.

Weighted RRF는 다음과 같이 표현할 수 있다.

[한글 수식 입력기 복붙용 — 최종 HWP에는 렌더링된 수식만 남김]

```text
RRF(d) = {0.6} over {k + rank_dense(d)} + {0.4} over {k + rank_BM25(d)}
```

## 2.3 Hypothetical Document Embeddings [스타일=절(1.1)]

HyDE는 질의에 직접 임베딩을 적용하는 대신, 질의에 답할 법한 가상의 문서를 생성하고 그 표현을 검색에 사용하는 방법이다[2]. 짧거나 설명형인 질의와 학술문서의 전문적 표현 사이에 간극이 있을 때 hypothetical document가 검색 표현을 확장하는 역할을 할 수 있다.

본 실험에서 HyDE ON은 한국어 질의를 영어 검색 표현으로 바꾸고 hypothetical document를 생성한 뒤 이를 dense retrieval 입력으로 사용한다. BM25와 CrossEncoder에는 원질의를 유지한다. 최종 답변은 HyDE를 통해 선택된 실제 문서 passage를 근거로 생성한다. 따라서 HyDE 결과는 번역·가상 문서 생성·dense retrieval·fusion·reranking·context selection을 포함한 end-to-end pipeline effect로 해석한다.

가상 문서는 질문을 영어 학술문서에 가까운 서술로 확장하고 검색 공간의 후보 순위에 영향을 준다. 포함된 표현에 따라 유용한 후보가 상위로 이동하거나 특정 세부사항의 비중이 커질 수 있다. 본 연구의 answer relevancy 변화는 이러한 검색 경로와 최종 답변의 질문 적합성 관계를 보여준다. retrieved ID와 최종 contexts를 함께 저장한 이유도 이 검색 경로 변화를 answer-level 결과와 연결해 확인하기 위해서다.

## 2.4 Context-Aware Decoding [스타일=절(1.1)]

CAD는 문맥이 포함된 next-token distribution과 문맥이 없는 distribution을 대조하여, 주어진 문맥에 의해 상대적으로 강화된 token을 생성에 반영하는 decoding 방법이다[3]. 본 실험에서는 CAD alpha=0.5를 고정한다. CAD는 retrieval 이후 generation 단계에서 동작하며, 독립적인 decoding 변화를 보기 위해 CAD ON/OFF에서 retrieved IDs, reranked IDs와 contexts가 동일한 대응쌍을 구성한다.

문맥이 포함된 logits를 `z_ctx`, 문맥이 없는 logits를 `z_noctx`라고 하면 본 연구의 CAD score는 다음과 같이 표현한다.

[한글 수식 입력기 복붙용 — 최종 HWP에는 렌더링된 수식만 남김]

```text
z_CAD = (1 + alpha) z_ctx - alpha z_noctx
```

CAD는 생성 단계마다 context branch와 no-context branch를 계산하므로 단일 branch보다 실행 비용이 증가할 수 있다. 따라서 결과는 faithfulness와 answer relevancy뿐 아니라 generation duration과 함께 본다. 동일 입력에서 나타나는 질의별 변화와 평균을 함께 분석해 문맥 기반 logit 조절의 결과 분포를 확인한다.

CAD 대응쌍은 query, retrieved ID, reranked ID, 최종 contexts가 같은지를 먼저 확인하고 decoding 조건만 달리한다. 이 통제가 성립하면 평균 변화와 사례 차이를 고정 근거에 대한 generation-side 변화로 해석할 수 있다. 같은 문맥에서 CAD ON/OFF를 비교하는 설계는 retrieval 선택과 generation 변화를 분리하는 핵심 조건이다.

## 2.5 Soft Constrained Decoding과 언어 이탈 [스타일=절(1.1)]

다국어 RAG에서는 질의 언어와 근거 문서 언어가 다를 때 답변의 표면 언어가 문맥 언어 쪽으로 이동할 수 있다. SCD는 vocabulary를 목표 언어, 비목표 언어, 중립 token으로 구분하고 decoding 중 token score에 서로 다른 제약을 적용해 이러한 언어 이탈을 완화한다[4]. 본 실험의 reference SCD는 alpha=1.1, beta=0.9, Tstart=5를 사용하며 CAD와 함께 적용될 때에는 CAD score를 구성한 뒤 SCD processor를 적용한다.

언어 효과는 생성 답변의 한글 문자 수를 한글 문자와 ASCII 영문자 수의 합으로 나눈 Korean-character ratio로 측정한다. 분모는 한글 문자와 ASCII 영문자로 구성한다. 이 값은 출력 언어 성향을 측정하며, 문법성·내용 정확성·전문용어 사용의 적절성은 별도 평가 차원으로 둔다. 본 연구는 Korean-character ratio를 language adherence의 operational indicator로 사용한다.

SCD의 token group별 score 조정과 Korean-character ratio는 한글 수식 입력기에 다음 형태로 입력한다.

[한글 수식 입력기 복붙용 — 한국어 목표 토큰]

```text
tilde z_i = alpha z_i
```

[한글 수식 입력기 복붙용 — 영어 비목표 토큰]

```text
tilde z_i = beta z_i
```

[한글 수식 입력기 복붙용 — 중립 토큰]

```text
tilde z_i = z_i
```

[한글 수식 입력기 복붙용 — 한국어 문자 비율]

```text
KoreanRatio = {N_Hangul} over {N_Hangul + N_ASCII}
```

SCD는 생성 중 token score를 조절해 목표 언어의 선택 성향을 조정한다. 동일 query·HyDE·CAD 조건을 고정한 ON/OFF 대응쌍에서 Korean-character ratio를 비교함으로써 영어 근거 문맥 아래에서 한국어 문자 사용이 어떻게 변하는지 직접 측정한다. 논문 제목, 모델명, 데이터셋명과 같은 영어 표기가 포함된 실제 답변도 동일한 계산 규칙을 적용하며, 출력 언어 성향과 답변 품질은 서로 다른 평가 축으로 분석한다.

## 2.6 RAG 평가 [스타일=절(1.1)]

HyDE와 CAD의 품질 비교에는 RAGAS의 faithfulness, answer relevancy, context precision, context recall을 사용한다[9]. Faithfulness는 답변의 주장이 제공된 context에 의해 지지되는 정도를, answer relevancy는 답변이 질문에 직접 대응하는 정도를 본다. Context precision과 context recall은 검색된 근거의 관련성과 필요한 근거의 포함 정도를 측정한다. 네 지표는 각각 독립적으로 분석한다.

요인별 효과는 동일 query의 ON/OFF 차이를 이용한 paired comparison으로 분석하고, 질의를 재표집 단위로 하는 bootstrap 신뢰구간을 함께 제시한다. 자동 평가 분석은 score가 존재하는 유효 대응쌍을 사용한다. SCD의 출력 언어 효과는 RAGAS와 별도로 Korean-character ratio로 측정한다. 실제 대응쌍 구성, 유효 표본 수와 practical threshold는 5.2절에서 제시한다.

## 2.7 관련 연구와 본 연구의 위치 [스타일=절(1.1)]

검색 증강 생성 연구는 검색기의 표현력, 여러 passage의 활용, decoding 제어와 검색·생성의 자기검증으로 확장되어 왔다. Dense Passage Retrieval은 dense retrieval의 대표 구조를 정립했고[10], Fusion-in-Decoder는 여러 검색 passage를 생성 단계에서 함께 이용하는 방식을 제안했다[11]. 긴 문맥에서는 관련 정보의 위치에 따라 모델의 활용 정도가 달라질 수 있다는 분석이 보고되었으며[12], contrastive decoding은 서로 다른 조건의 생성 분포를 대조하는 관점을 제시했다[13]. RAPTOR는 세부 passage와 상위 요약을 계층적으로 구성하는 retrieval 구조를 제안했고[14], Self-RAG[15]와 Corrective RAG[16]는 검색 필요성이나 근거 품질을 생성 과정에서 점검하는 방향을 보였다.

RAG 시스템 전반을 정리한 조사 연구[17], 한국어·영어 이중언어 생성 모델에 관한 Mi:dm 2.0 연구[18], RAG의 구성과 평가를 체계화한 조사 연구[19]는 본 실험의 시스템·언어 조건을 설정하는 배경이 된다. 검색 모델의 도메인·과제 간 편차는 BEIR[20]과 MTEB[21] 같은 벤치마크의 관점에서 참고하며, 실험 corpus 중 하나인 Mi:dm K 2.5 Pro는 해당 기술 보고서[22]를 사용한다.

본 연구는 HyDE, CAD, SCD를 각각 검색 표현, 문맥 기반 생성, 출력 언어 제어 요인으로 고정 backbone 안에 배치하고, 각 요인의 적용 위치에 맞는 통제 비교를 수행하는 application study로 구성하였다. HyDE는 검색 입력 변화까지 포함한 end-to-end 검색 확장 효과로, CAD는 동일 context의 generation-side 효과로, SCD는 동일 query·HyDE·CAD 조건의 output-language 효과로 분석한다.

표 2-1은 각 선행 연구 흐름과 본 실험의 연결 위치를 정리한다. DPR과 BEIR는 검색 표현과 도메인 편차를 읽는 관점을, FiD와 long-context 연구는 여러 문맥이 생성에 전달되는 조건을, contrastive decoding은 CAD의 분포 대조 관점을 제공한다. Self-RAG와 CRAG는 검색·생성·근거 점검을 서로 다른 단계로 구분하는 관점을 제공한다. 본 연구는 한국어 질의-영어 문서 환경에서 세 개입 지점이 fixed backbone 안에서 보이는 trade-off를 기록하며, 표의 마지막 열은 각 결과의 적용 위치와 분석 범위를 요약한다.

[표 2-1] 관련 연구와 본 실험의 연결 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T2-1_Related_Work | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
연구 흐름	대표 연구	본 연구에서의 적용 범위	해석 범위
Dense retrieval	DPR[10], BEIR[20]	한국어 질의와 영어 passage 사이의 검색 표현 간극을 HyDE 조건으로 관찰	본 고정 backbone의 application study 범위
Multi-passage generation	FiD[11], long-context 분석[12]	rerank된 상위 5개 문맥을 고정해 answer/context 지표를 분리	문맥 길이와 순서 정책은 고정
Hypothetical-document retrieval	HyDE[2]	H1/H0 end-to-end 대응 비교와 retrieved ID 확인	가상 문서는 검색 표현으로 사용
Contrastive decoding	CAD[3], contrastive decoding[13]	같은 input에서 C1/C0 paired 비교	CAD alpha=0.5 고정 조건
Corrective/reflective RAG	Self-RAG[15], CRAG[16]	검색·생성·출력 문제를 별도 층위로 해석하는 관점	관련 연구의 비교 관점으로 참조
RAG evaluation	RAGAS[9], RAG survey[19]	네 품질 지표와 artifact 기반 provenance 확인	자동 평가와 저장 artifact를 함께 사용
```

# 3. 시스템 설계 [스타일=장(1.)]

## 3.1 연구 및 실험 요구사항 [스타일=절(1.1)]

설계는 실험 변인의 통제와 결과 추적 가능성을 중심으로 구성하였다. 첫째, 각 query ID는 하나의 대상 문서와 고정 연결되어야 한다. 둘째, 60개 질의에 여덟 configuration이 빠짐없이 실행되어 동일 질문을 조건별로 비교할 수 있어야 한다. 셋째, H·C·S 이외의 검색·생성 backbone은 모든 조건에서 동일해야 한다. 넷째, answer와 함께 retrieved·reranked chunk ID, contexts, decoding metadata와 실행 시간을 저장해야 한다. 마지막으로 본문 수치와 사례가 source artifact로 다시 연결되어야 한다.

[표 3-1] 연구 및 실험 요구사항 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T3-1_Requirements | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
요구사항	확인 기준	값
한국어 질의 기반 영문 문서 QA	질의와 대상 문서 연결	60개 질의-문서 쌍
실험 요인	HyDE·CAD·SCD ON/OFF	2×2×2, 8개 조건
생성 기록	조건별 저장 record	480개, 조건별 60개
출력 언어	한국어 문자 비율	SCD ON/OFF 240개 대응쌍
추적성	source hash와 generation record	검증 보고서에 기록
```

## 3.2 아키텍처 설계 [스타일=절(1.1)]

실험 아키텍처는 질의 입력, 검색 표현 구성, hybrid retrieval, reranking, 문맥 선택, 조건별 decoding, generation record 저장, 평가·분석의 순서로 구성된다. HyDE OFF에서는 원질의를 dense retrieval에 사용하고, HyDE ON에서는 번역된 질의에서 만든 hypothetical document를 dense branch에 제공한다. BM25와 CrossEncoder에는 원질의를 유지한다. 검색 후보는 weighted RRF와 CrossEncoder를 거쳐 상위 5개 문맥으로 구성된다.

생성 단계에서는 같은 Mi:dm 2.0 Base Instruct를 사용하되 CAD와 SCD만 선택적으로 적용한다. CAD는 context/no-context 두 분포를 이용해 token score를 조절하고, SCD는 한국어·영어·중립 token partition에 따라 언어 score를 조절한다. 생성이 끝나면 query, paper, configuration, contexts, answer, duration과 요인별 metadata를 하나의 record에 저장한다. 이후 평가와 분석은 이 저장 record를 읽어 수행한다.

[그림삽입: FINALDOCS/FIGURES/fig3_1_rag_cube.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 3-1] HyDE, CAD, SCD의 독립 이진 요인으로 구성한 RAG-Cube 8개 조건 [스타일=그림제목]

## 3.3 상세설계 [스타일=절(1.1)]

RAG-Cube의 여덟 조건은 H, C, S의 ON/OFF로 구성한다. configuration 이름은 사람이 읽는 H0C0S0 표기와 함께 실제 저장 `config_name`, `use_hyde`, `use_cad`, `use_scd` field로 확인한다. 실행 상태는 configuration 이름과 parameter field를 함께 대조한다. SCD ON record에는 mode, alpha=1.1, beta=0.9, Tstart=5가, CAD ON record에는 alpha=0.5가 저장된다.

[표 3-2] RAG-Cube 8개 조건 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T3-2_RAG-Cube | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
조건	HyDE	CAD	SCD	생성 수
H0C0S0	OFF	OFF	OFF	60
H0C1S0	OFF	ON	OFF	60
H0C0S1	OFF	OFF	ON	60
H0C1S1	OFF	ON	ON	60
H1C0S0	ON	OFF	OFF	60
H1C1S0	ON	ON	OFF	60
H1C0S1	ON	OFF	ON	60
H1C1S1	ON	ON	ON	60
```

[표 3-3] 실험 요인별 적용 위치와 비교 단위 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T3-3_Factor_Position | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
요인	적용 위치	주 비교	주 지표
HyDE	검색 표현 확장	CAD OFF·SCD OFF의 60 대응쌍	RAGAS 4개 품질 지표
CAD	문맥 기반 decoding	동일 문맥 60 대응쌍; faithfulness 58 완결쌍	RAGAS 4개 품질 지표
SCD	출력 token logit 제어	동일 query·HyDE·CAD의 240 ON/OFF쌍	한국어 문자 비율
```

비교 설계는 요인별로 다르다. HyDE primary contrast는 같은 query의 H1C0S0과 H0C0S0을 연결하며, 검색 결과 변화를 end-to-end 효과에 포함한다. CAD primary contrast는 같은 query의 H0C1S0과 H0C0S0을 연결하고 retrieved IDs, reranked IDs, contexts가 모두 같은지를 확인한다. SCD는 query와 H·C 조건을 고정하고 S만 다른 240쌍을 만들며, HyDE OFF 120쌍에서는 context identity도 확인한다.

각 generation record에는 검색 후보와 최종 문맥을 함께 남긴다. retrieved IDs와 reranked IDs가 같더라도 context 구성 결과가 달라질 수 있으므로 실제 contexts까지 저장한다. 이러한 provenance는 HyDE의 검색 변화와 CAD의 동일 입력 비교를 구분하는 근거가 된다. evaluation artifact는 generation과 분리해 저장하며, derived-data builder가 두 artifact를 읽어 configuration 평균, paired delta와 bootstrap interval을 계산한다. 표와 그림은 이 파생 자료를 읽어 생성한다.

# 4. 프로그램 구현 [스타일=장(1.)]

## 4.1 시스템 환경 [스타일=절(1.1)]

Generation record에는 K-intelligence/Midm-2.0-Base-Instruct, deterministic greedy decoding, max_new_tokens=512가 기록되어 있다. 검색 backend는 BGE-M3 dense retrieval과 BM25 sparse retrieval을 weighted RRF로 결합하고 CrossEncoder로 재정렬한다. retrieval pool과 rerank top-N은 각각 8개, 최종 생성 문맥은 5개로 고정한다. 환경 표는 generation record에서 확인한 모델, decoding, retrieval pool, rerank top-N, context count와 요인별 parameter를 정리한다.

[표 4-1] 실험 실행 환경 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T4-1_Environment | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
구성	저장 record 기준 값
생성 모델	K-intelligence/Midm-2.0-Base-Instruct
디코딩	deterministic greedy
검색 backend	BGE-M3 dense + BM25 sparse + weighted RRF + CrossEncoder rerank
retrieval pool / rerank	8 / 8
최종 문맥 수	5
max_new_tokens	512
CAD alpha	0.5
SCD	reference_scd; alpha=1.1, beta=0.9, Tstart=5
```

[표 4-2] 고정 Paper-RAG backbone [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T4-2_Backbone | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
단계	고정 구성
입력	한국어 질의와 지정 대상 문서
검색	BGE-M3 dense retrieval + BM25 sparse retrieval
결합	weighted Reciprocal Rank Fusion
재정렬	CrossEncoder reranking
문맥 구성	rerank 결과에서 상위 5개 context
생성	Mi:dm 2.0 Base Instruct; max_new_tokens=512
요인	HyDE retrieval-side / CAD·SCD generation-side
```

## 4.2 시스템 구성 [스타일=절(1.1)]

프로그램은 query split과 source document chunk를 읽는 입력부, HyDE를 포함한 검색 표현 구성부, dense·sparse retrieval과 fusion·reranking을 수행하는 검색부, CAD·SCD를 선택적으로 적용하는 생성부, generation/evaluation artifact 저장부, 분석·재현 모듈로 구성된다. 모든 configuration은 같은 query split과 backbone을 사용하고 H·C·S 상태만 바꾼다.

HyDE ON에서는 translated query와 hypothetical document를 dense branch에 전달한다. 검색 결과는 weighted RRF와 CrossEncoder를 거쳐 다섯 문맥으로 구성된다. 생성부는 이 문맥과 질문을 입력으로 받아 기준 decoding 또는 CAD·SCD processor가 적용된 decoding을 수행한다. 저장부는 answer뿐 아니라 검색 ID, contexts, parameter와 duration을 함께 기록하며, 저장된 field를 이용해 이후 분석에서 비교 조건을 재확인한다.

[그림삽입: FINALDOCS/FIGURES/fig4_1_pipeline.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 4-1] 고정 Paper-RAG backbone에서 RAG-Cube 요인을 적용하는 실행 흐름 [스타일=그림제목]

## 4.3 시스템 구현 [스타일=절(1.1)]

주실험 실행기는 60개 query-document pair를 여덟 configuration으로 순회한다. HyDE가 적용된 record에는 검색 표현 생성 결과와 사용 상태가, CAD와 SCD가 적용된 record에는 각 processor의 활성 상태와 parameter가 저장된다. retrieval trace에는 retrieved·reranked chunk ID와 실제 contexts가 포함되며, 생성 결과에는 answer, duration, decoding mode가 함께 남는다.

[표 4-3] 조건별 평균 생성 시간 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T4-3_Runtime | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
조건	생성 수	평균 초	중앙값 초
H0C0S0	60	20.792	16.077
H0C1S0	60	63.867	57.819
H0C0S1	60	18.898	17.579
H0C1S1	60	55.159	51.127
H1C0S0	60	23.440	22.245
H1C1S0	60	73.532	71.700
H1C0S1	60	24.892	24.714
H1C1S1	60	64.125	64.834
```

[표 4-4] 생성 기록의 주요 필드 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T4-4_Record_Fields | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
구분	필드
식별	query_id, paper, config_name, status
요인	use_hyde, use_cad, use_scd, parameter fields
검색	retrieved_chunk_ids, reranked_chunk_ids, contexts
생성	generated_answer, duration_seconds, decoding_mode
재현	generation_model, retrieval backend, context count
```

HyDE의 hypothetical document는 dense retrieval 입력으로 사용하고, 최종 답변은 검색된 실제 문서 passage를 근거로 생성한다. CAD는 같은 generated prefix에서 context branch와 no-context branch를 계산하며, 표 4-3의 duration은 이 계산 구조에 따른 실행 시간 차이를 보여준다. SCD는 생성 중 token score를 조정하는 processor이며, Korean-character ratio는 저장된 answer 문자열에서 다시 계산할 수 있다.

[그림삽입: FINALDOCS/FIGURES/fig4_2_artifact_flow.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 4-2] generation, evaluation, analysis와 최종 표·그림 사이의 artifact 흐름 [스타일=그림제목]

# 5. 실험 [스타일=장(1.)]

## 5.1 실험 대상과 구성 [스타일=절(1.1)]

최종 질의 집합은 RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report에 각각 15개 질문을 연결한 60개 질의-대상문서 쌍이다. 모든 질의는 valid answer span과 answerable 상태를 가지며, 60개 고유 query ID와 고유 한국어 질문으로 구성하였다. 여덟 RAG-Cube configuration을 모두 적용하여 480개 generation record를 생성했다. 표 5-1은 문서별 분포를 제시하며, 부록 A에는 query ID·질문·대상 문서·질문 유형·source page·answer span 여부를 원자료에서 옮긴다.

[표 5-1] 4개 문서별 질의 구성 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-1_Dataset | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
대상 문서	질의 수
RAG Survey	15
CAD	15
RAPTOR	15
Mi:dm K 2.5 Pro Technical Report	15
합계	60
```

## 5.2 평가 및 분석 방법 [스타일=절(1.1)]

평가는 3.3절의 comparison contract에 따라 저장된 generation·evaluation artifact에서 대응쌍을 구성한다. RAGAS는 480개 score row의 faithfulness, answer relevancy, context precision, context recall을 사용한다. 전체 1,920 metric cell 중 5개 faithfulness 값은 빈 명제 집합으로 인해 결측이며, 각 비교는 유효값이 존재하는 대응쌍을 기준으로 계산한다. HyDE primary는 60쌍, CAD primary는 동일 검색 문맥의 대응쌍을 사용하며 CAD faithfulness는 양쪽 score가 존재하는 58쌍을 사용한다. SCD는 query·HyDE·CAD를 고정한 240 ON/OFF쌍의 Korean-character ratio를 비교하고, HyDE OFF 동일 문맥 120쌍을 별도로 확인한다.

60개 질의는 네 문서에 15개씩 배정되며 각 질의에는 source page와 answer span이 보존되어 있다. 문서별 균등 배정은 네 대상 문서의 결과를 같은 수의 질의로 비교하기 위한 표본 내 설계다. 각 문서와 질문 유형의 하위집단 결과는 부록 B에서 탐색 분석으로 제시한다.

요인 효과는 동일 query의 ON−OFF 차이로 계산한다. 질의를 재표집 단위로 하는 paired bootstrap을 사용하여 평균 차이의 95% 신뢰구간을 구한다. 품질 지표는 +0.01 초과를 win, -0.01 미만을 loss, 그 사이를 tie로 집계하고, SCD ratio는 ±0.02 practical band를 사용한다. configuration 평균은 여덟 조합의 기술통계로 제시하고, paired contrast는 특정 요인의 ON/OFF 차이를 통제 비교로 제시한다.

대응쌍의 개별 차이와 평균 변화는 다음 식으로 계산한다.

[한글 수식 입력기 복붙용 — 개별 대응쌍 차이]

```text
Delta_i = s_i^{ON} - s_i^{OFF}
```

[한글 수식 입력기 복붙용 — 대응 평균 변화]

```text
bar Delta = {1} over {n} sum_{i=1}^{n} Delta_i
```

[그림삽입: FINALDOCS/FIGURES/fig5_0_evaluation_design.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-1] 60-query 평가와 HyDE·CAD·SCD 대응 비교 설계 [스타일=그림제목]

## 5.3 RAG-Cube 조합별 결과 [스타일=절(1.1)]

표 5-2는 여덟 configuration의 평균 품질과 Korean ratio를 보여준다. Faithfulness가 가장 높은 조건은 H1C1S0(0.8599), answer relevancy가 가장 높은 조건은 H1C0S0(0.7633), context precision이 가장 높은 조건은 H0C0S1(0.7634)이다. Context recall은 H0C0S0과 H1C0S0이 0.9333으로 같고, Korean ratio는 H1C0S1이 0.8072로 가장 높다. 지표별 최고 조건이 서로 달랐으며, configuration 선택 기준도 목표 지표에 따라 달라졌다.

[표 5-2] RAG-Cube 8개 조건의 평균 품질 지표 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-2_Config_Scores | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
조건	생성 수	Faithfulness	Answer relevancy	Context precision	Context recall	Korean ratio
H0C0S0	60	0.7906	0.6828	0.7488	0.9333	0.4943
H0C1S0	60	0.8385	0.6755	0.7395	0.9167	0.4877
H0C0S1	60	0.7869	0.6372	0.7634	0.9000	0.6990
H0C1S1	60	0.7768	0.5996	0.7523	0.8500	0.7195
H1C0S0	60	0.8342	0.7633	0.7145	0.9333	0.5561
H1C1S0	60	0.8599	0.7045	0.7357	0.9000	0.5031
H1C0S1	60	0.8223	0.7097	0.7426	0.9000	0.8072
H1C1S1	60	0.8313	0.6671	0.7540	0.9167	0.7314
```

[그림삽입: FINALDOCS/FIGURES/fig5_1_quality_matrix.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-2] RAG-Cube 8개 조건의 평균 품질 지표. 셀 값은 저장된 RAGAS score의 configuration별 평균이다. [스타일=그림제목]

## 5.4 HyDE 결과 및 해석 [스타일=절(1.1)]

HyDE의 주 비교에서 answer relevancy 평균 변화는 +0.0805이고 95% CI는 [+0.0110, +0.1514]다. 60개 대응 질의에서 win/loss/tie는 29/15/16이며, 이 값은 본 연구에서 가장 명확한 HyDE 관련 결과다. Faithfulness 평균 변화는 +0.0436이고 CI는 [-0.0262, +0.1153]이며 win/loss/tie는 24/21/15다. Context precision은 -0.0343, context recall은 0.0000이고 context recall은 52개 질의가 tie에 해당한다.

HyDE는 answer relevancy에서 가장 명확한 양의 평균 변화를 보였고, faithfulness·context precision·context recall은 서로 다른 방향을 보였다. 검색 ID가 실제로 바뀐 저장 사례에서는 HyDE OFF 답변이 BIC 활용 정보를 찾지 못한 반면 HyDE ON 답변은 최적 cluster 수 선택을 설명했다. 이 사례는 retrieval change와 answer-level 결과를 실제 provenance로 연결한다.

answer relevancy의 양의 변화와 context precision의 음의 변화가 함께 나타난 가능한 해석은 HyDE가 질문을 설명하는 문서형 검색 표현을 제공하면서 최종 답변이 질문의 요구에 더 직접 반응하도록 도왔고, reranked 상위 문맥의 관련성 구성은 일부 질의에서 달라졌다는 것이다. HyDE ON은 dense query representation, fusion 후보, reranking 이후의 context selection까지 바꾸므로, +0.0805는 고정 pipeline 전체를 통과한 end-to-end answer-level 대응 차이다.

win/loss/tie 29/15/16은 평균과 신뢰구간의 결과를 질의 수준에서 보완한다. 29개 win과 함께 15개 loss, 16개 tie가 분포해 질문별 반응의 이질성을 보여준다. 특히 수치·모델명처럼 표면 단서가 강한 질문과 여러 문장을 종합해야 하는 설명형 질문은 검색 표현 변경에 다르게 반응할 수 있다. 부록 B는 문서별·질문유형별 차이를 탐색적으로 제시하며, 일부 질문유형 하위집단의 표본 수는 작다. 본문에서는 HyDE가 이 corpus의 질문 적합성에서 가장 명확한 평균 변화를 보였다는 결과를 중심으로 정리한다.

[표 5-3] HyDE 주 비교 결과 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-3_HyDE | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
지표	평균 변화 ON−OFF	95% CI	Win	Loss	Tie	n
faithfulness	+0.0436	[-0.0262, +0.1153]	24	21	15	60
answer_relevancy	+0.0805	[+0.0110, +0.1514]	29	15	16	60
context_precision	-0.0343	[-0.0932, +0.0247]	17	23	20	60
context_recall	0	[-0.1000, +0.1000]	4	4	52	60
```

[그림삽입: FINALDOCS/FIGURES/fig5_2_primary_forest.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-3] HyDE와 CAD의 통제 비교. 점은 ON−OFF 평균 차이, 선은 95% bootstrap 신뢰구간이다. [스타일=그림제목]

## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]

CAD의 주 비교는 검색 문맥을 동일하게 유지하고 decoding만 달리한 대응쌍이다. Faithfulness는 완결된 58쌍에서 평균 +0.0288, 95% CI [-0.0367, +0.0934], win/loss/tie 21/24/13이다. Answer relevancy는 60쌍에서 -0.0073, CI [-0.0855, +0.0719], win/loss/tie 19/32/9이다. Context precision은 -0.0092, context recall은 -0.0167이며, context recall은 59개 질의가 tie다.

CAD의 문맥 기반 logit 조절은 지표별 방향과 질의별 분포를 함께 보여준다. H1C1S0은 configuration 평균 faithfulness가 가장 높으며, HyDE ON strata에서는 faithfulness와 context precision이 양의 방향을 보이는 pattern이 있다. 동일 문맥 사례에는 CAD ON에서 faithfulness가 커진 경우와 작은 경우가 모두 저장되어 있으며, 이 변동은 CAD의 trade-off를 실제 응답 단위에서 보여준다.

CAD faithfulness의 win/loss/tie 21/24/13은 질의별 변동이 컸음을 보여준다. faithfulness의 신뢰구간은 0을 포함하며, 양쪽 score가 존재한 58쌍을 기준으로 계산하였다. 같은 문맥을 입력으로 하더라도 문맥에 직접 답이 포함된 정도, 여러 문장의 종합 필요성, 질문 유형에 따라 대조식 decoding의 반응이 달라질 수 있다.

[표 5-4] CAD 동일 문맥 주 비교 결과 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-4_CAD | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
지표	평균 변화 ON−OFF	95% CI	Win	Loss	Tie	n
faithfulness	+0.0288	[-0.0367, +0.0934]	21	24	13	58
answer_relevancy	-0.0073	[-0.0855, +0.0719]	19	32	9	60
context_precision	-0.0092	[-0.0306, +0.0077]	4	4	52	60
context_recall	-0.0167	[-0.0500, +0.0000]	0	1	59	60
```

[그림삽입: FINALDOCS/FIGURES/fig5_10_runtime.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-6] RAG-Cube 조건별 generation duration. CAD ON 조건의 실행 시간 증가를 품질 지표와 분리해 제시한다. [스타일=그림제목]

## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]

SCD의 직접 목적은 영어 근거 문맥에서 한국어 출력 언어를 유지하는 것이다. 240 ON/OFF 대응쌍의 한국어 문자 비율 평균 변화는 +0.2289이고 95% CI는 [+0.2051, +0.2532]다. +0.02를 초과한 증가는 219개, -0.02보다 작은 감소는 10개, 그 사이 동률은 11개다. HyDE OFF에서 contexts·retrieved ID·reranked ID가 같은 120쌍에서도 평균 변화는 +0.2182, 95% CI는 [+0.1880, +0.2487]이다.

네 HyDE·CAD strata에서 SCD ON−OFF 평균 변화는 각각 +0.2047, +0.2317, +0.2511, +0.2283이다. 네 strata 모두 양의 평균 변화를 보였으며, SCD의 직접 목표인 output-language control에서 일관된 방향을 확인했다. Korean-character ratio는 출력 언어 성향을 측정하고, faithfulness·answer relevancy·문법성·전문용어 적절성은 별도 지표와 평가 차원으로 둔다.

strata별 평균은 configuration 내 SCD ON/OFF 변화를 요약한다. SCD ON 답변에서도 영어 논문 제목, 모델명, 데이터셋명, 수식 기호가 자연스럽게 남을 수 있으며, Korean-character ratio는 한글 문자와 ASCII 영문자 비율을 통해 이러한 혼합 표기를 포함한 실제 답변의 언어 성향을 반영한다.

[표 5-5] SCD 조합별 한국어 문자 비율 변화 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-5_SCD_Config | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
SCD OFF	SCD ON	쌍 수	평균 변화	CI 하한	CI 상한	증가	감소	동률
H0C0S0	H0C0S1	60	+0.2047	+0.1566	+0.2512	51	4	5
H0C1S0	H0C1S1	60	+0.2317	+0.1874	+0.2786	54	2	4
H1C0S0	H1C0S1	60	+0.2511	+0.1938	+0.3078	57	1	2
H1C1S0	H1C1S1	60	+0.2283	+0.1832	+0.2762	57	3	0
```

[표 5-6] SCD 대응쌍 분석 요약 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-6_SCD_Paired | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
비교	쌍 수	Korean-character ratio 평균 변화	95% CI	증가 / 감소 / 동률
전체 SCD ON/OFF 대응	240	+0.2289	[+0.2051, +0.2532]	219 / 10 / 11
HyDE OFF 동일 문맥	120	+0.2182	[+0.1880, +0.2487]	분석 artifact 참조
```

[그림삽입: FINALDOCS/FIGURES/fig5_3_scd_language.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-7] HyDE·CAD strata별 SCD 적용에 따른 한국어 문자 비율 변화. 오차막대는 95% bootstrap 신뢰구간이다. [스타일=그림제목]

## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]

## 5.8 종합 논의 [스타일=절(1.1)]

CAD의 동일 문맥 비교에서는 faithfulness +0.0288, answer relevancy -0.0073이었고 두 신뢰구간은 0을 포함했다. 같은 입력에서 질의별 결과가 다양하게 분포했으며, CAD ON은 no-context branch 계산에 따라 generation duration도 증가했다. 따라서 CAD 분석은 품질 분포와 시간 비용을 함께 사용한다.

SCD는 직접 목표인 출력 언어 유지에서 가장 일관된 결과를 보였다. 240개 대응쌍의 Korean-character ratio는 +0.2289 증가했고, HyDE OFF 동일 문맥 120쌍에서도 +0.2182가 유지되었다. SCD 결과는 output-language control 지표를 중심으로 해석한다. 여덟 configuration의 최고 조건도 faithfulness, answer relevancy, context precision, context recall, Korean ratio에서 서로 달랐으며, configuration 선택은 사용 목적과 허용 지연, 출력 언어 요구에 따라 달라진다.

configuration 평균과 primary contrast는 서로 다른 역할을 가진다. 표 5-2의 평균은 각 조합의 기술통계를 보여주고, 표 5-3과 표 5-4의 primary contrast는 다른 요인을 고정한 상태에서 특정 요인의 ON/OFF 차이를 보여준다. H1C1S0의 faithfulness 평균과 H1C0S0의 answer relevancy 평균은 configuration 수준의 결과이며, HyDE·CAD paired contrast는 요인 수준의 결과다. 이 구분을 바탕으로 configuration은 목표 지표에 따라 선택한다.

문서별·질문유형별 부록 분석은 평균 아래의 차이를 탐색하는 용도다. 각 문서에 15개 질의가 배정되어 문서 단위의 방향을 확인할 수 있고, 질문 유형별 하위 집단은 후속 실험 가설을 구성하는 탐색 분석으로 사용한다. 본 연구가 제공하는 적용 기준은 질문 적합성이 중요할 때 HyDE의 answer relevancy와 검색 변화 사례를, 고정 근거의 생성 반영이 중요할 때 CAD의 same-context 결과와 시간을, 한국어 응답 유지가 중요할 때 SCD의 language ratio와 실제 답변을 함께 확인하는 방식이다.

[그림삽입: FINALDOCS/FIGURES/fig5_9_hyde_cad_strata.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 5-6] HyDE·CAD strata별 품질 지표 변화. strata 결과는 configuration-level descriptive pattern으로 해석한다. [스타일=그림제목]

## 5.9 연구의 한계 [스타일=절(1.1)]

본 연구는 네 문서와 60개 한국어 질의-대상문서 쌍, 하나의 generator, fixed CAD alpha=0.5를 사용한다. HyDE 비교는 한국어 질의 reformulation, hypothetical document 생성, dense retrieval 변경을 하나의 end-to-end 경로로 평가한다. Korean-character ratio는 출력 언어 성향을 측정하며 자연스러움·번역 충실도·내용 정확성은 후속 사람 평가 항목으로 남는다. RAGAS는 자동 judge protocol을 사용하며, faithfulness 분석은 다섯 결측 cell을 제외한 유효값으로 수행하였다. 독립 도메인, 다양한 generator·tokenizer, 사람 blind evaluation을 포함한 후속 검증은 외적 타당성을 확장하는 단계다.

# 6. 결론 [스타일=장(1.)]

본 연구는 한국어 질의로 영어 학술문서를 검색하고 한국어 답변을 생성하는 RAG 환경에서 HyDE, CAD, SCD를 각각 검색 표현, 문맥 기반 생성, 출력 언어 제어의 요인으로 비교하였다. 네 문서의 60개 질의-대상문서 쌍에 여덟 configuration을 적용한 480개 저장 generation record를 바탕으로, 연구 질문별 결과, 설계적 의미, 적용 시 선택 기준과 제한점을 다음 절에서 구분해 정리한다.

## 6.1 연구 질문별 최종 답 [스타일=절(1.1)]

첫 번째 연구 질문에 대해, HyDE는 CAD·SCD OFF의 60개 대응쌍에서 answer relevancy +0.0805와 95% bootstrap CI [+0.0110, +0.1514]라는 가장 명확한 양의 변화를 보였다. Faithfulness, context precision, context recall은 서로 다른 방향을 보여 HyDE의 주 결과가 answer relevancy에 집중되어 있음을 확인했다. 두 번째 질문에 대해, CAD는 동일 검색 문맥에서 faithfulness 평균이 +0.0288, answer relevancy 평균이 -0.0073이었고 두 interval은 0을 포함했다. CAD는 고정 근거에서 질의별 분포와 시간 비용을 함께 조정하는 generation-side 요인으로 나타났다.

세 번째 질문에 대해, SCD는 240개 대응쌍과 HyDE OFF 동일 문맥 120개 부분집합 모두에서 Korean-character ratio를 높였다. SCD의 직접 결과는 한국어 출력 유지 지표에서 확인되었다. 네 번째 질문에 대해, 여덟 configuration의 최고 조건은 지표별로 달랐다. 최종적으로 configuration은 검색 관련성, 근거 반영, 출력 언어, 허용 지연의 우선순위에 따라 선택한다.

## 6.2 실험 설계가 제공한 의미 [스타일=절(1.1)]

## 6.3 적용 시 configuration 선택 [스타일=절(1.1)]

한국어 질의-영어 문서 RAG의 configuration은 적용 환경의 목표 지표에 따라 선택한다. 설명형 질문의 질문 적합성과 검색 표현의 간극이 핵심이면 HyDE ON/OFF의 retrieved ID와 answer relevancy를 우선 점검한다. 이미 선택한 문맥에서 답변의 근거 반영을 조정하고자 하면 CAD의 same-context 분포와 generation duration을 함께 본다. 한국어 출력 유지가 핵심 요구라면 SCD의 ratio 변화와 함께 고유명사·인용·기술 용어의 보존 상태를 확인한다. 이 선택 절차는 각 환경에서 재측정할 지표와 사례를 정하는 실험 설계 기준으로 사용할 수 있다.

## 6.4 제한점과 후속 검증 [스타일=절(1.1)]

후속 연구는 관찰된 차이를 더 큰 표본과 독립 조건에서 다시 검토한다. HyDE에서는 한국어 reformulation, hypothetical document, dense retrieval 변경을 분리한 ablation을 수행할 수 있다. CAD에서는 alpha, 문맥 길이, 질문 복잡도와 시간 비용의 관계를 함께 조사할 수 있다. SCD에서는 Korean-character ratio에 더해 사람 평가로 언어 자연스러움, 번역 충실도, 전문 용어 보존을 확인할 수 있다. 또한 다른 전공 문서와 generator·tokenizer를 포함한 반복 실험은 현재 application study의 외적 타당성을 넓히는 단계다. 이러한 후속 검증은 60-query evidence에서 확인한 경향을 더 다양한 조건으로 확장한다.

# 참고문헌 [스타일=참고문헌제목]

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, 2020. [스타일=참고문헌리스트]

[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023. [스타일=참고문헌리스트]

[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024. [스타일=참고문헌리스트]

[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of the AAAI Conference on Artificial Intelligence*, Vol. 40, No. 37, pp. 31519–31526, 2026. [스타일=참고문헌리스트]

[5] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” *Findings of ACL*, 2024. [스타일=참고문헌리스트]

[6] S. E. Robertson et al., “Okapi at TREC-3,” *Text REtrieval Conference*, 1994. [스타일=참고문헌리스트]

[7] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009. [스타일=참고문헌리스트]

[8] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019. [스타일=참고문헌리스트]

[9] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024. [스타일=참고문헌리스트]

[10] V. Karpukhin et al., “Dense Passage Retrieval for Open-Domain Question Answering,” *Proceedings of EMNLP*, pp. 6769–6781, 2020. [스타일=참고문헌리스트]

[11] G. Izacard and E. Grave, “Leveraging Passage Retrieval with Generative Models for Open Domain Question Answering,” *Proceedings of EACL*, pp. 874–880, 2021. [스타일=참고문헌리스트]

[12] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024. [스타일=참고문헌리스트]

[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023. [스타일=참고문헌리스트]

[14] P. Sarthi et al., “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval,” *Proceedings of ICLR*, 2024. [스타일=참고문헌리스트]

[15] A. Asai et al., “Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection,” *Proceedings of ICLR*, 2024. [스타일=참고문헌리스트]

[16] S.-Q. Yan et al., “Corrective Retrieval Augmented Generation,” arXiv:2401.15884, 2024. [스타일=참고문헌리스트]

[17] Z. Zhao et al., “Retrieval-Augmented Generation for AI-Generated Content: A Survey,” arXiv:2402.19473, 2024. [스타일=참고문헌리스트]

[18] D. Shin et al., “Mi:dm 2.0 Korea-centric Bilingual Language Models,” arXiv:2601.09066, 2026. [스타일=참고문헌리스트]

[19] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997, 2023. [스타일=참고문헌리스트]

[20] N. Thakur et al., “BEIR: A Heterogeneous Benchmark for Zero-shot Evaluation of Information Retrieval Models,” *Proceedings of NeurIPS Datasets and Benchmarks Track*, 2021. [스타일=참고문헌리스트]

[21] N. Muennighoff et al., “MTEB: Massive Text Embedding Benchmark,” *Proceedings of EACL*, pp. 2014–2037, 2023. [스타일=참고문헌리스트]

[22] KT Tech Innovation Group, “Mi:dm K 2.5 Pro,” technical report, arXiv:2603.18788v2, 2026. [스타일=참고문헌리스트]

# 부록 A. 60개 질의 목록 [스타일=부록제목]

[표 A-1] 60개 질의-대상문서 쌍 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=Appendix_Queries | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
query ID	한국어 질문	대상 문서	유형	source page	answer span / GT
ext_cad_001	언어 모델이 생성 시 활용하는 prior knowledge와 context knowledge는 각각 어디에서 오는 정보입니까?	CAD	simple_qa	1	the context contains external knowledge; prior knowledge is encoded in the model parameters
ext_cad_002	CAD의 요약 실험에는 어떤 데이터셋과 평가 지표가 사용되었습니까?	CAD	section_result	3	CNN-DM and XSUM; ROUGE-L, BERT-Precision, and FactKB
ext_cad_003	CAD의 지식 충돌 실험에는 어떤 두 데이터셋이 사용되었고 각각 무엇을 평가합니까?	CAD	section_result	3	MemoTrap investigates memorization traps; NQ-Swap tests faithful answering from a modified reliable document.
ext_cad_004	NQ-Swap 데이터셋은 기존 Natural Questions의 정답과 문서를 어떤 방식으로 변형해 만들어집니까?	CAD	section_method	3	identify questions with named entity answers, find the supportive document, then replace the gold answer entity with a random entity
ext_cad_005	CAD 실험에서 요약 과제와 지식 충돌 과제에 사용한 α 값은 각각 얼마이며, 지식 충돌 과제에서 더 큰 값을 사용한 이유는 무엇입니까?	CAD	section_method	3	α = 0.5 for summarization and α = 1 for knowledge conflicts, where prior knowledge needs to be factored out more
ext_cad_006	CAD 논문의 베이스라인 디코딩은 요약 과제와 지식 충돌 과제에서 각각 어떤 샘플링 전략을 사용합니까?	CAD	section_method	3	greedy decoding for knowledge conflict tasks and top-p sampling with p=0.9 for summarization tasks
ext_cad_007	CAD가 실험에서 적용된 사전학습 및 instruction-finetuned 언어 모델 계열은 무엇입니까?	CAD	simple_qa	3	OPT, GPT-Neo, LLaMA, and FLAN-T5
ext_cad_008	지식 충돌 과제에서 모델 크기가 커질수록 CAD의 성능 향상 폭은 어떤 경향을 보였습니까?	CAD	section_result	5	the gain increases as the model size grows
ext_cad_009	LLaMA-30B에 CAD를 적용했을 때 XSUM에서 ROUGE-L, factKB, BERT-P 점수는 regular decoding과 비교해 어떻게 달라졌습니까?	CAD	section_result	4	Regular: 18.7, 47.7, 87.1; CAD: 22.0, 66.4, 90.3
ext_cad_010	외부 컨텍스트가 생성 토큰과 조건부 독립이라면 α가 0이 아니어도 CAD의 출력 분포에는 어떤 영향이 있습니까?	CAD	section_method	2	even a non-zero α would not have an impact to the original output distribution
ext_cad_011	CAD는 특정 instruction-finetuned 언어 모델에만 제한됩니까, 아니면 어떤 언어 모델에도 적용 가능한 디코딩 전략입니까?	CAD	simple_qa	6	a decoding strategy applicable to any LM
ext_midm_001	Mi:dm K 2.5 Pro의 학습 데이터는 어떤 세 가지 경로를 통해 확보됩니까?	Mi:dm K 2.5 Pro Technical Report	section_method	3	licensed proprietary datasets, public datasets that permit commercial use, and in-house synthetic data
ext_midm_002	Mi:dm K 2.5 Pro는 한국어 중심 학습을 유지하기 위해 다국어 데이터를 한국어 코퍼스 대비 어느 정도 비율로 제한하며, 그 이유는 무엇입니까?	Mi:dm K 2.5 Pro Technical Report	section_method	3	3–10% of the Korean corpus, to encourage cross-lingual transfer without diluting the Korean-language focus
ext_midm_003	응답 스타일 재작성 후 평균 응답 길이는 몇 % 증가했고, bullet_count=0인 응답의 비율은 어떻게 변했습니까?	Mi:dm K 2.5 Pro Technical Report	section_result	8	mean response length increases by 256.70%; bullet_count = 0 drops from 82.8% to 3.9%
ext_midm_004	Mi:dm K 2.5 Pro의 한국어 멀티턴 대화 데이터는 어떤 세 가지 차원을 기준으로 고품질 대화를 설계합니까?	Mi:dm K 2.5 Pro Technical Report	section_method	15	interaction structure, topic and task, and persona
ext_midm_005	Fusion SFT 단계에서 non-reasoning 데이터의 비중을 높인 목적은 무엇이며, 어떤 유형의 과제를 특히 보강합니까?	Mi:dm K 2.5 Pro Technical Report	section_method	21	to favor versatile conversational alignment; creative writing, translation, and general question answering
ext_midm_006	Fully asynchronous GSPO 학습은 synchronous 방식과 비교해 step time과 token throughput을 각각 어느 정도 개선했습니까?	Mi:dm K 2.5 Pro Technical Report	section_result	23	reduces step time by approximately 15% and improves token throughput by approximately 30%
ext_midm_007	LLM-as-a-Judge 기반 reward signal은 사람의 평가와 어느 정도의 일치율을 보였습니까?	Mi:dm K 2.5 Pro Technical Report	simple_qa	24	an agreement rate of 91%
ext_midm_008	Reasoning-enabled 평가에서 Mi:dm K 2.5 Pro가 HumanEval+와 τ²-Bench Telecom에서 기록한 점수는 각각 얼마입니까?	Mi:dm K 2.5 Pro Technical Report	section_result	25	HumanEval+ 92.07% and τ²-Bench Telecom 89%
ext_midm_009	한국어 red-teaming 평가에서 Mi:dm K 2.5 Pro의 Attack Success Rate는 얼마였으며 비교 모델들 가운데 어떤 수준이었습니까?	Mi:dm K 2.5 Pro Technical Report	section_result	31	ASR of 36.3%, the lowest attack success rate among the compared models
ext_rag_001	Advanced RAG의 pre-retrieval 단계는 인덱스와 사용자 질의를 각각 어떤 방향으로 최적화합니까?	RAG Survey	section_method	4	optimizing the indexing structure and the original query
ext_rag_002	Advanced RAG의 post-retrieval 단계에서 사용되는 두 가지 핵심 방법은 무엇입니까?	RAG Survey	section_method	4	rerank chunks and context compressing
ext_rag_003	RAG에서 큰 청크와 작은 청크를 사용할 때 각각 어떤 장단점이 발생합니까?	RAG Survey	simple_qa	8	Larger chunks can capture more context, but they also generate more noise; smaller chunks may not fully convey the necessary context, but have less noise.
ext_rag_004	문서 청크에 타임스탬프 같은 메타데이터를 부여하면 time-aware RAG는 최신 정보를 어떻게 우선할 수 있습니까?	RAG Survey	section_method	8	Assigning different weights to document timestamps during retrieval can achieve time-aware RAG, ensuring the freshness of knowledge and avoiding outdated information.
ext_rag_005	Reverse HyDE는 문서로부터 가상의 질문을 생성해 원래 질문과 답변 사이의 의미적 간극을 어떻게 줄입니까?	RAG Survey	section_method	8	using LLM to generate questions that can be answered by the document, then calculating the similarity between the original question and the hypothetical question
ext_rag_006	Multi-Query와 Sub-Query 방식은 원래 질의를 확장하거나 분해하는 방식에서 어떻게 다릅니까?	RAG Survey	section_method	8	Multi-Query expands queries via LLMs for parallel execution; Sub-Query decomposes a complex question into simpler sub-questions.
ext_rag_007	Iterative Retrieval, Recursive Retrieval, Adaptive Retrieval은 검색을 반복하거나 중단하는 방식에서 각각 어떻게 구분됩니까?	RAG Survey	section_method	11	Iterative retrieval alternates retrieval and generation; recursive retrieval refines queries and breaks problems into sub-problems; adaptive retrieval determines whether retrieval is necessary and when to stop.
ext_rag_008	RAG 평가에서 요구되는 네 가지 핵심 능력은 무엇입니까?	RAG Survey	section_result	12	noise robustness, negative rejection, information integration, and counterfactual robustness
ext_rag_009	RAG 평가에서 Negative Rejection은 어떤 능력을 측정합니까?	RAG Survey	simple_qa	12	refraining from responding when the retrieved documents do not contain the necessary knowledge to answer a question
ext_rag_010	RAG와 파인튜닝을 비교할 때 지식 업데이트의 동적 특성과 해석 가능성 측면에서 RAG가 갖는 특징은 무엇입니까?	RAG Survey	simple_qa	5	real-time knowledge updates and effective utilization of external knowledge sources with high interpretability
ext_raptor_001	RAPTOR는 초기 문서를 몇 토큰 길이의 청크로 나누며, 문장이 청크 경계를 넘을 때 어떻게 처리합니까?	RAPTOR	section_method	3	length 100; if a sentence exceeds the 100-token limit, the entire sentence is moved to the next chunk
ext_raptor_002	RAPTOR의 leaf node를 만들 때 텍스트 임베딩에 사용한 모델은 무엇입니까?	RAPTOR	simple_qa	3	SBERT, a BERT-based encoder (multi-qa-mpnet-base-cos-v1)
ext_raptor_003	RAPTOR의 GMM 클러스터링 전에 UMAP을 사용하는 이유는 무엇입니까?	RAPTOR	section_method	4	to mitigate the challenge of high-dimensional vector embeddings by dimensionality reduction
ext_raptor_004	RAPTOR의 클러스터링 과정에서 Bayesian Information Criterion(BIC)은 어떤 결정을 내리는 데 사용됩니까?	RAPTOR	section_method	4	to determine the optimal number of clusters
ext_raptor_005	RAPTOR에서 클러스터별 요약을 생성하는 데 사용한 언어 모델은 무엇입니까?	RAPTOR	simple_qa	4	gpt-3.5-turbo
ext_raptor_006	RAPTOR의 트리 구축 비용은 문서 길이가 증가할 때 build time과 token expenditure 측면에서 어떻게 확장됩니까?	RAPTOR	section_result	16	both build time and token expenditure scale linearly with document length
ext_raptor_007	QASPER 데이터셋은 몇 개의 질문과 NLP 논문으로 구성되며, 논문에서는 어떤 지표로 성능을 평가합니까?	RAPTOR	section_result	6	5,049 questions across 1,585 NLP papers; accuracy is measured using standard F1
ext_raptor_008	QuALITY-HARD는 일반 QuALITY 질문 중 어떤 기준을 만족하는 질문들로 구성됩니까?	RAPTOR	simple_qa	6	questions that a majority of human annotators answered incorrectly in a speed-setting
ext_raptor_009	QASPER에서 RAPTOR의 F1 Match 점수는 GPT-3, GPT-4, UnifiedQA를 사용할 때 각각 얼마였습니까?	RAPTOR	section_result	7	53.1%, 55.7%, and 36.6%, respectively
ext_raptor_010	QuALITY의 한 스토리에서 RAPTOR가 전체 3개 계층을 검색했을 때의 성능은 leaf node 한 계층만 검색했을 때와 어떻게 달라졌습니까?	RAPTOR	section_result	9	57.9 with one leaf layer versus 73.68 with all three layers
ext_raptor_011	Cinderella 사례의 정성 분석에서 RAPTOR의 tree-based retrieval이 DPR보다 주제형·멀티홉 질문에 유리했던 이유는 무엇입니까?	RAPTOR	simple_qa	20	RAPTOR retrieves relevant information across tree layers, while DPR retrieves detailed descriptions of a narrow subset of the story
track1_0009	RAG가 LLM에서 사실적으로 부정확한 콘텐츠 생성을 줄이는 데 어떻게 기여합니까?	RAG Survey	simple_qa	1	By referencing external knowledge, RAG effectively reduces the problem of generating factually incorrect content.
track1_0010	RAG의 Naive RAG 방법론은 어떤 과정으로 구성되어 있습니까?	RAG Survey	section_method	3	The Naive RAG follows a traditional process that includes indexing, retrieval, and generation, which is also characterized as a 'Retrieve-Read' framework.
track1_0012	RAG 시스템은 지식 집약적인 작업에서 어떻게 유리합니까?	RAG Survey	section_abstract	1	This enhances the accuracy and credibility of the generation, particularly for knowledge-intensive tasks, and allows for continuous knowledge updates and integration of domain-specific information.
track1_0015	RAG 프로세스에서 핵심적인 역할을 하는 세 가지 구성 기술은 무엇인가요?	RAG Survey	crosslingual_ko	2	the aspects of Retrieval, Generation and Augmentation
track1_0016	RAG 방법론의 평가 방법은 어떻게 요약되어 있습니까?	RAG Survey	decoder_ablation	2	We have summarized the current assessment methods of RAG, covering 26 tasks, nearly 50 datasets, outlining the evaluation objectives and metrics, as well as the current evaluation benchmarks and tools.
track1_0019	LLaMA-30B 모델에 CAD를 적용했을 때 CNN-DM 데이터셋에서 어떤 성과가 있었나요?	CAD	section_result	3	Specifically, when applied to LLAMA-30B in CNN-DM, CAD leads to 21% increase in ROUGE-L, 14.3% increase in factKB and 7.8% increase in BERT-P.
track1_0021	CAD는 어떻게 잘못된 정보 생성을 줄이나요?	CAD	numeric_or_factual_hallucination	2	These results demonstrate the potential of CAD in mitigating hallucinations in text generation and overriding prior knowledge with reliable and trusted information.
track1_0023	CAD는 언어 모델이 생성하는 요약문의 사실적 정확성을 향상시키나요?	CAD	crosslingual_ko	1	Experimental results from summarization tasks show that context-aware decoding significantly enhances the generation faithfulness of various vanilla LMs including OPT (Zhang et al., 2022), GPT-Neo (Black et al., 2021), LLaMA (Touvron et al., 2023) and instruction-finetuned LMs such as FLAN (Chung et al., 2021).
track1_0024	CAD를 적용하지 않은 경우와 비교했을 때, knowledge conflict QA 데이터셋에서 LLaMA-30B의 성능은 어떻게 변화하나요?	CAD	decoder_ablation	2	CAD brings a 2.9x improvement to LLaMA-30B on a knowledge conflicts QA dataset (Longpre et al., 2021).
track1_0025	RAPTOR 모델이 QuALITY 벤치마크에서 기존 성능을 얼마나 개선했나요?	RAPTOR	simple_qa	1	we can improve the best performance on the QuALITY benchmark by 20% in absolute accuracy.
track1_0026	RAPTOR의 트리 구조는 텍스트 클러스터링을 통해 어떻게 구축되나요?	RAPTOR	section_method	2	RAPTOR recursively clusters chunks of text based on their vector embeddings and generates text summaries of those clusters, constructing a tree from the bottom up.
track1_0027	RAPTOR가 여러 QA 작업에서 달성한 결과는 무엇인가요?	RAPTOR	section_result	2	RAPTOR coupled with GPT-4, and sometimes even with UnifiedQA, gives new state-of-the-art results on three QA tasks: free text response questions on books and movies (NarrativeQA, Koˇcisk`y et al. 2018), full-text NLP papers (QASPER, Dasigi et al. 2021), and multiple-choice questions based on medium-length passages (QuALITY, Pang et al. 2022).
track1_0032	RAPTOR의 계층에서 검색된 노드가 어느 계층에서 오는지에 대한 연구 결과는 무엇인가요?	RAPTOR	decoder_ablation	22	We observe that between 18.5% to 57% of the retrieved nodes come from non-leaf nodes.
track1_0033	Mi:dm K 2.5 Pro 모델의 파라미터 수는 몇 개입니까?	Mi:dm K 2.5 Pro Technical Report	simple_qa	2	32B parameters
track1_0034	Mi:dm K 2.5 Pro의 방법론에서 AST 분석은 어떤 목적으로 사용됩니까?	Mi:dm K 2.5 Pro Technical Report	section_method	1	abstract syntax tree (AST) analysis for code
track1_0035	Mi:dm K 2.5 Pro 모델은 어떤 한국어 벤치마크에서 최첨단 결과를 달성했습니까?	Mi:dm K 2.5 Pro Technical Report	section_result	1	sets state-of-the-art results on Korean-specific benchmarks
track1_0036	Mi:dm K 2.5 Pro가 해결하려는 주요 문제는 무엇입니까?	Mi:dm K 2.5 Pro Technical Report	section_abstract	1	address enterprise-grade complexity through reasoning-focused optimization
track1_0037	Mi:dm K 2.5 Pro 모델의 컨텍스트 윈도우(context window) 길이는 얼마인가요?	Mi:dm K 2.5 Pro Technical Report	numeric_or_factual_hallucination	1	128K token context window
track1_0040	Mi:dm K 2.5 Pro의 사후 훈련 파이프라인에서 모델 병합은 어떤 역할을 합니까?	Mi:dm K 2.5 Pro Technical Report	decoder_ablation	2	improve training stability and achieve balanced performance across complex reasoning, coding, instruction following, and agentic task execution
```

# 부록 B. 추가 증빙 화면 [스타일=부록제목]

# 부록 B. 추가 정량 분석 [스타일=부록제목]

문서별·질문 유형별 분석과 strata별 결과는 표본 수를 함께 제시하며 탐색적으로 해석한다.

[표 B-1] 문서별 탐색 분석 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=Appendix_Paper | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
대상 문서	요인	지표	n	평균 변화
Mi:dm K 2.5 Pro Technical Report	HyDE	faithfulness	15	0.0007
Mi:dm K 2.5 Pro Technical Report	HyDE	answer_relevancy	15	0.0994
Mi:dm K 2.5 Pro Technical Report	HyDE	context_precision	15	-0.0145
Mi:dm K 2.5 Pro Technical Report	HyDE	context_recall	15	0.1333
Mi:dm K 2.5 Pro Technical Report	CAD	faithfulness	15	0.0081
Mi:dm K 2.5 Pro Technical Report	CAD	answer_relevancy	15	0.0339
Mi:dm K 2.5 Pro Technical Report	CAD	context_precision	15	0
Mi:dm K 2.5 Pro Technical Report	CAD	context_recall	15	0
CAD	HyDE	faithfulness	15	-0.0491
CAD	HyDE	answer_relevancy	15	-0.0019
CAD	HyDE	context_precision	15	-0.0823
CAD	HyDE	context_recall	15	-0.0667
CAD	CAD	faithfulness	15	0.0664
CAD	CAD	answer_relevancy	15	-0.0099
CAD	CAD	context_precision	15	-0.0552
CAD	CAD	context_recall	15	-0.0667
RAG Survey	HyDE	faithfulness	15	0.1575
RAG Survey	HyDE	answer_relevancy	15	0.1314
RAG Survey	HyDE	context_precision	15	0.0036
RAG Survey	HyDE	context_recall	15	0.0667
RAG Survey	CAD	faithfulness	13	-0.0416
RAG Survey	CAD	answer_relevancy	15	-0.1004
RAG Survey	CAD	context_precision	15	0.0074
RAG Survey	CAD	context_recall	15	0
RAPTOR	HyDE	faithfulness	15	0.0652
RAPTOR	HyDE	answer_relevancy	15	0.093
RAPTOR	HyDE	context_precision	15	-0.0441
RAPTOR	HyDE	context_recall	15	-0.1333
RAPTOR	CAD	faithfulness	15	0.0731
RAPTOR	CAD	answer_relevancy	15	0.047
RAPTOR	CAD	context_precision	15	0.0108
RAPTOR	CAD	context_recall	15	0
```

[표 B-2] 질문 유형별 탐색 분석 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=Appendix_QueryType | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
질문 유형	요인	지표	n	평균 변화
crosslingual_ko	HyDE	faithfulness	2	0.1282
crosslingual_ko	HyDE	answer_relevancy	2	0.0899
crosslingual_ko	HyDE	context_precision	2	0.0528
crosslingual_ko	HyDE	context_recall	2	0
crosslingual_ko	CAD	faithfulness	2	-0.0333
crosslingual_ko	CAD	answer_relevancy	2	-0.0794
crosslingual_ko	CAD	context_precision	2	-0.077
crosslingual_ko	CAD	context_recall	2	0
decoder_ablation	HyDE	faithfulness	4	-0.1266
decoder_ablation	HyDE	answer_relevancy	4	0.0059
decoder_ablation	HyDE	context_precision	4	-0.0834
decoder_ablation	HyDE	context_recall	4	0
decoder_ablation	CAD	faithfulness	4	-0.0767
decoder_ablation	CAD	answer_relevancy	4	0.039
decoder_ablation	CAD	context_precision	4	0
decoder_ablation	CAD	context_recall	4	0
numeric_or_factual_hallucination	HyDE	faithfulness	2	-0.1357
numeric_or_factual_hallucination	HyDE	answer_relevancy	2	0.0711
numeric_or_factual_hallucination	HyDE	context_precision	2	0.0563
numeric_or_factual_hallucination	HyDE	context_recall	2	0
numeric_or_factual_hallucination	CAD	faithfulness	2	-0.05
numeric_or_factual_hallucination	CAD	answer_relevancy	2	-0.0606
numeric_or_factual_hallucination	CAD	context_precision	2	0
numeric_or_factual_hallucination	CAD	context_recall	2	0
section_abstract	HyDE	faithfulness	2	0.0312
section_abstract	HyDE	answer_relevancy	2	-0.0447
section_abstract	HyDE	context_precision	2	-0.2334
section_abstract	HyDE	context_recall	2	0
section_abstract	CAD	faithfulness	2	-0.2188
section_abstract	CAD	answer_relevancy	2	-0.4501
section_abstract	CAD	context_precision	2	0
section_abstract	CAD	context_recall	2	0
section_method	HyDE	faithfulness	20	0.1295
section_method	HyDE	answer_relevancy	20	0.2685
section_method	HyDE	context_precision	20	-0.0594
section_method	HyDE	context_recall	20	0.1
section_method	CAD	faithfulness	19	0.1284
section_method	CAD	answer_relevancy	20	0.1157
section_method	CAD	context_precision	20	0
section_method	CAD	context_recall	20	0
section_result	HyDE	faithfulness	16	0.0244
section_result	HyDE	answer_relevancy	16	-0.0364
section_result	HyDE	context_precision	16	-0.0029
section_result	HyDE	context_recall	16	0
section_result	CAD	faithfulness	16	0.0014
section_result	CAD	answer_relevancy	16	-0.0727
section_result	CAD	context_precision	16	0.0045
section_result	CAD	context_recall	16	-0.0625
simple_qa	HyDE	faithfulness	14	0.0066
simple_qa	HyDE	answer_relevancy	14	-0.0154
simple_qa	HyDE	context_precision	14	-0.0174
simple_qa	HyDE	context_recall	14	-0.1429
simple_qa	CAD	faithfulness	13	0.0094
simple_qa	CAD	answer_relevancy	14	-0.0405
simple_qa	CAD	context_precision	14	-0.0337
simple_qa	CAD	context_recall	14	0
```

# 부록 C. Artifact provenance [스타일=부록제목]

[표 C-1] 주요 연구 artifact provenance [스타일=표제목]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
artifact	상대 경로	역할	SHA-256
main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl	experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl	60-query source artifact	916817150e40e0d2803f7e145633d13737c2304d17efdc4d42dc65cb4ed007d5
extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl	experiments/results/extended_validation/extended-hyde-cad-scd-reference-scd__extended_validation_questions__extended_validation_generation.jsonl	60-query source artifact	93c0932f4f5071bf726e4cd5a31c7a9cc02ef243775fdef99a1a0d486b51f41e
merged.ragas_scores.json	experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json	60-query source artifact	700a2932a03bf615aab849297d6114968aafeff9bd49c0dfa0659050e8a4ef08
merged.ragas_scores.json	experiments/results/evaluation/ext60_gpt4o/merged.ragas_scores.json	60-query source artifact	fc705e3d3580246d53f17ff179027c2b43f3584f785fea3f047934ff2178476b
decoder_main_queries.json	experiments/data/query_splits/decoder_main_queries.json	60-query source artifact	378a7a3e6ffb446759b228943010e2a4861d4efb9626f3d066dae40d43410ff5
extended_validation_questions.json	experiments/data/query_splits/extended_validation_questions.json	60-query source artifact	91e9c1da0dec40c32a8370881cf708b2b4229a7d40d15206ab5f1cd78803061c
extended_validation_60_analysis.json	experiments/results/analysis/extended_validation_60_analysis.json	60-query source artifact	50870fc6c48407b22daf32861465accd459bd3972e5a80c58a3bb822d23a8e4d
```

# 부록 D. 저장 artifact 점검 절차 [스타일=부록제목]

[표 D-1] 저장 artifact 기반 점검 절차 [스타일=표제목]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
점검 단계	실제 경로 또는 명령	입력	확인 결과	목적
질의 감사	FINALDOCS/APPENDIX/QUERY_60_AUDIT.md	동결 query split 감사 결과	60개 질의 목록	60개 질의와 source metadata 확인
수치 대조	FINALDOCS/DATA/EXPERIMENT_60_VALIDATION.md	해시로 고정한 저장 artifact	검증 범위·핵심 수치	표와 본문 수치 대조
표 확인	FINALDOCS/TABLES/TABLES_60Q.xlsx	17개 HWP 이전용 sheet	HWP 표 이전	표 제목·값·출처 확인
제출 그림 확인	FINALDOCS/FIGURES	최종 10개 PNG	HWP 삽입 그림	구조·통계 그림의 고정 제출본 확인
패키지 검증	python -X utf8 FINALDOCS/VALIDATION/verify_finaldocs_60q.py	FINALDOCS	PASS/FAIL	원고·표·그림·출처 정합성 확인
```
