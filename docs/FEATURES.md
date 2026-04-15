# M-RAG 기능 명세

- 기준일 2026-04-15
- 범위 현재 main 브랜치 구현 기능
- 형식 운영 문서용 개조식

## 문서 처리

- PDF 업로드 지원
- DOCX 업로드 지원
- TXT 업로드 지원
- 업로드 크기 제한 50MB
- 파일 확장자 검증 `.pdf` `.docx` `.txt`
- MIME 및 시그니처 검증 적용
- 문서 유형 자동 판별 `paper` `lecture` `patent` `general`
- 섹션 단위 메타데이터 생성

## 검색 및 생성

- 라우트 기반 질의 처리
- Route A 단순 QA
- Route B 섹션 특화 검색
- Route C 2문서 비교
- Route D 인용 추적
- Route E 전체 요약
- Route F 퀴즈 생성
- 하이브리드 검색 Dense + BM25 + RRF
- 컬렉션 단위 BM25 인덱스 영속화
- Cross Encoder 재랭킹
- Context 압축 처리
- CAD 기반 생성 제어
- SCD 기반 언어 이탈 제어

## 인용 및 특허

- 인용 목록 조회 `/api/citations/list`
- 인용 다운로드 `/api/citations/download`
- 인용 추적 실행 `/api/citations/track`
- arXiv 대상 처리
- 특허 번호 파싱 KR US JP EP WO
- Google Patents 메타 조회
- 다운로드 URL allowlist 검증

## 인증 및 권한

- JWT 기반 인증
- 회원가입 로그인 로그아웃 지원
- 토큰 블랙리스트 기반 무효화
- 보호 라우트 인증 의존성 적용
- 사용자 소유 데이터 격리 `user_id`
- 컬렉션 네임스페이스 격리 `{user_id}__{collection}`

## API 및 실시간 처리

- REST API 제공
- SSE 스트리밍 응답 제공
- 스트리밍 타임아웃 처리
- 스트리밍 에러 프레임 전송
- 답변 완료 이벤트에 `follow_ups` 포함
- PPT 내보내기 API 제공 `/api/chat/export/ppt`

## 프론트엔드

- 3패널 레이아웃 소스 뷰어 채팅
- PDF 페이지 이동 및 하이라이트
- 참고문헌 탭 전환
- 추천 질문 말풍선 UI
- 401 응답 시 자동 로그아웃 및 로그인 이동
- 다국어 UI 한국어 영어

## 운영 및 관측

- JSON 구조화 로그
- 요청 ID 미들웨어
- 로그 로테이션 적용
- 전역 예외 처리
- 레이트 리밋 적용
- 보안 헤더 미들웨어 적용
- Alembic 마이그레이션 적용
- 백업 스크립트 제공
- CI 파이프라인 제공 backend frontend docker build

## 공개 전 잔여 범위

- Refresh Token 체계
- httpOnly 쿠키 전환
- CSRF 방어
- HTTPS 종단 강제
- 감사 로그 완성
- E2E 부하 테스트 완료
