# 교수 피드백 반영 문단 A→B 대조

기준 원고: `d4931ec76f591016b2601561d17fbd37ac2a833a`. 아래는 원고 줄의 정확한 변경 구간이다. 한 구간에 여러 문장이 포함될 수 있으며, 삭제·추가는 각각 표시한다. 최종 전체 문장과 제목의 검토 단위는 `PROSE_SENTENCE_REVIEW.json`에서 추적한다.

## 1. replace · 원고 3–3 → 3–3

A (기준 원고):

```text
한국어 질의–영어 학술·기술 문서 RAG에서의 HyDE·CAD·SCD 조합 실험 [스타일=논문제목]
```

B (최종 원고):

```text
한국어 질의로 영어 학술·기술 문서를 검색하는 RAG에서의 HyDE·CAD·SCD 조합 실험 [스타일=논문제목]
```

## 2. replace · 원고 21–21 → 21–21

A (기준 원고):

```text
검색 증강 생성(Retrieval-Augmented Generation, RAG)은 외부 문서에서 질문과 관련된 내용을 검색하고, 이를 생성 모델에 제공하여 답변을 생성하는 방법이다. 한국어 질문으로 영어 학술 및 기술 문서를 검색하는 과정에서는 질문과 원문의 표현 차이가 검색 결과에 영향을 줄 수 있다. 생성된 답변의 근거 충실도와 한국어 문자 비율은 각각 별도로 측정하였다. 본 연구에서는 Hypothetical Document Embeddings(HyDE), Context-Aware Decoding(CAD), Soft Constrained Decoding(SCD)을 각각 밀집 검색 입력 변경, 검색 문맥을 활용한 로짓 조정, 한국어 출력 제어에 적용하였다. 세 기법의 ON/OFF를 조합하여 RAG-Cube의 8개 실험 조건을 구성하였다.
```

B (최종 원고):

```text
검색 증강 생성(Retrieval-Augmented Generation, RAG)은 질문과 관련된 문서 구간을 검색하고 그 텍스트를 이용해 답변을 생성하는 방법이다. 한국어 질의로 영어 학술·기술 문서를 검색하는 환경에서는 검색 결과의 관련성, 답변이 근거를 반영하는 정도와 출력 언어를 함께 살펴볼 필요가 있다. 본 연구는 가상 문서 임베딩(Hypothetical Document Embeddings, HyDE), 문맥 인식 디코딩(Context-Aware Decoding, CAD), 소프트 제약 디코딩(Soft Constrained Decoding, SCD)을 같은 검색·생성 파이프라인에 적용하여 조합별 결과를 비교하였다.
```

## 3. replace · 원고 23–23 → 23–23

A (기준 원고):

```text
검색 단계에서는 BGE-M3 밀집 검색과 BM25 희소 검색을 사용하고, 두 검색 결과를 weighted Reciprocal Rank Fusion으로 결합한 뒤 CrossEncoder로 재정렬하였다. 답변 생성에는 K-intelligence/Midm-2.0-Base-Instruct를 사용하였다. RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report를 대상으로 각 문서에 대한 한국어 평가 질의를 15개씩 작성하여 총 60개를 구성하였다. 각 질의에 8개 조건을 적용하고 480개의 생성 기록을 저장하였다. HyDE는 CAD와 SCD를 모두 OFF로 고정한 60개 대응쌍에서 비교하였다. CAD는 HyDE와 SCD를 모두 OFF로 고정하고 검색 문맥이 동일한 대응쌍에서 평가하였다. SCD는 HyDE를 OFF로 고정하고 검색 문맥이 동일한 120개 대응쌍을 주 비교로 사용하였으며, HyDE와 CAD의 적용 상태를 각각 맞춘 전체 240개 대응쌍도 분석하였다.
```

B (최종 원고):

```text
영어 문서 4종에서 한국어 질의를 각각 15개씩 구성하였다. 질의 60개 각각에 세 기법의 적용 여부를 조합한 8조건을 적용하여 생성 기록 480개를 수집하였다. BGE-M3와 BM25의 검색 결과를 가중 역순위 융합으로 결합하고 CrossEncoder로 재정렬한 뒤 Mi:dm 2.0 Base Instruct로 답변을 생성하였다. 네 품질 지표는 RAG 자동 평가 프레임워크 RAGAS로 측정하고, 한국어 문자 비율은 생성 답변에서 계산하였다. 질의를 반복측정 단위로 삼아 조건별 평균과 표준편차, 요인별 주효과와 상호작용, 대응 점수 차이를 분석하였다. 품질 평가는 SCD OFF의 영어 문맥과 SCD ON의 한국어 번역 문맥을 구분하였다. 통계 검정에는 양측 유의수준 0.05와 Holm 보정을 적용하였다.
```

## 4. replace · 원고 25–25 → 25–25

A (기준 원고):

```text
HyDE의 답변 관련성 평균 대응 차이는 +0.0805였고, 95% 신뢰구간은 [+0.0110, +0.1514]였다. 근거 충실도, 문맥 정밀도와 문맥 재현율의 평균 대응 차이는 각각 +0.0436, -0.0343, 0.0000이었다. CAD의 근거 충실도 평균 대응 차이는 양쪽 평가값이 있는 58쌍에서 +0.0288이었고, 95% 신뢰구간은 [-0.0367, +0.0934]로 0을 포함하였다. 답변 관련성의 평균 대응 차이는 60쌍에서 -0.0073이었다. SCD의 한국어 문자 비율 평균 대응 차이는 HyDE OFF 동일 문맥 120개 대응쌍에서 +0.2182였고, 95% 신뢰구간은 [+0.1880, +0.2487]였다. 전체 240개 대응쌍에서는 +0.2289였다.
```

B (최종 원고):

```text
CAD와 SCD를 미적용한 HyDE 비교에서 답변 관련성의 평균 대응 점수 차이는 +0.080점이었다. 대응 t-검정은 t(59)=2.236, 보정 전 p=0.029, 네 품질 지표에 대한 보정 후 p=0.117이었다. 같은 검색 문맥에서 CAD를 비교한 근거 충실도 차이는 +0.029점, t(57)=0.862, 보정 전 p=0.393이었다. SCD의 HyDE OFF 동일 문맥 비교에서는 질의별로 두 CAD 상태의 차이를 평균하였다. 한국어 문자 비율의 평균 차이는 +21.8%p였으며, t(59)=13.951, 보정 후 p<0.001이었다. 전체 8조건의 문자 비율 분석에서도 SCD 주효과가 유의하였다. 조건 실행 시간에서는 HyDE와 CAD의 주효과 및 CAD×SCD 상호작용이 보정 후 유의하였다.
```

## 5. insert · 원고 27–26 → 27–27

A (기준 원고):

```text
(해당 없음)
```

B (최종 원고):

```text
세 기법은 서로 다른 처리 단계와 평가 항목에 영향을 주었다. 본 연구는 동일한 질의와 파이프라인에서 답변 품질, 출력 언어와 실행 시간을 구분하고, 단순 비교와 요인 효과를 연결하여 조합별 특성을 제시하였다.
```

## 6. replace · 원고 28–29 → 29–29

A (기준 원고):

```text

주요어: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, 한국어 질의, 영어 학술 및 기술 문서, 언어 이탈
```

B (최종 원고):

```text
주제어: 검색 증강 생성, HyDE, CAD, SCD, 한국어 질의, 영어 문서, 반복측정 실험
```

## 7. replace · 원고 33–33 → 33–33

A (기준 원고):

```text
Retrieval-augmented generation (RAG) retrieves information relevant to a question from external documents and supplies it to a generative model to produce an answer. When Korean questions are used to search English academic and technical documents, differences between the question and the source text can affect retrieval. We separately evaluated the faithfulness of generated answers to the retrieved evidence and the proportion of Korean characters in those answers. We used Hypothetical Document Embeddings (HyDE) to modify dense-retrieval inputs, Context-Aware Decoding (CAD) to adjust token scores using retrieved context, and Soft Constrained Decoding (SCD) to control Korean output. We evaluated eight combinations of these methods in a RAG-Cube experiment.
```

B (최종 원고):

```text
Retrieval-Augmented Generation (RAG) retrieves document passages and uses their text to generate answers. When Korean queries are used to search English academic and technical documents, retrieval relevance, grounding in retrieved evidence, and output language require separate evaluation. This study compares combinations of Hypothetical Document Embeddings (HyDE), Context-Aware Decoding (CAD), and Soft Constrained Decoding (SCD) within a fixed retrieval and generation pipeline.
```

## 8. replace · 원고 35–35 → 35–35

A (기준 원고):

```text
The Paper-RAG backbone used BGE-M3 for dense retrieval and BM25 for sparse retrieval. We combined their results using weighted Reciprocal Rank Fusion, reranked the candidates with a CrossEncoder, and generated answers with K-intelligence/Midm-2.0-Base-Instruct. We constructed 15 Korean evaluation queries for each of four English academic or technical documents, for a total of 60 queries. Each query was assigned a target document and evaluated under eight configurations, yielding 480 stored generation records. HyDE was compared on 60 matched pairs with CAD and SCD disabled. CAD was compared with HyDE and SCD disabled and the retrieval contexts held identical. The primary SCD comparison used 120 HyDE-OFF pairs with identical retrieval contexts. We also analyzed all 240 ON/OFF pairs matched by query and by HyDE and CAD settings.
```

B (최종 원고):

```text
Sixty Korean queries, fifteen from each of four English documents, were evaluated under all eight conditions of a two-level, three-factor design, yielding 480 generation records. The pipeline combines BGE-M3 and BM25 retrieval through weighted Reciprocal Rank Fusion (RRF), CrossEncoder reranking, and Mi:dm 2.0 Base Instruct generation. Four quality metrics were measured with the RAGAS evaluation framework, and the Korean-character ratio was computed directly from generated answers. Queries served as repeated-measures units. Quality analyses were stratified by the evaluation-context protocol: English contexts for SCD OFF and Korean-translated contexts for SCD ON. Two-sided tests used a significance level of 0.05 and Holm adjustment.
```

## 9. replace · 원고 37–37 → 37–37

A (기준 원고):

```text
The mean paired difference in answer relevancy between HyDE ON and OFF was +0.0805, with a 95% bootstrap confidence interval of [+0.0110, +0.1514]. The corresponding differences in faithfulness, context precision, and context recall were +0.0436, -0.0343, and 0.0000, respectively. In the identical-context CAD comparison, the mean paired difference in faithfulness was +0.0288 on 58 pairs with both scores available, with a 95% bootstrap confidence interval of [-0.0367, +0.0934], which included zero. The mean paired difference in answer relevancy was -0.0073 on 60 pairs. In the primary SCD comparison, the mean paired difference in the Korean-character ratio was +0.2182 on 120 HyDE-OFF identical-context pairs, with a 95% bootstrap confidence interval of [+0.1880, +0.2487]. The mean paired difference across all 240 state-matched pairs was +0.2289.
```

B (최종 원고):

```text
With CAD and SCD disabled, the HyDE comparison yielded a mean paired answer-relevancy difference of +0.080, t(59)=2.236, unadjusted p=0.029, and p=0.117 after adjustment across four quality metrics. The identical-context CAD comparison yielded a faithfulness difference of +0.029, t(57)=0.862, and unadjusted p=0.393. For the primary SCD comparison, the two CAD-state differences were averaged within each query under HyDE OFF. The mean Korean-character-ratio difference was +21.8 percentage points, t(59)=13.951, adjusted p<0.001. The eight-condition analysis also identified an SCD main effect on this ratio. HyDE and CAD main effects and the CAD-by-SCD interaction were significant for condition execution time after adjustment.
```

## 10. replace · 원고 39–39 → 39–41

A (기준 원고):

```text
Keywords: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, Korean query, English academic or technical document, language drift
```

B (최종 원고):

```text
The comparisons distinguish changes in answer quality, output language, and execution time at different pipeline stages. Reporting simple contrasts alongside factorial effects provides an empirical account of how the three techniques behave in combination.

Keywords: Retrieval-Augmented Generation, HyDE, Context-Aware Decoding, Soft Constrained Decoding, Korean queries, English documents, repeated measures
```

## 11. replace · 원고 46–46 → 48–48

A (기준 원고):

```text
1.3 연구 질문, 분석 관점 및 논문 구성 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

B (최종 원고):

```text
1.3 연구 질문 및 논문 구성 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

## 12. replace · 원고 50–50 → 52–52

A (기준 원고):

```text
2.3 HyDE와 가상 문서 기반 검색 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

B (최종 원고):

```text
2.3 가상 문서 임베딩과 검색 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

## 13. replace · 원고 58–58 → 60–60

A (기준 원고):

```text
3.3 상세설계 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

B (최종 원고):

```text
3.3 완전요인 실험 및 대응 비교 설계 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

## 14. replace · 원고 62–62 → 64–64

A (기준 원고):

```text
4.3 시스템 구현 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

B (최종 원고):

```text
4.3 시스템 구현과 실행 기록 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

## 15. replace · 원고 64–70 → 66–72

A (기준 원고):

```text
5.1 실험 대상과 구성 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.2 평가 및 분석 방법 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.3 RAG-Cube 조합별 결과 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.4 HyDE 결과 및 해석 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.5 CAD 결과 및 해석 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.6 SCD 출력 언어 결과 및 해석 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.7 대표 입출력 및 요구사항별 실행 결과 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

B (최종 원고):

```text
5.1 평가 대상 및 질의 구성 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.2 평가 지표와 해석 기준 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.3 실험 조건 및 평가 절차 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.4 통계 분석 방법 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.5 조합별 평가 결과 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.6 요인 주효과 및 상호작용 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
5.7 연구 질문별 대응 비교 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

## 16. replace · 원고 72–72 → 74–74

A (기준 원고):

```text
5.9 실험 범위와 해석 기준 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

B (최종 원고):

```text
5.9 평가 범위와 후속 검증 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

## 17. replace · 원고 74–77 → 76–78

A (기준 원고):

```text
6.1 연구 질문별 최종 답 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.2 비교 설계의 의의 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.3 적용 시 실험 조건 선택 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.4 후속 연구 방향 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

B (최종 원고):

```text
6.1 연구 질문별 결과 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.2 연구의 의의 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
6.3 적용 조건과 후속 연구 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
```

## 18. replace · 원고 79–80 → 80–84

A (기준 원고):

```text
그림 자료 이용 정보 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
부록 A~B ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
```

B (최종 원고):

```text
부록 A. 60개 질의 목록 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
부록 B. 추가 사례 및 탐색 분석 ···· [쪽번호 자동갱신] [스타일=목차리스트(장)]
B.1 저장된 생성·검색 사례 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]
B.2 문서별 및 질문 유형별 탐색 분석 ···· [쪽번호 자동갱신] [스타일=목차리스트(절)]

