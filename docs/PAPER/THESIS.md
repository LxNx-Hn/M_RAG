# M-RAG: 한국어 중심 학술 문서 질의응답을 위한 환각 억제형 모듈러 RAG 시스템

## 초록

학술 문서 질의응답에서는 질문 유형에 따라 필요한 검색 방식이 달라진다. 단순 질의, 섹션 특화 질의, 여러 문서 비교, 인용 추적, 전체 요약은 서로 다른 검색과 생성 전략을 요구한다. 본 연구는 이러한 문제를 해결하기 위해 쿼리 라우터 기반 모듈러 RAG 시스템인 M-RAG를 제안한다. M-RAG는 BGE-M3 임베딩, BM25, RRF, reranker, context compression을 결합하고, 생성 단계에서는 CAD와 SCD를 함께 적용해 파라메트릭 지식 개입과 Language Drift를 억제한다. 실험은 Track 1의 모듈 누적 ablation과 Track 2의 논문 도메인 특화 비교로 구성한다. 최종 수치는 `backend/evaluation/results` 산출물을 기준으로 제시한다.

## 1. 서론

RAG는 외부 문서를 검색해 LLM의 답변 근거로 제공하는 방식이다. 그러나 실제 학술 문서 질의응답에서는 모든 질문을 하나의 고정 파이프라인으로 처리하기 어렵다. 방법론 질문은 method 섹션이 중요하고, 결과 질문은 result 섹션이 중요하며, 비교 질문은 여러 문서의 근거를 나누어 검색해야 한다. 인용 질문은 참고문헌 추적이 필요하고, 학습 목적 질문은 퀴즈나 플래시카드 생성이 필요하다.

또 다른 문제는 생성 단계에서 발생한다. 모델은 문서가 제공되어도 사전학습 지식을 끼워 넣을 수 있고, 영어 논문 청크가 컨텍스트에 포함되면 한국어 질문에도 영어 답변으로 흐를 수 있다. 본 연구는 전자를 파라메트릭 지식 개입, 후자를 Language Drift로 보고, CAD와 SCD를 함께 적용해 완화한다.

본 연구의 기여는 다음과 같다.

- C1 모듈별 누적 ablation을 통해 범용 질의와 논문 도메인에서 각 모듈의 기여도를 분해한다
- C2 CAD와 SCD를 결합해 근거 중심 생성과 한국어 응답 안정성을 함께 다룬다
- C3 연구 경로 A~E와 운영 경로 F, 인용/특허 추적, SSE, Judge API를 포함한 실제 동작 시스템을 구현한다

## 2. 관련 연구

RAG의 기본 구조는 Lewis et al. [20]의 retrieval-augmented generation에서 출발한다. 이후 Gao et al. [1]은 RAG 시스템의 발전 방향을 정리했고, Wang et al. [13]은 RAG 구현 실무에서 검색, 재정렬, 평가 설계의 중요성을 논의했다.

다국어 RAG에서는 언어 불일치 문제가 중요하다. Chirkova et al. [31]과 Park & Lee [32]는 다국어 환경에서 검색 언어와 답변 언어의 불일치가 성능에 영향을 줄 수 있음을 보였다. Ul Islam et al. [30]은 LLM 환각률이 언어별로 달라질 수 있음을 보고했다. Li et al. [34]는 Language Drift 문제와 이를 줄이기 위한 SCD 계열 접근을 다룬다.

본 연구는 이러한 선행 연구를 바탕으로, 검색 모듈과 생성 제어 모듈을 분리해 실험적으로 비교한다. 특히 CAD [3]와 SCD [34]의 목적이 다르다는 점에 주목한다. CAD는 문서 없는 생성 경향을 억제하고, SCD는 비목표 언어 토큰을 억제한다.

## 3. 시스템 설계

### 3.1 전체 구조

M-RAG는 18개 코드 모듈로 구성된다. 이 중 논문 실험과 클레임의 중심이 되는 연구 핵심 모듈은 13개이고, 입력 처리와 운영 기능을 담당하는 확장 모듈은 5개다.

