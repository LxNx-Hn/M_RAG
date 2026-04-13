<!-- markdownlint-disable MD022 MD024 MD032 MD040 MD046 -->
# M-RAG 작업 추적 문서

> **목적**: 세션이 끊겨도 진행 상황을 이어갈 수 있도록 작업 체크리스트를 관리합니다.  
> **마지막 업데이트**: 2026-04-10  
> **현재 단계**: PHASE 0 시작

---

## 이미 완료된 항목 (이전 세션, 재작업 금지)

- [x] `docs/COMPETITIVE_ANALYSIS.md` 신규 작성
- [x] `docs/ACADEMIC_CLAIMS.md` 신규 작성
- [x] `docs/CRITIQUE_AND_IMPROVEMENTS.md` 신규 작성
- [x] `docs/ARCHITECTURE.md` 13 모듈로 통일 + M13A/M13B 분리
- [x] `CLAUDE.md` 13 모듈로 통일 + M13A/M13B 분리
- [x] `backend/config.py`: 한국어 SECTION_PATTERNS 보강 + GENERAL_DOC_PATTERNS 추가
- [x] `backend/modules/section_detector.py`: 문서 유형 자동 판별(paper/general) + 일반 문서 패턴 적용
- [x] `backend/evaluation/test_queries.json`: v2.1, 55개, `_meta` + `_validation_guide`
- [x] `backend/evaluation/ragas_eval.py`: `compare_cad_on_off()` + v2.1 로더
- [x] `backend/evaluation/ablation_study.py`: `run_cad_korean_evaluation()` + cad_decoder 임포트 정정

---

## PHASE 0 — 레이아웃 인식 추출 + 강의 도메인 확장

### T0a. requirements.txt — pymupdf4llm 추가

- [ ] `pymupdf4llm>=0.0.17` 추가
- 이유: pymupdf 공식 LLM-friendly 어댑터 (코드 블록, 표, 헤딩, 다중 컬럼 → markdown)

### T0b. pdf_parser.py — 구조 보존 모드 (핵심, 높은 위험도)