```

## 19. replace · 원고 83–83 → 87–87

A (기준 원고):

```text
[그림 1-1] 한국어 질의와 영어 학술 및 기술 문서를 사용하는 RAG 실험 환경 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
```

B (최종 원고):

```text
[그림 1-1] 한국어 질의와 영어 학술·기술 문서를 사용하는 RAG 실험 환경 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
```

## 20. replace · 원고 85–104 → 89–99

A (기준 원고):

```text
[그림 2-2] 긴 문맥에서 관련 정보 위치에 따른 성능 변화 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 2-3] HyDE의 가상 문서 기반 검색 구조 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 2-4] Context-Aware Decoding의 분포 대조 구조 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 2-5] 다국어 RAG의 출력 언어 이탈 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 2-6] RAGAS의 근거 충실도 높음/낮음 예시 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 3-1] HyDE, CAD, SCD를 조합한 RAG-Cube 8개 조건 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 4-1] 고정 Paper-RAG 백본 실행 흐름 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 4-2] 생성 기록–평가–대응 분석 흐름 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-1] 60개 질의 평가 및 HyDE, CAD, SCD의 대응 비교 설계 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-2] 평가 프로토콜별 RAG-Cube 조건 평균 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-3] HyDE 적용에 따른 검색 문맥 및 답변 변화 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-4] HyDE와 CAD의 주 대응 비교 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-5] 동일 검색 문맥에서 CAD 적용 전후 답변 비교 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-6] RAG-Cube 조건별 평균 실행 시간 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-7] SCD OFF 조건의 출력 언어 이탈 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-8] 동일 검색 문맥에서 SCD 적용 전후 출력 언어 변화 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-9] SCD의 한국어 문자 비율 변화 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-10] 질문, 검색 근거, 생성 답변과 평가 결과 예시 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-11] HyDE와 CAD의 조건군별 근거 충실도 및 답변 관련성 평균 대응 차이 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 B-1] 동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 추가 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
```

B (최종 원고):

```text
[그림 2-2] HyDE의 가상 문서 기반 검색 구조 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 2-3] CAD의 문맥 포함·제외 로짓 결합 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 2-4] SCD의 토큰 그룹별 로짓 조정 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 4-1] 한국어 질의의 검색·융합·재정렬 및 답변 생성 흐름 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-1] 질의별 생성 기록과 평가값을 연결하는 대응 비교 절차 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 5-2] RAPTOR 질의의 검색 근거, 생성 답변 및 평가 예시 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 B-1] 동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 B-2] HyDE 적용에 따른 검색 문맥 및 답변 변화 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 B-3] 동일 검색 문맥에서 CAD 적용 전후 답변 비교 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 B-4] SCD 미적용 조건의 영어 중심 출력 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[그림 B-5] SCD 적용 전후 한국어 문자 비율 변화 사례 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
```

## 21. replace · 원고 108–124 → 103–116

A (기준 원고):

```text
[표 2-1] 관련 연구와 본 실험의 연결 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 3-1] 연구 및 실험 요구사항 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 3-2] RAG-Cube 8개 조건 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 3-3] 실험 요인별 적용 위치와 비교 단위 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-1] 실험 실행 환경 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-2] 고정 Paper-RAG 백본 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-3] 실험 조건별 실행 시간 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-4] 생성 기록의 주요 필드 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-1] 4개 문서별 질의 구성 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-2] SCD 평가 프로토콜별 RAG-Cube 조건 평균 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-3] HyDE 주 비교 결과 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-4] CAD 동일 문맥 주 비교 결과 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-5] SCD 조합별 한국어 문자 비율 변화 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-6] SCD 대응쌍 분석 요약 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 A-1] 60개 질의–대상 문서 쌍 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 B-1] 문서별 탐색 분석 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 B-2] 질문 유형별 탐색 분석 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
```

B (최종 원고):

```text
[표 2-1] 선행연구의 접근과 본 연구의 비교 질문 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 3-1] HyDE·CAD·SCD의 3요인 2수준 실험 조건 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 4-1] 검색·재정렬·생성 단계의 모델과 공통 실행 설정 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-1] 평가 문맥 언어별 8조건의 품질 및 한국어 문자 비율 평균(SD) ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-2] 8조건의 질의별 조건 실행 시간 평균과 표준편차 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-3] SCD OFF 영어 평가 문맥의 품질 지표 H×C 반복측정 ANOVA ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-4] SCD ON 한국어 번역 평가 문맥의 품질 지표 H×C 반복측정 ANOVA ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-5] 한국어 문자 비율의 H×C×S 반복측정 ANOVA ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-6] 조건 실행 시간의 H×C×S 반복측정 ANOVA ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-7] HyDE·CAD 단순 비교의 품질 대응 점수 차이와 검정 결과 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 5-8] SCD 한국어 문자 비율의 질의별 평균 대응 차이(%p)와 검정 결과 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 A-1] 60개 한국어 질의의 대상 문서·유형·원문 페이지 및 정답 근거 ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 B-1] 문서별 HyDE·CAD 대응 점수 차이의 평균(SD) ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
[표 B-2] 질문 유형별 HyDE·CAD 대응 점수 차이의 평균(SD) ···· [쪽번호 자동갱신] [스타일=표/그림리스트]
```

## 22. replace · 원고 130–130 → 122–122

A (기준 원고):

```text
검색 증강 생성(Retrieval-Augmented Generation, RAG)은 외부 문서에서 질문과 관련된 내용을 검색하고, 검색된 문맥을 생성 모델에 제공하여 답변을 생성하는 방법이다[1]. 본 연구에서는 한국어 질의로 영어 학술 및 기술 문서에서 근거를 검색하고, 이를 이용해 한국어 답변을 생성하는 과정을 분석하였다. 한국어 질문과 영어 원문의 표현 차이는 검색 결과에 영향을 줄 수 있다. 생성된 답변에 대해서는 검색 근거에 대한 충실도와 한국어 문자 비율을 각각 측정하였다.
```

B (최종 원고):

```text
검색 증강 생성(Retrieval-Augmented Generation, RAG)은 사용자의 질문과 관련된 문서 구간을 외부 자료에서 검색하고, 검색 결과에 포함된 텍스트를 생성 모델에 제공하여 답변을 생성하는 방법이다[1]. 본 논문에서는 생성 모델에 제공하는 검색 결과의 텍스트를 검색 문맥으로 지칭한다. 검색기는 필요한 근거를 찾고, 생성 모델은 질문과 검색 문맥을 함께 입력받아 답변을 작성한다.
```

## 23. replace · 원고 132–132 → 124–124

A (기준 원고):

```text
HyDE는 입력 질의를 바탕으로 가상 문서를 생성하고, 이를 벡터로 변환하여 관련 문서를 검색한다[2]. CAD는 검색 문맥을 포함한 입력과 제외한 입력에서 다음 토큰의 로짓을 각각 계산한다. 두 로짓을 가중 결합하여 토큰 선택에 반영한다[3]. SCD는 토큰을 목표 언어, 다른 언어와 중립 토큰으로 구분한다. 본 구현에서는 목표 언어와 다른 언어 토큰의 로짓에 각각 정해진 계수를 곱하고, 중립 토큰의 로짓은 유지한다[4].
```

B (최종 원고):

```text
RAG의 검색 입력과 답변 생성 과정을 개선하기 위해 여러 기법이 제안되었다. 가상 문서 임베딩(Hypothetical Document Embeddings, HyDE)은 질의에서 생성한 가상 문서를 검색에 활용한다[2]. 문맥 인식 디코딩(Context-Aware Decoding, CAD)은 검색 문맥을 포함한 입력과 제외한 입력의 다음 토큰 점수를 결합한다[3]. 소프트 제약 디코딩(Soft Constrained Decoding, SCD)은 목표 언어에 해당하는 토큰의 점수를 조정하여 출력 언어를 제어한다[4]. 각 기법은 검색 표현, 검색 근거의 활용, 출력 언어에 개입한다.
```

## 24. replace · 원고 134–134 → 126–126

A (기준 원고):

```text
HyDE, CAD, SCD를 같은 Paper-RAG 백본에 적용하고 각 기법의 ON/OFF 결과를 비교하였다[2][3][4]. HyDE는 적용 전후 검색 문맥과 생성 답변의 변화를 함께 비교하였다. CAD는 검색 문맥을 동일하게 유지한 상태에서 답변 품질과 조건 실행 시간을 비교하였다. SCD는 HyDE OFF 조건에서 검색 문맥이 동일한 대응쌍을 사용해 한국어 문자 비율의 변화를 분석하였다. 대응쌍의 구성과 문맥 동일성 확인 기준은 3.3절에 제시한다.
```

B (최종 원고):

```text
한국어 질의로 영어 문서를 검색할 때에는 질문과 원문에 쓰인 언어와 표현이 다르다. 검색 단계에서는 질문에 필요한 문서 구간을 찾는지가 중요하다. 생성 단계에서는 찾은 구간이 답변의 주장을 뒷받침하는지 확인해야 한다. 영어 근거를 이용한 답변이 한국어 중심으로 작성되는지도 별도로 측정할 필요가 있다. 세 기법을 같은 파이프라인에 적용하면 이러한 항목이 적용 여부와 조합에 따라 어떻게 달라지는지 비교할 수 있다.
```

## 25. replace · 원고 136–136 → 128–128

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig1_1_research_setting.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
본 연구는 영어 학술·기술 문서의 텍스트 구간을 검색하고 이를 바탕으로 답변을 생성하는 고정 파이프라인을 구성하였다. 이하 이 파이프라인을 Paper-RAG로 지칭한다. Paper-RAG에 HyDE, CAD, SCD를 각각 적용하거나 미적용하여 8개 조건을 구성하였다. 이 조건 배치를 RAG-Cube로 지칭한다. 연구 목적은 한국어 질의와 영어 문서를 사용하는 동일한 환경에서 답변 품질과 출력 언어를 비교하고, 각 기법의 단순 효과와 조합에 따른 요인 효과를 분석하는 것이다.
```

## 26. replace · 원고 138–138 → 130–132

A (기준 원고):

```text
[그림 1-1] 한국어 질의와 영어 학술 및 기술 문서를 사용하는 RAG 실험 환경 [스타일=그림제목]
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig1_1_research_setting.png | 권장폭=본문폭 100% | 정렬=가운데]

[그림 1-1] 한국어 질의와 영어 학술·기술 문서를 사용하는 RAG 실험 환경 [스타일=그림제목]
```

## 27. replace · 원고 142–142 → 136–136

A (기준 원고):

```text
연구 대상으로 RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 영어 문서 4개를 선정하였다. 네 문서에 대해 각각 한국어 평가 질의 15개를 작성하였다. 총 60개 질의에는 각각 검색 대상 문서를 지정하였다. 각 질의에 8개 RAG-Cube 조건을 적용하여 480개의 생성 기록을 저장하였다. 검색 범위는 각 질의에 지정한 문서의 청크로 정하였다. BGE-M3와 BM25의 검색 결과를 weighted RRF로 결합하고 CrossEncoder로 재정렬하였다. 재정렬 상위 5개 청크에 문맥 길이 관리 절차를 적용한 뒤 Mi:dm 2.0 Base Instruct에 입력하였다. 실행 설정은 4.1절에 정리하였다.
```

B (최종 원고):

```text
RAG Survey, CAD, RAPTOR, Mi:dm K 2.5 Pro Technical Report의 영어 문서 4종을 대상으로 문서별 한국어 질의 15개씩 총 60개를 구성하였다. 각 질의에는 검색 대상 문서를 지정하였다. 검색 범위는 지정 문서의 텍스트 구간이며, 질의마다 같은 8조건을 적용하여 생성 기록 480개를 분석하였다.
```

## 28. replace · 원고 144–144 → 138–138

A (기준 원고):

```text
HyDE는 CAD와 SCD가 모두 OFF인 60개 대응쌍에서 검색부터 답변 생성까지의 변화를 비교하였다. CAD는 동일한 검색 문맥에서 생성한 답변의 품질과 조건 실행 시간을 비교하였다. SCD는 HyDE OFF 동일 문맥 120개 대응쌍을 주 비교로 삼고, 동일 질의의 HyDE와 CAD 상태를 각각 맞춘 전체 240개 대응쌍을 함께 분석하였다. 답변 품질은 RAGAS 지표로, 출력 언어는 한국어 문자 비율로 측정하였다.
```

B (최종 원고):

```text
비교 대상은 네 RAGAS 품질 지표, 한국어 문자 비율과 조건 실행 시간이다. 답변 생성 모델은 Mi:dm 2.0 Base Instruct이며, Mi:dm K 2.5 Pro Technical Report는 검색 대상 문서다. 두 명칭은 각각 생성 모델과 평가 자료를 가리킨다. 검색·재정렬·생성 설정은 4장에 제시한다.
```

## 29. replace · 원고 146–146 → 140–140

A (기준 원고):

```text
## 1.3 연구 질문, 분석 관점 및 논문 구성 [스타일=절(1.1)]
```

B (최종 원고):

```text
## 1.3 연구 질문 및 논문 구성 [스타일=절(1.1)]
```

## 30. replace · 원고 148–148 → 142–142

A (기준 원고):

```text
연구 질문은 다음 네 가지로 설정하였다. 첫째, CAD와 SCD를 OFF로 고정한 상태에서 HyDE를 적용하면 답변 관련성, 근거 충실도, 문맥 정밀도와 문맥 재현율은 어떻게 달라지는가? 둘째, 동일한 검색 문맥에서 CAD 적용 여부에 따라 답변 품질과 조건 실행 시간은 어떻게 달라지는가? 셋째, SCD 적용 여부에 따라 한국어 문자 비율은 어떻게 달라지는가? 넷째, 기법별 평가 결과와 조건 실행 시간을 기준으로 실험 조건을 어떻게 선택할 수 있는가?
```

B (최종 원고):

```text
RQ1. CAD와 SCD를 미적용한 상태에서 HyDE 적용 여부에 따라 답변 관련성, 근거 충실도, 문맥 정밀도와 문맥 재현율은 어떻게 달라지는가?
```

## 31. replace · 원고 150–150 → 144–144

A (기준 원고):

```text
SCD의 주 비교에는 HyDE를 OFF로 고정하고 검색 문맥이 동일한 120개 대응쌍을 사용하였다. 추가로 HyDE와 CAD의 적용 상태를 각각 맞춘 전체 240개 대응쌍도 분석하였다. 동일 질의의 ON 평가값에서 OFF 평가값을 뺀 대응 차이와 부트스트랩 신뢰구간을 계산하였다. 각 대응쌍의 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥을 대조하여 입력 문맥의 동일성을 확인하였다. 개별 사례에서는 질문, 검색 근거, 생성 답변과 평가값을 함께 제시하였다.
```

B (최종 원고):

```text
RQ2. 같은 검색 문맥에서 CAD 적용 여부에 따라 답변 품질과 조건 실행 시간은 어떻게 달라지는가?
```

## 32. replace · 원고 152–152 → 146–152

A (기준 원고):

```text
2장에서는 RAG와 세 실험 요인, 평가 및 관련 연구를 정리한다. 3장은 실험 요구사항과 비교 설계를, 4장은 구현과 생성 기록 저장 구조를 설명한다. 5장은 60개 질의 평가 결과와 사례를 제시하고, 6장은 주요 결과와 적용 기준 및 후속 연구를 종합한다.
```

B (최종 원고):

```text
RQ3. SCD 적용 여부에 따라 생성 답변의 한국어 문자 비율은 어떻게 달라지는가?

RQ4. HyDE·CAD·SCD의 조합에 따라 답변 품질, 한국어 문자 비율 및 실행 시간은 어떻게 달라지는가?

RQ1과 RQ2는 다른 기법을 미적용한 대응 비교로 분석한다. RQ3은 검색 문맥이 같은 HyDE OFF 비교를 중심으로 분석하고, RQ4는 반복측정 요인 분석으로 다룬다. 지표마다 비교 조건과 분석 단위를 명시하여 개별 조건의 차이와 요인 주효과를 구분한다.

2장에서는 기법과 선행연구를 정리한다. 3장에서는 완전요인 실험 설계를, 4장에서는 구현과 기록 방법을 설명한다. 5장에서는 평가 절차와 통계 결과를 제시하고, 6장에서는 연구 질문별 결과와 후속 연구를 논의한다.
```

## 33. replace · 원고 162–162 → 162–162

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_1_rag_independent.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_1_rag_independent.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 34. replace · 원고 182–182 → 182–182

A (기준 원고):

```text
고정 백본은 BGE-M3 밀집 검색과 BM25 희소 검색을 결합한다. 밀집 검색은 질의와 문서 구간의 의미적 유사성을 기준으로 관련 문서 구간을 검색한다. BM25는 모델명, 약어, 수치처럼 질의와 원문에 동일하게 등장하는 표현을 검색 단서로 활용하였다[5][6]. 두 검색 결과의 순위를 weighted Reciprocal Rank Fusion으로 결합한다[7]. 이어 CrossEncoder가 원질의와 각 후보 구간의 관련성을 계산하여 순서를 다시 정한다[8].
```

B (최종 원고):

```text
고정 백본은 BGE-M3 밀집 검색과 BM25 희소 검색을 결합한다. 밀집 검색은 질의와 문서 구간의 의미적 유사성을 기준으로 관련 문서 구간을 검색한다. BM25는 모델명, 약어, 수치처럼 질의와 원문에 동일하게 등장하는 표현을 검색 단서로 활용하였다[5][6]. 두 검색 결과의 순위를 가중 역순위 융합(weighted Reciprocal Rank Fusion, RRF)으로 결합한다[7]. 이어 CrossEncoder가 원질의와 각 후보 구간의 관련성을 계산하여 순서를 다시 정한다[8].
```

## 35. replace · 원고 190–196 → 190–190

A (기준 원고):

```text
관련 문서 구간을 검색하더라도 생성 모델이 이를 활용하는 정도는 입력 내 위치에 따라 달라질 수 있다. Liu 외[9]는 다중 문서 질의응답에서 정답 문서가 입력의 처음이나 끝에 있을 때보다 중간에 있을 때 성능이 낮아지는 U자형 패턴을 보고하였다. 그림 2-2는 관련 정보의 입력 위치에 따른 성능 차이를 보여준다. 본 실험에서는 최종 입력 문맥을 상위 5개 청크로 구성하고, 재정렬 순서대로 배치하였다. 검색 성능과 답변 품질은 별도 지표로 평가하였다.

[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_2_lost_middle_tacl.png | 권장폭=본문폭 75% | 정렬=가운데]

[그림 2-2] 긴 문맥에서 관련 정보 위치에 따른 성능 변화 [스타일=그림제목]

출처: Liu 외[9], 그림 1에서 발췌.
```

B (최종 원고):

```text
관련 문서 구간을 검색하더라도 생성 모델이 이를 활용하는 정도는 입력 내 위치에 따라 달라질 수 있다. Liu 외[9]는 다중 문서 질의응답에서 정답 문서가 입력의 처음이나 끝에 있을 때보다 중간에 있을 때 성능이 낮아지는 U자형 패턴을 보고하였다. 본 실험에서는 최종 입력 문맥을 상위 5개 청크로 구성하고, 재정렬 순서대로 배치하였다. 검색 성능과 답변 품질은 별도 지표로 평가하였다.
```

## 36. replace · 원고 206–206 → 200–200

A (기준 원고):

```text
## 2.3 HyDE와 가상 문서 기반 검색 [스타일=절(1.1)]
```

B (최종 원고):

```text
## 2.3 가상 문서 임베딩과 검색 [스타일=절(1.1)]
```

## 37. replace · 원고 208–208 → 202–202

A (기준 원고):

```text
HyDE는 입력 질의를 바탕으로 가상 문서를 생성한 뒤, 이를 임베딩 벡터로 변환한다. 생성된 벡터를 이용해 실제 문서 집합에서 유사한 문서를 검색한다[2].
```

B (최종 원고):

```text
가상 문서 임베딩(Hypothetical Document Embeddings, HyDE)은 입력 질의를 바탕으로 가상 문서를 생성한 뒤, 이를 임베딩 벡터로 변환한다. 생성된 벡터를 이용해 실제 문서 집합에서 유사한 문서를 검색한다[2]. Gao 외[2]는 관련성 레이블 없이 수행하는 검색에서 Contriever와 비교하고, 영어 과제와 한국어를 포함한 비영어 검색 과제의 성능을 보고하였다. 본 연구에서는 영어 문서에 대한 한국어 질의를 번역·가상 문서 생성과 결합하여 비교한다.
```

## 38. replace · 원고 210–210 → 204–204

A (기준 원고):

```text
그림 2-3은 입력 질의로 가상 문서를 생성하고, 이를 임베딩한 뒤 실제 문서 집합을 검색하는 HyDE의 처리 과정을 나타낸다.
```

B (최종 원고):

```text
그림 2-2은 입력 질의로 가상 문서를 생성하고, 이를 임베딩한 뒤 실제 문서 집합을 검색하는 HyDE의 처리 과정을 나타낸다.
```

## 39. replace · 원고 212–212 → 206–206

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_3_hyde_acl_no_logo.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_2_hyde_independent.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 40. replace · 원고 214–214 → 208–208

A (기준 원고):

```text
[그림 2-3] HyDE의 가상 문서 기반 검색 구조 [스타일=그림제목]
```

B (최종 원고):

```text
[그림 2-2] HyDE의 가상 문서 기반 검색 구조 [스타일=그림제목]
```

## 41. replace · 원고 216–216 → 210–210

A (기준 원고):

```text
출처: Gao 외[2]의 그림 1을 발췌하여 편집하였다.
```

B (최종 원고):

```text
본 연구에서 작성한 도식이며, Gao 외[2]의 HyDE 구조를 참고하였다.
```

## 42. replace · 원고 218–218 → 212–212

A (기준 원고):

```text
HyDE ON 조건에서는 한국어 질의를 영어로 번역하고 가상 문서를 생성하였다. 생성된 가상 문서를 BGE-M3로 임베딩하여 밀집 검색에 사용하였다. BM25 검색과 CrossEncoder 재정렬에는 원래의 한국어 질의를 사용하였다. 검색 범위는 질의에 지정한 문서의 청크로 정하였으며, 최종 답변은 검색한 실제 문서 구간으로 생성하였다. HyDE ON/OFF 비교에서는 질의 번역과 가상 문서 생성에 따라 밀집 검색 입력이 달라진다. 검색 청크 ID와 최종 검색 문맥을 대조하여 검색 결과의 변화를 확인하고, 생성 답변의 답변 관련성도 함께 분석하였다.
```

B (최종 원고):

```text
HyDE ON 조건에서는 답변 생성에 사용하는 Mi:dm 2.0 Base Instruct를 이용해 한국어 질의를 영어로 번역하고 가상 문서를 생성하였다. 생성된 가상 문서를 BGE-M3로 임베딩하여 밀집 검색에 사용하였다. BM25 검색과 CrossEncoder 재정렬에는 원래의 한국어 질의를 사용하였다. 검색 범위는 질의에 지정한 문서의 청크로 정하였으며, 최종 답변은 검색한 실제 문서 구간으로 생성하였다. HyDE ON/OFF 비교에서는 질의 번역과 가상 문서 생성에 따라 밀집 검색 입력이 달라진다. 검색 청크 ID와 최종 검색 문맥을 대조하여 검색 결과의 변화를 확인하고, 생성 답변의 답변 관련성도 함께 분석하였다.
```

