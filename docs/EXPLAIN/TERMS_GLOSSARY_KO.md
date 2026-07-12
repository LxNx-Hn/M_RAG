# M-RAG 용어사전

이 문서는 논문과 코드에 나오는 핵심 용어를 설명한다. 정의, 동작 원리, 실제 예시, 더 단순한 방법과의 비교 순서로 설명한다.

아래의 숫자와 짧은 문장 조각은 이해를 돕기 위한 예시다. 실제 실험 수치와 최종 표는 `experiments/results/` 산출물을 기준으로 확인한다.

---

## RAG

### 정의

RAG는 Retrieval-Augmented Generation의 약자다. 언어 모델이 답하기 전에 먼저 관련 문서를 검색하고, 그 검색 결과를 근거로 삼아 답변을 만드는 방식이다.

### 왜 필요한가

언어 모델은 훈련 때 배운 지식만 갖고 있다. 특정 논문 내용, 최신 연구 결과, 내부 문서 내용은 훈련 데이터에 없기 때문에 모른다. RAG는 검색으로 관련 문서를 찾아 모델에게 "이 내용을 참고해서 답해라"고 제공한다.

### 더 단순한 방법과 비교

**단순한 방법: 언어 모델에게 그냥 물어보기**
> 질문: "M-RAG 논문에서 CAD의 alpha 최적값이 뭐야?"
> 모델 답변: "일반적으로 0.5–0.7 사이가 좋습니다." (훈련 기억 기반, 틀릴 수 있음)

**RAG 방법: 논문을 먼저 검색해서 제공**
> 시스템이 논문에서 "예시 실험에서는 alpha=0.3 설정이 가장 높은 Faithfulness를 보였다"라는 문장을 찾아 모델에게 제공
> 모델 답변: "제공된 문맥에 따르면 alpha=0.3 설정이 가장 높은 Faithfulness를 보였습니다."

### 비유

시험에서 암기만으로 답하는 대신, 허용된 참고서를 펼쳐 놓고 그 내용을 근거로 답하는 오픈북 시험과 같다.

### 코드 위치

`backend/pipelines/*`, `backend/modules/hybrid_retriever.py`, `backend/modules/generator.py`

---

## Modular RAG

### 정의

질문 유형에 따라 서로 다른 검색/생성 경로(파이프라인)를 선택하는 RAG 구조다. M-RAG는 A–F 6개 경로를 갖는다.

### 왜 필요한가

하나의 경로로 모든 질문을 처리하면 어떤 질문에서 최적이 아니다.

**예시 비교**

| 질문 | 단일 경로의 문제 | Modular RAG 해결 |
|---|---|---|
| "이 논문의 연구 방법이 뭐야?" | 논문 전체를 검색해 Introduction, Result까지 섞임 | B 경로가 Method 섹션만 우선 검색 |
| "두 논문의 차이가 뭐야?" | 한 논문만 검색 가능 | C 경로가 두 문서를 동시에 검색 |
| "퀴즈 만들어줘" | 답변 형식으로 출력 | F 경로가 문제+선택지+해설 형식 출력 |

### 비유

병원에서 모든 환자를 같은 진료실로 보내지 않고, 증상에 따라 내과, 정형외과, 영상의학과로 나눠 보내는 것과 같다.

### 코드 위치

`backend/modules/query_router.py` (경로 선택), `backend/pipelines/` (각 경로 구현)

---

## Chunking (청킹)

### 정의

긴 문서를 검색과 언어 모델 처리에 적합한 크기의 조각(청크)으로 나누는 과정이다.

### 왜 필요한가

**이유 1: 언어 모델 한계**
언어 모델은 한 번에 처리할 수 있는 텍스트 양에 한계가 있다(컨텍스트 길이). 100페이지 논문을 통째로 넣을 수 없다.

**이유 2: 검색 정밀도**
논문 전체를 하나의 단위로 저장하면, 질문과 관련된 특정 단락을 찾지 못한다. 작은 조각으로 나눠야 정확한 위치를 찾을 수 있다.

### 실제로 어떻게 나뉘는가

원본 논문 텍스트 예시:
```
...CAD는 문서가 있을 때의 생성 분포와 없을 때의 생성 분포를 
대조해 파라메트릭 지식 개입을 억제한다. 실험에서 alpha=0.3일 때 
Faithfulness가 0.82로 가장 높았다. SCD는 목표 언어가 아닌 토큰에
패널티를 적용해 Language Drift를 줄인다...
```

