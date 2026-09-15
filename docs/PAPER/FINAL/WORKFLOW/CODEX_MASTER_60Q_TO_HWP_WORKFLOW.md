# Codex MASTER WORKFLOW — 60-query 확장실험 → 결과 교정/반영 → 표·그림 생성 → 한글 이전용 논문

## 최종 목표

M_RAG 저장소에서 **총 60개의 질의-대상문서 쌍**으로 RAG-Cube 확장실험을 수행하고,
그 결과를 기준으로 기존 교정 원고의 구조와 해석 논리를 재검토한 뒤,
필요한 표·그림·evidence panel을 먼저 생성하고,
마지막에 동국대학교 졸업자격실험보고서 한글 양식으로 옮길 수 있는 최종 국문 원고를 작성한다.

이 작업은 반드시 다음 순서로 진행한다.

> **1) 60-query 확장실험**
> → **2) 실험 검증·정밀분석·기존 교정안 피드백**
> → **3) 논문에 들어갈 결과 해석 확정**
> → **4) 표·그림·evidence panel 생성**
> → **5) 시각자료와 수치 교차검증**
> → **6) 한글 이전용 전체 논문 작성**
> → **7) 최종 validation**

단계를 건너뛰지 않는다.
앞 단계의 validation이 실패하면 다음 단계로 넘어가지 말고 원인을 기록하고 수정한다.

---

# 0. 중요한 작성 원칙

## 0.1 논문에는 최종 60-query 실험만 쓴다

최종 논문에서는 19-query 실험을 과거 결과로 회고하지 않는다.

금지 예:
- “기존 19개 실험에서는…”
- “이전 결과와 달리…”
- “예전에는…”
- “레거시 결과…”
- “수정 전 실험…”
- “잘못된 실험을 고쳐…”

최종 논문은 **60-query 최종 실험이 본 연구의 실험인 것처럼 현재형으로 직접 서술**한다.

19-query 원고와 결과는:
- 글의 구조
- 연구 질문
- 해석 프레임
- 표·그림 설계
- 검증 기준
을 참고하는 내부 작업 자료로만 사용한다.

## 0.2 RAG-Cube의 의미

RAG-Cube는 새 알고리즘, 새 방법, 새 프레임워크가 아니다.

정확한 정의:
> 본 연구에서는 HyDE, CAD, SCD를 각각 독립적인 이진 실험 요인으로 두어 구성한 2×2×2 조합 실험을 RAG-Cube로 지칭한다.

“제안한다”, “개발한다”, “새로운 프레임워크”, “최적화 방법” 같은 표현을 사용하지 않는다.

## 0.3 서비스 내용 금지

최종 논문에 다음 내용을 넣지 않는다.
- FastAPI
- React
- 웹 UI
- 서비스 route
- A/B/C/D/E/F 기능
- 사용자 화면
- API 기능
- 서비스 배포

이 논문의 시스템은 **RAG-Cube 실험 프로그램 및 Paper-RAG 실험 파이프라인**이다.

## 0.4 결과를 성공/실패로 단순화하지 않는다

각 결과를 다음 순서로 해석한다.

1. 평균 방향과 크기
2. 95% CI
3. win/loss/tie
4. query-level heterogeneity
5. configuration-level pattern
6. 해당 metric의 의미
7. 다른 metric과의 관계
8. 실제 입출력 사례
9. 어디까지 해석 가능한지

“효과 없음”, “실패”, “성공” 같은 단어 하나로 끝내지 않는다.

---

# 1. 입력 manuscript / 참고자료

다음 파일이 있으면 우선순위대로 사용한다.

1. `docs/PAPER/FINAL/THESIS_KO_EXPANDED_HWP_READY_CLEAN.md`
2. `docs/PAPER/FINAL/THESIS_KO_EXPANDED_HWP_READY.md`
3. `docs/PAPER/FINAL/THESIS_KO_EXPANDED.md`
4. `docs/PAPER/FINAL/GRADUATION_REPORT_TRANSFER_KO.md`

이 파일들은 **문체·구조·설명 밀도·표/그림 계획의 참고자료**다.
60-query 결과가 나오면 수치와 결과 해석은 전부 새 실험 기준으로 교체한다.

기존 19-query 수치를 최종 원고에 남기지 않는다.

---

# 2. STAGE 1 — 60-query 확장실험 준비

## 2.1 60개의 최종 질의-대상문서 쌍 확인

