# Reference SCD Rerun Report 한국어 번역본

이 보고서는 이전 `penalty_additive` v1 SCD 모드가
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md)에서 효과가 거의 없는
결과로 확인된 뒤 평가한, 논문에 충실한 Soft Constrained Decoding 구현인 보정된
`reference_scd` 재실행 결과를 기록한다.

결과는 실제 상충관계를 보인다. `reference_scd`는 자신이 해결하도록 설계된 목표
문제, 즉 한국어 언어 준수를 결정적으로 개선한다. 동시에 언어를 맞춘 RAG 품질
평가에서는 네 개 RAGAS 지표 중 세 개에서 측정 가능한 비용도 동반한다. 두 결과를
모두 최종 결과로 보고한다.

## 1. 실행 요약

`reference_scd`는 Soft Constrained Decoding을 논문의 기준 구현 그대로 옮긴
방식이다. 즉 목표 언어 토큰에 대한 곱셈식 강화 `alpha`, 방해 언어 토큰에 대한
곱셈식 패널티 `beta`, 그리고 `T_start`까지의 초기 완충 구간을 사용한다. 이는
이전 `penalty_additive` v1 모드와 다르다. v1은 덧셈식 조정만 사용했고, 목표 언어
강화가 없었으며, 초기 완충 구간도 없었다. 그 v1 모드는 이미
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md)에서 효과가 거의
없는 결과로 보고되어 있다.

실제 목표 지표인 한국어 언어 준수에서 `reference_scd`는 명확하고 강하며 확인된
성공 사례다. 이 결과는 LLM 심판이 아니라 생성 텍스트의 한국어 문자 비율에서
직접 계산되었으므로 심판 모델에 의존하지 않는다.

RAG 품질 지표에서는 `reference_scd`가 네 개 지표 중 세 개, 즉 faithfulness,
answer_relevancy, context_recall에서 실제적이고 엄격하게 검증된 비용을 보인다.
context_precision만이 유일한 예외이며 약간 양의 방향으로 움직인다.

이 상충관계는 언어를 맞추고 교차언어 교란을 통제한 평가 설계에서 검증되었다. 이
통제는 심판 모델의 교차언어 처리 잡음이 대안 설명이 될 가능성을 배제하기 위해
구체적으로 구축되었다. RAG 품질 비용은 그 통제를 통과한 뒤에도 남아 있었으므로,
측정상의 산물이 아니라 실제 확인된 결과로 보고한다.

## 2. 참고 논문: 인용 및 검증된 충실도

인용: **Language Drift in Multilingual Retrieval-Augmented Generation:
Characterization and Decoding-Time Mitigation**. Bo Li, Zhenghua Xu, Rui Xie.
Hebei University of Technology / Peking University. arXiv:2511.09984. Code:
https://github.com/pkuserc/SCD

논문의 전체 PDF 텍스트를 직접 점검하여 공식을 검증했다. 디코딩 단계 `t`에서 원시
logits `z(t)`가 주어지고, 어휘가 `Vtarget`, `Vneutral`, `Vdistractor`로 분할될 때
조정은 다음과 같다.

| 어휘 분류 | 조정된 logit |
|---|---|
| `i in Vtarget` | `alpha * z(t)_i`, 단 `alpha > 1.0` |
| `i in Vneutral` | 변경 없음 |
| `i in Vdistractor` | `beta * z(t)_i`, 단 `beta < 1.0` |

논문은 또한 초기 완충을 적용한다. 제약은 디코딩 단계 `Tstart`까지 비활성 상태다.

이는 이 저장소의 `reference_scd` 구현인
[`backend/modules/scd_decoder.py`](../../backend/modules/scd_decoder.py)와 정확히
일치한다.

하이퍼파라미터도 일치한다. 논문은 다음과 같이 명시한다. "We empirically find
moderate settings (alpha = 1.1, beta = 0.9, Tstart = 5) to balance language
fidelity and semantic fluency in SCD." 이 저장소의 `reference_scd` 생성 실행도 같은
값을 사용했다.

```text
--scd-alpha 1.1 --scd-beta 0.9 --scd-t-start 5
```

따라서 이는 공식만 충실한 것이 아니라 하이퍼파라미터까지 완전히 일치하는
구현이다.

