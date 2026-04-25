# M-RAG 논문 문서

- 기준일 2026-04-26
- 목적 논문 초안, 발표 자료, 심사 대응에서 함께 보는 현재 기준 문서 묶음
- 원칙 과거 이력보다 현재 코드와 현재 실험 경로를 우선

## 문서 구성

- [`GUIDE_ORIGINAL.md`](GUIDE_ORIGINAL.md) 과거 `Guide.md` 국문 원본 초안 복구본
- [`THESIS.md`](THESIS.md) 제출용 논문 본문 초안
- [`../GUIDE/GuideV2.md`](../GUIDE/GuideV2.md) 논문 본문 작성 기준
- [`ACADEMIC_CLAIMS.md`](ACADEMIC_CLAIMS.md) 논문에서 주장 가능한 기여와 근거 파일
- [`NEXT_STAGE_VLLM_CLAIM.md`](NEXT_STAGE_VLLM_CLAIM.md) `vLLM` 기반 다음 단계 연구 클레임 후보
- [`COMPETITIVE_ANALYSIS.md`](COMPETITIVE_ANALYSIS.md) 비교 포지셔닝 초안
- [`LIMITATIONS_AND_FUTURE_WORK.md`](LIMITATIONS_AND_FUTURE_WORK.md) 한계와 후속 과제
- [`../PRESENTATION/SUMMARY.md`](../PRESENTATION/SUMMARY.md) 발표용 요약
- [`../ARCHITECTURE.md`](../ARCHITECTURE.md) 구조도와 흐름도

## 현재 논문에서 고정할 범위

- 권장 고정 제목 `M-RAG: 한국어 중심 학술 문서 질의응답을 위한 환각 억제형 모듈러 RAG 시스템`
- 한국어 중심 학술 문서 QA
- 문서 유형 paper lecture patent general
- 라우터 기반 파이프라인 A B C D E F
- Dense + BM25 + RRF + reranker 기반 검색
- CAD SCD 기반 생성 제어
- 로컬 실행 기준 실험 파이프라인과 결과 표 생성

## 논문에서 피할 표현

- 공개 서비스 운영 완성
- 웹 전체를 다루는 범용 에이전트
- 모든 도메인에서 검증된 범용 성능 우위
- 미검증 실험 수치를 본문 대표 수치처럼 단정하는 표현

## 연결되는 코드 축

- 질의 라우팅 `backend/modules/query_router.py`
- 검색 스택 `backend/modules/hybrid_retriever.py`
- 생성 제어 `backend/modules/generator.py`, `backend/modules/cad_decoder.py`, `backend/modules/scd_decoder.py`
- 파이프라인 `backend/pipelines/`
- 실험 실행 `backend/evaluation/`, `backend/scripts/master_run.py`

## 제출 전 최소 확인

- 원본 초안과 최신 초안의 역할이 섞이지 않게 구분
- 논문 본문 용어가 `docs/FEATURES.md` 와 충돌하지 않는지 확인
- 구조 설명이 `docs/ARCHITECTURE.md` 와 일치하는지 확인
- 실험 표 번호와 `THESIS.md`, `GuideV2.md` 의 표 정의가 일치하는지 확인
- 결과 수치는 `backend/evaluation/results/` 산출물 기준으로만 기입