최종 query split은 정확히 60개의 **질의-대상문서 쌍**이어야 한다.

중요:
- 같은 60개 질문을 모든 문서에 던지는 구조가 아니다.
- 각 query는 하나의 target document와 연결된다.
- 총 60개의 query-document pair다.
- 기존 19개를 포함해 총 60개인지 확인한다.
- 60개가 아니라면 실험을 시작하지 않는다.

다음 항목을 query마다 검사:
- `query_id`
- Korean query
- target paper
- answer/reference span
- answerable 여부
- 중복 여부
- template/citation-only 여부
- 최종 split 포함 여부

검사 결과를:
`docs/PAPER/FINAL/generated/QUERY_60_AUDIT.md`
에 작성한다.

## 2.2 문서별 분포 확인

문서별 query 수를 자동 집계한다.

예상 target document:
- RAG Survey
- CAD
- RAPTOR
- Mi:dm K 2.5 Pro Technical Report

실제 분포는 60-query split을 source of truth로 한다.
균형이 완벽하지 않아도 임의로 재배분하지 않는다.

다만 다음을 보고:
- 문서별 개수
- 질문 유형별 개수
- numeric/method/definition/result/comparison 등 유형 분포
- 특정 문서 과도 편중 여부
- duplicate/near-duplicate 여부

문제가 있으면 실험 전에 report하고 수정 후 재검증한다.

## 2.3 최종 generation 수

60 query × 8 configurations = **480 generations**

각 configuration은 정확히 60개 record를 가져야 한다.

8개 configuration:
- H0C0S0
- H0C1S0
- H0C0S1
- H0C1S1
- H1C0S0
- H1C1S0
- H1C0S1
- H1C1S1

---

# 3. STAGE 1 — 60-query RAG-Cube 실험 실행

## 3.1 고정 backbone

실험 backbone은 현재 최종 연구 설정을 따른다.

- Dense retrieval: BGE-M3
- Sparse retrieval: BM25
- Fusion: dense 0.6 / BM25 0.4 weighted RRF
- Retrieval pool: 8
- Reranker: `ms-marco-MiniLM-L-6-v2`
- Rerank top-N: 8
- Generation context: 5 passages
- Generator: `K-intelligence/Midm-2.0-Base-Instruct`
- Answer decoding: deterministic greedy
- Max new tokens: 512
- CAD: alpha=0.5
- SCD: `reference_scd`
- SCD alpha=1.1
- SCD beta=0.9
- SCD T_start=5
- CAD → SCD processor order

HyDE:
- Korean query → English translation
- English hypothetical document
- hypothetical document → dense retrieval
- original Korean query → BM25
- original Korean query → CrossEncoder reranking

## 3.2 실험 실행

저장소의 기존 main-generation pipeline을 사용하되
최종 60-query split을 input으로 지정한다.

실험 결과는 **새 60-query 전용 경로**에 저장한다.
기존 19-query artifact를 덮어쓰지 않는다.

권장 naming:
`experiments/results/main_generation/main-hyde-cad-scd-reference-scd__decoder_60_queries__main_generation.jsonl`

실제 repository naming convention을 유지하되
60-query result임이 파일명에서 명확해야 한다.

## 3.3 generation validation

generation 완료 직후 자동 검증:

- unique query IDs = 60
- configs = 8
- total records = 480
- each config = 60
- all target paper assigned
- generator exact model consistent
- all records status succeeded
- CAD/SCD params consistent
- CAD→SCD order consistent
- HyDE metadata present when ON
- translated query present when required
- hypothetical document present when required
- retrieved IDs saved
- reranked IDs saved
- contexts saved
- duration saved

FAIL이 있으면 evaluation으로 넘어가지 않는다.

---

# 4. STAGE 1 — 평가 실행

## 4.1 official quality evaluation

480 record에 대해 기존 official protocol을 사용한다.

metrics:
- faithfulness
- answer relevancy
- context precision
- context recall

60-query official evaluation은 새로운 결과 경로에 저장한다.

## 4.2 SCD language analysis

SCD matched pairs:
60 queries × 4 HyDE×CAD strata = **240 SCD ON/OFF pairs**

자동 검증:
- expected = 240
- 실제 pair count 기록

계산:
- Korean-character ratio
- mean paired delta
- increase/decrease/tie
- drift < 0.5
- threshold crossing
- drift < 0.3
- already-Korean stability

practical band:
- Korean ratio ±0.02