청크 1 (512 토큰 기준):
```
...CAD는 문서가 있을 때의 생성 분포와 없을 때의 생성 분포를 
대조해 파라메트릭 지식 개입을 억제한다. 실험에서 alpha=0.3일 때 
Faithfulness가 0.82로 가장 높았다.
```

청크 2 (앞 청크와 64 토큰 겹침):
```
실험에서 alpha=0.3일 때 Faithfulness가 0.82로 가장 높았다. 
SCD는 목표 언어가 아닌 토큰에 패널티를 적용해 Language Drift를 줄인다...
```

겹치는 이유: "alpha=0.3일 때 Faithfulness 0.82" 문장이 두 청크 경계에 걸려도, 어느 청크에서 검색해도 이 내용을 포함한다.

### 기본 설정

- 청크 크기: 512 토큰 (약 단어 400개)
- 겹침(overlap): 64 토큰

### 코드 위치

`backend/modules/chunker.py`

---

## Embedding (임베딩)

### 정의

텍스트 문장을 고정된 개수의 숫자 배열(벡터)로 변환하는 과정이다. 의미가 비슷한 문장은 변환된 벡터도 서로 가까운 위치에 놓인다.

### 실제로 어떻게 생겼는가

"달이 지구를 돈다"를 BGE-M3 모델로 임베딩하면 1024개의 숫자가 나온다:
```
[0.021, -0.143, 0.892, 0.034, -0.217, 0.561, ...(1024개 숫자)]
```

이 숫자들은 의미 공간에서의 좌표다. 숫자 하나하나가 무엇을 의미하는지는 사람이 해석하기 어렵지만, 두 벡터 사이의 거리가 두 문장의 의미적 유사도를 나타낸다.

### 핵심 원리

```
"달이 지구를 돈다" → [0.021, -0.143, 0.892, ...]  ←거리 가까움
"The moon orbits the Earth" → [0.019, -0.141, 0.889, ...]  ↗

"오늘 날씨가 맑다" → [-0.891, 0.234, -0.102, ...]  ←거리 멂
```

같은 의미를 가진 한국어와 영어 문장의 벡터가 서로 가깝다. 이것이 한국어 질문으로 영어 논문을 검색할 수 있는 이유다.

### M-RAG에서 사용하는 모델

BAAI/bge-m3: 100개 이상의 언어를 같은 벡터 공간에서 표현한다. 출력 벡터 크기는 1024차원이다.

### 코드 위치

`backend/modules/embedder.py`

---

## Vector Store (벡터 저장소)

### 정의

임베딩 벡터와 원본 텍스트를 함께 저장하고, 쿼리 벡터와 가장 가까운 벡터들을 빠르게 찾아주는 데이터베이스다.

### 일반 데이터베이스와 차이

**일반 데이터베이스(SQLite 등)**
```sql
SELECT * FROM chunks WHERE text LIKE '%CAD alpha%'
```
→ 정확히 "CAD alpha"라는 글자가 있어야만 찾음

**벡터 저장소(ChromaDB)**
```python
vector_store.search("CAD에서 alpha 파라미터의 역할")
```
→ "alpha 값은 파라메트릭 지식 억제 강도를 결정한다"처럼 표현이 달라도 의미가 비슷하면 찾음

### M-RAG에서 사용하는 것

ChromaDB: 오픈소스 벡터 데이터베이스. 청크의 임베딩 벡터와 원본 텍스트, 섹션 정보를 함께 저장한다.

### 코드 위치

`backend/modules/vector_store.py`

---

## Dense Retrieval (밀집 검색)

### 정의

텍스트를 벡터로 변환한 뒤, 쿼리 벡터와 가장 가까운(코사인 유사도가 높은) 문서 벡터를 찾는 검색 방식이다.

### 코사인 유사도란

두 벡터가 같은 방향을 가리킬수록 1에 가깝고, 반대 방향이면 -1이다. 의미가 비슷한 문장일수록 코사인 유사도가 1에 가깝다.

### BM25와의 차이

