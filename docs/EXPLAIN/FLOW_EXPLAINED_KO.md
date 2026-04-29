# 요청부터 답변까지 흐름 — 깊이 있는 설명

이 문서는 PDF 업로드부터 답변이 나오기까지 각 단계에서 실제로 무슨 일이 일어나는지, 더 단순한 방법과 비교하면 왜 이렇게 설계했는지를 설명한다.

이 문서의 수치와 문장 조각은 흐름을 설명하기 위한 예시다. 실제 실험 결과와 테이블 값은 `backend/evaluation/results/` 산출물을 기준으로 확인한다.

---

# 1부. 문서 업로드 흐름

---

## 단계 1. 파일 검증

### 무슨 일이 일어나는가

서버가 파일을 받으면 형식(PDF/DOCX/TXT)과 크기를 확인한다. 허용되지 않는 형식이나 손상된 파일은 이 단계에서 거부된다.

### 더 단순한 방법과 비교

단순히 "어떤 파일이든 받는다"고 설계하면, 모델이 처리할 수 없는 파일(바이너리, 이미지만 있는 스캔 PDF)이 들어왔을 때 파이프라인 전체가 실패한다. 입구에서 걸러내는 것이 안전하다.

**관련 코드**: `backend/api/routers/papers.py`

---

## 단계 2. 텍스트 추출 (파싱)

### 무슨 일이 일어나는가

형식에 따라 다른 파서를 사용해 텍스트만 추출한다.

```
[입력] paper_bert.pdf (100페이지 바이너리)
          │
     pdf_parser.py
          │
[출력] 텍스트 + 구조 정보:
  "Abstract: In this paper, we introduce a new language representation 
   model called BERT, which stands for Bidirectional Encoder 
   Representations from Transformers...
   
   1. Introduction
   Language model pre-training has been shown to be effective...
   
   3. Pre-training BERT
   We pre-train BERT using two unsupervised tasks..."
```

### 왜 형식마다 다른 파서가 필요한가

PDF는 단순 텍스트 파일이 아니다. 내부적으로 페이지 레이아웃, 폰트, 객체로 구성된 바이너리다. 테이블, 수식, 다단 레이아웃이 있으면 텍스트 추출 순서가 뒤섞일 수 있다. PyMuPDF(fitz) 라이브러리로 구조를 보존하며 텍스트를 추출한다.

**관련 코드**: `backend/modules/pdf_parser.py`, `backend/modules/docx_parser.py`

---

## 단계 3. 섹션 감지

### 무슨 일이 일어나는가

논문의 각 부분이 어떤 섹션인지 태그를 붙인다.

```
[입력] 추출된 텍스트 블록들

[출력] 섹션 태그가 붙은 텍스트:
  {"text": "In this paper, we introduce...", "section": "abstract"}
  {"text": "Language model pre-training...", "section": "introduction"}
  {"text": "We pre-train BERT using...", "section": "method"}
  {"text": "We evaluate our approach on 11 NLP tasks...", "section": "result"}
  {"text": "While BERT achieves strong performance...", "section": "limitation"}
  {"text": "Devlin et al. (2018) introduced...", "section": "conclusion"}
```

### 왜 필요한가

섹션 정보가 없으면 경로 B(섹션 특화 QA)가 동작하지 않는다.

```
질문: "이 논문의 연구 방법이 뭐야?"

섹션 정보 없이 검색하면:
  → "우리는 다음 방법을 제안한다" (Introduction 문장) ← 가장 유사해 보임
  → "방법론의 전체 개요는..." (Abstract 문장) ← 두 번째
  → 실제 Method 섹션 내용이 밀릴 수 있음

섹션 "method" 필터 적용하면:
  → Method 섹션 청크만 검색 대상
  → 정확한 방법론 내용 반환
```

**관련 코드**: `backend/modules/section_detector.py`

---

## 단계 4. 청킹 (Chunking)

### 무슨 일이 일어나는가

섹션 태그가 붙은 텍스트를 512토큰 단위로 나눈다. 앞뒤 64토큰씩 겹치게 한다.

```
[입력] Method 섹션 텍스트 (3,200토큰)

[출력] 청크 7개:
  청크 1: 토큰 1~512 (섹션: method, paper: bert)
  청크 2: 토큰 449~960 (449~512는 청크 1과 겹침)
  청크 3: 토큰 897~1408 (897~960은 청크 2와 겹침)
  ...
  청크 7: 토큰 2753~3200
```

