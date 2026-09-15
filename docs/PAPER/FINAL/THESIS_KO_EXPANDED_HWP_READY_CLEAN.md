# 졸업자격실험보고서 확장 원고

## 한국어 질의 기반 영어 학술문서 RAG에서의 HyDE·CAD·SCD 조합 실험

**Combination Experiments of HyDE, CAD, and SCD in RAG over English Academic Documents with Korean Queries**

지도교수 김진석
컴퓨터공학과
동국대학교 WISE캠퍼스
문종건
2026

---

# 초록

대규모 언어모델(Large Language Model, LLM)을 활용한 학술정보 질의응답에서는 사용자가 지정한 문서의 내용을 근거로 답변을 구성하는 과정이 중요하다. Retrieval-Augmented Generation(RAG)은 질의와 관련된 외부 문서를 검색하여 생성 모델의 입력 문맥으로 제공함으로써 특정 문서의 내용과 최신 정보를 답변에 활용한다. 그러나 한국어 질의로 영어 학술문서를 검색하고 다시 한국어로 답변하는 환경에서는 검색과 생성이 연속적으로 연결되면서 서로 다른 문제가 함께 나타난다. 한국어 질의와 영어 학술문장 사이에는 언어와 표현의 차이가 존재하고, 검색된 근거가 생성 단계에서 충분히 활용되는지 확인할 필요가 있으며, 영어 문맥의 영향으로 최종 답변이 목표 언어인 한국어에서 벗어나는 언어 이탈도 발생할 수 있다. 본 연구는 이러한 과정을 검색 표현, 근거 기반 생성, 출력 언어 제어의 세 축으로 나누어 분석한다.

본 연구에서는 HyDE(Hypothetical Document Embeddings), CAD(Context-Aware Decoding), SCD(Soft Constrained Decoding)를 각각 검색 확장, 문맥 기반 생성 제어, 출력 언어 제어의 실험 요인으로 설정한다. 세 요인의 적용 여부를 독립적인 이진 조건으로 두어 구성한 2×2×2 조합 실험을 RAG-Cube로 지칭한다. 실험은 BGE-M3 dense retrieval, BM25 sparse retrieval, dense 0.6·BM25 0.4 weighted RRF, ms-marco-MiniLM-L-6-v2 CrossEncoder, 다섯 개 생성 문맥, K-intelligence/Midm-2.0-Base-Instruct 생성 모델로 구성된 고정 Paper-RAG backbone에서 수행한다. 연구 대상은 RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report에 각각 대응하는 총 19개의 한국어 질의-대상문서 쌍이며, 각 쌍에 여덟 가지 RAG-Cube 조건을 적용하여 152개의 생성 답변을 확보한다.

평가는 RAGAS의 faithfulness, answer relevancy, context precision, context recall과 생성 답변에서 직접 계산한 한국어 문자 비율을 함께 사용한다. HyDE는 CAD와 SCD를 끈 19개 대응쌍, CAD는 HyDE와 SCD를 끄고 검색 문맥을 동일하게 유지한 19개 대응쌍으로 비교한다. SCD의 직접 언어 효과는 동일 query·HyDE·CAD 조건으로 대응되는 76개 on/off 쌍으로 분석하며, 내용 품질은 HyDE OFF에서 검색 문맥이 동일한 38개 대응쌍을 영어와 한국어로 각각 정규화하여 gpt-4o와 gpt-4.1-2025-04-14 두 평가 모델로 교차 검토한다.

RAG-Cube의 여덟 조건을 전체적으로 보면 지표별 최고 configuration이 서로 다르게 나타난다. HyDE ON·CAD ON·SCD OFF 조건은 faithfulness 0.9230으로 가장 높고, HyDE ON·CAD OFF·SCD OFF 조건은 answer relevancy 0.8504로 가장 높다. Context precision은 HyDE OFF·CAD OFF·SCD ON 조건에서 0.8512, context recall은 모든 요인을 끈 기준 조건에서 1.0000으로 가장 높다. 통제된 HyDE 비교에서 answer relevancy는 평균 +0.0303 증가하고 95% 신뢰구간은 [+0.0016, +0.0615]이다. Faithfulness는 평균 +0.0734의 양의 차이를 보이며 19개 질의 중 9개에서 증가, 6개에서 감소, 4개에서 동률 범위를 나타낸다. 전체 76개 HyDE 대응쌍에서도 faithfulness와 answer relevancy의 평균 차이는 각각 +0.0732와 +0.0277로 양의 방향이다.

CAD의 동일 문맥 통제 비교에서는 faithfulness 평균 차이가 +0.0023이며 95% 신뢰구간은 [−0.0903, +0.0952]이다. 이 조건만으로 CAD의 독립적인 평균 품질 향상을 확정하기는 어렵다. 반면 RAG-Cube의 조합별 결과에서는 HyDE가 적용된 두 조건에서 CAD를 추가했을 때 faithfulness가 각각 +0.0338, +0.0503, context precision이 +0.0324, +0.0287 높아지는 패턴이 나타난다. 같은 비교에서 answer relevancy는 각각 −0.0997, −0.0131의 차이를 보여, CAD가 포함된 조합은 근거 충실도와 질문 관련성 사이의 조건 의존적 trade-off를 보인다. CAD ON 조건의 평균 생성 시간은 동일 HyDE·SCD 조건의 CAD OFF 대비 약 2.60~3.22배로 측정되어 품질과 계산비용을 함께 고려할 필요가 있다.

SCD는 직접 목표인 한국어 출력 유지에서 가장 일관된 결과를 보인다. 76개 대응쌍의 한국어 문자 비율은 평균 +0.2203 증가하고, 68개 쌍에서 +0.02를 초과하는 증가가 나타난다. 한국어 문자 비율 0.5 미만인 언어 이탈 출력은 26개에서 12개로 감소하며, 26개 언어 이탈 쌍 가운데 15개가 SCD 적용 후 0.5 이상으로 이동한다. HyDE와 CAD의 네 조합별 평균 차이도 +0.1981, +0.2415, +0.2012, +0.2402로 모두 양수이다. 검색 문맥을 동일하게 유지한 HyDE-OFF 38개 대응쌍에서도 평균 차이는 +0.2198로 유지된다. 반면 SCD의 내용 품질 변화는 평가 언어와 평가 모델에 따라 다른 범위를 보인다. gpt-4o에서는 answer relevancy의 평균 차이가 영어와 한국어 평가 모두 음의 신뢰구간을 보이지만, gpt-4.1-2025-04-14에서는 두 평가 언어 모두 신뢰구간이 0을 포함한다. 따라서 본 연구에서 SCD의 직접적인 결과는 출력 언어 제어로 해석하며 내용 품질 효과는 평가 조건에 따른 변동과 함께 제시한다.

본 연구의 결과는 한국어 질의 기반 영어 학술문서 RAG에서 HyDE, CAD, SCD가 하나의 공통 성능 방향으로 작동하기보다 서로 다른 목표와 trade-off를 갖는다는 점을 보여준다. HyDE는 질문 관련성과 faithfulness에서 반복적인 양의 방향을 보이고, CAD는 조합 조건에 따라 근거 충실도와 문맥 정밀도에서 긍정적 패턴을 보이는 동시에 질문 관련성과 계산비용의 trade-off를 형성한다. SCD는 검색 조건과 무관하게 비교적 안정적인 한국어 출력 유지 효과를 보인다. 따라서 RAG 기법의 적용 결과는 하나의 종합 점수보다 해결하려는 문제와 직접 연결된 지표, 조합 조건, 실제 입출력 사례를 함께 고려하여 해석하는 것이 적절하다.

**주요어:** Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, 교차언어 검색, 학술정보 질의응답, 언어 이탈, RAG-Cube

---

# Abstract

Academic question answering with large language models requires generated responses to remain grounded in the documents specified by the user. Retrieval-Augmented Generation (RAG) retrieves external evidence and supplies it to the generator, allowing responses to use document-specific information. In a setting where Korean queries target English academic documents and the desired response language is Korean, however, retrieval and generation introduce multiple coupled challenges. Korean queries and English academic passages differ in language and expression; retrieved evidence must be reflected in the generation process; and English context can induce output-language drift away from Korean. This study analyzes these issues along three axes: retrieval representation, evidence-aware generation, and output-language control.

Hypothetical Document Embeddings (HyDE), Context-Aware Decoding (CAD), and Soft Constrained Decoding (SCD) are used as experimental factors for the three axes. Their on/off combinations form a 2×2×2 experimental configuration referred to as RAG-Cube. A fixed Paper-RAG backbone combines BGE-M3 dense retrieval, BM25 sparse retrieval, weighted reciprocal rank fusion with dense/BM25 weights of 0.6/0.4, an ms-marco-MiniLM-L-6-v2 CrossEncoder, five generation passages, and K-intelligence/Midm-2.0-Base-Instruct. The evaluation set consists of 19 Korean query–target-document pairs distributed across four English academic or technical documents: a RAG survey, the CAD paper, the RAPTOR paper, and the Mi:dm K 2.5 Pro Technical Report. Applying eight configurations to the 19 pairs produces 152 generated answers.

Quality is measured with RAGAS faithfulness, answer relevancy, context precision, and context recall, while output-language adherence is measured directly with a Korean-character ratio. The primary HyDE contrast uses 19 pairs with CAD and SCD disabled. The primary CAD contrast uses 19 pairs with HyDE and SCD disabled and byte-identical retrieved contexts. SCD language adherence is analyzed over 76 matched on/off pairs. Content quality under SCD is additionally examined using 38 identical-context pairs normalized into English and Korean panels and evaluated with both gpt-4o and gpt-4.1-2025-04-14.

Across the eight RAG-Cube configurations, no single configuration achieves the highest score on every quality metric. HyDE+CAD with SCD disabled reaches the highest faithfulness (0.9230), while HyDE alone reaches the highest answer relevancy (0.8504). The highest context precision (0.8512) appears in the SCD-only condition, and the baseline configuration reaches the highest context recall (1.0000). In the controlled HyDE contrast, answer relevancy increases by +0.0303 with a 95% confidence interval of [+0.0016, +0.0615], while faithfulness shows a positive mean difference of +0.0734 with heterogeneous query-level outcomes. Across all 76 HyDE-matched pairs, the mean differences in faithfulness and answer relevancy remain positive at +0.0732 and +0.0277.

The strict identical-context CAD contrast yields a faithfulness difference of +0.0023 with a 95% confidence interval of [−0.0903, +0.0952], so an independent average gain is not established in that controlled setting. Configuration-level results nevertheless show a conditional pattern: when HyDE is enabled, adding CAD increases faithfulness by +0.0338 and +0.0503 in the SCD-off and SCD-on strata, respectively, and context precision by +0.0324 and +0.0287. Answer relevancy moves in the opposite direction, indicating a quality trade-off. CAD also increases mean generation time by approximately 2.60–3.22× across matched HyDE/SCD conditions.

SCD shows the most consistent direct target effect. The Korean-character ratio increases by +0.2203 on average across 76 matched pairs, with 68 increases, three decreases, and five ties under a ±0.02 practical band. Outputs below the 0.5 language-drift threshold decrease from 26 to 12, and 15 of the 26 drifting pairs cross above the threshold after SCD is applied. The four HyDE×CAD strata all show positive mean language-adherence deltas, and the HyDE-off identical-context subset of 38 pairs retains a +0.2198 mean increase. Content-quality differences under SCD are more evaluator-dependent: gpt-4o shows a negative answer-relevancy interval in both normalization languages, whereas the fixed gpt-4.1 judge produces intervals overlapping zero. The strongest conclusion for SCD is therefore its output-language control effect rather than a general content-quality effect.

The results indicate that HyDE, CAD, and SCD address different aspects of Korean-query RAG over English academic documents and should not be treated as interchangeable performance boosters. HyDE shows repeated positive patterns in answer relevance and faithfulness, CAD exhibits condition-dependent faithfulness/precision gains together with answer-relevance and computational trade-offs, and SCD provides a robust direct effect on Korean output adherence. Configuration selection should therefore be aligned with the target objective and interpreted with controlled comparisons, configuration-level patterns, and actual input–evidence–output examples.

**Keywords:** Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, cross-lingual retrieval, academic question answering, language drift, RAG-Cube

---

# 목차

1. 서론
   1.1 연구배경 및 목적
   1.2 연구범위

2. 이론적 배경
   2.1 Retrieval-Augmented Generation
   2.2 Hybrid Retrieval과 재정렬
   2.3 Hypothetical Document Embeddings
   2.4 Context-Aware Decoding
   2.5 Soft Constrained Decoding과 언어 이탈
   2.6 RAG 평가

3. 시스템 설계
   3.1 연구 및 실험 요구사항
   3.2 아키텍처 설계
   3.3 상세설계

4. 프로그램 구현
   4.1 시스템 환경
   4.2 시스템 구성
   4.3 시스템 구현

5. 실험
   5.1 실험 대상과 구성
   5.2 평가 및 분석 방법
   5.3 RAG-Cube 조합별 결과
   5.4 HyDE 결과 및 해석
   5.5 CAD 결과 및 해석
   5.6 SCD 출력 언어 결과 및 해석
   5.7 SCD 대칭 품질 평가 및 해석
   5.8 대표 입출력 사례 분석
   5.9 종합 논의
   5.10 연구의 한계

6. 결론

참고문헌
부록

---

# 그림 목차

[그림 1-1] 한국어 질의 기반 영어 학술문서 RAG 연구 환경
[그림 3-1] HyDE·CAD·SCD의 2×2×2 RAG-Cube 실험 구성
[그림 3-2] RAG-Cube 실험 아키텍처와 단계별 데이터 흐름
[그림 4-1] 고정 Paper-RAG backbone과 실험 요인의 적용 위치
[그림 4-2] 생성 artifact와 평가·분석 자료의 연결 구조
[그림 5-1] 실험 요인별 비교 및 평가 설계
[그림 5-2] RAG-Cube 여덟 조건의 품질 지표 비교
[그림 5-3] HyDE와 CAD 통제 비교의 대응 평균 차이
[그림 5-4] HyDE·CAD 조합 조건별 품질 변화 패턴
[그림 5-5] SCD 적용 전후 한국어 문자 비율과 언어 이탈 변화
[그림 5-6] 평가 언어와 평가 모델에 따른 SCD 품질 차이
[그림 5-7] 한국어 질의–영어 근거–한국어 응답의 실제 입출력 사례
[그림 5-8] SCD 미적용 언어 이탈과 동일 문맥 SCD 적용 사례
[그림 5-9] HyDE 적용에 따른 검색 표현과 검색 결과 변화 사례
[그림 5-10] 동일 검색 문맥에서 CAD 적용 전후의 상반된 응답 사례