| | Dense Retrieval | BM25 |
|---|---|---|
| 찾는 방식 | 의미가 비슷한 것 | 키워드가 일치하는 것 |
| 강점 | 표현이 달라도 찾음 | 전문 용어, 숫자에 강함 |
| 약점 | 정확한 키워드를 놓칠 수 있음 | 표현이 다르면 못 찾음 |
| 예시 | "달이 지구를 돈다" → "월-지구 공전" 찾음 | "CAD alpha 0.3" → 정확히 그 숫자가 있는 곳 찾음 |

### 코드 위치

`backend/modules/embedder.py`, `backend/modules/vector_store.py`

---

## BM25

### 정의

문서 안에 검색 키워드가 얼마나 자주 등장하는지(TF)와, 그 키워드가 전체 문서 중 얼마나 드문지(IDF)를 조합해 검색 점수를 계산하는 방법이다.

### 점수 계산 원리 (직관적으로)

```
BM25 점수 ↑ 조건:
1. 이 청크에 검색어가 많이 나올수록 (TF 높음)
2. 검색어가 다른 청크에는 잘 안 나올수록 (IDF 높음, 즉 희귀한 단어일수록)
3. 청크가 너무 길지 않을수록 (긴 문서는 자연히 단어가 많아 불공평)
```

### 실제 예시

검색어: "CAD alpha"

청크 A: "CAD의 alpha 값은 0.3이다. alpha가 높을수록 억제가 강하다." → 점수 높음 (alpha가 2번 나옴)
청크 B: "실험 결과 Faithfulness가 개선됐다." → 점수 낮음 (alpha 없음)
청크 C: "모든 파라미터는 alpha, beta, gamma로 구성된다." → 점수 중간 (alpha 1번, 하지만 "CAD" 없음)

### 코드 위치

`backend/modules/hybrid_retriever.py`

---

## Hybrid Retrieval (하이브리드 검색)

### 정의

Dense Retrieval(의미 기반)과 BM25(키워드 기반)를 동시에 수행하고, 두 결과를 RRF로 합쳐 최종 검색 결과를 만드는 방식이다.

### 왜 둘을 합치는가

**Dense만 쓰면 놓치는 것**
"alpha=0.3"처럼 정확한 숫자가 중요한 경우, 의미적으로 비슷해 보이는 "0.5" 관련 청크가 더 높게 올 수 있다.

**BM25만 쓰면 놓치는 것**
"이 논문이 해결한 문제가 뭐야?"처럼 넓은 의미의 질문은, 키워드 일치만으로는 핵심 청크를 찾기 어렵다.

**합치면**
두 방법 각각의 장점이 보완된다. 양쪽에서 상위에 오른 청크는 특히 신뢰도가 높다.

### 코드 위치

`backend/modules/hybrid_retriever.py`

---

## RRF (Reciprocal Rank Fusion)

### 정의

여러 검색 결과의 순위를 하나로 합치는 수식이다. 각 결과의 순위를 역수로 변환해 합산한다.

### 수식

```
RRF 점수(문서 d) = Σ 1 / (k + rank(d))
```
k는 보정 상수(보통 60), rank는 각 검색에서의 순위다.

### 실제 예시

| 청크 | Dense 순위 | BM25 순위 | RRF 점수 |
|---|---|---|---|
| 청크 A | 1위 | 3위 | 1/(60+1) + 1/(60+3) ≈ 0.0320 |
| 청크 B | 5위 | 1위 | 1/(60+5) + 1/(60+1) ≈ 0.0310 |
| 청크 C | 2위 | 2위 | 1/(60+2) + 1/(60+2) ≈ 0.0323 |

→ 청크 C가 양쪽에서 모두 2위이므로 최종 1위가 된다.

### 왜 점수를 그냥 더하지 않는가

Dense 점수는 0–1 사이 코사인 유사도고, BM25 점수는 0–수십까지 나올 수 있다. 단위가 달라 그냥 더하면 BM25가 압도한다. RRF는 순위만 사용하므로 점수 단위가 달라도 공정하게 합칠 수 있다.

### 코드 위치

`backend/modules/hybrid_retriever.py`

---

## Reranker (재정렬 모델)

### 정의

처음 검색으로 가져온 후보 청크들을 질문과 함께 다시 정밀하게 비교해 재정렬하는 모델이다. Cross-encoder 방식으로, 질문과 각 청크를 쌍으로 입력해 관련도 점수를 계산한다.