- [ ] `TextBlock.block_type`에 새 값: `"code"`, `"heading"`, `"list_item"`, `"math"`
- [ ] `parse()` 내부에서 pymupdf4llm.to_markdown() 병합 호출
- [ ] 표 보존: pymupdf4llm markdown 표 → `block_type="table"`
- [ ] 수식 보존: 폰트명(math/stix/cmsy 등) + 유니코드 밀도 ≥25% → `block_type="math"`
- [ ] 코드 블록: markdown ``` 펜스 → `block_type="code"`
- [ ] 헤딩: markdown #/##/### → `block_type="heading"` + header_level
- [ ] fallback: pymupdf4llm 실패 시 기존 raw 추출만 사용

### T0c. chunker.py — 구조 블록 보존 로직

- [ ] `block_type in ("code", "table", "math")` → 분할 금지
- [ ] 청크 메타데이터에 `is_structured=True` + `structured_type`
- [ ] 수식 블록 인접 텍스트에 `[수식 참조]` 앵커

### T0d. config.py — LECTURE_PATTERNS 추가

- [ ] definition/theorem/proof/example/exercise/code_block/chapter/section 패턴

### T0e. section_detector.py — lecture 유형 분기

- [ ] `_LECTURE_SIGNALS` 정규식
- [ ] `_detect_document_type()` → 3분류 (paper/lecture/general)
- [ ] `LECTURE_SECTION_ORDER` 추가
- [ ] `get_section_order()` lecture 분기

---

## PHASE 0.5 — 특허 문서 도메인 확장

### T0k. config.py — PATENT_PATTERNS + ROUTE_MAP 특허 키워드

- [ ] 특허 섹션 패턴 11종 (title/abstract/technical_field/background/...)
- [ ] ROUTE_MAP citation에 특허 키워드 추가

### T0l. section_detector.py — patent 유형 추가

- [ ] `_PATENT_SIGNALS` 정규식
- [ ] `_detect_document_type()` → 4분류 (paper/lecture/patent/general)
- [ ] `PATENT_SECTION_ORDER` 추가

### T0m. patent_tracker.py — 신규 생성

- [ ] PatentInfo dataclass
- [ ] parse_cited_patents(): 특허 번호 파싱 (KR/US/JP/EP/WO)
- [ ] fetch_from_google_patents(): Google Patents HTML 파싱
- [ ] fetch_from_kipris(): 선택적 (KIPRIS API 키 설정 시만)
- [ ] search_similar_patents(): 청구항 키워드 기반 검색

### T0n. pipeline_d_citation.py — paper/patent 분기

- [ ] doc_type == "patent" → patent_tracker 경로

### T0o. dependencies.py — patent_tracker 싱글턴

- [ ] ModuleManager에 patent_tracker 추가

### T0p. (T0k에 합침)

---

## PHASE 0 문서 업데이트

### T0f~T0i + T0r — 문서 업데이트

- [ ] COMPETITIVE_ANALYSIS.md: 강의/교재 + 특허 섹션 추가
- [ ] ACADEMIC_CLAIMS.md: 검증 vs 적용 범위 분리 + 특허 추가
- [ ] CRITIQUE_AND_IMPROVEMENTS.md: L1/L2/L8 멀티모달 문구 교체 + arXiv 한계에 특허 언급
- [ ] CLAUDE.md: "논문 특화" → "학술/교육 PDF", M1 설명 보강, Pipeline D 설명 보강
- [ ] ARCHITECTURE.md: 동일 표현 정정 + TextBlock 스키마 업데이트

### T0j+T0q — test_queries.json 확장

- [ ] lecture 쿼리 8개 추가 (type: "lecture")
- [ ] patent 쿼리 6개 추가 (type: "patent")
- [ ] _validation_guide에 lecture_E_compiler, patent_F_kr_ai 추가

---

## PHASE 1 — 문서 잔작업

### T1. CRITIQUE_AND_IMPROVEMENTS.md lint 수정

- [ ] MD032/MD060/MD009 경고 수정 (T0h와 합쳐 수행)

---

## PHASE 2 — 평가 데이터 개선

### T2. test_queries.json — ground_truth 전략

- [ ] cad_ablation 쿼리에 `ground_truth_template` + `ground_truth_source_section` 추가

### T3. ragas_eval.py — None-aware 평가

- [ ] `_mean_skip_none()` 헬퍼
- [ ] ground_truth 빈 문자열 시 `context_recall=None`
- [ ] ablation_study.py `format_results_table()`에도 동일 적용

---

## PHASE 3 — Citation Tracker + L5 뷰어 백엔드

### T4. citation_tracker.py — graceful fallback

- [ ] `fetch_error: Optional[str]` 필드 추가
- [ ] arXiv 미등록 시 `"arxiv_not_found"` 설정

### T5. schemas.py — CitationItem 확장

- [ ] `fetch_error: Optional[str] = None`

### T6. citations.py — 엔드포인트 분리

- [ ] `POST /api/citations/list` (메타데이터만)
- [ ] `POST /api/citations/download` (단일 다운로드+인덱싱)

---

## PHASE 4 — Pipeline F (퀴즈 생성)

### T7. pipeline_f_quiz.py — 신규 생성

- [ ] run() 함수: 섹션별 검색 → 객관식 5문제 생성 프롬프트
- [ ] use_cad=True 강제

### T8. query_router.py — RouteType.F + quiz 슬롯

- [ ] F 라우팅 추가

### T9. config.py — ROUTE_MAP quiz

- [ ] `"quiz": ["문제", "퀴즈", "연습", "시험", "quiz", "exercise", "출제"]`

### T10. chat.py — F 분기

- [ ] `route.route == "F"` 분기 추가

### T11. schemas.py — F 라벨

- [ ] `F: "퀴즈 생성"` 추가

---

## PHASE 5 — 프론트엔드 인용 뷰어 패널

### T12. CitationPanel.tsx — 신규

- [ ] 참고문헌 탭 UI (제목/저자/연도/상태/다운로드 버튼)

### T13. PDFViewer.tsx — 탭 토글

- [ ] PDF 뷰어 / 참고문헌 탭 전환 (display:none으로 상태 보존)

### T14. citations.ts — API 클라이언트

- [ ] listCitations(), downloadCitation()

---

## PHASE 6 — 배포·실험 진입점

### T15. run_c3_experiment.py — C3 실험 한 줄 실행

- [ ] 인덱싱 → load_test_queries → compare_cad_on_off → run_cad_korean_evaluation
- [ ] GPU 미존재 시 스킵 + 경고

### T16. verify_deployment.py — 배포 sanity check

- [ ] 모듈 임포트 + ChromaDB + 환경변수 체크

### T17. docker-compose.yml 검증

- [ ] 볼륨/의존성 확인

---

## 핵심 원칙

1. **PHASE 순서 준수** — 0 → 0.5 → 1 → 2 → 3 → 4 → 5 → 6
2. **텍스트 전용 정책** — 멀티모달 기능 범위 외
3. **검증/적용 분리** — 논문=C1~C4 검증, 강의/특허=시연
4. **graceful fallback** — 모든 외부 의존성 실패에 우아한 처리
5. **회귀 차단** — 기존 5 파이프라인 깨뜨리지 않기
6. **기존 완료 작업 재작업 금지**

이전까지 검증후 수행할것
PHASE 0: T0f~T0i+T0r — 문서 업데이트 (4개 docs + CLAUDE.md + ARCHITECTURE.md)

PHASE 0: T0j+T0q — test_queries.json lecture 8개 + patent 6개 추가

PHASE 1: T1 — CRITIQUE markdown lint 수정

PHASE 2: T2+T3 — ground_truth 전략 + None-aware 평가

PHASE 3: T4+T5+T6 — citation_tracker fallback + citations API 분리

PHASE 4: T7~T11 — Pipeline F 퀴즈 생성

PHASE 5: T12~T14 — 프론트엔드 인용 뷰어 패널

PHASE 6: T15+T16 — C3 실험 스크립트 + 배포 검증

PHASE 6: T17 — docker-compose 검증

# M-RAG: 차별점 강화 + 즉시 배포·논문 실험 가능 상태로 마무리

## Context

이전 세션에서 NotebookLM 대비 학술 RAG 차별점 강화, C1~C4 학술 클레임 정리, 13 모듈/5 파이프라인 구조 통일, 일반 문서 섹션 감지, RAGAS/Ablation 평가 코드 확장까지 상당 부분 완료했음.

**이번 세션 추가 발견 (사용자 스크린샷 + 피드백)**:

1. **강의 PDF 구조 보존**: NotebookLM이 일반 강의 PDF(BNF 문법, EBNF, 코드 블록, 다중 컬럼 ①②③ 참조)에서도 **구조 보존 추출**을 수행. 현재 M-RAG의 `pdf_parser.py`는 raw 텍스트 블록 추출만 가능하여 코드/문법/수식 블록 구조가 손실됨.
2. **특허 문서 도메인 확장 (사용자 명시 요구)**: "특허 문서에 대해서도 유사 특허와 참고 특허를 확인할 수 있게 확장" — 논문용 Pipeline D(arXiv 인용 추적)의 특허 버전을 구현. 특허 명세서 섹션(청구항/배경기술/상세한 설명) 인식, 인용 특허 파싱, Google Patents / KIPRIS API 연동.

이 두 격차를 메우면:

- **포지셔닝 변경**: "논문 특화" → "학술 + 강의/교재 + 특허 문서 범용 RAG" (검증은 논문, 적용은 더 넓게)
- **arXiv 한계 은폐**: 강의/교재/특허는 arXiv 의존도 0
- **실용성 확대**: 특허 실무자, 지재권 연구자까지 타겟 확장

3. **추가 질문 제안 + 퀴즈 후속 연계 (사용자 명시 요구)**: "노트북 LM의 기능은 다 가지되 우리만의 특색을 가지는걸로 가야지" — NotebookLM의 (1) 답변 후 추천 질문 말풍선, (2) 퀴즈 생성 + 후속 질문 연계 기능을 M-RAG 특색으로 구현. M-RAG 차별점: **라우트 인식 추천** (파이프라인 경로에 따라 다른 후속 질문 제안) + **CAD 강제 퀴즈** (환각 억제된 문제 생성).

이 세 격차를 메우면:

- **포지셔닝 변경**: "논문 특화" → "학술 + 강의/교재 + 특허 문서 범용 RAG" (검증은 논문, 적용은 더 넓게)
- **arXiv 한계 은폐**: 강의/교재/특허는 arXiv 의존도 0
- **실용성 확대**: 특허 실무자, 지재권 연구자까지 타겟 확장
- **UX 경쟁력**: NotebookLM 동등 대화형 UX + 라우트 인식 추천으로 차별화

이번 작업의 목표는 **남은 잔작업 + 잠재 이슈 + 위 신규 요구사항을 전부 해소**하여, 적용 직후 (1) 도커 배포, (2) C3 핵심 논문 실험 실행, (3) 강의 PDF 시연, (4) 특허 문서 시연, (5) 추천 질문 + 퀴즈 시연이 한 번에 가능한 상태로 만드는 것.

### 이미 완료된 항목 (재작업 금지)

- `docs/COMPETITIVE_ANALYSIS.md`, `docs/ACADEMIC_CLAIMS.md`, `docs/CRITIQUE_AND_IMPROVEMENTS.md` 신규 작성
- `docs/ARCHITECTURE.md`, `CLAUDE.md` 13 모듈로 통일 + M13A/M13B 분리
- `backend/config.py`: 한국어 SECTION_PATTERNS 보강 + GENERAL_DOC_PATTERNS 추가
- `backend/modules/section_detector.py`: 문서 유형 자동 판별 + 일반 문서 패턴 적용
- `backend/evaluation/test_queries.json`: v2.1, 55개, `_meta` + `_validation_guide`
- `backend/evaluation/ragas_eval.py`: `compare_cad_on_off()` + v2.1 로더
- `backend/evaluation/ablation_study.py`: `run_cad_korean_evaluation()` + cad_decoder 임포트 정정

### 남은 잔작업 / 잠재 이슈

| 영역 | 이슈 | 영향 |
|---|---|---|
| **파서** | `pdf_parser.py`가 raw block 추출만 → 코드/문법/수식 블록 손실 | **NotebookLM 동등 기능 미달** |
| **도메인** | 특허 문서 지원 없음 — 청구항/배경기술/인용 특허 인식 불가 | 사용자 명시 요구 미충족 |
| **포지셔닝** | "논문 특화" 표현이 강의/특허 시연을 가림 | 시연 폭 좁음 |
| 문서 | `CRITIQUE_AND_IMPROVEMENTS.md` markdown lint 경고 | 표시 깨짐 가능성 |
| 평가 | `cad_ablation` 5개 쿼리의 `ground_truth`가 `""` | C3 표 절반만 집계 |
| 평가 | C3 실험을 한 줄로 실행할 진입점 스크립트 부재 | 사용자가 코드 작성 필요 |
| 코드 | `citation_tracker.py`가 arXiv 미등록 시 사용자 안내 없음 | L5 한계 노출 안 됨 |
| 코드 | `/api/citations` 라우터가 `track`만 있음 | 프론트 뷰어 패널 구현 불가 |
| 기능 | Quiz 생성 Pipeline F (사용자 명시 요구) | 미구현 |
| **UX** | 답변 후 추천 질문 말풍선 (NotebookLM 동등) | **미구현** |
| **UX** | 퀴즈 후속 질문 연계 ("왜 틀렸는지 설명해줘") | **미구현** |
| 프론트 | 인용 논문 뷰어 패널 (L5 사용자 제안) | 미구현 |
| 배포 | docker-compose 환경 신규 의존성/볼륨 검증 안 됨 | 빌드 실패 가능 |

---

## 작업 순서 (PHASE 0 → 0.5 → 1 → 2 → 3 → 3.5 → 4 → 5 → 6, 순차 실행)

### PHASE 0 — 레이아웃 인식 추출 + 문서 도메인 확장 (논문/강의/특허)

> 이 단계가 완료되어야 (a) 강의 PDF에서 코드/BNF/수식 블록 보존, (b) 특허 PDF에서 청구항/인용 특허 추적이 가능. C3 논문 실험과는 독립적이므로 병행 가능.

**T0a.** [backend/requirements.txt](backend/requirements.txt) — `pymupdf4llm>=0.0.17` 추가

- 이유: pymupdf 공식 LLM-friendly 어댑터. 코드 블록(monospace 폰트), 표, 헤딩, 다중 컬럼을 markdown으로 출력.
- 라이선스: AGPL (pymupdf와 동일) — 학술 프로젝트 OK

**T0b.** [backend/modules/pdf_parser.py](backend/modules/pdf_parser.py) — 구조 보존 모드 추가 (텍스트 전용, 멀티모달 無)

- `TextBlock.block_type`에 새 값 추가: `"code"`, `"heading"`, `"list_item"`, `"math"` (기존 `"text"`, `"table"`, `"image"` 유지)
- `parse()` 메서드 내부에서 두 단계 실행:

  1. 기존 raw block 추출 (현재 로직 그대로) — 폰트/bbox/span 단위 감지용
  2. **신규** `pymupdf4llm.to_markdown(pdf_path, page_chunks=True)` 호출 → 페이지별 markdown 추출
  3. 두 결과를 페이지 번호로 매칭해 병합 — bbox/font 정보는 raw에서, structured 마크다운은 pymupdf4llm에서

- **표 보존**: pymupdf4llm이 markdown 표로 변환한 영역을 묶어 `block_type="table"` + `markdown` 원본을 `TextBlock.content`에 그대로 저장. 기존 `extract_tables()` fallback 유지 (pymupdf4llm이 놓친 표는 pymupdf find_tables로 보강)
- **수식 보존** (이미지/OCR 없이 텍스트·폰트 기반):

  - span 단위 추출 시 `font` 이름에 `(?i)(math|stix|cmsy|cmex|cmmi|cmr|symbol|asana)` 포함되면 math span으로 마킹
  - 또는 span 텍스트가 유니코드 수학 기호(`[∀∃∑∏∫√≤≥≠≈∞αβγδθλμπσφω∂∇⊕⊗]` 외 Block `Mathematical Operators`, `Greek`)를 25% 이상 포함하면 math 마킹
  - math span이 연속된 영역(동일 줄 또는 인접 bbox) → `block_type="math"` 단일 블록으로 묶어 보존
  - 결과: display 수식은 독립 블록, inline 수식은 기존 text 블록 내 유니코드 그대로 유지 (pymupdf가 이미 유니코드로 추출함)

- **코드 블록 감지**: markdown ` ``` ` 펜스 영역 → `block_type="code"`
- **헤딩 감지**: markdown `#`/`##`/`###` → `block_type="heading"` + `header_level` 메타
- **fallback**: pymupdf4llm 임포트 실패 시 기존 raw 추출만 사용 (graceful degradation), 수식 폰트 기반 감지는 raw 경로에서도 동작

