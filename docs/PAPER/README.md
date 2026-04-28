# M-RAG 논문 문서

## 문서 역할

| 문서 | 역할 |
|---|---|
| `GUIDE_ORIGINAL.md` | 35편 참고문헌 기반 전체 설계 기준 문서 |
| `THESIS.md` | 제출용 논문 본문 초안 |
| `PPT_SUMMARY.md` | PPT 제작용 개조식 요약 |
| `PPT_KEYWORDS.md` | PPT 제작용 키워드 요약 |
| `LIMITATIONS_AND_FUTURE_WORK.md` | 한계와 향후 과제 |
| `NEXT_STAGE_VLLM_CLAIM.md` | 현재 논문 이후 vLLM 연구 후보 |
| `DOC_SYNC_PLAN_35.md` | 이번 문서 정리 실행 계획과 검토 기준 |

## 읽는 순서

1. `GUIDE_ORIGINAL.md`
2. `THESIS.md`
3. `docs/EXPLAIN/TERMS_GLOSSARY_KO.md`
4. `docs/EXPLAIN/ARCHITECTURE_EXPLAINED_KO.md`
5. `docs/EXPLAIN/ROUTE_MODULE_MATRIX_KO.md`
6. `PPT_SUMMARY.md`

## 기준

- 논문 기본 모델은 MIDM Base
- Mini는 로컬 스모크 검증용
- 실험 빠른 실행은 SQLite + SQLAlchemy
- 운영/서비스 경로는 PostgreSQL + SQLAlchemy
- 논문 실험 경로는 MIDM Base 직접 디코딩을 기준으로 함

## 주의

- 결과 수치는 검증된 실험 산출물에서만 옮김
- 문서 링크는 현재 `PAPER`, `EXPLAIN`, `USAGE` 구조를 기준으로 함
- 자세한 설명은 `docs/EXPLAIN`에 둠
- 발표용 요약은 `PPT_*` 문서만 사용
