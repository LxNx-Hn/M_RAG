# Codex 지시 — 졸업자격실험보고서 전체 확장본 + 시각자료 + HWP 이전용 수식

## 작업 목표

M_RAG 저장소의 현재 최종 실험을 기준으로 졸업자격실험보고서를 30~40쪽 수준의 연구보고서 밀도로 완성한다.
문장을 반복해 분량을 늘리는 방식이 아니라, 실험 설계·구현·8개 조합·통제 비교·질의별 분포·실제 입출력·평가 민감도·한계를 충분히 설명한다.

최종 논문은 **현재 실험 구성과 결과만** 서술한다.
과거 버전, 레거시 결과, 수정 전 설정, 이전 실험을 회고하는 문장을 넣지 않는다.

최종 원고의 문체는 연구의 현재 상태를 직접 서술한다.
다음과 같은 메타형 방어 문장을 피한다.

- “평가의 절대적 정확성을 보장하는 근거로 사용하지 않는다.”
- “예전 결과와 다르다.”
- “레거시 결과는 제외한다.”
- “수정 전에는 …였다.”
- “잘못된 실험을 고쳤다.”

대신 역할을 바로 정의한다.

예:
- “GPT-4o System Card는 평가 모델의 사양과 실행 provenance를 설명하는 참고자료로 활용한다.”
- “Korean-character ratio는 language adherence의 직접 지표로 사용하고 content quality는 symmetric evaluation으로 측정한다.”
- “CAD의 generation-side 통제 해석은 H0/S0 identical-context 19쌍을 기준으로 한다.”
- “H1의 CAD 결과는 RAG-Cube configuration 수준의 기술적 패턴으로 제시한다.”

FastAPI, React, 웹 UI, A–F route, 서비스 기능은 논문에 넣지 않는다.

RAG-Cube는 **HyDE·CAD·SCD 세 이진 요인의 2×2×2 실험 구성명**이다.
새 알고리즘·새 방법·새 프레임워크로 표현하지 않는다.
본문에서는 “본 연구에서는 … 조합 실험을 RAG-Cube로 지칭한다.”라고 쓴다.

---

## 1. manuscript source

우선순위:

1. `docs/PAPER/FINAL/THESIS_KO_EXPANDED_HWP_READY.md`가 있으면 이 파일
2. `docs/PAPER/FINAL/THESIS_KO_EXPANDED.md`
3. `docs/PAPER/FINAL/GRADUATION_REPORT_TRANSFER_KO.md`

오래된 `docs/PAPER/THESIS_KO.md`를 최종 원고로 되돌리지 않는다.

최종 출력:
- `docs/PAPER/FINAL/THESIS_KO_EXPANDED_HWP_READY.md`
- `docs/PAPER/FINAL/GRADUATION_REPORT_TRANSFER_KO.md`
- `docs/PAPER/FINAL/HWP_EQUATION_INPUTS.txt`
- `docs/PAPER/FINAL/figures/*.svg`
- `docs/PAPER/FINAL/figures/*.png`
- `docs/PAPER/FINAL/generated/*.csv`
- `docs/PAPER/FINAL/generated/*.json`
- `docs/PAPER/FINAL/generated/evidence_manifest.json`
- `docs/PAPER/FINAL/VALIDATION_REPORT.md`

---

## 2. 최종 실험 source of truth

Generation:
`experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_main_queries__main_generation.jsonl`

Official evaluation:
`experiments/results/evaluation/main-hyde-cad-scd-reference-scd-gpt4o-official/merged.ragas_scores.json`

Configuration / axis:
`experiments/results/analysis/reference_scd_gpt4o_official/main_config_scores.csv`
`experiments/results/analysis/reference_scd_gpt4o_official/main_axis_effects.json`

SCD language:
`experiments/results/analysis/reference_scd_language_adherence.json`

Symmetric:
`experiments/results/analysis/reference_scd_symmetric_gpt4o.json`
`experiments/results/analysis/reference_scd_symmetric_gpt41_2025_04_14.json`

