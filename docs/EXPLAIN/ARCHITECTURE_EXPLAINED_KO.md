# M-RAG 전체 구조 깊이 이해하기

---

아래의 짧은 수치 예시와 문장 조각은 구조 설명용이다. 실제 실험 수치와 최종 표는 `backend/evaluation/results/` 산출물을 기준으로 정리한다.

## 한 줄 설명

M-RAG는 논문 PDF를 업로드하면, 질문 유형을 분석해 알맞은 검색 경로를 선택하고, CAD+SCD로 제어된 한국어 답변을 만드는 모듈러 RAG 시스템이다.

---

## 왜 이 시스템을 만들었는가

논문 리뷰 챗봇을 만들 때 두 가지 문제가 핵심이었다.

### 문제 1: Hallucination (환각)

언어 모델은 논문을 참고해서 답해야 하는데, 훈련 데이터에서 배운 기억이 더 강하게 나올 수 있다.

```
실제 논문: "이 모델은 KorQuAD에서 F1 87.3을 달성했다."

모델이 훈련 중 비슷한 실험에서 90점대를 많이 봤다면:
→ 잘못된 답변: "이 모델은 KorQuAD에서 F1 92.1을 달성했습니다."
```

논문 리뷰에서 수치가 틀리면 사용자가 잘못된 이해를 갖게 된다.

### 문제 2: Language Drift (언어 이탈)

한국어로 질문해도 영어 논문 내용이 섞여 답변에 영어가 나온다.

```
질문: "이 논문의 핵심 기여가 뭐야?"
문제 있는 답변: "이 논문은 We propose a context-aware decoding method를 통해..."
```

### 해결 전략

- **Hallucination**: CAD(Context-Aware Decoding)로 사전 기억 개입 억제
- **Language Drift**: SCD(Selective Context-aware Decoding)로 비목표 언어 토큰 페널티

그리고 이 두 기술이 각각, 그리고 함께 얼마나 효과가 있는지 실험으로 정량화한다. 이것이 논문의 핵심 기여다.

---

## 연구 기여 C1, C2, C3와 코드 연결

논문은 세 가지 기여를 주장한다. 각각이 코드 어디에서 구현되는지 연결해서 보면 논문 전체가 이해된다.

### C1: 모듈별 기여도 정량 분해

**주장**: 단순히 "전체 시스템이 좋다"가 아니라, 어떤 모듈이 어떤 문제를 얼마나 줄이는지 정량적으로 분해할 수 있다.

**구현 위치**:
```
backend/evaluation/run_track1.py       ← Ablation 실험 실행
backend/evaluation/ablation_study.py   ← 6개 설정 정의
backend/evaluation/ragas_eval.py       ← RAGAS 점수 계산
backend/evaluation/results/table1_track1.json  ← 결과
```

**실험 설계**:
```
설정 1: Naive RAG만            → 기준선
설정 2: + Query Expansion      → 검색 개선 효과 분리
설정 3: + Hybrid Retrieval     → 하이브리드 검색 효과 분리
설정 4: + CAD                  → Hallucination 억제 효과 분리
설정 5: + SCD                  → Language Drift 억제 효과 분리
설정 6: Full System            → 전체 효과
```

설정 2에서 올라간 만큼이 Query Expansion의 기여, 설정 4에서 올라간 만큼이 CAD의 기여.

---

### C2: CAD+SCD 조합으로 두 문제 동시 억제

**주장**: CAD는 Hallucination을, SCD는 Language Drift를 억제하며, 두 방법은 서로 다른 원인을 해결하므로 함께 쓰면 두 효과가 동시에 난다.

**구현 위치**:
```
backend/modules/cad_decoder.py          ← CAD 구현
backend/modules/scd_decoder.py          ← SCD 구현
backend/modules/generator.py            ← 두 디코더 적용 조율
backend/evaluation/results/table2_*.json  ← alpha/beta sweep 결과
```

**alpha/beta sweep 실험**:
```
CAD alpha: [0.0, 0.1, 0.3, 0.5, 0.7, 1.0] × 2편 논문
SCD beta:  [0.1, 0.3, 0.5] × 1편 논문 (한국어)
```

각 값에서 Faithfulness가 어떻게 바뀌는지 측정해 최적값을 찾는다.

---

### C3: 오픈소스 모듈러 RAG 구현 공개

**주장**: 논문 도메인 특화 + 범용 다국어 동작이 가능한 시스템을 오픈소스로 공개한다.

**구현 위치**:
```
backend/pipelines/          ← A~F 6개 파이프라인
backend/modules/            ← 18개 모듈
backend/api/                ← FastAPI 서버
frontend/src/               ← React 프론트엔드
```

---

## 전체 데이터 흐름 (구체적으로)

### 업로드 흐름