### 겹치는 이유 (중요)

중요한 문장이 청크 경계에 걸릴 수 있다.

```
청크 경계 상황 예시:
  청크 3 마지막: "We use alpha=0.3 as the"
  청크 4 처음:  "optimal hyperparameter for our experiments."

→ "alpha=0.3이 최적" 이라는 정보가 어느 청크에도 온전히 없음

64토큰 겹침 적용 후:
  청크 3 마지막: "We use alpha=0.3 as the optimal hyperparameter for our experiments."
  청크 4 처음:  "alpha=0.3 as the optimal hyperparameter for our experiments. The result shows..."

→ 어느 청크에서도 "alpha=0.3 최적" 정보를 검색할 수 있음
```

**관련 코드**: `backend/modules/chunker.py`

---

## 단계 5. 임베딩 생성

### 무슨 일이 일어나는가

각 청크를 BGE-M3 모델로 처리해 1024차원 벡터로 변환한다.

```
[입력] 청크 텍스트:
  "We use alpha=0.3 as the optimal hyperparameter. 
   The result shows Faithfulness improved from 0.67 to 0.82."

[출력] 1024차원 벡터:
  [0.021, -0.143, 0.892, 0.034, -0.217, 0.561, 0.103, ...(1024개)]
```

이 숫자들이 뭘 의미하는지 직접 읽기는 어렵다. 하지만 의미가 비슷한 두 문장의 벡터는 서로 가깝다(코사인 유사도 높음).

### 왜 BM25만 쓰지 않는가

```
질문: "CAD에서 alpha가 뭐야?"
논문: "파라미터 α는 비맥락적 생성 분포의 억제 강도를 결정한다."

BM25 검색: "alpha"라는 단어가 논문에서 "α"로만 표기되어 있으면 못 찾음
Dense 검색: 의미가 같으므로 벡터가 가깝다 → 찾음
```

**관련 코드**: `backend/modules/embedder.py`

---

## 단계 6. 벡터 저장

### 무슨 일이 일어나는가

벡터, 원본 텍스트, 메타데이터를 ChromaDB에 저장한다. 동시에 논문 제목, 파일명, 청크 수를 SQLite에 기록한다.

```
ChromaDB 저장 내용 (청크 1개):
  {
    "id": "bert_chunk_047",
    "embedding": [0.021, -0.143, ...],  ← 검색에 사용
    "document": "We use alpha=0.3 as the optimal...",  ← 검색 후 반환
    "metadata": {
      "paper_id": "paper_nlp_bge",
      "section": "method",
      "chunk_index": 47
    }
  }
```

**관련 코드**: `backend/modules/vector_store.py`

---

# 2부. 질문 처리 흐름

---

## 단계 1. 인증 확인

### 무슨 일이 일어나는가

JWT 토큰(로그인 시 발급받은 인증서)을 확인해 사용자가 누구인지 파악한다. 각 사용자의 문서는 분리된 컬렉션에 저장되어, 내가 올린 논문만 내가 접근할 수 있다.

### 왜 필요한가

인증 없이 설계하면 다른 사용자의 논문 내용이 내 검색 결과에 섞인다. 또한 무제한 요청으로 서버가 과부하될 수 있다.

**관련 코드**: `backend/api/routers/chat.py`, `backend/api/dependencies.py`

---

## 단계 2. 경로 선택 (Query Routing)

### 무슨 일이 일어나는가

질문 텍스트를 분석해 A~F 중 가장 적합한 경로를 선택한다.

```
[입력] "이 논문의 연구 방법이 뭐야?"

query_router.py 분석:
  - "연구 방법" → 섹션 특화 질문으로 판단
  - "이 논문" → 단일 문서 질문
  → 경로 B 선택

[입력] "BERT와 GPT의 차이가 뭐야?"

query_router.py 분석:
  - "차이" → 비교 질문
  - "BERT와 GPT" → 복수 문서
  → 경로 C 선택
```

### 더 단순한 방법과 비교

경로 선택 없이 모든 질문을 경로 A로 처리하면:
- "연구 방법이 뭐야?"에 Introduction 내용이 섞임
- "두 논문을 비교해줘"에 한 논문만 검색됨
- "퀴즈 만들어줘"에 답변 형식 텍스트가 나옴

