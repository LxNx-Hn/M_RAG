# M-RAG 논문 본문 초안

- 기준일 2026-04-26
- 상태 현재 코드 기준 제출용 초안
- 원칙 기능과 구조는 현재 저장소 기준으로 서술
- 원칙 미검증 수치는 넣지 않고 결과 재실행 후 삽입

## 고정 제목

### 국문 제목

- M-RAG: 한국어 중심 학술 문서 질의응답을 위한 환각 억제형 모듈러 RAG 시스템

### 영문 제목

- M-RAG: A Hallucination-Controlled Modular Retrieval-Augmented Generation System for Korean-Centered Academic Document Question Answering

## 초록

학술 문서 질의응답은 단순 사실 조회뿐 아니라 섹션 기반 질의, 다중 문서 비교, 인용 추적, 전체 요약처럼 서로 다른 검색 경로를 요구한다  
기존의 일반적인 검색 증강 생성 시스템은 이질적인 질문 유형을 하나의 고정된 검색 및 생성 흐름으로 처리하는 경우가 많아 학술 문서 구조를 충분히 반영하지 못한다  
본 연구는 한국어 중심 학술 문서 질의응답을 위해 질의 라우팅, 하이브리드 검색, 재정렬, 컨텍스트 압축, CAD와 SCD 기반 생성 제어를 결합한 모듈형 시스템 M-RAG를 제안한다  
M-RAG는 질문 의도에 따라 A부터 F까지의 파이프라인을 선택하고, Dense 임베딩과 BM25를 결합한 검색 결과를 재정렬한 뒤, 문서 근거 중심의 응답을 생성한다  
또한 로컬 환경에서 반복 가능한 실험 실행 경로와 결과 표 생성 경로를 함께 제공하여 구현과 평가를 하나의 저장소 안에서 연결한다  
실험은 Track 1의 모듈 누적 ablation과 디코더 비교, Track 2의 도메인 특화 구성 비교로 설계하며, 최종 수치는 재실행된 결과 파일을 기준으로 삽입한다  
본 연구의 기여는 라우트 기반 학술 문서 QA 구조, 검색과 생성 제어의 통합, 한국어 중심 로컬 실험 경로의 정리라는 세 축으로 요약된다

## Abstract

Academic document question answering requires heterogeneous retrieval paths such as section-aware lookup, cross-document comparison, citation tracing, and long-form summarization rather than a single fixed retrieval flow  
Many conventional retrieval-augmented generation systems apply one uniform pipeline to all query types and therefore underutilize document structure in scholarly settings  
This paper presents M-RAG, a modular retrieval-augmented generation system for Korean-centered academic document question answering that combines query routing, hybrid retrieval, reranking, context compression, and CAD plus SCD based decoding control  
M-RAG selects one of six specialized pipelines according to query intent, retrieves evidence with dense retrieval and BM25, reranks candidate passages, and generates grounded answers with controlled decoding  
The system also provides a reproducible local evaluation path with automated result aggregation so that implementation and experimentation remain connected within a single repository  
The evaluation is organized into Track 1 module accumulation and decoder studies and Track 2 domain-oriented comparisons, while final numeric results are inserted only after validated reruns  
The contributions of this work are a route-aware modular QA architecture, an integrated retrieval and decoding-control stack, and a reproducible local experimentation workflow for Korean academic QA

## 주요어

- Modular RAG
- Academic QA
- Korean QA
- Query Routing
- Hybrid Retrieval
- Contrastive Decoding

## 1 서론

대규모 언어 모델은 질의응답과 요약, 비교 설명 같은 고수준 언어 작업에서 강한 표현 능력을 보이지만 학술 문서 환경에서는 여전히 근거 부족과 환각, 언어 이탈 문제가 반복된다  
특히 논문과 강의 자료, 특허 문서처럼 구조가 분명한 문서는 질문 유형에 따라 필요한 검색 범위와 생성 방식이 달라지며, 하나의 균일한 RAG 파이프라인으로는 사용자의 의도를 충분히 반영하기 어렵다  
예를 들어 특정 섹션만을 묻는 질문은 문서 전체 검색보다 섹션 필터가 중요하고, 두 문서를 비교하는 질문은 다중 근거 정렬과 표 형식 정리가 중요하며, 인용 추적 질문은 참고문헌과 외부 식별자 연결이 중요하다  
한국어 사용자 환경에서는 여기에 더해 영어 원문 기반 학술 문서를 한국어 질문으로 다루는 과정에서 용어 혼합과 언어 이탈 문제가 함께 나타난다  