## 4.3 HyDE primary comparison

Primary:
H1C0S0 vs H0C0S0

expected:
- 60 matched pairs

품질 practical band:
- ±0.01

계산:
- mean delta
- 95% paired bootstrap CI
- W/L/T
- query-level deltas

bootstrap iteration은 기존 thesis protocol 이상 유지.
현재 200,000회를 사용하면 그대로 유지.

## 4.4 CAD primary comparison

Primary:
H0C1S0 vs H0C0S0

expected:
- 60 matched pairs

반드시 각 pair마다:
- context identical
- retrieved IDs identical
- reranked IDs identical
을 검사한다.

60/60 identical이면 primary CAD analysis 사용.

일부 pair가 identical이 아니면:
- 이유를 자동 추측하지 않는다.
- identity를 만족하는 pair 수를 보고한다.
- primary CAD analysis sample을 어떻게 정의할지 report한다.
- 논문 수치에 자동으로 60이라고 쓰지 않는다.

## 4.5 symmetric SCD quality

HyDE OFF에서:
60 queries × 2 CAD states = 최대 **120 SCD ON/OFF pairs**

실제 identical-context pair count를 검사한다.

English-normalized / Korean-normalized panel 생성.

judges:
- gpt-4o
- gpt-4.1-2025-04-14 또는 현재 고정 judge version

metrics:
- faithfulness
- answer relevancy

query-clustered bootstrap.

## 4.6 평가 완료 report

생성:
`docs/PAPER/FINAL/generated/EXPERIMENT_60_VALIDATION.md`

포함:
- dataset counts
- generation completeness
- official evaluation counts
- HyDE pair count
- CAD identical-context count
- SCD pair count
- symmetric pair count
- model versions
- hashes
- PASS/FAIL

---

# 5. STAGE 2 — 60-query 결과 정밀분석

실험을 끝낸 직후 **논문을 바로 쓰지 않는다.**
먼저 새 결과를 분석하고 기존 교정 원고의 해석 프레임을 재검토한다.

생성:
`docs/PAPER/FINAL/RESULT_REVIEW_60Q.md`

## 5.1 RAG-Cube 8개 configuration 전체

각 config별:
- F
- AR
- CP
- CR
- Korean ratio
- drift count
- mean generation duration

각 metric의:
- best config
- second best
- range
- ranking
을 계산한다.

분석:
- 하나의 config가 모든 지표에서 best인지
- metric-specific optimum인지
- 모두 ON이 실제로 좋은지
- H/C/S 조합에서 반복되는 패턴
- quality/runtime trade-off

## 5.2 HyDE 정밀분석

Primary controlled result:
- mean
- CI
- W/L/T

Full matrix:
C0S0
C1S0
C0S1
C1S1

각 stratum에서 H1−H0:
- F
- AR
- CP
- CR

분석:
- 60-query로 늘렸을 때 faithfulness positive pattern이 유지되는지
- AR의 CI 방향이 유지되는지
- CP/CR 패턴
- query-level heterogeneity
- paper별 패턴
- 질문 유형별 탐색 분석이 가능한 sample size인지

유형별 sample이 충분하지 않으면 논문 본문 결론으로 확대하지 않는다.

## 5.3 CAD 정밀분석

Primary identical-context:
- F
- AR
- CP
- CR
- CI
- W/L/T

Full matrix:
H0S0
H0S1
H1S0
H1S1

C1−C0 delta 계산.

분석:
- CAD의 부분적 긍정 패턴이 60-query에서도 유지되는지
- HyDE ON에서 F/CP positive pattern 유지 여부
- AR trade-off 유지 여부
- runtime cost
- H1C1S0 등 특정 configuration이 여전히 F 상위인지

주의:
HyDE ON CAD pair는 context identity가 다를 수 있으므로
formal interaction effect로 부르지 않는다.

## 5.4 SCD 정밀분석

전체 240 matched pair 기준:
- mean delta
- median delta
- increase/decrease/tie
- drift OFF→ON
- rescue
- regress
- H×C four strata
- identical-context subset

분석:
- direct language-control effect의 일관성
- effect size 안정성
- baseline ratio별 effect
- already-Korean answer stability

## 5.5 symmetric quality

두 judge × 두 languages × CAD strata.

분석:
- F/AR direction
- CI
- W/L/T
- judge robustness
- language robustness
- positive/negative pair coexistence

## 5.6 paper별 exploratory analysis