연구 핵심 모듈은 embedder, chunker, reranker, hybrid retriever, query router, section detector, generator, CAD decoder, SCD decoder, context compressor, query expander, citation tracker, follow-up generator다. 확장 모듈은 PDF parser, DOCX parser, patent tracker, PPTX exporter, vector store다.

질문 생성 계층은 운영 대화 기능이다. 후속 질문은 `followup_generator.py`가 담당하고, 퀴즈와 플래시카드는 `pipeline_f_quiz.py`가 담당한다. 논문 실험은 A~E 연구 경로와 CAD/SCD 효과를 중심으로 구성하고, 서비스 시연은 A~F 전체 경로를 사용한다.

### 3.2 질의 라우팅

`query_router.py`는 질문을 A~F 여섯 경로로 분류한다.

| 경로 | 목적 |
|---|---|
| A | 일반 질의응답 |
| B | 섹션 특화 질의응답 |
| C | 여러 문서 비교 |
| D | 인용 또는 특허 추적 |
| E | 전체 요약 |
| F | 퀴즈 또는 플래시카드 생성 |

A~E는 논문 실험과 클레임의 중심 경로다. F는 서비스 시연과 운영 대화 흐름에서 사용하는 학습 보조 경로다.

이 구조가 본 연구에서 말하는 Modular RAG의 핵심이다. 모든 질문을 같은 순서로 처리하지 않고, 질문 유형에 맞는 모듈 조합을 선택한다.

### 3.3 검색과 압축

검색 단계는 dense retrieval과 BM25를 함께 사용하고, RRF로 순위를 결합한다. 이후 reranker가 상위 문서를 재정렬하고, context compressor가 생성 모델에 들어갈 근거를 줄인다. 이 구조는 검색 정확도와 컨텍스트 길이 제약을 함께 다루기 위한 설계다.

청크에는 문서 언어 메타데이터를 함께 저장한다. HyDE 확장 문서는 검색 대상 문서의 대표 언어를 기준으로 생성하여, 영어 논문에서는 영어 가상 문서가, 한국어 소스에서는 한국어 가상 문서가 검색에 사용되도록 한다.

### 3.4 생성 제어

생성 모델은 논문 실험 기준 MIDM Base를 사용한다. Mini 모델은 로컬 스모크 검증용 선택지다.

CAD는 문서 포함 프롬프트와 질문 단독 입력의 logits 차이를 이용한다. 목적은 모델의 사전학습 지식이 문서 근거보다 강하게 개입하는 현상을 줄이는 것이다. CAD가 활성화된 생성은 greedy decoding을 사용해 생성 제어 효과를 직접 반영한다.

SCD는 목표 언어가 아닌 토큰에 패널티를 준다. 본 연구에서는 한국어 답변 안정성을 높이기 위해 사용한다.

## 4. 구현

백엔드는 FastAPI 기반이며, 주요 라우터는 auth, papers, chat, citations, history로 분리된다. chat router는 `/api/chat/query`, `/api/chat/query/stream`, `/api/chat/search`, `/api/chat/judge`, `/api/chat/export/ppt`를 제공한다.

프론트엔드는 React 기반이며, 업로드한 문서, 채팅, 출처 패널, PDF 뷰어, 인용 패널, 퀴즈/플래시카드 표시를 포함한다.

데이터 저장은 SQLAlchemy를 사용한다. 논문 실험의 빠른 실행 경로는 SQLite를 사용하고, 운영 경로는 PostgreSQL을 사용한다. 벡터 저장소는 ChromaDB다.

## 5. 실험 설계

실험 코퍼스는 8개 문서로 구성한다. 영어 NLP 논문은 BGE M3-Embedding, RAG Survey, CAD, RAPTOR 네 편이고, 한국어/MIDM 문서는 MIDM-2.0 Technical Report, Korean RAG Evaluation Framework, Korean RAG RRF/Chunking, Korean CAD Contrastive Decoding 네 편이다. 8편 전체를 저장소의 `backend/data/`에 포함하여 새 인스턴스에서 `git pull`만으로 기본 실험을 재현할 수 있게 한다.