### Dense 검색과의 차이

**Dense 검색 (Bi-encoder)**
질문 벡터와 청크 벡터를 따로 만들어 비교한다. 빠르지만 두 텍스트를 함께 보지 않아 세밀한 비교가 어렵다.

**Reranker (Cross-encoder)**
질문과 청크를 하나로 이어 붙여 모델에 입력한다.
```
입력: "[질문] CAD의 alpha 최적값은? [청크] alpha=0.3일 때 Faithfulness 0.82 달성"
출력: 관련도 점수 0.91
```
두 텍스트를 동시에 보기 때문에 더 정밀하지만, 후보 전체를 이렇게 비교하면 너무 느리다.

### 왜 두 단계로 나누는가

```
전체 청크 (수천 개)
        ↓ Dense 검색 (빠름, 대략적)
상위 20–30개 후보
        ↓ Reranker (느리지만 정밀)
최종 상위 5–10개
```

처음부터 Reranker를 수천 개에 적용하면 너무 느리다. Dense로 먼저 좁히고, 좁혀진 후보에만 Reranker를 쓰면 속도와 정확도 모두 얻는다.

### 코드 위치

`backend/modules/reranker.py`

---

## HyDE (Hypothetical Document Embeddings)

### 정의

질문에 대해 가상의 답변 문서를 먼저 생성하고, 그 가상 문서로 실제 검색을 수행하는 방식이다.

### 왜 질문 그대로 검색하면 부족한가

질문 문장과 논문 문장은 표현 방식이 다르다.

```
질문:  "CAD에서 alpha가 뭐야?"
논문:  "파라미터 α는 비맥락적 생성 분포의 가중치를 결정하며, 실험에서 α=0.3이 최적으로 나타났다."
```

의미는 같지만 표현이 달라서, 질문 벡터와 논문 문장 벡터의 유사도가 낮을 수 있다.

### HyDE 해결 방식

```
질문: "CAD에서 alpha가 뭐야?"
     ↓ 언어 모델이 가상 답변 생성
가상 답변: "CAD의 alpha는 비맥락적 생성의 억제 강도를 결정하는 파라미터다. 
            값이 클수록 파라메트릭 지식 개입이 줄어든다."
     ↓ 가상 답변으로 검색
논문 문장: "파라미터 α는 비맥락적 생성 분포의 가중치를 결정하며..." ← 훨씬 잘 찾힘
```

가상 답변이 논문 표현과 더 비슷해서, 임베딩 거리가 가깝고 검색 정확도가 높아진다.

### 코드 위치

`backend/modules/query_expander.py`

---

## RAGAS

### 정의

RAG 시스템을 자동으로 평가하기 위한 평가 프레임워크다. 사람이 직접 채점하는 대신, 언어 모델이 여러 기준으로 답변 품질을 판정한다.

### 4가지 지표 관계

```
질문 ──────────────────────────────┐
  │                                 │
  ▼                                 │
[검색] → 컨텍스트 ──→ [생성] → 답변 ┘
            │                  │
            │                  │
     Context Precision    Faithfulness (답변이 컨텍스트에 근거하는가)
     Context Recall       Answer Relevancy (답변이 질문에 맞는가)
```

### M-RAG에서 사용하는 방식

공식 평가는 RAGAS 0.2.15 패키지로 네 가지 지표를 계산한다. 프로젝트 코드는 RAGAS를 대체해 점수 공식을 임의 구현하지 않고, 고정 judge·로컬 임베딩·재시도·provenance 기록·null 셀 처리를 오케스트레이션한다. 별도의 lightweight evaluator는 빠른 점검용이며 공식 논문 점수와 섞지 않는다.

### 코드 위치

`experiments/evaluators/official_ragas_runner.py`

---

## Faithfulness (충실도)

### 정의

답변의 각 주장이 검색된 컨텍스트(문서 내용)에 의해 얼마나 지지되는지를 나타내는 지표다. 0–1 사이 값이며, 1이 완전히 충실하다는 뜻이다.

### 측정 방법

Judge 모델이 답변의 각 문장을 보고 판정한다.