Reports:
`experiments/reports/reference_scd_rerun_report.md`
`experiments/reports/reference_scd_rerun_report_KO.md`
`experiments/reports/reference_scd_symmetric_input_audit.md`
`experiments/reports/reference_scd_symmetric_cross_judge_report.md`

Queries:
`experiments/data/query_splits/decoder_main_queries.json`

Evidence:
`cli/evidence_cases.py`
`cli/evidence_replay.py`
`docs/PAPER/EVIDENCE_SCREENSHOT_PLAN.md`

Verifier:
`docs/PAPER/scripts/verify_current_thesis_results.py`

새 generation, retrieval, translation, RAGAS, judge API 호출 없이 저장 artifact에서 계산한다.

---

## 3. 실험 사실

현재 원고 기준으로 자동 검증:

- 19 query-document pairs
- RAG Survey 5
- CAD 4
- RAPTOR 4
- Mi:dm K 2.5 Pro Technical Report 6
- 8 configurations
- 152 generations
- generator = `K-intelligence/Midm-2.0-Base-Instruct`
- Mi:dm K 2.5 Pro = target document
- CAD α=0.5
- SCD = reference_scd, α=1.1, β=0.9, T_start=5
- CAD → SCD processor order
- quality practical band = ±0.01
- SCD language band = ±0.02

추가 60-query 실험이 저장소에 반영된 뒤에는 이 숫자를 새 artifact 기준으로 자동 갱신하고, 19-query 값을 본문에 잔존시키지 않는다.

---

## 4. 최종 목차

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

3단계 번호(예: 5.8.1)는 만들지 않는다.
5.8 안에서는 `사례 1.`, `사례 2.` 형태의 본문 라벨을 사용한다.

---

## 5. 한컴 한글 수식 규칙

Markdown LaTeX `\\frac`, `\\begin{cases}`를 최종 HWP 이전용 원고에 남기지 않는다.
학교 양식에 없는 수식 번호나 `[수식 ...]`, `(2-1)` 형태의 표기를 새로 만들지 않는다.
본문에서는 설명 문장 다음에 수식 자체만 삽입한다.

다음 exact string을 `HWP_EQUATION_INPUTS.txt`에도 저장한다.

검색 결과:
`C_q = Retrieve(q,D)`

생성 답변:
`y = LM(q,C_q)`

Weighted RRF:
`RRF(d) = {0.6} over {k + rankDense(d)} + {0.4} over {k + rankBM25(d)}`

CAD:
`z_{CAD} = (1 + alpha) z_{ctx} - alpha z_{noctx}`

SCD 한국어 목표 토큰:
`tilde z_i = alpha z_i`
조건: `i in V_{ko}`

SCD 영어 비목표 토큰:
`tilde z_i = beta z_i`
조건: `i in V_{en}`

SCD 중립 토큰:
`tilde z_i = z_i`
조건: `i in V_{neutral}`

대응쌍 점수 차이:
`Delta_i = s_i(ON) - s_i(OFF)`

Korean-character ratio:
`KoreanRatio = {N_{Hangul}} over {N_{Hangul} + N_{ASCII}}`

현재 초안의 총 생성 수:
`19 times 8 = 152`

추가 60-query 실험이 반영되면 실제 dataset size로 자동 갱신한다.

## 6. 주요 표

표 3-1 연구 및 실험 요구사항
표 3-2 RAG-Cube 8개 조건
표 3-3 실험 요인별 적용 위치와 비교 단위

표 4-1 실험 실행 환경
표 4-2 고정 Paper-RAG backbone
표 4-3 configuration별 평균 생성시간
표 4-4 generation record 저장 field

표 5-1 문서별 query-document pair
표 5-2 RAG-Cube 8개 조건별 평균 RAGAS
표 5-3 HyDE primary controlled result
표 5-4 CAD identical-context result
표 5-5 SCD configuration별 Korean ratio / drift
표 5-6 SCD paired language summary
표 5-7 symmetric quality summary