논문은 세 개 데이터셋, HotpotQA, MuSiQue, DuReader를 평가한다. 또한 두 개
기반 모델인 LLaMA3-8B-Instruct와 Qwen2.5-7B-Instruct를 사용한다. 세 개 지표는 BLEU
(BLEU-1/2/3의 평균), ROUGE (ROUGE-1/2/L의 평균), Language Consistency (LC)다.
기준 방법은 Prompted Language Instruction (PLI)과 Vocabulary-Restricted Decoding
(VRD)이다.

논문의 핵심 결과는 SCD가 언어 일관성과 내용 품질을 "consistently improves"한다고
말하며, 목표 언어 정렬을 일관되고 정확한 추론의 장애물이 아니라 지원 요소로
제시한다. 검증된 예시 하나는 ZH-EN HotpotQA다. 여기서 SCD는 PLI 대비 LC를
68.4%에서 90.6%로, BLEU를 0.086에서 0.155로, ROUGE를 0.182에서 0.306으로
개선한다.

같은 논문은 강한 어휘 제약 방식인 VRD가 자체 데이터에서 실제 품질 비용을
초래한다는 점도 보인다. 더 짧고 저하된 출력이 나오며, 때로는 ROUGE에서 PLI보다도
낮다. 논문의 요지는 SCD의 부드러운 설계가 강한 제약이 초래하는 비용을 구체적으로
피한다는 것이다. 논문 어디에도 RAG 기반성이나 faithfulness 계열 지표는 등장하지
않는다.

## 3. 확인된 결과: 언어 준수

출처:
[`experiments/results/analysis/reference_scd_language_adherence.json`](../results/analysis/reference_scd_language_adherence.json).
이는 생성 답변의 한국어 문자 비율에서 직접 계산되었다. LLM 심판은 관여하지
않으므로, 이 결과는 RAGAS 지표를 어떤 심판 모델이 채점하든 관계없이 최종이다.

`reference_scd`는 76개의 대응 쌍 전체에서 SCD-on minus SCD-off로 측정한 평균
대응 차이 **+0.2203**을 산출했다. SCD-on은 76개 쌍 중 68개에서 더 한국어였고,
3개에서만 덜 한국어였으며, 동률은 5개였다.

0.5 한국어 비율 임계값에서 SCD off 상태로 언어 이탈을 보이던 쌍은 26개였다.
`reference_scd`는 그 평균을 0.2515에서 0.5639로 올렸고, 26개 중 15개를 임계값
너머로 완전히 회복시켰다.

0.3 임계값에서는 12개 쌍이 언어 이탈 상태였다. `reference_scd`는 그 평균을
0.0667에서 0.3843으로 올렸고, 12개 중 6개를 회복시켰다.

손상 여부 점검도 깨끗하다. SCD off에서 이미 한국어 비율이 최소 0.7이었던 20개 쌍
중, SCD-on에 의해 0.65 아래로 끌려 내려간 것은 0개였다.

기존 `penalty_additive` v1 결과는 다르며, 최종 reference-SCD 주장으로 이어받으면
안 된다. 그 출처는
[`experiments/results/analysis/scd_language_adherence.json`](../results/analysis/scd_language_adherence.json)이고,
이미 [phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md)에 보고되어
있다. v1은 평균 대응 차이 **-0.0137**로 거의 효과가 없었다. 승/패는 22/24로
동전 던지기에 가까웠고, 언어 이탈 쌍 19개 중 2개만 회복시켰으며, 실제 손상도
있었다. 이미 좋은 답변 28개 중 9개가 0.65 아래로 끌려 내려갔다.

| 지표 | v1 (`penalty_additive`) | `reference_scd` |
|---|---:|---:|
| 평균 대응 차이 | -0.0137 | **+0.2203** |
| 승 / 패 (76개 중) | 22 / 24 | **68 / 3** |
| 언어 이탈 회복 @0.5 | 2/19 | **15/26** |
| 이미 좋은 답변에 대한 손상 | 9/28 손상 | **0/20 손상 없음** |

SCD의 실제 목표 지표에서 `reference_scd`는 확인된, 강한, 메커니즘으로 검증된
성공이며, 논문의 중심 주장 및 정확한 하이퍼파라미터와 직접 일관된다. v1의 무효에
가까운 결과는 강화, 곱셈식 패널티, 초기 완충 구간이 빠져 있었기 때문이며, 이는
이미 [phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md)에 문서화되어
있다. 그 세 가지 간극을 고치자 보정된 결과가 나왔다. 이 결론은 이 보고서의 다른
어떤 내용에도 의존하지 않는다.