---

# 표 목차

[표 3-1] 연구 및 실험 요구사항
[표 3-2] RAG-Cube의 여덟 가지 실험 조건
[표 3-3] 실험 요인별 적용 위치와 비교 단위
[표 4-1] 실험 실행 환경
[표 4-2] 고정 Paper-RAG backbone 설정
[표 4-3] 조건별 평균 생성 시간
[표 4-4] 생성 record의 주요 저장 필드
[표 5-1] 실험 대상 문서와 질의-대상문서 쌍 구성
[표 5-2] RAG-Cube 여덟 조건의 평균 RAGAS 품질 지표
[표 5-3] HyDE 통제 비교 결과
[표 5-4] CAD 동일 문맥 통제 비교 결과
[표 5-5] SCD 설정별 한국어 문자 비율과 언어 이탈 수
[표 5-6] SCD 언어 유지 효과의 대응 분석
[표 5-7] SCD의 평가 언어·모델별 품질 차이

---

# 1. 서론

## 1.1 연구배경 및 목적

대규모 언어모델은 자연어 질문을 이해하고 자연스러운 문장 형태의 답변을 생성할 수 있어 정보 탐색, 문서 요약, 질의응답과 같은 작업에 폭넓게 활용된다. 학술정보 활용에서도 사용자가 논문 전체를 순차적으로 읽는 방식에 더해, 특정 방법론의 정의, 실험 조건, 수치 결과, 결론과 한계를 자연어로 질문하고 관련 내용을 빠르게 확인하는 방식이 가능해졌다. 그러나 이러한 활용에서 중요한 것은 단순히 그럴듯한 답변을 생성하는 능력이 아니라, 사용자가 지정한 문서의 실제 내용과 답변 사이의 연결을 유지하는 것이다.

Retrieval-Augmented Generation(RAG)은 생성 모델의 파라미터에 저장된 정보만을 사용하는 대신 외부 문서에서 관련 근거를 검색하고 이를 생성 입력으로 제공하는 구조이다[1]. RAG는 검색 단계와 생성 단계를 연결함으로써 특정 문서의 세부 내용을 답변에 반영할 수 있게 한다. 특히 학술문서 질의응답에서는 검색된 문단이 답변의 근거가 되기 때문에 어떤 문단을 가져오는지, 해당 문단을 생성 과정에서 얼마나 활용하는지, 생성된 답변이 사용자가 요청한 형식과 언어를 유지하는지가 모두 최종 품질에 영향을 준다. RAG의 연구 흐름도 검색 전 처리, 검색, 검색 후 처리, 생성, 평가 등 여러 단계의 설계 선택을 함께 다루는 방향으로 확장되고 있다[2].

본 연구가 다루는 환경은 한국어 질의와 영어 학술·기술 문서가 결합된 질의응답이다. 사용자는 한국어로 질문하고, 각 질문에 지정된 영어 문서에서 근거를 검색하며, 최종 답변은 한국어를 목표 언어로 한다. 이 환경에서는 일반적인 RAG 문제에 더해 질의 언어와 근거 문서 언어가 다르다는 조건이 존재한다. 한국어 질의와 영어 학술문장은 같은 개념을 서로 다른 어휘와 표현으로 기술할 수 있기 때문에 짧은 질의 표현이 실제 문서의 관련 구절과 충분히 연결되지 않을 수 있다. 반대로 의미적으로 관련된 문단이 검색되더라도 생성 모델이 해당 근거보다 모델 내부 지식이나 일반적인 설명을 우선하면 근거와 답변 사이의 충실도가 낮아질 수 있다. 또한 생성 입력의 상당 부분이 영어 문맥으로 구성되면 사용자가 한국어로 질문하더라도 답변이 영어로 이어지는 언어 이탈이 발생할 수 있다.

이 세 문제는 서로 다른 단계에 위치한다. 첫 번째 문제는 검색 표현과 관련된다. 질의를 문서와 가까운 표현으로 확장하면 dense retrieval이 다른 후보를 선택할 수 있다. 두 번째 문제는 생성 분포와 관련된다. 검색 문맥이 존재하더라도 모델이 그 문맥의 정보를 얼마나 강하게 반영하는지는 디코딩 방식에 따라 달라질 수 있다. 세 번째 문제는 출력 토큰 선택과 관련된다. 동일한 의미의 답변을 생성하면서도 목표 언어의 토큰을 더 안정적으로 선택하도록 디코딩을 제어할 수 있다. 따라서 하나의 RAG 구성에서 검색 표현, 근거 기반 생성, 출력 언어 제어를 구분해 분석하면 각 기법이 최종 응답의 어떤 부분에 영향을 주는지 더 구체적으로 확인할 수 있다.

본 연구는 이러한 세 지점에 대응하는 기존 기법으로 HyDE(Hypothetical Document Embeddings)[3], CAD(Context-Aware Decoding)[4], SCD(Soft Constrained Decoding)[5]를 사용한다. HyDE는 질문에 답할 것으로 예상되는 가상 문서를 생성하고 그 표현을 dense retrieval에 활용하여 검색 입력을 확장한다. CAD는 동일한 생성 모델에서 문맥이 있는 분포와 문맥이 없는 분포를 대조하여 문맥에 의해 강화되는 토큰을 생성 과정에서 더 반영한다. SCD는 목표 언어, 비목표 언어, 중립 토큰을 구분하고 raw logit을 조정하여 목표 언어의 출력을 유지한다. 세 기법은 각각 retrieval, context-aware generation, language control이라는 서로 다른 위치에서 동작한다.

세 기법의 적용 여부를 독립적인 이진 요인으로 두면 여덟 개의 조합이 만들어진다. 본 연구에서는 이 2×2×2 실험 구성을 **RAG-Cube**로 지칭한다. RAG-Cube는 HyDE·CAD·SCD 세 요인을 동일한 backbone에서 비교하기 위해 구성한 2×2×2 실험 구성을 가리킨다. 이 구성은 개별 기법의 통제 비교와 함께 세 기법이 결합된 실제 configuration의 결과를 동시에 관찰할 수 있다는 장점이 있다.

개별 요인의 효과만 확인하면 특정 기법을 다른 조건과 분리해서 해석하기는 쉽지만, 실제 조합에서 나타나는 trade-off를 파악하기는 어렵다. 예를 들어 검색 표현을 변경하는 HyDE가 생성 모델에 제공되는 근거를 바꾸면 CAD의 생성 제어가 작동하는 입력 자체가 달라질 수 있다. SCD는 출력 언어를 제어하지만 그 과정이 answer relevancy나 faithfulness와 같은 내용 품질 지표에 어떤 관계를 갖는지는 별도로 확인해야 한다. 따라서 본 연구는 각 요인의 통제 대비와 전체 8개 configuration의 기술적 결과를 함께 제시한다. 통제 대비는 가능한 범위에서 비교 조건을 고정하여 요인별 변화를 분석하고, 전체 조합 분석은 실제 RAG-Cube 조건에서 나타나는 성능 패턴과 trade-off를 관찰하는 데 사용한다.

본 연구의 고정 Paper-RAG backbone은 BGE-M3 dense retrieval, BM25 sparse retrieval, weighted Reciprocal Rank Fusion(RRF), CrossEncoder 재정렬, 문맥 선택·압축, Mi:dm 2.0 Base Instruct 생성 모델로 구성된다. HyDE를 제외한 검색 구조와 생성 모델은 전체 configuration에서 동일하게 유지하며 CAD와 SCD는 생성 단계의 logits 처리 과정에 적용한다. 연구 대상은 네 개 영어 학술·기술 문서에 각각 대응하는 19개의 한국어 질의-대상문서 쌍이다. 각 쌍에 여덟 configuration을 적용하여 총 152개의 생성 답변을 구성한다.

연구 질문은 다음과 같다.

첫째, CAD·SCD 미적용 통제 조건에서 HyDE는 RAG 품질 지표를 어떻게 변화시키는가?
둘째, HyDE·SCD 미적용 및 동일 검색 문맥 조건에서 CAD는 답변 품질을 어떻게 변화시키는가?
셋째, HyDE와 CAD 조건을 동일하게 맞춘 대응쌍에서 SCD는 한국어 출력 유지와 언어 이탈에 어떤 변화를 만드는가?
넷째, RAG-Cube의 여덟 조합에서는 faithfulness, answer relevancy, context precision, context recall 사이에 어떤 configuration별 trade-off가 나타나는가?
다섯째, SCD 적용에 따른 내용 품질 차이는 평가 언어와 평가 모델을 변경했을 때 어떤 범위로 나타나는가?

본 연구의 목적은 세 기법을 각자의 적용 단계와 직접 목표에 따라 분석하고, 조합 조건에서 나타나는 품질 차이와 trade-off를 함께 해석하는 데 있다. HyDE는 검색 표현을 바꾸고, CAD는 근거를 고려한 생성 분포를 조정하며, SCD는 출력 언어를 제어한다. 따라서 각 기법의 목적과 직접 연결되는 지표를 우선하여 분석하고, 전체 조합에서 나타나는 품질 차이와 실제 입출력 사례를 함께 검토함으로써 한국어 질의 기반 영어 학술문서 RAG에서 각 기법의 적용 결과를 구체적으로 해석한다.

[그림 삽입: `figures/fig01_research_setting.svg`]

**[그림 1-1]** 한국어 질의 기반 영어 학술문서 RAG 연구 환경. 한국어 질의와 영어 근거 문서 사이의 언어·표현 차이, 검색 근거의 생성 단계 반영, 한국어 출력 유지라는 세 분석 지점을 나타낸다.

## 1.2 연구범위

연구 대상 문서는 RAG의 전반적인 구조와 분류를 다루는 *Retrieval-Augmented Generation for Large Language Models: A Survey*, 문맥 기반 디코딩을 다루는 CAD 논문, 계층적 검색을 다루는 RAPTOR 논문[21], Mi:dm K 2.5 Pro Technical Report[22]의 네 문서이다. 네 문서는 모두 영어 본문을 검색 대상으로 사용한다. 19개의 한국어 질의는 각 문서의 내용에 대응하도록 구성되며, 하나의 질의는 하나의 대상 문서와 연결된다. 따라서 실험 단위는 동일 질문을 여러 문서에 반복 적용하는 구조가 아니라 19개의 **질의-대상문서 쌍**이다.

문서별 질의 수는 RAG Survey 5개, CAD 4개, RAPTOR 4개, Mi:dm K 2.5 Pro Technical Report 6개이다. 각 질의는 지정된 문서의 청크 집합 안에서 검색을 수행한다. 이 구성은 대상 문서를 이미 알고 있는 학술문서 질의응답 상황을 모델링하며, 동일한 질의-문서 쌍을 여덟 configuration에서 반복 실행하여 조건 간 차이를 대응 비교할 수 있게 한다.

검색 backbone은 BGE-M3와 BM25의 두 경로, weighted RRF, CrossEncoder, 다섯 개 생성 문맥으로 고정한다. 생성 모델은 K-intelligence/Midm-2.0-Base-Instruct[20]를 사용한다. 생성 모델의 파라미터는 고정된 상태로 추론을 수행하며, 실험 요인은 HyDE·CAD·SCD의 적용 여부와 각 기법의 고정 설정으로 한정한다. HyDE는 검색 표현을 변경하고 CAD와 SCD는 생성 단계의 logits 처리에 적용한다.

평가 범위는 네 가지 RAGAS 품질 지표와 직접 언어 지표를 포함한다. HyDE와 CAD의 기본 비교는 다른 요인의 영향을 제한한 19개 대응쌍으로 수행한다. CAD 비교에서는 저장된 검색 문맥의 byte-level identity를 확인하여 generation-side 차이를 중심으로 분석한다. SCD의 직접 언어 효과는 76개 on/off 대응쌍에서 한국어 문자 비율과 언어 이탈 수로 측정한다. SCD의 내용 품질은 HyDE OFF의 동일 문맥 38개 대응쌍을 별도 정규화하여 두 평가 언어와 두 평가 모델에서 검토한다.

전체 RAG-Cube 분석은 여덟 configuration의 평균 품질 지표를 함께 제시하여 실제 조합에서 나타나는 패턴을 확인한다. 조합별 기술통계와 통제 대비를 서로 다른 분석 수준으로 사용하며, CAD의 generation-side 통제 결과는 HyDE OFF의 동일 문맥 비교를 기준으로 하고 HyDE ON의 CAD 결과는 조합 수준의 기술적 패턴으로 제시한다.

연구 결과의 재현성을 위해 generation record에는 질의, 대상 문서, configuration, 검색 문맥, retrieved chunk ID, reranked chunk ID, 생성 답변, 모델과 decoding 설정, 실행 상태와 시간 정보를 저장한다. 품질 평가와 언어 분석도 generation artifact와 분리된 파일로 보존하여 본문 표와 그림의 수치를 다시 계산할 수 있게 한다. 이러한 범위는 본 연구의 핵심 분석 단위인 질의-문서 쌍, configuration, 검색 문맥, 생성 답변, 평가 결과를 하나의 추적 가능한 흐름으로 연결한다.

---

# 2. 이론적 배경

## 2.1 Retrieval-Augmented Generation

RAG는 사용자의 질의를 기반으로 외부 문서 집합에서 관련 정보를 검색하고, 검색된 정보를 생성 모델의 조건 문맥으로 제공하는 구조이다[1]. 사용자의 질의를 q, 검색 대상 문서 집합을 D, 검색 결과를 C_q, 생성 답변을 y라고 하면 기본 과정은 다음과 같이 표현할 수 있다.
한컴 한글 수식 입력기 입력값:
```text
C_q = Retrieve(q,D)
```
한컴 한글 수식 입력기 입력값:
```text
y = LM(q,C_q)
```

첫 번째 식은 검색 단계가 질의와 관련된 근거 후보를 선택하는 과정을 나타내며, 두 번째 식은 생성 모델이 질문과 검색 문맥을 함께 이용하여 답변을 생성하는 과정을 나타낸다. 이 단순한 구조에서도 최종 답변은 검색과 생성 두 단계의 영향을 모두 받는다. 질문에 필요한 근거가 검색되지 않으면 생성 모델이 해당 근거를 사용할 수 없고, 적절한 근거가 검색되어도 생성 모델이 이를 충분히 반영하지 않으면 근거와 답변 사이의 정합성이 낮아질 수 있다.