**T0c.** [backend/modules/chunker.py](backend/modules/chunker.py) — 구조 블록 보존 로직

- `_chunk_by_section()`에서 `block_type in ("code", "table", "math")`인 블록은:

  - **분할 금지** — 청크 크기를 초과하더라도 단일 청크로 유지 (수식/표가 잘려 의미 손실되는 것 방지)
  - 청크 메타데이터에 `is_structured=True` + `structured_type` 표시

- 일반 텍스트 블록과 구조 블록을 섞어 청킹할 때, 구조 블록은 청크 경계로 사용 (앞/뒤 텍스트 분리)
- 수식 블록이 해설 문단과 인접한 경우: 수식 블록은 독립 청크로 두되, 바로 앞 텍스트 청크 끝에 `[수식 참조]` 앵커 삽입 (검색 시 맥락 연결용)

**T0d.** [backend/config.py](backend/config.py) — 강의/교재 패턴 추가
```python
LECTURE_PATTERNS = {
    "definition": [r"(?i)^(definition|정의|정\.|def\.)\s*\d*"],
    "theorem": [r"(?i)^(theorem|정리|thm\.)\s*\d*", r"(?i)^lemma\s*\d*"],
    "proof": [r"(?i)^(proof|증명)\b"],
    "example": [r"(?i)^(example|예제|예\.|보기)\s*\d*"],
    "exercise": [r"(?i)^(exercise|연습\s*문제|문제|practice)\s*\d*"],
    "code_block": [r"(?i)^(코드|예제\s*코드|listing|algorithm)\s*\d*"],
    "chapter": [r"(?i)^chapter\s+\d+", r"^제\s*\d+\s*장"],
    "section": [r"^\d+\.\d+\s+", r"^제\s*\d+\s*절"],
}
```

**T0e.** [backend/modules/section_detector.py](backend/modules/section_detector.py) — 강의 문서 유형 분기

- `_LECTURE_SIGNALS` 정규식 추가: `(?i)(강의|강의노트|lecture|syllabus|예제|연습\s*문제|exercise|definition|theorem|proof|BNF|EBNF|algorithm)`
- `_detect_document_type()` 반환값을 3분류로 확장: `"paper"` / `"lecture"` / `"general"`

  - 카운팅: paper_count, lecture_count, general_count 중 최대값으로 결정
  - 동점 시 우선순위: lecture > paper > general

- `LECTURE_SECTION_ORDER = ["chapter", "section", "definition", "theorem", "proof", "example", "exercise", "code_block"]`
- `get_section_order()`도 lecture 분기 추가
- `detect()`가 lecture 유형이면 `LECTURE_PATTERNS` 사용

**T0f.** [docs/COMPETITIVE_ANALYSIS.md](docs/COMPETITIVE_ANALYSIS.md) — 강의/교재 처리 섹션 신규 추가

- 신규 섹션: "## 강의/교재 PDF 처리 (NotebookLM 동등 + α)"

  - NotebookLM 스크린샷 케이스 (BNF/EBNF/코드 블록) 설명
  - M-RAG의 `pymupdf4llm` 기반 구조 보존 추출 설명
  - 비교 표: 코드 블록 보존 / 다중 컬럼 / 표 / 수식 — 양쪽 모두 ✓로 표시 (M-RAG 동등성 확보)
  - **추가 우위**: M-RAG는 chunker 단에서 구조 블록 분할 금지 → LLM이 BNF 문법을 깨뜨리지 않고 인용 가능

**T0g.** [docs/ACADEMIC_CLAIMS.md](docs/ACADEMIC_CLAIMS.md) — 클레임 범위 명확화

- C1~C4는 그대로 유지 (논문에서 검증)
- 새 섹션 "## 검증 vs 적용 범위 (포지셔닝)" 추가:

  - **검증**: 학술 논문 4편 (RAGAS + Ablation, C1~C4 표)
  - **적용**: 학술 논문 + 한국어 논문 + 강의/교재 PDF + 특허 명세서 + 일반 기술 문서
  - **강의/특허 시연**: 기능 적용 시연용이며 정량 평가는 논문 도메인에서만 수행

- 기존 "한계" 섹션의 "논문 특화" 표현 → "검증 도메인은 논문, 적용 도메인은 광범위" 로 정정

**T0h.** [docs/CRITIQUE_AND_IMPROVEMENTS.md](docs/CRITIQUE_AND_IMPROVEMENTS.md) — Section 0 보강 + 멀티모달 관련 문구 전면 제거

- arXiv 미등록 한계 문단 마지막에 추가:

  > **단, 강의/교재/특허/기술문서 시연 모드에서는 arXiv 의존도가 0이므로 이 한계가 비활성화된다.** Pipeline D(인용 추적)는 학술 논문 모드에서는 arXiv, 특허 모드에서는 Google Patents로 분기되며, 일반 문서 모드에서는 라우팅되지 않는다.

- **L1 (수식 처리) 문단 전면 교체**:

  > pymupdf4llm + 폰트/유니코드 기반 수식 감지로 해결. Math 폰트(CMSY/STIX/Symbol) 또는 유니코드 수학 기호 밀도 ≥25%인 span을 `block_type="math"` 블록으로 묶고 chunker에서 분할 금지. 인라인 수식은 유니코드 그대로 텍스트 블록에 포함. **LaTeX 원본 복원은 수행하지 않음** (이미지 기반 OCR은 멀티모달 정책에 의해 제외).

- **L2 (Figure/Table) 문단 전면 교체**:

  > **표(Table)**: pymupdf4llm이 markdown 표로 변환하여 보존 + pymupdf `find_tables()` fallback. chunker에서 분할 금지. **Figure/이미지 QA는 지원하지 않음** — 멀티모달 정책에 의해 Vision-LM 의존 기능은 제외. Figure 캡션 텍스트만 검색 가능.