```
컨텍스트: "실험 결과 alpha=0.3일 때 Faithfulness 0.82로 최고였다."
답변 문장 1: "alpha=0.3일 때 Faithfulness가 가장 높았다." → SUPPORTED ✓
답변 문장 2: "alpha=0.5일 때 가장 좋은 결과가 나왔다." → UNSUPPORTED ✗ (컨텍스트와 다름)
답변 문장 3: "일부 실험에서 개선이 확인됐다." → PARTIAL △

Faithfulness = SUPPORTED 수 / 전체 문장 수 = 1/3 ≈ 0.33
```

### 낮아지는 원인

Hallucination(모델이 컨텍스트에 없는 내용을 지어냄)이 주요 원인이다. CAD를 적용하면 Faithfulness가 올라가는 것을 실험으로 측정했다.

### 코드 위치

`experiments/evaluators/official_ragas_runner.py` (RAGAS `faithfulness`)

---

## Answer Relevancy (답변 관련성)

### 정의

답변이 질문에 얼마나 직접적으로 답하는지를 나타내는 지표다. 답변이 사실이어도, 질문이 묻지 않은 것을 말하면 점수가 낮아진다.

### 낮은 경우와 높은 경우 비교

```
질문: "CAD의 alpha 최적값이 뭐야?"

Answer Relevancy 낮음:
"CAD는 Context-Aware Decoding의 약자입니다. 2023년에 제안됐으며, 
 파라메트릭 지식 억제에 효과적인 방법입니다."
→ 사실이지만 alpha 값에 대한 답이 없음

Answer Relevancy 높음:
"본 논문의 실험에서 alpha=0.3일 때 Faithfulness 0.82로 최적이었습니다."
→ 질문이 요구한 alpha 값을 직접 답함
```

### 코드 위치

`experiments/evaluators/official_ragas_runner.py` (RAGAS `answer_relevancy`)

---

## Context Precision (컨텍스트 정밀도)

### 정의

검색해온 컨텍스트(청크들) 중에서 실제로 답변을 만드는 데 유용한 청크의 비율이다.

### 높은 경우와 낮은 경우 비교

```
질문: "CAD의 alpha 최적값이 뭐야?"

검색 결과 5개:
청크 1: "alpha=0.3일 때 Faithfulness 0.82" → USEFUL ✓
청크 2: "SCD의 beta 값은 0.1–0.5 범위" → NOISY ✗ (관련 없음)
청크 3: "alpha가 높을수록 억제 강도가 커짐" → USEFUL ✓
청크 4: "실험은 7개 논문에서 진행됨" → NOISY ✗ (관련 없음)
청크 5: "alpha=0.0이면 CAD 비활성화" → PARTIAL △

Context Precision = USEFUL 2 / 전체 5 = 0.40
```

검색 모듈이 관련 없는 청크를 많이 가져올수록 낮아진다.

### 코드 위치

`experiments/evaluators/official_ragas_runner.py` (RAGAS `context_precision`)

---

## Context Recall (컨텍스트 재현율)

### 정의

정답을 만드는 데 필요한 근거가 검색 결과에 얼마나 포함됐는지를 나타낸다. 필요한 근거를 빠뜨리지 않았는지를 측정한다.

### 높은 경우와 낮은 경우 비교

```
정답(Ground Truth): "alpha=0.3이 최적이고, Faithfulness 0.82를 달성했으며,
                    이는 CAD 없음(alpha=0) 대비 0.15 향상됐다."

필요한 근거:
① alpha=0.3 최적 → 검색에 포함 ✓
② Faithfulness 0.82 → 검색에 포함 ✓
③ CAD 없음 대비 0.15 향상 → 검색에 없음 ✗

Context Recall = 2/3 ≈ 0.67
```

검색이 관련 청크를 전부 가져오지 못할 때 낮아진다.

### 코드 위치

`experiments/evaluators/official_ragas_runner.py` (RAGAS `context_recall`)

---

## Hallucination (환각)

### 정의

언어 모델이 컨텍스트(문서)에 없는 사실을 그럴듯하게 만들어내는 현상이다. 모델이 훈련 데이터에서 배운 기억이 문서 내용보다 강하게 출력될 때 발생한다.

### 실제 발생 예시