학술문서 질의응답은 이러한 특성이 명확하게 드러나는 응용 환경이다. 사용자가 특정 논문의 방법론이나 수치 결과를 질문할 때 답변의 근거는 해당 논문의 관련 문단에 존재한다. 검색기는 질문에 대응되는 부분을 가져와야 하며, 생성기는 해당 문단의 내용을 중심으로 답변을 구성해야 한다. 따라서 일반적인 자연어 유창성만으로는 학술문서 질의응답의 품질을 평가하기 어렵고, 검색 근거가 질문과 얼마나 관련되는지, 답변의 주장이 근거에 의해 뒷받침되는지를 함께 확인해야 한다.

RAG 연구는 검색 전 처리, 검색기, 검색 결과의 결합과 재정렬, 문맥 구성, 생성, 평가로 세분화된다[2]. 검색 전 단계에서는 질의를 변환하거나 확장할 수 있고, 검색 단계에서는 dense·sparse retrieval을 단독 또는 함께 사용할 수 있다. 검색 후 단계에서는 여러 검색기의 결과를 결합하고 reranker로 순서를 조정할 수 있다. 생성 단계에서는 문맥을 단순히 prompt에 넣는 것뿐 아니라 모델의 decoding distribution을 제어할 수도 있다. 본 연구의 HyDE, CAD, SCD는 이 가운데 서로 다른 지점에 위치한다.

본 연구에서 RAG는 새로운 구조를 제안하기 위한 대상이 아니라 세 기존 기법을 동일 조건에서 비교하기 위한 고정 backbone이다. 검색 backbone과 생성 모델을 가능한 범위에서 고정하고, HyDE·CAD·SCD의 적용 위치만 변화시켜 각 configuration을 구성한다. 이를 통해 하나의 기법이 작동하는 단계와 해당 기법의 직접 목표가 어떤 평가 지표와 연결되는지를 구분한다.

학술문서의 길이와 구조도 문맥 구성에 영향을 준다. 긴 문맥에서는 관련 정보가 위치하는 지점에 따라 언어모델의 활용 정도가 달라질 수 있다는 연구가 보고되어 있다[11]. 본 연구는 reranking된 후보에서 다섯 개 문맥을 선택하고, 높은 순위 문맥이 앞쪽에만 집중되지 않도록 순서를 재배치한 뒤 추출형 압축과 길이 제한을 적용한다. 이러한 처리는 세 실험 요인과 별도로 고정된 backbone의 일부로 사용한다.

## 2.2 Hybrid Retrieval과 재정렬

Dense retrieval은 질의와 문서를 연속적인 벡터로 변환하여 의미적 유사성을 계산한다. 본 연구의 dense retriever는 BGE-M3 계열의 표현 모델을 사용한다[6]. BGE-M3는 다국어 입력을 지원하므로 한국어 질의와 영어 문단을 하나의 임베딩 공간에서 비교할 수 있다. 교차언어 질의응답에서는 질의와 문서가 동일한 표면 단어를 공유하지 않는 경우가 많기 때문에 의미적 유사성을 활용하는 dense retrieval이 중요한 역할을 한다.

Sparse retrieval은 토큰의 표면적 일치와 통계적 중요도를 이용한다. 본 연구는 BM25를 sparse retriever로 사용한다[7]. BM25는 질의와 문서의 단어가 직접 일치할 때 강한 신호를 제공하므로 모델명, 약어, 벤치마크 이름, 숫자와 같은 표현을 찾는 데 dense retrieval을 보완할 수 있다. 한국어 질의와 영어 문서의 언어가 다르기 때문에 모든 질의에서 sparse 경로가 동일하게 작동한다고 가정하기보다 실제 후보 기록을 함께 확인하는 것이 중요하다.

Dense와 BM25는 점수의 의미와 범위가 서로 다르기 때문에 raw score를 직접 더하지 않고 rank 기반 결합을 사용한다. 본 연구는 Reciprocal Rank Fusion(RRF)[8]을 기반으로 dense와 BM25 순위에 각각 0.6과 0.4의 가중치를 적용한다. 문서 d의 결합 점수는 다음 형태로 표현된다.
한컴 한글 수식 입력기 입력값:
```text
RRF(d) = {0.6} over {k + rank_dense(d)} + {0.4} over {k + rank_BM25(d)}
```

여기서 0.6과 0.4는 본 연구에서 고정한 dense·BM25 fusion weight이다. 두 검색기에서 모두 발견된 문단은 두 항의 기여를 함께 받으며 한 경로에만 나타난 문단도 해당 순위를 통해 후보에 포함될 수 있다.

결합된 후보는 ms-marco-MiniLM-L-6-v2 CrossEncoder로 다시 정렬한다. CrossEncoder 계열의 passage reranking은 질의와 후보 문단을 함께 입력하여 pair-level 관련성을 계산한다[9][10]. 본 연구는 최대 8개의 결합 후보를 reranker에 입력하고, 상위 결과를 바탕으로 다섯 개 생성 문맥을 구성한다. Reranker 단계에는 원래 한국어 질의를 사용한다. 따라서 본 실험의 reranking 결과는 한국어 질의와 영어 passage를 직접 매칭하는 고정 backbone 조건에서 해석한다.

검색 결과는 단순한 상위 순서 그대로 생성 모델에 연결되지 않는다. 문맥 선택 단계는 reranking 결과에서 상위 다섯 문단을 선정하고, 높은 관련도의 문단이 입력의 앞과 뒤에 배치되도록 순서를 조정한다. 이후 질의 관련 문장을 유지하는 추출형 압축과 전체 길이 제한을 적용한다. 이러한 문맥 구성은 모든 RAG-Cube 조건에서 동일한 규칙을 사용하며, HyDE가 검색 후보 자체를 변경하는 경우에만 입력 문맥이 달라질 수 있다.

## 2.3 Hypothetical Document Embeddings

HyDE는 질의를 직접 dense embedding으로 변환하는 대신, 질의에 답할 법한 가상의 문서를 먼저 생성하고 그 문서의 embedding으로 실제 자료를 검색하는 방법이다[3]. 정답 relevance label이 없는 zero-shot dense retrieval에서 짧은 질문과 실제 문서 사이의 표현 차이를 보완하기 위해 제안되었다. 질문 자체보다 문서와 유사한 형태의 가상 서술을 검색 표현으로 사용한다는 점이 핵심이다.

교차언어 학술문서 환경에서 HyDE는 두 가지 변환을 포함한다. 본 연구에서는 한국어 질의를 영어로 번역한 뒤 영어 가상 문서를 생성한다. 생성된 가상 문서는 BGE-M3 dense retrieval의 입력으로 사용한다. 반면 BM25 경로와 CrossEncoder reranking에는 원래 한국어 질의를 사용한다. 따라서 HyDE ON 조건은 dense retrieval 표현을 변경하지만 sparse path와 reranking query는 고정한다.

HyDE 가상 문서는 dense retrieval의 검색 표현으로 사용하고, 최종 생성 모델에는 실제 대상 문서에서 검색된 passage를 제공한다. 이 구성은 hypothetical document와 최종 근거 문맥의 역할을 분리한다. 이 구분은 HyDE가 retrieval-side intervention이라는 점을 명확하게 한다.

본 연구의 HyDE 조건은 영어 번역과 hypothetical document generation을 하나의 검색 확장 과정으로 구성한다. 따라서 HyDE ON/OFF 차이는 번역 자체의 영향과 가상 문서 생성의 영향을 분리한 순수 효과가 아니라 본 연구의 HyDE pipeline 전체가 만든 end-to-end retrieval 차이를 의미한다. 이 해석 범위는 HyDE 결과를 논의할 때 함께 고려한다.

HyDE의 결과는 retrieval metric만으로 평가하기 어렵다. 가상 문서가 검색 후보를 변경하면 최종 answer relevancy나 faithfulness가 개선될 수 있지만 동시에 검색 문맥 전체의 precision이 높아진다는 보장은 없다. 본 연구는 이러한 가능성을 확인하기 위해 context precision·recall과 answer relevancy·faithfulness를 함께 보고하고, 실제 retrieval ID가 바뀐 대표 사례도 별도로 제시한다.

## 2.4 Context-Aware Decoding

CAD는 모델의 생성 단계에서 문맥이 존재할 때와 존재하지 않을 때의 next-token distribution을 대조하여 문맥에 의해 강화되는 방향을 반영하는 decoding 기법이다[4]. 검색 결과를 변경하는 방법이 아니라 이미 주어진 문맥을 생성 과정에서 어떻게 활용할 것인지에 관여한다.

문맥이 포함된 logits를 z_ctx, 문맥이 없는 logits를 z_noctx라고 하면 본 연구에서 사용하는 CAD의 기본 형태는 다음과 같다.
한컴 한글 수식 입력기 입력값:
```text
z_CAD = (1 + alpha) z_ctx - alpha z_noctx
```

본 실험에서는 α=0.5를 고정한다. 동일한 생성 prefix에 대해 context branch와 no-context branch를 계산하고 두 분포의 차이를 반영한다. 이 구조는 모델이 문맥 없이도 쉽게 생성하는 토큰보다 주어진 문맥에서 더 강하게 활성화되는 토큰을 상대적으로 강조한다.

CAD의 primary comparison은 retrieval을 고정한 generation-side 비교로 구성한다. HyDE OFF, SCD OFF 조건의 CAD ON/OFF 19개 대응쌍에서 검색 문맥의 byte 단위 동일성을 확인하고, 이 19쌍을 primary CAD contrast로 사용한다. 따라서 해당 비교의 핵심 해석 대상은 동일 근거에서 나타나는 생성 결과의 변화이다.

CAD는 계산비용 측면에서도 특징이 분명하다. 매 토큰에서 context branch와 no-context branch를 함께 계산하므로 단일 branch 생성보다 연산량이 증가한다. 본 연구는 품질 지표뿐 아니라 configuration별 평균 생성 시간도 함께 제시하여 CAD가 보이는 품질 변화와 계산비용을 동시에 분석한다.

CAD는 contrastive decoding의 일반적인 대조 관점과 관련된다[12]. 국내에서도 CAD의 대조 구조를 확장한 연구가 제시되어 있다[13]. 본 연구는 CAD 자체를 변경하는 것이 아니라 원 기법의 context-aware score를 고정 α 조건으로 적용하고, Paper-RAG backbone의 실제 조합에서 나타나는 결과를 비교한다.

## 2.5 Soft Constrained Decoding과 언어 이탈

다국어 RAG에서 검색 문서의 언어는 생성 결과의 언어에 영향을 줄 수 있다. 사용자가 한국어로 질문하더라도 생성 모델에 영어 근거가 연속적으로 제공되면 답변이 영어로 이어지거나 한국어와 영어가 불필요하게 혼합될 수 있다. SCD는 이러한 language drift를 decoding 단계에서 완화하기 위해 목표 언어와 비목표 언어에 따라 token score를 조정하는 방법이다[5].

본 연구의 SCD는 tokenizer vocabulary를 한국어 목표 토큰, 영어 비목표 토큰, 중립 토큰으로 구분한다. 중립 토큰에는 공백, 문장부호, 숫자, 수식, 괄호와 인용 표기처럼 언어에 직접 종속되지 않는 표현이 포함된다. generated-token warm-up T_start=5 이후 raw logit에 다음 계수를 적용한다.

SCD의 token group별 score 조정은 한글 수식 입력기에서 안정적으로 사용할 수 있도록 세 식으로 나누어 제시한다.
```text
tilde z_i = alpha z_i
```
```text
tilde z_i = beta z_i
```
```text
tilde z_i = z_i
```

한국어 목표 토큰에는 `alpha` 계수를, 영어 비목표 토큰에는 `beta` 계수를 적용하며, 중립 토큰의 score는 그대로 유지한다. 각 적용 대상은 각각 `i in V_ko`, `i in V_en`, `i in V_neutral`로 구분한다.

본 연구의 설정은 α=1.1, β=0.9, T_start=5이다. CAD와 SCD가 함께 적용되는 경우 CAD score를 계산한 뒤 SCD processor를 적용하여 processor order를 고정한다.

SCD의 직접 목표는 생성 답변의 언어 유지이다. 본 연구는 이 목표를 생성 답변에서 직접 계산한 한국어 문자 비율로 측정한다. 한국어 문자 비율은 생성 답변의 한글 문자 수를 한글 문자 수와 ASCII 영문자 수의 합으로 나누어 계산한다. 이 비율이 0.5 미만인 출력을 언어 이탈 사례로 분류한다.

출력 언어 제어와 답변 내용 품질은 별개의 평가 차원이다. 본 연구는 Korean-character ratio를 language adherence의 직접 지표로 사용하고, faithfulness와 answer relevancy는 동일 검색 문맥 대응쌍을 대상으로 한 symmetric evaluation에서 별도로 측정한다.

## 2.6 RAG 평가

본 연구의 품질 평가는 RAGAS의 faithfulness, answer relevancy, context precision, context recall을 사용한다[15]. RAGAS는 RAG 시스템의 검색 문맥과 생성 답변을 분리하여 평가할 수 있는 자동 평가 프레임워크이다. 국내 RAG 평가 연구와 재현 가능한 benchmarking 연구도 검색과 생성의 다차원 평가 필요성을 보여준다[16][17].

Faithfulness는 답변의 주장들이 제공된 검색 문맥에 의해 뒷받침되는 정도를 나타낸다. Answer relevancy는 생성된 답변이 사용자의 질문에 얼마나 직접적이고 적절하게 대응하는지를 측정한다. Context precision은 검색 문맥 중 질문과 관련된 근거가 얼마나 우선되고 포함되는지를, context recall은 reference answer를 뒷받침하는 필요한 정보가 검색 문맥에 얼마나 포함되는지를 평가한다. 네 지표는 서로 다른 목표를 측정하므로 결과 해석에서는 각 지표의 방향과 조합별 trade-off를 개별적으로 확인한다.

HyDE와 CAD의 primary comparison은 동일한 19개 query ID의 on/off 차이를 계산한다. 각 질의를 재표집 단위로 하는 paired percentile bootstrap을 200,000회 수행하여 평균 차이의 95% 신뢰구간을 계산한다. 품질 지표의 practical win/loss/tie는 on−off 차이가 +0.01을 초과하면 win, −0.01 미만이면 loss, 그 사이이면 tie로 구분한다.

SCD 언어 분석의 practical band는 품질 비교와 구분하여 ±0.02를 사용한다. 동일 query·HyDE·CAD 조건의 76개 on/off 쌍에서 한국어 문자 비율의 차이를 계산하고 +0.02 초과를 증가, −0.02 미만을 감소, 그 사이를 동률로 집계한다. 또한 0.5와 0.3 threshold에서 SCD OFF 상태의 drift pair가 SCD ON에서 기준선 위로 이동하는지를 분석한다.

