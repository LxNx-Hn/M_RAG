# M-RAG 논문 작성 기준서

- 기준일 2026-04-26
- 목적 제출 문서와 현재 구현 상태를 정합하게 유지
- 원칙 과거 변경 이력보다 현재 코드와 현재 실험 경로를 우선

## 같이 보는 문서

- `docs/PAPER/README.md` 논문 문서 묶음 진입점
- `docs/PAPER/ACADEMIC_CLAIMS.md` 기여 주장과 근거 파일
- `docs/PAPER/COMPETITIVE_ANALYSIS.md` 비교 포지셔닝
- `docs/PAPER/LIMITATIONS_AND_FUTURE_WORK.md` 한계와 후속 과제

## 1 연구 범위

- 대상 한국어 중심 학술 문서 QA
- 문서 유형 paper lecture patent general
- 파이프라인 A B C D E F
- 생성 제어 CAD SCD
- 평가 프레임워크 RAGAS + ablation

## 2 핵심 기여 문장

- C1 라우트 기반 모듈형 RAG 구조 제시
- C2 하이브리드 검색과 재정렬 결합 적용
- C3 CAD SCD 기반 생성 제어 통합
- C4 재현 가능한 로컬 실험 경로와 표 생성 파이프라인 제공

## 3 실험 표 구성

- Table 1 모듈 누적 ablation
- Table 2 CAD alpha ablation
- Table 3 SCD beta ablation
- Table 4 CAD SCD 조합 비교

## 4 구현 연결 포인트

- parser chunker section_detector
- query_router hybrid_retriever reranker
- generator cad_decoder scd_decoder
- citation_tracker patent_tracker
- pipelines A B C D E F

## 5 제외 범위 명시

- 외부 공개 운영 보안 완성 항목
- Refresh Token 및 쿠키 전환
- HTTPS 강제 및 인증서 자동 갱신
- E2E 부하 테스트 최종 수치

## 6 논문 본문 작성 체크

- 문제 정의는 현재 구현 범위 안에서 서술
- 기능 소개는 `docs/FEATURES.md` 와 동일 용어 사용
- 구조 설명은 `docs/ARCHITECTURE.md` 와 충돌하지 않게 유지
- API 경로 표기는 실제 라우터 기준 사용
- 과거 대비 개선 표현보다 현재 동작 기준 서술 우선
- 한계 항목은 `docs/PAPER/LIMITATIONS_AND_FUTURE_WORK.md` 와 일치

## 7 제출 전 점검

- 테스트 가이드 절차 실행 로그 확보
- 실험 산출 JSON 경로 명시
- 스크린샷은 최신 UI 기준 반영
- 문서 날짜와 커밋 해시 동기화