경로 분리는 각 질문 유형에 최적화된 처리를 가능하게 한다.

**관련 코드**: `backend/modules/query_router.py`

---

## 단계 3. 쿼리 확장 (경로 A 기준)

### 무슨 일이 일어나는가

하나의 질문을 두 가지 방법으로 확장해 검색 품질을 높인다.

**방법 1: HyDE (Hypothetical Document Embeddings)**

```
[입력 질문] "BERT의 핵심 아이디어가 뭐야?"

[HyDE 가상 답변 생성]
  "BERT의 핵심 아이디어는 양방향(bidirectional) Transformer를 이용한 
   사전학습이다. Masked Language Model(MLM) 방식으로 문장의 일부 토큰을 
   [MASK]로 가리고, 나머지 문맥에서 가려진 토큰을 예측하도록 훈련한다.
   이를 통해 왼쪽과 오른쪽 문맥을 동시에 학습한다."

→ 이 가상 답변으로 실제 논문 검색
```

왜 질문보다 가상 답변이 더 잘 찾히는가:

```
질문 벡터와 논문 문장의 거리:
  "BERT의 핵심 아이디어가 뭐야?" ←─── 거리 크다 ───→ "BERT uses bidirectional Transformers..."

가상 답변 벡터와 논문 문장의 거리:
  "양방향 Transformer 사전학습이다" ←─ 거리 작다 ─→ "BERT uses bidirectional Transformers..."
```

표현 방식이 비슷할수록 임베딩 벡터가 가깝다.

**방법 2: 다중 쿼리 생성**

```
원래 질문: "BERT의 핵심 아이디어가 뭐야?"

추가 쿼리:
  - "BERT 사전학습 방법론"
  - "양방향 언어 모델 구조"
  - "Masked Language Model이란"
  - "BERT Transformer 구조"
```

같은 내용을 다른 표현으로 검색하면 더 다양한 관련 청크를 찾을 수 있다.

**관련 코드**: `backend/modules/query_expander.py`

---

## 단계 4. 하이브리드 검색

### 무슨 일이 일어나는가

두 가지 검색을 동시에 수행하고 RRF로 합친다.

**Dense 검색 (의미 기반)**

```
[HyDE 가상 답변 벡터] ────┐
[다중 쿼리 1 벡터] ────────┤ 각각 ChromaDB에서 가장 가까운 벡터 20개 검색
[다중 쿼리 2 벡터] ────────┘

결과: 의미적으로 유사한 청크 20개 (중복 포함)
```

**BM25 검색 (키워드 기반)**

```
키워드: "BERT", "핵심", "아이디어", "양방향", "Transformer"

→ 이 키워드가 많이 포함된 청크 상위 20개
```

**RRF로 합산**

```
청크 A: Dense 3위, BM25 1위 → RRF: 1/(60+3) + 1/(60+1) ≈ 0.0321
청크 B: Dense 1위, BM25 5위 → RRF: 1/(60+1) + 1/(60+5) ≈ 0.0316
청크 C: Dense 2위, BM25 2위 → RRF: 1/(60+2) + 1/(60+2) ≈ 0.0323

최종 순위: C(0.0323) > A(0.0321) > B(0.0316)
```

양쪽에서 고르게 잘 나온 청크가 최종 상위에 온다.

**관련 코드**: `backend/modules/hybrid_retriever.py`

---

## 단계 5. 재정렬 (Reranking)

### 무슨 일이 일어나는가

하이브리드 검색으로 가져온 20개 후보를 Cross-encoder로 정밀 재정렬한다.

```
[입력] 질문 + 청크 쌍 20개

각 쌍을 Cross-encoder에 입력:
  쌍 1: "BERT 핵심 아이디어? | We use bidirectional Transformers..." → 점수: 0.94
  쌍 2: "BERT 핵심 아이디어? | The attention mechanism in BERT..." → 점수: 0.87
  쌍 3: "BERT 핵심 아이디어? | Training data for BERT includes..." → 점수: 0.41
  ...

[출력] 점수 순으로 정렬된 청크 목록
  → 상위 5~10개만 다음 단계로 전달
```

### Cross-encoder가 더 정밀한 이유

