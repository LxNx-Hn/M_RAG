# 졸업자격실험보고서 한글 이전용 최종 원고

이 파일은 원본 한글 템플릿의 글꼴·문단 모양을 수정하지 않고 내용을 옮기기 위한 원고이다. 대괄호 안의 스타일 이름은 해당 문단에 적용할 템플릿 스타일이다. 저자·지도교수·제출일·인준자·페이지 번호는 제출자가 입력한다. 연구 보고서의 성격에 맞추어 유스케이스 항목은 연구 요구사항, 실험 아키텍처, 데이터 흐름으로 구성하였다.

---

한국어 질의 기반 영어 학술문서 RAG에서 HyDE·CAD·SCD 조합 실험 [스타일=논문제목]

Combination Experiments of HyDE, CAD, and SCD in RAG over English Academic Documents with Korean Queries

지도교수: [지도교수 이름]

컴퓨터공학과

동국대학교 WISE캠퍼스

[학생 이름]

[제출 연도]

---

졸업자격실험보고서

한국어 질의 기반 영어 학술문서 RAG에서 HyDE·CAD·SCD 조합 실험

Combination Experiments of HyDE, CAD, and SCD in RAG over English Academic Documents with Korean Queries

[학생 이름]

지도교수 [지도교수 이름]

본 보고서를 졸업자격 실험보고서로 제출함.

[제출 연도]년 00월 00일

[학생 이름]의 졸업자격 실험보고 통과를 인준함.

[제출 연도]년 00월 00일

주심                    (인)

부심                    (인)

동국대학교 컴퓨터공학과

---

## 초록

대규모 언어모델(Large Language Model, LLM)을 활용한 학술정보 질의응답에서는 답변 생성에 외부 문서의 근거를 활용하는 것이 중요하다. Retrieval-Augmented Generation(RAG)은 관련 문서를 검색하여 생성 과정에 제공하지만, 한국어 질의로 영어 학술문서를 대상으로 하는 환경에서는 질의와 문서 간 언어·표현 차이, 검색된 근거의 생성 단계 활용, 영어 문맥에 따른 출력 언어 이탈과 같은 문제가 함께 나타날 수 있다. 본 연구에서는 이러한 문제와 관련된 HyDE(Hypothetical Document Embeddings), CAD(Context-Aware Decoding), SCD(Soft Constrained Decoding)를 각각 검색 확장, 문맥 기반 생성 제어, 출력 언어 제어의 실험 요인으로 설정하였다. [스타일=본문]

세 기법의 적용 여부를 조합한 2×2×2 실험 구성을 RAG-Cube로 지칭하고, 동일한 Paper-RAG backbone에서 19개의 한국어 질의에 8개 조합을 적용하여 총 152개의 답변을 생성하였다. HyDE와 CAD는 각각 다른 요인의 영향을 배제한 조건에서 비교하였으며, SCD는 동일 질의와 HyDE·CAD 조건으로 대응되는 76개 on/off 쌍을 이용하여 한국어 출력 유지 정도를 분석하였다. 또한 SCD의 품질 변화가 평가 언어와 평가 모델에 따라 달라지는지를 확인하기 위해 동일 문맥을 사용하는 38개 대응쌍에 대해 영어·한국어 정규화 평가와 두 평가 모델을 이용한 추가 검증을 수행하였다. [스타일=본문]

실험 결과, HyDE 적용 시 CAD와 SCD를 사용하지 않은 조건에서 answer relevancy가 평균 +0.0303 증가하였으나, faithfulness, context precision, context recall의 차이는 명확하지 않았다. CAD는 동일한 검색 문맥을 사용한 조건에서 faithfulness 차이가 +0.0023으로 나타났으며, 본 실험에서는 명확한 품질 개선이 확인되지 않았다. 반면 SCD는 76개 대응쌍에서 한국어 문자 비율을 평균 +0.2203 높였고, 68개 쌍에서 한국어 비율이 증가하였다. 한국어 문자 비율 0.5 미만으로 정의한 언어 이탈 출력은 26개에서 12개로 감소하였다. 다만 SCD 적용에 따른 답변 품질 차이는 영어·한국어 평가와 두 평가 모델에서 일관되게 재현되지 않았다. [스타일=본문]

이 결과는 한국어 질의 기반 영어 학술문서 RAG 환경에서 HyDE, CAD, SCD가 서로 다른 목적 지표에 작용하며, 검색 확장, 근거 기반 생성, 출력 언어 유지라는 각 목적에 따라 적용 결과를 구분하여 검토할 필요가 있음을 보여준다. [스타일=본문]

주요어: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, 교차언어 검색, 학술정보 질의응답, 언어 이탈

## Abstract

In academic question answering with large language models, generated answers need to use evidence from external documents. Retrieval-Augmented Generation retrieves relevant documents and supplies them during generation. In a setting where Korean queries target English academic documents, however, differences in language and expression, use of retrieved evidence during generation, and output-language drift can occur together. This study uses Hypothetical Document Embeddings, Context-Aware Decoding, and Soft Constrained Decoding as experimental factors for retrieval expansion, context-aware generation control, and output-language control, respectively. [스타일=본문]

The 2×2×2 combination of the three factors is referred to as RAG-Cube. Using a fixed Paper-RAG backbone, eight configurations were applied to 19 Korean queries, producing 152 answers. HyDE and CAD were compared under controlled conditions, and SCD was analyzed using 76 matched on/off pairs. An additional symmetric evaluation used 38 identical-context pairs, two normalization languages, and two evaluation models. HyDE increased mean answer relevancy by 0.0303 when CAD and SCD were disabled, while the remaining quality differences were inconclusive. CAD produced a faithfulness difference of 0.0023 under identical contexts, without a clear quality gain. SCD increased the Korean-character ratio by 0.2203 on average and reduced language-drift outputs from 26 to 12, although its answer-quality differences were not consistently reproduced across evaluation languages and models. The results show that the three factors should be examined according to their respective objectives in Korean-query RAG over English academic documents. [스타일=본문]

Keywords: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, cross-lingual retrieval, academic question answering, language drift

---

목    차 [스타일=목차제목]

1. 서론 [스타일=목차리스트(장)]

1.1 연구배경 및 목적 [스타일=목차리스트(절)]

1.2 연구범위 [스타일=목차리스트(절)]

2. 이론적 배경 [스타일=목차리스트(장)]

2.1 Retrieval-Augmented Generation [스타일=목차리스트(절)]

2.2 Hybrid Retrieval과 재정렬 [스타일=목차리스트(절)]

2.3 Hypothetical Document Embeddings [스타일=목차리스트(절)]

2.4 Context-Aware Decoding [스타일=목차리스트(절)]

2.5 Soft Constrained Decoding [스타일=목차리스트(절)]

2.6 RAG 평가 [스타일=목차리스트(절)]

3. 시스템 설계 [스타일=목차리스트(장)]

3.1 연구 및 실험 요구사항 [스타일=목차리스트(절)]

3.2 아키텍처 설계 [스타일=목차리스트(절)]

3.3 상세설계 [스타일=목차리스트(절)]