본 연구는 이러한 문제를 해결하기 위해 M-RAG를 제안한다  
M-RAG는 질문을 일반 QA, 섹션 QA, 비교, 인용 추적, 요약, 퀴즈 생성의 여섯 유형으로 분기하고, 각 유형에 맞는 검색 및 생성 경로를 선택하는 라우트 기반 모듈형 구조를 가진다  
검색 단계에서는 Dense 임베딩, BM25, RRF, reranker, context compression을 결합하고, 생성 단계에서는 MIDM 계열 언어 모델에 CAD와 SCD 기반 제어를 연결한다  
구현은 FastAPI 기반 백엔드와 React 기반 프론트엔드, SQLAlchemy 기반 영속 계층과 ChromaDB 저장소, 로컬 실험 러너와 결과 변환 스크립트까지 포함한다  

본 연구의 기여는 다음과 같다  

- 질의 의도에 따라 파이프라인을 분기하는 라우트 기반 모듈형 학술 문서 QA 구조를 제시
- Dense 검색과 BM25, reranker, context compression을 결합한 검색 스택을 학술 문서 QA 맥락에서 통합
- CAD와 SCD를 결합해 근거 중심 생성과 한국어 응답 안정성을 함께 다루는 생성 제어 경로를 제시
- 로컬 실행 가능한 실험 파이프라인과 결과 표 생성 경로를 함께 정리해 구현과 평가의 재현 가능성을 높임

이후 구성은 다음과 같다  
2장에서는 관련 연구를 정리하고  
3장에서는 시스템 구조를 설명하며  
4장에서는 구현과 실험 설계를 기술하고  
5장에서는 결과 정리 방식을 제시하고  
6장과 7장에서는 논의와 결론을 제시한다

## 2 관련 연구

### 2.1 검색 증강 생성 기반 질의응답

검색 증강 생성은 언어 모델 외부에 근거 문서를 연결하여 사실성과 최신성을 보완하는 대표적 접근이다  
그러나 다수의 시스템은 검색기와 생성기의 기본 조합에 집중하며 질문 유형별 처리 경로를 명시적으로 분리하지 않는다  
학술 문서 환경에서는 초록, 방법, 결과, 결론, 참고문헌처럼 구조가 분명하고, 질문 역시 구조 의존성을 갖기 때문에 단일 경로 처리만으로는 한계가 생긴다  

### 2.2 학술 문서 QA와 구조 인식 검색

학술 문서 QA 연구는 논문 검색, 논문 요약, 인용 기반 탐색, 문헌 비교를 중심으로 발전해 왔다  
이 계열 연구들은 보통 검색 품질 개선이나 특정 도메인 특화 기능에 강점을 가지지만, 질의 라우팅과 생성 제어까지 하나의 시스템 안에 묶는 경우는 제한적이다  
M-RAG는 섹션 인식 청킹, 하이브리드 검색, 인용 추적을 결합해 학술 문서 구조를 활용한다는 점에서 이 흐름과 연결된다  

### 2.3 생성 제어와 환각 억제

생성 단계의 사실성 문제를 줄이기 위해 contrastive decoding 계열 접근이 제안되어 왔다  
또한 다국어 혹은 번역 혼합 환경에서는 목표 언어를 유지하기 위한 디코딩 제어가 중요하다  
M-RAG는 CAD와 SCD를 각각 환각 억제와 언어 이탈 억제의 축으로 분리하여 적용하고, 검색 기반 근거와 디코딩 제어를 함께 묶는다  

### 2.4 본 연구의 위치

본 연구는 학술 문서 QA를 위한 구현 중심 시스템 연구로 위치지을 수 있다  
즉 개별 알고리즘 하나의 성능 개선보다 라우팅, 검색, 생성 제어, 실험 실행 경로를 하나의 일관된 구조로 묶는 데 초점을 둔다  
논문에서는 특정 외부 서비스와의 절대적 우열보다, 질문 유형별 경로와 한국어 중심 운용 맥락에서의 통합 설계를 핵심 차별점으로 제시한다

