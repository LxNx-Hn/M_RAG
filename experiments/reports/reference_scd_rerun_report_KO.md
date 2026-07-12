# Reference SCD Rerun Report 한국어 번역본

이 보고서는 이전 `penalty_additive` v1 SCD 모드가
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md)에서 효과가 거의 없는
결과로 확인된 뒤 평가한, 논문에 충실한 Soft Constrained Decoding 구현인 보정된
`reference_scd` 재실행 결과를 기록한다.

최종적으로 지지되는 결론은 초기 해석보다 좁다. `reference_scd`는 직접 측정한
한국어 언어 준수를 크게 개선한다. 완전한 `gpt-4o` 점수표는 SCD의 독립적인 인과
효과가 아니라, 해당 전처리 프로토콜에 대한 민감도 분석으로 보존한다. 이후 완료한
대칭 이중언어 후속 평가는 동일 context의 HyDE-off 38쌍에서 이전의 SCD-on-only
전처리 상관을 제거했다. faithfulness 방향은 확정하지 못했고 두 목표 언어 모두
`gpt-4o` answer relevancy 구간은 음수였지만 고정 `gpt-4.1-2025-04-14`에서는
0이 아닌 구간이 재현되지 않았다. judge에 강건한 0이 아닌 RAG-quality 효과는 없다.

## 1. 실행 요약

`reference_scd`는 Soft Constrained Decoding을 논문의 기준 구현 그대로 옮긴
방식이다. 즉 목표 언어 토큰에 대한 곱셈식 강화 `alpha`, 방해 언어 토큰에 대한
곱셈식 패널티 `beta`, 그리고 `T_start`까지의 초기 완충 구간을 사용한다. 이는
이전 `penalty_additive` v1 모드와 다르다. v1은 덧셈식 조정만 사용했고, 목표 언어
강화가 없었으며, 초기 완충 구간도 없었다. 그 v1 모드는 이미
[phase8_scd_failure_analysis.md](phase8_scd_failure_analysis.md)에서 효과가 거의
없는 결과로 보고되어 있다.

실제 목표 지표인 한국어 언어 준수에서 `reference_scd`는 강한 개선을 보인다. 이
결과는 생성 텍스트에서 직접 계산되므로 LLM 심판에 의존하지 않는다. 다만 26개
언어 이탈 중 15개를 회복했고, SCD-on 76개 중 12개는 여전히 0.5 미만이며 3개 쌍은
감소했으므로 모든 언어 이탈을 해결한 것은 아니다.

`gpt-4o` 패널은 152개 샘플과 0/608 null 셀을 가진다. 그 프로토콜에서 SCD-on
셀은 faithfulness, answer_relevancy, context_recall이 낮고 context_precision이
높았다. 그러나 SCD-on 문맥만 번역했고 GT는 영어로 남았으며 일부 HyDE-on 쌍의
검색 문맥도 달랐다. 따라서 이 차이는 프로토콜별 관찰값이지 SCD의 인과적 품질
효과가 아니다.

더 엄격한 이중언어 후속 평가는 HyDE-off 네 조건 모두에 점수와 무관하게 정한 같은
정규화 규칙을 적용했고, 영어·한국어 패널 총 304개 지표 셀을 모두 채웠다. query
cluster bootstrap 95% 구간은 두 언어의 faithfulness에서 모두 0을 포함한다. answer
relevancy는 영어 -0.0910 [-0.1725, -0.0240], 한국어 -0.0752
[-0.1501, -0.0138]로 두 언어 모두 낮았다. 이는 가능한 품질 비용 신호지만,
생성 후 정규화이고 같은 `gpt-4o`가 정규화와 판정을 모두 수행했으므로 무편향 인과
효과로 해석하지 않는다.
같은 304셀을 고정 `gpt-4.1-2025-04-14`로 교차 채점한 결과도 null 없이 완료됐다.
answer relevancy는 영어 -0.0327 [-0.0851, +0.0129], 한국어 -0.0356
[-0.1149, +0.0315]로 두 구간 모두 0을 포함한다. 따라서 0이 아닌 비용은 judge에
강건하지 않다.

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

직접 언어 결과는 검색 문맥을 고정해도 유지된다. HyDE-off 38쌍은 검색 문맥이
byte 단위로 모두 같고, 그 하위집합의 평균 Korean-ratio 차이도 +0.2198이다. 따라서
언어 제어 결론은 4장에서 설명하는 HyDE-on 검색 변동과 분리해 지지된다.

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
| 사전 정의 손상(기준 >=0.7에서 SCD-on <0.65) | 9/28 | **0/20** |