표 제목은 항상 표 위.

---

## 7. 주요 그림

공통:
- 흰 배경
- Malgun Gothic 또는 한글 호환 sans-serif
- text #222222
- neutral #AAB2BA
- HyDE #2F6BFF
- CAD #24866D
- SCD #C86A1B
- SVG + 600dpi PNG
- grayscale 판독 가능
- 그림 내부에 큰 장식형 제목 배치 금지
- HWP caption이 그림 제목 역할

그림 1-1 연구 환경
그림 3-1 RAG-Cube
그림 3-2 실험 아키텍처
그림 4-1 Paper-RAG 상세 pipeline
그림 4-2 artifact / evaluation flow
그림 5-1 evaluation design
그림 5-2 RAG-Cube 8×4 quality matrix
그림 5-3 HyDE/CAD controlled forest
그림 5-4 HyDE/CAD stratum delta matrix
그림 5-5 SCD language adherence
그림 5-6 symmetric SCD quality
그림 5-7 Normal QA
그림 5-8 language drift + SCD matched-context rescue
그림 5-9 HyDE retrieval-change
그림 5-10 CAD balanced identical-context cases

---

## 8. 5.3 RAG-Cube 전체 분석

현재 19-query final artifact에서는:

H0C0S0:
F .8159 / AR .8201 / CP .8343 / CR 1.0000

H0C1S0:
F .8181 / AR .7485 / CP .8321 / CR .9474

H0C0S1:
F .7906 / AR .7758 / CP .8512 / CR .9474

H0C1S1:
F .7792 / AR .6556 / CP .8446 / CR .7895

H1C0S0:
F .8892 / AR .8504 / CP .7664 / CR .9474

H1C1S0:
F .9230 / AR .7507 / CP .7988 / CR .8947

H1C0S1:
F .8171 / AR .7614 / CP .8135 / CR .8947

H1C1S1:
F .8674 / AR .7483 / CP .8422 / CR .8947

해석:
- F best = H1C1S0
- AR best = H1C0S0
- CP best = H0C0S1
- CR best = H0C0S0
- metric별 optimum이 다름
- RAG-Cube의 핵심은 목적별 configuration trade-off

SCD content quality의 해석은 5.7 symmetric 결과를 기준으로 하고, 5.3은 configuration-level profile로 제시.

---

## 9. 5.4 HyDE 해석

Primary H1C0S0−H0C0S0:

F +0.0734 [-0.0248,+0.1777], 9/6/4
AR +0.0303 [+0.0016,+0.0615], 9/3/7
CP -0.0679 [-0.1702,+0.0194], 7/6/6
CR -0.0526 [-0.1579,0], 0/1/18

해석:
- AR = 가장 강한 controlled positive result
- F = positive mean + query heterogeneity
- CP = mixed direction
- CR = 18/19 practical tie

Full 76:
F +0.0732, 40/24/12
AR +0.0277, 27/19/30

Faithfulness H1−H0 by C×S:
+0.0733
+0.1049
+0.0265
+0.0882
네 strata 모두 양수.

“성공/실패” 단문으로 줄이지 말고 지표별로 해석.

---

## 10. 5.5 CAD 해석

Primary H0/S0 identical-context:
F +0.0023 [-0.0903,+0.0952], 7/9/3
AR -0.0715 [-0.1792,+0.0004], 5/12/2
CP -0.0022, 2/1/16
CR -0.0526, 0/1/18

서술:
- faithfulness 평균은 0 부근, query별 증가/감소 혼재
- AR는 감소 방향 신호
- CP/CR은 동일 context 통제 확인용 보조 결과

Full matrix CAD:
F +0.0187
CP +0.0131
AR -0.0762
CR -0.0658

H1S0:
F +.0338
CP +.0324
AR -.0997

H1S1:
F +.0503
CP +.0287
AR -.0131
CR 0

H1C1S0 = 전체 faithfulness 최고.