## 3 시스템 설계

### 3.1 전체 구조

M-RAG의 상위 구조는 프론트엔드, API 계층, 모듈 계층, 파이프라인 계층, 저장 계층으로 구성된다  
프론트엔드는 문서 업로드, PDF 뷰어, 채팅, 인용 패널, 대화 이력을 제공하고, API 계층은 인증과 문서 업로드, 검색 및 답변 생성, 인용, 대화 저장을 담당한다  
모듈 계층은 파서, 섹션 감지기, 청커, 임베더, 검색기, 재정렬기, 컨텍스트 압축기, 생성기, 인용 추적기로 구성되며, 파이프라인 계층은 질문 유형별 경로를 묶는다  
저장 계층은 SQLAlchemy가 여는 로컬 SQLite 기본 경로와 PostgreSQL 확장 경로, ChromaDB, 로컬 파일 저장소로 구성된다  

### 3.2 문서 처리 경로

업로드된 문서는 PDF, DOCX, TXT 형식으로 입력되며 파서가 텍스트와 메타데이터를 추출한다  
이후 섹션 감지기는 abstract, introduction, method, experiment, conclusion, references 같은 섹션 유형을 감지하고, 청커는 검색에 적합한 크기로 문서를 분할한다  
생성된 청크는 BGE-M3 임베딩을 거쳐 ChromaDB에 저장되며, 문서 메타데이터는 관계형 데이터베이스에 함께 저장된다  
이 과정은 향후 섹션 필터 검색과 인용 추적, 결과 하이라이트에 활용된다  

### 3.3 질의 라우팅과 파이프라인 분기

질문이 입력되면 QueryRouter가 의도를 분석해 A부터 F까지의 파이프라인 중 하나를 선택한다  
Route A는 일반 QA  
Route B는 섹션 필터 기반 QA  
Route C는 다중 문서 비교  
Route D는 인용 추적  
Route E는 전체 요약  
Route F는 퀴즈와 플래시카드 생성을 담당한다  
이 구조는 서로 다른 질문 유형을 하나의 프롬프트와 하나의 검색 경로로 처리하지 않도록 만드는 핵심 요소다  

### 3.4 검색 스택

검색은 Dense 임베딩 검색과 BM25를 함께 사용하며, 두 결과는 RRF 기반으로 통합된다  
통합된 후보는 Cross-Encoder reranker를 통해 재정렬되며, 이후 context compression 단계에서 생성 모델 입력 길이에 맞게 압축된다  
이 구조는 단일 검색기보다 다양한 근거 유형을 포착하고, 생성 모델이 더 밀도 높은 문맥을 입력받도록 돕는다  

### 3.5 생성 제어

생성기는 MIDM Mini 또는 Base 모델을 사용하며, 논문 기준 기본 경로는 Base 모델로 고정한다  
Mini 모델은 로컬 스모크 검증 경로로만 사용한다  
답변 생성 시 시스템 프롬프트는 컨텍스트 밖 내용을 추측하지 않도록 제한하고, 수치와 비교 결과는 원문 근거를 유지하도록 설계된다  
여기에 CAD를 적용해 환각을 억제하고, SCD를 적용해 한국어 응답에서의 언어 이탈을 줄인다  
즉 M-RAG의 생성 단계는 단순한 후처리 문장 생성기가 아니라 검색 근거와 제어 로직이 결합된 최종 해석 단계다  

## 4 구현

### 4.1 백엔드와 프론트엔드

백엔드는 FastAPI와 SQLAlchemy를 기반으로 구현되며 인증, 문서 업로드, 검색, 스트리밍 응답, 인용 추적, 대화 저장 API를 제공한다  
프론트엔드는 React와 TypeScript, Zustand를 기반으로 구현되며 3열 레이아웃 안에서 문서 목록, PDF 뷰어, 채팅 인터페이스를 통합한다  
사용자는 업로드한 문서를 기준으로 질문을 입력하고, 응답과 출처, 인용 강조를 함께 확인할 수 있다  