SCD의 실제 목표 지표에서 `reference_scd`는 확인된 강한 개선이며 논문의 공식과
하이퍼파라미터에 부합한다. 0/20은 사전 정의한 임계값 손상만 뜻하며, 어떤 감소도
없었다는 뜻은 아니다. 직접 언어 결과는 아래 RAGAS 패널에 의존하지 않는다.

## 4. 방법론 메모: RAG 품질 평가에 별도 설계가 필요했던 이유

평가에서는 SCD-on 레코드의 검색 문맥만 한국어로 번역했고, 생성 답변은 수정하지
않았다. 사용한 도구는
[`experiments/evaluators/translate_context_for_scd.py`](../evaluators/translate_context_for_scd.py)다.
이는 유용한 민감도 패널을 만들었지만 완전한 언어 일치 통제는 아니다.

보존된 산출물에서 SCD-off 답변도 50/76이 한국어 비율 0.5 이상이고, GT는 모두
영어로 남아 있다. 번역 처치는 SCD와 완전히 결합되어 있으며, 번역된 SCD-on chunk
380개 중 20개에는 한글이 없고 한 5-chunk 레코드는 성공 metadata에도 불구하고
영문 원문과 동일하다. 원래 검색 문맥도 76쌍 중 51쌍만 동일했고, HyDE-on 38쌍 중
25쌍은 서로 달랐다.

RAGAS 0.2.15에서 answer_relevancy는 질문과 생성 답변만 사용한다. context_precision과
context_recall은 질문·문맥·GT를 사용하지만 생성 답변은 보지 않는다. faithfulness만
생성 답변과 문맥을 함께 사용한다. 따라서 context 지표 차이를 디코더인 SCD가 만든
품질 효과라고 해석할 수 없다.

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

## 5. 완전한 `gpt-4o` 민감도 패널

이 보존된 민감도 패널의 심판은 NVIDIA NIM이 아니라 OpenAI
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

### 프로토콜 수준 해석

HyDE는 faithfulness를 명확히 올린다. +0.073으로, 어떤 축이 어떤 지표에 준 효과
중 가장 큰 양의 효과다. 또한 context_precision에는 일부 비용(-0.035)을 초래하며,
이는 전형적인 recall/precision 상충 패턴이다. 더 넓은 검색은 관련 근거를 더 많이
끌어오지만, 일부 잡음도 함께 끌어온다.

CAD는 모든 축/지표 쌍 중 단일 최대 음의 효과를 유발한다. answer_relevancy -0.076,
패배 34건이다. faithfulness에는 아주 제한적으로만 도움이 된다(+0.019). 이는
contrastive decoding이 직접적인 질문 관련성을 어느 정도 희생하면서 생성을 검색
문맥에 과도하게 고정하는 것과 일관된다.

이 프로토콜에서 SCD-on 셀은 faithfulness -0.048, answer_relevancy -0.057,
context_recall -0.066, context_precision +0.030의 차이를 보인다. answer_relevancy는
질문-답변 점수의 직접적인 연관값이다. 나머지 세 지표는 비대칭 문맥 번역의 영향을
받고, 두 context 지표는 생성 답변을 아예 보지 않는다. 따라서 네 값을 SCD 효과로
묶지 않고 민감도 분석으로만 사용한다.

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

`hyde_off__scd_only`는 HyDE 없이 SCD-on 셀의 낮은 점수 연관을 보인다. faithfulness는
0.8159에서 0.7906으로 하락하고(-0.0253), answer_relevancy는 0.8201에서 0.7758로
하락하며(-0.0443), context_recall은 1.0000에서 0.9474로 하락한다(-0.0526).
상쇄되는 차이는 context_precision의 0.8512 대 0.8343(+0.0169)이다. 이는 protocol
수준 축 표와 같은 방향이지만, 분리된 인과 효과로 읽으면 안 된다.

`hyde_off__cad_scd`는 행렬에서 단일하게 가장 위험한 조합이다. 이는
answer_relevancy에서 최악의 설정인 0.6556이고, context_recall에서 최악의 hyde-off
설정인 0.7895다. hyde-off 기준선보다 -0.2105 낮다. 이것은 CAD의
CAD-on 및 SCD-on의 answer_relevancy 점수 차이가 부분적으로 상쇄되기보다
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
추가한 셀의 faithfulness 차이가 HyDE 없을 때보다 작지만, 낮은 answer_relevancy
연관은 지속된다.

동일한 CAD/SCD 설정을 가진 네 개 대응 HyDE-on/off 쌍 전체에서, 모든 HyDE-on 변형은
대응되는 HyDE-off 변형보다 faithfulness가 높다. 각각 +0.0733, +0.1049, +0.0265,
+0.0882다. answer_relevancy에서는 같은 일관된 패턴이 성립하지 않는다. 대응 차이는
+0.0303, +0.0022, -0.0144, +0.0927이다. 따라서 HyDE는 CAD와 SCD 제약 아래를
포함하여 이 대응 비교들에서 faithfulness 수준을 일관되게 완충하지만,
answer_relevancy에 대해서는 같은 방식의 일관된 완충을 제공하지 않는다.