SCD content quality는 38개 동일 문맥 대응쌍을 영어와 한국어 panel로 정규화한 뒤 gpt-4o와 gpt-4.1-2025-04-14로 평가한다. Faithfulness와 answer relevancy의 SCD ON−OFF 차이를 계산하고 19개 query ID를 cluster로 하는 10,000회 percentile bootstrap을 적용한다. 다국어 LLM-as-a-Judge는 평가 언어와 judge model에 따라 결과 범위가 달라질 수 있다는 점이 보고되어 있다[19]. 본 연구는 동일한 effect가 두 평가 언어와 두 judge에서 어떤 범위로 나타나는지를 함께 비교한다. GPT-4o System Card[18]는 평가에 사용한 모델의 사양과 실행 provenance를 설명하는 참고자료로 활용한다.

---

# 3. 시스템 설계

## 3.1 연구 및 실험 요구사항

본 연구의 설계 대상은 사용자 기능 중심의 응용 서비스가 아니라 HyDE·CAD·SCD의 조합을 동일한 Paper-RAG backbone에서 실행하고, 비교에 필요한 입력·검색·생성·평가 정보를 보존하는 실험 프로그램이다. 따라서 요구사항은 화면 기능보다 연구 변인의 통제, 조건 반복, 결과 추적, 재현 가능성에 초점을 둔다.

**[표 3-1] 연구 및 실험 요구사항**

| ID | 요구사항 | 검증 기준 |
|---|---|---|
| R1 | 한국어 질의와 지정된 영어 대상 문서를 연결한다. | query ID와 paper ID가 1:1로 추적된다. |
| R2 | HyDE·CAD·SCD의 여덟 조합을 동일한 19개 질의-문서 쌍에 적용한다. | 각 configuration 19개, 총 152개 generation record가 존재한다. |
| R3 | 비교 대상 이외의 Paper-RAG backbone을 고정한다. | retriever, fusion, reranker, context 수, generator 설정을 기록한다. |
| R4 | HyDE, CAD, SCD의 적용 상태와 세부 파라미터를 record에 저장한다. | configuration 및 decoder metadata를 확인한다. |
| R5 | 답변과 함께 검색 문맥, retrieved ID, reranked ID를 보존한다. | 각 record에서 retrieval provenance를 추적할 수 있다. |
| R6 | CAD 통제 비교에 동일 검색 문맥을 사용할 수 있어야 한다. | primary CAD 19쌍의 context identity를 확인한다. |
| R7 | SCD 언어 효과와 내용 품질을 별도 평가 흐름으로 계산한다. | Korean ratio 분석과 symmetric quality 분석을 분리한다. |
| R8 | 본문 표와 그림의 수치를 저장 artifact에서 다시 계산할 수 있어야 한다. | verifier와 figure builder가 모델 재실행 없이 결과를 재현한다. |
| R9 | 실행 상태와 시간을 기록한다. | status, 시작 시각, duration을 record별로 확인한다. |
| R10 | 평가 결과와 원 generation을 분리 보존한다. | generation JSONL과 evaluation/analysis artifact를 독립적으로 추적한다. |

요구사항 R1과 R2는 실험 단위의 일관성을 보장한다. 각 질의는 지정된 하나의 대상 문서와 연결되며 여덟 configuration에서 동일한 질의-문서 쌍을 반복한다. 따라서 configuration 간 차이는 질의나 대상 문서의 변경이 아니라 실험 요인의 적용 상태 변화와 연결된다.

R3과 R4는 고정 조건과 실험 요인을 구분한다. BGE-M3, BM25, RRF, reranker, context 수, generator는 backbone으로 관리하고 HyDE·CAD·SCD만 요인으로 변경한다. 각 요인의 설정은 결과 record에 함께 저장하여 configuration 이름과 실제 실행 metadata를 일치시켜 확인할 수 있게 한다.

R5와 R6는 특히 CAD와 HyDE 결과 해석에 중요하다. HyDE는 retrieval을 변경하므로 retrieved ID와 context가 달라지는 것이 정상적인 효과의 일부이다. 반면 CAD는 generation-side intervention이므로 primary comparison에서는 검색 문맥의 동일성을 확인해야 한다. 따라서 generation answer뿐 아니라 retrieval provenance 자체가 연구 데이터로 취급된다.

R7과 R8은 평가 단계의 분리를 보장한다. SCD는 직접 언어 제어 지표와 content-quality 지표가 서로 다른 의미를 가지므로 별도 파일에서 계산한다. 표와 그림은 저장된 결과에서 계산한 분석 artifact를 기반으로 생성한다. 이 구조는 논문에 사용되는 수치와 원자료의 연결을 명확하게 한다.

## 3.2 아키텍처 설계

RAG-Cube의 세 요인은 RAG pipeline의 서로 다른 지점에 배치된다. HyDE는 dense retrieval 입력을 결정하는 검색 전 단계에, CAD와 SCD는 생성 모델의 token decoding 단계에 적용된다. 이러한 위치 차이를 유지하기 위해 실험 아키텍처는 입력, 검색 표현 구성, hybrid retrieval, 재정렬 및 문맥 구성, 생성, artifact 저장, 평가·분석의 일곱 단계로 구성한다.

[그림 삽입: `figures/fig03_rag_cube.svg`]

**[그림 3-1]** HyDE·CAD·SCD의 2×2×2 RAG-Cube 실험 구성. H, C, S는 각 기법을 나타내며 0과 1은 각각 OFF와 ON을 의미한다. RAG-Cube는 세 이진 실험 요인의 조합을 나타내는 실험 구성이다.

**[표 3-2] RAG-Cube의 여덟 가지 실험 조건**

| Configuration | HyDE | CAD | SCD |
|---|---|---|---|
| H0C0S0 | OFF | OFF | OFF |
| H0C1S0 | OFF | ON | OFF |
| H0C0S1 | OFF | OFF | ON |
| H0C1S1 | OFF | ON | ON |
| H1C0S0 | ON | OFF | OFF |
| H1C1S0 | ON | ON | OFF |
| H1C0S1 | ON | OFF | ON |
| H1C1S1 | ON | ON | ON |

입력 단계는 query split에서 19개 질의와 각 질의의 target paper를 읽는다. 검색 표현 단계에서 HyDE OFF이면 원질의를 dense retrieval에 사용하고, HyDE ON이면 한국어 질의를 영어로 번역한 뒤 생성한 영어 hypothetical document를 dense retrieval에 사용한다. BM25와 CrossEncoder에는 원질의를 사용한다.

Hybrid retrieval은 BGE-M3와 BM25에서 각각 최대 8개 후보를 수집하고 weighted RRF로 결합한다. 결합 후보는 CrossEncoder로 재정렬한 뒤 다섯 문단의 생성 문맥을 구성한다. 문맥 구성은 높은 순위 후보의 위치 재배치, 추출형 압축, 길이 제한을 포함한다.

생성 단계는 Mi:dm 2.0 Base Instruct가 질문과 영어 근거 문맥을 입력받아 답변 token을 순차 생성한다. CAD OFF에서는 context branch의 logits를 그대로 사용하고, CAD ON에서는 context/no-context score를 대조한다. SCD ON이면 CAD 처리 후의 score 또는 기본 logits에 한국어·영어·중립 vocabulary coefficient를 적용한다.

생성 결과는 JSONL record로 저장된다. 이후 evaluation 단계가 해당 record를 읽어 RAGAS 점수를 계산하며 language analyzer는 Korean-character ratio를 계산한다. 분석 단계는 configuration 평균, paired delta, bootstrap interval, win/loss/tie, drift transition을 계산하고 figure builder는 같은 결과를 표와 그림으로 변환한다.

[그림 삽입: `figures/fig04_experiment_architecture.svg`]

**[그림 3-2]** RAG-Cube 실험 아키텍처와 단계별 데이터 흐름. 입력과 고정 backbone, 세 실험 요인의 적용 위치, generation artifact, 품질·언어 평가와 분석 흐름을 나타낸다.

## 3.3 상세설계

HyDE ON 조건의 검색 표현은 두 단계로 구성된다. 먼저 한국어 질문을 영어 질의로 변환하고, 이어서 해당 질문에 답할 법한 영어 hypothetical document를 생성한다. hypothetical document generation은 temperature 0.1, top-p 0.9, 최대 512 token의 sampling을 사용한다. 생성된 hypothetical document는 dense retrieval의 검색 표현이며 최종 answer context에는 포함하지 않는다.

Dense retrieval과 BM25는 각각 최대 8개 후보를 반환한다. Weighted RRF는 dense rank에 0.6, BM25 rank에 0.4를 적용한다. CrossEncoder는 fusion 후보를 원질의와 함께 입력받아 다시 정렬한다. Context construction은 상위 후보의 위치를 조정한 뒤 다섯 passage를 선택한다. 전체 configuration에서 retrieval pool, rerank top-N, context passage 수를 고정한다.

CAD는 동일 generation prefix에 대해 context가 포함된 branch와 context가 없는 branch를 계산한다. α=0.5를 사용하여 \(z_{CAD}=1.5z_{ctx}-0.5z_{noctx}\) 형태의 score를 구성한다. SCD는 reference_scd 설정으로 α=1.1, β=0.9, Tstart=5를 사용한다. CAD와 SCD를 함께 사용하는 condition에서는 CAD score가 먼저 계산되고 SCD coefficient가 뒤에 적용된다.

**[표 3-3] 실험 요인별 적용 위치와 비교 단위**

| 요인 | 적용 위치 | Primary comparison | 비교 단위 | 핵심 직접 지표 |
|---|---|---|---:|---|
| HyDE | Dense retrieval 이전 | H1C0S0 ↔ H0C0S0 | 19쌍 | RAGAS 4지표 |
| CAD | Token generation | H0C1S0 ↔ H0C0S0 | 19쌍 | Faithfulness, answer relevancy |
| SCD | Token generation | 동일 query·H·C의 S1 ↔ S0 | 76쌍 | Korean-character ratio |
| SCD symmetric | 평가 입력 정규화 후 | H0의 동일 문맥 S1 ↔ S0 | 38쌍 | Faithfulness, answer relevancy |

HyDE primary comparison은 CAD와 SCD를 모두 OFF로 고정한 19쌍을 사용한다. 이 비교는 HyDE pipeline이 retrieval과 최종 answer quality에 미치는 end-to-end 차이를 본다. 전체 RAG-Cube에서는 CAD×SCD 네 strata의 HyDE ON−OFF 평균도 함께 계산하여 조합별 방향성을 확인한다.

CAD primary comparison은 HyDE OFF·SCD OFF에서 검색 문맥이 byte 단위로 동일한 19쌍을 사용한다. 이 19쌍은 CAD의 generation-side 변화를 해석하는 통제 비교이다. HyDE ON의 CAD 조합은 RAG-Cube configuration 수준의 기술적 패턴으로 제시한다.

SCD 언어 분석은 HyDE와 CAD의 상태를 동일하게 맞춘 76개 대응쌍을 사용한다. 네 H×C strata마다 19개 SCD on/off pair가 존재한다. 추가로 HyDE OFF 38쌍은 저장된 context가 동일하여 retrieval change의 영향을 제거한 상태에서 SCD의 언어 차이를 확인할 수 있다.

---

# 4. 프로그램 구현

## 4.1 시스템 환경

실험 프로그램은 Python을 중심으로 구성되며 PyTorch와 Transformers를 이용하여 embedding, reranking, generation model, logits processor를 실행한다. Transformers는 4.45.2, sentence-transformers는 2.7.0을 사용하며 generation model은 K-intelligence/Midm-2.0-Base-Instruct이다[20]. 품질 평가는 RAGAS 0.2.15 계열과 외부 judge model을 사용하고 answer relevancy의 embedding은 로컬 BGE-M3를 사용한다.

본 생성은 Alice Cloud G-NAHP-80 환경에서 실행한다. generation artifact의 152개 record는 해당 실행 환경을 기록하고 있으며 GPU, CPU, RAM 구성과 표본별 실행 시간도 보존한다.

**[표 4-1] 실험 실행 환경**

| 항목 | 실험 환경 |
|---|---|
| 본 생성 실행 위치 | Alice Cloud G-NAHP-80 |
| GPU | NVIDIA A100 80GB PCIe 1개 |
| CPU | 16 vCore |
| RAM | 192 GiB |
| 실행 관측 최대 GPU 메모리 | 34,800 MiB |
| 최대 GPU utilization | 96% |
| 구현 언어 | Python |
| 주요 라이브러리 | PyTorch, Transformers 4.45.2, sentence-transformers 2.7.0 |
| 생성 모델 | K-intelligence/Midm-2.0-Base-Instruct |
| 품질 평가 | RAGAS 0.2.15, 외부 judge, 로컬 BGE-M3 embedding |
| 연구 자료 형식 | SQLite, JSONL, JSON, CSV |

Mi:dm 2.0 Base Instruct의 파라미터는 고정하고 추론 실험을 수행한다. 따라서 실험 자원은 모델 학습보다 검색, hypothetical document generation, context construction, token generation, CAD branch 계산, SCD processing에 사용된다.

**[표 4-2] 고정 Paper-RAG backbone 설정**

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
| CAD | α=0.5 |
| SCD | reference_scd, α=1.1, β=0.9, Tstart=5 |
| CAD+SCD order | CAD → SCD |

최종 152개 generation record의 wall-clock 실행 구간은 2026-07-08 07:23:49부터 09:17:04 KST까지이며 경과 시간은 1시간 53분 14.7초이다. 각 record에 기록된 duration 합계는 6,888.611초, 평균은 45.320초, 중앙값은 30.556초이다. 최소 duration은 3.975초, 최대 duration은 164.153초이다.

Configuration별 평균 시간은 CAD 적용 여부에 따라 뚜렷하게 달라진다.

**[표 4-3] 조건별 평균 생성 시간**

| HyDE | CAD | SCD | n | 평균 시간(초) |
|---|---|---|---:|---:|
| OFF | OFF | OFF | 19 | 24.6 |
| OFF | ON | OFF | 19 | 63.9 |
| OFF | OFF | ON | 19 | 18.8 |
| OFF | ON | ON | 19 | 56.8 |
| ON | OFF | OFF | 19 | 24.5 |
| ON | ON | OFF | 19 | 79.0 |
| ON | OFF | ON | 19 | 25.0 |
| ON | ON | ON | 19 | 69.9 |

동일 HyDE·SCD 조건에서 CAD를 켠 configuration의 평균 시간은 CAD OFF보다 각각 약 2.60배, 3.02배, 3.22배, 2.80배이다. CAD가 token generation마다 context/no-context branch를 함께 계산하는 구조와 일치하는 방향이다. 실제 duration은 답변 길이와 질의별 처리시간의 영향도 받기 때문에 이 비율은 실험 조건에서 관찰된 실행비용으로 해석한다.