## 43. replace · 원고 224–224 → 218–218

A (기준 원고):

```text
그림 2-4에서 문맥을 포함한 분포와 제외한 분포는 모두 “Two”의 점수가 가장 높다. 두 분포의 로짓을 CAD 식으로 결합하면 문맥에 제시된 우승 횟수에 해당하는 “Three”가 선택된다.
```

B (최종 원고):

```text
Shi 외[3]는 OPT, GPT, LLaMA, FLAN-T5를 이용한 요약 및 지식 충돌 과제에서 CAD의 근거 활용을 평가하였다. 본 연구는 한국어 질의와 영어 검색 문맥을 사용하는 Mi:dm 모델에서 같은 문맥의 CAD 적용 여부를 비교한다. 그림 2-3은 두 입력에서 계산한 로짓을 결합하는 과정을 나타낸다.
```

## 44. replace · 원고 226–226 → 220–220

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_4_cad_original.png | 권장폭=본문폭 72% | 정렬=가운데]
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_3_cad_independent.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 45. replace · 원고 228–228 → 222–222

A (기준 원고):

```text
[그림 2-4] Context-Aware Decoding의 분포 대조 구조 [스타일=그림제목]
```

B (최종 원고):

```text
[그림 2-3] CAD의 문맥 포함·제외 로짓 결합 [스타일=그림제목]
```

## 46. replace · 원고 230–230 → 224–224

A (기준 원고):

```text
출처: Shi 외[3], 그림 1에서 발췌.
```

B (최종 원고):

```text
본 연구에서 작성한 도식이며, Shi 외[3]의 CAD 로짓 결합을 참고하였다.
```

## 47. replace · 원고 240–240 → 234–234

A (기준 원고):

```text
CAD는 토큰을 생성할 때 검색 문맥을 포함한 입력과 제외한 입력에 대해 각각 다음 토큰의 로짓을 계산한다. 5.5절에서는 답변 품질의 대응 차이, 질의별 변화 분포와 조건 실행 시간의 증가를 분석하였다.
```

B (최종 원고):

```text
CAD는 토큰을 생성할 때 검색 문맥을 포함한 입력과 제외한 입력에 대해 각각 다음 토큰의 로짓을 계산한다. 5.7절에서는 답변 품질의 대응 차이, 질의별 변화 분포와 조건 실행 시간의 증가를 분석하였다.
```

## 48. replace · 원고 246–246 → 240–240

A (기준 원고):

```text
다국어 RAG에서는 검색 문서의 언어로 답변이 생성되는 출력 언어 이탈(language drift)이 발생할 수 있다. Li 외[4]는 목표 언어와 비목표 언어가 추론 과정에서 혼합된 뒤 최종 출력이 비목표 언어로 이동하는 사례를 분석하였다. 그림 2-5는 원 논문의 출력 언어 이탈 사례다.
```

B (최종 원고):

```text
다국어 RAG에서는 검색 문서의 언어로 답변이 생성되는 출력 언어 이탈(language drift)이 발생할 수 있다. Li 외[4]는 목표 언어와 비목표 언어가 추론 과정에서 혼합된 뒤 최종 출력이 비목표 언어로 이동하는 사례를 분석하였다. Li 외[4]는 세 다국어 데이터셋과 여러 언어·모델에서 언어 이탈과 SCD를 평가하였다. 그림 2-4는 본 실험의 한국어 목표 토큰, 비목표 언어 토큰과 중립 토큰의 점수 조정 과정을 나타낸다.
```

## 49. replace · 원고 248–248 → 242–242

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_5_scd_no_logos.png | 권장폭=본문폭 78% | 정렬=가운데]
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_4_scd_independent.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 50. replace · 원고 250–250 → 244–244

A (기준 원고):

```text
[그림 2-5] 다국어 RAG의 출력 언어 이탈 사례 [스타일=그림제목]
```

B (최종 원고):

```text
[그림 2-4] SCD의 토큰 그룹별 로짓 조정 [스타일=그림제목]
```

## 51. replace · 원고 252–252 → 246–246

A (기준 원고):

```text
출처: Li 외[4]의 그림 1을 발췌하여 편집하였다.
```

B (최종 원고):

```text
본 연구에서 작성한 도식이며, Li 외[4]의 SCD 토큰별 점수 조정을 참고하였다.
```

## 52. replace · 원고 284–284 → 278–278

A (기준 원고):

```text
한국어 문자 비율을 계산할 때는 답변에 포함된 영어 논문 제목, 모델명과 데이터셋명의 ASCII 영문자도 분모에 포함하였다. SCD 대응쌍의 구성과 변화 판정 기준은 5.2절에서 설명한다.
```

B (최종 원고):

```text
한국어 문자 비율 0.700은 계산 대상인 한글과 ASCII 영문자 중 한글이 70.0%임을 나타낸다. 한글 완성형·자모와 ASCII 영문자를 세며, 숫자·공백·문장부호는 계산에서 제외한다. 영어 논문 제목, 모델명과 데이터셋명의 ASCII 영문자는 분모에 포함한다. 한국어 문자 비율 분석기는 계산 대상 문자 수가 0인 답변의 비율을 0으로 기록한다. 해당 답변 1건과 질의 제외 민감도 분석은 5.4절에서 설명한다. SCD 대응쌍의 구성과 변화 판정 기준은 5.4절에서 설명한다.
```

## 53. replace · 원고 288–288 → 282–282

A (기준 원고):

```text
HyDE와 CAD의 답변 품질은 RAGAS의 근거 충실도(faithfulness), 답변 관련성(answer relevancy), 문맥 정밀도(context precision), 문맥 재현율(context recall)로 평가하였다[10]. 근거 충실도는 검색 문맥이 답변의 주장을 뒷받침하는 정도를 측정한다. 답변 관련성은 평가 모델이 생성 답변을 바탕으로 만든 질문과 원질문의 의미적 유사도를 이용해 측정한다. 본 실험에서 사용한 RAGAS 0.2.15의 문맥 정밀도는 참조 답변을 기준으로 검색 문맥의 관련성을 판정하고, 관련 문맥이 상위에 배치되는 정도를 측정한다. 문맥 재현율은 검색 문맥이 참조 답변의 내용을 뒷받침하는 정도를 측정한다.
```

B (최종 원고):

```text
RAG 자동 평가 프레임워크(Retrieval Augmented Generation Assessment, RAGAS)는 검색 결과와 생성 답변을 지표별로 평가한다[10]. 본 연구의 답변 품질은 RAGAS의 근거 충실도(faithfulness), 답변 관련성(answer relevancy), 문맥 정밀도(context precision), 문맥 재현율(context recall)로 평가하였다[10]. 근거 충실도는 검색 문맥이 답변의 주장을 뒷받침하는 정도를 측정한다. 답변 관련성은 평가 모델이 생성 답변을 바탕으로 만든 질문과 원질문의 의미적 유사도를 이용해 측정한다. 본 실험에서 사용한 RAGAS 0.2.15의 문맥 정밀도는 참조 답변을 기준으로 검색 문맥의 관련성을 판정하고, 관련 문맥이 상위에 배치되는 정도를 측정한다. 문맥 재현율은 검색 문맥이 참조 답변의 내용을 뒷받침하는 정도를 측정한다.
```

## 54. replace · 원고 290–296 → 284–284

A (기준 원고):

```text
Es 외[10]는 WikiEval에서 동일한 질문과 검색 문맥에 대한 서로 다른 답변을 비교하여 근거 충실도를 설명하였다. 그림 2-6은 원 논문의 표 2에서 발췌한 사례이며, 같은 검색 문맥으로 뒷받침되는 답변과 그렇지 않은 답변을 보여준다.

[그림삽입: FINALDOCS/FIGURES/LITERATURE/fig2_6_ragas_faithfulness_original.png | 권장폭=본문폭 92% | 정렬=가운데]

[그림 2-6] RAGAS의 근거 충실도 높음/낮음 예시 [스타일=그림제목]

출처: Es 외[10], 표 2에서 발췌.
```

B (최종 원고):

```text
Es 외[10]는 WikiEval에서 질문, 검색 문맥과 생성 답변을 대조하여 근거 충실도를 설명하였다. 본 연구의 실제 평가 예시는 5.3절에 제시한다.
```

## 55. replace · 원고 310–310 → 298–298

A (기준 원고):

```text
[표 2-1] 관련 연구와 본 실험의 연결 [스타일=표제목]
```

B (최종 원고):

```text
[표 2-1] 선행연구의 접근과 본 연구의 비교 질문 [스타일=표제목]
```

## 56. delete · 원고 314–315 → 302–301

A (기준 원고):

```text
[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```

B (최종 원고):

```text
(삭제)
```

## 57. replace · 원고 317–323 → 303–309

A (기준 원고):

```text
연구 흐름	대표 연구	본 연구에서의 적용 범위	해석 범위
밀집 검색과 검색 평가	DPR[11], BEIR[20]	한국어 질의와 영어 문서 사이의 검색 표현 차이를 HyDE 조건으로 비교	DPR은 검색 방법, BEIR은 관련 평가 연구로 참조
다중 문맥 생성	FiD[12], 긴 문맥 분석[9]	재정렬 순위에 따라 상위 5개 청크를 선택하고 답변 지표와 문맥 지표를 구분	문맥 수와 순서 정책 고정
가상 문서 검색	HyDE[2]	H1/H0 종단 간 대응 비교와 검색 청크 ID 확인	가상 문서는 검색 표현으로 사용
대조 디코딩	CAD[3], Contrastive Decoding[13]	같은 질의와 검색 문맥에서 C1/C0 주 비교	CAD ON 조건의 alpha=0.5 고정
교정 및 자기검증 RAG	Self-RAG[15], CRAG[16]	검색, 생성과 출력 언어의 문제를 구분하여 설명	관련 연구의 비교 관점으로 참조
RAG 평가	RAGAS[10], RAG survey[19]	근거 충실도, 답변 관련성, 문맥 정밀도와 문맥 재현율 평가	자동 평가 지표와 대응 비교에 사용
```

B (최종 원고):

```text
연구	핵심 접근	본 연구의 비교 질문
HyDE[2]	가상 문서를 임베딩하여 검색	번역·가상 문서 검색을 함께 적용한 조건의 품질 차이
CAD[3]	문맥 포함·제외 로짓의 결합	같은 문맥에서 답변 품질과 실행 시간 차이
SCD[4]	언어별 토큰 로짓의 조정	한국어 문자 비율과 다른 요인과의 상호작용
DPR[11], FiD[12]	밀집 검색과 다중 검색 구간 활용	고정 검색·생성 구조의 구성
Self-RAG[15], CRAG[16]	검색 및 근거 품질의 점검	검색 지표와 답변 지표를 구분하는 평가
RAGAS[10], BEIR[20], MTEB[21]	자동 평가와 검색·임베딩 평가	고정 문서 집합에서 질의별 대응 비교
```

## 58. replace · 원고 330–345 → 316–316

A (기준 원고):

```text
각 질의 ID를 하나의 대상 문서와 연결하였다. 이후 60개 질의 각각에 HyDE, CAD, SCD의 적용 여부를 조합한 8개 조건을 실행하였다. 검색 모델, 재정렬 모델과 생성 모델은 모든 조건에서 동일하게 사용하였다. 각 생성 기록에는 생성 답변, 검색 청크 ID, 재정렬 청크 ID, 최종 검색 문맥, 디코딩 설정과 조건 실행 시간을 저장하였다. 질의 데이터에는 원문 페이지와 정답 근거 구간을 기록하였다.

[표 3-1] 연구 및 실험 요구사항 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T3-1_Requirements | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
요구사항	확인 기준	값
한국어 질의 기반 영문 문서 QA	질의와 대상 문서 연결	60개 질의-문서 쌍
실험 요인	HyDE, CAD, SCD의 ON/OFF	2×2×2, 8개 조건
생성 기록	조건별 생성 기록	480개, 조건별 60개
출력 언어	한국어 문자 비율	SCD ON/OFF 240개 대응쌍
자료 식별	query ID, config_name, 원문 페이지, 정답 근거 구간	60개 질의 메타데이터와 480개 생성 기록
```
```

B (최종 원고):

```text
본 연구는 한국어 질의 60개 각각에 HyDE, CAD, SCD의 적용 여부를 조합한 8조건을 적용하였다. 검색·재정렬·생성 모델은 고정하고, 질의별 검색 결과와 생성 답변, 실행 시간 및 적용 파라미터를 저장하였다. 같은 질의의 결과를 조건별로 연결하여 품질, 출력 언어와 실행 시간을 비교하도록 설계하였다.
```

## 59. replace · 원고 349–349 → 320–320

A (기준 원고):

```text
실험에서는 질의를 입력받아 조건에 맞는 검색 입력을 구성하였다. HyDE OFF 조건에서는 원래의 한국어 질의를 밀집 검색에 사용하였다. HyDE ON 조건에서는 한국어 질의를 영어로 번역한 뒤 가상 문서를 생성하고, 이를 벡터로 변환하여 밀집 검색에 사용하였다. HyDE ON과 OFF 조건 모두 BGE-M3를 사용해 밀집 검색용 벡터를 생성하였다. BM25 검색과 CrossEncoder 재정렬에는 두 조건 모두 원래의 한국어 질의를 사용하였다. 밀집 검색과 BM25의 후보를 weighted RRF로 결합하고 CrossEncoder로 재정렬하였다. 재정렬 순위에 따라 상위 5개 청크를 선택한 뒤 ContextCompressor로 입력 문맥의 길이를 관리하였다. 이 문맥을 생성 모델에 제공하여 답변을 생성하고, 생성 결과를 저장한 뒤 평가하였다.
```

B (최종 원고):

```text
Paper-RAG는 한국어 질의와 대상 문서를 입력받아 밀집·희소 검색, 순위 융합, 재정렬, 답변 생성을 수행한다. HyDE 적용 조건에서는 질의를 영어로 번역하고 가상 문서를 생성하여 BGE-M3 밀집 검색에 사용한다. 미적용 조건에서는 한국어 원질의를 사용한다. BM25 희소 검색과 CrossEncoder 재정렬에는 모든 조건에서 한국어 원질의를 사용한다.
```

## 60. replace · 원고 351–351 → 322–322

A (기준 원고):

```text
답변 생성에는 모든 조건에서 같은 Mi:dm 2.0 Base Instruct를 사용하였다. CAD ON에서는 검색 문맥을 포함했을 때와 제외했을 때 계산한 로짓을 이용해 다음 토큰의 점수를 조정하였다. SCD ON에서는 어휘를 한국어 토큰, 다른 언어의 토큰과 중립 토큰으로 구분하였다. 한국어 토큰과 다른 언어 토큰의 로짓에 각각 정해진 계수를 곱하고, 중립 토큰의 로짓은 유지하였다. 실행이 끝나면 질의, 대상 문서, 실험 조건, 최종 검색 문맥, 생성 답변, 조건 실행 시간과 요인별 메타데이터를 저장하였다. 평가 단계에서는 생성 기록을 불러와 평가값을 계산하고 요인별 대응 차이를 분석하였다.
```

B (최종 원고):

```text
가중 RRF가 두 검색 순위를 결합하고 CrossEncoder가 후보 구간을 재정렬한다. 상위 5개 구간을 문맥 길이 관리 절차에 통과시킨 뒤 생성 모델에 제공한다. CAD와 SCD를 함께 적용할 때에는 문맥 포함·제외 로짓을 CAD 식으로 결합한 후 SCD의 언어별 계수를 적용한다. 최종 답변과 중간 기록은 평가 단계의 입력으로 저장한다.
```

## 61. replace · 원고 353–353 → 324–324

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig3_1_rag_cube.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
## 3.3 완전요인 실험 및 대응 비교 설계 [스타일=절(1.1)]
```

## 62. replace · 원고 355–355 → 326–326

A (기준 원고):

```text
[그림 3-1] HyDE, CAD, SCD를 조합한 RAG-Cube 8개 조건 [스타일=그림제목]
```

B (최종 원고):

```text
HyDE, CAD, SCD를 각각 미적용과 적용의 두 수준으로 설정한 3요인 2수준 완전요인설계(2³ full factorial design)를 사용하였다. 요인 H, C, S는 각각 HyDE, CAD, SCD이며 0은 미적용, 1은 적용을 뜻한다. 같은 질의 60개를 8조건에서 측정하여 480개 생성 결과를 얻었다. 질의가 반복측정 단위이며, 같은 조건에서 난수 시드를 바꾸어 반복 생성한 횟수와 구분한다.
```

## 63. replace · 원고 357–357 → 328–328

A (기준 원고):

```text
## 3.3 상세설계 [스타일=절(1.1)]
```

B (최종 원고):

```text
[표 3-1] HyDE·CAD·SCD의 3요인 2수준 실험 조건 [스타일=표제목]
```

## 64. replace · 원고 359–365 → 330–330

A (기준 원고):

```text
RAG-Cube의 여덟 조건은 HyDE(H), CAD(C), SCD(S)의 ON/OFF 조합으로 구성하였다. 0은 OFF, 1은 ON을 뜻하며, 각 조건을 H0C0S0과 같은 형식으로 표기하였다. 실제 적용 상태는 생성 기록의 `config_name`, `use_hyde`, `use_cad`, `use_scd` 필드로 확인하였다. SCD ON 기록에는 mode=reference_scd, alpha=1.1, beta=0.9, Tstart=5를, CAD ON 기록에는 alpha=0.5를 저장하였다.

[표 3-2] RAG-Cube 8개 조건 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T3-2_RAG-Cube | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T3-1_Factorial_Design | 한글 표로 복사]
```

## 65. replace · 원고 368–376 → 333–341

A (기준 원고):

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

B (최종 원고):

```text
조건	H	C	S
H0C0S0	0	0	0
H0C0S1	0	0	1
H0C1S0	0	1	0
H0C1S1	0	1	1
H1C0S0	1	0	0
H1C0S1	1	0	1
H1C1S0	1	1	0
H1C1S1	1	1	1
```

## 66. replace · 원고 379–379 → 344–344

A (기준 원고):

```text
[표 3-3] 실험 요인별 적용 위치와 비교 단위 [스타일=표제목]
```

B (최종 원고):

```text
HyDE의 단순 비교는 H0C0S0과 H1C0S0, CAD의 단순 비교는 H0C0S0과 H0C1S0을 사용한다. CAD 비교에서는 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥의 동일성을 확인하였다. SCD 주 비교는 H0C0S0–H0C0S1과 H0C1S0–H0C1S1의 동일 문맥 120쌍이다. 전체 비교는 각 질의의 H·C 상태를 맞춘 240쌍이다. SCD 검정에서는 질의별 두 차이 또는 네 차이를 먼저 평균하여 표본 60개를 구성한다.
```

