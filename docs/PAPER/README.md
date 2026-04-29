# M-RAG 논문 문서

## 문서 역할

| 문서 | 역할 |
|---|---|
| `THESIS.md` | 투고용 논문 본문 (9개 장, 39편 참고문헌) |
| `GUIDE_ORIGINAL.md` | 35편 참고문헌 기반 전체 설계 기준 문서 (논문 작성 시 참고용) |
| `PPT_SUMMARY.md` | PPT 제작용 개조식 요약 |
| `PPT_KEYWORDS.md` | PPT 제작용 키워드 요약 |
| `LIMITATIONS_AND_FUTURE_WORK.md` | 한계와 향후 과제 (THESIS.md 8장에 통합) |
| `NEXT_STAGE_VLLM_CLAIM.md` | 현재 논문 이후 vLLM 연구 후보 |
| `DOC_SYNC_PLAN_35.md` | 39편 기준 문서 동기화 기록 |

## 읽는 순서

1. `THESIS.md` — 논문 전체 (9개 장)
2. `GUIDE_ORIGINAL.md` — 설계 배경 상세
3. `docs/EXPLAIN/TERMS_GLOSSARY_KO.md` — 용어 사전
4. `docs/EXPLAIN/ARCHITECTURE_EXPLAINED_KO.md` — 구조 쉬운 설명
5. `docs/EXPLAIN/ROUTE_MODULE_MATRIX_KO.md` — 경로별 모듈 동작
6. `PPT_SUMMARY.md` — 발표 요약

## 논문 구조 (THESIS.md)

| 장 | 제목 | 분량 |
|---|---|---|
| 1 | 서론 | ~3페이지 |
| 2 | 관련 연구 | ~4페이지 |
| 3 | 시스템 설계 | ~6페이지 |
| 4 | 구현 | ~4페이지 |
| 5 | 실험 설계 | ~5페이지 |
| 6 | 실험 결과 | ~4페이지 (표 틀 + `[결과 삽입]`) |
| 7 | 분석 | ~3페이지 (조건부 구조) |
| 8 | 한계와 향후 과제 | ~2페이지 |
| 9 | 결론 | ~1페이지 |
| 참고문헌 | 39편 | ~2페이지 |

## 기준

- 논문 기본 모델은 MIDM-2.0 Base Instruct [36]
- Mini는 로컬 스모크 검증용
- 실험 빠른 실행은 SQLite + SQLAlchemy
- 운영/서비스 경로는 PostgreSQL + SQLAlchemy
- 논문 실험 경로는 MIDM Base 직접 디코딩을 기준으로 함
- CAD 실험 기준 alpha = 0.5, SCD 실험 기준 beta = 0.3

## 주의

- 결과 수치는 검증된 실험 산출물에서만 옮김
- `[결과 삽입]` 자리표시자는 실험 실행 후 채움
- 문서 링크는 현재 `PAPER`, `EXPLAIN`, `USAGE` 구조를 기준으로 함
- 자세한 설명은 `docs/EXPLAIN`에 둠 (참고문헌 총 39편)
- 발표용 요약은 `PPT_*` 문서만 사용