### 5.1 연구 질문

- RQ1 모듈을 누적 추가할 때 RAG 품질이 어떻게 변하는가
- RQ2 CAD와 SCD는 환각과 언어 이탈을 줄이는가
- RQ3 논문 도메인 특화 모듈은 범용 RAG보다 유리한가

### 5.2 Track 1

Track 1은 8개 문서에 대한 논문별 특화 쿼리로 모듈 누적 ablation과 decoder ablation을 다룬다. 모든 기본 쿼리는 한국어이며, `crosslingual_en` 타입만 영어 대조군으로 사용한다.

모듈 누적 비교는 다음 순서로 수행한다.

- Baseline 1 Naive RAG
- Baseline 2 Section Chunking
- Baseline 3 BGE-M3 또는 Hybrid Search
- Baseline 4 Hybrid + Reranker
- Baseline 5 Router + HyDE
- Full System CAD + SCD + Compression

decoder 비교는 다음 조합을 사용한다.

- decoder 없음
- CAD only
- SCD only
- CAD + SCD

### 5.3 Track 2

Track 2는 네 편의 NLP 논문을 대상으로 논문 도메인 특화 모듈의 효과를 비교한다. 비교 대상은 범용 RAG, 섹션 인식 청킹, 섹션 필터, RAPTOR 스타일 요약/검색, 인용 추적, 전체 도메인 결합 경로다.

### 5.4 평가 지표

평가는 RAGAS 계열 지표와 내부 judge endpoint를 사용한다.

- Faithfulness 답변이 검색 근거에 의해 지지되는 정도
- Answer Relevancy 질문에 답변이 얼마나 관련 있는지
- Context Precision 검색된 컨텍스트 중 유용한 근거 비율
- Context Recall 필요한 근거가 검색에 포함된 정도
- Numeric Hallucination Rate 수치 오류 비율
- Language Drift Rate 한국어 질의에서 비한국어 답변으로 흐르는 비율

## 6. 결과 작성 방식

최종 표는 `backend/evaluation/results/*.json`과 `TABLES.md`를 기준으로 삽입한다. 검증되지 않은 수치는 포함하지 않는다.

표 1은 Track 1 모듈 누적 ablation을 다룬다.
표 2는 CAD/SCD 조합 비교를 다룬다.
표 3은 CAD alpha 및 SCD beta sweep을 다룬다.
표 4는 Track 2 논문 도메인 특화 비교를 다룬다.

## 7. 한계

본 연구의 한계는 다음과 같다.

- CAD와 SCD는 추론 비용을 증가시킬 수 있다
- SCD의 한국어 판별은 토큰 단위 휴리스틱에 영향을 받는다
- Track 2는 수집한 논문 집합과 질의 구성에 따라 결과가 달라질 수 있다
- 한국어 원문 논문 4편으로 한국어 검증 범위를 확보했으나, 추가 도메인 확장은 후속 과제로 남는다
- 자동 평가는 judge 모델의 품질에 영향을 받는다
- 추론 서버 최적화와 외부 LLM API 비교는 다음 단계 연구에서 다룬다

## 8. 결론

M-RAG는 학술 문서 질의응답에서 질문 유형별 경로 선택, 하이브리드 검색, 재정렬, 컨텍스트 압축, CAD/SCD 생성 제어를 결합한 모듈러 RAG 시스템이다. 본 연구는 모듈별 기여도와 생성 제어 효과를 분리해 분석하고, 논문 도메인에 필요한 섹션 질의, 비교, 인용 추적, 요약, 퀴즈 생성 경로를 하나의 시스템 안에 통합한다.

## 참고문헌

참고문헌 35편의 상세 목록은 `GUIDE_ORIGINAL.md`를 기준으로 한다. 제출본 작성 시 번호와 표기는 해당 문서를 기준으로 맞춘다.