### 이 값이 인과적 faithfulness 기여도 분해가 아닌 이유

이 프로젝트의 핵심 목표는 한국어 언어 적응과 RAG groundedness다. 아래 값은 이
평가 프로토콜을 기술하지만 인과 기여도를 분해하지 않는다.

위 표의 축 수준 faithfulness 효과는 다음과 같다.

| 축 | 대응 faithfulness 차이 |
| --- | ---: |
| use_hyde | +0.0732 |
| use_cad | +0.0187 |
| use_scd | -0.0480 |

패널에서 `hyde_on__cad_only`는 0.9230, `hyde_on__cad_scd`는 0.8674로 -0.0556
차이가 난다. 그러나 문맥 번역과 다수 HyDE-on 쌍의 검색 내용도 달라 이 차이만으로
SCD가 faithfulness를 낮췄다고 말할 수 없다. 높였다고도 말할 수 없다. 이후 대칭
이중언어 패널이 동일 검색 문맥과 불확실성 추정을 추가했지만 두 faithfulness 구간은
여전히 0을 포함했다. 독립 judge와 사람 검토가 필요하다.

## 6. 이 패널을 참고 논문과 직접 비교할 수 없는 이유

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

이 보고서는 논문이 틀렸다고 주장하지 않는다. 논문이 시험한 적 없는 RAGAS 지표
공간에서 다른 영역과 기반 모델의 프로토콜별 관찰값을 기록하며, 인과적 품질 효과는
미해결로 남긴다.

## 7. 전체 결론

`reference_scd`는 직접 측정한 한국어 언어 준수를 크게 개선하고 26개 threshold
drift 중 15개를 회복한다. 사전 정의한 심각한 손상 전이는 0/20이지만 3/76은
감소했고 12/76 SCD-on 출력은 0.5 미만이다. 이것이 가장 중요한 확인 결과다.

`gpt-4o` 패널은 완전한 점수 산출물이지만 비대칭 번역과 검색 차이 때문에 SCD의
인과적 RAG 품질 결론을 만들 수 없다. 숫자를 인용할 때는 반드시 이 제한을 함께
적어야 한다.

완료한 대칭 후속 평가는 이 한계를 실질적으로 줄였다. HyDE-off 38개 SCD 비교쌍은
검색 context가 같고, 두 목표 언어 모두 동일한 field-level 정규화 정책을 사용하며,
19개 query cluster bootstrap으로 불확실성을 보고한다. faithfulness 방향은
확정되지 않았다. `gpt-4o` answer relevancy는 양쪽 언어에서 음의 구간이며 CAD-on
층에서 뚜렷했지만 고정 `gpt-4.1-2025-04-14`에서는 모든 해당 구간이 0을 포함했다.
고정 규칙이어도 한국어 답변의 실제 번역은 SCD-off 23/38, SCD-on 11/38로 달랐다.
최종 판정은 judge에 강건한 0이 아닌 RAG-quality 효과가 없다는 것이며, 인과 또는
배포 판정으로 쓰지 않는다. 자세한 표는
[reference_scd_symmetric_cross_judge_report.md](reference_scd_symmetric_cross_judge_report.md),
입력 감사는
[reference_scd_symmetric_input_audit.md](reference_scd_symmetric_input_audit.md)에 있다.

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

두 패널 모두 SCD-on 셀에서 answer_relevancy와 faithfulness 점수가 낮아 방향성
삼각 확인에는 유용하다. 그러나 서로 동등한 통제가 아니며 인과성을 확정하지 않는다.
context_recall은 +0.0132에서 -0.0658로 방향까지 바뀌어 judge에 제시한 텍스트와
언어에 대한 민감성을 보여준다.

번역 기반 BLEU/ROUGE 평가도 NIM RAGAS 채점 과정이 종료된 뒤 Alice Cloud 인스턴스에서
자동 실행되도록 대기열에 올라가 있었다. 그 지표는 참고 논문 자체의 번역 기반 평가
방법을 반영하여, SCD-on 답변을 NVIDIA NIM을 통해 영어로 번역한 다음 영어
`answer_span` 기준값과 비교해 점수를 낼 예정이었다. 실행기는
[`experiments/evaluators/translated_bleu_rouge_runner.py`](../evaluators/translated_bleu_rouge_runner.py)다.
그 단계가 끝나기 전에 Alice 인스턴스가 삭제되어 완료되지 않았다. 현재 RAGAS
민감도 패널은 인과적 내용 품질 질문에 답하지 못하므로 이 평가는 향후 과제로 남는다.