## 4.2 시스템 구성

실험 프로그램은 입력 데이터, 검색 모듈, 생성 모듈, 실행기, artifact 저장, 평가·분석 모듈로 구성된다. 입력 데이터에는 query split, source paper chunks, configuration, fixed parameter가 포함된다. 실행기는 query ID와 target paper를 읽고 configuration을 순회하며 동일 질의-문서 쌍에 여덟 조건을 적용한다.

검색 모듈의 QueryExpander는 HyDE 조건을 처리한다. HyDE OFF에서는 원질의를 dense retriever로 전달하고, HyDE ON에서는 translated query와 hypothetical document를 생성하여 dense 검색 입력을 만든다. BGE-M3와 BM25는 각각 후보를 반환하며 fusion module이 weighted RRF를 계산한다. CrossEncoder와 ContextCompressor는 후보의 순서와 생성 입력 길이를 조정한다.

생성 모듈은 Mi:dm 2.0 Base Instruct와 CAD·SCD logits processor로 구성된다. CAD ON에서는 no-context branch를 함께 계산하여 CAD score를 만들고, SCD ON에서는 token partition에 따라 raw score를 조정한다. 생성은 deterministic greedy 방식으로 진행되어 동일한 저장 입력과 model state에서 sampling variability를 제한한다.

[그림 삽입: `figures/fig05_paper_rag_pipeline.svg`]

**[그림 4-1]** 고정 Paper-RAG backbone과 실험 요인의 적용 위치. HyDE는 dense retrieval 입력, CAD와 SCD는 Mi:dm token generation 단계에 적용된다. BM25와 CrossEncoder에는 원질의를 사용한다.

Generation artifact는 평가와 분리된 source of truth 역할을 한다. RAGAS evaluator는 generation JSONL과 reference 정보를 읽어 네 품질 지표를 계산하고, language analyzer는 생성 답변의 Korean-character ratio와 matched-pair delta를 계산한다. Symmetric input builder는 HyDE OFF의 identical-context pair를 영어와 한국어 panel로 구성하며 judge별 scoring result는 독립 파일로 보존한다.

[그림 삽입: `figures/fig06_artifact_flow.svg`]

**[그림 4-2]** 생성 artifact와 평가·분석 자료의 연결 구조. 최종 generation JSONL을 중심으로 RAGAS, language analysis, symmetric evaluation, 표·그림 생성이 분리된 후속 단계로 연결된다.

## 4.3 시스템 구현

주실험 실행기는 19개 query-document pair와 8개 configuration을 순회한다. 각 iteration은 대상 문서의 chunk collection을 선택하고, HyDE 상태에 따라 검색 표현을 구성한 뒤 retrieval, fusion, reranking, context construction, generation을 수행한다. 실행 결과는 한 record 단위로 저장한다. 152개 generation record는 모두 succeeded 상태이며 generation model field는 K-intelligence/Midm-2.0-Base-Instruct로 일치한다.

HyDE record는 원질의 외에 translated query, hypothetical document, HyDE generation setting, hyde_used 상태를 저장한다. Retrieval trace는 dense·sparse·fusion 결과 수, retrieved chunk ID, reranked chunk ID와 실제 context를 포함한다. 이를 통해 E04와 같은 사례에서 HyDE ON/OFF가 실제로 검색 결과를 변경하는지 answer만 보고 추정하지 않고 저장 ID로 확인할 수 있다.

CAD와 SCD record는 해당 processor의 활성 상태와 파라미터를 저장한다. CAD는 α=0.5, SCD는 reference_scd identifier, α=1.1, β=0.9, Tstart=5 및 vocabulary partition 정보를 보존한다. 두 processor가 함께 동작하는 condition에서는 CAD → SCD 순서를 metadata와 implementation에서 동일하게 유지한다.

**[표 4-4] 생성 record의 주요 저장 필드**

| 범주 | 주요 필드 | 용도 |
|---|---|---|
| 실험 식별 | query_id, config, paper | 질의·문서·조건 추적 |
| 검색 표현 | original query, translated query, hypothetical document | HyDE 경로 확인 |
| 검색 결과 | retrieved IDs, reranked IDs, contexts | retrieval 변화·동일성 확인 |
| 생성 | answer, generation model, decoding setting | 실제 출력 및 모델 확인 |
| CAD/SCD | use_cad, use_scd, α, β, Tstart, processor order | decoding 조건 확인 |
| 실행 | status, start time, duration, alice_mode | 성공 상태·시간·환경 확인 |
| 평가 연결 | record key, reference | RAGAS·언어 분석과 연결 |

품질 평가는 generation 완료 후 별도 단계에서 수행한다. Official quality evaluation은 152개 record를 대상으로 faithfulness 0.8376, answer relevancy 0.7639, context precision 0.8229, context recall 0.9145의 전체 평균을 기록한다. 이 전체 평균은 실험 corpus의 전반적인 score profile을 나타내며 요인별 효과는 paired comparison과 configuration-level analysis를 통해 별도로 해석한다.

언어 분석은 generation answer만을 읽어 Korean-character ratio를 계산한다. 전체 152개 답변의 ratio 분포는 최소 0.0, 중앙값 0.7099, 최대 1.0이며 0.5 미만의 답변은 38개이다. SCD effect 분석은 이 전체 분포를 다시 SCD ON/OFF matched pair로 구성하여 76개 delta를 계산한다.

본문 수치의 재검증은 저장 artifact를 읽는 verifier를 이용한다. 검증 항목은 19개 질의, 8개 configuration, 152개 generation, primary HyDE/CAD pair, SCD 76 pair, symmetric 38 pair, metric mean, confidence interval, win/loss/tie를 포함한다. 그림 생성은 동일 artifact에서 파생한 CSV/JSON을 사용하여 본문 수치와 시각자료의 재현성을 유지한다.

---

# 5. 실험

## 5.1 실험 대상과 구성

실험 대상은 네 개 영어 학술·기술 문서와 각 문서의 내용을 묻는 19개 한국어 질의-대상문서 쌍이다. RAG Survey 질의는 RAG의 기본 구조, Naive RAG, retrieval·generation·augmentation, 평가 방법 등을 포함한다. CAD 문서 질의는 CAD의 생성 원리와 summarization·knowledge conflict 결과를 포함한다. RAPTOR 질의는 tree construction과 QA benchmark 결과를 다루며, Mi:dm K 2.5 Pro Technical Report 질의는 모델 규모, context window, post-training, benchmark 결과와 같은 기술 내용을 포함한다.

**[표 5-1] 실험 대상 문서와 질의-대상문서 쌍 구성**

| 대상 문서 | 질의 수 | 주요 질의 내용 |
|---|---:|---|
| RAG Survey | 5 | RAG 구조, Naive RAG, 지식 집약 작업, 평가 |
| CAD | 4 | CAD 원리, summarization, hallucination, knowledge conflict |
| RAPTOR | 4 | tree construction, QuALITY, QA 결과 |
| Mi:dm K 2.5 Pro Technical Report | 6 | 모델 규모, benchmark, context, post-training |
| **합계** | **19** | |

각 질의-문서 쌍은 여덟 configuration에서 반복되므로 generation 수는 \(19\times8=152\)이다. 이 구조에서 query와 target paper는 대응쌍 전체에서 유지되고 HyDE·CAD·SCD 적용 상태만 변경된다.

HyDE primary comparison은 H1C0S0과 H0C0S0의 19쌍이다. CAD primary comparison은 H0C1S0과 H0C0S0의 19쌍이며 19쌍 모두 저장 검색 문맥이 동일하다. SCD language comparison은 H와 C 상태를 동일하게 맞춘 S1/S0 76쌍이다. Symmetric quality evaluation은 H0에 속하는 38개 동일 문맥 S1/S0 pair를 사용한다.

[그림 삽입: `figures/fig07_evaluation_design.svg`]

**[그림 5-1]** 실험 요인별 비교 및 평가 설계. HyDE와 CAD는 각각 19개 primary pair, SCD 언어 분석은 76개 pair, SCD symmetric quality는 38개 identical-context pair를 사용한다.

부록 A에는 19개의 query ID, target paper, 실제 한국어 질문을 전체 목록으로 제시한다. 이를 통해 본문의 문서별 개수뿐 아니라 실제 평가 질문의 범위를 확인할 수 있게 한다.

## 5.2 평가 및 분석 방법

HyDE와 CAD의 품질 비교는 RAGAS 네 지표를 모두 제시한다. Pair \(i\)에서 on score를 \(s_i^{on}\), off score를 \(s_i^{off}\)라고 하면 paired delta는 다음과 같다.
한컴 한글 수식 입력기 입력값:
```text
Delta_i = s_i^on - s_i^off
```

평균 효과는 19개 Δ_i의 평균으로 계산한다. Bootstrap은 query ID를 sampling unit으로 하여 200,000회 paired percentile resampling을 수행하고 평균 delta의 95% confidence interval을 구한다. Practical band는 +0.01과 −0.01을 사용하여 +0.01 초과를 win, −0.01 미만을 loss, 나머지를 tie로 분류한다.

HyDE primary contrast는 CAD와 SCD를 OFF로 고정하여 retrieval-side intervention을 분석한다. HyDE는 실제 검색 문맥을 바꿀 수 있으므로 context precision과 context recall의 변화 역시 결과의 일부이다. 전체 RAG-Cube에서는 같은 C/S 상태끼리 H1−H0의 configuration mean difference를 계산하여 조합별 방향성을 기술한다.

CAD primary contrast는 H0/S0에서 C1−C0을 비교한다. 이 19쌍은 context, retrieved ID, reranked ID의 동일성을 확인한다. 따라서 CAD는 generation-side quality를 중심으로 해석한다. 동일 context에서 나타나는 context precision·recall의 작은 score 차이는 평가 변동과 함께 기술하고, H1의 CAD 조합 차이는 RAG-Cube configuration 수준의 패턴으로 제시한다.

SCD direct language metric은 다음과 같이 계산한다.
한컴 한글 수식 입력기 입력값:
```text
KoreanRatio = {N_Hangul} over {N_Hangul + N_ASCII}
```

한글과 ASCII 영문자의 합이 0인 출력은 분석 규칙에 따라 0으로 처리한다. 76개 matched pair에서 SCD ON−OFF ratio delta를 계산하며 +0.02 초과를 increase, −0.02 미만을 decrease, 나머지를 tie로 구분한다. KoreanRatio < 0.5를 language drift로 정의하고 threshold crossing을 계산한다.

Symmetric quality evaluation은 H0의 38개 identical-context pair를 대상으로 한다. Answer와 필요한 평가 입력을 영어와 한국어 panel로 정규화하고, gpt-4o와 gpt-4.1-2025-04-14에서 faithfulness와 answer relevancy를 평가한다. 전체 38쌍뿐 아니라 CAD OFF 19쌍과 CAD ON 19쌍도 별도로 계산한다. Bootstrap은 19 query cluster를 sampling unit으로 10,000회 수행한다.

RAG-Cube 8개 configuration의 평균 score table은 전체 조합의 상대적 위치를 보여주는 기술통계로 사용한다. 이 표는 configuration별 quality profile과 trade-off를 관찰하는 데 목적이 있으며, 특히 SCD의 content-quality causal effect는 5.7의 symmetric evaluation을 기준으로 해석한다.

## 5.3 RAG-Cube 조합별 결과

152개 generation의 official quality evaluation에서 전체 평균은 faithfulness 0.8376, answer relevancy 0.7639, context precision 0.8229, context recall 0.9145이다. 전체 평균만으로는 configuration의 차이를 알기 어렵기 때문에 여덟 조건을 분리하여 비교한다.

**[표 5-2] RAG-Cube 여덟 조건의 평균 RAGAS 품질 지표**

| H | C | S | Faithfulness | Answer relevancy | Context precision | Context recall |
|---|---|---|---:|---:|---:|---:|
| 0 | 0 | 0 | 0.8159 | 0.8201 | 0.8343 | **1.0000** |
| 0 | 1 | 0 | 0.8181 | 0.7485 | 0.8321 | 0.9474 |
| 0 | 0 | 1 | 0.7906 | 0.7758 | **0.8512** | 0.9474 |
| 0 | 1 | 1 | 0.7792 | 0.6556 | 0.8446 | 0.7895 |
| 1 | 0 | 0 | 0.8892 | **0.8504** | 0.7664 | 0.9474 |
| 1 | 1 | 0 | **0.9230** | 0.7507 | 0.7988 | 0.8947 |
| 1 | 0 | 1 | 0.8171 | 0.7614 | 0.8135 | 0.8947 |
| 1 | 1 | 1 | 0.8674 | 0.7483 | 0.8422 | 0.8947 |

표 5-2에서 가장 먼저 확인되는 특징은 지표별 최고 configuration이 서로 다르다는 점이다. Faithfulness는 H1C1S0에서 0.9230으로 가장 높다. Answer relevancy는 H1C0S0에서 0.8504로 가장 높다. Context precision은 H0C0S1에서 0.8512, context recall은 H0C0S0에서 1.0000으로 가장 높다. 따라서 RAG-Cube의 최고 configuration은 평가 지표별로 서로 다르게 나타난다.

Faithfulness의 상위 configuration은 HyDE ON 조건에 집중되어 있다. H1C1S0이 0.9230, H1C0S0이 0.8892, H1C1S1이 0.8674이다. 특히 H1C1S0은 H1C0S0보다 faithfulness가 0.0338 높지만 answer relevancy는 0.0997 낮다. 이 비교는 근거 충실도와 질문 직접성 사이의 trade-off 가능성을 보여준다.

Answer relevancy는 H1C0S0이 0.8504로 가장 높으며 H0C0S0이 0.8201로 뒤를 잇는다. H1C1S0은 faithfulness 최고값을 보이지만 answer relevancy는 0.7507이다. 따라서 faithfulness 최고 configuration과 answer relevancy 최고 configuration은 서로 다르다.

Context precision은 SCD ON configuration에서 비교적 높은 값이 나타난다. SCD는 generation 단계의 요인이므로 이 값은 5.3의 configuration-level 기술통계로 제시하고, SCD의 직접 효과는 5.6의 language-adherence analysis와 5.7의 symmetric quality analysis를 기준으로 해석한다.

Context recall은 baseline H0C0S0에서 1.0000으로 가장 높고 H0C1S0, H0C0S1, H1C0S0에서 0.9474이다. Recall의 최고점은 baseline에 위치하며 조합별 변화 폭은 다른 지표보다 제한적이다. 특히 recall은 다른 metric에 비해 동일값과 tie가 많이 발생하기 때문에 평균 차이와 pair distribution을 함께 확인한다.