- **L3 (스캔 PDF OCR) 문단 유지**: OCR은 이미지 인식이 아닌 광학 문자 인식이므로 멀티모달과 구분됨. Phase 2(중기)로 유지하되, 본 plan 범위 밖.
- **L8 (멀티모달 입력) 문단 전면 교체**:

  > **정책**: M-RAG는 텍스트 전용 RAG로 유지. YouTube/오디오/Vision-LM/이미지 QA는 모두 범위 외. 슬라이드 PDF는 T0b 적용 후 코드/문법/표/수식 블록이 모두 텍스트 레벨에서 보존되므로 별도 멀티모달 없이 처리 가능.

- L2에 있던 "향후: Vision-Language Model(LLaVA, InternVL)로 그림 설명 자동 생성" 문구 **삭제**
- L1에 있던 "향후: LaTeX-OCR 또는 Mathpix API로 수식을 LaTeX 문자열로 변환" 문구 **삭제**
- Phase 3 장기 로드맵에서 "Figure/Table Vision QA (LLaVA)", "LaTeX-OCR 수식 파싱" 항목 **삭제**

**T0i.** [CLAUDE.md](CLAUDE.md) 및 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 표현 정정

- "논문 특화" / "학술 논문 PDF" → "학술/교육 PDF (논문 + 강의/교재)"로 통일
- M1 (PDF Parser) 설명에 `pymupdf4llm 기반 구조 보존 추출` 명시
- 데이터 스키마 섹션의 `TextBlock`에 새 block_type 값 4종 (`text/heading/code/table/list_item/image`) 명시

**T0j.** [backend/evaluation/test_queries.json](backend/evaluation/test_queries.json) — 강의 쿼리 8개 추가

- 신규 type: `"lecture"`
- 추천 테스트 자료에 `lecture_E_compiler` 추가 (예: 컴파일러/이산수학 강의 PDF)
- 쿼리 예시:

  ```
  "이 강의에서 BNF의 정의가 정확히 뭐야?" (코드 블록 보존 검증)
  "Definition 2.1을 그대로 인용해줘" (정의 블록 보존)
  "예제 3번의 풀이 과정을 단계별로 설명해줘" (예제 분리 검증)
  "이 강의에서 EBNF가 BNF와 다른 점이 뭐야?" (다중 정의 검색)
  "Theorem 3.2의 증명을 보여줘" (정리/증명 페어)
  "연습문제 5번의 정답이 뭐야?" (exercise 섹션 검색)
  "이 챕터의 핵심 개념을 정리해줘" (E경로 + 강의 모드)
  "강의 슬라이드의 코드 예제를 그대로 출력해줘" (코드 블록 원형 보존)
  ```

---

### PHASE 0.5 — 특허 문서 도메인 확장 (사용자 명시 요구)

> 특허 PDF 업로드 → 섹션 자동 인식(청구항/배경기술/상세한 설명) → 유사 특허/인용 특허 추적. Pipeline D(arXiv)의 특허 버전.

**T0k.** [backend/config.py](backend/config.py) — 특허 섹션 패턴 추가
```python
PATENT_PATTERNS = {
    "title": [r"(?i)^(발명의\s*명칭|title\s*of\s*(the\s*)?invention)"],
    "abstract": [r"(?i)^(요약|초록|abstract)\s*$"],
    "technical_field": [r"(?i)^(기술\s*분야|technical\s*field)"],
    "background": [r"(?i)^(배경\s*기술|background\s*art|prior\s*art)"],
    "summary": [r"(?i)^(발명의\s*요약|summary\s*of\s*(the\s*)?invention)"],
    "problem": [r"(?i)^(해결하려는\s*과제|problems?\s*to\s*be\s*solved)"],
    "solution": [r"(?i)^(과제의\s*해결\s*수단|means?\s*of\s*solving|solution\s*to\s*problem)"],
    "detailed_description": [
        r"(?i)^(발명의\s*상세한\s*설명|detailed\s*description|description\s*of\s*embodiments?)",
        r"(?i)^(발명을\s*실시하기\s*위한\s*구체적인\s*내용)",
    ],
    "drawings": [r"(?i)^(도면의\s*간단한\s*설명|brief\s*description\s*of\s*(the\s*)?drawings?)"],
    "claims": [r"(?i)^(청구(의)?\s*범위|청구항|claims?)\s*$", r"^【청구항\s*\d+】"],
    "cited_patents": [r"(?i)^(인용\s*문헌|선행\s*기술\s*문헌|references?\s*cited|cited\s*patents?)"],
}
```

**T0l.** [backend/modules/section_detector.py](backend/modules/section_detector.py) — 특허 문서 유형 추가

- `_PATENT_SIGNALS = re.compile(r"(?i)(청구항|특허\s*출원|발명의\s*명칭|patent|invention|embodiment|claim\s*\d+|prior\s*art|KR\s*\d{2}-\d{4}-\d{7}|US\s*\d{7,})")`
- `_detect_document_type()` 반환을 4분류로 확장: `"paper"` / `"lecture"` / `"patent"` / `"general"`

  - 카운팅: 각 신호 카운트 후 최대값 결정
  - 특허 우선순위는 patent > lecture > paper > general (특허 키워드가 매우 독특하여 오판 낮음)

- `PATENT_SECTION_ORDER = ["title", "abstract", "technical_field", "background", "summary", "problem", "solution", "detailed_description", "drawings", "claims", "cited_patents"]`
- `get_section_order()` patent 분기 추가
- `detect()`가 patent 유형이면 `PATENT_PATTERNS` 사용

**T0m.** `backend/modules/patent_tracker.py` 신규 생성 — 특허 인용/유사 특허 추적 모듈