60개에서는 document별 sample이 커졌다면
다음 탐색 분석을 수행한다.

- RAG Survey
- CAD
- RAPTOR
- Mi:dm K 2.5 Pro

각 문서에서 H/C/S paired delta.

단:
문서별 sample이 작으면 descriptive appendix로만 보낸다.

## 5.7 query-type exploratory analysis

query metadata가 충분히 신뢰 가능하면:
- method
- factual/result
- numeric
- definition
- comparison
등으로 그룹화.

각 그룹에서:
- n
- H/C/S mean delta
- W/L/T

n이 작으면 본문에서 일반화하지 않는다.

---

# 6. STAGE 2 — 기존 교정 원고 기반 피드백

`THESIS_KO_EXPANDED_HWP_READY_CLEAN.md`를 구조·문체 기준으로 읽는다.

새 결과와 비교하여:
- 유지할 논리
- 수정할 결과 해석
- 제거할 주장
- 추가해야 할 발견
- 새 한계
- 새 그림 필요성
을 정리한다.

생성:
`docs/PAPER/FINAL/THESIS_FEEDBACK_AFTER_60Q.md`

형식:

## 초록
- 유지
- 수정
- 추가

## 1장
...

## 5.3
...

숫자만 교체하지 않는다.
새 60-query 결과가 기존 해석을 약화/강화/변경하면 **문장 논리 자체를 다시 작성**한다.

최종 논문에는 “19-query와 비교해 달라졌다”는 메타 서술을 넣지 않는다.

---

# 7. STAGE 3 — 최종 논문 주장 확정

표와 그림을 만들기 전에
`docs/PAPER/FINAL/FINAL_CLAIM_MAP_60Q.md`
를 생성한다.

각 claim마다:

- claim ID
- manuscript section
- 정확한 문장 초안
- source artifact
- numerical support
- controlled vs descriptive
- limitation
- figure/table support

예:
- C-HYDE-01
- C-CAD-03
- C-SCD-02
- C-RAGCUBE-01

주장과 source가 1:1로 추적 가능해야 한다.

---

# 8. STAGE 4 — 파생 데이터 생성

`docs/PAPER/FINAL/generated/`

생성:

- `rag_cube_config_scores_60q.csv`
- `hyde_primary_60q.csv`
- `hyde_strata_deltas_60q.csv`
- `cad_primary_60q.csv`
- `cad_strata_deltas_60q.csv`
- `scd_language_summary_60q.csv`
- `symmetric_quality_summary_60q.csv`
- `runtime_summary_60q.csv`
- `paper_level_exploratory_60q.csv`
- `query_type_exploratory_60q.csv`
- `evidence_manifest_60q.json`

모든 값은 source artifact에서 자동 생성.
manuscript에 수동 복붙한 숫자를 source로 사용하지 않는다.

---

# 9. STAGE 4 — 본문 표 생성

최종 60-query 결과에 맞게 자동 작성.

## 3장
[표 3-1] 연구 및 실험 요구사항
[표 3-2] RAG-Cube 여덟 조건
[표 3-3] 실험 요인별 적용 위치와 비교 단위

## 4장
[표 4-1] 실험 실행 환경
[표 4-2] 고정 Paper-RAG backbone 설정
[표 4-3] RAG-Cube 조건별 평균 생성시간
[표 4-4] generation record 주요 저장 필드

## 5장
[표 5-1] 실험 대상 문서와 60개 질의-대상문서 쌍 구성
[표 5-2] RAG-Cube 8개 조건별 평균 품질 지표
[표 5-3] HyDE primary controlled result
[표 5-4] CAD identical-context primary result
[표 5-5] SCD configuration별 Korean ratio / drift
[표 5-6] SCD matched-pair language summary
[표 5-7] symmetric quality result

필요하면 추가:
[표 5-8] 문서별 exploratory result
또는 부록으로 이동.

표 제목은 위.

---

# 10. STAGE 4 — 시각자료 생성

## 공통 스타일

output:
`docs/PAPER/FINAL/figures/`

각 그림:
- SVG
- PNG 600 dpi

스타일:
- white background
- text `#222222`
- neutral `#AAB2BA`
- HyDE `#2F6BFF`
- CAD `#24866D`
- SCD `#C86A1B`
- Malgun Gothic 또는 한글 호환 sans-serif
- 그림 내부 큰 장식 제목 금지
- gradient/drop shadow 금지
- grayscale readable
- 숫자 직접 표시
- thesis caption이 제목 역할