[그림 삽입: `figures/fig08_rag_cube_quality_matrix.svg`]

**[그림 5-2]** RAG-Cube 여덟 조건의 품질 지표 비교. 각 cell에 실제 평균값을 표시하고 각 지표의 최고 configuration을 강조한다. 이 그림은 조합별 quality profile을 위한 기술적 비교이다.

이 결과는 RAG-Cube의 의미를 개별 기법의 단순 on/off 합계보다 조합별 trade-off 분석에서 찾을 수 있음을 보여준다. HyDE가 포함된 configuration은 faithfulness에서 강한 패턴을 보이고, CAD는 HyDE 조합에서 faithfulness와 context precision을 더 높이는 경우가 있으며, SCD는 content-quality table보다 직접 언어 지표에서 일관된 효과를 보인다. 이후 절에서는 각 요인의 primary controlled result와 configuration-level pattern을 분리하여 분석한다.

## 5.4 HyDE 결과 및 해석

HyDE의 primary comparison은 H1C0S0−H0C0S0 19쌍이다. CAD와 SCD를 모두 OFF로 유지하므로 검색 표현을 HyDE pipeline으로 변경했을 때의 end-to-end 차이를 본다.

**[표 5-3] HyDE 통제 비교 결과(CAD OFF, SCD OFF, n=19)**

| 지표 | 평균 차이(ON−OFF) | 95% CI | Win/Loss/Tie |
|---|---:|---:|---:|
| Faithfulness | +0.0734 | [−0.0248, +0.1777] | 9/6/4 |
| Answer relevancy | +0.0303 | [+0.0016, +0.0615] | 9/3/7 |
| Context precision | −0.0679 | [−0.1702, +0.0194] | 7/6/6 |
| Context recall | −0.0526 | [−0.1579, 0.0000] | 0/1/18 |

Answer relevancy는 평균 +0.0303이고 95% confidence interval 전체가 0보다 크다. 19개 질의 가운데 9개가 +0.01을 초과하는 증가, 3개가 −0.01 미만의 감소, 7개가 practical tie이다. 효과의 크기는 크지 않지만 HyDE primary contrast에서 가장 일관된 양의 결과이다. 이 결과는 본 실험 조건에서 HyDE pipeline이 최종 답변을 질문과 더 직접적으로 연결하는 방향으로 작동한 질의가 감소 질의보다 많다는 점을 보여준다.

Faithfulness의 평균 차이는 +0.0734로 네 지표 가운데 절대 평균 변화가 가장 크다. 9개 질의에서 증가하고 6개에서 감소하며 4개는 tie이다. Confidence interval은 0을 포함하므로 19개 질의 전체에서 하나의 고정된 평균 효과를 확정하는 것보다 질의별 이질성이 존재하는 양의 패턴으로 해석한다. 일부 질의에서는 HyDE에 의해 달라진 검색 근거가 답변의 근거 충실도와 강하게 연결되고, 다른 질의에서는 반대 방향의 변화도 함께 나타난다.

Context precision은 평균 −0.0679이지만 win/loss/tie가 7/6/6으로 세 범주에 분산된다. Answer relevancy가 양의 결과를 보인 반면 검색 문맥 전체의 precision은 혼재된 방향을 보인다. 따라서 HyDE의 answer-level 이점은 retrieval precision의 일괄 상승보다 질의별 검색 근거 구성의 변화와 함께 해석하는 것이 적절하다. HyDE는 검색 후보 구성을 바꾸고 그 가운데 생성에 유리한 근거를 포함할 수 있지만, 동시에 관련도가 낮은 문맥이 포함되는 질의도 존재한다.

Context recall의 평균은 −0.0526이지만 practical distribution은 0 win, 1 loss, 18 tie이다. 즉 19개 중 18개에서 ±0.01을 넘는 변화가 없다. 평균값만 보면 음의 방향처럼 보이지만 pair-level distribution에서는 대부분 질의의 recall이 실질적으로 유지된다. 따라서 HyDE가 전반적인 recall을 낮춘다고 해석하기보다, 본 19쌍에서 recall 변화가 대부분 제한적이고 한 질의의 감소가 평균에 반영된 구조로 보는 것이 적절하다.

전체 RAG-Cube에서 HyDE 상태만 맞춰 76개 대응쌍을 기술적으로 집계하면 faithfulness 평균 차이는 +0.0732이며 40 win, 24 loss, 12 tie이다. Answer relevancy는 +0.0277, 27 win, 19 loss, 30 tie이다. Context precision은 −0.0353, context recall은 −0.0132이며 recall은 65개 pair가 tie이다. Primary contrast뿐 아니라 전체 configuration에서도 answer-level 두 지표가 양의 방향을 유지한다.

조합별 평균을 보면 HyDE ON−OFF faithfulness difference는 C0S0 +0.0733, C1S0 +0.1049, C0S1 +0.0265, C1S1 +0.0882로 네 strata 모두 양수이다. Answer relevancy는 각각 +0.0303, +0.0022, −0.0144, +0.0927로 네 strata 중 세 곳에서 양수이다. 특히 C1S1에서는 faithfulness +0.0882와 answer relevancy +0.0927이 함께 나타난다.

반면 HyDE의 context precision 차이는 네 strata 모두 음의 방향이며 C1S1에서는 −0.0024로 거의 동일하다. Context recall은 C1S1에서 +0.1052, 나머지 세 strata에서는 약 −0.0526~−0.0527이다. 따라서 HyDE configuration pattern은 모든 retrieval metric을 일괄적으로 높이는 형태가 아니라 answer-level quality와 context metric이 서로 다른 방향으로 움직이는 복합적인 결과이다.

[그림 삽입: `figures/fig09_hyde_cad_controlled_forest.svg`]

**[그림 5-3]** HyDE와 CAD 통제 비교의 대응 평균 차이와 95% 신뢰구간.

[그림 삽입: `figures/fig10_hyde_cad_strata_matrix.svg`]

**[그림 5-4]** HyDE와 CAD의 조합 조건별 평균 품질 변화. HyDE panel은 각 C×S stratum의 H1−H0, CAD panel은 각 H×S stratum의 C1−C0 configuration mean difference를 표시한다. 이 그림은 조합별 기술 패턴을 나타내며 interaction 분석의 후속 가설을 제공한다.

HyDE가 실제 retrieval-side intervention이라는 점은 저장 artifact에서도 확인된다. 대표 사례인 track1_0010에서는 HyDE ON/OFF 사이의 retrieved ID, reranked ID, context가 모두 달라지고 answer relevancy도 0.7472에서 0.9286으로 높아진다. 이 사례는 가장 큰 answer-relevancy 차이를 보이는 retrieval-change 사례로 선택된 것이므로 평균적인 HyDE 사례를 대표하는 예시가 아니라, HyDE가 검색 표현과 검색 결과를 실제로 바꾸는 과정을 보여주는 증빙으로 사용한다.

HyDE 결과를 종합하면 가장 강한 controlled evidence는 answer relevancy의 양의 차이이다. Faithfulness는 primary contrast와 full matrix 모두 양의 방향을 반복적으로 보이지만 질의별 변동도 크다. Context precision과 recall은 answer-level metric과 분리된 방향을 보인다. 따라서 본 설정에서 HyDE의 장점은 검색 품질 전반을 일률적으로 높이는 것으로 단순화하기보다 검색 표현을 바꾸어 일부 질의의 최종 답변 관련성과 근거 충실도를 높이는 방향으로 해석한다.

## 5.5 CAD 결과 및 해석

CAD의 primary comparison은 H0C1S0−H0C0S0의 19쌍이다. 두 configuration은 HyDE와 SCD를 OFF로 고정하고 저장된 context, retrieved ID, reranked ID가 동일하다. 따라서 이 비교는 CAD의 generation-side 차이를 가장 직접적으로 관찰하는 조건이다.

**[표 5-4] CAD 동일 문맥 통제 비교 결과(HyDE OFF, SCD OFF, n=19)**

| 지표 | 평균 차이(ON−OFF) | 95% CI | Win/Loss/Tie |
|---|---:|---:|---:|
| Faithfulness | +0.0023 | [−0.0903, +0.0952] | 7/9/3 |
| Answer relevancy | −0.0715 | [−0.1792, +0.0004] | 5/12/2 |
| Context precision | −0.0022 | [−0.0447, +0.0322] | 2/1/16 |
| Context recall | −0.0526 | [−0.1579, 0.0000] | 0/1/18 |

Faithfulness 평균 차이는 +0.0023으로 0 부근에 위치하고 7 win, 9 loss, 3 tie이다. Confidence interval은 −0.0903부터 +0.0952까지 양쪽을 포함한다. 동일 검색 근거를 사용한 19쌍에서는 질의별 증가와 감소가 함께 나타나는 혼재된 분포를 보인다.

Answer relevancy는 평균 −0.0715이고 5 win, 12 loss, 2 tie이다. Confidence interval 상한은 +0.0004로 0에 매우 가깝다. 본 통제 조건에서는 CAD ON에서 질문 직접성이 낮아지는 질의가 증가하는 질의보다 많다. 다만 interval이 0을 포함하므로 이 결과는 본 표본에서 관찰된 감소 방향의 신호로 해석한다.

Context precision과 context recall은 각각 16/19, 18/19가 practical tie이다. CAD primary pair의 실제 저장 context가 동일하므로 두 context metric은 통제 조건이 유지되는지 확인하는 보조 지표로 사용하고, CAD의 핵심 품질 해석은 faithfulness와 answer relevancy를 중심으로 한다.

Primary contrast는 CAD의 평균 효과가 0 부근에서 질의별로 혼재하는 모습을 보인다. RAG-Cube 전체 configuration에서는 HyDE와 SCD 상태에 따라 다른 조합 패턴이 나타난다. 76개 CAD-matched pair의 기술적 평균은 faithfulness +0.0187, context precision +0.0131, answer relevancy −0.0762, context recall −0.0658이다. Faithfulness는 31 win, 27 loss, 18 tie이며 context precision은 14 win, 9 loss, 53 tie이다.

Configuration mean difference를 H×S strata별로 계산하면 H0S0에서는 faithfulness +0.0022, answer relevancy −0.0716, context precision −0.0022이다. H0S1에서는 faithfulness −0.0114, answer relevancy −0.1202, context precision −0.0066이다. 반면 HyDE ON인 H1S0에서는 faithfulness +0.0338과 context precision +0.0324가 함께 양수이며 answer relevancy는 −0.0997이다. H1S1에서는 faithfulness +0.0503, context precision +0.0287, answer relevancy −0.0131, context recall 0.0000이다.

이 패턴은 CAD를 하나의 성공·실패로 요약하기보다 조건 의존적 trade-off로 해석할 필요가 있음을 보여준다. HyDE ON의 두 strata에서는 CAD가 포함된 configuration의 faithfulness와 context precision이 모두 높다. 특히 H1C1S0은 faithfulness 0.9230으로 전체 여덟 configuration 가운데 가장 높은 값을 보인다. 반면 같은 H1S0에서 answer relevancy는 H1C0S0의 0.8504에서 H1C1S0의 0.7507로 낮아진다.

H1S1에서는 CAD 추가 후 faithfulness와 context precision이 높아지면서 answer relevancy 차이는 −0.0131로 작아진다. 이 조합은 CAD의 긍정적 품질 패턴과 answer-relevance cost가 조건에 따라 크기가 달라질 수 있음을 보여준다. HyDE ON에서는 hypothetical document가 configuration별 검색 결과에 영향을 줄 수 있다. 따라서 H1 strata의 결과는 RAG-Cube configuration에서 관찰된 조합별 패턴으로 제시하고, CAD의 generation-side 통제 해석은 H0/S0 primary comparison을 기준으로 한다.

CAD의 또 다른 trade-off는 실행 시간이다. H0S0에서는 CAD OFF 24.6초에서 CAD ON 63.9초, H0S1에서는 18.8초에서 56.8초, H1S0에서는 24.5초에서 79.0초, H1S1에서는 25.0초에서 69.9초로 평균 시간이 증가한다. 대응 비율은 약 2.60~3.22배이다. CAD를 실제 configuration에 적용할 때는 faithfulness와 context precision의 조건별 이득뿐 아니라 answer relevancy와 계산비용을 함께 고려해야 한다.

CAD의 실제 입출력 사례도 동일 문맥 통제 구조를 보여주는 데 활용한다. 본문에서는 19개 identical-context pair 중 CAD 적용 후 faithfulness가 증가한 사례와 품질 trade-off가 나타난 사례를 하나씩 선택하여 같은 검색 근거에서 generation output이 어떻게 달라지는지 나란히 제시한다. 이 선택은 평균 효과를 대표한다고 주장하기 위한 것이 아니라 pair-level heterogeneity를 실제 텍스트에서 확인하기 위한 것이다.

## 5.6 SCD 출력 언어 결과 및 해석

SCD의 직접 목표는 한국어 출력 유지이므로 76개 matched pair의 Korean-character ratio를 우선 분석한다. 네 H×C strata 각각에 19개의 SCD ON/OFF pair가 존재한다.

**[표 5-5] SCD 설정별 한국어 문자 비율과 언어 이탈 수**

| HyDE | CAD | SCD | 평균 Korean ratio | Drift(<0.5) |
|---|---|---|---:|---:|
| OFF | OFF | OFF | 0.5088 | 8/19 |
| OFF | ON | OFF | 0.5175 | 8/19 |
| OFF | OFF | ON | 0.7069 | 4/19 |
| OFF | ON | ON | 0.7590 | 3/19 |
| ON | OFF | OFF | 0.6023 | 3/19 |
| ON | ON | OFF | 0.5099 | 7/19 |
| ON | OFF | ON | 0.8035 | 2/19 |
| ON | ON | ON | 0.7501 | 3/19 |

각 H×C stratum에서 SCD ON의 평균 Korean ratio가 SCD OFF보다 높다. H0C0은 +0.1981, H0C1은 +0.2415, H1C0은 +0.2012, H1C1은 +0.2402이다. 네 HyDE×CAD strata 모두에서 평균 delta가 양수라는 점이 특징적이다.

**[표 5-6] SCD 언어 유지 효과의 대응 분석**