## 67. replace · 원고 381–394 → 346–346

A (기준 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T3-3_Factor_Position | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
요인	적용 위치	주 비교	주 지표
HyDE	검색 표현 확장	CAD와 SCD가 모두 OFF인 60개 대응쌍	RAGAS 품질 지표
CAD	문맥 기반 디코딩	동일 문맥 60쌍(근거 충실도 유효쌍 58개)	근거 충실도, 답변 관련성과 조건 실행 시간
SCD	출력 토큰 로짓 제어	HyDE OFF 동일 문맥 120쌍; 동일 질의의 HyDE와 CAD 상태를 맞춘 전체 240쌍	한국어 문자 비율
```

요인별 대응쌍은 다음과 같이 구성하였다. HyDE 주 비교에서는 동일 질의의 H1C0S0과 H0C0S0을 연결하여 검색 결과의 변화까지 포함한 답변 차이를 측정하였다. CAD 주 비교에서는 동일 질의의 H0C1S0과 H0C0S0을 연결하고, 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥이 모두 동일한지 확인하였다. SCD 주 비교에서는 HyDE를 OFF로 고정하고 CAD 상태가 같은 SCD ON/OFF 기록을 연결하여 120개 대응쌍을 구성하였다. 이 120쌍도 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥이 동일함을 확인하였다. 추가로 동일 질의의 HyDE와 CAD 상태를 각각 맞춘 전체 240개 SCD 대응쌍에서 출력 언어 변화를 분석하였다. 전체 240쌍에는 HyDE ON 조건의 가상 문서 샘플링에 따른 검색 문맥 변화가 포함된다.

평가값은 질의 ID와 실험 조건으로 생성 기록에 연결하였다. 조건별 평균은 각 지표의 평가값이 있는 기록으로 계산하였다. 평균 대응 차이는 같은 질의의 ON 평가값에서 OFF 평가값을 뺀 차이의 평균이다. 질의 단위 부트스트랩으로 대응 차이의 95% 신뢰구간을 추정하였다. 조건별 평균과 대응 비교에는 각각의 유효 표본 수와 비교 조건을 기록하였다.
```

B (최종 원고):

```text
단순 비교는 나머지 요인을 특정 수준으로 고정했을 때의 차이를 측정한다. 주효과는 다른 요인의 수준에 걸친 평균 차이이며, 상호작용은 한 요인의 차이가 다른 요인의 수준에 따라 달라지는 정도를 나타낸다. RAGAS는 SCD 상태에 따라 평가 문맥의 언어가 달라지므로 각 상태 안에서 H×C 효과를 분석한다. 한국어 문자 비율과 조건 실행 시간에는 전체 H×C×S 분석을 적용한다.
```

## 68. replace · 원고 400–400 → 352–352

A (기준 원고):

```text
생성에는 K-intelligence/Midm-2.0-Base-Instruct를 사용하고 최대 생성 토큰 수를 512로 설정하였다. 답변 생성에는 각 단계에서 점수가 가장 높은 토큰을 선택하는 탐욕적 디코딩을 사용하였다.
```

B (최종 원고):

```text
모든 조건은 같은 검색·재정렬·생성 구성으로 실행하였다. 표 4-1은 비교 요인 이외에 공통으로 적용한 설정과 각 기법의 파라미터를 정리한다. 청크 분할과 문맥 길이 관리는 공백으로 분리한 단어 수를 사용하며, 답변 길이 제한은 생성 모델의 토큰 수를 사용한다.
```

## 69. replace · 원고 402–408 → 354–354

A (기준 원고):

```text
일반 텍스트는 Python `split()`의 공백 분리 단위를 기준으로 청크로 나누었다. 청크의 최대 크기는 512단어, 최소 크기는 50단어로 설정하였으며, 같은 텍스트 구간에서 연속으로 나눈 청크는 64단어가 겹치도록 하였다. section 분할 전략에서는 수식, 표와 코드 블록을 나누지 않고 각각 독립된 구조 청크로 보존하였다. BGE-M3 밀집 검색과 BM25 희소 검색은 dense 0.6, BM25 0.4의 weighted RRF(k=60)로 결합하고 cross-encoder/ms-marco-MiniLM-L-6-v2로 재정렬하였다. 같은 CrossEncoder를 모든 조건에 적용하였다. 검색 후보 수와 재정렬 후보 수는 각각 8개, 최종 생성 문맥은 5개로 설정하였다.

ContextCompressor의 문맥 길이 상한은 Python `split()` 기준 3,072개 단어, 추출식 압축 비율은 0.5로 설정하였다. 모듈은 입력 문맥이 상한을 초과할 때 추출식 압축을 수행하고, 상한 이내이면 입력 청크를 그대로 반환한다. 표 4-1에는 모델 구성, 검색 및 생성 설정과 HyDE, CAD, SCD의 파라미터를 정리하였다.

검색 폭 설정은 최종 평가 집합과 분리된 5개 튜닝 질의를 사용하여 사전에 선정하였다. 검색 후보 수, 재정렬 후보 수와 최종 문맥 수를 달리한 세 가지 설정을 비교하였으며, 문맥 재현율 0.95 이상을 충족한 후보 가운데 평균 근거 충실도가 가장 높은 설정을 선택하였다. 선정된 검색 후보 8개, 재정렬 후보 8개, 최종 문맥 5개 설정을 60개 평가 질의의 모든 조건에 적용하였다.

[표 4-1] 실험 실행 환경 [스타일=표제목]
```

B (최종 원고):

```text
[표 4-1] 검색·재정렬·생성 단계의 모델과 공통 실행 설정 [스타일=표제목]
```

## 70. delete · 원고 412–413 → 358–357

A (기준 원고):

```text
[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```

B (최종 원고):

```text
(삭제)
```

## 71. replace · 원고 415–442 → 359–369

A (기준 원고):

```text
구성	생성 기록 기준 값
생성 모델	K-intelligence/Midm-2.0-Base-Instruct
답변 생성 방식	각 단계에서 최종 로짓이 가장 높은 토큰 선택
검색 구성	BGE-M3 밀집 검색 + BM25 희소 검색 + weighted RRF(k=60; 0.6/0.4) + cross-encoder/ms-marco-MiniLM-L-6-v2
검색 후보 수 / 재정렬 후보 수	8 / 8
일반 텍스트 청크 분할	공백 분리 기준 최대 크기 512개 단어 / 중첩 크기 64개 단어 / 최소 크기 50개 단어
문맥 길이 관리	ContextCompressor; 공백 분리 기준 3,072개 단어 초과 시 추출식 압축, 압축 비율 설정 0.5
최종 문맥 수	5
max_new_tokens	512
CAD ON의 α	0.5
SCD	α=1.1, β=0.9, Tstart=5
```

[표 4-2] 고정 Paper-RAG 백본 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T4-2_Backbone | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
단계	고정 구성
입력	한국어 질의와 지정 대상 문서
검색	BGE-M3 밀집 검색 + BM25 희소 검색
결합	weighted Reciprocal Rank Fusion
재정렬	cross-encoder/ms-marco-MiniLM-L-6-v2
문맥 구성	재정렬 상위 5개 청크 선택 → ContextCompressor의 조건부 추출식 압축 → 3,072개 단어 상한에 맞춘 문맥 절단
생성	Mi:dm 2.0 Base Instruct; max_new_tokens=512
요인	HyDE는 밀집 검색 입력에 적용 / CAD와 SCD는 답변 디코딩에 적용
```

B (최종 원고):

```text
구성 단계	사용 모델 또는 방법	주요 설정
밀집 검색	BAAI/bge-m3	후보 8개, 가중치 0.6
희소 검색	BM25	후보 8개, 가중치 0.4
순위 융합	가중 RRF	k=60
재정렬	cross-encoder/ms-marco-MiniLM-L-6-v2	후보 8개, 최종 구간 5개
문서 분할	공백 기준 단어 분할	최대 512단어, 중첩 64단어, 최소 50단어
문맥 길이 관리	ContextCompressor	3,072단어 초과 시 압축, 비율 0.5
답변 생성	K-intelligence/Midm-2.0-Base-Instruct	greedy, 최대 새 토큰 512개
HyDE	영어 번역과 가상 문서 생성	temperature=0.1, top_p=0.9, sampling
CAD	문맥 포함·제외 로짓 결합	α=0.5 고정
SCD	reference_scd	α=1.1, β=0.9, Tstart=5
```

## 72. replace · 원고 447–447 → 374–374

A (기준 원고):

```text
프로그램은 입력부, 검색 표현 구성부, 검색 및 재정렬부, 답변 생성부, 기록 저장부, 분석 및 재현 모듈로 구성하였다. 검색 및 재정렬부는 밀집 검색과 BM25 검색의 결과를 weighted RRF로 결합하고, CrossEncoder 재정렬, 상위 청크 선택과 문맥 길이 관리를 수행한다. 답변 생성부는 조건에 따라 CAD와 SCD를 적용한다. 모든 조건에서 질의 집합과 백본을 고정하고 HyDE(H), CAD(C), SCD(S)의 ON/OFF를 바꾼다.
```

B (최종 원고):

```text
그림 4-1은 입력 질의에서 답변까지의 처리 순서를 나타낸다. HyDE의 가상 문서는 밀집 검색 입력에 사용하고, 답변 생성에는 실제로 검색한 영어 문서 구간을 제공한다. BM25와 재정렬은 한국어 원질의를 유지한다. 검색 결과, 재정렬 결과와 최종 입력 구간을 각각 기록하여 조건 간 검색 입력을 대조할 수 있도록 하였다.
```

## 73. replace · 원고 449–449 → 376–376

A (기준 원고):

```text
검색부는 HyDE의 가상 문서 또는 한국어 원질의를 BGE-M3로 임베딩하여 밀집 검색을 수행하고, 한국어 원질의로 BM25 검색과 CrossEncoder 재정렬을 수행하였다. 생성부에는 최종 검색 문맥과 한국어 원질의를 전달하고, CAD와 SCD 처리기를 조건에 따라 적용하였다. 대응쌍을 구성할 때는 저장된 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥을 대조해 문맥의 동일성을 확인하고, 파라미터 기록으로 각 기법의 적용 상태를 확인하였다.
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig4_1_pipeline.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 74. replace · 원고 451–451 → 378–378

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig4_1_pipeline.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
[그림 4-1] 한국어 질의의 검색·융합·재정렬 및 답변 생성 흐름 [스타일=그림제목]
```

## 75. replace · 원고 453–453 → 380–380

A (기준 원고):

```text
[그림 4-1] 고정 Paper-RAG 백본 실행 흐름 [스타일=그림제목]
```

B (최종 원고):

```text
## 4.3 시스템 구현과 실행 기록 [스타일=절(1.1)]
```

## 76. replace · 원고 455–455 → 382–382

A (기준 원고):

```text
## 4.3 시스템 구현 [스타일=절(1.1)]
```

B (최종 원고):

```text
시스템은 각 생성 기록에 질의 ID, 실험 조건, 검색·재정렬 청크 ID, 최종 검색 문맥, 생성 답변, 실행 시간과 적용 파라미터를 저장한다. 평가 기록은 질의 ID와 조건명을 기준으로 연결한다. 원문 근거와 참조 답변, 검색 문맥 및 생성 답변의 역할을 구분하여 지표별 입력을 구성한다.
```

## 77. replace · 원고 457–457 → 384–384

A (기준 원고):

```text
실험 실행기는 60개 질의–대상 문서 쌍에 각각 8개 조건을 적용하였다. HyDE ON 기록에는 번역 질의와 가상 문서를 저장하였다. CAD와 SCD의 활성 상태 및 파라미터, 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥도 기록하였다. 생성 기록의 주요 필드는 답변, 조건 실행 시간과 디코딩 방식이며, 표 4-4에 정리하였다.
```

B (최종 원고):

```text
조건 실행 시간은 모델과 검색 구성요소의 초기화가 끝난 뒤, 각 질의·조건의 처리를 시작하는 시점부터 답변 생성과 기록용 메타데이터 구성이 끝난 시점까지 측정하였다. HyDE 조건에서는 번역과 가상 문서 생성, 이후 검색·재정렬·문맥 처리·답변 생성 시간이 포함된다. 평가 API 호출과 파일 기록은 측정 구간 이후에 수행한다. 초 단위 측정값은 로그에 소수점 세 자리로 저장되었다. 조건 순서와 초기 질의 처리의 영향은 저장된 실행 기록에 포함되며, 실행 시간은 이 실행 환경에서 관측한 값으로 해석한다.
```

## 78. replace · 원고 459–496 → 386–386

A (기준 원고):

```text
[표 4-3] 실험 조건별 실행 시간 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T4-3_Runtime | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```text
조건	생성 수	평균 조건 실행 시간(초)	조건 실행 시간 중앙값(초)
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
검색	retrieved_chunk_ids(검색 후보 ID), reranked_chunk_ids(재정렬 후 최종 선택 청크 ID), contexts(최종 검색 문맥)
생성	generated_answer, duration_seconds, decoding_mode
재현	generation_model, retrieval backend, context count
```

CAD는 같은 질의와 생성 접두 시퀀스에서 문맥 포함 로짓과 문맥 제외 로짓을 계산한다. SCD는 답변 생성 단계에서 토큰의 로짓을 조정한다. 표 4-3은 검색부터 답변 생성까지의 조건 실행 시간을 정리한 것이며, HyDE ON의 실행 시간에는 질의 번역과 가상 문서 생성 시간이 포함된다. 한국어 문자 비율은 저장된 답변 문자열에서 계산하였다.

[그림삽입: FINALDOCS/FIGURES/fig4_2_artifact_flow.png | 권장폭=본문폭 90% | 정렬=가운데]

[그림 4-2] 생성 기록–평가–대응 분석 흐름 [스타일=그림제목]
```

B (최종 원고):

```text
CAD는 매 생성 단계에서 문맥을 포함한 입력과 제외한 입력의 로짓을 각각 구한다. SCD는 이미 생성한 토큰 수를 기준으로 언어별 로짓 조정을 시작한다. 검색 문맥이 같은 CAD 비교와 HyDE OFF SCD 비교는 저장된 텍스트 및 ID를 직접 대조하였다. 나머지 조합의 문맥 변화는 HyDE 가상 문서 샘플링을 포함한 실제 실행 결과로 기록하였다.
```

## 79. replace · 원고 500–500 → 390–390

A (기준 원고):

```text
## 5.1 실험 대상과 구성 [스타일=절(1.1)]
```

B (최종 원고):

```text
## 5.1 평가 대상 및 질의 구성 [스타일=절(1.1)]
```

## 80. replace · 원고 504–504 → 394–396

A (기준 원고):

```text
네 문서의 평가 질의는 같은 절차로 작성하였다. 연구자는 각 문서의 질문 형식과 범위를 정하기 위해 초기 질문 3개를 작성하였다. 이후 초기 질문의 표현 방식과 범위를 기준으로 LLM이 각 문서의 주요 내용을 요약하도록 하였다. 요약을 15개의 내용 단위로 나누고, 각 단위에서 한국어 평가 질의 1개를 작성하여 문서별 15개, 총 60개를 구성하였다.
```

B (최종 원고):

```text
네 문서의 평가 질의는 같은 절차로 작성하였다. 연구자는 각 문서의 질문 형식과 범위를 정하기 위해 초기 질문 3개를 작성하였다. 이후 초기 질문의 표현 방식과 범위를 기준으로 대규모 언어 모델(Large Language Model, LLM)이 각 문서의 주요 내용을 요약하도록 하였다. 요약을 15개의 내용 단위로 나누고, 각 단위에서 한국어 평가 질의 1개를 작성하여 문서별 15개, 총 60개를 구성하였다.

질의 작성 절차는 연구자의 설명에 근거한다. 문서별 초기 질문 3개와 LLM 요약 대화 원본은 미보관 상태이며, 최종 60개 질의와 대상 문서, 원문 페이지, 정답 근거는 부록 A와 질의 감사 자료에 보존하였다.
```

## 81. replace · 원고 512–512 → 404–404

A (기준 원고):

```text
[표 5-1] 4개 문서별 질의 구성 [스타일=표제목]
```

B (최종 원고):

```text
문서별 15개 구성은 문서별 질의 수를 맞추기 위한 기준이다. 질문 유형의 비중은 원문에서 묻는 내용에 따라 달라진다. 부록 A는 60개 질의의 원문 페이지와 정답 근거를 제시한다. 각 질의의 대상 문서, 원문 근거의 존재, 해당 근거로 질문에 답할 수 있는지를 확인하였다.
```

## 82. replace · 원고 514–514 → 406–406

A (기준 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-1_Dataset | 한글 표로 복사]
```

B (최종 원고):

```text
## 5.2 평가 지표와 해석 기준 [스타일=절(1.1)]
```

## 83. replace · 원고 516–516 → 408–408

A (기준 원고):

```text
[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
근거 충실도는 생성 답변에서 추출한 주장 중 검색 문맥으로 뒷받침되는 주장의 비율이다. 답변 관련성은 생성 답변을 바탕으로 평가 모델이 만든 질문과 원질문 사이의 임베딩 코사인 유사도를 사용한다. 문맥 정밀도는 참조 답변에 유용한 검색 구간이 상위 순위에 배치된 정도를 평균 정밀도로 계산한다. 문맥 재현율은 참조 답변의 주장 중 검색 문맥이 뒷받침하는 비율이다. 네 지표는 값이 높을수록 각 지표가 평가하는 관련성이나 근거 포괄 정도가 높다. 답변 관련성의 코사인 유사도는 이론적으로 −1~1이며, 본 실험에서 저장된 네 품질 지표의 관측값은 0~1 범위였다.
```

## 84. replace · 원고 518–525 → 410–410

A (기준 원고):

```text
```text
대상 문서	질의 수
RAG Survey	15
CAD	15
RAPTOR	15
Mi:dm K 2.5 Pro Technical Report	15
합계	60
```
```

B (최종 원고):

```text
한국어 문자 비율은 한글 문자 수를 한글과 ASCII 영문자 수의 합으로 나눈 값이다. 0.700은 한글 사용 비중 70.0%를 뜻하며, 조건 간 비율 차이 0.218은 21.8%p다. 이 지표는 문자 구성의 측정값이다. 정답과의 의미적 일치와 문장 자연스러움은 별도 평가 대상으로 구분한다. 조건 실행 시간은 초 단위이며 측정 구간은 4.3절에 제시하였다.
```

## 85. replace · 원고 527–527 → 412–412

A (기준 원고):

```text
## 5.2 평가 및 분석 방법 [스타일=절(1.1)]
```

B (최종 원고):

```text
## 5.3 실험 조건 및 평가 절차 [스타일=절(1.1)]
```

## 86. replace · 원고 529–529 → 414–414

A (기준 원고):

```text
질의 ID와 실험 조건을 기준으로 생성 기록과 평가값을 연결하고, 3.3절의 대응 비교 설계에 따라 분석하였다. RAGAS 0.2.15를 사용하였으며, 평가 모델은 OpenAI `gpt-4o`, 답변 관련성 계산에 사용하는 임베딩 모델은 BAAI/bge-m3로 설정하였다. 평가 지표는 근거 충실도, 답변 관련성, 문맥 정밀도와 문맥 재현율의 네 항목이다.
```

B (최종 원고):

```text
평가에는 RAGAS 0.2.15, OpenAI gpt-4o 평가 모델과 BAAI/bge-m3 임베딩 모델을 사용하였다. 실제 사용한 지표는 Faithfulness, AnswerRelevancy, ContextPrecision과 ContextRecall이다. RAGAS 0.2.15에서 ContextPrecision은 참조 답변을 사용하는 LLMContextPrecisionWithReference를 상속한다. 생성 답변을 기준으로 관련 구간을 판정하는 지표와 입력이 구분된다.
```

## 87. replace · 원고 531–531 → 416–416

A (기준 원고):

```text
SCD OFF의 RAGAS 평가에는 생성 기록의 영어 검색 문맥을 사용하였다. SCD ON 조건의 RAGAS 평가에서는 저장된 영어 검색 문맥을 `gpt-4o`로 한국어 번역하여 평가 문맥으로 사용하였다. 생성 답변은 번역하거나 수정하지 않고 저장된 원문을 사용하였다. 문맥 번역은 자동 평가 단계에서 수행하였으며, 답변 생성 모델의 입력은 영어 검색 문맥이었다. SCD OFF와 ON의 RAGAS 결과는 평가 문맥의 언어에 따라 두 블록의 조건별 기술통계로 제시하였다. 출력 언어 변화는 저장된 답변에서 직접 계산한 한국어 문자 비율의 대응 차이로 분석하였다.
```

B (최종 원고):

```text
SCD OFF의 RAGAS 평가에는 답변 생성에 입력한 영어 검색 문맥을 사용하였다. SCD ON의 평가에는 저장된 영어 문맥을 gpt-4o로 한국어 번역한 평가용 문맥을 사용하였다. 답변 생성에는 모든 조건에서 영어 문맥을 입력했고, 평가할 생성 답변은 저장된 원문을 유지하였다. 따라서 품질 결과표에는 평가 문맥 언어를 표시하고, H×C 분석은 각 SCD 상태 안에서 수행하였다.
```

## 88. replace · 원고 533–533 → 418–418

A (기준 원고):

```text
근거 충실도는 ON과 OFF 양쪽에 평가값이 있는 대응쌍으로 분석하였다. CAD 주 비교의 유효 대응쌍은 58개였다.
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig5_0_evaluation_design.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 89. replace · 원고 535–535 → 420–420

A (기준 원고):

```text
HyDE 주 비교는 CAD와 SCD를 모두 OFF로 고정한 60개 질의에서 수행하였다. CAD 주 비교는 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥이 동일한 대응쌍을 사용하여 검색 결과를 고정한 상태의 답변 차이를 측정하였다. SCD의 주 비교에는 HyDE를 OFF로 고정하고 CAD 상태를 맞춘 120개 대응쌍을 사용하였다. 이 대응쌍의 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥은 동일하였다. 추가로 동일 질의의 HyDE와 CAD 상태를 각각 맞춘 전체 240개 SCD 대응쌍에서 8개 조건의 출력 언어 변화를 집계하였다.
```

B (최종 원고):

```text
[그림 5-1] 질의별 생성 기록과 평가값을 연결하는 대응 비교 절차 [스타일=그림제목]
```

## 90. replace · 원고 537–537 → 422–422

A (기준 원고):

```text
최종 답변 생성 설정은 4.1절과 동일하게 유지하였다. HyDE 가상 문서 생성에는 temperature=0.1, top_p=0.9의 샘플링을 사용하였다. 요인별 대응 차이는 같은 질의의 ON 평가값에서 OFF 평가값을 빼서 계산하였다. 대응 차이의 신뢰구간을 계산하기 위해 질의 단위로 200,000회 부트스트랩 재표집을 수행하였다. 난수 시드는 20260713으로 고정하였다. SCD 분석에서는 같은 질의에 속한 2개 또는 4개의 대응쌍을 함께 재표집하였다. RAGAS 지표의 대응 차이가 +0.01을 초과하면 증가, -0.01 미만이면 감소, -0.01 이상 +0.01 이하이면 동률로 집계하였다. 한국어 문자 비율의 대응 차이는 +0.02 초과를 증가, -0.02 미만을 감소, -0.02 이상 +0.02 이하를 동률로 집계하였다. 신뢰구간은 네 대상 문서를 고정했을 때 질의 수준의 변동성을 나타낸다.
```

B (최종 원고):

```text
그림 5-2는 RAPTOR 문서의 질의 ext_raptor_011에 대해 질문, 검색 근거, 생성 답변과 평가값을 연결한 예시다. 참조 답변은 원문 근거에서 구성하며, 검색 문맥과 생성 답변은 해당 조건의 저장 기록을 사용한다. 근거 충실도는 답변의 주장과 검색 문맥을, 문맥 재현율은 참조 답변과 검색 문맥을 대조한다. 각 지표가 사용하는 입력을 구분하여 결과를 해석하였다.
```

## 91. replace · 원고 539–539 → 424–424

A (기준 원고):

```text
개별 대응쌍의 차이와 평균 대응 차이는 다음 식으로 계산한다.
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/EVIDENCE/IO_CASES/E01_normal_qa.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 92. replace · 원고 541–541 → 426–434

A (기준 원고):

```text
[한글 수식 입력기 복붙용 — 개별 대응쌍 차이]
```

B (최종 원고):

```text
[그림 5-2] RAPTOR 질의의 검색 근거, 생성 답변 및 평가 예시 [스타일=그림제목]

## 5.4 통계 분석 방법 [스타일=절(1.1)]

질의 ID와 조건으로 연결한 원정밀도 평가값을 사용하였다. 조건별 기술통계는 평균과 표본표준편차(SD, 분모 n−1)로 제시하였다. RAGAS 평가 셀 1,920개 중 1,915개가 유효했고, 결측 5개는 모두 근거 충실도에서 발생하였다. 결측 질의는 ext_rag_003, ext_rag_005, ext_rag_006이다. H0C1S0에서 003·006, H0C0S1에서 003·005·006이 결측이었다. 검정에 필요한 모든 조건의 값이 있는 질의를 사용하였다. 충실도의 H×C 분석은 SCD OFF n=58, ON n=57이며, 다른 지표는 n=60이다.

RAGAS는 평가 문맥 언어별 H×C 반복측정 ANOVA를, 한국어 문자 비율과 실행 시간은 H×C×S 반복측정 ANOVA를 적용하였다. 모든 요인은 두 수준이므로 효과별 자유도는 (1,n−1)이다. 질의별 직교 요인 대비에서 계산한 t²와 statsmodels AnovaRM의 F값을 대조하였다. 효과크기는 부분 η²로 제시하였다.

RQ1과 RQ2는 3.3절의 조건을 고정한 양측 대응 t-검정으로 분석하고, 평균 대응 점수 차이와 차이의 SD, t, 자유도, p, Cohen dz를 보고하였다. SCD는 같은 질의의 두 CAD 상태 차이를 평균한 주 비교와 네 H·C 상태 차이를 평균한 전체 비교를 사용하였다. 두 비교 모두 검정 단위는 질의 60개다. 개별 차이와 대응 t 통계량은 다음과 같다.
```

## 93. delete · 원고 547–548 → 440–439

A (기준 원고):

```text
[한글 수식 입력기 복붙용 — 대응 평균 변화]

```

B (최종 원고):

```text
(삭제)
```

## 94. replace · 원고 553–553 → 444–446

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig5_0_evaluation_design.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
```text
t = {bar Delta} over {s_Delta / sqrt n}
```
```

## 95. replace · 원고 555–555 → 448–448

A (기준 원고):

```text
[그림 5-1] 60개 질의 평가 및 HyDE, CAD, SCD의 대응 비교 설계 [스타일=그림제목]
```

B (최종 원고):

```text
실행 시간의 CAD×SCD 상호작용을 해석하기 위해, 각 SCD 상태에서 두 HyDE 수준을 평균한 CAD 단순 효과를 추가로 검정하였다. 두 후속 비교에 별도로 Holm 보정을 적용하였다.
```

## 96. replace · 원고 557–557 → 450–450

A (기준 원고):

```text
## 5.3 RAG-Cube 조합별 결과 [스타일=절(1.1)]
```

B (최종 원고):

```text
양측 유의수준은 0.05로 정하였다. 품질 요인 검정 24개를 한 가설군으로, 문자 비율과 실행 시간의 요인 검정은 각각 7개를 가설군으로 정해 Holm 보정을 적용하였다. HyDE와 CAD의 단순 비교는 각각 네 품질 지표를, SCD 문자 비율은 주 비교와 전체 비교 두 검정을 함께 보정하였다. 관측 결과에 기초한 탐색적 통계 분석으로, 보정 전과 후의 p를 함께 제시한다.
```

## 97. replace · 원고 559–559 → 452–452

A (기준 원고):

```text
표 5-2에 SCD OFF와 ON을 평가 프로토콜별로 구분하여 8개 조건의 RAGAS 평균과 한국어 문자 비율을 제시하였다.
```

B (최종 원고):

```text
질의별 대응 차이의 분포와 0·1 경계값, 동률을 확인하고, 질의 단위 부호 순열검정 100,000회(seed=20261015)와 Wilcoxon 부호순위 검정을 민감도 분석으로 수행하였다. 문서 하나씩을 제외한 평균 차이도 계산하였다. 같은 질의의 조건들을 함께 묶어 재표집하거나 평균하여 반복측정 구조를 유지하였다. 질의 단위 부트스트랩 분석 결과는 보조자료에 제시하며, 본문은 평균(SD)와 검정표로 정리하였다.
```

## 98. replace · 원고 561–561 → 454–454

A (기준 원고):

```text
SCD OFF에서는 H1C1S0의 근거 충실도가 0.8599, H1C0S0의 답변 관련성이 0.7633으로 가장 높았다. 문맥 정밀도는 H0C0S0에서 0.7488이었고, 문맥 재현율은 H0C0S0과 H1C0S0에서 0.9333이었다. 한국어 문자 비율은 전체 8개 조건 가운데 H1C0S1에서 0.8072로 가장 높았다.
```

B (최종 원고):

```text
track1_0035의 H1C0S1 답변은 숫자만 반복하여 한글·ASCII 영문자 분모가 0이었다. 본 분석은 기존 코드가 기록한 비율 0을 재현하고, 해당 질의 전체를 제외한 n=59 분석을 추가하였다. 이 규칙은 본문에서 공개하고 민감도 결과와 함께 해석하였다.
```

## 99. replace · 원고 563–563 → 456–456

A (기준 원고):

```text
[표 5-2] SCD 평가 프로토콜별 RAG-Cube 조건 평균 [스타일=표제목]
```

B (최종 원고):

```text
## 5.5 조합별 평가 결과 [스타일=절(1.1)]
```

## 100. replace · 원고 565–565 → 458–458

A (기준 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-2_Config_Scores | 한글 표로 복사]
```

B (최종 원고):

```text
표 5-1은 8조건의 품질 지표와 한국어 문자 비율의 평균(SD)을 제시한다. 품질은 S0의 영어 평가 문맥과 S1의 한국어 번역 평가 문맥을 구분하였다.
```

## 101. replace · 원고 567–567 → 460–460

A (기준 원고):

```text
[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
[표 5-1] 평가 문맥 언어별 8조건의 품질 및 한국어 문자 비율 평균(SD) [스타일=표제목]
```

## 102. replace · 원고 569–569 → 462–462

A (기준 원고):

```text
SCD OFF 블록은 저장된 영어 검색 문맥을 평가 문맥으로 사용한다.
```

B (최종 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-1_Mean_SD | 한글 표로 복사]
```

## 103. replace · 원고 572–576 → 465–473

A (기준 원고):

```text
조건	생성 수	근거 충실도	답변 관련성	문맥 정밀도	문맥 재현율	한국어 문자 비율
H0C0S0	60	0.7906	0.6828	0.7488	0.9333	0.4943
H0C1S0	60	0.8385	0.6755	0.7395	0.9167	0.4877
H1C0S0	60	0.8342	0.7633	0.7145	0.9333	0.5561
H1C1S0	60	0.8599	0.7045	0.7357	0.9000	0.5031
```

B (최종 원고):

```text
조건	충실도	관련성	정밀도	재현율	한국어 비율
H0C0S0	0.791 (0.260)	0.683 (0.282)	0.749 (0.302)	0.933 (0.252)	0.494 (0.265)
H0C0S1	0.787 (0.254)	0.637 (0.296)	0.763 (0.300)	0.900 (0.303)	0.699 (0.329)
H0C1S0	0.839 (0.201)	0.675 (0.261)	0.740 (0.302)	0.917 (0.279)	0.488 (0.245)
H0C1S1	0.777 (0.270)	0.600 (0.321)	0.752 (0.301)	0.850 (0.360)	0.719 (0.218)
H1C0S0	0.834 (0.186)	0.763 (0.209)	0.714 (0.296)	0.933 (0.252)	0.556 (0.213)
H1C0S1	0.822 (0.218)	0.710 (0.272)	0.743 (0.281)	0.900 (0.303)	0.807 (0.200)
H1C1S0	0.860 (0.181)	0.705 (0.248)	0.736 (0.271)	0.900 (0.303)	0.503 (0.229)
H1C1S1	0.831 (0.253)	0.667 (0.286)	0.754 (0.267)	0.917 (0.279)	0.731 (0.209)
```

## 104. replace · 원고 579–579 → 476–480

A (기준 원고):

```text
SCD ON 블록은 각 생성 기록의 영어 검색 문맥을 한국어로 번역한 문맥을 RAGAS 평가에 사용한다.
```

B (최종 원고):

```text
S0는 영어 문맥 평가, S1은 한국어 번역 문맥 평가다. 충실도는 H0C1S0 n=58, H0C0S1 n=57이며, 나머지 조건·지표는 n=60이다. 한국어 비율은 생성 답변에서 계산하였다. 질의별 관측값의 SD와 대응 차이의 SD는 서로 다른 통계량이다.

[표 5-2] 8조건의 질의별 조건 실행 시간 평균과 표준편차 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-2_Runtime_SD | 한글 표로 복사]
```

## 105. replace · 원고 582–586 → 483–491

A (기준 원고):

```text
조건	생성 수	근거 충실도	답변 관련성	문맥 정밀도	문맥 재현율	한국어 문자 비율
H0C0S1	60	0.7869	0.6372	0.7634	0.9000	0.6990
H0C1S1	60	0.7768	0.5996	0.7523	0.8500	0.7195
H1C0S1	60	0.8223	0.7097	0.7426	0.9000	0.8072
H1C1S1	60	0.8313	0.6671	0.7540	0.9167	0.7314
```

B (최종 원고):

```text
조건	평균(초)	SD(초)
H0C0S0	20.792	23.404
H0C0S1	18.898	5.085
H0C1S0	63.867	25.312
H0C1S1	55.159	26.465
H1C0S0	23.440	4.707
H1C0S1	24.892	5.196
H1C1S0	73.532	21.584
H1C1S1	64.125	21.675
```

## 106. replace · 원고 589–589 → 494–494

A (기준 원고):

```text
표의 생성 수는 각 조건에 저장된 생성 기록의 수이다. 근거 충실도 평균에 사용한 유효 평가값은 H0C1S0에서 58개, H0C0S1에서 57개이며 나머지 조건에서는 각각 60개다. 조건별 평균은 SCD OFF에서 영어 문맥으로, SCD ON에서 한국어 번역 문맥으로 평가한 값이다.
```

B (최종 원고):

```text
모든 조건의 실행 시간 표본 수는 60이다. 시간에는 조건별 검색과 답변 생성 과정이 포함되며, HyDE 적용 시 번역과 가상 문서 생성도 포함된다.
```

## 107. replace · 원고 591–591 → 496–496

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig5_1_quality_matrix.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
## 5.6 요인 주효과 및 상호작용 [스타일=절(1.1)]
```