### 4.2 저장 구조

문서 파일은 로컬 데이터 디렉터리에 저장되고, 벡터는 ChromaDB에 저장되며, 사용자와 문서 메타데이터, 대화 이력은 SQLAlchemy가 관리하는 PostgreSQL에 기본 저장된다  
SQLite 경로는 로컬 임시 검증에서만 선택적으로 사용한다  
이 구조는 문서 관리와 검색 근거 저장을 분리해 유지보수와 확장성을 높인다  

### 4.3 운영과 실험 경로

저장소는 로컬 실행 기준 러너 `master_run.py` 를 중심으로 실험 경로를 제공한다  
평가 스크립트는 Track 1과 Track 2로 분리되어 있으며, 결과는 JSON과 Markdown 표로 집계된다  
이 구조는 연구용 시스템에서 흔히 발생하는 구현과 실험 코드의 분리를 줄이고, 동일 저장소 안에서 실험을 재현할 수 있게 한다  

## 5 실험 설계

### 5.1 연구 질문

- RQ1 질의 라우팅과 검색 모듈의 누적 결합이 학술 문서 QA 품질을 얼마나 개선하는가
- RQ2 CAD와 SCD 기반 생성 제어가 환각과 언어 이탈을 얼마나 줄이는가
- RQ3 학술 문서 구조를 반영한 도메인 특화 경로가 범용 경로보다 더 나은 근거 적합성을 보이는가
- RQ4 로컬 실험 경로가 반복 가능한 결과 집계 흐름을 제공하는가

### 5.2 실험 데이터

Track 1은 범용 다국어 QA 성격의 질의 집합과 논문 기반 질의를 함께 사용한다  
Track 2는 학술 문서 구조를 더 직접적으로 반영하는 질의와 문서 집합을 사용한다  
세부 질의 파일은 `backend/evaluation/data/track1_queries.json`, `backend/evaluation/data/track2_queries.json` 을 기준으로 관리한다  
KorQuAD 샘플과 CRAG 기반 샘플, pseudo ground truth 생성 경로는 보조 스크립트로 준비한다  

### 5.3 비교 구성

Track 1의 모듈 누적 비교는 다음 순서로 수행한다  

- Baseline 1 Naive RAG
- Baseline 2 Section Chunking
- Baseline 3 Hybrid Search
- Baseline 4 Reranker
- Baseline 5 Query Router + HyDE
- Full System CAD + SCD + Compression

디코더 비교는 다음 구성을 사용한다  

- Decoder 없음
- CAD only
- SCD only
- CAD + SCD

추가로 CAD alpha sweep과 SCD beta sweep을 수행해 제어 강도에 따른 변화를 관찰한다  
Track 2는 범용 경로와 섹션 인식 청킹, 섹션 필터, RAPTOR 스타일 검색, 인용 추적, 전체 도메인 경로를 비교한다  

### 5.4 평가 지표

정량 평가는 faithfulness, context precision, answer relevancy를 중심으로 수행한다  
디코더 비교에서는 numeric hallucination rate와 language drift rate를 함께 본다  
질적 평가는 섹션 적합성, 비교 응답 구조성, 인용 추적의 유용성, 한국어 응답 안정성을 중심으로 정리한다  

### 5.5 실행 환경

로컬과 원격 실행의 논문 기준 기본 모델은 MIDM Base다  
Mini 모델은 자원 제약 환경에서 스모크 검증용으로만 사용한다  
실험 실행 기준 러너는 `backend/scripts/master_run.py` 이며 결과 집계는 `backend/scripts/results_to_markdown.py` 를 사용한다  

## 6 결과 정리 초안

본 절의 수치는 결과 재실행 후 `backend/evaluation/results/` 산출물을 기준으로 삽입한다  
현재 초안에서는 표 구조와 해석 문장만 고정한다  

### 6.1 표 1 모듈 누적 ablation

표 1에는 Baseline 1부터 Full System까지의 누적 결과를 삽입한다  
해석은 Full System이 Naive RAG 대비 faithfulness와 context precision에서 얼마나 개선되었는지를 중심으로 정리한다  
또한 Section Chunking, Hybrid Search, Reranker, Query Router + HyDE가 각각 어떤 구간에서 가장 큰 기여를 보였는지 단계별로 해석한다  