Dense 검색: 질문 벡터와 청크 벡터를 따로 만들어 비교
→ 두 텍스트를 동시에 보지 않아 세밀한 관계 파악 어려움

Cross-encoder: `[질문] + [청크]`를 하나로 이어 붙여 입력
→ 두 텍스트의 모든 단어 관계를 함께 분석 → 더 정밀

Cross-encoder가 처음부터 수천 개에 적용 불가능한 이유: 하나 계산에 수백 ms → 수천 개면 수십 분. 그래서 Dense로 먼저 20개로 줄이고, 그 20개에만 적용한다.

**관련 코드**: `backend/modules/reranker.py`

---

## 단계 6. 컨텍스트 압축

### 무슨 일이 일어나는가

재정렬된 상위 청크에서 질문과 관련 있는 문장만 추려낸다.

```
[입력] 상위 청크 5개 (총 약 2,500토큰)

청크 1 (512토큰):
  "BERT introduces a new pre-training objective called Masked LM.
   The training data consists of BooksCorpus (800M words) and English Wikipedia.
   We randomly mask 15% of all WordPiece tokens in each sequence.
   In cases when a word is masked, the model predicts the original vocabulary 
   id of the masked word based on its context."

압축 후 (질문 "BERT 핵심 아이디어?") 관련 문장만:
  "BERT introduces a new pre-training objective called Masked LM.
   We randomly mask 15% of all WordPiece tokens in each sequence.
   The model predicts the original vocabulary id of the masked word based on its context."

[출력] 핵심 문장만 추린 컨텍스트 (약 800토큰)
```

### 왜 필요한가

언어 모델에는 컨텍스트 길이 한계가 있다. 관련 없는 문장이 많으면:
1. 처리 시간이 늘어남
2. "Lost in the middle" 현상: 긴 컨텍스트 중간에 있는 핵심 내용을 모델이 놓치는 현상

압축하면 핵심 근거만 남아 답변 품질이 높아지고 처리 속도도 빨라진다.

**관련 코드**: `backend/modules/context_compressor.py`

---

## 단계 7. 답변 생성 (CAD + SCD)

### 무슨 일이 일어나는가

압축된 컨텍스트와 질문으로 MIDM 모델을 호출한다. 이때 CAD와 SCD가 생성 과정에서 개입한다.

### CAD 동작 (Hallucination 억제)

```
같은 입력을 두 번 모델에 넣는다:
  실행 1: [컨텍스트 포함] 질문 → logits_문서있음
  실행 2: [컨텍스트 없음] 질문 → logits_문서없음

조정:
  logits_최종 = logits_문서있음 - 0.3 × logits_문서없음
```

예시 (다음 토큰 예측):

```
"alpha=___ 일 때" 다음에 올 숫자 예측:

logits_문서있음: "0.3" 확률 0.70, "0.5" 확률 0.20, "0.7" 확률 0.10
logits_문서없음: "0.5" 확률 0.40, "0.7" 확률 0.35, "0.3" 확률 0.25
(컨텍스트 없으면 0.5나 0.7 같은 "흔한" 값을 더 많이 예측)

CAD 조정 후 (alpha=0.3):
  "0.3": 0.70 - 0.3×0.25 = 0.625  ← 올라감
  "0.5": 0.20 - 0.3×0.40 = 0.080  ← 내려감
  "0.7": 0.10 - 0.3×0.35 = 0.005  ← 내려감

결과: "0.3" 선택 → 논문 내용과 일치
```

### SCD 동작 (Language Drift 억제)

```
답변 중 "이 논문은 " 다음 토큰 예측:

원래 logits:
  "제안합니다" (한국어): 0.30
  "proposes"  (영어):   0.50  ← 영어 논문 영향으로 높음
  "suggests"  (영어):   0.20

SCD 적용 (beta=0.3):
  "제안합니다": 0.30 (변화 없음, 한국어이므로)
  "proposes":   0.50 - 0.30 = 0.20  ← 영어 토큰이므로 페널티
  "suggests":   0.20 - 0.30 = -0.10 → 확률 거의 0

결과: "제안합니다" 선택
```

**관련 코드**: `backend/modules/cad_decoder.py`, `backend/modules/scd_decoder.py`, `backend/modules/generator.py`

---

## 단계 8. 후속 질문 생성

### 무슨 일이 일어나는가