| 분석 항목 | 결과 |
|---|---:|
| Matched pairs | 76 |
| 평균 Korean ratio Δ | **+0.2203** |
| Increase (>+0.02) | **68** |
| Decrease (<−0.02) | **3** |
| Tie | 5 |
| Increase 비율 | **89.5%** |
| Drift(<0.5), SCD OFF | 26 |
| Drift(<0.5), SCD ON | 12 |
| Drift 감소율 | **53.8%** |
| 기존 drift 26쌍 중 0.5 이상 회복 | 15 |
| Threshold 0.3 drift pair | 12 |
| 0.3 이상 회복 | 6 |
| SCD OFF ratio≥0.7인 pair | 20 |
| SCD ON에서 0.65 미만으로 하락 | 0 |
| H0 identical-context 38쌍 평균 Δ | **+0.2198** |

전체 76쌍의 평균 delta는 +0.2203이다. 68쌍이 +0.02를 초과하여 증가하고 3쌍만 −0.02 미만으로 감소하며 5쌍은 tie이다. 증가 pair의 비율은 약 89.5%이므로 평균값이 소수의 극단적인 사례에 의해 만들어진 것보다 대부분의 pair가 동일한 방향으로 이동한 결과에 가깝다.

Language drift threshold 0.5를 적용하면 SCD OFF에서 26개였던 drift가 SCD ON에서 12개로 감소한다. 발생 수 기준으로 약 53.8% 감소한다. SCD OFF에서 drift 상태인 26개 pair만 분리하면 평균 Korean ratio는 0.2515에서 0.5639로 이동하고 15개가 0.5 이상으로 crossing한다.

더 강한 drift를 보기 위해 threshold 0.3을 적용하면 SCD OFF에서 12개 pair가 해당하며 평균은 0.0667이다. SCD ON 평균은 0.3843이고 6개가 0.3 이상으로 이동한다. 이미 SCD OFF에서 Korean ratio가 0.7 이상인 20개 pair에서는 SCD ON 후 0.65 미만으로 내려간 사례가 0개이다. 이는 본 표본에서 SCD가 이미 한국어 비율이 높은 출력을 크게 훼손하기보다 drift pair를 끌어올리는 방향이 우세함을 보여준다.

Retrieval change를 제거한 H0 identical-context 38쌍의 평균 delta는 +0.2198이다. 전체 76쌍의 +0.2203과 거의 같은 크기이다. 따라서 Korean ratio의 증가가 HyDE로 인해 검색 문맥이 달라진 경우에만 나타나는 현상으로 보기 어렵고, 동일 검색 근거에서도 SCD decoding이 출력 언어와 직접 연결된다는 해석을 지지한다.

[그림 삽입: `figures/fig11_scd_language_adherence.svg`]

**[그림 5-5]** SCD 적용 전후 Korean-character ratio와 language drift 변화. 76개 matched pair의 slope, 평균 변화 +0.2203, drift 26→12, 네 H×C strata의 평균 delta와 H0 identical-context 38쌍의 +0.2198을 함께 표시한다.

SCD 결과는 본 연구에서 가장 직접적인 목적 지표와 일치한다. Korean-character ratio는 출력 언어 구성을 측정하는 language-adherence 지표로 사용하고, 문법적 자연스러움·질문 적합성·근거 정확성과 관련된 content quality는 다음 절의 symmetric evaluation에서 분석한다.

## 5.7 SCD 대칭 품질 평가 및 해석

SCD 적용에 따른 content-quality 차이를 평가할 때 원래 생성 언어가 서로 다르면 judge가 언어 자체에 영향을 받을 수 있다. 이를 줄이기 위해 H0의 identical-context 38개 pair를 영어와 한국어 두 panel로 정규화하고, 동일 입력 파일을 gpt-4o와 gpt-4.1-2025-04-14 두 judge로 평가한다. 분석 metric은 generation answer를 직접 사용하는 faithfulness와 answer relevancy이다.

**[표 5-7] SCD의 평가 언어·모델별 품질 차이**

| Judge | 평가 언어 | Faithfulness Δ [95% CI] | Answer relevancy Δ [95% CI] |
|---|---|---:|---:|
| gpt-4o | English | +0.0071 [−0.0596, +0.0714] | −0.0910 [−0.1725, −0.0240] |
| gpt-4o | Korean | −0.0283 [−0.1044, +0.0510] | −0.0752 [−0.1501, −0.0138] |
| gpt-4.1-2025-04-14 | English | −0.0579 [−0.1322, +0.0060] | −0.0327 [−0.0851, +0.0129] |
| gpt-4.1-2025-04-14 | Korean | −0.0326 [−0.0997, +0.0226] | −0.0356 [−0.1149, +0.0315] |

Faithfulness는 네 전체 panel 모두 confidence interval이 0을 포함한다. gpt-4o English panel의 평균은 +0.0071이며 18 win, 12 loss, 8 tie이다. 평균 효과를 확정할 수는 없지만 pair-level로는 증가 사례가 감소 사례보다 많다. CAD ON stratum만 보면 gpt-4o English faithfulness는 +0.0432, 10 win, 5 loss, 4 tie로 양의 방향이 더 뚜렷하지만 interval은 여전히 0을 포함한다.

gpt-4o Korean panel의 faithfulness는 −0.0283이고 15 win, 15 loss, 8 tie이다. English panel과 Korean panel의 평균 방향은 서로 다르고 두 interval 모두 0을 포함한다. Faithfulness 결과는 평가 언어에 따른 변동성을 함께 보여준다.

Answer relevancy는 gpt-4o에서 더 뚜렷한 음의 방향을 보인다. English panel은 −0.0910 [−0.1725, −0.0240], Korean panel은 −0.0752 [−0.1501, −0.0138]로 두 interval 모두 0보다 작다. 특히 CAD ON stratum의 gpt-4o English answer relevancy는 −0.1365이고 Korean은 −0.1078로 음의 방향이 강하다. 이 결과만 보면 SCD language control과 answer relevancy 사이에 비용 신호가 관찰된다.

Fixed gpt-4.1-2025-04-14 judge에서는 같은 비교의 confidence interval이 0을 포함하는 범위로 나타난다. English answer relevancy는 −0.0327 [−0.0851, +0.0129], Korean은 −0.0356 [−0.1149, +0.0315]로 0을 포함한다. Korean overall의 raw win/loss는 17/17, tie 4로 거의 균형을 이룬다. English CAD OFF stratum은 평균 +0.0015이며 10 win, 8 loss, 1 tie이지만 interval은 넓게 0을 포함한다.

이 결과는 SCD의 content-quality response가 query, CAD condition, evaluation language, judge model에 따라 이질적임을 보여준다. gpt-4o에서는 answer-relevancy cost signal이 나타나고, gpt-4.1에서는 같은 비교가 zero-crossing interval로 나타난다. Faithfulness 역시 일부 panel에서 양의 평균과 win 우세가 관찰되며 interval 폭은 비교적 넓다. 따라서 content-quality 결과는 judge와 평가 언어에 따른 민감도를 포함하는 분포로 정리한다.

[그림 삽입: `figures/fig12_symmetric_scd_quality.svg`]

**[그림 5-6]** 평가 언어와 평가 모델에 따른 SCD faithfulness·answer relevancy 차이. 각 점은 SCD ON−OFF 평균, 가로선은 query-clustered bootstrap 95% confidence interval이다.

따라서 SCD에 대해 가장 강하게 지지되는 결과는 5.6의 direct language-adherence effect이다. Content-quality 결과는 language control과 별도 축으로 해석하고 judge별 결과를 함께 제시한다. 이 구분은 output-language success와 semantic quality를 서로 다른 평가 차원으로 유지한다.

## 5.8 대표 입출력 사례 분석

정량 결과가 실제 생성 텍스트에서 어떻게 나타나는지 확인하기 위해 저장 artifact의 질의, 검색 근거, 생성 답변을 함께 제시한다. 사례는 보존된 generation record의 질문·근거·답변을 학술용 panel로 재구성한다. 긴 답변과 근거는 핵심 부분을 원문 그대로 표시하고 생략 부분은 명시한다.

**사례 1. 한국어 질의–영어 근거–한국어 응답의 정상 입출력**

RAPTOR 문서를 대상으로 한 track1_0027의 질문은 “RAPTOR가 여러 QA 작업에서 달성한 결과는 무엇인가요?”이다. 저장된 영어 근거는 RAPTOR의 conclusion과 QA benchmark 성능을 포함하고, 생성 답변은 한국어를 중심으로 QASPER, QuALITY, NarrativeQA 결과를 정리한다. 이 사례는 한국어 질문, 영어 근거, 한국어 생성이라는 본 연구의 기본 입출력 구조가 실제 artifact에 어떻게 기록되는지를 보여준다.

[그림 삽입: `figures/fig13_normal_qa_panel.svg`]

**[그림 5-7]** 한국어 질의–영어 근거–한국어 응답의 실제 입출력 사례. 저장된 질문, 검색 근거 일부, 생성 답변 일부와 configuration·Korean ratio·평가값을 함께 표시한다.

**사례 2. SCD OFF에서 관찰되는 언어 이탈**

track1_0009의 질문은 “RAG가 LLM에서 사실적으로 부정확한 콘텐츠 생성을 줄이는 데 어떻게 기여합니까?”이다. SCD OFF 조건 가운데 선택된 언어 이탈 사례는 Korean ratio가 0.0000이며 한국어 질문에 대해 저장 답변의 주된 서술이 영어로 생성된다. 검색 근거도 영어이므로 질문 언어보다 근거 문서 언어가 출력에 강하게 나타난 사례이다. 이 예시는 본 실험의 실제 generation에서 관찰된 language drift를 직접 보여준다.

**사례 3. 동일 검색 문맥에서 SCD 적용에 따른 출력 언어 변화**

track1_0035의 질문은 “Mi:dm K 2.5 Pro 모델은 어떤 한국어 벤치마크에서 최첨단 결과를 달성했습니까?”이다. H0C1S0과 H0C1S1을 비교하면 contexts identical, retrieved IDs identical, reranked IDs identical 조건이 모두 성립한다. SCD OFF의 Korean ratio는 0.0007, SCD ON은 0.7099이며 delta는 +0.7092이다.

두 조건의 검색 근거가 동일하므로 이 사례의 출력 언어 차이를 retrieval change로 설명하기 어렵다. SCD 적용 여부가 generation 단계에서 달라지는 유일한 실험 요인이며, 76개 pair의 평균 +0.2203과 identical-context 38개 pair의 +0.2198이 실제 텍스트에서는 어떤 형태로 나타나는지 보여주는 대표적인 증빙이다. 이 사례는 SCD의 동일 문맥 language-control 현상을 보여주는 정성적 증빙으로 사용한다.

[그림 삽입: `figures/fig14_scd_drift_rescue_panel.svg`]

**[그림 5-8]** SCD 미적용 언어 이탈과 동일 검색 문맥 SCD 적용 사례. E02의 실제 drift와 E03의 matched-context SCD OFF/ON을 두 panel로 구성한다.

**사례 4. HyDE 적용에 따른 retrieval 변화**

track1_0010의 질문은 “RAG의 Naive RAG 방법론은 어떤 과정으로 구성되어 있습니까?”이다. H0C0S0과 H1C0S0 비교에서 contexts identical=False, retrieved IDs identical=False, reranked IDs identical=False가 기록된다. HyDE OFF의 answer relevancy는 0.7472, HyDE ON은 0.9286이며 faithfulness도 0.4167에서 0.9500으로 높아진다. Korean ratio는 0.0143에서 0.7647로 차이가 난다.

HyDE ON record에는 translated query와 hypothetical document가 함께 저장되어 있으며 dense retrieval 결과도 달라진다. 이 사례는 HyDE가 answer decoding만 바꾸는 기법이 아니라 검색 표현을 바꾸어 실제 retrieval provenance와 generation context를 변경하는 요인임을 보여준다. 해당 사례는 HyDE-only pair 중 answer-relevancy 절대 차이가 큰 retrieval-change 사례로 선택되며, HyDE가 검색 표현과 retrieval provenance를 실제로 변경하는 과정을 보여준다.

[그림 삽입: `figures/fig15_hyde_retrieval_change_panel.svg`]

**[그림 5-9]** HyDE 적용에 따른 검색 표현과 검색 결과 변화 사례. HyDE OFF/ON의 검색 입력, changed retrieval IDs, 생성 답변과 품질 점수를 비교한다.

**사례 5. 동일 검색 문맥에서 CAD 적용 후 나타나는 상반된 응답 변화**

CAD의 primary 19쌍은 검색 문맥이 동일하지만 faithfulness와 answer relevancy 변화 방향이 질의마다 다르다. 본문에서는 CAD ON에서 faithfulness가 증가하는 pair 1개와 품질 trade-off가 나타나는 pair 1개를 deterministic criterion으로 선택하여 같은 검색 근거에서 generation output이 어떻게 달라지는지 나란히 제시한다. 두 사례 모두 retrieved ID·reranked ID·context가 동일함을 먼저 표시하고, CAD OFF/ON의 실제 저장 답변과 faithfulness·answer relevancy를 나란히 제시한다.

이 사례 구성은 CAD primary pair의 상반된 질의별 반응을 균형 있게 보여준다. Primary contrast에서 7 win, 9 loss, 3 tie의 faithfulness distribution과 5 win, 12 loss, 2 tie의 answer-relevancy distribution이 실제 텍스트 수준에서도 서로 다른 형태로 나타남을 확인하는 데 있다.

[그림 삽입: `figures/fig16_cad_balanced_cases.svg`]

**[그림 5-10]** 동일 검색 문맥에서 CAD 적용 전후의 상반된 응답 사례. Faithfulness 증가 사례와 품질 trade-off 사례를 함께 제시하며 두 pair의 retrieval identity를 표시한다.

이상의 사례는 정량 결과의 평균, confidence interval, pair distribution을 실제 질문·근거·답변 수준의 현상과 연결한다. HyDE는 retrieval provenance의 변화, CAD는 동일 context에서의 generation variability, SCD는 동일 context에서도 나타나는 output-language change를 각각 직접 확인할 수 있다.

## 5.9 종합 논의

첫째, HyDE 결과에서는 retrieval metric과 answer-level metric의 변화 방향이 분리된다. Primary comparison에서 answer relevancy는 양의 interval을 보이고 faithfulness도 평균과 win count가 양의 방향이다. 반면 context precision은 일관된 상승이 아니며 context recall은 대부분 tie이다. 따라서 HyDE의 효과를 “검색 precision 증가” 하나로 설명하기보다 검색 표현을 변경하면서 최종 답변의 질문 적합성과 근거 충실도에 유리한 근거 구성이 나타나는 일부 질의가 존재한다고 보는 것이 적절하다.

