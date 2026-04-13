# M-RAG: PPT용 개조식 요약

> 마침표 없이, 슬라이드에 바로 붙여넣을 수 있는 개조식

---

## 개요

- 한국어 학술 논문 질의응답을 위한 Modular RAG 시스템
- 쿼리 유형에 따라 6개 파이프라인(A~F)이 동적으로 분기
- 논문 + 강의/교재 + 특허 3가지 문서 유형 자동 감지
- 환각 억제(CAD) + 언어 이탈 방지(SCD) 내장
- RAGAS 기반 정량 평가 프레임워크 포함

---

## 문제 정의

- 기존 RAG: 단일 파이프라인, 모든 질문에 동일 전략 적용
- 학술 논문: 섹션 구조, 인용 관계, 수치 데이터 등 도메인 특수성 존재
- 영어 논문 + 한국어 사용자: LLM 답변이 영어로 전환되는 Language Drift
- LLM 환각: 논문에 없는 수치나 사실을 그럴듯하게 생성하는 문제

---

## 동기

- NotebookLM: 범용 문서 QA, AI 아키텍처 미공개, 학술 특화 기능 부재
- SciRAG/PaperQA2: 영어 전용, 환각 억제 없음, 단일 파이프라인
- 한국어 학술 RAG에 CAD를 적용·평가한 선행 연구가 존재하지 않음

---

## 해결 — 13개 모듈 + 6개 파이프라인

### 인덱싱 흐름
- PDF → 구조 보존 파싱(M1) → 섹션 감지(M2) → 청킹(M3) → 임베딩(M4) → 벡터 저장(M5)

### 질의응답 흐름
- 쿼리 → 라우터(M6) → 파이프라인 분기 → 검색(M7~M9) → 압축(M10) → 생성(M12) + CAD/SCD(M13)

### 6개 파이프라인

| 경로 | 용도 | 핵심 기법 |
|------|------|----------|
| A | 단순 QA | HyDE 확장 + 하이브리드 검색 |
| B | 섹션 특화 | 섹션 필터링 + 부스트 재랭킹 |
| C | 비교 분석 | 논문별 병렬 검색 + 비교 표 |
| D | 인용 추적 | arXiv/Google Patents 자동 인덱싱 |
| E | 전체 요약 | 섹션별 5회 검색 + 구조화 |
| F | 퀴즈/플래시카드 | CAD 강제 적용 출제 |

---

## 핵심 차별점

- **CAD (Context-Aware Decoding)**: LLM의 파라메트릭 지식 개입을 α 강도로 억제
- **SCD (Selective Context-aware Decoding)**: 비한국어 토큰에 β 패널티 부여
- **라우트 투명성**: 매 답변에 어떤 파이프라인이 사용되었는지 배지로 표시
- **완전 오픈소스**: 전체 코드 + 평가 프레임워크 공개
- **로컬 배포 가능**: 민감 자료 외부 유출 차단

---

## 시스템 구성

- Frontend: React + TypeScript + Vite + TailwindCSS
- Backend: FastAPI + 13개 RAG 모듈
- LLM: MIDM-2.0 Instruct (Mini 2.3B / Base 11.5B)
- Embedding: BAAI/bge-m3 (1024차원, 한영 동일 공간)
- Vector DB: ChromaDB + BM25 하이브리드
- Auth/History: PostgreSQL + JWT
- 배포: Docker Compose 원클릭

---

## 실험 결과 (Table 1~4)

### Table 1: 모듈별 Ablation (누적 추가)
- Baseline 1 (Naive RAG) → Full System까지 6단계
- 각 모듈 추가 시 RAGAS 4개 지표 변화 측정

### Table 2: CAD α Ablation
- α ∈ {0.1, 0.3, 0.5, 0.7, 1.0}
- Faithfulness delta 기준 최적 α 도출

### Table 3: SCD β Ablation
- β ∈ {0.1, 0.3, 0.5}
- 한국어 답변 유지율 및 Overall delta 측정

### Table 4: CAD + SCD 결합 효과
- 4가지 조합: Both Off / CAD Only / SCD Only / Both On
- 결합 시 시너지 효과 확인

---

## 한계 및 향후 과제

- arXiv 미등록 논문은 인용 추적 불가 (Pipeline D 제약)
- MIDM Base 모델 24GB VRAM 필요 (Mini로 대체 가능하나 품질 차이)
- 수식의 의미 이해 불가 (구조 보존은 가능)
- 특허 도메인: KIPRIS API 키 필요, Google Patents 비공식 크롤링
- SCD의 영어 기술 용어 오탐 가능성 (허용 목록 확장 필요)