## 그림 목록

### [그림 1-1]
한국어 질의 기반 영어 학술문서 RAG 연구 환경

### [그림 3-1]
RAG-Cube 2×2×2

### [그림 3-2]
실험 전체 아키텍처

### [그림 4-1]
Paper-RAG detailed pipeline

정확한 흐름:
Korean query
→ HyDE branch for dense
→ original query for BM25
→ fusion
→ reranker
→ context
→ Mi:dm logits
→ CAD
→ SCD
→ token
→ answer

### [그림 4-2]
generation artifact → evaluation/analysis → tables/figures

### [그림 5-1]
60-query evaluation design

예상:
- HyDE primary n=60
- CAD primary n=actual identical count
- SCD language n=240
- symmetric n=actual identical count

### [그림 5-2]
RAG-Cube 8×4 quality matrix

### [그림 5-3]
HyDE/CAD primary forest plot

### [그림 5-4]
HyDE/CAD stratum-delta matrix

### [그림 5-5]
SCD 240-pair language-adherence plot
- slope/paired distribution
- mean
- drift count
- H×C strata
- identical-context subset

60-query에서 240 lines가 너무 복잡하면:
- alpha를 낮추거나
- violin + paired mean
- ECDF + mean
등 더 읽기 좋은 학술형 시각화로 변경.
개별 pair 정보를 완전히 숨기지 않는다.

### [그림 5-6]
Symmetric quality forest
judge × language.

### [그림 5-7]
Normal QA evidence panel

### [그림 5-8]
Language drift + SCD rescue evidence

### [그림 5-9]
HyDE retrieval-change evidence

### [그림 5-10]
CAD balanced identical-context cases
- positive example
- negative/trade-off example

---

# 11. Evidence-case 재선정

60-query dataset에서 사례를 다시 선정한다.

19-query E01~E08 selector를 그대로 고정하지 않는다.
선정 규칙은 유지하되 **60-query final artifact에서 다시 뽑는다.**

## Normal QA
Korean ratio ≥0.5이고
quality score가 안정적인 실제 사례.

## Language drift
SCD OFF 중 낮은 Korean ratio 사례.

## SCD rescue
- identical context
- SCD OFF drift
- SCD ON threshold recovery
- 큰 positive Korean-ratio delta

## HyDE retrieval change
- H0C0S0 vs H1C0S0
- retrieved IDs differ
- answer relevance/faithfulness 변화가 명확
- extreme case라면 caption에 selection rule 표시

## CAD balanced cases
H0/S0 identical-context pair에서:
1. CAD positive faithfulness example
2. CAD negative/trade-off example

`evidence_manifest_60q.json`에:
- query_id
- target paper
- config A/B
- selection rule
- source files
- context identity
- retrieved/reranked identity
- displayed text range
- metric
기록.

Stored answer/context text를 새로 생성, 번역, 다듬지 않는다.
생략은 `… [이하 생략]`으로 표시.

---

# 12. STAGE 5 — 표·그림 검증

논문 작성 전에 자동 검증:

- figure 값 = derived CSV 값
- derived CSV = source artifact 값
- 표 값 = derived CSV 값
- caption의 n = actual pair count
- evidence text = stored artifact exact text
- evidence metric = source evaluation exact value
- Korean font render
- no clipping
- no overlap
- no tiny labels
- no misleading axis
- legend correct
- grayscale readable

생성:
`docs/PAPER/FINAL/FIGURE_INDEX.md`

각 행:
- figure no.
- filename
- section
- source
- claim
- validation

---

# 13. STAGE 6 — 한글 이전용 최종 논문 작성

표·그림 검증이 끝난 후에만 원고를 작성한다.

출력:
`docs/PAPER/FINAL/GRADUATION_REPORT_TRANSFER_KO_60Q.md`

필요하면 연구용 clean version:
`docs/PAPER/FINAL/THESIS_KO_60Q.md`

## 분량 목표

한글 10pt, 학교 기본 여백, 줄간격 150~160%, 표·그림 포함 기준으로
대략 30~40쪽 수준의 내용 밀도를 목표로 한다.

페이지를 인위적으로 채우지 않는다.
다음을 충분히 풀어 쓴다.

- 연구 동기
- 기존 연구와 기법
- 실험 설계 근거
- 구현 세부
- query/document 구성
- 평가 설계
- 8 config 전체
- 각 요인
- 조합별 패턴
- runtime
- 실제 사례
- 종합 논의
- 한계