## 108. replace · 원고 593–593 → 498–498

A (기준 원고):

```text
[그림 5-2] 평가 프로토콜별 RAG-Cube 조건 평균 [스타일=그림제목]
```

B (최종 원고):

```text
[표 5-3] SCD OFF 영어 평가 문맥의 품질 지표 H×C 반복측정 ANOVA [스타일=표제목]
```

## 109. replace · 원고 595–613 → 500–500

A (기준 원고):

```text
(a)는 영어 검색 문맥을 사용한 SCD OFF의 RAGAS 평가 결과이고, (b)는 한국어로 번역한 문맥을 사용한 SCD ON의 RAGAS 평가 결과이다.

## 5.4 HyDE 결과 및 해석 [스타일=절(1.1)]

HyDE의 답변 관련성 평균 대응 차이는 +0.0805이고 95% 부트스트랩 신뢰구간은 [+0.0110, +0.1514]이다. 답변 관련성은 29개 질의에서 증가, 15개에서 감소하였으며, 16개는 동률이었다. 근거 충실도 평균 대응 차이는 +0.0436, 95% 신뢰구간은 [-0.0262, +0.1153]이며 증가 24개, 감소 21개, 동률 15개였다. 문맥 정밀도의 평균 대응 차이는 -0.0343이었고, 문맥 재현율의 평균 대응 차이는 0.0000이었다.

HyDE 비교에는 질의 번역, 가상 문서 생성과 검색 문맥 선택의 변화가 함께 포함된다. 문서별 결과와 질문 유형별 결과는 부록 B에 제시하였다.

그림 5-3은 HyDE 적용 전후의 검색 문맥과 생성 답변을 비교한 사례다. 질의 `ext_midm_004`의 H0C0S0과 H1C0S0은 같은 질문을 사용하였으며, 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥은 서로 달랐다. 답변 관련성은 0.0000에서 0.8531로, 문맥 재현율은 0.0000에서 1.0000으로 변하였다. HyDE ON 답변은 한국어 멀티턴 대화 데이터의 세 설계 차원으로 interaction structure, topic and task, persona를 제시하였다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png | 권장폭=본문폭 95% | 정렬=가운데]

[그림 5-3] HyDE 적용에 따른 검색 문맥 및 답변 변화 사례 [스타일=그림제목]

[표 5-3] HyDE 주 비교 결과 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-3_HyDE | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-3_Quality_S0 | 한글 표로 복사]
```

## 110. replace · 원고 616–620 → 503–515

A (기준 원고):

```text
지표	평균 대응 차이 ON−OFF	95% 신뢰구간	증가	감소	동률	n
근거 충실도	+0.0436	[-0.0262, +0.1153]	24	21	15	60
답변 관련성	+0.0805	[+0.0110, +0.1514]	29	15	16	60
문맥 정밀도	-0.0343	[-0.0932, +0.0247]	17	23	20	60
문맥 재현율	0	[-0.1000, +0.1000]	4	4	52	60
```