| 시스템 | Faithfulness | Context Precision | Answer Relevancy | 해석 메모 |
|---|---|---|---|---|
| Baseline 1 Naive RAG | [입력] | [입력] | [입력] | 기준선 |
| Baseline 2 Section Chunking | [입력] | [입력] | [입력] | 구조 정보 반영 효과 |
| Baseline 3 Hybrid Search | [입력] | [입력] | [입력] | Dense + BM25 결합 효과 |
| Baseline 4 Reranker | [입력] | [입력] | [입력] | 상위 근거 정렬 효과 |
| Baseline 5 Router + HyDE | [입력] | [입력] | [입력] | 질의 확장과 라우팅 효과 |
| Full System | [입력] | [입력] | [입력] | 전체 결합 효과 |

### 6.2 표 2 디코더 조합 비교

표 2에는 Decoder 없음, CAD only, SCD only, CAD + SCD를 비교한 결과를 삽입한다  
해석은 환각 억제와 언어 이탈 억제가 서로 다른 축임을 보이고, 두 제어가 함께 적용될 때의 균형점을 설명하는 방향으로 작성한다  

| 구성 | Numeric Hallucination | Language Drift | Faithfulness | 해석 메모 |
|---|---|---|---|---|
| No Decoder | [입력] | [입력] | [입력] | 기준선 |
| CAD only | [입력] | [입력] | [입력] | 환각 억제 중심 |
| SCD only | [입력] | [입력] | [입력] | 언어 유지 중심 |
| CAD + SCD | [입력] | [입력] | [입력] | 통합 효과 |

### 6.3 표 3 파라미터 sweep

표 3은 두 개의 소표로 구성한다  
표 3(a)는 CAD alpha sweep  
표 3(b)는 SCD beta sweep을 다룬다  
해석은 제어 강도가 너무 낮거나 높을 때보다 중간 지점에서 더 안정적인 결과가 나타나는지 확인하는 방식으로 정리한다  

| 표 3(a) CAD alpha | Faithfulness | Numeric Hallucination | 해석 메모 |
|---|---|---|---|
| 0.0 | [입력] | [입력] | [입력] |
| 0.1 | [입력] | [입력] | [입력] |
| 0.3 | [입력] | [입력] | [입력] |
| 0.5 | [입력] | [입력] | [입력] |
| 0.7 | [입력] | [입력] | [입력] |
| 1.0 | [입력] | [입력] | [입력] |

| 표 3(b) SCD beta | Faithfulness | Language Drift | 해석 메모 |
|---|---|---|---|
| 0.1 | [입력] | [입력] | [입력] |
| 0.3 | [입력] | [입력] | [입력] |
| 0.5 | [입력] | [입력] | [입력] |

### 6.4 표 4 Track 2 도메인 특화 비교

표 4에는 범용 경로와 도메인 특화 경로의 비교 결과를 삽입한다  
해석은 섹션 인식 청킹, 섹션 필터, 인용 추적이 학술 문서 QA의 맥락 적합성과 답변 관련성에 어떤 영향을 주는지에 초점을 둔다  

| 시스템 | Faithfulness | Context Precision | Answer Relevancy | 해석 메모 |
|---|---|---|---|---|
| General RAG | [입력] | [입력] | [입력] | 범용 기준선 |
| + Section-aware Chunking | [입력] | [입력] | [입력] | 구조 반영 |
| + Query Router Section Filter | [입력] | [입력] | [입력] | 질의별 필터 효과 |
| + RAPTOR-style Retrieval | [입력] | [입력] | [입력] | 계층 검색 효과 |
| + Citation Tracker | [입력] | [입력] | [입력] | 인용 추적 효과 |
| Full Track 2 System | [입력] | [입력] | [입력] | 도메인 전체 결합 |

## 7 논의