둘째, HyDE의 faithfulness 방향은 전체 조합에서도 반복된다. C0S0, C1S0, C0S1, C1S1 네 strata 모두 H1 configuration의 평균 faithfulness가 H0보다 높다. 특히 C1S0에서 +0.1049, C1S1에서 +0.0882의 차이가 관찰된다. 이 값은 번역과 hypothetical document generation을 함께 포함한 본 연구의 HyDE pipeline 수준에서 해석한다.

셋째, CAD는 가장 복합적인 결과를 보인다. Strict identical-context comparison에서는 faithfulness 평균이 0 부근에서 질의별로 혼재하고 answer relevancy는 감소 방향을 보인다. 반면 HyDE ON configuration에서는 CAD를 포함한 조건의 faithfulness와 context precision이 반복적으로 높다. H1C1S0은 전체 faithfulness 최고 configuration이며 H1S1에서도 CAD 추가 후 faithfulness와 context precision이 함께 높아진다. 이 결과는 CAD가 특정 retrieval context 구성에서 더 유리하게 작동할 가능성을 보여주지만, H1에서 context identity가 고정되지 않기 때문에 정식 interaction effect보다 후속 통제 실험의 가설로 보는 것이 적절하다.

넷째, CAD는 quality metric 사이의 trade-off뿐 아니라 계산비용의 trade-off를 갖는다. Faithfulness와 context precision이 높아지는 H1 strata에서도 answer relevancy는 낮아진다. 또한 CAD ON 평균 생성 시간은 대응 CAD OFF 조건보다 약 2.6~3.2배 길다. 따라서 근거 충실도를 우선하는 상황과 빠른 생성 또는 질문 직접성을 우선하는 상황에서 configuration 선택이 달라질 수 있다.

다섯째, SCD는 세 요인 가운데 직접 목표 지표에서 가장 일관된 결과를 보인다. 76개 matched pair 중 68개에서 Korean ratio가 증가하고 네 H×C strata 모두 양의 평균 delta를 보인다. 동일 retrieval context의 38쌍에서도 전체 평균과 거의 같은 +0.2198이 유지된다. 이는 output-language control이 retrieval change에 의존하지 않고 generation 단계에서 반복적으로 나타나는 결과임을 뒷받침한다.

여섯째, SCD의 language-control result와 content-quality result는 서로 다른 평가 축으로 해석한다. gpt-4o에서는 answer-relevancy 감소 signal이 영어와 한국어 panel에서 나타나고, gpt-4.1에서는 같은 비교의 confidence interval이 0을 가로지른다. Faithfulness도 judge와 evaluation language에 따라 평균 방향이 달라진다. 즉 목표 언어 비율의 증가는 안정적으로 관찰되지만 답변 내용 품질의 변화는 동일한 강도로 일반화하기 어렵다.

일곱째, RAG-Cube 전체 결과는 하나의 절대적인 최적 configuration보다 목적에 따른 configuration 선택의 필요성을 보여준다. Faithfulness 최고 configuration은 H1C1S0, answer relevancy 최고는 H1C0S0, context precision 최고는 H0C0S1, context recall 최고는 H0C0S0이다. 모든 요인을 ON으로 두는 H1C1S1은 일부 지표에서 강한 값을 보이지만 모든 metric의 최고점은 아니다. 따라서 세 기법을 “많이 적용할수록 좋은” 모듈로 보는 것보다 해결하려는 문제에 따라 조합을 선택하는 관점이 더 적절하다.

마지막으로 본 연구의 결과는 평균값과 실제 사례를 함께 볼 필요성을 보여준다. 평균 confidence interval이 0을 포함하는 요인에서도 상당수 질의는 긍정적인 변화를 보이고, 평균이 양수인 요인에서도 감소 질의가 존재한다. 조합 실험에서는 특정 configuration이 하나의 metric을 높이는 동시에 다른 metric을 낮출 수 있다. 따라서 mean delta, interval, win/loss/tie, configuration mean, 실제 질문·근거·답변을 함께 제시하는 것이 본 연구의 결과를 가장 정확하게 설명한다.

## 5.10 연구의 한계

본 연구의 질문 집합은 자연어처리와 언어모델 분야의 네 문서에 대응하는 19개 질의-대상문서 쌍으로 구성된다. Primary HyDE와 CAD contrast의 sampling unit도 각각 19개 query이다. 따라서 confidence interval이 넓은 지표는 질의 수와 질의별 이질성의 영향을 함께 받는다. 다른 학문 분야와 문서 구조를 포함하는 더 큰 질의 집합은 결과의 외적 타당성을 확장할 수 있다.

HyDE ON 조건은 한국어 질의의 영어 번역과 hypothetical document generation을 하나의 검색 확장 pipeline으로 구성한다. 따라서 HyDE ON/OFF 결과는 이 두 단계가 결합된 end-to-end 차이이다. Translation-only condition을 추가하면 언어 변환과 hypothetical document expansion의 기여를 별도로 비교할 수 있다.

HyDE가 적용되는 configuration에서는 hypothetical document에 따라 CAD ON/OFF의 retrieval context가 서로 달라질 수 있다. 본 연구의 CAD primary conclusion은 H0/S0 identical-context 19쌍을 기준으로 하며, H1의 CAD 결과는 조합별 기술 패턴으로 제시한다. 후속 실험에서는 동일 hypothetical document와 동일 retrieval context를 고정한 CAD ON/OFF 반복을 통해 HyDE×CAD 결합 효과를 직접 비교할 수 있다.

RAGAS의 faithfulness와 answer relevancy는 LLM judge의 영향을 받는다. Symmetric evaluation에서도 gpt-4o와 gpt-4.1-2025-04-14의 answer-relevancy confidence interval이 서로 다른 범위를 보인다. 또한 정규화 과정에서 실제 답변 번역이 필요한 비율은 SCD OFF 23/38, SCD ON 11/38로 다르다. 두 judge가 같은 제공자 계열이라는 조건도 존재한다. 독립 제공자의 judge와 한국어·영어 능력을 갖춘 human blind evaluation을 추가하면 content-quality 해석의 독립성을 높일 수 있다.

Korean-character ratio는 한글과 ASCII 영문자의 상대적 비율을 측정하는 직접 언어 지표이다. 본 연구는 이 값을 language adherence에 사용하고, 문법적 자연스러움·의미적 품질·근거 정확성은 symmetric content-quality evaluation으로 다룬다.

최종 실행 기록에서 RAG Survey의 5개 질의×8 configuration, 총 40개 record는 BM25 후보 수가 0이고 나머지 112개 record는 BM25 후보 8개를 반환한다. 본문에서는 이 candidate trace를 그대로 관찰 결과로 제시하며, hybrid retrieval의 실제 기여는 record별 dense·BM25 후보 상태를 기준으로 해석한다.

CrossEncoder는 원래 한국어 질의와 영어 passage를 함께 입력받는다. 본 연구는 해당 reranker를 고정 backbone 조건으로 사용한다. 후속 실험에서는 reranker 비교 또는 번역 질의 reranking 조건을 추가하여 retrieval pipeline 내부의 기여를 더 세분화할 수 있다.

숫자 환각률과 질문 유형별 효과는 각각 전용 human annotation과 더 큰 category별 표본을 필요로 한다. 본 연구의 19개 질의를 세부 유형으로 나누면 각 범주의 sample size가 작아지므로 주요 결론은 전체 query-level paired analysis에 둔다. 이러한 분석은 독립적인 후속 평가 항목으로 확장할 수 있다.

---

# 6. 결론

본 연구는 한국어 질의로 영어 학술·기술 문서를 검색하고 한국어 답변을 생성하는 RAG 환경에서 HyDE, CAD, SCD의 적용 결과를 2×2×2 RAG-Cube 구성으로 분석한다. 네 개 문서에 각각 대응하는 19개의 질의-대상문서 쌍을 여덟 configuration에서 실행하여 152개의 답변을 생성하고, 고정 Paper-RAG backbone에서 retrieval expansion, context-aware generation, output-language control을 구분하여 비교한다. 전체 configuration 결과에서는 하나의 설정이 모든 품질 지표에서 동시에 최고값을 보이지 않는다. H1C1S0은 faithfulness 0.9230으로 가장 높고 H1C0S0은 answer relevancy 0.8504로 가장 높다. HyDE의 primary contrast에서는 answer relevancy가 +0.0303의 양의 차이를 보이고 전체 RAG-Cube에서도 faithfulness가 네 CAD×SCD strata 모두에서 양의 방향을 보인다. CAD는 strict identical-context condition에서 독립적인 평균 향상이 확립되지는 않지만 HyDE ON 조합에서 faithfulness와 context precision이 높아지는 패턴을 보이며 answer relevancy와 계산비용 사이의 trade-off가 함께 나타난다. SCD는 76개 pair에서 Korean ratio를 평균 +0.2203 높이고 68개 pair에서 증가하며 language drift를 26개에서 12개로 줄인다. 동일 검색 문맥 38쌍에서도 +0.2198이 유지되어 output-language control과 직접 연결되는 결과를 보인다.

이 결과는 RAG 기법의 적용 효과를 하나의 공통 점수로 판단하기보다 각 기법의 목적과 조합 조건을 함께 고려할 필요가 있음을 보여준다. HyDE는 질문 관련성과 faithfulness에서 반복적인 양의 패턴을 보이고, CAD는 일부 조합에서 근거 충실도와 문맥 정밀도를 높이는 대신 질문 관련성과 실행시간의 비용을 형성하며, SCD는 가장 안정적인 한국어 출력 유지 효과를 보인다. 향후 연구에서는 질의와 학문 분야를 확대하고, translation-only retrieval condition과 고정 hypothetical document를 이용한 matched-context HyDE×CAD 분석, 독립 judge와 human blind evaluation, 다른 generator와 tokenizer에서의 반복 실험을 통해 조합별 효과의 일반성과 인과 해석을 확장할 수 있다.

---

# 참고문헌

[1] P. Lewis et al., “Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,” *Advances in Neural Information Processing Systems*, Vol. 33, 2020.

[2] Y. Gao et al., “Retrieval-Augmented Generation for Large Language Models: A Survey,” arXiv:2312.10997, 2023.

[3] L. Gao et al., “Precise Zero-Shot Dense Retrieval without Relevance Labels,” *Proceedings of ACL*, pp. 1762–1777, 2023.

[4] W. Shi et al., “Trusting Your Evidence: Hallucinate Less with Context-Aware Decoding,” *Proceedings of NAACL*, pp. 783–791, 2024.

[5] B. Li, Z. Xu, and R. Xie, “Language Drift in Multilingual Retrieval-Augmented Generation: Characterization and Decoding-Time Mitigation,” *Proceedings of AAAI*, Vol. 40, No. 37, pp. 31519–31526, 2026.

[6] J. Chen et al., “M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation,” *Findings of ACL 2024*, pp. 2318–2335, 2024.

[7] S. E. Robertson et al., “Okapi at TREC-3,” *Text REtrieval Conference*, 1994.

[8] G. V. Cormack, C. L. A. Clarke, and S. Büttcher, “Reciprocal Rank Fusion Outperforms Condorcet and Individual Rank Learning Methods,” *Proceedings of SIGIR*, pp. 758–759, 2009.

[9] R. Nogueira and K. Cho, “Passage Re-ranking with BERT,” arXiv:1901.04085, 2019.

[10] P. Bajaj et al., “MS MARCO: A Human Generated Machine Reading Comprehension Dataset,” arXiv:1611.09268, 2016.

[11] N. F. Liu et al., “Lost in the Middle: How Language Models Use Long Contexts,” *Transactions of the Association for Computational Linguistics*, Vol. 12, pp. 157–173, 2024.

[12] X. L. Li et al., “Contrastive Decoding: Open-ended Text Generation as Optimization,” *Proceedings of ACL*, pp. 12286–12312, 2023.

[13] G. Jang et al., “Contrastive CAD: Contrastive Context-Aware Decoding for Mitigating Hallucinations in Large Language Models,” *Proceedings of HCLT-KACL*, 2024.

[14] Y. Kim et al., “Improving Retrieval Performance Using HyDE-Based Multi-Hop Retrieval,” *Information Systems Review*, Vol. 27, No. 2, pp. 127–148, 2025.

[15] S. Es et al., “RAGAs: Automated Evaluation of Retrieval Augmented Generation,” *Proceedings of EACL System Demonstrations*, pp. 150–158, 2024.

[16] B. Kim and J. Yang, “A Comparative Analysis of Automatic Dataset Generation Frameworks for RAG System Performance Evaluation,” *Journal of the Korea Institute of Information and Electronic Communication Technology*, Vol. 18, No. 2, pp. 143–154, 2025.

[17] D. Rau et al., “BERGEN: A Benchmarking Library for Retrieval-Augmented Generation,” *Findings of EMNLP*, pp. 7640–7663, 2024.

[18] OpenAI, “GPT-4o System Card,” 2024.

[19] X. Fu and W. Liu, “How Reliable is Multilingual LLM-as-a-Judge?,” *Findings of EMNLP*, 2025.

[20] D. Shin et al., “Mi:dm 2.0 Korea-centric Bilingual Language Models,” arXiv:2601.09066, 2026.

[21] P. Sarthi et al., “RAPTOR: Recursive Abstractive Processing for Tree-Organized Retrieval,” *International Conference on Learning Representations*, 2024, arXiv:2401.18059.

[22] KT Tech Innovation Group, “Mi:dm K 2.5 Pro Technical Report,” arXiv:2603.18788v2, 2026.

[23] EliceCloud, “Getting Started with Run Box: Choose an Instance Type,” 2026.

---

# 부록

## 부록 A. 19개 질의-대상문서 쌍

`experiments/data/query_splits/decoder_main_queries.json`의 19개 query를 query_id, target paper, 실제 한국어 질문의 세 열로 표 A-1에 정리한다. 본문에 제시한 문서별 5/4/4/6 분포와 일치하도록 자동 생성한다.

## 부록 B. RAG-Cube configuration과 주요 파라미터

표 B-1에는 H/C/S 8개 configuration, 표 B-2에는 retrieval pool, fusion weight, rerank top-N, context 수, generation model, CAD α, SCD α·β·Tstart를 정리한다.

## 부록 C. 추가 입출력 증빙

E01 Normal QA, E05 CAD Identical Context, E06 Low Faithfulness review case의 전체 replay를 논문용 panel과 함께 제시한다. E06은 자동 faithfulness 0.0을 기록한 `low-faithfulness review case`로 표기한다.

## 부록 D. SCD 대칭 평가 입력 및 교차 Judge 검증

E07 symmetric input audit와 E08 cross-judge report를 표 형태로 정리한다. 영어·한국어 panel의 record 수, identical-context pair 수, normalization method, judge, metric, input hash와 결과 hash를 추적 가능하게 제시한다.