```
컨텍스트(논문 내용): "본 모델은 KorQuAD에서 F1 87.3을 달성했다."

Hallucination이 발생한 답변:
"본 모델은 KorQuAD에서 F1 92.1을 달성했습니다."
→ 숫자를 바꿔서 말함 (훈련 중 비슷한 실험에서 90점대를 많이 봤기 때문)
```

### 이 프로젝트에서 특히 위험한 이유

논문 리뷰 시스템이므로, 성능 수치, 실험 조건, 결론이 틀리면 사용자가 잘못된 논문 이해를 갖게 된다. 학술적 맥락에서 Hallucination은 특히 해롭다.

### 억제 방법

CAD: 모델의 사전 기억 개입을 수식으로 줄임
Faithfulness 측정: Hallucination이 얼마나 발생했는지 정량화

---

## Language Drift (언어 이탈)

### 정의

한국어로 질문했는데, 영어 논문 내용의 영향으로 답변에 영어가 섞이거나 영어 중심 답변이 나오는 현상이다.

### 실제 발생 예시

```
질문(한국어): "이 논문의 핵심 기여가 뭐야?"

Language Drift 발생 답변:
"이 논문의 핵심 기여는 We propose a novel CAD-based approach that 
effectively reduces parametric knowledge interference를 통해 
한국어 RAG 성능을 개선한 것입니다."
→ 한국어 문장 중간에 영어가 섞임
```

### 왜 발생하는가

영어 논문에서 검색된 청크를 컨텍스트로 제공하면, 언어 모델이 영어 텍스트의 영향을 받아 영어 토큰을 출력하는 확률이 높아진다. 특히 전문 용어나 논문 특유의 표현에서 자주 발생한다.

### 억제 방법

SCD: 한국어 답변 중 영어 토큰이 나오려 할 때 그 확률을 낮춤

---

## CAD (Context-Aware Decoding)

### 정의

언어 모델이 컨텍스트(문서)를 참고할 때와 참고하지 않을 때의 생성 분포를 비교하고, 그 차이를 이용해 파라메트릭 지식(훈련 기억) 개입을 억제하는 생성 제어 방법이다.

### 수식

```
logits_최종 = (1 + α) × logits_문서있음 - α × logits_문서없음
```

- `logits_문서있음`: 논문 내용을 참고해서 다음 토큰을 예측한 점수
- `logits_문서없음`: 논문 없이 훈련 기억만으로 다음 토큰을 예측한 점수
- `α (alpha)`: 문맥/무문맥 대조 강도. 논문 실험 고정값은 0.5

### 직관적으로 이해하기

문맥이 있을 때와 없을 때의 raw logit 차이를 이용해 문맥 의존 후보의 상대 순위를
높이는 방식이다. 계산 대상은 확률이 아니며 음수 logit도 있으므로, 모든 후보가
무조건 숫자상 오르거나 내린다고 설명하지 않는다.

### alpha 값 선택

alpha가 너무 크면 문맥 조건을 과도하게 강조할 수 있고, 너무 작으면 대조 효과가
약할 수 있다. 현재 논문 실험은 별도 sensitivity 결과가 아니라 고정 `alpha=0.5`를
사용한다.

### 코드 위치

`backend/modules/cad_decoder.py`

---

## SCD (Korean-target Soft Constrained Decoding)

### 정의

답변 생성 중 토큰의 언어군에 따라 raw logit을 조정해 Language Drift를 줄이는
방법이다. 저장소에는 서로 다른 v1과 `reference_scd`가 있으므로 결과도 분리한다.

### 수식

```text
penalty_additive v1: 비한국어·비중립·비whitelist token -> logit - 0.3
reference_scd: 5단계 warm-up 뒤 target -> 1.1 * logit,
               neutral -> unchanged, distractor -> 0.9 * logit
```

`penalty_additive`의 whitelist는 v1 전용이다. `reference_scd`는 참고 논문의 vocabulary
partition을 사용한다. raw logit은 음수일 수 있어 1.1/0.9를 항상적인 숫자
상승/하락으로 단순화하면 안 된다.

### CAD와 SCD가 다른 이유

| | CAD | SCD |
|---|---|---|
| 문제 | 훈련 기억이 문서보다 강하게 나옴 (Hallucination) | 영어가 한국어 답변에 섞임 (Language Drift) |
| 원인 | 모델의 사전 기억 | 영어 컨텍스트의 언어적 영향 |
| 해결 | 문서 있음/없음 분포 대조 | 토큰 언어군별 raw-logit 조정 |