M-RAG의 핵심 의미는 질의 유형에 따라 검색 경로를 분기하고, 검색 단계와 생성 단계의 기여를 분리해 설명할 수 있게 했다는 점에 있다  
이 구조는 단일 파이프라인보다 해석 가능성이 높고, 사용자가 어떤 질문에서 어떤 경로가 동작하는지 추적하기 쉽다  
특히 학술 문서 QA는 섹션 구조와 인용 구조를 함께 다뤄야 하므로, 단순 벡터 검색만으로는 놓치는 문맥이 많다  
M-RAG는 구조 인식 청킹과 하이브리드 검색, 인용 추적을 결합함으로써 이 문제를 시스템 차원에서 다룬다  

생성 제어 측면에서는 CAD와 SCD를 동시에 다룬 점이 중요하다  
학술 문서 QA는 단순 자연어 생성보다 근거 유지와 수치 보존, 언어 일관성이 중요하므로, 디코딩 제어를 별도 기여로 설명할 필요가 있다  
다만 이 기여는 반드시 재실행된 결과와 함께 제시되어야 하며, 미검증 상태의 수치를 넣어서는 안 된다  

또한 본 연구는 공개 서비스 완성을 목표로 한 시스템 논문이라기보다, 학술 문서 QA를 위한 구현 중심 연구 프로토타입에 가깝다  
따라서 운영 보안, 대규모 동시 사용자 처리, 웹 전체 탐색 같은 항목은 핵심 기여보다 한계와 향후 과제로 분리하는 것이 타당하다  

## 8 한계

첫째 인용 추적과 외부 문헌 연결은 접근 가능한 메타데이터와 외부 소스 범위에 영향을 받는다  
둘째 문서 업로드 기반 흐름이 중심이므로 웹 전체를 다루는 범용 에이전트로 서술하기는 어렵다  
셋째 로컬 12GB급 GPU에서는 Mini 모델을 스모크 검증 용도로만 사용하는 것이 현실적이며, 논문 본 실험은 Base 모델을 충분한 자원 환경에서 수행하는 것이 적절하다  
넷째 실험용 질의 집합과 업로드 논문 구성에 따라 정량 결과가 달라질 수 있으므로 데이터 구성과 실행 로그를 함께 보존해야 한다  

## 9 결론

본 연구는 한국어 중심 학술 문서 질의응답을 위해 질의 라우팅, 하이브리드 검색, 생성 제어를 결합한 모듈형 시스템 M-RAG를 제안했다  
M-RAG는 질문 유형에 맞는 파이프라인 분기, 검색 스택의 단계적 결합, CAD와 SCD 기반 생성 제어, 로컬 재현 실험 경로라는 네 축으로 구성된다  
이 시스템은 학술 문서 QA를 하나의 고정 경로가 아니라 질문 유형과 문서 구조에 반응하는 조합형 문제로 다룬다는 점에서 의미가 있다  
향후에는 실험 수치의 재검증, 더 넓은 한국어 데이터셋 적용, 인용 추적 범위 확장, 서비스 운영 수준의 고도화를 통해 시스템과 논문을 함께 확장할 수 있다  

## 부록 A 그림과 표 배치 메모

- 그림 1 전체 시스템 구조도는 `docs/ARCHITECTURE.md` 의 전체 구조도 사용
- 그림 2 질의응답 흐름도는 `docs/ARCHITECTURE.md` 의 흐름도 사용
- 표 1부터 표 4까지의 수치는 `backend/evaluation/results/` 재생성 후 삽입
- 현재 `TABLES.md` 에 남아 있는 동일값 반복 결과는 본문 수치로 사용하지 않음

## 부록 B 참고 문헌 키 초안

- [RAG] Retrieval-Augmented Generation 원 논문
- [HyDE] Hypothetical Document Embeddings 관련 논문
- [RRF] Reciprocal Rank Fusion 관련 논문
- [BGE-M3] BGE-M3 임베딩 모델 논문
- [RAPTOR] RAPTOR 계층 검색 논문
- [CAD] Contrastive Decoding 계열 논문
- [SCD] Self Contrastive Decoding 계열 논문
- [RAGAS] RAGAS 평가 프레임워크 논문

## 부록 C 제출 직전 교체할 항목

- 초록 마지막 문장의 성능 요약 수치
- 표 1부터 표 4의 정량 결과
- 관련 연구의 실제 인용 번호와 참고 문헌 형식
- 실험 환경의 정확한 GPU와 실행 시간 서술
