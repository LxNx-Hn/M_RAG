# M-RAG 설명 문서

## 문서 역할

이 폴더는 비전공자와 신규 참여자가 M-RAG 구조를 이해하기 위한 상세 설명 문서다

| 문서 | 역할 |
|---|---|
| `TERMS_GLOSSARY_KO.md` | RAGAS, CAD, SCD, BM25 같은 핵심 용어 설명 |
| `ARCHITECTURE_EXPLAINED_KO.md` | 전체 구조를 쉬운 말로 설명 |
| `FLOW_EXPLAINED_KO.md` | 업로드부터 답변까지의 흐름 설명 |
| `FEATURES_EXPLAINED_KO.md` | 사용자 기능과 연구 기능 설명 |
| `ROUTE_MODULE_MATRIX_KO.md` | A–F 경로별 동작 모듈 설명 |
| `REFERENCE_EXPLAINED_KO.md` | 현재 참고문헌 구성과 역할 설명 |
| `TABLE_INTERPRETATION_GUIDE.md` | 실험 표 읽는 법 설명 |
| `COMPLETE_REPOSITORY_GUIDE_KO.md` | 코드·서비스·실험·논문·검증·운영을 한 번에 연결하는 통합 안내서 |
| `../../experiments/reports/reference_scd_rerun_explainer_KO.md` | 수정된 SCD 재현 실험을 가장 쉽게 설명한 문서 |
| `../../experiments/reports/reference_scd_symmetric_cross_judge_report.md` | 대칭 전처리·교차 judge 후속 평가의 공식 보고서 |

## 읽는 순서

1. `COMPLETE_REPOSITORY_GUIDE_KO.md`
2. `TERMS_GLOSSARY_KO.md`
3. `ARCHITECTURE_EXPLAINED_KO.md`
4. `FLOW_EXPLAINED_KO.md`
5. `ROUTE_MODULE_MATRIX_KO.md`
6. `TABLE_INTERPRETATION_GUIDE.md`
7. `../../experiments/reports/reference_scd_rerun_explainer_KO.md`
8. `../PAPER/THESIS_KO.md`

국문 전체 논문은 `docs/PAPER/THESIS_KO.md`, 영문 전체 논문은 `docs/PAPER/THESIS.md`를 참고한다. 결과 수치는 논문에 연결된 공식 분석 산출물만 사용하며, 역사적 `penalty_additive` v1과 수정된 `reference_scd` 결과를 합치지 않는다.