- `CitationTracker`와 동일 설계 패턴
- `@dataclass PatentInfo`: `patent_id`, `title`, `inventors`, `applicant`, `publication_date`, `abstract`, `pdf_url`, `fetched`, `fetch_error`
- `parse_cited_patents(cited_text)`: 인용 특허 섹션 파싱 → 특허 번호(`KR 10-2020-0012345`, `US 10,000,000`) 추출
- `fetch_from_google_patents(patent_id)`: Google Patents 공개 페이지 스크레이핑 또는 [SerpAPI Google Patents endpoint](https://serpapi.com/google-patents-api) (SerpAPI는 유료 — 무료 대안 우선)
- **무료 구현 기본**: Google Patents 공개 URL 패턴 `https://patents.google.com/patent/<patent_id>` HTML 파싱 (BeautifulSoup)
- `fetch_from_kipris(patent_id)`: [KIPRIS Plus API](https://plus.kipris.or.kr/) 선택적 — 키 설정 시에만 활성화
- `search_similar_patents(claims_text, top_k=5)`: 청구항 키워드 기반 Google Patents 검색 URL 호출 → 상위 5개 후보 메타데이터
- `download_pdf(patent)`, `get_patent_summary()` 메서드 — `CitationTracker`와 시그니처 동일

**T0n.** [backend/pipelines/pipeline_d_citation.py](backend/pipelines/pipeline_d_citation.py) — doc_type 분기 추가

- 기존 arXiv 로직 유지 (paper 유형)
- 신규: 업로드 문서가 patent 유형이면 `patent_tracker.parse_cited_patents()` + `fetch_from_google_patents()` 경로 실행
- **추가 분기**: 쿼리에 "유사 특허" / "similar patent" 키워드 포함 시 `search_similar_patents()` 호출 → 결과를 임시 컬렉션에 인덱싱
- 반환 스키마는 기존과 동일 (`answer`, `sources`, `pipeline: "D"`, `steps`) — 프론트 변경 최소화

**T0o.** [backend/api/dependencies.py](backend/api/dependencies.py) — `ModuleManager`에 `patent_tracker` 싱글턴 추가 (citation_tracker와 동일 패턴)

**T0p.** [backend/config.py](backend/config.py) — `ROUTE_MAP.citation`에 특허 키워드 추가
```python
"citation": ["인용", "참고문헌", "reference", "cited by", "레퍼런스",
             "유사\s*특허", "인용\s*특허", "선행\s*기술", "similar\s*patent", "prior\s*art"],
```

**T0q.** [backend/evaluation/test_queries.json](backend/evaluation/test_queries.json) — 특허 쿼리 6개 추가

- 신규 type: `"patent"`
- 추천 테스트 자료에 `patent_F_kr_ai` 추가 (예: 한국 AI/ML 특허 PDF 1편)
- 쿼리 예시:

  ```
  "이 특허의 청구항 1번을 그대로 인용해줘" (청구항 블록 보존 검증)
  "이 특허의 배경기술에서 언급한 선행 기술이 뭐야?" (background 섹션 검색)
  "이 특허가 해결하려는 과제가 뭐야?" (problem 섹션)
  "이 특허와 유사한 특허를 찾아줘" (유사 특허 검색 — Pipeline D)
  "이 특허의 인용 특허 목록을 보여줘" (인용 특허 파싱)
  "발명의 상세한 설명에서 제시한 실시예가 몇 개야?" (detailed_description + embodiment 카운팅)
  ```

**T0r.** 문서 업데이트 (특허 도메인 반영)

- [docs/COMPETITIVE_ANALYSIS.md](docs/COMPETITIVE_ANALYSIS.md): "특허 문서 처리" 섹션 신규 추가 — NotebookLM도 일반 문서 처리하지만, M-RAG는 특허 섹션 감지 + 유사 특허/인용 특허 API 연동으로 차별화
- [docs/ACADEMIC_CLAIMS.md](docs/ACADEMIC_CLAIMS.md): 적용 범위 목록에 "특허 명세서" 추가
- [docs/CRITIQUE_AND_IMPROVEMENTS.md](docs/CRITIQUE_AND_IMPROVEMENTS.md): Section 0(arXiv 한계)에 특허 도메인 언급 — "특허는 Google Patents / KIPRIS 별도 경로 사용, arXiv 무관"
- [CLAUDE.md](CLAUDE.md) / [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): Pipeline D 설명에 "arXiv(논문) / Google Patents(특허) 분기" 추가, M11(citation_tracker) 옆에 `patent_tracker` 신규 모듈 표기
- **모듈 수 재산정**: 13 → 14 (M11에 patent_tracker 서브 모듈 추가) 또는 M11을 "Reference Tracker (논문 + 특허)"로 묶고 13 유지 — 후자 선택(구조 단순화)

---

### PHASE 1 — 문서 잔작업 (의존성 0)

**T1.** [docs/CRITIQUE_AND_IMPROVEMENTS.md](docs/CRITIQUE_AND_IMPROVEMENTS.md) markdown lint 경고 수정

- MD032: 라인 13, 19, 80, 100, 152, 158 — 리스트 위/아래 빈 줄 추가
- MD060: 라인 26 — 표 헤더/구분선 컬럼 정렬 수정
- MD009: 라인 157 — 후행 공백 제거
- T0h 작업과 합쳐서 한 번에 수정 (lint 0건 목표)

---

### PHASE 2 — 평가 데이터 ground_truth 채움 (C3 실험 전제 조건)

**T2.** [backend/evaluation/test_queries.json](backend/evaluation/test_queries.json) — `cad_ablation` 5개 쿼리에 `ground_truth_template` + `ground_truth_source_section` 필드 추가

- 현재: `ground_truth = ""`
- 변경: `ground_truth_template = "이 논문 Experiment 섹션의 정확한 수치"`, `ground_truth_source_section = "experiment"`
- 사용자가 실제 페이퍼 업로드 후 이 가이드를 보고 수동 채움

**T3.** [backend/evaluation/ragas_eval.py](backend/evaluation/ragas_eval.py) — None-aware 평가

- `_evaluate_single()`/`_evaluate_heuristic()`: `sample.ground_truth`가 빈 문자열이면 `context_recall=None`
- `evaluate()` 평균 계산에 `_mean_skip_none()` 헬퍼 사용
- `per_sample` JSON 출력에 `null` 직렬화 허용
- 같은 변경을 [backend/evaluation/ablation_study.py](backend/evaluation/ablation_study.py) `format_results_table()`에도 적용

---

### PHASE 3 — Citation Tracker graceful fallback + L5 뷰어 패널 백엔드

**T4.** [backend/modules/citation_tracker.py](backend/modules/citation_tracker.py)

- `CitationInfo` dataclass에 `fetch_error: Optional[str] = None` 추가
- `fetch_from_arxiv()`: 결과 없을 때 `citation.fetch_error = "arxiv_not_found"`
- `get_citation_summary()` 출력에 `fetch_error` 포함

**T5.** [backend/api/schemas.py](backend/api/schemas.py) — `CitationItem`에 `fetch_error: Optional[str] = None` 추가

**T6.** [backend/api/routers/citations.py](backend/api/routers/citations.py) — 엔드포인트 분리

- `POST /api/citations/list` (신규): 메타데이터만 (PDF 다운로드 X)
- `POST /api/citations/download` (신규): 단일 인용 다운로드 + 인덱싱 (`{doc_id, citation_index}`)
- 기존 `POST /api/citations/track`은 호환성 유지

---

### PHASE 3.5 — 추천 질문 엔진 + 프론트 후속 질문 UI (NotebookLM 동등 + M-RAG 차별점)

> 모든 답변 하단에 클릭 가능한 추천 질문 말풍선 3개 표시. M-RAG 차별점: **라우트 인식** — 파이프라인 경로(A~F)에 따라 다른 맥락의 후속 질문 제안.

**T3.5a.** `backend/modules/followup_generator.py` 신규 생성 — 추천 질문 생성 모듈

- **하이브리드 접근**: 템플릿 기반 (GPU 불요) + LLM 기반 (generator 있을 때)
- 라우트별 템플릿:

```python
FOLLOWUP_TEMPLATES = {
    "A": [  # 단순 QA
        "이 내용을 더 자세히 설명해줘",
        "관련된 다른 연구는 뭐가 있어?",
        "이 개념의 핵심 정의가 뭐야?",
    ],
    "B": [  # 섹션 특화
        "{section}의 다른 부분도 보여줘",
        "이 섹션의 핵심을 요약해줘",
        "이 부분과 관련된 수식이나 표가 있어?",
    ],
    "C": [  # 비교
        "이 논문들의 공통점은 뭐야?",
        "어떤 논문의 방법이 더 효과적이야?",
        "실험 결과를 표로 비교해줘",
    ],
    "D": [  # 인용 추적
        "이 인용 논문의 핵심 기여가 뭐야?",
        "인용된 논문 중 가장 관련 깊은 건 뭐야?",
        "이 논문의 참고문헌을 더 보여줘",
    ],
    "E": [  # 요약
        "이 요약에서 빠진 중요한 내용이 있어?",
        "이 내용으로 퀴즈 5문제 만들어줘",
        "핵심 키워드 10개를 뽑아줘",
    ],
    "F": [  # 퀴즈
        "이 문제의 정답과 해설을 알려줘",
        "더 어려운 문제를 만들어줘",
        "이 주제의 핵심 개념을 정리해줘",
    ],
}
```

- `generate_followups(query, answer, route, section_filter=None, generator=None) -> list[str]`:

  - generator 없으면: 템플릿에서 3개 선택, `{section}` 플레이스홀더 치환
  - generator 있으면: LLM에게 "답변 맥락을 보고 후속 질문 3개 제안" 프롬프트 → 파싱
  - LLM 실패 시 템플릿 fallback (항상 3개 보장)

- 중복 제거: 원래 쿼리와 유사도 높은 후속 질문 필터링

**T3.5b.** [backend/api/routers/chat.py](backend/api/routers/chat.py) — SSE done 이벤트에 follow_ups 추가

- `event_generator()` 내 done 이벤트 수정:

```python

# 추천 질문 생성

from modules.followup_generator import generate_followups
follow_ups = generate_followups(
    query=req.query,
    answer=full_answer,
    route=decision.route.value,
    section_filter=decision.section_filter,
    generator=m.generator if m.has_generator else None,
)
yield f'event: done\ndata: {json.dumps({"full_answer": full_answer, "follow_ups": follow_ups}, ensure_ascii=False)}\n\n'
```

- 비스트리밍 `/query` 엔드포인트의 `QueryResponse`에도 `follow_ups: list[str]` 추가

**T3.5c.** [backend/api/schemas.py](backend/api/schemas.py) — `QueryResponse`에 `follow_ups: list[str] = []` 추가

**T3.5d.** [frontend/src/types/api.ts](frontend/src/types/api.ts) — SSE/Response 타입 확장

```typescript
export interface SSEDoneEvent {
  full_answer: string
  follow_ups?: string[]  // 추가
}

export interface QueryResponse {
  answer: string
  route: RouteInfo
  sources: SourceDocument[]
  steps: Record<string, unknown>[]
  pipeline: string
  follow_ups?: string[]  // 추가
}
```

**T3.5e.** [frontend/src/types/chat.ts](frontend/src/types/chat.ts) — `Message`에 `followUps?: string[]` 추가

**T3.5f.** [frontend/src/stores/chatStore.ts](frontend/src/stores/chatStore.ts) — `finalizeAssistantMessage`에 `followUps` 파라미터 추가

```typescript
finalizeAssistantMessage: (
  fullAnswer: string,
  route?: RouteInfo,
  sources?: SourceDocument[],
  steps?: Record<string, unknown>[],
  pipeline?: string,
  followUps?: string[],  // 추가
) => void
```

- 메시지 저장 시 `followUps` 필드도 저장

**T3.5g.** [frontend/src/components/chat/ChatPanel.tsx](frontend/src/components/chat/ChatPanel.tsx) — done 콜백에서 follow_ups 전달

```typescript
(doneData) => {
  finalizeAssistantMessage(
    doneData.full_answer,
    streamRoute,
    streamSources,
    undefined,
    undefined,
    doneData.follow_ups,  // 추가
  )
}
```

- `handleSend`를 `MessageBubble`에 prop으로 전달 (추천 질문 클릭 → 자동 전송)

**T3.5h.** [frontend/src/components/chat/MessageBubble.tsx](frontend/src/components/chat/MessageBubble.tsx) — 추천 질문 말풍선 UI

- `Props`에 `onFollowUpClick?: (query: string) => void` 추가
- 출처 영역 아래에 추천 질문 렌더링:

```tsx
{/* 추천 질문 말풍선 */}
{message.followUps && message.followUps.length > 0 && !message.isStreaming && (
  <div className="mt-2 pt-2 flex flex-wrap gap-1.5" style={{ borderTop: '1px solid var(--border-light)' }}>
    {message.followUps.map((q, i) => (
      <button
        key={i}
        onClick={() => onFollowUpClick?.(q)}
        className="px-3 py-1.5 rounded-full text-[11px] font-medium transition-all hover:scale-105"
        style={{
          background: 'var(--accent-light)',
          color: 'var(--accent)',
          border: '1px solid var(--accent)',
          borderOpacity: 0.2,
        }}
      >
        {q}
      </button>
    ))}
  </div>
)}
```

- 디자인: 라운드 pill 버튼, accent 색상, hover 시 살짝 확대

---

### PHASE 4 — Pipeline F (Quiz 생성, 사용자 명시 요구)

**T7.** `backend/pipelines/pipeline_f_quiz.py` 신규 생성

- `run(query, retriever, generator, ...)` 시그니처
- 흐름: 쿼리 의도 파싱(섹션 지정 여부) → 섹션별 검색 → 컨텍스트 결합 → "객관식 5문제 + 정답 + 해설 생성" 프롬프트 → `generator.generate()`
- `use_cad=True` 강제 (꾸며낸 문제 방지)
- 강의 모드(lecture doc_type)에서는 `exercise` 섹션 제외 (이미 답이 있는 문제 회피)
- **퀴즈 전용 후속 질문**: F 라우트 followup_generator 템플릿에 "왜 정답이 그건지 설명해줘", "더 어려운 문제를 만들어줘", "이 주제의 핵심 개념을 정리해줘" 포함 → 퀴즈 후 즉시 학습 연계
- 반환: `{ answer, sources, source_documents, pipeline: "F", steps }`

**T8.** [backend/modules/query_router.py](backend/modules/query_router.py) — `RouteType.F` + `quiz` 슬롯 처리

**T9.** [backend/config.py](backend/config.py) — `ROUTE_MAP`에 `"quiz": ["문제", "퀴즈", "연습", "시험", "quiz", "exercise", "출제"]` 추가

- "summary"의 "정리"와 충돌 가능 → quiz가 우선 매칭되도록 query_router에서 우선순위 명시

**T10.** [backend/api/routers/chat.py](backend/api/routers/chat.py) — `route.route == "F"` 분기 추가

**T11.** [backend/api/schemas.py](backend/api/schemas.py) / 라우트 라벨 매핑 위치 — `F: "퀴즈 생성"` 추가

---

### PHASE 5 — 프론트엔드 인용 뷰어 패널 (L5)

**T12.** `frontend/src/components/viewer/CitationPanel.tsx` 신규 생성

- 탭: PDF 뷰어 / 참고문헌
- API: `POST /api/citations/list` → `CitationItem[]`
- 각 항목: 제목, 저자, 연도, 상태 배지(`fetched` / `arxiv_not_found`), `[다운로드 & 인덱싱]` 버튼
- `arxiv_not_found` 항목 회색 + 툴팁: "arXiv 미등록 — PDF 직접 업로드 필요"

**T13.** [frontend/src/components/viewer/PDFViewer.tsx](frontend/src/components/viewer/PDFViewer.tsx) — 상단 탭 토글 + `<CitationPanel />` 전환

- 탭 전환 시 PDF 캔버스는 unmount 대신 `display: none` 처리하여 zoom/page 상태 보존

**T14.** `frontend/src/api/citations.ts` 신규 생성: `listCitations()`, `downloadCitation()`

---

### PHASE 6 — 배포·실험 진입점 통합

**T15.** `backend/scripts/run_c3_experiment.py` 신규 생성 (논문 실험 한 줄 실행)

- 인자: `--paper-pdf <path>` `--collection <name>` (기본 `c3_eval`)
- 흐름:

  1. 페이퍼 인덱싱 (parser → section_detector → chunker → embedder → vector_store)
  2. `load_test_queries(query_types=["cad_ablation","crosslingual_mixed","crosslingual_en"])`
  3. ground_truth 비어 있는 쿼리 경고 출력
  4. `compare_cad_on_off()` α=0.5 실행
  5. `AblationStudy.run_cad_korean_evaluation()` α 5단계 실행
  6. 결과 → `evaluation/results/c3_<timestamp>.json` + 마크다운 표 stdout

- GPU 미존재 시: 휴리스틱 모드 경고 + CAD 비교 스킵

**T16.** `backend/scripts/verify_deployment.py` 신규 생성 (배포 직전 sanity check)

- 임포트: `modules.cad_decoder`, `modules.scd_decoder`, `pipelines.pipeline_f_quiz`, `api.routers.citations`, `pymupdf4llm`
- ChromaDB 디렉토리 쓰기 권한, BGE-M3 캐시 존재
- 환경 변수 `LOAD_GPU_MODELS` 체크
- 출력: 모든 항목 `[OK]` 또는 명확한 실패 사유

**T17.** [docker-compose.yml](docker-compose.yml) 검토만

- `backend` 컨테이너 볼륨이 `evaluation/results/` 까지 커버하는지
- pymupdf4llm 의존성이 backend Dockerfile `pip install -r requirements.txt` 단계에서 정상 설치되는지

---

## 변경 파일 요약

| # | 파일 | 작업 | 위험도 |
|---|---|---|---|
| **T0a** | backend/requirements.txt | pymupdf4llm 추가 | 낮음 |
| **T0b** | backend/modules/pdf_parser.py | 구조 보존 + 수식/표 감지 | **높음** |
| **T0c** | backend/modules/chunker.py | code/table/math 분할 금지 | 중간 |
| **T0d** | backend/config.py | LECTURE_PATTERNS 추가 | 낮음 |
| **T0e** | backend/modules/section_detector.py | lecture 유형 분기 | 중간 |
| **T0f** | docs/COMPETITIVE_ANALYSIS.md | 강의/교재 섹션 추가 | 낮음 |
| **T0g** | docs/ACADEMIC_CLAIMS.md | 검증/적용 범위 분리 | 낮음 |
| **T0h** | docs/CRITIQUE_AND_IMPROVEMENTS.md | L1/L2/L8 멀티모달 제거 + 수식/표 반영 | 낮음 |
| **T0i** | CLAUDE.md, docs/ARCHITECTURE.md | "논문 특화" 표현 정정 | 낮음 |
| **T0j** | backend/evaluation/test_queries.json | lecture 쿼리 8개 추가 | 낮음 |
| **T0k** | backend/config.py | PATENT_PATTERNS + ROUTE_MAP 특허 키워드 | 낮음 |
| **T0l** | backend/modules/section_detector.py | patent doc_type + 섹션 순서 | 중간 |
| **T0m** | backend/modules/patent_tracker.py | **신규** (Google Patents 연동) | **중간** |
| **T0n** | backend/pipelines/pipeline_d_citation.py | paper/patent 분기 | 중간 |
| **T0o** | backend/api/dependencies.py | patent_tracker 싱글턴 | 낮음 |
| **T0p** | backend/config.py | ROUTE_MAP citation에 특허 키워드 (T0k와 합침) | 낮음 |
| **T0q** | backend/evaluation/test_queries.json | patent 쿼리 6개 추가 (T0j와 합침) | 낮음 |
| **T0r** | 4개 docs | 특허 도메인 문서 업데이트 (T0f~T0i에 흡수) | 낮음 |
| T1 | docs/CRITIQUE_AND_IMPROVEMENTS.md | lint 수정 (T0h와 합침) | 낮음 |
| T2 | backend/evaluation/test_queries.json | ground_truth_template 필드 | 낮음 |
| T3 | backend/evaluation/ragas_eval.py | None-aware 평균 | 중간 |
| T4 | backend/modules/citation_tracker.py | fetch_error 필드 | 낮음 |
| T5 | backend/api/schemas.py | fetch_error 필드 | 낮음 |
| T6 | backend/api/routers/citations.py | list/download 분리 | 중간 |
| **T3.5a** | backend/modules/followup_generator.py | **신규** (추천 질문 엔진) | 중간 |
| **T3.5b** | backend/api/routers/chat.py | SSE done에 follow_ups 추가 | 중간 |
| **T3.5c** | backend/api/schemas.py | QueryResponse follow_ups 추가 | 낮음 |
| **T3.5d** | frontend/src/types/api.ts | SSEDoneEvent follow_ups 타입 | 낮음 |
| **T3.5e** | frontend/src/types/chat.ts | Message followUps 필드 | 낮음 |
| **T3.5f** | frontend/src/stores/chatStore.ts | finalizeAssistantMessage followUps | 낮음 |
| **T3.5g** | frontend/src/components/chat/ChatPanel.tsx | follow_ups 전달 + handleSend prop | 낮음 |
| **T3.5h** | frontend/src/components/chat/MessageBubble.tsx | 추천 질문 말풍선 UI | 중간 |
| T7 | backend/pipelines/pipeline_f_quiz.py | **신규** | 중간 |
| T8 | backend/modules/query_router.py | F 라우팅 | 중간 |
| T9 | backend/config.py | quiz ROUTE_MAP | 낮음 |
| T10 | backend/api/routers/chat.py | F 분기 | 중간 |
| T11 | backend/api/schemas.py | F 라벨 | 낮음 |
| T12 | frontend/src/components/viewer/CitationPanel.tsx | **신규** | 중간 |
| T13 | frontend/src/components/viewer/PDFViewer.tsx | 탭 추가 | 낮음 |
| T14 | frontend/src/api/citations.ts | **신규** | 낮음 |
| T15 | backend/scripts/run_c3_experiment.py | **신규** | 낮음 |
| T16 | backend/scripts/verify_deployment.py | **신규** | 낮음 |

---

## 발생할 수 있는 잠재 이슈와 사전 대응

| 이슈 | 발생 가능성 | 사전 대응 |
|---|---|---|
| **pymupdf4llm 임포트 실패** (Windows 환경 / 버전 충돌) | 중 | T0b에서 try/except로 graceful fallback — 실패 시 raw 추출만 사용, 로그 경고 |
| **pymupdf4llm 출력과 raw bbox 매칭 실패** (페이지 번호 어긋남) | 중 | T0b에서 page_chunks 모드 사용, 페이지 단위로만 병합 (블록 단위 매칭 시도 안 함) |
| **코드/표/수식 블록 보존 시 청크 크기 초과** → 임베딩 모델 입력 한계 위반 | 중 | T0c에서 분할 금지하되, BGE-M3는 8192 토큰까지 지원하므로 일반 강의/논문 블록은 안전 |
| **수식 감지 false positive** — 일반 이탤릭 텍스트를 math로 오판 | 중 | T0b에서 폰트명 whitelist(CMSY/STIX/Symbol/Math/Asana) + 유니코드 밀도 25% 임계값 이중 조건 사용 |
| **수식 감지 false negative** — 수식이 일반 폰트로 렌더링된 경우 (워드 변환 PDF 등) | 중 | 폰트 조건 실패 시에도 유니코드 밀도 단독 조건으로 백업 감지 |
| **복잡한 다중 행렬 표가 markdown으로 표현 불가** → pymupdf4llm이 일부 셀 깨뜨림 | 중 | T0b에서 pymupdf `find_tables()` 결과와 비교하여 셀 수가 덜 잡힌 경우 raw table을 우선 사용 |
| **lecture 유형 오판** (논문에 example/exercise 키워드 포함) | 중 | T0e에서 paper_count > 0이면 lecture로 판별 보류 (paper 우선) |
| **C3 실험 시 lecture 쿼리가 섞여 들어와 이상치 발생** | 중 | T15에서 `query_types=["cad_ablation","crosslingual_*"]`로 명시 필터 |
| **pymupdf4llm AGPL 라이선스** | 낮 | 학술 졸업작품 + 비공개 배포 → 문제 없음, 상업화 시 재검토 |
| **compare_cad_on_off() 시그니처 vs evaluator 인자 불일치** | 중 | T15에서 진입점 스크립트가 직접 인자 주입 |
| **CAD가 GPU 미존재 시 NoneType** | 높 | T15에서 GPU 미존재 시 CAD 비교 스킵 + 경고 |
| **Pipeline F 추가 후 기존 23개 API 테스트 회귀** | 중 | T7~T10 후 `tests/test_api.py` 실행 — 깨지면 즉시 수정 |
| **CitationPanel 추가 시 PDFViewer zoom/page 상태 손실** | 중 | T13에서 `display: none` 처리 (unmount 금지) |
| **ROUTE_MAP "quiz" 키워드와 "summary" 키워드 충돌** | 중 | T8에서 quiz 매칭을 우선 처리하는 명시적 우선순위 |
| **docker-compose 빌드에서 pymupdf4llm 누락** | 낮 | T17 검증 단계에서 `docker compose build --no-cache` 실행 |
| **arXiv API rate limit (429)** | 낮 | T6 `/list`는 delay=0, `/download`만 1초 delay 유지 |
| **Google Patents HTML 파싱 구조 변경** (비공식 API) | 중 | T0m에서 BeautifulSoup 선택자를 try/except + 구조 버전 주석, 실패 시 `fetch_error="patents_parser_outdated"` |
| **KIPRIS API 키 없음** | 낮 | T0m에서 KIPRIS는 선택적(키 설정 시에만 활성화), 기본 경로는 Google Patents 공개 URL |
| **특허 번호 형식 다양성** (KR/US/JP/EP/WO) | 중 | T0m `parse_cited_patents()`에서 국가 코드 5종 alternation + 숫자/하이픈 정규식으로 폭넓게 커버 |
| **특허 doc_type 오판** (논문이 prior art 섹션 인용 시 patent로 분류) | 중 | T0l에서 `청구항\s*\d+` 또는 `【청구항` 등 특허 고유 패턴 필수 조건 추가 |
| **LLM 후속 질문 생성 실패** (포맷 파싱 실패, 빈 결과) | 중 | T3.5a에서 LLM 실패 시 템플릿 fallback — 항상 3개 보장 |
| **후속 질문이 원래 쿼리와 동일** (LLM이 같은 질문 재생성) | 중 | T3.5a에서 원래 쿼리와 문자열 유사도 체크 후 필터링 |
| **SSE done 이벤트 크기 증가** (follow_ups 추가) | 낮 | 후속 질문 3개 × ~50자 = 추가 ~150자, SSE 한계 내 |

---

## 검증 (적용 후 한 번에 실행)

### 1. 코드 import sanity check (GPU 불요)

```bash
cd backend && python scripts/verify_deployment.py
```

기대: 모든 항목 `[OK]`. pymupdf4llm 포함.

### 2. 단위/통합 테스트

```bash
cd backend && uvicorn api.main:app --host 0.0.0.0 --port 8000 &
python -X utf8 tests/test_api.py
```

기대: 23개 + Pipeline F 신규 분량 모두 통과.

### 3. 강의/수식/표 구조 보존 검증 (T0b/T0c 핵심 검증)

```bash
cd backend && python -c "
from modules.pdf_parser import PDFParser
from modules.section_detector import SectionDetector
p = PDFParser().parse('data/lecture_E_compiler.pdf')
sd = SectionDetector().detect(p)
print('doc_type:', sd.metadata.get('doc_type'))
for bt in ('code','table','math','heading'):
    blocks = [b for b in sd.blocks if b.block_type == bt]
    print(f'{bt} blocks: {len(blocks)}')
    for b in blocks[:2]: print(' ', repr(b.content[:150]))
"
```

기대:

- `doc_type: lecture`
- code 블록 ≥ 1개 (BNF/EBNF 문법 온전)
- table 블록 ≥ 1개 (markdown 표 형태, `|`로 셀 구분)
- math 블록 ≥ 1개 (수학 논문/강의 PDF 사용 시) — 유니코드 기호 그대로 포함

### 4. 특허 PDF doc_type 및 인용 특허 파싱 검증 (T0l/T0m)

```bash
cd backend && python -c "
from modules.pdf_parser import PDFParser
from modules.section_detector import SectionDetector
from modules.patent_tracker import PatentTracker
p = PDFParser().parse('data/patent_F_kr_ai.pdf')
sd = SectionDetector().detect(p)
print('doc_type:', sd.metadata.get('doc_type'))
claims = sd.get_section_text(sd, 'claims') if sd.metadata.get('doc_type') == 'patent' else ''
print('claims length:', len(claims))
cited_text = sd.get_section_text(sd, 'cited_patents')
patents = PatentTracker().parse_cited_patents(cited_text)
print(f'cited patents: {len(patents)}')
"
```

기대: `doc_type: patent`, claims length > 0, cited patents ≥ 1개.

### 5. 문서 lint

[docs/CRITIQUE_AND_IMPROVEMENTS.md](docs/CRITIQUE_AND_IMPROVEMENTS.md) markdown lint 0건 확인.

### 6. 도커 빌드

```bash
docker compose build --no-cache
docker compose up
```

기대: backend, frontend, db 세 컨테이너 정상 기동. `:8000/health` 200 OK. pymupdf4llm 설치 로그 확인.

### 7. 프론트 수동 검증

- `cd frontend && npm run dev`
- 강의 PDF 1편 업로드 → 채팅 "BNF 문법 정의가 어떻게 돼?" → 답변에 코드 블록 ` ``` ` 형태 보존
- 수학 논문 1편 업로드 → 채팅 "Theorem 3.2의 수식을 그대로 보여줘" → 유니코드 수학 기호 깨짐 없이 출력
- 표 포함 논문 1편 업로드 → 채팅 "Table 1의 모든 행을 보여줘" → markdown 표 형태 유지
- 특허 PDF 1편 업로드 → 채팅 "이 특허와 유사한 특허를 찾아줘" → Pipeline D(patent 분기) 실행 + 뷰어 패널에 Google Patents 결과 표시
- 채팅 "이 논문에서 인용한 논문 보여줘" → Pipeline D(arxiv 분기) 실행
- 뷰어 패널 → 참고문헌 탭 → arxiv_not_found / patents_parser_outdated 회색 처리 확인
- 채팅 "이 내용으로 5문제 만들어줘" → Pipeline F + 라우트 배지 "F: 퀴즈 생성"
- **모든 답변 하단에 추천 질문 말풍선 3개 표시 확인** (라운드 pill 버튼)
- 추천 질문 클릭 → 해당 질문이 자동으로 입력·전송 → 새 답변 + 새 추천 질문 3개 표시
- Pipeline F(퀴즈) 답변 후 추천 질문이 퀴즈 맥락에 맞는지 확인 ("정답과 해설을 알려줘", "더 어려운 문제를 만들어줘" 등)
- Pipeline D(인용) 답변 후 추천 질문이 인용 맥락에 맞는지 확인 ("인용 논문의 핵심 기여가 뭐야?" 등)

### 8. C3 논문 실험 (GPU 환경)

```bash
LOAD_GPU_MODELS=true \
  python backend/scripts/run_c3_experiment.py \
    --paper-pdf backend/data/paper_A_nlp.pdf \
    --collection c3_eval
```

산출물:

- `backend/evaluation/results/c3_<timestamp>.json` — α별 faithfulness delta
- stdout 마크다운 표 (논문 Table 2 직접 사용)
- best_alpha + max_faithfulness_delta 요약

GPU 없으면 휴리스틱 모드, "참고용 (논문 인용 불가)" 라벨.

---

## 핵심 원칙

1. **PHASE 0/0.5 우선** — pymupdf4llm 도입, 수식/표 감지, 특허 도메인 확장이 가장 먼저 끝나야 시연이 가능. C3 논문 실험과는 독립 경로이므로 병행 가능하나 검증 #3/#4는 PHASE 0 완료 후만 수행.
2. **텍스트 전용 정책** — 멀티모달(Vision-LM, LaTeX-OCR, Mathpix 등 이미지 기반) 기능은 범위 외. 수식/표 보존은 폰트·유니코드·markdown 수준에서만 수행. 관련 "향후 계획" 문구도 기존 문서에서 삭제.
3. **검증/적용 분리** — 논문은 C1~C4 검증용, 강의/교재/특허는 적용 시연용. 두 도메인의 메시지를 섞지 않는다.
4. **graceful fallback 우선** — pymupdf4llm 임포트 실패, GPU 미존재, arXiv/Google Patents 응답 실패 모두 우아하게 처리하여 기존 동작 유지.
5. **기존 완료 작업 재작업 금지** — "이미 완료된 항목" 리스트 외에는 손대지 않음. PHASE 0의 문서 수정은 기존 파일에 **추가**만 하고 기존 내용은 건드리지 않음 (단, L1/L2/L8 멀티모달 문구 삭제는 명시적 예외).
6. **회귀 우선 차단** — Pipeline F + lecture/patent 분기 추가로 기존 5 파이프라인이 깨지면 안 됨. 모든 phase 후 `tests/test_api.py` 회귀 테스트 필수.

---

## 전체 작업 체크리스트 (잔작업·이슈 완전 커버)

### 신규 요구사항 (이번 세션)

- [x] 레이아웃 인식 추출 (코드/BNF/다중 컬럼) → T0a~T0e
- [x] 수식 보존 (멀티모달 無, 폰트·유니코드 기반) → T0b/T0c
- [x] 표 보존 (markdown + pymupdf fallback) → T0b/T0c
- [x] 특허 문서 도메인 확장 (청구항/배경기술/상세한 설명 섹션) → T0k/T0l
- [x] 유사 특허·인용 특허 추적 (Google Patents 연동) → T0m/T0n
- [x] 포지셔닝 전환 ("논문 특화" → "학술+강의+특허") → T0f~T0i/T0r
- [x] 멀티모달 관련 모든 "향후 계획" 문구 삭제 → T0h
- [x] 추천 질문 엔진 (라우트 인식 템플릿 + LLM 하이브리드) → T3.5a
- [x] SSE done 이벤트 follow_ups 통합 → T3.5b/T3.5c
- [x] 프론트 추천 질문 말풍선 UI → T3.5d~T3.5h
- [x] 퀴즈 후속 질문 연계 (Pipeline F 전용 템플릿) → T7 + T3.5a

### 이전 세션에서 이월된 잔작업

- [x] CRITIQUE_AND_IMPROVEMENTS.md markdown lint → T1 (T0h와 합침)
- [x] cad_ablation 쿼리 ground_truth 전략 → T2
- [x] ragas_eval None-aware 평균 → T3
- [x] citation_tracker graceful fallback → T4
- [x] CitationItem 스키마 확장 → T5
- [x] /api/citations list/download 분리 → T6
- [x] Pipeline F (퀴즈 생성) → T7~T11
- [x] CitationPanel 프론트 뷰어 → T12~T14
- [x] C3 실험 한 줄 진입점 → T15
- [x] 배포 sanity check → T16
- [x] docker-compose 검증 → T17

### 잠재 이슈 전부 사전 대응됨 (총 20행)

- 파서/청킹 관련 이슈 6개 (pymupdf4llm 실패, bbox 매칭, 청크 초과, 수식 FP/FN, 복잡 표)
- 도메인 분류 이슈 2개 (lecture 오판, patent 오판)
- 평가/실행 이슈 3개 (시그니처 불일치, GPU 미존재, 테스트 회귀)
- 프론트 이슈 2개 (상태 손실, 키워드 충돌)
- 배포 이슈 2개 (docker, rate limit)
- 특허 이슈 2개 (HTML 파싱 변경, KIPRIS 키 없음)
- 추천 질문 이슈 3개 (LLM 생성 실패, 쿼리 중복, SSE 크기)