4. 프로그램 구현 [스타일=목차리스트(장)]

4.1 시스템 환경 [스타일=목차리스트(절)]

4.2 시스템 구성 [스타일=목차리스트(절)]

4.3 시스템 구현 [스타일=목차리스트(절)]

5. 실험 [스타일=목차리스트(장)]

5.1 실험 대상과 구성 [스타일=목차리스트(절)]

5.2 평가 방법 [스타일=목차리스트(절)]

5.3 HyDE와 CAD 결과 [스타일=목차리스트(절)]

5.4 SCD의 한국어 출력 유지 결과 [스타일=목차리스트(절)]

5.5 SCD 대칭 품질 평가 [스타일=목차리스트(절)]

5.6 결과 종합 및 한계 [스타일=목차리스트(절)]

6. 결론 [스타일=목차리스트(장)]

참고문헌

---

그 림 목 차 [스타일=목차제목]

[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경 [스타일=표/그림리스트]

[그림 3-1] HyDE·CAD·SCD의 2×2×2 RAG-Cube 실험 구성 [스타일=표/그림리스트]

[그림 3-2] 고정 Paper-RAG backbone과 실험 요인의 적용 위치 [스타일=표/그림리스트]

[그림 5-1] 실험 요인별 비교 및 평가 설계 [스타일=표/그림리스트]

[그림 5-2] HyDE와 CAD 적용에 따른 품질 지표의 대응 평균 차이 [스타일=표/그림리스트]

[그림 5-3] SCD 적용 전후의 한국어 문자 비율과 언어 이탈 수 [스타일=표/그림리스트]

[그림 5-4] 평가 언어와 평가 모델에 따른 SCD 품질 차이 [스타일=표/그림리스트]

---

표 목 차 [스타일=목차제목]

[표 3-1] 연구 및 실험 요구사항 [스타일=표/그림리스트]

[표 3-2] RAG-Cube의 여덟 가지 실험 조건 [스타일=표/그림리스트]

[표 4-1] 실험 실행 환경 [스타일=표/그림리스트]

[표 4-2] 고정 Paper-RAG backbone 설정 [스타일=표/그림리스트]

[표 4-3] 최종 생성 실행 시간 [스타일=표/그림리스트]

[표 5-1] 실험 대상 문서와 질의 수 [스타일=표/그림리스트]

[표 5-2] HyDE 적용에 따른 품질 지표 차이 [스타일=표/그림리스트]

[표 5-3] CAD 적용에 따른 품질 지표 차이 [스타일=표/그림리스트]

[표 5-4] 설정별 한국어 문자 비율과 언어 이탈 수 [스타일=표/그림리스트]

[표 5-5] SCD의 평가 언어·모델별 품질 차이 [스타일=표/그림리스트]

---

# 1. 서론 [스타일=장(1.)]

## 1.1 연구배경 및 목적 [스타일=절(1.1)]

대규모 언어모델은 자연어 질의를 이해하고 문장 형태의 응답을 생성하는 능력을 바탕으로 정보 탐색과 질의응답에 활용되고 있다. 학술정보 활용에서도 사용자가 논문 전체를 순차적으로 읽는 방식에 더해, 자연어 질문을 통해 필요한 방법론, 실험 조건, 수치와 결론을 확인하는 방식이 가능해졌다. 그러나 언어모델이 내부 학습 정보만으로 답변하면 사용자가 지정한 논문의 내용을 직접적인 근거로 활용하기 어렵고, 생성된 설명이 논문의 어느 부분에 의해 뒷받침되는지 확인하기도 어렵다. [스타일=본문]

Retrieval-Augmented Generation(RAG)은 사용자의 질의와 관련된 외부 문서를 검색하고, 검색 결과를 생성 모델의 입력 문맥으로 제공하는 구조이다[1]. 이 구조는 특정 문서의 최신 정보와 세부 내용을 답변에 활용할 수 있게 한다. 한편 최종 답변의 품질은 검색과 생성의 두 과정에 함께 영향을 받는다. 필요한 근거가 검색되지 않으면 생성 모델이 해당 내용을 이용할 수 없으며, 적절한 근거가 제공되어도 생성 과정에서 그 근거가 충분히 반영되지 않을 수 있다. [스타일=본문]

본 연구가 다루는 환경은 한국어로 질문하고 영어로 작성된 학술·기술 문서에서 근거를 검색하여 한국어로 답변하는 질의응답이다. 이 환경에서는 한국어 질의와 영어 학술문장 사이의 표현 차이가 검색에 영향을 줄 수 있다. 검색된 영어 문맥은 생성 모델의 답변 내용뿐 아니라 출력 언어에도 영향을 주어, 한국어로 요청한 답변이 영어로 이어지는 언어 이탈을 일으킬 수 있다. 따라서 검색 표현, 검색 근거의 생성 단계 활용, 출력 언어 유지라는 세 지점을 함께 관찰할 필요가 있다. [스타일=본문]

본 연구에서는 HyDE[2], CAD[3], SCD[4]를 각각 검색 확장, 문맥 기반 생성 제어, 출력 언어 제어의 실험 요인으로 적용하였다. HyDE는 한국어 질의를 영어 학술문장에 가까운 가상 문서로 확장하여 dense 검색에 사용한다. CAD는 문맥이 있는 생성 분포와 문맥이 없는 생성 분포를 대조하여 검색 문맥의 영향을 토큰 생성에 반영한다. SCD는 한국어 목표 토큰과 영어 비목표 토큰의 점수를 조정하여 출력 언어 유지를 돕는다. 세 요인은 RAG 파이프라인의 서로 다른 위치에서 동작한다. [스타일=본문]

세 기법의 적용 여부를 독립적인 이진 요인으로 두면 2×2×2의 여덟 가지 실험 조건이 만들어진다. 본 연구에서는 이 실험 구성을 RAG-Cube로 지칭한다. 동일한 검색·생성 backbone을 유지한 상태에서 네 개의 영어 학술·기술 문서에 관한 한국어 질의 19개를 모든 조건에 적용하고, 총 152개의 답변을 생성하였다. 연구의 목적은 각 요인의 적용 여부에 따른 검색·답변 품질과 한국어 출력 유지의 차이를 대응 비교로 분석하고, 그 결과를 적용 목적별로 해석하는 데 있다. [스타일=본문]

[그림 삽입: figures/fig01_research_setting.svg]

[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경. 한국어 질의와 영어 문서 사이의 언어·표현 차이, 검색 근거의 답변 반영, 한국어 출력 유지라는 세 검토 지점을 나타낸다. [스타일=그림제목]

연구 질문은 다음과 같다. 첫째, CAD와 SCD를 적용하지 않은 조건에서 HyDE 적용 여부에 따라 RAG 품질은 어떻게 달라지는가? 둘째, HyDE와 SCD를 적용하지 않고 검색 문맥을 동일하게 유지했을 때 CAD 적용 여부에 따라 답변 품질은 어떻게 달라지는가? 셋째, HyDE와 CAD 조건이 동일할 때 SCD 적용 여부에 따라 한국어 출력 유지 정도는 어떻게 달라지는가? 넷째, SCD에 따른 품질 차이는 평가 언어와 평가 모델을 달리했을 때 어떻게 나타나는가? [스타일=본문]

## 1.2 연구범위 [스타일=절(1.1)]

연구 대상은 RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 네 개 영어 학술·기술 문서와 해당 문서의 내용을 묻는 19개 한국어 질의이다. 각 질의에는 대상 문서가 지정되어 있으며, 검색은 지정 문서의 청크 안에서 수행한다. 이 범위는 같은 질문과 문서에 서로 다른 실험 조건을 적용하여 결과를 대응 비교하는 데 적합하다. [스타일=본문]

연구의 핵심 범위는 첫째, BGE-M3와 BM25를 결합한 hybrid retrieval, weighted RRF, CrossEncoder 재정렬 및 Mi:dm 2.0 Base Instruct 생성 모델로 이루어진 고정 backbone의 구성, 둘째, HyDE·CAD·SCD 적용 여부에 따른 여덟 조건의 실행, 셋째, 저장된 답변·검색 문맥·실행 설정을 이용한 품질 평가와 출력 언어 분석, 넷째, 동일 질의 대응쌍과 동일 문맥 조건을 활용한 통제 비교이다. [스타일=본문]

후속 연구 범위에는 더 다양한 학문 분야와 독립 질의의 확대, 한국어 번역만 적용한 검색과 HyDE 검색의 분리 비교, 사람 평가, 서로 다른 제공자의 평가 모델을 이용한 검증, 다른 생성 모델과 tokenizer에서의 SCD 비교가 포함된다. 이러한 항목은 현재 결과의 외적 타당성과 평가 독립성을 확장하기 위한 과제로 제시한다. [스타일=본문]

# 2. 이론적 배경 [스타일=장(1.)]

## 2.1 Retrieval-Augmented Generation [스타일=절(1.1)]

RAG는 생성 모델의 파라미터에 저장된 정보와 외부 문서 검색을 결합한다[1]. 사용자의 질의를 q, 검색 대상 문서 집합을 D, 검색된 문맥을 Cq, 생성 답변을 y라 하면 기본 과정은 Cq=Retrieve(q,D), y=LM(q,Cq)로 표현할 수 있다. 검색기는 질의와 관련된 근거 후보를 선택하고, 생성기는 질문과 선택된 근거를 이용하여 답변을 구성한다. RAG의 전반적인 연구 흐름은 검색 전 처리, 검색, 검색 후 처리, 생성으로 세분화되고 있으며, 각 단계의 설계가 최종 응답에 영향을 준다[5]. [스타일=본문]

학술문서 질의응답에서는 검색 문맥이 답변의 근거 역할을 한다. 따라서 검색 결과의 관련성과 함께 답변의 주장들이 검색 문맥에 의해 지지되는지를 확인해야 한다. 긴 문맥에서 정보의 위치가 모델 활용에 영향을 줄 수 있다는 연구[6]도 문맥 선택과 배치의 중요성을 보여준다. 본 연구는 검색 결과를 재정렬한 뒤 앞·뒤 위치를 고려하여 재배치하고, 선택·압축된 다섯 개 문맥을 생성 모델에 제공한다. [스타일=본문]

## 2.2 Hybrid Retrieval과 재정렬 [스타일=절(1.1)]

Dense retrieval은 문장을 연속 벡터로 표현하여 의미적 유사성을 계산한다. 본 연구에서 사용하는 BGE-M3는 다국어·다기능·다중 세분성 표현을 지원하는 임베딩 모델로, 한국어 질의와 영어 문서를 같은 표현 공간에서 비교하는 데 활용된다[7]. Sparse retrieval은 질의와 문서의 표면적 단어 일치를 이용한다. BM25는 단어 빈도와 문서 빈도를 이용하여 점수를 계산하므로 모델명, 약어, 전문용어와 수치 표현을 찾을 때 dense retrieval을 보완한다[8]. [스타일=본문]

두 검색 결과는 Reciprocal Rank Fusion(RRF)으로 결합한다[9]. 본 연구에서는 dense와 BM25 순위에 각각 0.6과 0.4의 가중치를 적용한다. 결합된 후보는 BERT 기반 passage re-ranking 연구[10]와 MS MARCO 데이터[11]를 기반으로 한 ms-marco-MiniLM-L-6-v2 CrossEncoder로 다시 정렬한다. 이 구성은 의미 유사성, 표면 일치, 쌍별 관련성 판단을 차례로 결합한다. [스타일=본문]

## 2.3 Hypothetical Document Embeddings [스타일=절(1.1)]

HyDE는 질의를 직접 임베딩하는 대신, 질의에 답할 것으로 예상되는 가상 문서를 생성하고 그 문서의 임베딩으로 실제 문서를 검색한다[2]. 짧은 질의를 문서와 유사한 표현으로 확장할 수 있어 zero-shot dense retrieval에 활용된다. 국내 연구에서도 HyDE 기반 다중 단계 검색의 retrieval 성능이 비교되며 질의 확장 방식의 적용 가능성이 검토되었다[12]. 본 연구에서는 한국어 질의를 영어로 번역한 뒤 영어 학술문장 형태의 가상 문서를 생성하고, 이를 BGE-M3 dense 검색 입력으로 사용한다. BM25 검색과 CrossEncoder 재정렬에는 원래 한국어 질의를 사용한다. 답변 생성에는 가상 문서가 아니라 검색된 실제 학술문서 문맥을 제공한다. [스타일=본문]

## 2.4 Context-Aware Decoding [스타일=절(1.1)]

CAD는 문맥이 포함된 조건과 포함되지 않은 조건의 다음 토큰 점수를 비교하여 문맥에 의해 강화된 생성 경향을 반영한다[3]. 문맥이 있는 logits를 zcontext, 문맥이 없는 logits를 zno-context라 하면 CAD 점수는 zCAD=(1+α)zcontext−αzno-context로 계산한다. 본 실험에서는 α=0.5를 사용하였다. CAD는 검색 결과를 변경하지 않고 생성 단계의 계산을 변경하므로, 동일한 검색 문맥을 사용한 on/off 대응쌍을 통해 생성 방식에 따른 차이를 분석할 수 있다. 이 계산은 contrastive decoding의 토큰 대조 관점과도 관련되며[13], 국내에서도 CAD의 대조 구조를 확장한 생성 제어 연구가 발표되었다[14]. [스타일=본문]

## 2.5 Soft Constrained Decoding [스타일=절(1.1)]

다국어 RAG에서는 검색 문서의 언어가 생성 결과에 영향을 주어 목표 언어에서 벗어나는 language drift가 나타날 수 있다. SCD는 목표 언어, 비목표 언어, 중립 토큰으로 vocabulary를 구분하고 토큰 점수를 조정하여 출력 언어를 제어한다[4]. 본 연구의 reference_scd 설정은 생성 시작 후 5개 토큰이 지난 시점부터 한국어 목표 토큰에 α=1.1, 영어 비목표 토큰에 β=0.9를 곱하고 공백, 문장부호, 숫자, 수식, 괄호와 인용 표시는 중립으로 유지한다. CAD와 SCD가 함께 적용되면 CAD 점수 계산 후 SCD를 적용한다. [스타일=본문]

## 2.6 RAG 평가 [스타일=절(1.1)]

본 연구에서는 RAGAS의 faithfulness, answer relevancy, context precision, context recall을 사용한다[15]. Faithfulness는 답변의 내용이 검색 문맥에 의해 뒷받침되는 정도를, answer relevancy는 답변이 질문에 적절히 대응하는 정도를 평가한다. Context precision과 context recall은 검색 문맥과 reference의 관계를 평가한다. 자동 데이터셋 생성과 RAG 평가 구성을 비교한 국내 연구[16] 및 재현 가능한 RAG 평가 라이브러리 연구[17]를 고려하면 평가 조건을 함께 기록하는 것이 중요하다. 이에 본 연구는 같은 질문을 이용한 조건 간 대응 차이와 신뢰구간을 중심으로 분석한다. [스타일=본문]

SCD의 직접 목표인 출력 언어는 생성 텍스트에서 한글 문자 수를 한글과 ASCII 영문자 수의 합으로 나눈 한국어 문자 비율로 측정한다. 이 값은 LLM judge와 독립적으로 계산된다. 내용 품질에 대한 추가 검증에서는 동일 문맥 대응쌍을 영어와 한국어로 정규화하고, gpt-4o[18]와 gpt-4.1-2025-04-14를 평가 모델로 사용한다. 다국어 LLM-as-a-judge의 신뢰도와 언어 편향 가능성[19]을 고려하여 두 평가 언어와 두 모델의 결과를 함께 제시한다. [스타일=본문]

# 3. 시스템 설계 [스타일=장(1.)]

## 3.1 연구 및 실험 요구사항 [스타일=절(1.1)]

본 연구의 설계 대상은 동일한 질의와 문서에 HyDE·CAD·SCD 조건을 체계적으로 적용하고, 비교에 필요한 근거와 실행 정보를 보존하는 실험 프로그램이다. 서비스 사용자 행동 대신 연구 변인의 통제, 실험 반복성, 결과 추적성을 요구사항으로 정의하였다. [스타일=본문]

[표 3-1] 연구 및 실험 요구사항 [스타일=표제목]

| 번호 | 요구사항 | 확인 방법 |
|---|---|---|
| R1 | 한국어 질의와 대상 영어 문서를 연결한다. | query ID와 paper ID를 확인한다. |
| R2 | HyDE·CAD·SCD의 여덟 조합을 동일 질의 집합에 적용한다. | 조건별 19개, 총 152개 생성 기록을 확인한다. |
| R3 | 생성 모델과 검색 backbone을 모든 조건에서 고정한다. | 모델명, 검색 수, 재정렬 수, 문맥 수를 검증한다. |
| R4 | 답변과 함께 검색 문맥, 청크 ID, 설정, 상태를 저장한다. | JSONL record의 필수 필드를 확인한다. |
| R5 | HyDE와 CAD의 효과를 다른 요인의 영향을 배제한 대응쌍으로 비교한다. | 19개 질의 ID 및 CAD 동일 문맥 여부를 확인한다. |
| R6 | SCD의 출력 언어 효과와 내용 품질을 별도 지표로 평가한다. | 한국어 문자 비율과 RAGAS 결과를 분리한다. |
| R7 | 누락된 평가값을 임의의 정상 점수로 대체하지 않는다. | null 및 실패 상태를 별도로 기록한다. |
| R8 | 보존된 실험 자료에서 본문 수치를 다시 계산할 수 있어야 한다. | 검증 스크립트로 표와 핵심 수치를 재현한다. |

각 조건의 식별자는 HyDE, CAD, SCD의 on/off 상태를 이름에 포함한다. [표 3-2]의 여덟 조건은 RAG-Cube의 꼭짓점에 대응한다. [스타일=본문]

[표 3-2] RAG-Cube의 여덟 가지 실험 조건 [스타일=표제목]

| 설정 | HyDE | CAD | SCD |
|---|---:|---:|---:|
| hyde_off__no_decoder_control | OFF | OFF | OFF |
| hyde_off__cad_only | OFF | ON | OFF |
| hyde_off__scd_only | OFF | OFF | ON |
| hyde_off__cad_scd | OFF | ON | ON |
| hyde_on__no_decoder_control | ON | OFF | OFF |
| hyde_on__cad_only | ON | ON | OFF |
| hyde_on__scd_only | ON | OFF | ON |
| hyde_on__cad_scd | ON | ON | ON |

[그림 삽입: figures/fig02_rag_cube.svg]

[그림 3-1] HyDE·CAD·SCD의 2×2×2 RAG-Cube 실험 구성. H, C, S는 각 기법을 나타내며 0과 1은 각각 미적용과 적용을 의미한다. [스타일=그림제목]

## 3.2 아키텍처 설계 [스타일=절(1.1)]

실험 아키텍처는 입력, 검색, 문맥 구성, 생성, 저장, 평가·분석 단계로 구성된다. 입력 단계는 19개 질의와 각 질의의 대상 문서를 읽는다. 검색 단계는 HyDE 조건에 따라 dense 검색 표현을 선택하고, BGE-M3와 BM25 결과를 weighted RRF로 결합한 뒤 CrossEncoder로 재정렬한다. 문맥 구성 단계는 재정렬 결과의 위치를 조정하고 다섯 개 문단을 선택한 뒤 추출형 압축과 길이 제한을 적용한다. 생성 단계는 Mi:dm 2.0 Base Instruct를 사용하며 조건에 따라 CAD와 SCD를 토큰 생성 과정에 연결한다. 저장 단계는 답변과 검색 문맥, 청크 ID, 설정과 실행 상태를 JSONL에 기록한다. 평가·분석 단계는 저장된 자료를 읽어 품질 점수와 한국어 문자 비율을 계산한다. [스타일=본문]

[그림 삽입: figures/fig03_experimental_pipeline.svg]

[그림 3-2] 고정 Paper-RAG backbone과 실험 요인의 적용 위치. HyDE는 검색 단계, CAD와 SCD는 생성 단계에 적용되며 평가 단계는 저장된 답변과 문맥을 사용한다. [스타일=그림제목]

## 3.3 상세설계 [스타일=절(1.1)]

HyDE가 OFF이면 원질의를 BGE-M3 dense 검색에 사용한다. HyDE가 ON이면 한국어 질의를 영어로 번역하고 영어 가상 문서를 생성하여 dense 검색에 사용한다. BM25에는 원질의를 입력한다. 두 검색기의 후보 수는 각각 최대 8개이며, dense 순위에는 0.6, BM25 순위에는 0.4의 가중치를 적용한 RRF 점수로 결합한다. CrossEncoder는 결합 후보를 질의와의 관련성에 따라 다시 정렬한다. [스타일=본문]

생성 문맥은 재정렬 결과에서 다섯 개를 선택하여 구성한다. 긴 문맥의 중간 위치에서 정보 활용이 약해질 수 있다는 연구를 반영하여 높은 순위 문맥을 앞과 뒤에 분산 배치한다[6]. 각 문맥에는 질의 관련 문장을 보존하는 추출형 압축과 전체 길이 제한을 적용한다. 최종 답변 생성은 deterministic greedy 방식으로 수행하고 최대 512개 새 토큰을 허용한다. HyDE 가상 문서 생성은 temperature 0.1, top-p 0.9의 sampling을 사용한다. [스타일=본문]

CAD는 매 토큰 단계에서 현재 생성 이력을 공유하는 문맥 분기와 무문맥 분기를 계산한다. 고정 α=0.5를 사용하여 두 logits를 결합한다. SCD는 tokenizer vocabulary를 한국어·영어·중립 집합으로 구분하고 5번째 토큰 이후 reference_scd 규칙을 적용한다. 실험 실행기는 CAD 처리기 다음에 SCD 처리기를 연결하여 결합 조건의 순서를 고정한다. [스타일=본문]

비교 설계에서 HyDE는 CAD와 SCD가 모두 OFF인 19개 대응쌍을 사용한다. CAD는 HyDE와 SCD가 OFF이고 검색 문맥이 byte 단위로 같은 19개 대응쌍을 사용한다. SCD는 동일 query·HyDE·CAD 조건의 76개 on/off 대응쌍을 사용한다. 이 구조는 각 결과가 어떤 조건에서 계산되었는지를 명확하게 추적하도록 한다. [스타일=본문]

# 4. 프로그램 구현 [스타일=장(1.)]

## 4.1 시스템 환경 [스타일=절(1.1)]

실험 프로그램은 Python으로 구현하였으며 PyTorch와 Transformers를 이용해 임베딩, 재정렬, 생성 모델 및 logits processor를 실행하였다. Transformers 버전은 4.45.2, sentence-transformers는 2.7.0이며, 생성 모델은 K-intelligence/Midm-2.0-Base-Instruct이다[20]. 품질 평가는 RAGAS 0.2 계열을 사용하였다[15]. 연구용 데이터와 실행 결과는 SQLite와 UTF-8 JSONL·JSON 파일로 관리하였다. [스타일=본문]

[표 4-1] 실험 실행 환경 [스타일=표제목]

| 항목 | 확인된 내용 |
|---|---|
| 본 생성 실행 위치 | Alice Cloud G-NAHP-80; 최종 152개 record의 alice_mode=true |
| GPU | NVIDIA A100 80GB PCIe 1개, VRAM 80GB |
| CPU | 16 vCore |
| RAM | 192 GiB |
| 실행 관측 최대 GPU 메모리 | 34,800 MiB, 최대 utilization 96%, CUDA OOM 없음 |
| 로컬 개발 장치 참고 | NVIDIA GeForce RTX 3080 Ti 12GB; 계획·smoke 용도 |
| 구현 언어 | Python |
| 주요 실행 라이브러리 | PyTorch, Transformers 4.45.2, sentence-transformers 2.7.0 |
| 평가 | RAGAS 0.2 계열, 외부 judge API, 로컬 BGE-M3 embedding |
| 연구 데이터 저장 | SQLite, JSONL, JSON, CSV |

최종 reference_scd 생성 artifact에는 Alice Cloud 실행 여부와 각 표본의 시작 시각·소요 시간이 기록되어 있다. 실험에 선택한 G-NAHP-80 인스턴스는 Alice Cloud 공식 사양표에서 NVIDIA A100 80GB PCIe 1개, 16 vCore, RAM 192 GiB로 제공된다[21]. 실행 검증 보고서에는 A100 80GB PCIe 81,920 MiB와 최대 GPU 메모리 34,800 MiB, 최대 utilization 96%, CUDA OOM 없음이 기록되어 있다. [스타일=본문]

본 연구는 사전학습된 Mi:dm 2.0 Base Instruct의 파라미터를 미세조정하지 않았다. 따라서 별도의 모델 학습 시간과 epoch는 없다. 다섯 개 tuning 질의와 세 개 검색 폭 profile로 15개 결과를 비교하여 retrieval pool 8, rerank 8, context 5를 선택했으며, 이 과정의 실행 시간은 최종 보존 기록에 남아 있지 않아 정량값을 제시하지 않는다. [스타일=본문]

[표 4-2] 고정 Paper-RAG backbone 설정 [스타일=표제목]

| 구성 | 설정 |
|---|---|
| Dense retrieval | BGE-M3 |
| Sparse retrieval | BM25 |
| Fusion | Dense 0.6 / BM25 0.4 weighted RRF |
| Retrieval pool | 8 |
| Reranker | ms-marco-MiniLM-L-6-v2 |
| Rerank top-N | 8 |
| Generation context | 5 passages |
| Generator | K-intelligence/Midm-2.0-Base-Instruct |
| Answer decoding | deterministic greedy |
| Max new tokens | 512 |
| HyDE generation | sampling, temperature 0.1, top-p 0.9 |
| CAD | fixed α=0.5 |
| SCD | reference_scd, α=1.1, β=0.9, Tstart=5 |

[표 4-3] 최종 생성 실행 시간 [스타일=표제목]

| 항목 | 기록값 |
|---|---:|
| 생성 답변 수 | 152 |
| 실행 구간 | 2026-07-08 07:23:49–09:17:04 KST |
| 기록된 wall-clock 구간 | 1시간 53분 14.7초 |
| 표본별 duration 합계 | 6,888.611초 |
| 표본당 평균 | 45.320초 |
| 표본당 중앙값 | 30.556초 |
| 최소 / 최대 | 3.975초 / 164.153초 |

표본별 duration의 합계는 각 record에 기록된 처리 시간을 더한 값이고, wall-clock 구간은 가장 이른 시작 시각부터 가장 늦은 종료 시각까지 계산한 값이다. CAD는 문맥·무문맥 분기를 함께 계산하므로 CAD 적용 조건의 평균 시간이 상대적으로 길었다. 조건별 19개 표본의 평균은 HyDE OFF/CAD OFF/SCD OFF 24.6초, HyDE OFF/CAD ON/SCD OFF 63.9초, HyDE OFF/CAD OFF/SCD ON 18.8초, HyDE OFF/CAD ON/SCD ON 56.8초, HyDE ON/CAD OFF/SCD OFF 24.5초, HyDE ON/CAD ON/SCD OFF 79.0초, HyDE ON/CAD OFF/SCD ON 25.0초, HyDE ON/CAD ON/SCD ON 69.9초였다. [스타일=본문]

## 4.2 시스템 구성 [스타일=절(1.1)]

입력 자료는 질의 분할 파일, 대상 논문 청크, 고정 매개변수와 8개 실험 조건으로 구성된다. 검색 모듈은 QueryExpander, BGE-M3 dense 검색기, BM25 검색기, weighted RRF, CrossEncoder 및 ContextCompressor를 연결한다. 생성 모듈은 Mi:dm 모델과 CAD·SCD logits processor를 연결한다. 실행기는 질문과 조건을 순회하면서 검색과 생성을 호출하고, 답변·문맥·retrieved ID·reranked ID·실험 설정·상태·시간을 한 record로 저장한다. [스타일=본문]

평가 모듈은 생성과 분리되어 저장된 record를 입력으로 받는다. RAGAS 평가기는 네 개 품질 지표를 계산하며, 언어 분석기는 답변의 한국어 문자 비율과 SCD on/off 차이를 계산한다. 대칭 평가 입력 생성기는 동일 문맥 38쌍을 영어와 한국어 panel로 정규화하고, 두 평가 모델의 결과를 별도 파일에 기록한다. 분석기와 검증기는 대응 평균 차이, 신뢰구간, win/loss/tie, drift 전환 수를 다시 계산한다. [스타일=본문]

## 4.3 시스템 구현 [스타일=절(1.1)]

주실험 실행기는 설정 파일에서 8개 configuration을 읽고, 19개 질의마다 지정된 문서 collection을 선택한다. 검색 결과가 없는 상태를 정상 결과로 변환하지 않으며, 오류와 성공 상태를 record에 분리하여 기록한다. 최종 artifact는 152개 record 모두 status=succeeded이고 생성 답변과 문맥이 존재한다. 생성 모델 필드도 152개 모두 K-intelligence/Midm-2.0-Base-Instruct로 확인된다. [스타일=본문]

HyDE가 적용된 record에는 번역 질의, 가상 문서, 생성 설정과 hyde_used가 저장된다. 검색 추적 정보에는 dense·sparse·fusion 결과 수, retrieved chunk ID와 reranked chunk ID가 포함된다. CAD와 SCD가 적용된 record에는 α, β, 시작 토큰, vocabulary partition, processor 순서가 기록된다. 이러한 필드는 비교 조건이 실제 실행에 반영되었는지를 결과 파일에서 확인할 수 있게 한다. [스타일=본문]

실험 수치의 재현은 저장된 artifact를 읽는 검증 프로그램으로 수행한다. 검증 프로그램은 152개 생성 결과, 19개 질의, 8개 조건, 동일 문맥 대응쌍, SCD 76쌍, 품질 점수와 신뢰구간을 확인한다. 그림 생성 프로그램도 같은 보존 자료를 읽어 7개 SVG와 300 dpi PNG를 생성한다. 이 과정은 새로운 답변 생성이나 평가 모델 호출 없이 수행된다. [스타일=본문]

# 5. 실험 [스타일=장(1.)]

## 5.1 실험 대상과 구성 [스타일=절(1.1)]

최종 질의 집합은 네 개 문서에 대한 19개의 한국어 질문으로 구성된다. RAG Survey는 RAG의 구조와 검색·생성 개념, CAD 논문은 문맥 기반 디코딩, RAPTOR 논문은 계층적 검색, Mi:dm K 2.5 Pro Technical Report는 모델의 기술적 특성을 묻는 질문을 포함한다[3,5,17,22]. 각 질문은 하나의 대상 문서와 연결된다. [스타일=본문]

[표 5-1] 실험 대상 문서와 질의 수 [스타일=표제목]

| 문서 | 질의 수 |
|---|---:|
| RAG Survey | 5 |
| CAD | 4 |
| RAPTOR | 4 |
| Mi:dm K 2.5 Pro Technical Report | 6 |
| 합계 | 19 |

각 질의에 8개 조건을 적용하여 152개의 답변을 생성하였다. HyDE의 기본 비교는 CAD와 SCD가 OFF인 HyDE on/off 19쌍이다. CAD의 기본 비교는 HyDE와 SCD가 OFF이며 검색 문맥이 동일한 CAD on/off 19쌍이다. SCD의 언어 분석은 query·HyDE·CAD가 같은 SCD on/off 76쌍이다. SCD 대칭 품질 평가는 HyDE가 OFF이며 문맥이 같은 38쌍을 사용한다. [스타일=본문]

[그림 삽입: figures/fig04_evaluation_design.svg]

[그림 5-1] 실험 요인별 비교 및 평가 설계. HyDE와 CAD는 각각 19개 통제 대응쌍, SCD 언어 분석은 76쌍, 대칭 품질 평가는 38쌍을 사용한다. [스타일=그림제목]

## 5.2 평가 방법 [스타일=절(1.1)]

HyDE와 CAD 비교에는 faithfulness, answer relevancy, context precision, context recall의 네 RAGAS 지표를 사용한다. 동일한 19개 query ID의 on/off 점수 차이를 계산하고, 19개 질의를 재표집 단위로 하는 paired percentile bootstrap을 200,000회 수행하여 평균 차이의 95% 신뢰구간을 계산한다. 차이가 +0.02보다 크면 win, −0.02보다 작으면 loss, 그 사이이면 tie로 집계한다. [스타일=본문]

SCD의 출력 언어 평가는 한국어 문자 비율=한글 문자 수/(한글 문자 수+ASCII 영문자 수)로 계산한다. 비율이 0.5 미만인 답변을 언어 이탈로 분류한다. 전체 76쌍의 평균 차이와 ±0.02 기준의 증가·감소·동률, 기준선 전환을 분석한다. 한글과 영문자가 전혀 없는 숫자 반복 답변 1건은 기존 최종 분석 함수의 규칙과 동일하게 비율 0으로 집계하였다. [스타일=본문]

대칭 품질 평가는 같은 검색 문맥을 사용하는 38개 SCD on/off 쌍의 답변을 영어와 한국어로 각각 정규화한다. gpt-4o와 gpt-4.1-2025-04-14를 평가 모델로 사용하고, faithfulness와 answer relevancy의 on−off 차이를 계산한다. 신뢰구간은 19개 query를 cluster 단위로 10,000회 bootstrap하여 산출한다. [스타일=본문]

## 5.3 HyDE와 CAD 결과 [스타일=절(1.1)]

[표 5-2] HyDE 적용에 따른 품질 지표 차이(CAD OFF, SCD OFF, n=19) [스타일=표제목]

| 지표 | 평균 차이(ON−OFF) | 95% 신뢰구간 | Win/Loss/Tie |
|---|---:|---:|---:|
| Faithfulness | +0.0734 | [−0.0248, +0.1777] | 9/6/4 |
| Answer relevancy | +0.0303 | [+0.0016, +0.0615] | 9/3/7 |
| Context precision | −0.0679 | [−0.1702, +0.0194] | 7/6/6 |
| Context recall | −0.0526 | [−0.1579, 0.0000] | 0/1/18 |

HyDE 적용 시 answer relevancy의 평균 차이는 +0.0303이었고 95% 신뢰구간은 0을 포함하지 않았다. Faithfulness는 양의 평균 차이를 보였으나 신뢰구간이 0을 포함하였다. Context precision의 신뢰구간도 0을 포함하였으며 context recall의 상한은 0에 닿았다. 따라서 본 실험에서는 HyDE 적용과 answer relevancy의 제한적인 증가가 함께 나타났으며, 네 지표 전체에서 같은 방향의 변화가 관찰되지는 않았다. [스타일=본문]

[표 5-3] CAD 적용에 따른 품질 지표 차이(HyDE OFF, SCD OFF, 동일 문맥, n=19) [스타일=표제목]

| 지표 | 평균 차이(ON−OFF) | 95% 신뢰구간 | Win/Loss/Tie |
|---|---:|---:|---:|
| Faithfulness | +0.0023 | [−0.0903, +0.0952] | 7/9/3 |
| Answer relevancy | −0.0715 | [−0.1792, +0.0004] | 5/12/2 |
| Context precision | −0.0022 | [−0.0447, +0.0322] | 2/1/16 |
| Context recall | −0.0526 | [−0.1579, 0.0000] | 0/1/18 |

CAD의 faithfulness 평균 차이는 +0.0023이었으며 신뢰구간은 0을 포함하였다. Answer relevancy는 음의 평균 차이를 보였지만 신뢰구간 상한이 +0.0004였다. 네 지표의 신뢰구간은 모두 0을 포함하거나 경계에 닿았다. 동일한 검색 문맥을 사용한 본 비교에서 CAD 적용에 따른 명확한 품질 증가는 관찰되지 않았다. [스타일=본문]

[그림 삽입: figures/fig05_hyde_cad_contrasts.svg]

[그림 5-2] HyDE와 CAD 적용에 따른 품질 지표의 대응 평균 차이. 점은 평균 차이, 가로선은 95% 신뢰구간이며 세로 점선은 차이 0을 나타낸다. [스타일=그림제목]

## 5.4 SCD의 한국어 출력 유지 결과 [스타일=절(1.1)]

[표 5-4] 설정별 한국어 문자 비율과 언어 이탈 수 [스타일=표제목]

| 설정 | 평균 한국어 문자 비율 | 언어 이탈 수(<0.5) |
|---|---:|---:|
| HyDE OFF / CAD OFF / SCD OFF | 0.5088 | 8/19 |
| HyDE OFF / CAD ON / SCD OFF | 0.5175 | 8/19 |
| HyDE OFF / CAD OFF / SCD ON | 0.7069 | 4/19 |
| HyDE OFF / CAD ON / SCD ON | 0.7590 | 3/19 |
| HyDE ON / CAD OFF / SCD OFF | 0.6023 | 3/19 |
| HyDE ON / CAD ON / SCD OFF | 0.5099 | 7/19 |
| HyDE ON / CAD OFF / SCD ON | 0.8035 | 2/19 |
| HyDE ON / CAD ON / SCD ON | 0.7501 | 3/19 |

SCD on−off 76개 대응쌍에서 한국어 문자 비율의 평균 차이는 +0.2203이었다. 68쌍은 +0.02를 초과하여 증가했고, 3쌍은 −0.02보다 크게 감소했으며, 5쌍은 ±0.02 범위였다. 한국어 문자 비율이 0.5 미만인 언어 이탈 출력은 SCD OFF의 26개에서 SCD ON의 12개로 감소하였다. 기존 26개 언어 이탈 중 15개는 SCD 적용 후 0.5 이상으로 이동했고, 반대 방향 이동은 1개였다. [스타일=본문]

HyDE와 CAD의 네 조합별 평균 차이는 각각 +0.1981, +0.2415, +0.2012, +0.2402로 모두 양의 방향이었다. 검색 문맥이 완전히 같은 HyDE-OFF 38개 대응쌍에서도 평균 차이는 +0.2198이었다. 이 결과에서 SCD 적용은 한국어 출력 비율의 증가와 언어 이탈 감소에 연결되었다. [스타일=본문]

[그림 삽입: figures/fig06_scd_language_adherence.svg]

[그림 5-3] SCD 적용 전후의 한국어 문자 비율과 언어 이탈 수. 회색 선은 76개 개별 대응쌍, 주황 선은 평균이며, 기준선 0.5 미만의 출력은 26개에서 12개로 감소하였다. [스타일=그림제목]

## 5.5 SCD 대칭 품질 평가 [스타일=절(1.1)]

[표 5-5] SCD의 평가 언어·모델별 품질 차이 [스타일=표제목]

| 평가 모델 | 평가 언어 | Faithfulness Δ [95% CI] | Answer relevancy Δ [95% CI] |
|---|---|---:|---:|
| gpt-4o | 영어 | +0.0071 [−0.0596, +0.0714] | −0.0910 [−0.1725, −0.0240] |
| gpt-4o | 한국어 | −0.0283 [−0.1044, +0.0510] | −0.0752 [−0.1501, −0.0138] |
| gpt-4.1-2025-04-14 | 영어 | −0.0579 [−0.1322, +0.0060] | −0.0327 [−0.0851, +0.0129] |
| gpt-4.1-2025-04-14 | 한국어 | −0.0326 [−0.0997, +0.0226] | −0.0356 [−0.1149, +0.0315] |

Faithfulness는 네 평가 조건 모두 95% 신뢰구간이 0을 포함하였다. Answer relevancy의 평균 차이는 네 조건 모두 음의 방향이었으며, gpt-4o의 영어·한국어 평가에서는 신뢰구간 전체가 0보다 작았다. gpt-4.1-2025-04-14의 두 평가에서는 신뢰구간이 0을 포함하였다. 따라서 SCD의 내용 품질 차이는 평가 모델을 바꾸었을 때 동일하게 재현되지 않았다. [스타일=본문]

[그림 삽입: figures/fig07_symmetric_quality.svg]

[그림 5-4] 평가 언어와 평가 모델에 따른 SCD 품질 차이. 점과 가로선은 SCD 적용에 따른 평균 차이와 query-clustered bootstrap 95% 신뢰구간을 나타낸다. [스타일=그림제목]

## 5.6 결과 종합 및 한계 [스타일=절(1.1)]

세 실험 요인은 서로 다른 결과를 보였다. HyDE는 CAD와 SCD가 없는 통제 비교에서 answer relevancy의 소폭 증가와 연결되었지만 다른 지표의 신뢰구간은 0을 포함하거나 경계에 닿았다. CAD는 같은 검색 문맥을 사용한 비교에서도 명확한 품질 증가가 나타나지 않았다. SCD는 한국어 문자 비율과 언어 이탈 수에서 가장 분명한 차이를 보였으나, faithfulness와 answer relevancy의 변화는 두 평가 모델에서 일관되지 않았다. 따라서 실험 결과는 검색 확장, 문맥 기반 생성, 출력 언어 제어의 목적 지표를 구분하여 해석해야 한다. [스타일=본문]

본 실험은 네 개 문서와 19개 질의에 한정되며, HyDE와 CAD의 주요 비교는 각각 19쌍이다. 문서도 자연어처리와 언어모델 관련 분야에 집중되어 있다. 더 다양한 학문 분야, 문서 구조와 독립 질문을 이용한 반복 실험이 필요하다. HyDE ON 조건에서는 가상 문서가 조건별로 새로 생성되어 CAD on/off의 검색 문맥이 충분히 같지 않았으므로 CAD의 품질 해석은 HyDE OFF 동일 문맥 비교에 집중하였다. [스타일=본문]

RAGAS의 일부 지표는 LLM judge에 의존하며, 실제 대칭 평가에서도 answer relevancy의 신뢰구간이 평가 모델에 따라 달라졌다. 한국어 정규화 panel을 만들 때 실제 답변 번역이 필요했던 비율도 SCD OFF 23/38, SCD ON 11/38로 달랐다. 번역 모델과 첫 평가 모델이 gpt-4o이고 두 judge가 같은 제공자의 모델이라는 조건도 남아 있다. 사람에 의한 blind 평가와 독립 평가 모델을 추가하면 품질 결과의 해석을 강화할 수 있다. [스타일=본문]

한국어 문자 비율은 한글과 ASCII 영문자의 상대적 비율이므로 문법적 자연스러움, 근거 정확성, 다른 언어 문자 전체를 직접 평가하지 않는다. 숫자만 반복되어 한글·영문자 분모가 0인 답변 1건도 존재한다. 또한 숫자 환각과 질문 유형별 차이는 전용 annotation과 충분한 표본이 없어 현재 평가 항목에 포함하지 않았다. [스타일=본문]

최종 실행 기록에서 RAG Survey 대상 5개 질의의 8개 조건, 총 40개 record는 BM25 후보가 0개였고 나머지 112개 record는 BM25 후보 8개를 반환하였다. 해당 40개는 dense 후보로 검색 문맥이 구성되었다. 따라서 hybrid retrieval의 두 경로가 모든 질의에서 동일하게 기여했다고 해석하기보다, 질의·문서별 실제 후보 기록을 함께 살펴야 한다. [스타일=본문]

# 6. 결론 [스타일=장(1.)]

본 연구에서는 한국어 질의를 이용하여 영어 학술·기술 문서를 검색하고 한국어 답변을 생성하는 RAG 환경에서 HyDE, CAD, SCD의 적용 결과를 분석하였다. 세 기법의 적용 여부를 독립적인 이진 요인으로 두어 RAG-Cube의 여덟 조건을 구성하고, 네 개 문서에 관한 19개 질문으로 152개의 답변을 생성하였다. HyDE는 CAD와 SCD를 사용하지 않은 조건에서 answer relevancy를 평균 +0.0303 높였으나 다른 품질 지표의 차이는 명확하지 않았다. CAD는 동일 문맥 비교에서 faithfulness 차이가 +0.0023으로 나타났고 명확한 품질 증가는 확인되지 않았다. SCD는 76개 대응쌍의 한국어 문자 비율을 평균 +0.2203 높였으며 언어 이탈 출력을 26개에서 12개로 줄였다. 한편 SCD의 내용 품질 차이는 두 평가 모델에서 일관되게 재현되지 않았다. 이 결과는 각 기법의 적용 효과를 검색 확장, 문맥 기반 생성, 출력 언어 유지라는 목적별 지표로 나누어 확인해야 함을 보여준다. [스타일=본문]

향후 연구에서는 학문 분야와 질의 수를 확대하고, 한국어 질의의 영어 번역만 적용한 검색 조건을 추가하여 번역과 가상 문서 생성의 영향을 분리할 필요가 있다. HyDE 가상 문서를 조건 간에 고정하면 CAD 결합 효과를 더 엄밀하게 비교할 수 있다. 또한 독립 제공자의 평가 모델과 한국어·영어 능력을 갖춘 사람 평가자를 이용한 blind 평가, 숫자와 인용 근거에 대한 별도 annotation, 다른 생성 모델과 tokenizer에서의 반복 실험을 수행하면 현재 결과의 일반성과 품질 해석을 확장할 수 있다. [스타일=본문]

# 참고문헌 [스타일=참고문헌제목]

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” Advances in Neural Information Processing Systems, Vol. 33, 2020.

[2] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” Proceedings of ACL, pp. 1762–1777, 2023.

[3] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-aware Decoding,” Proceedings of NAACL, pp. 783–791, 2024.

[4] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” Proceedings of AAAI, Vol. 40, No. 37, pp. 31519–31526, 2026.

[5] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997, 2023.

[6] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” Transactions of the Association for Computational Linguistics, Vol. 12, pp. 157–173, 2024.

[7] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” Findings of the Association for Computational Linguistics: ACL 2024, pp. 2318–2335, 2024.

[8] S. E. Robertson et al., “Okapi at TREC-3,” Text REtrieval Conference, 1994.

[9] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” Proceedings of SIGIR, pp. 758–759, 2009.

[10] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019.

[11] P. Bajaj et al., “MS MARCO: A Human Generated Machine Reading Comprehension Dataset,” arXiv:1611.09268, 2016.

[12] Y. Kim et al., “Improving Retrieval Performance Using HyDE-Based Multi-Hop Retrieval,” Information Systems Review, Vol. 27, No. 2, pp. 127–148, 2025.

[13] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” Proceedings of ACL, pp. 12286–12312, 2023.

[14] G. Jang et al., “Contrastive CAD: Contrastive Context-Aware Decoding for Mitigating Hallucinations in Large Language Models,” Proceedings of HCLT-KACL, 2024.

[15] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” Proceedings of EACL System Demonstrations, pp. 150–158, 2024.

[16] B. Kim and J. Yang, “A Comparative Analysis of Automatic Dataset Generation Frameworks for RAG System Performance Evaluation,” Journal of the Korea Institute of Information and Electronic Communication Technology, Vol. 18, No. 2, pp. 143–154, 2025.

[17] D. Rau et al., “BERGEN: A Benchmarking Library for Retrieval-Augmented Generation,” Findings of EMNLP, pp. 7640–7663, 2024.

[18] OpenAI, “GPT-4o System Card,” 2024.

[19] X. Fu and W. Liu, “How Reliable is Multilingual LLM-as-a-Judge?,” Findings of EMNLP, 2025.

[20] D. Shin et al., “Mi:dm 2.0 Korea-centric Bilingual Language Models,” arXiv:2601.09066, 2026.

[21] Elice Cloud, “Getting Started with Run Box: Choose an Instance Type,” https://elice.io/help/en/docs/elicecloud/ondemand/create-instances, accessed September 15, 2026.

[22] KT Tech Innovation Group, “Mi:dm K 2.5 Pro Technical Report,” 2026.

---

## 한글 이전 시 확인할 사항

1. 원본 HWP 템플릿의 문단 모양·글꼴·스타일 정의는 수정하지 않는다.
2. 장 제목에는 `장(1.)`, 절 제목에는 `절(1.1)`, 본문에는 `본문` 스타일을 적용한다.
3. 표 제목은 표 위에 `표제목`, 그림 제목은 그림 아래에 `그림제목` 스타일로 배치한다.
4. 그림은 가능하면 SVG를 삽입하고, HWP에서 SVG 호환 문제가 있으면 같은 이름의 300 dpi PNG를 사용한다.
5. 목차·그림 목차·표 목차의 페이지 번호는 본문 조판을 마친 뒤 갱신한다.
6. 표를 HWP 표로 다시 구성한 뒤 각 셀에 `표내용` 스타일을 적용한다.
7. 저자, 지도교수, 제출일, 인준자와 실제 페이지 번호를 입력한다.
8. 템플릿의 안내 문구와 작성 후 삭제 표시가 있는 상자는 최종 제출 전에 제거한다.
