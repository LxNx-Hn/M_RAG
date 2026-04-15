# M-RAG 최신 작업 계획

- 기준일 2026-04-15
- 목적 최신 코드 기준 잔여 작업 관리
- 원칙 완료 항목 미기재
- 원칙 마침표 없는 개조식 유지

## P0 공개 전 필수

- [ ] Access Token 15분 + Refresh Token 7일 정책 적용
- [ ] `/api/auth/refresh` 구현 및 refresh rotation 적용
- [ ] Access Token 저장소를 httpOnly 쿠키로 전환
- [ ] CSRF 방어 적용 double submit 또는 SameSite 전략 확정
- [ ] Nginx TLS 종단 적용 및 HTTPS 강제 리다이렉트
- [ ] HSTS 운영 값 확정 및 프록시 헤더 점검
- [ ] 감사 로그 테이블 설계 로그인 업로드 삭제 권한실패 기록
- [ ] 감사 로그 조회 기준 문서화
- [ ] Prompt Injection 방어 규칙 적용 토큰 이스케이프 경계 구분
- [ ] Playwright E2E 시나리오 3종 이상 구축
- [ ] Locust 부하 테스트 프로파일 작성 동시 사용자 기준 확정

## P1 운영 안정화

- [ ] BM25 한국어 형태소 기반 토크나이저 적용
- [ ] Generator 동시성 큐 정책 튜닝 429 기준치 확정
- [ ] 모델 추론 타임아웃 정책 환경변수화
- [ ] 백업 복구 리허설 수행 Postgres Chroma data 디렉터리
- [ ] 배포 헬스체크 항목에 외부 의존성 상태 상세화
- [ ] 로그 대시보드 필드 표준화 request_id user_id route latency

## P2 문서 동기화

- [ ] README 운영 단계 정의와 실제 릴리스 범위 일치
- [ ] FEATURES 문서와 API 스키마 동기화
- [ ] TESTING_GUIDE와 CI 파이프라인 절차 동기화
- [ ] GuideV2 논문 기여 항목과 실제 구현 범위 일치
- [ ] 변경 시점마다 최신 문서 한 벌 유지 원칙 점검

## 승인 게이트

- [ ] 연구용 게이트 로컬 수동 검증 통과
- [ ] 내부 시연 게이트 인증 인가 격리 로그 검증 통과
- [ ] 외부 공개 게이트 P0 전항목 완료 및 보안 리뷰 완료