B (최종 원고):

```text
지표	효과	df	F	p	보정 p	부분 η²
근거 충실도	H	1, 57	1.162	0.286	1.000	0.020
근거 충실도	C	1, 57	1.034	0.313	1.000	0.018
근거 충실도	H×C	1, 57	0.073	0.789	1.000	0.001
답변 관련성	H	1, 59	2.844	0.097	1.000	0.046
답변 관련성	C	1, 59	1.498	0.226	1.000	0.025
답변 관련성	H×C	1, 59	1.185	0.281	1.000	0.020
문맥 정밀도	H	1, 59	0.496	0.484	1.000	0.008
문맥 정밀도	C	1, 59	0.226	0.636	1.000	0.004
문맥 정밀도	H×C	1, 59	1.567	0.216	1.000	0.026
문맥 재현율	H	1, 59	0.039	0.843	1.000	0.001
문맥 재현율	C	1, 59	1.000	0.321	1.000	0.017
문맥 재현율	H×C	1, 59	0.109	0.742	1.000	0.002
```

## 111. replace · 원고 623–623 → 518–518

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig5_2_primary_forest.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
[표 5-4] SCD ON 한국어 번역 평가 문맥의 품질 지표 H×C 반복측정 ANOVA [스타일=표제목]
```

## 112. replace · 원고 625–645 → 520–520

A (기준 원고):

```text
[그림 5-4] HyDE와 CAD의 주 대응 비교 [스타일=그림제목]

점은 ON−OFF 평균 차이, 선은 95% 부트스트랩 신뢰구간이다.

## 5.5 CAD 결과 및 해석 [스타일=절(1.1)]

CAD는 같은 질의와 검색 문맥에서 OFF와 ON의 답변을 비교하였다. 근거 충실도의 평균 대응 차이는 양쪽 평가값이 있는 58쌍에서 +0.0288이었고, 95% 신뢰구간은 [-0.0367, +0.0934]로 0을 포함하였다. 근거 충실도는 58개 유효 대응쌍 중 21쌍에서 증가하고 24쌍에서 감소하였으며, 13쌍은 동률이었다. 답변 관련성의 평균 대응 차이는 60쌍에서 -0.0073이었고, 신뢰구간은 [-0.0855, +0.0719]였다. 답변 관련성은 60개 대응쌍 중 19쌍에서 증가하고 32쌍에서 감소하였으며, 9쌍은 동률이었다.

검색 문맥이 동일한 CAD 대응쌍에서도 문맥 정밀도는 60쌍 중 8쌍, 문맥 재현율은 60쌍 중 1쌍에서 자동 평가값이 달랐다. 이 차이는 자동 평가의 변동을 확인하기 위한 진단값으로 기록하였다. 표 4-3의 H0S0, H0S1, H1S0, H1S1 조건군에서 CAD 적용 전후 평균 조건 실행 시간은 각각 20.792초에서 63.867초, 18.898초에서 55.159초, 23.440초에서 73.532초, 24.892초에서 64.125초로 증가하였다.

그림 5-5는 같은 검색 문맥에서 CAD 적용 전후의 근거 충실도를 비교한 사례다. 질의 `ext_midm_001`은 Mi:dm K 2.5 Pro의 학습 데이터 확보 경로 세 가지를 묻는다. CAD OFF와 ON의 검색 청크 ID, 재정렬 청크 ID와 검색 문맥은 모두 같다. 두 답변은 licensed proprietary datasets, commercial-use public datasets, in-house synthetic data의 세 경로를 제시하였다. 저장된 근거 충실도는 OFF에서 0.8333, ON에서 1.0000이었고 답변 관련성은 각각 0.8261과 0.8124였다. 근거 충실도가 감소한 추가 사례는 부록 B의 그림 B-1에 제시하였다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]

[그림 5-5] 동일 검색 문맥에서 CAD 적용 전후 답변 비교 사례 [스타일=그림제목]

[표 5-4] CAD 동일 문맥 주 비교 결과 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-4_CAD | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-4_Quality_S1 | 한글 표로 복사]
```

## 113. replace · 원고 648–650 → 523–535

A (기준 원고):

```text
지표	평균 대응 차이 ON−OFF	95% 신뢰구간	증가	감소	동률	n
근거 충실도	+0.0288	[-0.0367, +0.0934]	21	24	13	58
답변 관련성	-0.0073	[-0.0855, +0.0719]	19	32	9	60
```

B (최종 원고):

```text
지표	효과	df	F	p	보정 p	부분 η²
근거 충실도	H	1, 56	2.434	0.124	1.000	0.042
근거 충실도	C	1, 56	0.137	0.713	1.000	0.002
근거 충실도	H×C	1, 56	0.188	0.666	1.000	0.003
답변 관련성	H	1, 59	3.012	0.088	1.000	0.049
답변 관련성	C	1, 59	2.628	0.110	1.000	0.043
답변 관련성	H×C	1, 59	0.011	0.917	1.000	0.000
문맥 정밀도	H	1, 59	0.158	0.693	1.000	0.003
문맥 정밀도	C	1, 59	0.000	0.994	1.000	0.000
문맥 정밀도	H×C	1, 59	0.823	0.368	1.000	0.014
문맥 재현율	H	1, 59	0.529	0.470	1.000	0.009
문맥 재현율	C	1, 59	0.396	0.532	1.000	0.007
문맥 재현율	H×C	1, 59	2.744	0.103	1.000	0.044
```

## 114. replace · 원고 653–653 → 538–538

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig5_10_runtime.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
품질 요인 검정 24개에 Holm 보정을 적용한 결과는 모두 0.05 이상이었다. SCD OFF 답변 관련성의 HyDE 주효과는 F(1,59)=2.844, 보정 전 p=0.097이었다. 이 값은 CAD OFF에 고정한 HyDE 단순 비교와 다른 가설을 검정한다. 품질 요인 효과의 크기와 방향은 표의 F와 부분 η², 조건 평균을 함께 사용해 해석하였다.
```

## 115. replace · 원고 655–655 → 540–540

A (기준 원고):

```text
[그림 5-6] RAG-Cube 조건별 평균 실행 시간 [스타일=그림제목]
```

B (최종 원고):

```text
[표 5-5] 한국어 문자 비율의 H×C×S 반복측정 ANOVA [스타일=표제목]
```

## 116. replace · 원고 657–681 → 542–542

A (기준 원고):

```text
## 5.6 SCD 출력 언어 결과 및 해석 [스타일=절(1.1)]

SCD를 적용한 답변과 적용하지 않은 답변의 한국어 문자 비율을 비교하였다. 두 조건 모두 생성 모델에는 영어 검색 문맥을 입력하였다. HyDE OFF에서 검색 청크 ID, 재정렬 청크 ID와 검색 문맥이 같은 120쌍의 평균 대응 차이는 +0.2182였고, 95% 신뢰구간은 [+0.1880, +0.2487]이었다. 동일 질의에서 HyDE와 CAD의 ON/OFF 상태를 맞춘 전체 240개 SCD 대응쌍의 평균 대응 차이는 +0.2289였고, 95% 신뢰구간은 [+0.2051, +0.2532]이었다. 전체 240쌍에서 +0.02를 초과한 증가는 219개, -0.02 미만의 감소는 10개, -0.02 이상 +0.02 이하의 동률은 11개였다.

SCD 적용에 따른 한국어 문자 비율의 평균 변화는 H0C0 조건에서 +0.2047, H0C1 조건에서 +0.2317, H1C0 조건에서 +0.2511, H1C1 조건에서 +0.2283이었다. HyDE OFF의 H0C0과 H0C1 조건군에서는 SCD 적용 전후에 동일한 검색 문맥을 사용하였다. H1의 두 조건군에는 조건마다 독립 생성한 HyDE 가상 문서에 따른 검색 문맥 변화가 포함된다.

답변에 포함된 영어 논문 제목, 모델명과 데이터셋명의 ASCII 영문자도 한국어 문자 비율의 분모에 포함하였다.

그림 5-7은 SCD OFF에서 영어 중심 답변이 생성된 사례다. 한국어 질문과 영어 검색 근거가 주어졌으며, 생성 답변의 한국어 문자 비율은 0.0000이었다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E02_language_drift.png | 권장폭=본문폭 95% | 정렬=가운데]

[그림 5-7] SCD OFF 조건의 출력 언어 이탈 사례 [스타일=그림제목]

그림 5-8은 같은 검색 문맥에서 SCD 적용 전후의 답변 언어를 비교한다. 질의 `ext_midm_005`의 H1C0S0과 H1C0S1은 검색 청크 ID, 재정렬 청크 ID와 검색 문맥이 같고 SCD 상태만 다르다. 한국어 문자 비율은 0.0000에서 0.7713으로 증가하였으며, SCD ON 답변은 한국어 중심으로 생성되었다.

[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png | 권장폭=본문폭 95% | 정렬=가운데]

[그림 5-8] 동일 검색 문맥에서 SCD 적용 전후 출력 언어 변화 사례 [스타일=그림제목]

[표 5-5] SCD 조합별 한국어 문자 비율 변화 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-5_SCD_Config | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-5_Factorial | 한글 표로 복사]
```

## 117. replace · 원고 684–688 → 545–552

A (기준 원고):

```text
SCD OFF	SCD ON	쌍 수	평균 대응 차이	신뢰구간 하한	신뢰구간 상한	증가	감소	동률
H0C0S0	H0C0S1	60	+0.2047	+0.1566	+0.2512	51	4	5
H0C1S0	H0C1S1	60	+0.2317	+0.1874	+0.2786	54	2	4
H1C0S0	H1C0S1	60	+0.2511	+0.1938	+0.3078	57	1	2
H1C1S0	H1C1S1	60	+0.2283	+0.1832	+0.2762	57	3	0
```

B (최종 원고):

```text
효과	df	F	p	보정 p	부분 η²
H	1, 59	2.924	0.093	0.370	0.047
C	1, 59	3.365	0.072	0.358	0.054
S	1, 59	341.302	<0.001	<0.001	0.853
H×C	1, 59	4.417	0.040	0.239	0.070
H×S	1, 59	0.771	0.384	0.940	0.013
C×S	1, 59	0.006	0.939	0.940	0.000
H×C×S	1, 59	1.035	0.313	0.940	0.017
```

## 118. replace · 원고 691–691 → 555–555

A (기준 원고):

```text
[표 5-6] SCD 대응쌍 분석 요약 [스타일=표제목]
```

B (최종 원고):

```text
[표 5-6] 조건 실행 시간의 H×C×S 반복측정 ANOVA [스타일=표제목]
```

## 119. replace · 원고 693–695 → 557–557

A (기준 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-6_SCD_Paired | 한글 표로 복사]

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-6_Factorial | 한글 표로 복사]
```

## 120. replace · 원고 698–700 → 560–567

A (기준 원고):

```text
비교	쌍 수	한국어 문자 비율 평균 대응 차이	95% 신뢰구간	증가 / 감소 / 동률
전체 SCD ON/OFF 대응	240	+0.2289	[+0.2051, +0.2532]	219 / 10 / 11
HyDE OFF 동일 문맥	120	+0.2182	[+0.1880, +0.2487]	105 / 6 / 9
```

B (최종 원고):

```text
효과	df	F	p	보정 p	부분 η²
H	1, 59	16.362	<0.001	<0.001	0.217
C	1, 59	423.765	<0.001	<0.001	0.878
S	1, 59	6.097	0.016	0.066	0.094
H×C	1, 59	2.262	0.138	0.414	0.037
H×S	1, 59	0.401	0.529	0.976	0.007
C×S	1, 59	12.080	<0.001	0.005	0.170
H×C×S	1, 59	0.487	0.488	0.976	0.008
```

## 121. replace · 원고 703–703 → 570–570

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig5_3_scd_language.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
한국어 문자 비율은 SCD 주효과가 유의하였다(F(1,59)=341.302, 보정 p<0.001). H×C 상호작용의 보정 전 p는 0.040, 보정 후 p는 0.239였다. 실행 시간에서는 HyDE와 CAD 주효과 및 CAD×SCD 상호작용이 보정 후 유의하였다. SCD의 실행 시간 주효과는 보정 전 p=0.016, 보정 후 p=0.066이었다.
```

## 122. replace · 원고 705–705 → 572–572

A (기준 원고):

```text
[그림 5-9] SCD의 한국어 문자 비율 변화 [스타일=그림제목]
```

B (최종 원고):

```text
실행 시간의 후속 비교에서 CAD 적용에 따른 질의별 평균 차이는 SCD OFF에서 +46.583초(SD 18.937), t(59)=19.054, dz=2.460이었다. SCD ON에서는 +37.747초(SD 18.405), t(59)=15.886, dz=2.051이었다. 두 비교 모두 보정 p<0.001이었다. CAD의 시간 증가는 두 SCD 수준에서 관찰되었고, 그 평균 차이는 SCD ON에서 더 작았다.
```

## 123. replace · 원고 707–707 → 574–574

A (기준 원고):

```text
H0 조건군은 동일 검색 문맥 주 비교이며, H1 조건군은 조건별 HyDE 샘플링을 포함한다. 오차막대는 95% 부트스트랩 신뢰구간이다.
```

B (최종 원고):

```text
## 5.7 연구 질문별 대응 비교 [스타일=절(1.1)]
```

## 124. replace · 원고 709–709 → 576–576

A (기준 원고):

```text
## 5.7 대표 입출력 및 요구사항별 실행 결과 [스타일=절(1.1)]
```

B (최종 원고):

```text
[표 5-7] HyDE·CAD 단순 비교의 품질 대응 점수 차이와 검정 결과 [스타일=표제목]
```

## 125. replace · 원고 711–711 → 578–578

A (기준 원고):

```text
그림 5-10은 질문, 검색 근거, 생성 답변과 RAGAS 평가값을 함께 제시한 입출력 사례다.
```

B (최종 원고):

```text
[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-7_Paired_Quality | 한글 표로 복사]
```

## 126. replace · 원고 713–713 → 580–590

A (기준 원고):

```text
질의 `ext_raptor_011`은 RAPTOR의 계층적 검색이 DPR보다 주제형 질문과 멀티홉 질문에 유리한 이유를 묻는다. H0C0S0 답변의 근거 충실도는 1.0000, 답변 관련성은 0.9365였으며, 문맥 정밀도와 문맥 재현율은 각각 1.0000이었다.
```

B (최종 원고):

```text
```text
요인·지표	n	평균 차이(SD)	t(df)	p	보정 p	dz
HyDE 근거 충실도	60	0.044 (0.281)	1.200 (59)	0.235	0.705	0.155
HyDE 답변 관련성	60	0.080 (0.279)	2.236 (59)	0.029	0.117	0.289
HyDE 문맥 정밀도	60	-0.034 (0.234)	-1.134 (59)	0.261	0.705	-0.146
HyDE 문맥 재현율	60	0.000 (0.368)	0.000 (59)	1.000	1.000	0.000
CAD 근거 충실도	58	0.029 (0.255)	0.862 (57)	0.393	1.000	0.113
CAD 답변 관련성	60	-0.007 (0.313)	-0.181 (59)	0.857	1.000	-0.023
CAD 문맥 정밀도	60	-0.009 (0.077)	-0.930 (59)	0.356	1.000	-0.120
CAD 문맥 재현율	60	-0.017 (0.129)	-1.000 (59)	0.321	1.000	-0.129
```
```

## 127. replace · 원고 715–715 → 592–592

A (기준 원고):

```text
[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E01_normal_qa.png | 권장폭=본문폭 95% | 정렬=가운데]
```

B (최종 원고):

```text
HyDE 비교는 C0S0, CAD 비교는 H0S0에 고정하였다. 평균 차이는 적용 조건 점수에서 미적용 조건 점수를 뺀 값이다. SD는 질의별 차이의 표본표준편차이며, 각 요인의 네 품질 검정에 Holm 보정을 적용하였다.
```

## 128. replace · 원고 717–717 → 594–594

A (기준 원고):

```text
[그림 5-10] 질문, 검색 근거, 생성 답변과 평가 결과 예시 [스타일=그림제목]
```

B (최종 원고):

```text
HyDE의 답변 관련성은 평균 대응 점수 차이 +0.080점, 차이 SD 0.279였다. 보정 전 p=0.029, 보정 후 p=0.117로, 네 품질 지표를 함께 고려한 검정의 보정 p는 유의수준 0.05보다 높았다. HyDE 조건은 번역과 가상 문서 생성에 따른 밀집 검색 입력의 변화를 함께 포함한다. 검색 경로가 달라진 실제 사례는 부록 B에 제시하였다.
```

## 129. replace · 원고 719–719 → 596–608

A (기준 원고):

```text
부록 B의 그림 B-1에는 CAD의 근거 충실도가 감소한 사례를 추가하였다.
```

B (최종 원고):

```text
CAD의 근거 충실도 평균 대응 점수 차이는 +0.029점, 차이 SD 0.255였고, t(57)=0.862, 보정 전 p=0.393이었다. 질의별로 증가와 감소가 함께 나타났다. 같은 검색 문맥의 문맥 정밀도 8/60쌍과 문맥 재현율 1/60쌍에서도 평가값 차이가 기록되었다. 평가 입력 대조와 평가자 변동성의 해석은 5.9절에서 다룬다. CAD의 추가 로짓 계산과 실행 시간 증가는 함께 관찰되었다.

[표 5-8] SCD 한국어 문자 비율의 질의별 평균 대응 차이(%p)와 검정 결과 [스타일=표제목]

[표삽입: FINALDOCS/TABLES/TABLES_60Q.xlsx | Sheet=T5-8_Paired_Language | 한글 표로 복사]

```text
요인·지표	n	평균 차이(SD)	t(df)	p	보정 p	dz
HyDE OFF 동일 문맥	60	21.822 (12.117)	13.951 (59)	<0.001	<0.001	1.801
전체 H·C 상태 일치	60	22.894 (9.599)	18.474 (59)	<0.001	<0.001	2.385
```

주 비교는 120쌍, 전체 비교는 240쌍을 질의별로 평균한 결과이며 각각 검정 표본은 60개다. 한국어 문자 비율의 평균 차이는 주 비교 +21.822%p, 전체 비교 +22.894%p였고, 두 검정 모두 보정 p<0.001이었다. 두 CAD 상태의 차이를 질의마다 평균해도 SCD 적용 후 한글 사용 비중의 증가가 확인되었다.
```

## 130. replace · 원고 723–723 → 612–612

A (기준 원고):

```text
HyDE 적용 후 답변 관련성의 평균 대응 차이는 +0.0805였으며, 문맥 정밀도는 -0.0343, 문맥 재현율은 0.0000이었다. 그림 5-3의 사례에서도 검색 청크 ID, 재정렬 청크 ID와 최종 검색 문맥이 달라졌다. 따라서 HyDE의 결과는 질의 번역과 가상 문서 생성에 따른 검색 경로의 변화를 포함하여 해석하였다.
```