## 4. 방법론 메모: RAG 품질 평가에 별도 설계가 필요했던 이유

SCD가 성공하면 생성 답변은 한국어이고, 검색된 문맥은 영어 원문 논문에서 가져오기
때문에 영어로 남아 있다. 그러면 RAGAS `faithfulness`와 `answer_relevancy`는 SCD-on
레코드에서는 심판 LLM이 교차언어 추론을 해야 하고, SCD-off 레코드에서는 같은 언어
안에서 추론하게 된다. 이 비대칭은 실제 품질 차이와 무관하게 지표를 교란할 수
있다.

승인된 해결책은 엄격한 선택지였다. SCD-on 레코드에 대해서만 검색 문맥을 한국어로
번역했고, 이를 위해
[`experiments/evaluators/translate_context_for_scd.py`](../evaluators/translate_context_for_scd.py)를
사용했다. 따라서 SCD-on은 한국어 답변과 한국어 문맥의 조합으로 판정되고,
SCD-off는 영어 답변과 영어 문맥의 조합으로 남는다. 생성 답변 자체는 어느
조건에서도 수정하지 않는다. 비교 대상 쪽의 문맥만 언어를 맞춘다.

이는 답변을 번역하는 방법보다 우선 선택되었다. 답변은 평가 대상인 실제 산출물이기
때문이다. 답변을 번역하면 평가되는 출력에 번역 산물이 섞일 위험이 있다. 기준
문맥 쪽만 번역하면 그 위험을 피할 수 있다.

검색 및 디코딩 기반 구조는 검증 대상인 프로젝트 설정 그대로 유지되었다:
HyDE is dense branch within fixed hybrid backbone, using weighted RRF, dense 0.6
/ BM25 0.4. CAD uses exact single-sequence CAD for greedy decoding. SCD는 위에서
설명한 논문 충실 `reference_scd` 모드다.

구현 세부사항:

| 항목 | 검증 결과 |
|---|---|
| 문맥 중복 제거 기준 | 정확히 같은 문맥 내용 |
| 내용 기준 중복 제거를 사용한 이유 | HyDE-on 검색이 명목상 같은 질의와 HyDE 설정 전반에서 완전히 결정적이지 않았음 |
| HyDE-off 검색 | 완전히 결정적이며 공유됨 |
| 고유 문맥 그룹 | 48 |
| 번역된 전체 청크 | 240 |
| 번역 모델 | `gpt-4o` |
| 번역 실패 | 0 |
| 제외된 SCD-on 레코드 | 0 |
| 번역된 문맥을 가진 SCD-on 레코드 | 76/76 |

문맥을 `(query_id, use_hyde)`로 중복 제거할 수 있다는 원래 가정은 기각되었다.
원래 생성 실행에서 HyDE-on 레코드의 검색이 명목상 같은 질의와 HyDE 설정 전반에
걸쳐 완전히 결정적이지 않다는 점이 확인되었기 때문이다. HyDE의 가상 문서 생성
단계는 명목상 같은 query+HyDE-setting 쌍에서도 검색 변동을 도입한다. 따라서 내용
기반 중복 제거가 올바른 비교 그룹을 만들었다.

문맥 번역이 실패한 레코드는 파이프라인에서 통째로 제외되도록 설계되어 있었다.
파이프라인은 번역되지 않은 문맥으로 조용히 되돌아가지 않는다. 이번 실행에서는
제외된 레코드가 없었다.

## 5. 공식 RAG 품질 결과

이 `reference_scd` RAG 품질 평가의 공식 심판은 NVIDIA NIM이 아니라 OpenAI
`gpt-4o`다.

심판 모델 변경은 이 실험 트랙에 한정되며, 경험적으로 확인된 신뢰성 문제 때문에
이루어졌다. 2026-07-03 결정에서 프로젝트가 원래 선택한 심판 모델을 사용한 이전
NVIDIA NIM 시도는 60시간 넘게 실행되었고, 1차 실행을 38.6% null 비율(235/608
칸)로 완료했으며, 기반 Alice Cloud 인스턴스가 실행 도중 삭제된 뒤 중단되었다.

그다음 `gpt-4o`는 완전히 수렴했다. 약 2시간 동안 null은 0/608이었다. 1차 실행은 약
98분이 걸렸다. 2차 실행은 아직 null이던 38개 쌍을 재시도했고 약 27분이 걸렸다.

