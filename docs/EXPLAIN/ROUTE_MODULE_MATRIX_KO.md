# A~F 경로별 모듈 동작 가이드

## 문서 목적

이 문서는 모듈러 RAG에서 질문 유형별로 어떤 모듈이 움직이는지 설명한다

코드 근거

- `backend/modules/query_router.py`
- `backend/api/routers/chat.py`
- `backend/pipelines/pipeline_a_simple_qa.py`
- `backend/pipelines/pipeline_b_section.py`
- `backend/pipelines/pipeline_c_compare.py`
- `backend/pipelines/pipeline_d_citation.py`
- `backend/pipelines/pipeline_e_summary.py`
- `backend/pipelines/pipeline_f_quiz.py`

---

## 경로 한눈에 보기

| 경로 | 서비스 의미 | 연구/운영 분류 | 대표 질문 |
|---|---|---|---|
| A | 단순 질의응답 | 연구 | 이 논문의 핵심 아이디어는 뭐야 |
| B | 섹션 특화 질의응답 | 연구 | 실험 결과만 설명해줘 |
| C | 여러 문서 비교 | 연구 | 두 논문의 방법론 차이를 비교해줘 |
| D | 인용/특허 추적 | 연구 + 운영 | 이 논문이 인용한 연구 흐름을 알려줘 |
| E | 전체 요약 | 연구 | 논문 전체를 구조적으로 요약해줘 |
| F | 퀴즈/플래시카드 | 운영/학습 보조 | 이 논문으로 객관식 문제 만들어줘 |

연구 문서는 A~E와 CAD/SCD 실험을 중심으로 설명한다

운영 문서는 A~F 전체와 후속 질문, PPT Export, Search/Judge API를 함께 설명한다

---

## 경로별 실행 흐름

### A 단순 QA

1. `query_router.py`가 일반 질문으로 분류
2. `query_expander.py`가 질문을 보강
3. `hybrid_retriever.py`가 dense 검색과 BM25 검색 수행
4. `reranker.py`가 근거 후보를 재정렬
5. `context_compressor.py`가 컨텍스트 길이 조정
6. `generator.py`가 답변 생성
7. `cad_decoder.py`, `scd_decoder.py`가 생성 제어
8. `followup_generator.py`가 다음 질문 후보 생성

### B 섹션 특화

1. `query_router.py`가 섹션 질문으로 분류
2. `section_detector.py` 결과를 이용해 섹션 필터 적용
3. `hybrid_retriever.py`가 해당 섹션 중심으로 검색
4. `reranker.py`가 섹션 근거를 재정렬
5. `generator.py`가 섹션 중심 답변 생성
6. CAD/SCD와 후속 질문 생성 적용

### C 여러 문서 비교

1. `query_router.py`가 비교 질문으로 분류
2. 문서별로 검색 범위를 나눔
3. 각 문서의 근거를 모아 비교 컨텍스트 구성
4. `generator.py`가 공통점과 차이점 중심으로 답변 생성
5. CAD/SCD와 후속 질문 생성 적용

### D 인용/특허 추적

1. `query_router.py`가 인용 또는 특허 질문으로 분류
2. `citation_tracker.py`가 참고문헌과 arXiv 기반 인용 정보를 보조
3. `patent_tracker.py`가 특허 문서 질의에서 prior art 맥락을 보조
4. 검색 결과와 추적 결과를 함께 사용해 답변 생성
5. CAD/SCD와 후속 질문 생성 적용

### E 전체 요약

1. `query_router.py`가 요약 질문으로 분류
2. 청킹 결과와 요약용 컨텍스트 구성
3. `context_compressor.py`가 긴 문서를 요약 가능한 근거로 압축
4. `generator.py`가 구조적 요약 생성
5. CAD/SCD와 후속 질문 생성 적용

### F 퀴즈/플래시카드

1. `query_router.py`가 퀴즈 또는 플래시카드 질문으로 분류
2. `hybrid_retriever.py`가 문제 출제 근거를 검색
3. `reranker.py`가 출제에 적합한 근거를 재정렬
4. `context_compressor.py`가 근거를 짧게 정리
5. `pipeline_f_quiz.py`가 퀴즈 또는 플래시카드 프롬프트 구성
6. `generator.py`가 문제와 해설 생성
7. CAD/SCD가 근거 기반성과 한국어 응답 안정성을 보조

---

## 경로별 모듈 매트릭스

| 모듈 | A QA | B 섹션 | C 비교 | D 인용/특허 | E 요약 | F 퀴즈 |
|---|---:|---:|---:|---:|---:|---:|
| `query_router.py` | O | O | O | O | O | O |
| `query_expander.py` | O | 선택 | - | - | - | - |
| `section_detector.py` | 색인 | O | 색인 | 색인 | 색인 | 색인 |
| `hybrid_retriever.py` | O | O | O | O | O | O |
| `reranker.py` | O | O | 선택 | 선택 | 선택 | O |
| `context_compressor.py` | O | O | 선택 | 선택 | O | O |
| `citation_tracker.py` | - | - | - | O | - | - |
| `patent_tracker.py` | - | - | - | 특허 질문 | - | - |
| `generator.py` | O | O | O | O | O | O |
| `cad_decoder.py` | O | O | O | O | O | O |
| `scd_decoder.py` | O | O | O | O | O | O |
| `followup_generator.py` | O | O | O | O | O | O |
| `pipeline_f_quiz.py` | - | - | - | - | - | O |

---

## 읽는 기준

- 연구 결과 표를 해석할 때는 A~E와 CAD/SCD를 중심으로 본다
- 서비스 시연을 준비할 때는 A~F 전체와 후속 질문, PPT Export를 함께 본다
- F 경로는 운영/학습 보조 기능이며, 논문 표의 핵심 ablation 축은 검색 모듈과 CAD/SCD다

---

참고문헌 번호(`[N]`)는 `docs/PAPER/THESIS.md`의 참고문헌 목록 기준이다 (총 39편)