답변이 완성된 후, 사용자가 자연스럽게 다음으로 물어볼 만한 질문 2~3개를 생성한다.

```
[입력]
  질문: "BERT의 핵심 아이디어가 뭐야?"
  답변: "BERT는 양방향 Transformer로 Masked LM 방식으로 사전학습합니다..."

[출력 후속 질문]
  - "BERT와 GPT의 가장 큰 차이는 뭐야?"
  - "BERT의 Masked Language Model이 구체적으로 어떻게 동작해?"
  - "BERT를 fine-tuning할 때 어떤 방식을 써?"
```

이 질문들은 논문 내용을 더 깊이 탐색하게 유도한다.

**관련 코드**: `backend/modules/followup_generator.py`

---

## 단계 9. 최종 반환

### 무슨 일이 일어나는가

```
최종 응답 구조:
{
  "answer": "BERT의 핵심 아이디어는...",
  "sources": [
    {"paper": "paper_nlp_bge", "section": "method", "text": "BGE M3 supports dense..."},
    {"paper": "paper_nlp_bge", "section": "abstract", "text": "M3-Embedding introduces..."}
  ],
  "route": "A",
  "steps": ["query_expansion", "hybrid_retrieval", "reranking", "compression", "CAD+SCD"],
  "followup_questions": ["GPT와의 차이?", "Masked LM 방법은?", "Fine-tuning 방법은?"]
}
```

### SSE 스트리밍 모드

스트리밍 엔드포인트(`/api/chat/query/stream`)에서는 답변이 한 번에 오지 않고 토큰 단위로 전달된다.

```
이벤트 흐름:
  event: metadata  → {"route": "A", "sources": [...]}
  event: token     → "BERT"
  event: token     → "의"
  event: token     → " 핵심"
  event: token     → " 아이디어는"
  ...
  event: done      → {"full_answer": "...", "followup": [...]}
```

30초를 기다리는 대신, 글자가 나오는 즉시 화면에 표시된다.

---

# 3부. 평가 흐름

---

## Judge 엔드포인트 (`/api/chat/judge`)

### 무슨 일이 일어나는가

실험 평가에서 각 답변의 품질을 자동으로 판정한다.

```
[입력 프롬프트]
  "검색된 컨텍스트와 답변을 보고 반드시 다음 중 하나만 출력하라:
   SUPPORTED / PARTIAL / UNSUPPORTED

   [컨텍스트]
   예시 실험에서는 alpha=0.3 설정이 가장 높은 Faithfulness를 보였다.

   [답변]
   alpha=0.5일 때 가장 좋은 결과가 나왔다.

   Label:"

[출력]
  "UNSUPPORTED"
```

이 레이블을 집계해 Faithfulness 점수를 계산한다.

```
실험 1개 config에서:
  질문 60개 × 평균 3개 문장 = 180번 judge 호출
  SUPPORTED: 140번, PARTIAL: 25번, UNSUPPORTED: 15번

Faithfulness = (140 × 1.0 + 25 × 0.5 + 15 × 0.0) / 180 = 0.847
```

### max_new_tokens가 32인 이유

```
max_new_tokens=8이면:
  모델 출력: "물론이죠, 아래 답변을" → 레이블이 잘려 출력 안 됨
  → PARTIAL로 fallback (정확도 저하)

max_new_tokens=32이면:
  모델 출력: "물론이죠, 아래 답변을 평가하겠습니다: UNSUPPORTED"
  → 레이블이 포함됨 → 정확한 판정
```

**관련 코드**: `backend/api/routers/chat.py`, `backend/evaluation/ragas_eval.py`

---

## 검색 전용 엔드포인트 (`/api/chat/search`)

답변 생성 없이 검색 결과만 반환한다. 실험에서 검색 단계가 제대로 동작하는지 독립적으로 확인할 때 사용한다.

```
[입력] {"query": "CAD alpha 최적값", "collection": "papers"}
[출력] 상위 10개 청크 (텍스트 + 유사도 점수 + 섹션 정보)
```

이를 통해 Context Precision 문제 진단이 가능하다:
"검색 결과에 관련 없는 청크가 많이 나온다면 → 임베딩 모델 또는 BM25 설정 문제"

---

참고문헌 번호(`[N]`)는 `docs/PAPER/THESIS.md`의 참고문헌 목록 기준이다 (총 39편)