이는 `reference_scd`의 RAG 품질 지표가 NVIDIA NIM으로 채점된 이 프로젝트의 다른
실험과 직접 수치 비교될 수 없다는 뜻이다. `reference_scd` 자체에 대해 수렴한
NVIDIA NIM RAG 품질 점수는 없다. NIM이 그 평가에서 끝내 수렴하지 않았기 때문이다.
이 심판 모델 변경은 3장의 v1 대비 언어 준수 비교에는 영향을 주지 않는다.
그 비교는 심판 모델에 의존하지 않는다.

### 전체 8개 설정 표

총 152개 샘플, 설정당 19개다. 모든 지표가 수렴했고, null은 0개다.

| 설정 | HyDE | CAD | SCD | faithfulness | answer_relevancy | context_precision | context_recall |
|---|:-:|:-:|:-:|---:|---:|---:|---:|
| no_decoder_control | off | off | off | 0.8159 | 0.8201 | 0.8343 | 1.0000 |
| cad_only | off | on | off | 0.8181 | 0.7485 | 0.8321 | 0.9474 |
| scd_only | off | off | on | 0.7906 | 0.7758 | 0.8512 | 0.9474 |
| cad_scd | off | on | on | 0.7792 | 0.6556 | 0.8446 | 0.7895 |
| no_decoder_control | on | off | off | 0.8892 | 0.8504 | 0.7664 | 0.9474 |
| cad_only | on | on | off | 0.9230 | 0.7507 | 0.7988 | 0.8947 |
| scd_only | on | off | on | 0.8171 | 0.7614 | 0.8135 | 0.8947 |
| cad_scd | on | on | on | 0.8674 | 0.7483 | 0.8422 | 0.8947 |

전체 152개 샘플에 대한 집계:

| 지표 | 집계 |
|---|---:|
| faithfulness | 0.8376 |
| answer_relevancy | 0.7639 |
| context_precision | 0.8229 |
| context_recall | 0.9145 |

### 축별 효과

대응 차이는 각각 76개의 대응 쌍 전체에서 계산된다. 승/패는 `|delta| > 0.01`인 쌍을
센 것이다.

| 축 | faithfulness | answer_relevancy | context_precision | context_recall |
|---|---:|---:|---:|---:|
| use_hyde | +0.0732 (40W/24L) | +0.0277 (27W/19L) | -0.0353 (27W/23L) | -0.0132 (5W/6L) |
| use_cad | +0.0187 (31W/27L) | -0.0762 (24W/34L) | +0.0131 (14W/9L) | -0.0658 (2W/7L) |
| **use_scd** | **-0.0480 (28W/30L)** | **-0.0571 (22W/32L)** | **+0.0300 (13W/7L)** | **-0.0658 (2W/7L)** |

Null-cell 민감도는 의미가 없다. 608개 중 null cell이 0개이므로, 유의미한 민감도
분석 대상이 없다. 민감하게 반응할 결측 데이터 자체가 없다.

### 축별 해석

HyDE는 faithfulness를 명확히 올린다. +0.073으로, 어떤 축이 어떤 지표에 준 효과
중 가장 큰 양의 효과다. 또한 context_precision에는 일부 비용(-0.035)을 초래하며,
이는 전형적인 recall/precision 상충 패턴이다. 더 넓은 검색은 관련 근거를 더 많이
끌어오지만, 일부 잡음도 함께 끌어온다.

CAD는 모든 축/지표 쌍 중 단일 최대 음의 효과를 유발한다. answer_relevancy -0.076,
패배 34건이다. faithfulness에는 아주 제한적으로만 도움이 된다(+0.019). 이는
contrastive decoding이 직접적인 질문 관련성을 어느 정도 희생하면서 생성을 검색
문맥에 과도하게 고정하는 것과 일관된다.

SCD는 네 개 RAG 품질 지표 중 세 개에서 비용을 낸다. faithfulness -0.048,
answer_relevancy -0.057, context_recall -0.066이다. SCD는 context_precision에서
양의 효과(+0.030)를 보이는 유일한 축이다. 특히 SCD의 answer_relevancy 비용
(-0.057)은 CAD의 비용(-0.076)과 방향 및 크기가 가깝다. 두 디코딩 시점 제약
메커니즘, 즉 하나는 사실 기반성을 위한 것이고 하나는 언어 제어를 위한 것인 두
메커니즘이 유사한 형태의 품질 비용 패턴을 보인다. 검색 쪽 개입인 HyDE는 상대적으로
더 완만하고 혼합된 양상을 보인다. 이는 데이터에서 관찰된 패턴이지, 데이터가
뒷받침하는 범위를 넘어선 인과 메커니즘 주장이 아니다.