---

# 14. 최종 논문 목차

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

3단계 번호는 사용하지 않는다.
5.8 내부는:
- 사례 1.
- 사례 2.
형태.

---

# 15. 한컴 한글 양식

원본 템플릿 style name을 유지한다.

예:
- `본문`
- `장(1.)`
- `절(1.1)`
- `목차제목`
- `목차리스트(장)`
- `목차리스트(절)`
- `표/그림리스트`
- `논문제목`
- `부록제목`
- `참고문헌제목`
- `표제목`
- `표내용`
- `그림제목`
- `참고문헌리스트`

Markdown transfer manuscript에서:
`[스타일=...]`
marker를 유지해 HWP로 옮길 위치를 표시한다.

표 제목은 위.
그림 제목은 아래.

---

# 16. 한컴 수식 입력기

수식 번호를 새로 만들지 않는다.
`[수식 2-1]`, `(2-1)` 형식 금지.

본문 설명 뒤에 수식 자체만 둔다.

한컴 입력용 exact strings:

검색:
`C_q = Retrieve(q,D)`

생성:
`y = LM(q,C_q)`

RRF:
`RRF(d) = {0.6} over {k + rankDense(d)} + {0.4} over {k + rankBM25(d)}`

CAD:
`z_{CAD} = (1 + alpha) z_{ctx} - alpha z_{noctx}`

SCD Korean:
`tilde z_i = alpha z_i`
조건 `i in V_{ko}`

SCD English:
`tilde z_i = beta z_i`
조건 `i in V_{en}`

SCD neutral:
`tilde z_i = z_i`
조건 `i in V_{neutral}`

Pair delta:
`Delta_i = s_i(ON) - s_i(OFF)`

Korean ratio:
`KoreanRatio = {N_{Hangul}} over {N_{Hangul} + N_{ASCII}}`

60-query final generation:
`60 times 8 = 480`

실제 final query count가 60인지 검증한 뒤 사용.

`docs/PAPER/FINAL/HWP_EQUATION_INPUTS_60Q.txt`
도 별도 생성.

---

# 17. 참고문헌

본문의 실제 first appearance 순서와 bibliography를 1:1 대응시킨다.

반드시 역할을 구분:
- RAG
- RAG Survey
- HyDE
- CAD
- SCD
- BGE-M3
- BM25
- RRF
- BERT reranking
- MS MARCO
- Lost in the Middle
- Contrastive Decoding
- 국내 CAD 관련
- 국내 HyDE 관련
- RAGAS
- 국내 RAG evaluation
- BERGEN
- GPT-4o System Card
- multilingual LLM-as-Judge
- Mi:dm 2.0
- RAPTOR
- Mi:dm K 2.5 Pro
- Alice/EliceCloud environment reference

Mi:dm 2.0 = generator
Mi:dm K 2.5 Pro = target document

---

# 18. STAGE 7 — 최종 validation

생성:
`docs/PAPER/FINAL/VALIDATION_REPORT_60Q.md`

## Data
- query count = 60
- config count = 8
- generations = 480
- each config = 60
- paper counts
- unique query IDs
- model
- params

## Analysis
- HyDE pair count
- CAD identical pair count
- SCD matched pair count
- symmetric pair count
- all mean/CI/WLT
- config means
- runtime
- language result

## Manuscript
- 60-query 수치만 존재
- 19-query 수치 잔존 여부 검사
- 과거/레거시 회고 문구 없음
- service/UI 내용 없음
- no 3-level headings
- figure/table references valid
- bibliography complete
- HWP equation syntax present
- equation numbering absent

## Figure
- all expected figures exist
- SVG + PNG
- no clipping
- source verified
- evidence exact

모든 critical check가 PASS여야 최종 완료.

---

# 19. 최종 완료 보고

Codex 최종 응답은 다음만 간결하게 보고한다.

1. 60-query experiment result path
2. validation result
3. 주요 결과 5~10줄
4. 기존 교정안에서 수정된 핵심 논리
5. 생성 표 목록
6. 생성 그림 목록
7. 최종 HWP-transfer manuscript path
8. 사람이 마지막으로 확인할 항목
   - HWP 페이지 배치
   - 표·그림 크기
   - 지도교수/제출일
   - 목차 페이지 번호
   - 참고문헌 최종 서식

설명만 하고 끝내지 말고 실제 파일을 생성한다.