B (최종 원고):

```text
검색 입력을 바꾸는 HyDE, 생성 로짓에 개입하는 CAD와 출력 언어를 조정하는 SCD는 서로 다른 평가 항목에서 결과를 보였다. HyDE 답변 관련성의 단순 비교에서는 양의 평균 차이가 관찰되었으며, 네 품질 지표 보정 후 p는 0.117이었다. CAD는 평균 충실도 차이에 비해 질의별 차이의 SD가 컸다. 따라서 품질 지표의 평균 순위만으로 기법의 적용 효과를 판단하기보다 대응 차이와 검정을 함께 읽어야 한다.
```

## 131. replace · 원고 725–725 → 614–614

A (기준 원고):

```text
CAD 동일 문맥 비교에서 근거 충실도의 평균 대응 차이는 +0.0288, 답변 관련성의 평균 대응 차이는 -0.0073이었다. 두 지표의 95% 부트스트랩 신뢰구간은 모두 0을 포함하였다. CAD ON은 같은 검색 문맥을 유지하면서 문맥을 제외한 입력의 로짓을 추가로 계산하였다.
```

B (최종 원고):

```text
SCD의 한국어 문자 비율 증가는 단순 비교와 전체 요인 분석에서 일관되었다. 이 결과는 문자 사용 비중에 관한 관측이다. 자연스러운 한국어 문장과 원문 근거의 정확한 전달은 별도의 질적 검토가 필요하다. CAD×SCD 실행 시간 상호작용은 두 기법을 함께 적용했을 때의 비용이 개별 주효과만으로 설명되는 정도와 다름을 보여준다. 실행 시간을 비교할 때에는 답변 길이와 저장된 실행 순서의 영향도 고려해야 한다.
```

## 132. replace · 원고 727–727 → 616–616

A (기준 원고):

```text
SCD의 한국어 문자 비율 평균 대응 차이는 HyDE OFF 동일 문맥 120개 대응쌍에서 +0.2182였고, HyDE와 CAD 상태를 맞춘 전체 240개 대응쌍에서 +0.2289였다.
```

B (최종 원고):

```text
문서별·질문 유형별 평균 대응 차이와 SD는 부록 B에 제시하였다. 문서 하나씩을 제외한 분석과 질의 단위 순열검정으로 특정 문서와 경계값이 결과에 미치는 영향을 확인하였다. 적용 조건의 선택은 필요한 출력 언어와 허용 가능한 실행 시간을 정한 뒤, 그 조건의 품질 결과와 함께 판단할 수 있다.
```

## 133. replace · 원고 729–729 → 618–618

A (기준 원고):

```text
표 5-2의 조합별 평균은 8개 실험 조건 각각에서 계산한 지표별 평균이다. 표 5-3~5-6의 요인별 대응 차이는 동일한 질의에서 특정 기법을 적용했을 때와 적용하지 않았을 때의 평가값 차이를 나타낸다. 조건 선택에는 답변 관련성, 근거 충실도, 조건 실행 시간과 한국어 문자 비율 중 적용 목적에 맞는 지표를 사용한다.
```

B (최종 원고):

```text
HyDE 답변 관련성 차이의 Shapiro–Wilk 검정은 p<0.001이었다. 평균 차이를 검정하는 질의 단위 부호 순열검정의 Holm 보정 p는 0.112였고, 순위에 근거한 위치 차이를 다루는 Wilcoxon 검정의 보정 p는 0.012였다. 검정이 사용하는 정보와 가설에 따라 결과가 달랐으며, 본문의 평균 차이 해석에는 대응 t-검정과 부호 순열 결과를 함께 사용하였다. SCD의 두 문자 비율 비교는 부호 순열과 Wilcoxon 검정에서도 보정 p<0.001이었다.
```

## 134. replace · 원고 731–731 → 620–620

A (기준 원고):

```text
그림 5-11에는 HyDE와 CAD의 근거 충실도 및 답변 관련성 평균 대응 차이를 제시하였다. HyDE의 결과는 CAD와 SCD의 설정별로, CAD의 결과는 HyDE와 SCD의 설정별로 구분하였다. 답변 관련성에서 HyDE의 평균 대응 차이는 C0S0에서 +0.0805, C1S0에서 +0.0290, C0S1에서 +0.0725, C1S1에서 +0.0675였다. CAD의 답변 관련성 평균 대응 차이는 H0S0에서 -0.0073, H1S0에서 -0.0588, H0S1에서 -0.0377, H1S1에서 -0.0427이었다. HyDE ON에서는 각 실험 조건마다 temperature=0.1, top_p=0.9로 가상 문서를 독립 생성하였다. 따라서 H1 조건의 CAD 비교와 SCD 비교에는 디코딩 설정에 따른 답변 변화와 HyDE 샘플링에 따른 검색 문맥 변화가 함께 포함된다.
```

B (최종 원고):

```text
문서 하나씩을 제외했을 때 HyDE 답변 관련성 평균 차이는 +0.064~+0.108점, CAD 충실도는 +0.013~+0.049점, SCD 주 비교 문자 비율은 +21.2~+22.8%p였다. 숫자 반복 답변의 질의를 제외한 n=59 분석에서도 SCD 문자 비율 주효과는 F(1,58)=332.971, Holm 보정 p<0.001이었다. 전체 기술통계와 민감도 검정은 동일한 저장 기록에서 재계산하였다.
```

## 135. replace · 원고 733–733 → 622–622

A (기준 원고):

```text
부록 B는 문서별 및 질문 유형별 대응 차이를 제시한다. 각 문서의 질의 수는 15개다. 질문 유형별 질의 수는 사실 및 정의 8개, 방법 및 절차 29개, 결과 및 비교 20개, 목적 및 기여 3개이며, 각 결과는 해당 표본 수를 기준으로 탐색적으로 해석하였다.
```

B (최종 원고):

```text
## 5.9 평가 범위와 후속 검증 [스타일=절(1.1)]
```

## 136. replace · 원고 735–735 → 624–624

A (기준 원고):

```text
[그림삽입: FINALDOCS/FIGURES/fig5_9_hyde_cad_strata.png | 권장폭=본문폭 90% | 정렬=가운데]
```

B (최종 원고):

```text
평가 문서는 네 종류이며 각 문서에서 구성한 질의 15개가 분석에 사용되었다. 반복측정 검정은 이 문서 집합의 질의별 변동을 다룬다. 문서 수가 네 개이므로 문서 집단 전체에 대한 추론에는 추가 문서가 필요하다. HyDE 가상 문서는 샘플링으로 생성되었고, 각 질의·조건의 생성은 한 번씩 수행하였다. 생성 시드 간 변동은 별도 반복 실험으로 확인할 항목이다.
```

## 137. replace · 원고 737–737 → 626–626

A (기준 원고):

```text
[그림 5-11] HyDE와 CAD의 조건군별 근거 충실도 및 답변 관련성 평균 대응 차이 [스타일=그림제목]
```

B (최종 원고):

```text
HyDE ON에서는 조건마다 가상 문서를 샘플링하므로 검색 문맥이 달라질 수 있다. H1에서의 CAD·SCD 비교와 전체 요인 효과에는 이러한 검색 차이가 함께 포함된다. 이를 실제 조합 조건에서 관측된 결과로 해석하였다.
```

## 138. replace · 원고 739–743 → 628–628

A (기준 원고):

```text
## 5.9 실험 범위와 해석 기준 [스타일=절(1.1)]

영어로 작성된 학술 및 기술 문서 4개를 대상으로 문서별 한국어 평가 질의 15개씩, 총 60개를 구성하였다. 각 질의의 원문 페이지와 정답 근거 구간을 확인하였다. 답변 생성에는 K-intelligence/Midm-2.0-Base-Instruct를 사용하였으며, CAD ON 조건에만 α=0.5를 적용하였다.

이 실험의 HyDE 비교에는 질의 번역, 가상 문서 생성과 밀집 검색 입력의 변화가 포함된다. 가상 문서는 temperature=0.1, top_p=0.9로 생성하였고, 비교에는 저장된 검색 기록과 생성 기록을 사용하였다. SCD의 RAGAS 결과는 SCD ON의 한국어 번역 문맥과 SCD OFF의 영어 문맥을 사용하는 두 평가 프로토콜의 조건별 기술통계이다. 출력 언어의 변화는 답변 원문의 한국어 문자 비율로 비교하였다.
```

B (최종 원고):

```text
RAGAS 품질은 SCD 상태마다 평가 문맥 언어가 달라 각 프로토콜 안에서 분석하였다. 모든 조건에 같은 평가 문맥 언어를 적용한 품질 비교는 추가 평가 과제다. CAD의 H0S0 비교에서 질문·참조답변·평가 문맥은 60쌍 모두 같았다. 문맥 정밀도와 재현율이 달라진 저장 결과는 같은 평가 입력에 대한 결과 변동을 살펴보는 진단 자료이며, 반복 평가 분산의 크기는 같은 입력의 추가 평가로 측정할 수 있다. 근거 충실도 결측과 숫자 반복 답변은 원자료에 남기고 처리 규칙과 분석 표본을 공개하였다.
```

## 139. replace · 원고 747–747 → 632–632

A (기준 원고):

```text
본 연구에서는 영어 문서 4개를 대상으로 한국어 평가 질의 60개를 구성하고, HyDE, CAD, SCD의 적용 여부에 따른 총 480개의 생성 결과를 비교하였다.
```

B (최종 원고):

```text
본 연구는 한국어 질의로 영어 학술·기술 문서를 검색하는 고정 RAG 파이프라인에서 HyDE, CAD, SCD의 8개 조합을 비교하였다. 질의 60개와 생성 기록 480개를 이용하여 품질, 한국어 문자 비율과 조건 실행 시간을 분석하였다.
```

## 140. replace · 원고 749–749 → 634–634

A (기준 원고):

```text
## 6.1 연구 질문별 최종 답 [스타일=절(1.1)]
```

B (최종 원고):

```text
## 6.1 연구 질문별 결과 [스타일=절(1.1)]
```

## 141. replace · 원고 751–751 → 636–636

A (기준 원고):

```text
첫 번째 연구 질문에서는 CAD와 SCD가 OFF인 대응쌍을 비교하였다. HyDE의 답변 관련성 평균 대응 차이는 +0.0805였고, 95% 부트스트랩 신뢰구간은 [+0.0110, +0.1514]였다. 근거 충실도, 문맥 정밀도와 문맥 재현율의 평균 대응 차이는 각각 +0.0436, -0.0343, 0.0000이었다.
```

B (최종 원고):

```text
RQ1에서 HyDE의 답변 관련성 평균 대응 점수 차이는 +0.080점이었다. CAD와 SCD를 미적용한 비교의 보정 전 p는 0.029였고, 네 품질 지표를 함께 보정한 p는 0.117이었다. RQ2에서 같은 문맥의 CAD 충실도 차이는 +0.029점, 보정 전 p=0.393이었다. 품질 검정에서는 양의 평균 차이와 통계적 유의성을 구분하였다.
```

## 142. replace · 원고 753–753 → 638–638

A (기준 원고):

```text
두 번째 연구 질문에서는 검색 문맥을 고정하고 CAD를 비교하였다. 근거 충실도의 평균 대응 차이는 58개 유효쌍에서 +0.0288이었고, 95% 신뢰구간은 [-0.0367, +0.0934]였다. 답변 관련성의 평균 대응 차이는 60쌍에서 -0.0073이었고 신뢰구간은 0을 포함하였다. 네 대응 조건군에서 CAD ON의 평균 조건 실행 시간은 OFF보다 길었다.
```

B (최종 원고):

```text
RQ3에서 HyDE OFF 동일 문맥의 SCD 한국어 문자 비율 차이는 +21.8%p였으며 보정 p<0.001이었다. 질의별로 네 H·C 상태를 평균한 전체 비교의 차이는 +22.9%p였고 보정 p<0.001이었다. SCD는 본 실험의 한국어 문자 사용 비중을 높였다.
```

## 143. replace · 원고 755–755 → 640–640

A (기준 원고):

```text
세 번째 연구 질문에서는 SCD 적용 전후의 한국어 문자 비율을 비교하였다. 평균 대응 차이는 HyDE OFF 동일 문맥 120개 대응쌍에서 +0.2182였고, 같은 질의의 HyDE와 CAD 상태를 맞춘 전체 240개 대응쌍에서 +0.2289였다.
```

B (최종 원고):

```text
RQ4에서 품질의 H×C 효과는 SCD 평가 프로토콜별 Holm 보정 후 모두 p≥0.05였다. 문자 비율에서는 SCD 주효과가, 실행 시간에서는 HyDE와 CAD 주효과 및 CAD×SCD 상호작용이 유의하였다. 조합을 비교할 때에는 품질, 문자 비율과 비용을 각각 확인해야 한다.
```

## 144. replace · 원고 757–757 → 642–642

A (기준 원고):

```text
네 번째 연구 질문에서는 적용 목적에 따른 실험 조건의 선택 기준을 검토하였다. 답변 관련성, 근거 충실도, 조건 실행 시간과 한국어 문자 비율 중 우선할 지표를 정하고, 해당 지표의 요인별 대응 결과를 확인한다. 목적별 비교 방법은 6.3절에 제시한다.
```

B (최종 원고):

```text
## 6.2 연구의 의의 [스타일=절(1.1)]
```

## 145. replace · 원고 759–759 → 644–644

A (기준 원고):

```text
## 6.2 비교 설계의 의의 [스타일=절(1.1)]
```

B (최종 원고):

```text
본 연구는 세 선행기법을 같은 검색·생성 파이프라인과 질의 집합에서 비교하였다. 검색 경로를 바꾸는 HyDE 비교와 검색 문맥이 같은 CAD 비교를 구분하고, SCD 출력 언어 비교의 여러 대응쌍을 질의 단위로 묶어 검정하였다. 또한 단순 비교와 요인 주효과·상호작용을 함께 제시하여 고정 조건의 결과와 조합 전반의 결과를 연결하였다.
```

## 146. replace · 원고 761–761 → 646–646

A (기준 원고):

```text
HyDE, CAD, SCD의 적용 단계와 검색 문맥의 동일성 여부를 기준으로 대응쌍을 구성하였다. HyDE는 검색부터 답변 생성까지의 변화를 비교하고, CAD는 검색 청크 ID, 재정렬 청크 ID와 최종 문맥이 같은 쌍에서 답변 품질을 비교하였다. SCD는 HyDE OFF 동일 문맥 120쌍을 주 비교로 삼고, 같은 질의의 HyDE와 CAD 상태를 맞춘 전체 240개 대응쌍에서 조합 전반의 출력 언어 변화를 집계하였다.
```

B (최종 원고):

```text
## 6.3 적용 조건과 후속 연구 [스타일=절(1.1)]
```

## 147. replace · 원고 763–763 → 648–648

A (기준 원고):

```text
조합별 평균은 특정 실험 조건에서 평가값이 있는 기록으로 계산한 지표별 평균이다. 요인별 대응 차이는 동일 질의에서 특정 기법을 적용했을 때와 적용하지 않았을 때의 평가값 차이를 나타낸다. H1C1S0의 근거 충실도 평균 0.8599는 한 설정의 평균이다. CAD의 +0.0288은 같은 질의와 검색 문맥을 사용한 유효 대응쌍에서 구한 ON−OFF 평균 차이이다.
```

B (최종 원고):

```text
한국어 중심의 출력을 우선하는 경우에는 SCD의 문자 비율 결과를 참고할 수 있다. 답변의 근거 충실도와 실행 시간이 중요한 경우에는 CAD의 질의별 변화와 추가 비용을 함께 검토해야 한다. HyDE는 번역과 가상 문서 생성이 결합된 검색 조건으로 해석하며, 번역만 적용한 비교를 추가하면 각 요소의 기여를 구분할 수 있다.
```

## 148. replace · 원고 765–777 → 650–650

A (기준 원고):

```text
그림 5-3, 5-5, 5-7, 5-8, 5-10에는 저장된 질문, 검색 문맥과 생성 답변에 평가값을 연결하여 제시하였다. 부록 B의 그림 B-1에는 CAD 적용 후 근거 충실도가 감소한 사례를 수록하였다.

## 6.3 적용 시 실험 조건 선택 [스타일=절(1.1)]

실험 조건을 선택할 때는 적용 목적에 맞는 평가 지표를 먼저 정하고, 해당 지표의 대응 비교 결과를 확인한다. 답변 관련성이 중요한 경우에는 HyDE 적용 전후의 검색 문맥과 답변 관련성을 비교한다. 동일한 검색 문맥에서 생성 품질을 평가할 때는 CAD의 근거 충실도, 답변 관련성과 조건 실행 시간을 함께 검토한다. 한국어 출력이 중요한 경우에는 HyDE OFF 동일 문맥 대응쌍에서 SCD 적용 전후의 한국어 문자 비율을 비교한다. 고유명사, 인용 표현과 전문용어의 보존 여부는 후속 사람 평가에서 확인할 항목으로 제안한다.

## 6.4 후속 연구 방향 [스타일=절(1.1)]

후속 연구에서는 평가 질의, 문서 도메인과 생성 모델의 범위를 확대하는 방향을 제안한다. 답변 불가능 질의, 대상 문서를 잘못 지정한 질의와 검색 근거가 제공되지 않은 입력을 추가하여 근거가 부족한 상황의 생성 결과를 평가하는 과제가 있다. 문서 도메인, 생성 모델과 토크나이저를 달리한 반복 실험에서는 조건별 답변 품질과 한국어 문자 비율의 차이를 분석할 수 있다.

HyDE에는 질의 번역, 가상 문서 생성과 밀집 검색 입력 변경을 분리한 실험을 제안한다. 같은 질의로 가상 문서를 반복 생성하여 검색 결과의 실행 간 변동을 측정하는 절차도 포함한다. CAD는 α와 검색 문맥의 길이를 달리하여 근거 충실도, 답변 관련성과 조건 실행 시간의 변화를 비교하는 것이 후속 과제다.

SCD의 후속 평가 항목은 답변의 자연스러움, 번역 충실도, 내용 정확성과 전문용어 보존이다. 평가자에게 기법의 적용 여부를 알리지 않는 사람 평가로 이 항목들을 확인하는 절차를 제안한다. 재정렬 단계의 비교에서는 현재 CrossEncoder와 다국어 재정렬 모델에 같은 검색 후보를 제공하고, 최종 검색 문맥과 답변 품질의 차이를 분석할 수 있다.
```

B (최종 원고):

```text
후속 연구에서는 평가 문서와 질의 범위를 확대하고, 생성 시드와 평가 모델을 반복하여 변동성을 측정할 필요가 있다. 모든 조건에 통일한 RAGAS 평가 프로토콜을 적용하고, 숫자 반복 및 언어 혼합 사례의 의미 정확성과 문장 자연스러움을 사람 평가와 함께 확인할 수 있다.
```