### 설정별 해석

`hyde_off__no_decoder_control`은 개입이 없는 깨끗한 기준선이다. 이는 모든 설정
중 가장 높은 context_recall인 1.0000과 강한 answer_relevancy인 0.8201을 가진다.
다른 모든 설정은 이 기준선을 기준으로 읽어야 한다.

`hyde_off__cad_only`는 hyde-off 기준선 대비 faithfulness를 사실상 평평하게
유지한다. 0.8181 대 0.8159, 대응 차이는 +0.0022다. 주된 비용은
answer_relevancy다. 0.7485 대 0.8201, 대응 차이는 -0.0716이며, context_precision
(-0.0022)과 context_recall (-0.0526)에는 더 작은 하락이 있다. 따라서 HyDE 없는
CAD는 그 자체로 faithfulness 개선이 아니다. 눈에 보이는 상충관계는 질문 관련성에
있다.

`hyde_off__scd_only`는 HyDE 없이 분리된 SCD 비용을 보인다. faithfulness는
0.8159에서 0.7906으로 하락하고(-0.0253), answer_relevancy는 0.8201에서 0.7758로
하락하며(-0.0443), context_recall은 1.0000에서 0.9474로 하락한다(-0.0526).
상쇄되는 이득은 context_precision이다. 0.8512 대 0.8343(+0.0169)이며, 이는 SCD가
precision에는 긍정적이지만 다른 RAGAS 지표에서는 품질 비용을 동반한다는 축 수준
결과와 일관된다.

`hyde_off__cad_scd`는 행렬에서 단일하게 가장 위험한 조합이다. 이는
answer_relevancy에서 최악의 설정인 0.6556이고, context_recall에서 최악의 hyde-off
설정인 0.7895다. hyde-off 기준선보다 -0.2105 낮다. 이것은 CAD의
answer_relevancy 비용과 SCD의 answer_relevancy 비용이 부분적으로 상쇄되기보다
누적되는 것처럼 보이는 유일한 설정이다. CAD-only는 hyde-off 기준선에서 -0.0716,
SCD-only는 -0.0443, CAD+SCD는 -0.1645다.

`hyde_on__no_decoder_control`은 디코더 제어가 활성화되지 않았을 때 HyDE의
깨끗한 상승 효과를 보여준다. hyde-off 기준선과 비교하면, faithfulness는
0.8159에서 0.8892로 상승하고(+0.0733), answer_relevancy는 0.8201에서 0.8504로
상승한다(+0.0303). 반면 context_precision은 0.8343에서 0.7664로 하락하고(-0.0679),
context_recall은 1.0000에서 0.9474로 하락한다(-0.0526). 이 설정은 축 수준 HyDE
faithfulness 상승과 precision 상충관계의 주요 출처다.

`hyde_on__cad_only`는 모든 설정 중 가장 높은 faithfulness인 0.9230에 도달한다.
`hyde_off__cad_only`와 비교하면 HyDE는 faithfulness에 +0.1049를 더하고,
answer_relevancy는 0.7507 대 0.7485(+0.0022)로 거의 변하지 않는다. HyDE의
faithfulness 상승과 CAD의 작은 faithfulness 상승은 여기서 서로 더해지는 것처럼
보인다. HyDE-off에서 CAD 단독은 faithfulness를 +0.0022만 올렸음에도 그렇다.

`hyde_on__scd_only`는 HyDE가 SCD-only 조건의 절대 faithfulness 수준을 완충한다는
점을 보인다. `hyde_off__scd_only`의 0.7906 대비 0.8171로, 대응 쌍 기준 상승은
+0.0265다. answer_relevancy는 같은 보호를 받지 못한다. 0.7614 대 0.7758로,
대응 쌍 차이는 -0.0144다. 따라서 SCD 주변의 HyDE 보호 효과는 여기서
faithfulness에 특화되어 있으며, 모든 지표에 일반적으로 적용되지는 않는다.