최종 해석:
conditional partial positive pattern + AR/runtime trade-off.
H1 결과는 configuration-level pattern.
CAD generation-side primary 해석은 H0/S0 identical-context 19쌍.

시간:
약 2.60× / 3.02× / 3.22× / 2.80×.

---

## 11. 5.6 SCD language

+0.2203
68 increase / 3 decrease / 5 tie
increase 89.5%
drift 26→12
15/26 rescued at .5
6/12 rescued at .3
already Korean 20 pairs 중 .65 아래 crossing 0
identical-context H0 n=38 +.2198
strata:
+.1981
+.2415
+.2012
+.2402

직접 목표에 대한 강하고 일관된 language-control result로 작성.

---

## 12. 5.7 symmetric quality

gpt-4o EN:
F +.0071, 18/12/8, CI crosses zero
AR -.0910, CI below zero

gpt-4o KO:
F -.0283, CI crosses zero
AR -.0752, CI below zero

gpt-4.1 EN:
F -.0579, CI crosses zero
AR -.0327, CI crosses zero

gpt-4.1 KO:
F -.0326, CI crosses zero
AR -.0356, CI crosses zero
AR W/L/T = 17/17/4

gpt-4o의 AR cost signal과 gpt-4.1의 zero-crossing 범위를 함께 설명.
SCD language-control result와 content-quality result를 별도 축으로 유지.

---

## 13. evidence panel

원본 stored text를 사용.

E01 Normal QA
E02 language drift
E03 SCD matched-context rescue
E04 HyDE retrieval change

CAD:
H0/S0 identical-context 19쌍에서
- positive faithfulness pair 1개
- negative/trade-off pair 1개
를 deterministic rule로 선택해 하나의 balanced figure에 배치.

E06 = low-faithfulness review case.
본문에서는 필요 시 한계 또는 부록.

evidence_manifest.json에 selection criterion과 query_id 기록.

---

## 14. 한계 문체

한계 절에서도 과거 반성형 문체를 사용하지 말고 현재 분석 범위를 설명한다.

예:
- “본 연구의 HyDE condition은 번역과 hypothetical generation을 하나의 retrieval-expansion pipeline으로 평가한다.”
- “CAD의 generation-side primary conclusion은 H0/S0 identical-context pair를 기준으로 한다.”
- “Korean-character ratio는 language adherence를 측정하고 semantic quality는 symmetric evaluation으로 다룬다.”
- “BM25 candidate trace는 RAG Survey 40개 record에서 0, 나머지 112개 record에서 8로 관찰된다.”
- “CrossEncoder는 한국어 query–영어 passage를 직접 매칭하는 고정 backbone 조건이다.”

원인 추측이나 과거 설정 회고는 넣지 않는다.

---

## 15. 참고문헌

본문 first appearance 순서로 1:1 정리.
실제 본문에서 사용한 문헌만 유지.

Mi:dm 2.0 = generator provenance.
Mi:dm K 2.5 Pro = target document.
RAPTOR와 BERGEN 역할 구분.

GPT-4o System Card의 본문 역할은:
“평가 모델의 사양과 실행 provenance를 설명하는 참고자료”
로만 직접 서술.

---

## 16. 검증

최종 validation:
- dataset/query count
- paper distribution
- configs
- generation count
- generator exact model
- CAD/SCD params
- processor order
- primary pair count
- context identity
- SCD pair count
- symmetric pair count
- config means
- CI/WLT
- language stats
- judge results
- table/figure citation
- bibliography matching
- HWP equation syntax file 존재
- 3단계 heading 없음
- 서비스 관련 내용 없음
- 원고에 과거/레거시/수정 전 실험 회고 없음

`VALIDATION_REPORT.md`에 source path와 PASS/FAIL 기록.

추가 60-query 실험이 반영된 경우에는 모든 수치·표·그림·초록·결론을 새 artifact 기준으로 갱신하고 현재 19-query 숫자를 최종 원고에 남기지 않는다.