두 방법은 목표가 다르지만 둘 다 디코딩 점수를 바꾸므로 상호작용과 실제 효과를
실험으로 확인해야 한다.

### 코드 위치

`backend/modules/scd_decoder.py`

---

## SSE (Server-Sent Events)

### 정의

서버가 클라이언트에게 이벤트를 순차적으로 단방향으로 보내는 방식이다. 답변이 완성될 때까지 기다리지 않고, 생성되는 토큰을 즉시 전달한다.

### 일반 API와 비교

**일반 HTTP 요청**
```
클라이언트: 질문 전송 →
           (30초 대기, 화면 멈춤)
서버: ← 완성된 답변 전송
```

**SSE 스트리밍**
```
클라이언트: 질문 전송 →
서버: ← "이" 토큰
서버: ← "논문의" 토큰
서버: ← "핵심은" 토큰
...
서버: ← [done] 이벤트 + 후속 질문
```

### 이벤트 종류

| 이벤트 | 내용 |
|---|---|
| `metadata` | 선택된 경로, 출처 청크, 실행 단계 |
| `token` | 답변 텍스트 조각 |
| `done` | 전체 답변 + 후속 질문 |
| `error` | 타임아웃 또는 생성 실패 |

### 코드 위치

`backend/api/routers/chat.py` (`/api/chat/query/stream`)

---

## Ground Truth (정답 기준)

### 정의

평가에서 모델 답변의 품질을 측정할 기준이 되는 정답 답변이다.

### 이 프로젝트에서 어떻게 만드는가

완료된 본 실험은 `experiments/data/query_splits/*.json`의 검증된 `answer_span`을
RAGAS reference로 사용한다. 평가 시 OpenAI 또는 로컬 모델로 GT를 새로 만들거나,
실패 시 pseudo GT로 대체하지 않는다.

### 코드 위치

`experiments/data/query_splits/*.json` (검증된 `answer_span`을 RAGAS reference로 사용; 별도 GT 생성 없음)

---

## LLM-as-Judge (언어 모델 판정자)

### 정의

사람이 직접 채점하는 대신, 언어 모델이 채점자 역할을 하는 평가 방식이다.

### 이 프로젝트의 두 판정 경로

- 서비스 `/api/chat/judge`: 로컬 경량 판정 API다.
- `official_ragas_runner.py`: RAGAS의 서로 다른 지표 프롬프트/계산을 실행한다.

RAGAS에서 faithfulness는 답변 주장과 문맥, answer relevancy는 질문과 답변,
context precision/recall은 질문·문맥·reference를 사용한다. 하나의
`SUPPORTED/PARTIAL/UNSUPPORTED` 레이블로 네 지표를 모두 계산하는 구조가 아니다.

### 한계

Judge 모델 자체가 틀릴 수 있고, 언어 조합에 따라 판정 신뢰도가 달라질 수 있다.
완료된 실험의 null 처리와 재시도 정책은 공식 runner와 결과 artifact로 확인한다.

### 코드 위치

`backend/api/routers/chat.py` (`/api/chat/judge`), `experiments/evaluators/official_ragas_runner.py`

---

## Ablation Study (절제 연구)

### 정의

시스템에서 구성 요소를 하나씩 제거하거나 추가하면서, 각 요소가 성능에 얼마나 기여하는지 측정하는 실험 방법이다.

### 현재 M-RAG 본 실험 설계

```
HyDE off/on × CAD off/on × SCD off/on = 8 configs
```

완료된 본 실험은 RAGAS 4개 지표와 직접 Korean ratio를 측정했다. numeric
hallucination과 query-type별 분석은 아직 측정되지 않은 향후 과제다.

이것이 논문의 핵심 실험이다. A-F route는 졸업작품 서비스 기능이며, 현재 결과는
전역 임시 정책만 뒷받침하고 route별 정책은 별도 검증이 필요하다.

### 코드 위치

`experiments/runners/run_generation.py` (8-config HyDE×CAD×SCD 본 생성)

---

참고문헌 번호(`[N]`)는 `docs/PAPER/THESIS.md`와 `THESIS_KO.md`의 공통 참고문헌 목록 기준이다 (총 20편)