`hyde_on__cad_scd`는 세 축이 모두 활성화된 상태에서 `hyde_off__cad_scd` 대비
faithfulness를 회복한다. 0.8674 대 0.7792(+0.0882)다. answer_relevancy 점수는
0.7483으로 낮게 남아 있다. `hyde_off__cad_scd`보다 +0.0927 높지만, 여전히
`hyde_on__no_decoder_control`보다 -0.1021 낮다. HyDE 아래에서는 CAD+SCD를 함께
추가할 때 faithfulness 비용이 HyDE 없을 때보다 적지만, answer_relevancy 비용은
지속된다.

동일한 CAD/SCD 설정을 가진 네 개 대응 HyDE-on/off 쌍 전체에서, 모든 HyDE-on 변형은
대응되는 HyDE-off 변형보다 faithfulness가 높다. 각각 +0.0733, +0.1049, +0.0265,
+0.0882다. answer_relevancy에서는 같은 일관된 패턴이 성립하지 않는다. 대응 차이는
+0.0303, +0.0022, -0.0144, +0.0927이다. 따라서 HyDE는 CAD와 SCD 제약 아래를
포함하여 이 대응 비교들에서 faithfulness 수준을 일관되게 완충하지만,
answer_relevancy에 대해서는 같은 방식의 일관된 완충을 제공하지 않는다.

### faithfulness 기여도 분해

이 프로젝트의 핵심 목표는 두 가지다. 하나는 한국어 언어 적응이고, 다른 하나는
RAG 환각 감소이며, 이 보고서에서는 후자를 RAGAS `faithfulness`로 조작화한다.
`hyde_on__cad_scd`처럼 모든 개입이 켜진 설정이 언어 준수와 faithfulness 양쪽에서
무개입 기준선을 이기므로, SCD도 환각 감소에 긍정적으로 기여한다고 해석하기 쉽다.
그러나 이 해석은 맞지 않다.

위 표의 축 수준 faithfulness 효과는 다음과 같다.

| 축 | 대응 faithfulness 차이 |
| --- | ---: |
| use_hyde | +0.0732 |
| use_cad | +0.0187 |
| use_scd | -0.0480 |

직접 설정 비교도 같은 점을 분명히 보여준다. SCD 없이 HyDE+CAD만 켠
`hyde_on__cad_only`는 faithfulness 0.9230에 도달하며, 이는 8개 설정 전체에서 가장
높은 값이다. 같은 HyDE+CAD 조합에 SCD를 추가한 `hyde_on__cad_scd`는 faithfulness가
0.8674로 내려간다. HyDE와 CAD를 모두 켠 상태로 고정하고 SCD만 켰을 때 -0.0556이
감소한 것이다.

따라서 모든 개입이 켜진 설정의 faithfulness가 무개입 기준선보다 좋아진 것,
즉 0.8159에서 0.8674로 올라간 +0.0515 순이득은 전적으로 HyDE와 CAD에
기인한다. 이 보고서의 모든 측정에서 SCD 자체의 분리된 faithfulness 기여는
음수다. 축 수준 효과에서도 그렇고, `hyde_on__cad_only`와
`hyde_on__cad_scd`를 직접 비교해도 그렇다. 이 프로젝트의 두 핵심 목표에 대해
정확히 말하면, SCD는 언어 적응 목표를
달성하지만 환각 감소 목표에는 기여하지 않는다. 오히려 HyDE와 CAD가 만든
faithfulness 이득의 일부를 비용으로 소모한다. 모든 개입을 켠 설정이 두 측면에서
무개입보다 여전히 앞서는 이유는 SCD가 도움이 되어서가 아니라, HyDE와 CAD의
faithfulness 기여인 +0.0732와 +0.0187이 SCD의 비용인 -0.0480보다 크기 때문이다.

부차적으로 논의할 만한 흥미로운 패턴도 있다. CAD는 이 프로젝트에서 명목상 환각
완화 축이다. 즉 contrastive decoding을 통해 생성을 검색 문맥에 더 강하게 묶어
환각을 줄이도록 설계된 축이다. 그런데 CAD 자체의 분리된 faithfulness 효과인
+0.0187은 HyDE의 부수적 효과인 +0.0732보다 작다. 이 데이터셋에서는 명시적인
환각 억제 설계 목표가 없는 검색 쪽 개입인 HyDE가 CAD보다 faithfulness에 더 크게
기여했다. 이는 CAD가 작동하지 않는다는 주장이 아니라, 데이터에서 관찰된 패턴으로
논의할 필요가 있다는 뜻이다. CAD의 효과는 양수이지만 HyDE보다 작다.