```
사용자가 paper_bert.pdf 업로드
    │
    ▼
papers.py → 파일 검증 (형식, 크기)
    │
    ▼
pdf_parser.py → 텍스트 추출
  출력 예시:
  "Abstract: In this paper, we present BERT...
   Introduction: Language model pre-training...
   Method: We use a multi-layer bidirectional..."
    │
    ▼
section_detector.py → 섹션 태깅
  출력 예시:
  {"text": "In this paper...", "section": "abstract"}
  {"text": "Language model...", "section": "introduction"}
  {"text": "We use a multi-layer...", "section": "method"}
    │
    ▼
chunker.py → 512토큰 단위 분할 (64토큰 겹침)
  출력 예시 (청크 47번):
  {"text": "We use a multi-layer bidirectional Transformer...",
   "section": "method", "chunk_id": 47, "paper_id": "1810.04805_bert"}
    │
    ▼
embedder.py → BGE-M3로 벡터화
  출력 예시 (1024차원):
  [0.021, -0.143, 0.892, 0.034, ...(1024개)]
    │
    ▼
vector_store.py → ChromaDB에 저장
  저장 내용: 벡터 + 원본 텍스트 + 메타데이터(section, paper_id)
    │
    ▼
SQLAlchemy → Paper 메타데이터 DB 저장 (제목, 파일명, 청크 수)
```

---

### 질문 처리 흐름

```
질문: "BERT의 핵심 아이디어가 뭐야?"
    │
    ▼
chat.py → JWT 토큰으로 사용자 확인
    │
    ▼
query_router.py → 경로 선택
  분석: "핵심 아이디어" → 일반 QA → 경로 A 선택
    │
    ▼
query_expander.py → 쿼리 확장
  ① HyDE 가상 답변 생성:
    "BERT의 핵심 아이디어는 양방향 Transformer를 사전학습하는 것이다.
     Masked Language Model로 문맥 양쪽을 모두 보도록 훈련한다."
  ② 다중 쿼리:
    - "BERT 사전학습 방법"
    - "양방향 언어 모델 구조"
    - "Masked Language Model이란"
    │
    ▼
hybrid_retriever.py → 검색 수행
  ① Dense 검색 (BGE-M3):
    - 가상 답변 벡터와 청크 벡터 비교
    - 상위 20개 반환
  ② BM25 검색:
    - "BERT", "핵심", "아이디어" 키워드 매칭
    - 상위 20개 반환
  ③ RRF로 합산:
    - 최종 상위 20개 청크
    │
    ▼
reranker.py → Cross-encoder 재정렬
  각 청크를 질문과 함께 평가:
  입력: "[질문] BERT 핵심 아이디어? [청크] BERT는 양방향 Transformer..."
  출력: 관련도 점수 0.94
  → 상위 5~10개로 줄임
    │
    ▼
context_compressor.py → 핵심 문장만 남겨 압축
  입력: 청크 5개 (총 2500토큰)
  출력: 핵심 문장만 (총 800토큰)
    │
    ▼
generator.py + cad_decoder.py + scd_decoder.py → 답변 생성
  ① 컨텍스트 + 질문으로 MIDM 모델 호출
  ② CAD: logits_문서있음 - 0.3 × logits_문서없음
  ③ SCD: 영어 토큰 확률 패널티
  출력: "BERT의 핵심 아이디어는 양방향 Transformer 구조로
        문장의 왼쪽과 오른쪽 문맥을 동시에 학습하는 것입니다..."
    │
    ▼
followup_generator.py → 후속 질문 생성
  출력: ["GPT와 BERT의 차이가 뭐야?", "BERT의 사전학습 방법이 뭐야?"]
    │
    ▼
최종 반환:
  - 답변 텍스트
  - 출처 청크 (어느 논문 어느 섹션에서 왔는지)
  - 실행된 경로 (A)
  - 후속 질문 2~3개
```

---

## 18개 모듈 상세

### 연구 핵심 모듈 13개

| 모듈 | 입력 | 출력 | 없으면 어떻게 되는가 |
|---|---|---|---|
| embedder | 텍스트 | 1024차원 벡터 | 의미 검색 불가, BM25만 사용 |
| chunker | 전체 문서 텍스트 | 청크 리스트 (텍스트+메타) | 논문 전체를 하나로 저장, 검색 불가 |
| reranker | 질문+청크 쌍 | 관련도 점수 목록 | 재정렬 없이 초기 검색 순서 그대로 |
| hybrid_retriever | 쿼리, 컬렉션명 | 청크 목록 (점수 포함) | Dense 또는 BM25 단독만 가능 |
| query_router | 질문 텍스트 | 경로 코드 (A~F) | 모든 질문이 A 경로로 처리 |
| section_detector | 문서 텍스트 | 섹션 태그 목록 | B 경로 섹션 필터링 불가 |
| generator | 컨텍스트+질문 | 답변 텍스트 | 답변 생성 자체 불가 |
| cad_decoder | logits (두 벌) | 조정된 logits | Hallucination 억제 없음 |
| scd_decoder | logits, 목표언어 | 조정된 logits | Language Drift 억제 없음 |
| context_compressor | 청크 목록 | 압축된 텍스트 | 컨텍스트가 너무 길어 품질 저하 |
| query_expander | 질문 | HyDE문서+다중쿼리 | 표현 다른 관련 청크 검색 실패 가능 |
| citation_tracker | 논문 텍스트 | 인용 목록+arXiv 정보 | D 경로 인용 추적 불가 |
| followup_generator | 질문+답변 | 후속 질문 목록 | 다음 질문 제안 없음 |