## 149. replace · 원고 827–831 → 700–700

A (기준 원고):

```text
그림 2-2~2-6은 CC BY 4.0에 따라 이용하였다. 각 그림의 저자와 서지정보는 참고문헌 번호로 표시하였다. 원본 자료의 주소와 편집 내역은 아래와 같다.

공통 라이선스: CC BY 4.0. [스타일=본문]

라이선스 안내: https://creativecommons.org/licenses/by/4.0/ [스타일=본문]
```

B (최종 원고):

```text
그림 2-1~2-4는 선행연구의 개념과 본 실험의 처리 과정을 참고하여 본 연구에서 작성한 독립 도식이다. 각 그림의 개념 출처와 참고 자료는 다음과 같다.
```

## 150. replace · 원고 835–835 → 704–704

A (기준 원고):

```text
원본 자료: https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf
```

B (최종 원고):

```text
참고 자료: https://proceedings.neurips.cc/paper/2020/file/6b493230205f780e1bc26945df7481e5-Paper.pdf
```

## 151. replace · 원고 837–837 → 706–706

A (기준 원고):

```text
그림 2-2 — Nelson F. Liu 외[9], TACL 2024, 12:157–173; PDF page 2 (printed 158). 원본 그림 1. 변경: 도표 영역 잘라내기.
```

B (최종 원고):

```text
그림 2-2 — 본 연구 작성. Gao 외[2]의 HyDE 구조를 참고하여 독립 도식을 작성하였다.
```

## 152. replace · 원고 839–839 → 708–708

A (기준 원고):

```text
원본 자료: https://aclanthology.org/2024.tacl-1.9.pdf
```

B (최종 원고):

```text
참고 자료: https://aclanthology.org/2023.acl-long.99/
```

## 153. replace · 원고 841–841 → 710–710

A (기준 원고):

```text
그림 2-3 — Luyu Gao 외[2], ACL 2023, 1762–1777; PDF page 2 (printed 1763). 원본 그림 1. 변경: 도식 영역 잘라내기, OpenAI 로고 생략.
```

B (최종 원고):

```text
그림 2-3 — 본 연구 작성. Shi 외[3]의 CAD 로짓 결합을 참고하여 독립 도식을 작성하였다.
```

## 154. replace · 원고 843–843 → 712–712

A (기준 원고):

```text
원본 자료: https://aclanthology.org/2023.acl-long.99.pdf
```

B (최종 원고):

```text
참고 자료: https://aclanthology.org/2024.naacl-short.69/
```

## 155. replace · 원고 845–845 → 714–714

A (기준 원고):

```text
그림 2-4 — Weijia Shi 외[3], NAACL 2024 short, PDF page 1. 원본 그림 1. 변경: 그림 영역 잘라내기.
```

B (최종 원고):

```text
그림 2-4 — 본 연구 작성. Li 외[4]의 SCD 토큰별 점수 조정을 참고하여 독립 도식을 작성하였다.
```

## 156. replace · 원고 847–847 → 716–716

A (기준 원고):

```text
원본 자료: https://aclanthology.org/2024.naacl-short.69.pdf
```

B (최종 원고):

```text
참고 자료: https://arxiv.org/abs/2511.09984
```

## 157. delete · 원고 849–855 → 718–717

A (기준 원고):

```text
그림 2-5 — Bo Li 외[4], arXiv:2511.09984v1, PDF page 1. 원본 그림 1. 변경: 그림 영역 잘라내기, OpenAI와 Ollama 로고 생략.

원본 자료: https://arxiv.org/pdf/2511.09984v1

그림 2-6 — Shahul Es 외[10], arXiv:2309.15217v2, PDF page 8. 원본 표 2. 변경: 표 영역 잘라내기.

원본 자료: https://arxiv.org/pdf/2309.15217v2
```

B (최종 원고):

```text
(삭제)
```

## 158. replace · 원고 858–858 → 720–720

A (기준 원고):

```text
부록 A의 질문 문장은 실제 실험 입력을 그대로 수록하였다.
```

B (최종 원고):

```text
각 질의의 대상 문서, 원문 페이지와 정답 근거를 제시한다.
```

## 159. replace · 원고 860–860 → 722–722

A (기준 원고):

```text
[표 A-1] 60개 질의–대상 문서 쌍 [스타일=표제목]
```

B (최종 원고):

```text
[표 A-1] 60개 한국어 질의의 대상 문서·유형·원문 페이지 및 정답 근거 [스타일=표제목]
```

## 160. delete · 원고 863–864 → 725–724

A (기준 원고):

```text

[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
(삭제)
```

## 161. replace · 원고 932–932 → 792–792

A (기준 원고):

```text
## B.1 추가 입출력 사례 [스타일=절(1.1)]
```

B (최종 원고):

```text
## B.1 저장된 생성·검색 사례 [스타일=절(1.1)]
```

## 162. replace · 원고 934–934 → 794–794

A (기준 원고):

```text
그림 B-1은 동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 사례다.
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/EVIDENCE/IO_CASES/E06_cad_tradeoff_same_context.png | 권장폭=본문폭 100% | 정렬=가운데]
```

## 163. replace · 원고 936–937 → 796–796

A (기준 원고):

```text
[입출력증빙삽입: FINALDOCS/EVIDENCE/IO_CASES/E06_cad_tradeoff_same_context.png | 권장폭=본문폭 95% | 정렬=가운데]
[그림 B-1] 동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 추가 사례 [스타일=그림제목]
```

B (최종 원고):

```text
[그림 B-1] 동일 검색 문맥에서 CAD 적용 후 근거 충실도가 감소한 사례 [스타일=그림제목]
```

## 164. replace · 원고 939–939 → 798–814

A (기준 원고):

```text
질의 ID: track1_0012.
```

B (최종 원고):

```text
[그림삽입: FINALDOCS/EVIDENCE/IO_CASES/E04_hyde_retrieval_change.png | 권장폭=본문폭 100% | 정렬=가운데]

[그림 B-2] HyDE 적용에 따른 검색 문맥 및 답변 변화 사례 [스타일=그림제목]

[그림삽입: FINALDOCS/EVIDENCE/IO_CASES/E05_cad_positive_same_context.png | 권장폭=본문폭 100% | 정렬=가운데]

[그림 B-3] 동일 검색 문맥에서 CAD 적용 전후 답변 비교 사례 [스타일=그림제목]

[그림삽입: FINALDOCS/EVIDENCE/IO_CASES/E02_language_drift.png | 권장폭=본문폭 100% | 정렬=가운데]

[그림 B-4] SCD 미적용 조건의 영어 중심 출력 사례 [스타일=그림제목]

[그림삽입: FINALDOCS/EVIDENCE/IO_CASES/E03_scd_rescue.png | 권장폭=본문폭 100% | 정렬=가운데]

[그림 B-5] SCD 적용 전후 한국어 문자 비율 변화 사례 [스타일=그림제목]

E03은 HyDE ON 사례로 전체 상태 일치 비교에 속한다. 주 비교의 HyDE OFF 동일 문맥 120쌍과 구분한다. 각 그림은 저장된 답변의 발췌이며, 전체 원문과 지표는 연결된 생성·평가 기록에서 확인할 수 있다.
```

## 165. replace · 원고 943–945 → 818–818

A (기준 원고):

```text
표 B-1에는 문서별 평균 대응 차이와 유효쌍 수를, 표 B-2에는 질문 유형별 평균 대응 차이와 유효쌍 수를 정리하였다. 목적 및 기여 유형에는 질의가 3개 포함되었다. 질문 유형별 분석 결과는 각 유형의 질의 수를 고려하여 탐색적으로 해석하였다.

[표 B-1] 문서별 탐색 분석 [스타일=표제목]
```

B (최종 원고):

```text
[표 B-1] 문서별 HyDE·CAD 대응 점수 차이의 평균(SD) [스타일=표제목]
```

## 166. delete · 원고 949–950 → 822–821

A (기준 원고):

```text
[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]

```

B (최종 원고):

```text
(삭제)
```

## 167. replace · 원고 952–984 → 823–855

A (기준 원고):

```text
대상 문서	요인	지표	유효쌍 수 n	평균 대응 차이
Mi:dm K 2.5 Pro Technical Report	HyDE	근거 충실도	15	0.0007
Mi:dm K 2.5 Pro Technical Report	HyDE	답변 관련성	15	0.0994
Mi:dm K 2.5 Pro Technical Report	HyDE	문맥 정밀도	15	-0.0145
Mi:dm K 2.5 Pro Technical Report	HyDE	문맥 재현율	15	0.1333
Mi:dm K 2.5 Pro Technical Report	CAD	근거 충실도	15	0.0081
Mi:dm K 2.5 Pro Technical Report	CAD	답변 관련성	15	0.0339
Mi:dm K 2.5 Pro Technical Report	CAD	문맥 정밀도	15	0
Mi:dm K 2.5 Pro Technical Report	CAD	문맥 재현율	15	0
CAD	HyDE	근거 충실도	15	-0.0491
CAD	HyDE	답변 관련성	15	-0.0019
CAD	HyDE	문맥 정밀도	15	-0.0823
CAD	HyDE	문맥 재현율	15	-0.0667
CAD	CAD	근거 충실도	15	0.0664
CAD	CAD	답변 관련성	15	-0.0099
CAD	CAD	문맥 정밀도	15	-0.0552
CAD	CAD	문맥 재현율	15	-0.0667
RAG Survey	HyDE	근거 충실도	15	0.1575
RAG Survey	HyDE	답변 관련성	15	0.1314
RAG Survey	HyDE	문맥 정밀도	15	0.0036
RAG Survey	HyDE	문맥 재현율	15	0.0667
RAG Survey	CAD	근거 충실도	13	-0.0416
RAG Survey	CAD	답변 관련성	15	-0.1004
RAG Survey	CAD	문맥 정밀도	15	0.0074
RAG Survey	CAD	문맥 재현율	15	0
RAPTOR	HyDE	근거 충실도	15	0.0652
RAPTOR	HyDE	답변 관련성	15	0.093
RAPTOR	HyDE	문맥 정밀도	15	-0.0441
RAPTOR	HyDE	문맥 재현율	15	-0.1333
RAPTOR	CAD	근거 충실도	15	0.0731
RAPTOR	CAD	답변 관련성	15	0.047
RAPTOR	CAD	문맥 정밀도	15	0.0108
RAPTOR	CAD	문맥 재현율	15	0
```

B (최종 원고):

```text
집단	요인	지표	유효 n	평균 차이(SD)
CAD	HyDE	근거 충실도	15	-0.049 (0.260)
CAD	HyDE	답변 관련성	15	-0.002 (0.287)
CAD	HyDE	문맥 정밀도	15	-0.082 (0.203)
CAD	HyDE	문맥 재현율	15	-0.067 (0.258)
CAD	CAD	근거 충실도	15	0.066 (0.227)
CAD	CAD	답변 관련성	15	-0.010 (0.126)
CAD	CAD	문맥 정밀도	15	-0.055 (0.131)
CAD	CAD	문맥 재현율	15	-0.067 (0.258)
Mi:dm K 2.5 Pro Technical Report	HyDE	근거 충실도	15	0.001 (0.198)
Mi:dm K 2.5 Pro Technical Report	HyDE	답변 관련성	15	0.099 (0.244)
Mi:dm K 2.5 Pro Technical Report	HyDE	문맥 정밀도	15	-0.014 (0.240)
Mi:dm K 2.5 Pro Technical Report	HyDE	문맥 재현율	15	0.133 (0.352)
Mi:dm K 2.5 Pro Technical Report	CAD	근거 충실도	15	0.008 (0.171)
Mi:dm K 2.5 Pro Technical Report	CAD	답변 관련성	15	0.034 (0.362)
Mi:dm K 2.5 Pro Technical Report	CAD	문맥 정밀도	15	0.000 (0.000)
Mi:dm K 2.5 Pro Technical Report	CAD	문맥 재현율	15	0.000 (0.000)
RAG Survey	HyDE	근거 충실도	15	0.157 (0.361)
RAG Survey	HyDE	답변 관련성	15	0.131 (0.134)
RAG Survey	HyDE	문맥 정밀도	15	0.004 (0.258)
RAG Survey	HyDE	문맥 재현율	15	0.067 (0.258)
RAG Survey	CAD	근거 충실도	13	-0.042 (0.381)
RAG Survey	CAD	답변 관련성	15	-0.100 (0.322)
RAG Survey	CAD	문맥 정밀도	15	0.007 (0.062)
RAG Survey	CAD	문맥 재현율	15	0.000 (0.000)
RAPTOR	HyDE	근거 충실도	15	0.065 (0.266)
RAPTOR	HyDE	답변 관련성	15	0.093 (0.396)
RAPTOR	HyDE	문맥 정밀도	15	-0.044 (0.248)
RAPTOR	HyDE	문맥 재현율	15	-0.133 (0.516)
RAPTOR	CAD	근거 충실도	15	0.073 (0.224)
RAPTOR	CAD	답변 관련성	15	0.047 (0.385)
RAPTOR	CAD	문맥 정밀도	15	0.011 (0.031)
RAPTOR	CAD	문맥 재현율	15	0.000 (0.000)
```

## 168. replace · 원고 987–987 → 858–858

A (기준 원고):

```text
[표 B-2] 질문 유형별 탐색 분석 [스타일=표제목]
```

B (최종 원고):

```text
[표 B-2] 질문 유형별 HyDE·CAD 대응 점수 차이의 평균(SD) [스타일=표제목]
```

## 169. replace · 원고 991–991 → 862–896

A (기준 원고):

```text
[한글 표 복붙용 — 아래 탭 구분 블록 전체 복사 → 한글 `표 > 문자열을 표로` → 구분 문자 `탭`]
```

B (최종 원고):

```text
```text
집단	요인	지표	유효 n	평균 차이(SD)
결과 및 비교	HyDE	근거 충실도	20	-0.051 (0.176)
결과 및 비교	HyDE	답변 관련성	20	-0.022 (0.207)
결과 및 비교	HyDE	문맥 정밀도	20	-0.029 (0.153)
결과 및 비교	HyDE	문맥 재현율	20	-0.050 (0.394)
결과 및 비교	CAD	근거 충실도	20	-0.004 (0.149)
결과 및 비교	CAD	답변 관련성	20	-0.068 (0.302)
결과 및 비교	CAD	문맥 정밀도	20	-0.012 (0.081)
결과 및 비교	CAD	문맥 재현율	20	-0.050 (0.224)
목적 및 기여	HyDE	근거 충실도	3	0.188 (0.272)
목적 및 기여	HyDE	답변 관련성	3	-0.029 (0.052)
목적 및 기여	HyDE	문맥 정밀도	3	-0.111 (0.229)
목적 및 기여	HyDE	문맥 재현율	3	0.000 (0.000)
목적 및 기여	CAD	근거 충실도	3	-0.160 (0.241)
목적 및 기여	CAD	답변 관련성	3	-0.314 (0.508)
목적 및 기여	CAD	문맥 정밀도	3	0.000 (0.000)
목적 및 기여	CAD	문맥 재현율	3	0.000 (0.000)
방법 및 절차	HyDE	근거 충실도	29	0.079 (0.343)
방법 및 절차	HyDE	답변 관련성	29	0.172 (0.339)
방법 및 절차	HyDE	문맥 정밀도	29	-0.003 (0.252)
방법 및 절차	HyDE	문맥 재현율	29	0.069 (0.371)
방법 및 절차	CAD	근거 충실도	27	0.082 (0.325)
방법 및 절차	CAD	답변 관련성	29	0.068 (0.326)
방법 및 절차	CAD	문맥 정밀도	29	0.003 (0.015)
방법 및 절차	CAD	문맥 재현율	29	0.000 (0.000)
사실 및 정의	HyDE	근거 충실도	8	0.097 (0.221)
사실 및 정의	HyDE	답변 관련성	8	0.045 (0.088)
사실 및 정의	HyDE	문맥 정밀도	8	-0.133 (0.337)
사실 및 정의	HyDE	문맥 재현율	8	-0.125 (0.354)
사실 및 정의	CAD	근거 충실도	8	0.000 (0.174)
사실 및 정의	CAD	답변 관련성	8	-0.014 (0.084)
사실 및 정의	CAD	문맥 정밀도	8	-0.049 (0.170)
사실 및 정의	CAD	문맥 재현율	8	0.000 (0.000)
```
```

## 170. replace · 원고 993–1027 → 898–898

A (기준 원고):

```text
```text
질문 유형	요인	지표	유효쌍 수 n	평균 대응 차이
사실 및 정의	HyDE	근거 충실도	8	0.0966
사실 및 정의	HyDE	답변 관련성	8	0.0455
사실 및 정의	HyDE	문맥 정밀도	8	-0.1328
사실 및 정의	HyDE	문맥 재현율	8	-0.1250
사실 및 정의	CAD	근거 충실도	8	0.0005
사실 및 정의	CAD	답변 관련성	8	-0.0145
사실 및 정의	CAD	문맥 정밀도	8	-0.0486
사실 및 정의	CAD	문맥 재현율	8	0
방법 및 절차	HyDE	근거 충실도	29	0.0792
방법 및 절차	HyDE	답변 관련성	29	0.1719
방법 및 절차	HyDE	문맥 정밀도	29	-0.0029
방법 및 절차	HyDE	문맥 재현율	29	0.0690
방법 및 절차	CAD	근거 충실도	27	0.0823
방법 및 절차	CAD	답변 관련성	29	0.0684
방법 및 절차	CAD	문맥 정밀도	29	0.0029
방법 및 절차	CAD	문맥 재현율	29	0
결과 및 비교	HyDE	근거 충실도	20	-0.0509
결과 및 비교	HyDE	답변 관련성	20	-0.0216
결과 및 비교	HyDE	문맥 정밀도	20	-0.0289
결과 및 비교	HyDE	문맥 재현율	20	-0.0500
결과 및 비교	CAD	근거 충실도	20	-0.0037
결과 및 비교	CAD	답변 관련성	20	-0.0683
결과 및 비교	CAD	문맥 정밀도	20	-0.0124
결과 및 비교	CAD	문맥 재현율	20	-0.0500
목적 및 기여	HyDE	근거 충실도	3	0.1875
목적 및 기여	HyDE	답변 관련성	3	-0.0289
목적 및 기여	HyDE	문맥 정밀도	3	-0.1111
목적 및 기여	HyDE	문맥 재현율	3	0
목적 및 기여	CAD	근거 충실도	3	-0.1597
목적 및 기여	CAD	답변 관련성	3	-0.3139
목적 및 기여	CAD	문맥 정밀도	3	0
목적 및 기여	CAD	문맥 재현율	3	0
```
```

B (최종 원고):

```text
하위집단 표는 탐색적 기술통계다. 질문 유형의 질의 수는 사실·정의 8, 방법·절차 29, 결과·비교 20, 목적·기여 3개이며, 결측이 있는 비교는 표의 유효 n을 사용하였다.
```