## 6. 참고 논문은 상충관계를 보고하지 않는데 이 보고서는 상충관계를 찾은 이유

### 서로 다른 지표 구성

이것이 주된 이유다. 논문의 내용 품질 지표는 BLEU/ROUGE다. 즉 목표 언어
기준 답변과의 어휘적 n-gram 겹침이다. 그 점수는 답변이 올바른 언어로 전환될
때마다, 답변 내용이 검색 근거에 잘 기반하는지와 대체로 무관하게 기계적으로
개선된다.

RAGAS `faithfulness`는 범주적으로 다른 것을 측정한다. 이는 표면 언어 일치와
무관하게 답변의 구체적 주장이 검색 문맥에 의해 뒷받침되는지를 측정한다. SCD가
언어 일관성과 함께 BLEU/ROUGE를 올린다는 논문의 주장은 그것이 RAGAS 방식의
groundedness도 올린다는 것을 함의하지 않는다. 이는 같은 대상을 두고 경쟁하는
측정이 아니라, 서로 다른 대상을 측정하는 서로 다른 방식이다.

### 범위 차이일 뿐, 모순은 아님

논문은 RAG groundedness나 faithfulness를 전혀 측정하지 않는다. 지표 묶음은
BLEU/ROUGE/LC뿐이다. 따라서 이 보고서의 발견은 논문의 주장을 반박한다기보다,
논문 자체 평가가 전혀 다루지 않은 공간에서 수행한 측정이다.

### 이 설정의 차이가 여기서 효과를 키웠을 수 있음

이 프로젝트의 말뭉치는 밀도 높은 학술 및 기술 텍스트다. 용어, 인용, 정확한
수치가 중요하다. 그런 영역에서는 언어 전환을 강제하는 것이 논문의 일반 multi-hop
QA benchmark인 HotpotQA, MuSiQue, DuReader에서보다 더 큰 정밀도 손실 위험을
그럴듯하게 만들 수 있다.

논문의 하이퍼파라미터인 `alpha=1.1`, `beta=0.9`, `Tstart=5`는
LLaMA3-8B-Instruct와 Qwen2.5-7B-Instruct에서 조정되었다. 이 프로젝트는 다른
기반 모델인 Mi:dm을 사용한다. 같은 고정 하이퍼파라미터 값이 다른 모델에서도 동일한
충실도/제어 균형점에 놓인다는 보장은 없다.

이 보고서는 논문이 틀렸다고 주장하지 않는다. 이 보고서는 논문이 시험한 적 없는
지표 공간, 즉 RAG 근거성으로 측정을 확장하고, 다른 영역과 기반 모델 아래에서
실제 비용을 찾는다.

## 7. 전체 결론

SCD는 `reference_scd`로서 의도한 목표를 결정적으로 달성한다. 강한 양의 효과,
의미 있는 언어 이탈 회복, 이미 좋은 답변에 대한 무손상으로 한국어 언어 준수를
개선한다. 이는 참고 논문의 정확한 공식 및 하이퍼파라미터와 완전히 일관되며,
그에 비추어 검증되었다. 이것이 가장 중요한 확인 결과다.

별도로, 언어를 엄격히 맞추고 교차언어 교란을 통제한 평가 아래에서 SCD는 네 개
RAGAS RAG 품질 지표 중 세 개, 즉 faithfulness, answer_relevancy, context_recall에서
실제 비용을 동반한다. context_precision은 개선한다.

이는 측정상의 산물이 아니다. 이 비용은 심판 모델의 교차언어 처리 잡음이 대안
설명이 될 가능성을 배제하기 위해 설계된 구체적 통제를 통과한 뒤에도 남아 있었다.
두 결과는 나란히 보고되어야 한다. 언어 제어 성공은 축소해서는 안 되고, RAG 품질
비용도 완화하거나 묻어서는 안 된다.

## 8. 부록: 비공식 gpt-4o-mini 교차 점검(비정본)

이는 다른, 더 약한 심판 모델인 `gpt-4o-mini`를 사용했다. 공식 `gpt-4o`가 아니다.

중요하게도, 이 교차 점검은 4장에서 설명한 문맥 번역 보정 전에 실행되었다.
원본의 번역되지 않은 생성 파일을 사용했기 때문에, 4장이 구체적으로
제거하도록 설계된 동일한 교차언어 심판 교란을 가지고 있다. 따라서 이는
5장 결과를 같은 엄격도로 확인하거나 반박하는 것으로 읽으면 안 된다. 역사적
완결성과 대략적인 방향성 삼각 확인을 위해서만 포함한다.