### 확장/운영 모듈 5개

| 모듈 | 역할 | 연결되는 핵심 모듈 |
|---|---|---|
| pdf_parser | PDF 텍스트 추출 | chunker, section_detector |
| docx_parser | DOCX/TXT 텍스트 추출 | chunker, section_detector |
| patent_tracker | 특허 문헌 추적 | citation_tracker (D 경로) |
| pptx_exporter | 답변 → PPTX 파일 | generator 출력 |
| vector_store | ChromaDB 저장/검색 관리 | embedder, hybrid_retriever |

---

## A~F 경로의 핵심 차이점

### 경로 A (일반 QA) — 모든 모듈 활성

```
질문 → HyDE 확장 → Hybrid 검색 → Rerank → 압축 → CAD+SCD 생성
```

### 경로 B (섹션 특화) — 섹션 필터 추가

```
"이 논문의 연구 방법이 뭐야?" 
→ section_detector가 "method" 태그 청크 우선 검색
→ 나머지는 A와 동일
```

왜 필요한가: 섹션 태그 없이 검색하면 Introduction의 "우리는 다음 방법을 제안한다" 같은 문장이 Method 섹션보다 높게 올 수 있다.

### 경로 C (비교) — 멀티 컬렉션 검색

```
"BGE-M3와 ColBERT 비교해줘"
→ 두 논문 컬렉션에서 각각 검색
→ 두 결과를 합쳐 비교 포맷으로 생성
```

### 경로 D (인용) — arXiv 실시간 연동

```
"이 논문이 인용한 핵심 연구는?"
→ citation_tracker가 논문 참고문헌 목록 파싱
→ arXiv API로 각 논문 정보 조회
→ 인용 관계와 함께 답변
```

### 경로 E (요약) — RAPTOR 계층 활용

```
"이 논문 전체 요약해줘"
→ 청크 수준 요약 → 섹션 수준 요약 → 전체 요약 순서로 계층 생성
→ 전체 수준 요약에서 검색
```

### 경로 F (퀴즈) — 구조화된 출력

```
"퀴즈 만들어줘"
→ 논문 내용 검색
→ 문제 + 4개 선택지 + 정답 + 해설 형식으로 생성
→ 논문에 있는 내용만 문제로 출제
```

---

## 실험 구조 전체

### Track 1 (Table 1, 2)

```
7편 논문 × 60개 질문 × 6개 설정 = 2,520 API 호출
```

7편: paper_nlp_bge, paper_nlp_rag, paper_nlp_cad, paper_nlp_raptor, 1810.04805_bert, 2101.08577, paper_korean

6개 설정:
- Naive RAG
- + Query Expansion  
- + Hybrid Retrieval
- + CAD
- + CAD + SCD
- Full System (CAD + SCD + 압축 + 섹션)

각 설정별 Faithfulness, Answer Relevancy, Context Precision 측정 → Table 1

### Track 2 (Table 3)

```
4편 NLP 논문 × 28개 전문 질문 × 6개 설정 = 672 API 호출
```

논문 도메인 특화 효과 측정. CAD ablation 쿼리(의도적으로 논문에 없는 정보를 물어봄)로 Hallucination 억제 효과를 정밀 측정한다.

---

## 인프라 선택의 이유

| 선택 | 이유 |
|---|---|
| MIDM Base (생성 모델) | 논문 기준 모델. 한국어 특화. Mini는 로컬 스모크 테스트 전용 |
| BGE-M3 (임베딩) | 한영 동일 벡터 공간 → 한국어 질문으로 영어 논문 검색 가능 |
| ChromaDB (벡터 저장소) | 오픈소스, 설치 간단, 소규모 실험에 적합 |
| SQLite (실험 DB) | 설치 없이 파일 하나로 운영. PostgreSQL은 운영 환경에서만 |
| GPT-4o (GT 생성) | 평가 모델(MIDM)과 독립된 외부 모델로 정답 생성 → 신뢰도 높음 |
| FastAPI (API 서버) | 비동기 처리, 빠른 개발, OpenAPI 문서 자동 생성 |