출처:
[`experiments/results/analysis/reference_scd_openai_side/main_config_scores.csv`](../results/analysis/reference_scd_openai_side/main_config_scores.csv)
및
[`experiments/results/evaluation/main-hyde-cad-scd-reference-scd-openai-side/`](../results/evaluation/main-hyde-cad-scd-reference-scd-openai-side/).

| 설정 | faithfulness | answer_relevancy | context_precision | context_recall |
|---|---:|---:|---:|---:|
| hyde_off__no_decoder_control | 0.8443 | 0.8370 | 0.9330 | 0.9474 |
| hyde_off__cad_only | 0.8653 | 0.6614 | 0.9432 | 0.9474 |
| hyde_off__scd_only | 0.8216 | 0.7177 | 0.9330 | 0.9474 |
| hyde_off__cad_scd | 0.7595 | 0.6142 | 0.9330 | 0.9474 |
| hyde_on__no_decoder_control | 0.9115 | 0.8603 | 0.8803 | 0.9474 |
| hyde_on__cad_only | 0.9047 | 0.7566 | 0.9181 | 1.0000 |
| hyde_on__scd_only | 0.8086 | 0.7609 | 0.9238 | 1.0000 |
| hyde_on__cad_scd | 0.8413 | 0.7430 | 0.9164 | 1.0000 |

출처:
[`experiments/results/analysis/reference_scd_openai_side/main_axis_effects.json`](../results/analysis/reference_scd_openai_side/main_axis_effects.json).

| 지표 | `use_scd` 대응 차이 | n | 승/패 |
|---|---:|---:|---:|
| faithfulness | -0.0737 | 76 | +17/-30 |
| answer_relevancy | -0.0699 | 76 | +22/-30 |
| context_precision | +0.0079 | 76 | +7/-4 |
| context_recall | +0.0132 | 76 | +1/-0 |

주요 결과의 방향은 문맥 번역 통제가 적용되기 전에도 재현된다. 비공식이며 통제되지
않은 `gpt-4o-mini` 실행과 공식이며 통제된 `gpt-4o` 실행 모두 SCD가 faithfulness와
answer_relevancy에 비용을 낸다는 점을 보이며, 둘 다 context_precision을 SCD가 돕는
하나의 지표로 보인다. 이는 5장 결과가 특정 번역 방법론의 산물만은 아니라는
부수적 근거를 더한다. 그러나 실제 주장에 인용해야 할 숫자는 이 비공식 숫자가
아니라 공식적이고 통제된 5장의 숫자다. context_recall은 두 실행 사이에서
방향이 다르다. 비공식 결과는 +0.0132, 공식 결과는 -0.0658이다. 그럴듯한 설명은
context_recall이 심판 모델이 정답 기준문과 비교하도록 받은 텍스트가
원문인지 번역문인지에 민감하다는 것이지만, 이는 확인된 메커니즘이 아니라 향후
과제로 남는 열린 질문이다.

번역 기반 BLEU/ROUGE 평가도 NIM RAGAS 채점 과정이 종료된 뒤 Alice Cloud 인스턴스에서
자동 실행되도록 대기열에 올라가 있었다. 그 지표는 참고 논문 자체의 번역 기반 평가
방법을 반영하여, SCD-on 답변을 NVIDIA NIM을 통해 영어로 번역한 다음 영어
`answer_span` 기준값과 비교해 점수를 낼 예정이었다. 실행기는
[`experiments/evaluators/translated_bleu_rouge_runner.py`](../evaluators/translated_bleu_rouge_runner.py)다.
그 단계가 끝나기 전에 프로젝트 소유자가 Alice 인스턴스를 삭제했기 때문에 완료되지
않았다. 이 지표는 `gpt-4o` 경로에서 의도적으로 재시도하지 않았다. 5장의
문맥 번역 RAGAS 결과가 BLEU/ROUGE가 답하려던 같은 근본 질문, 즉 SCD가 내용 품질
비용을 동반하는지에 대해 이미 엄격하고 언어를 맞춘 답을 제공하기 때문이다. 나중에
논문 자체 방법론에 맞는 보조 내용 겹침 지표가 필요해지면 향후 과제 후보로 남는다.
